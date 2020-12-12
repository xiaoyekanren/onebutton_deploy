# coding=UTF-8
import fabfile
from fabric.api import *

section = 'hostname_to_host'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts = cf.get(section, 'hosts').split(',')
env.user = cf.get(section, 'sudouser')
env.password = cf.get(section, 'sudouser_passwd')
ip = cf.get(section, 'ip').split(',')
hostname = cf.get(section, 'hostname').split(',')  # split即以逗号分隔每项
# sum一下host数量
hostname_sum = len(hostname)
ip_sum = len(ip)


# 安装
def install():
    if ip_sum == hostname_sum:
        for i in range(hostname_sum):  # 做循环，将IP和主机名写入hosts文件
            sudo('echo "%s %s" >> /etc/hosts' % (ip[i], hostname[i]))
    else:
        print('ip and hostname must one-to-one,please check.......exit')  # config.ini里面的ip 和hostname 不相等
        exit()

