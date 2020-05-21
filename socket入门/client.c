#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <sys/select.h>
#include <netinet/in.h>
#include <netdb.h>
#include <unistd.h>
#include <fcntl.h>
#include <ctype.h>
#define BUFFER_SIZE 32768

int main(int argc, char **argv)
{

    int i, port_number;
    
    /* 通过参数获取主机名称和端口号 */
    char *host, *str_port_number;   // host为主机名

	if(argc != 2) {
        fprintf(stderr, "invalid arguments");
        exit(1);
    }
    else {
        host = argv[1];
        for(i=0; argv[1][i]!=':'; i++) ;
            *(host+i) = '\0';
        str_port_number = argv[1]+i+1;
        port_number = atoi(str_port_number);    // 端口号
        printf("%s / %d\n", host, port_number);
    }

    struct hostent *hp;
    hp = gethostbyname(host);
    
    
    if(!hp) {
        fprintf(stderr, "client: unknow host: %s\n", host);
        exit(1);
    }
	int sockfd;
	char rbuf[BUFFER_SIZE]={0};
	char wbuf[BUFFER_SIZE]={0};
	int max_sd;
 
	int size,on=1;
	int ret;
	fd_set fdset;
	struct sockaddr_in saddr;
	size = sizeof(struct sockaddr_in);
 
	saddr.sin_family = AF_INET;
    saddr.sin_port = htons(port_number);
    if(strcmp(host, "localhost") == 0)
        memcpy(hp->h_addr, &saddr.sin_addr, hp->h_length);
    else
	    saddr.sin_addr.s_addr = inet_addr(host);
    
    bzero(&(saddr.sin_zero), 8);  
	sockfd = socket(AF_INET,SOCK_STREAM,0);
	setsockopt(sockfd,SOL_SOCKET,SO_REUSEADDR,&on,sizeof(on));

	if(connect(sockfd,(struct sockaddr*)&saddr,size) < 0) {
        perror("cilent: connect");
        close(sockfd);
        exit(1);
	}

    char last_head;
	while(1) {
		FD_ZERO(&fdset);
		FD_SET(sockfd, &fdset); // 把监测服务端的描述符集放到集合中
		FD_SET(STDIN_FILENO, &fdset); // STDIN_FILENO这个文件描述符用于监测标准输入（键盘）
		max_sd = sockfd > STDIN_FILENO ? sockfd : STDIN_FILENO;
		select(max_sd+1, &fdset, NULL, NULL, (struct timeval*)0); // 这里的select是设置为一直阻塞到有文件描述符发生响应
 
		if(FD_ISSET(sockfd, &fdset)) {    // 判断是否服务端有数据发过来
			bzero(rbuf, BUFFER_SIZE);
			read(sockfd,rbuf, BUFFER_SIZE);
            if(strcmp(rbuf, "\n\n") == 0) {
				printf("Server has turned off\n");
				return 0;
			}
			fputs(rbuf, stdout);
		}
        
		if(FD_ISSET(STDIN_FILENO, &fdset)) { // 判断键盘是否有数据传过来
			bzero(wbuf, BUFFER_SIZE);
			// scanf("%s",wbuf);
            if(fgets(wbuf, sizeof(wbuf), stdin)) {  // 当输入不是EOF时
                if(last_head == '\n' && wbuf[0] =='\n') {
                    strcpy(wbuf, "\n\n");
                    write(sockfd, wbuf, BUFFER_SIZE);
                    return 0;
                }
                last_head = wbuf[0];
                //把键盘传过来的数据发给服务端
                write(sockfd, wbuf, BUFFER_SIZE);
            }
            else {  // 有EOF
                strcpy(wbuf, "\n\n");
                write(sockfd, wbuf, BUFFER_SIZE);
                return 0;
            }
			
		}
	}
	return 0;
}