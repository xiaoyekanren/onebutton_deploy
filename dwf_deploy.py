# coding=utf-8
from fabric.api import *
import fabfile
import os

# 读取fabfile文件的cf参数,读取passwd.ini文件
cf = fabfile.cf
# 定义env
env.user = cf.get('dwf', 'localuser')
env.password = cf.get('dwf', 'localuser_passwd')
env.hosts = cf.get('dwf', 'hosts').split(',')


def check_user_home():
    return sudo("cat /etc/passwd|grep -i ^%s|awk -F ':' {'print $6'}" % env.user)


# 定义sudo用户参数
sudouser = cf.get('dwf', 'sudouser')
sudouser_passwd = cf.get('dwf', 'sudouser_passwd')
dwf_url = cf.get('dwf', 'dwf_url')
# -----------
current_path = user_home = check_user_home()





def check_user():
    if env.user == 'root':
        print ("can't install by root")
        exit()


# 杀死当前全部java进程，虽然是新机器
def killpid():
    with settings(user=sudouser, password=sudouser_passwd):
        run("ps aux | grep '[d]wf-modeler' | awk '{print $2}' | xargs kill -9")
        run("ps aux | grep '[d]wf-app' | awk '{print $2}' | xargs sudo kill -9")
        run("ps aux | grep '[d]wf-monitor' | awk '{print $2}' | xargs kill -9")
        run("ps aux | grep '[p]ostgres' | awk '{print $2}' | xargs sudo kill -9")
        run("ps aux | grep '[t]omcat' | awk '{print $2}' | xargs sudo kill -9")


def upload_release():
    # 下载
    run('wget -O setupfiles.tar.gz %s' % dwf_url)
    # 解压&删除
    run('tar -zxvf setupfiles.tar.gz')
    # 删除
    # run('rm -f setupfiles.tar.gz')
    release_path =


# 安装
def install():
    # 创建opt目录
    sudo('mkdir -p /opt')
    sudo('chown -R %s:%s /opt' % env.user, env.user)


def install_jdk():
