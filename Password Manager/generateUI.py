from tkinter import *
import string
from tkinter import messagebox
import tkinter.font as tkFont
from tkinter import ttk
from password import *
import pyperclip
import copy


def getKey(checkVar):
    a = ""
    if checkVar & 1 != 0:
        a += string.digits
    if checkVar & 2 != 0:
        a += string.ascii_lowercase
    if checkVar & 4 != 0:
        a += string.ascii_uppercase
    if checkVar & 8 != 0:
        a += string.punctuation
    num1 = int(pwd_length_entry.get())  # num1为密码个数
    while num1 > len(a):
        a += a
    if checkVar & 8 == 0 or (checkVar & 8 != 0 and checkVar & 4 == 0 and checkVar & 2 == 0 and checkVar & 1 == 0):
        key = random.sample(a, num1)
        keys = "".join(key)
        return keys
    else:  # 包含标点符号和其他选项的情况
        key = random.sample(a, num1)
        pun_cnt = 0
        limit_cnt = (num1 // 4) + 1  # 标点符号最大值
        update_list = []
        flag = False  # 是否进行符号的更改

        for i in range(len(key)):
            if key[i] in string.punctuation:
                update_list.append(i)
                pun_cnt += 1
                if pun_cnt > limit_cnt:
                    flag = True

        if flag:
            for i in range(pun_cnt - limit_cnt):
                index = random.randint(0, len(update_list) - 1)
                key[update_list[index]] = random.sample(set(a) - set(string.punctuation), 1)[0]

        keys = "".join(key)
        return keys


def show(sth):
    text.delete(1.0, END)
    text.insert(1.0, sth)


def output():
    inputTxt2 = pwd_count_entry.get()
    key = []
    outputkey = ""
    # 密码个数？
    if inputTxt2 == "":
        messagebox.showinfo("提示", "请填写个数")
        return
    else:
        num2 = int(inputTxt2)  # num2为密码个数
        # 长度？
    inputTxt1 = pwd_length_entry.get()
    if inputTxt1 == "":
        messagebox.showinfo("提示", "请填写长度")
        return

    checkVar = rVar1.get() + rVar2.get() + rVar3.get() + rVar4.get()
    if checkVar == 0:
        messagebox.showinfo("提示", "请勾选至少一项内容")
        return

    for i in range(num2):
        password = getKey(checkVar)
        flag = check([password])[0]
        if flag == 0:
            strength = ' [弱]'
        elif flag == 1:
            strength = ' [中]'
        else:
            strength = ' [强]'
        outputkey += password + strength + '\n'
    show(outputkey)


def btn_detect():
    """ 检测键 处理函数 """
    password = pwd_entry.get()

    if password == "":
        messagebox.showinfo("提示", "请输入待检测密码")
        return
    else:
        flag = check([password])[0]
        # flag = detect(password)
        if flag == 0:
            detect_result.config(text='弱', bg='red')
        elif flag == 1:
            detect_result.config(text='中', bg='yellow')
        else:
            detect_result.config(text='强', bg='green')


def btn_storage(new_name, new_pwd, main_pwd, index_frame):
    # print(current_mp)
    current_mp = load(main_pwd)
    if len(current_mp) == 12 and (new_name not in current_mp):  # 规定密码上限，但是允许修改密码
        messagebox.showinfo('提示', '密码数量已达上限')
    else:
        if new_name != '' and new_pwd != '':
            # init(main_pwd_entry.get())  # 主密码
            dump(new_name, new_pwd)
            current_mp = load(main_pwd)
            refresh_data(current_mp, index_frame)
            if have_repeat_passwd() > 0:
                messagebox.showinfo('提示', '目前有' + str(have_repeat_passwd() + 1) + '个重复密码，建议进行修改')


def btn_eye(pwd, eye_btn):
    if pwd['show'] == '●':
        pwd.config(show='')
        eye_btn.config(text='隐藏')
    else:
        pwd.config(show='●')
        eye_btn.config(text='显示')


def btn_copy(pwd):
    pyperclip.copy(pwd.get())


def btn_delete(pwd_name, pwd_mp, index_frame):
    new_mp = copy.deepcopy(pwd_mp)
    new_mp.pop(pwd_name)
    # print(pwd_mp)
    # print('new mp' + str(new_mp))
    with open("./src/passwd", 'wb') as file:
        pickle.dump(new_mp, file)
    refresh_data(new_mp, index_frame)


def create_index(pwd_name, pwd_map, index_frame):
    # print(pwd_name + ' ' + password)
    menu_index = Frame(index_frame)
    name = Label(menu_index, text=pwd_name, width=7)
    pwd = Entry(menu_index, width=20, show='●')
    pwd.insert(0, pwd_map[pwd_name])
    eye_btn = Button(menu_index, text='显示', width=3, command=lambda: btn_eye(pwd, eye_btn))
    copy_btn = Button(menu_index, text='复制', width=3, command=lambda: btn_copy(pwd))
    delete_btn = Button(menu_index, text='删除', width=3, command=lambda: btn_delete(pwd_name, pwd_map, index_frame))

    name.grid(row=0, column=0)
    pwd.grid(row=0, column=1, padx=5)
    eye_btn.grid(row=0, column=2, padx=1)
    copy_btn.grid(row=0, column=3, padx=1)
    delete_btn.grid(row=0, column=4, padx=1)

    return menu_index


def refresh_data(pwd_mp, index_frame):
    for widget in index_frame.winfo_children():
        widget.destroy()

    # print(pwd_mp)
    current_row = 0
    for key in pwd_mp:
        # print(key + ':' + pwd_mp[key])
        current_index = create_index(key, pwd_mp, index_frame)
        # current_index = create_index(key, pwd_mp[key], index_frame)
        current_index.grid(row=current_row)
        current_row += 1


def btn_door(main_pwd):
    pwd_mp = load(main_pwd)
    if pwd_mp is not None:
        for widget in tab_storage.winfo_children():
            widget.destroy()

        storage_frame = Frame(tab_storage, width=360)
        index_frame = Frame(tab_storage, width=360)

        storage_frame.grid(row=0, padx=20, pady=10)
        index_frame.grid(row=1, pady=20)

        # 1. 存储部分

        name_label = Label(storage_frame, text='名称', width=10)
        storage_pwd_label = Label(storage_frame, text='密码')
        name_entry = Entry(storage_frame, width=10)
        storage_pwd_entry = Entry(storage_frame, width=20)
        storage_pwd_btn = Button(
            storage_frame, text='存储', width=10,
            command=lambda: btn_storage(name_entry.get(), storage_pwd_entry.get(), main_pwd, index_frame))

        name_label.grid(row=0, column=0)
        storage_pwd_label.grid(row=0, column=1)
        name_entry.grid(row=1, column=0)
        storage_pwd_entry.grid(row=1, column=1, padx=5)
        storage_pwd_btn.grid(row=1, column=2)

        refresh_data(pwd_mp, index_frame)


window = Tk()
window.title('Password Manager')
window.geometry('380x530+300+200')
window.resizable(width=False, height=False)

nb = ttk.Notebook(window, width=370, height=480)
nb.grid(row=0, padx=5, pady=10)

tab_detect = Frame(nb)
nb.add(tab_detect, text='检测和生成')

tab_storage = Frame(nb)
nb.add(tab_storage, text='存储和提取')

# 检测强度和生成密码两部分
detect_frame = Frame(tab_detect)
generate_frame = Frame(tab_detect)

detect_frame.grid(row=0)
generate_frame.grid(row=1)

# tag1 ------------------------------------------------------------------------
# 1. 检测强度部分

title_font = tkFont.Font(size=15, weight=tkFont.BOLD)
title1 = Label(detect_frame, text='强度检测', font=title_font)
pwd_label = Label(detect_frame, text='密码', width=10)
pwd_entry = Entry(detect_frame, width=25)
detect_btn = Button(detect_frame, text='检测', width=10, command=btn_detect)
detect_result = Label(detect_frame, text='弱/中/强', width=20)

title1.grid(row=0, padx=10, pady=10)
pwd_label.grid(row=1, column=0, padx=10, pady=10)
pwd_entry.grid(row=1, column=1, columnspan=3, padx=10, pady=10)
detect_btn.grid(row=2, column=0, padx=10, pady=10)
detect_result.grid(row=2, column=1, columnspan=3, padx=10, pady=10)

# 2. 生成密码部分

title2 = Label(generate_frame, text='密码生成', font=title_font)
pwd_length = Label(generate_frame, text='密码长度', width=10)
pwd_count = Label(generate_frame, text='密码个数', width=10)
pwd_length_entry = Entry(generate_frame, width=25)
pwd_count_entry = Entry(generate_frame, width=25)
btn_generate = Button(generate_frame, text='生成', width=10, command=output)
text = Text(generate_frame, width=45, height=6)

# 盛装复选按钮的盒子
checkBox = Frame(generate_frame)
checkBox.grid(row=3, columnspan=2, sticky=W, padx=30, pady=10)
# 数字？
rVar1 = IntVar()
r1 = Checkbutton(checkBox, text="存在数字", variable=rVar1, onvalue=1, offvalue=0)  # 修改
# 小写字母？
rVar2 = IntVar()
r2 = Checkbutton(checkBox, text="存在小写字母", variable=rVar2, onvalue=2, offvalue=0)  # 修改
# 大写字母？
rVar3 = IntVar()
r3 = Checkbutton(checkBox, text="存在大写字母", variable=rVar3, onvalue=4, offvalue=0)  # 修改
# 标点符号？
rVar4 = IntVar()
r4 = Checkbutton(checkBox, text="存在标点", variable=rVar4, onvalue=8, offvalue=0)  # 修改

title2.grid(row=0, padx=20, pady=10)
pwd_length.grid(row=1, column=0, padx=10, pady=10)
pwd_length_entry.grid(row=1, column=1, padx=10, pady=10)
pwd_count.grid(row=2, column=0)
pwd_count_entry.grid(row=2, column=1)

r1.grid(row=0, column=0, sticky=W)
r2.grid(row=0, column=1, sticky=W)
r3.grid(row=1, column=0, sticky=W)
r4.grid(row=1, column=1, sticky=W)

btn_generate.grid(row=4, padx=10, pady=10)
text.grid(row=5, column=0, columnspan=2, padx=20)

# tag2 ------------------------------------------------------------------------

door_frame = Frame(tab_storage)

door_label = Label(door_frame, text='主密码')
door_pwd = Entry(door_frame, show='●')
door_btn = Button(door_frame, text='确认', command=lambda: btn_door(door_pwd.get()))

door_frame.grid(row=0, padx=115, pady=160)

door_label.grid(pady=5)
door_pwd.grid(pady=5)
door_btn.grid(pady=5)

# init('15pwd')

window.mainloop()
