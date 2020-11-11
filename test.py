# coding=UTF-8
import fabfile
from fabric.api import *
from os import path
from time import strftime


# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('test', 'localuser')
env.password = cf.get('test', 'localuser_passwd')
env.hosts = cf.get('test', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('test', 'sudouser')
sudouser_passwd = cf.get('test', 'sudouser_passwd')


# 这个是将shell的输出结果传给python程序
# 应用于python需要取得某些值，在给其他地方去定义
def test1():
    bbb = run("whoami", shell=False, pty=False)
    print bbb


# 这个是忽略类似于模拟shell命令的一步一步执行的情况，根据提示信息，输出相对应的值
# 应用于添加用户、hadoop第一次启动，等需要根据提示信息填值的情况
def test2():
    with settings(prompts={
        'Are you sure you want to continue connecting (yes/no)? ': 'yes'
    }):
        run('whoami')


# 这个貌似是碰到错误继续执行？
def test3():
    with settings(warn_only=True):
        run("whoami")


def test4():
    aaa = run('pwd')

    print aaa[:-1]


def test5():
    a=b=3
    print a, b


def test6():
    try:
        aaa = cf.get('66666', 'loc7777aluser')
    except:
        aaa = ''
        print aaa

def test7():
    print '我草泥马'
