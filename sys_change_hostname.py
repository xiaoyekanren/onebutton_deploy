# coding=UTF-8
import fabfile
from fabric.api import *

section = 'change_hostname'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts = cf.get(section, 'hosts').split(',')
env.user = cf.get(section, 'sudouser')
env.password = cf.get(section, 'sudouser_passwd')


# 安装
def install():
    hostname = str(env.host).split('.')[-1]
    if len(hostname) == 1:
        hostname = 'node0' + hostname
    else:
        hostname = 'node' + hostname
    # print hostname
    old_hostname = sudo('cat /etc/hostname')
    sudo('sed -i \'s:%s:%s:g\' /etc/hostname' % (old_hostname, hostname))
    sudo('sed -i -e \'/^127.0.1.1.*/d\' /etc/hosts')


