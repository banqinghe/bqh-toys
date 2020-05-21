#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctype.h>
#define BUFFER_SIZE 32768

struct client_list
{
	int sock;
	struct client_list *next;
};
  
struct client_list *head = NULL;

struct client_list *init_list(struct client_list*head)
{
	head = malloc(sizeof(struct client_list));
	head->sock = -1;
	head->next = NULL;
	return head;
}

// 新的客户端加到客户端队列中
int add_sock(struct client_list*head,int new_sock)
{
	struct client_list *p = head;
	struct client_list *new_node = malloc(sizeof(struct client_list));
	new_node->sock = new_sock;
	new_node->next = NULL;
 
	while(p->next!=NULL) {
		p = p->next;
	}
	p->next = new_node;
	return 0;
}
 
// 找出最大的文件描述符
int find_max(struct client_list*head)
{
	struct client_list *p = head->next;
	if(p==NULL)
		return 0;
	int max_sd = p->sock;
	for(p;p!=NULL;p=p->next) {
		if(max_sd < p->sock)
			max_sd = p->sock;
	}
	return max_sd;
}

//当有新的客户端作为新的文件描述符加进来时，显示客户端列表中的所有客户端文件描述符
void show_client_list(struct client_list*head)
{
	struct client_list *p = head;
	if(p->next == NULL) {
		printf("IS A EMPTY LIST!\n");
		return ;
	}
	else {
		printf("client_list is : ");
		for(p =head->next; p!=NULL;p = p->next) {
			printf("%d ",p->sock);
		}
		printf("\n");
	}
}
//取消退出客户端的结点。
int del_node(struct client_list* head,int target_sock)
{
	struct client_list *p = head->next;
	struct client_list *q = head;

	while(p != NULL) {
		if(p->sock == target_sock) {
			q->next = p->next;
			free(p);
			p = NULL;
		}
		else {
			q = q->next;
			p = p->next;
		}
	}

	return 0;
}
 
int main(int argc, char **argv)
{
    if(argc != 2) {
        fprintf(stderr, "invalid arguments");
        exit(1);
    }

	char rbuf[BUFFER_SIZE]={0};
	char wbuf[BUFFER_SIZE]={0};
 
	int sockfd, new_sock;
	int max_sd;
	int on = 1;
	int client_cnt = 0;
	struct client_list *pos;
	fd_set fdset;
	long val;
 
	head = init_list(head);   //初始化客户端链表。
	pos = head;

	int port_number = atoi(argv[1]);

	struct sockaddr_in server_addr;
	struct sockaddr_in client_addr;
	int size = sizeof(struct sockaddr_in);
	bzero(&server_addr, sizeof(struct sockaddr_in));
 
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(port_number);
	server_addr.sin_addr.s_addr = htonl(INADDR_ANY);
	
	sockfd = socket(AF_INET,SOCK_STREAM,0);
	setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, &on, sizeof(on));	// 设置socket套接字为复用，不设也可以
	
	// 把sockfd设置为非阻塞
	val = fcntl(sockfd,F_GETFL);
	val|=O_NONBLOCK;
	fcntl(sockfd,F_SETFL,val);

	if(port_number <= 0 || port_number > 65535) {
		fprintf(stderr, "Incorrect port number range\n");
		exit(1);
	}

	if(bind(sockfd, (struct sockaddr*)&server_addr, sizeof(struct sockaddr_in)) < 0) {
		fprintf(stderr, "This port number has been used\n");
		close(sockfd);
		exit(1);
	}
	listen(sockfd, 100);

	char last_head= '\0';

	while(1) {
		
/*-------------------------------检测是否有新的client---------------------------------------*/

		new_sock = accept(sockfd, (struct sockaddr*)&client_addr, &size);//循环接受新连接的客户端
		
		if (new_sock != -1) {
			add_sock(head, new_sock);
			//有新的客户端连接时的调试信息，根据要求并不显示
			client_cnt++;
			printf("new sock is %d, total number of client is %d, ",new_sock, client_cnt);
			show_client_list(head);
		}

		max_sd = find_max(head);     //从客户端队列中，找出最大的文件描述符
		FD_ZERO(&fdset);             //清空文件描述符集
		pos = head;
		//把每个套接字加入到集合中
		if(pos->next != NULL) { // 若套接字列表不是空
			for(pos=head->next; pos!=NULL; pos=pos->next) {
				FD_SET(pos->sock, &fdset);
			}
		}

		FD_SET(sockfd, &fdset);	//  把server描述符也放进fdset
		FD_SET(STDIN_FILENO, &fdset);	// 标准输入放如fdset

		max_sd = sockfd > max_sd ? sockfd : max_sd;
		max_sd = STDIN_FILENO > max_sd ? STDIN_FILENO : max_sd;	// 得到最大文件描述符

		select(max_sd+1, &fdset, NULL, NULL, (struct timeval *)0); // 等待描述符

		int id;//发送消息类型
		int enter_cnt = 0; // 换行符个数

/*-------------------------------针对键盘输入的情况-------------------------------------------*/

		if(FD_ISSET(STDIN_FILENO, &fdset)) {	// 检测是否有键盘输入
			bzero(wbuf, BUFFER_SIZE);
			if(fgets(wbuf, sizeof(wbuf), stdin)) {
				if(last_head == '\n' && wbuf[0] == '\n') {
					strcpy(wbuf, "\n\n");
					for(pos = head->next; pos != NULL; pos = pos->next) {
						write(pos->sock, wbuf, BUFFER_SIZE);
						del_node(head, pos->sock);
						client_cnt--;
					}
					return 0;
				}
				else {
					if(strlen(wbuf) == 1) {
						last_head = wbuf[0];
						continue;
					}

					int i, broadcast = 0;	// 不符合"number:information"形式的字符串被认为广播
					for(i = 0; wbuf[i] != ':'; i++) {
						if(!isdigit(wbuf[i]) || wbuf[i] == '\0') {
							broadcast = 1;
							break;
						}
					}
					
					if(broadcast) {	//  广播情况，把信息发送给每个client
						for(pos = head->next; pos != NULL; pos = pos->next) {
							write(pos->sock, wbuf, BUFFER_SIZE);
						}
					}
					else {	// 非广播情况，发送信息给特定client
						char str[32768];
						strcpy(str, wbuf);
						str[i] = '\0';
						id = atoi(str);
						
						if(id > max_sd || id <0) {	// 特例：如果发现id过大，依然广播
							for(pos = head->next; pos != NULL; pos = pos->next) {
								write(pos->sock, wbuf, BUFFER_SIZE);
							}	
						}

						// 只考虑转发，并不考虑发送给自身的情况
						for(pos = head->next; pos != NULL; pos = pos->next) {
							if(pos->sock == id) {
								write(pos->sock, wbuf+1+i, BUFFER_SIZE);
								break;
							}
						}
					}
				}
			}
		}

/*-------------------------------针对client传数据的情况-------------------------------------------*/

		for(pos=head->next;pos!=NULL;pos = pos->next)  {    // 检查哪个套接字有响应
			if(FD_ISSET(pos->sock, &fdset)) {    // 判断pos->sock这个文件描述符指向的客户端有没有数据写过来
				bzero(rbuf,BUFFER_SIZE);
				read(pos->sock, rbuf, BUFFER_SIZE);
				
                if(strcmp(rbuf,"\n\n")==0) {    // 若客户端发来的信息为两次回车,则取消这个客户端的结点。
					printf("client %d has left\n", pos->sock);	
					del_node(head,pos->sock);
				}
                else {
					if(strlen(rbuf) == 1) {	// 如果发来的消息为\n，则不作出处理
						if(enter_cnt == 0) {
							enter_cnt++;
							fputs(rbuf, stdout);
						}
						else {
							enter_cnt = 0;
						}
						continue;
					}
					
					int i, only_send_to_server = 0;	// 不符合"number:information"形式的字符串被认为无需转发
					for(i = 0; rbuf[i] != ':'; i++) {
						if(!isdigit(rbuf[i]) || rbuf[i] == '\0') {
							only_send_to_server = 1;
							break;
						}
					}

					if(only_send_to_server)
						fputs(rbuf, stdout);
					else {
						char str[32768];
						strcpy(str, rbuf);
						str[i] = '\0';
						int id = atoi(str);

						if(id > max_sd || id < 0) 	// id过大，仍然认为该信息无需转发
							fputs(rbuf, stdout);

						write(id, rbuf+i+1, BUFFER_SIZE);
					}
				}
			}
		}
	}
	return 0;
}