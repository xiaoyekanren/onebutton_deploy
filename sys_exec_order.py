# coding=UTF-8
import fabfile
from fabric.api import sudo, run, env, settings

section = 'exec_order'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts = cf.get(section, 'hosts').split(',')
env.user = cf.get(section, 'user')
env.password = cf.get(section, 'user_passwd')
sudouser = cf.get(section,'sudouser')
sudouser_passwd = cf.get(section, 'sudouser_passwd')



# 安装 
def install():
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建文件夹并授权给hadoop所属用户
        sudo('setenforce 0')
        sudo('sed -i ":^SELINUX=.*:SELINUX=disabled:" /etc/selinux/config')
     