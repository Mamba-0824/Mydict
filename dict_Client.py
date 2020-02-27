#!/usr/bin/python3
#coding=utf-8


import sys
from socket import *
import traceback
import getpass


def main():
    if len(sys.argv) < 3:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
    s = socket()
    try:
        s.connect((HOST, PORT))
    except Exception as e:
        print(e)
        return
    
    while True:
        print(
            '''
            =============== WELCOME ===============
            --- 1.注册       2.登录        3.退出---
            =======================================
            '''
        )
        try:
            cmd = int(input("输入选项>>"))
        except Exception as e:
            print("命令错误")
            continue
        if cmd not in [1, 2, 3]:
            print("请输入正确选项")
            sys.stdin.flush() #清除标准输入
            continue
        elif cmd == 1:
            r = do_register(s)
            if r == 0:
                print("注册成功")
            elif r == 1:
                print("用户存在")
            else:
                print("注册失败")
        elif cmd == 2:
            name = do_login(s)
            if name:
                print("登录成功")
                login(s, name)
            else:
                print("用户名或密码不正确")
        elif cmd == 3:
            s.send(b'E')
            sys.exit("谢谢使用")

def do_register(s):
    while True:
        name = input("User:")
        passwd = getpass.getpass()
        passwd1 = getpass.getpass("Again:")

        if (' ' in name) or (' ' in passwd):
            print("用户名和密码不许有空格")
            continue
        if passwd !=passwd1:
            print("两次密码不一致")
            continue
        
        msg = 'R {} {}'.format(name,passwd)
        #发送请求
        s.send(msg.encode())
        #等待回复
        data = s.recv(128).decode()
        if data == "OK":
            return 0
        elif data == "EXISTS":
            return 1
        else:
            return 2

#以下是客户端登录函数
def do_login(s):
    print("正在登录...")
    while True:
        name = input("User:")
        passwd = getpass.getpass("Password:")

        if (' ' in name) or (' ' in passwd):
            print("用户名或密码格式有误")
            continue
        msg = 'L {} {}'.format(name, passwd)
        s.send(msg.encode())
        #接收服务器响应结果
        data = s.recv(128).decode()
        if data == 'OK':
            return name
        else:
            return None
            

def login(s, name):           
    while True:
        print(
            '''
            ================查询界面=================
            1.查词          2.历史记录         3.退出
            ========================================
            ''')
        try:
            cmd = int(input("输入选项>>"))
        except Exception as e:
            print("命令错误")
            continue
        if cmd not in [1, 2, 3]:
            print("请输入正确选项")
            sys.stdin.flush() #清除标准输入
            continue
        elif cmd == 1:
            do_query(s, name)
        elif cmd == 2:
            do_hist(s, name)
        elif cmd == 3:
            return

def do_query(s, name):
    while True:
        word = input("Please input word: ")
        if (' ' in word):
            print("输入的单词不允许有空隔")
            return
        elif word == '##':
            return    

        msg = "Q {} {}".format(name, word)
        s.send(msg.encode())
        res = s.recv(1024).decode()
        if res != 'None':
            print(res)
        else:
            print("Fail,this word is not exist")
    
def do_hist(s, name):
    s.send("H {}".format(name).encode())
    data = ''
    # while True:
    data += s.recv(4096).decode()
        # if not data:
        #     break
    if data == 'None':
        print("%s没有相关查询记录" % name)
        return
    else:
        print(data)

    

if __name__ == "__main__":
    main()