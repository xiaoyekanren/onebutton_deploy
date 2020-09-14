# coding=UTF-8
import configparser
from fabric.api import *
import os

# fabfirc==1.14.1


# 读取配置文件password.ini
cf = configparser.ConfigParser()
cf.read('config.ini')

# 定义env
env.user = cf.get('keyfree_login', 'localuser')
env.password = cf.get('keyfree_login', 'localuser_passwd')
env.hosts = cf.get('keyfree_login', 'hosts').split(",")
# 需要拼接的字符串
hostsum = len(env.hosts)


# 卸载
def uninstall():
    run('rm -rf ~/.ssh/id_rsa*')  # 删除已有的公钥私钥
    # run('rm -rf ~/.ssh/authorized_keys')  # 删除当前的密钥


# 安装
def install():
    uninstall()
    run('ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""')  # 生成公钥新的公钥私钥

    current_path = "".join(os.path.dirname(os.path.abspath('sys-keyfree_login.py')))  # 获取当前的路径
    current_file_path = os.path.join(current_path, "".join(env.host)).replace('\\', '/')  # 写一个路径+文件名，为下一步骤get提供本地路径+文件名
    get('.ssh/id_rsa.pub', current_file_path)  # 将公钥拿到本地

    if env.host == env.hosts[-1]:  # 即在最后一个主机运行的时候，此时全部主机已经生成了id_rsa，然后执行install2
        os.system('fab -f sys-keyfree_login.py install2')


def install2():
    run('echo "' + addrsa() + '" > .ssh/authorized_keys')
    if env.host == env.hosts[-1]:
        os.system('fab -f sys-keyfree_login.py rmlocalfile')
    run('chmod 600 ~/.ssh/authorized_keys')
    run('chmod 700 ~/.ssh')


def addrsa():
    rsa_global = ''
    i = 0
    while i < hostsum:
        rsa = open(env.hosts[i]).read()
        rsa_global = rsa_global + rsa
        i += 1
    return rsa_global


def rmlocalfile():
    os.remove(env.host)
