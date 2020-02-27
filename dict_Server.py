'''
name : Tedu
date : 2018-10-1
email: xxx
modules: pymysql
This is a dict project for AID
'''
import os, sys
from socket import *
import time
import signal 
import pymysql
import traceback

#定义需要的全局变量　
DICT_TEXT = "./dict.txt"
HOST = "0.0.0.0"
PORT = 8000
ADDR = (HOST, PORT)

#流程控制
def main():
    #创建数据库连接
    db = pymysql.connect('localhost','root','123456','dict')

    #创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)

    #忽略子进程信号　
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    while True:
        try:
            c, addr = s.accept()
            print("Connect from", addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit("服务器退出")
        except Exception as e:
            print(e)
            continue 

        pid = os.fork()
        if pid == 0:
            s.close()
            do_child(c,db)
        else:
            c.close()
            continue

def do_child(c,db):
    while True:
        data = c.recv(1024).decode()
        print(c.getpeername(),":",data)
        if (not data) or data[0] == 'E':
            c.close()
            sys.exit(0)
        elif data[0] == 'R':
            do_register(c, db, data)
        elif data[0] == 'L':
            do_login(c, db, data)
        elif data[0] == 'Q':
            do_query(c, db, data)
        elif data[0] == 'H':
            do_hist(c, db, data)


def do_query(c, db, data):
    print("查询单词操作")
    l = data.split(' ')
    name = l[1]
    word = l[2]
    cursor = db.cursor()
    def insert_hist():
        try:
            sql = "insert into hist(name,word,time) values(%s,%s,%s)"
            cursor.execute(sql,[name,word,time.ctime()])
            db.commit()
        except Exception as e:
            traceback.print_exc(e)
            db.rollback()
            c.send(b'None')
            return 
        else:
            return "OK"
            

    try:
        sql = "select * from words where word='%s';" % word
        cursor.execute(sql)
        db.commit()
        r = cursor.fetchone()
    except Exception as e:
        traceback.print_exc(e)
        db.rollback()
        c.send(b'None')
        return
    else:
        if r != None:           
            res = insert_hist()
            if res == 'OK':
                c.send("{} : {}".format(r[1], r[2]).encode())
        
        else:
            print("查词失败")
            c.send(b'None')


def do_login(c, db, data):
    print("登录操作")
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()

    sql = "select * from user where name='%s' and passwd='%s'" % (name,passwd)
    cursor.execute(sql)
    r = cursor.fetchone()

    if r == None:
        c.send(b'FAIL')
        return
    else:
        c.send(b'OK')
        print("登录成功%s" % name)


def do_register(c,db,data):
    print("注册操作")
    l = data.split(' ')
    name = l[1]
    passwd = l[2]
    cursor = db.cursor()

    sql = "select * from user where name='%s'" % name
    cursor.execute(sql)
    r = cursor.fetchone()

    if r != None:
        c.send(b'EXISTS')
        return
    #如果用户不存在插入用户
    sql = "insert into user (name,passwd) values \
        ('%s','%s')"%(name,passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except:
        db.rollback()
        c.send(b'FAIL')
    else:
        print("注册成功 %s" % name)


def do_hist(c, db, data):
    l = data.split(' ')
    name = l[1]
    sql = "select * from hist where name='%s'" % name
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    r = cursor.fetchall()
    print(r)
    if r == None:
        print("没有查询记录")
        c.send(b'None')
    else:
        histr = ''
        for line in r:
            histr += "{} : {}\n".format(line[2], line[3])   
        c.send(histr.encode())
        
    
    

if __name__ == "__main__":
    main()















