# coding=UTF-8
import python2.fabfile
from fabric.api import *

# 读取fabfile文件的cf参数
cf = python2.fabfile.cf
# 定义env
env.user = cf.get('ssh_root_allow', 'sudouser')
env.password = cf.get('ssh_root_allow', 'sudouser_passwd')


# 安装
def install():
    sudo('sed -i ' + "'s:prohibit-password:yes:'" + ' /etc/ssh/sshd_config')
    sudo('/etc/init.d/ssh restart')
