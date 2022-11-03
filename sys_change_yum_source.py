# coding=UTF-8
import fabfile
from fabric.api import *

section = 'change_yum'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts = cf.get(section, 'hosts').split(',')
env.user = cf.get(section, 'sudouser')
env.password = cf.get(section, 'sudouser_passwd')
sudouser = cf.get(section, 'sudouser')
sudouser_passwd = cf.get(section, 'sudouser_passwd')


# 安装
def install():
    sudo("sudo sed -e 's|^mirrorlist=|#mirrorlist=|g' \
         -e 's|^#baseurl=http://mirror.centos.org|baseurl=https://mirrors.tuna.tsinghua.edu.cn|g' \
         -i.bak \
         /etc/yum.repos.d/CentOS-*.repo")
    sudo('echo nameserver 166.111.8.28 > /etc/resolv.conf')
    sudo('yum makecache')
