# coding=UTF-8
import fabfile
from fabric.api import *
import os

section = 'jdk'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)
software_home = fabfile.get_software_home(section)
# config.ini指定的软件配置
install_for = cf.get(section, 'install_for')
# 需定义的参数
java_home = software_home
if install_for == 'alone':
    pathfile = '~/.bashrc'
elif install_for == 'public':
    pathfile = '/etc/profile'
else:
    print ("'install_for' can only be 'alone' or 'public' ")
    exit()


def install():
    # 检查是否是root用户，是就退出
    fabfile.check_user(env.user)
    # 上传
    upload_file = fabfile.upload(section)  # 返回upload_file
    # 解压
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压到install_path(在函数decompress里面定义),无返回值
    # 正式开始安装
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo修改,该文件必然存在，无需修改权限
        sudo('sed -i \'2a\export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH\' %s' % pathfile)  # PATH
        sudo('sed -i \'2a\export CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH\' %s' % pathfile)  # CLASSPATH
        sudo('sed -i \'2a\export JRE_HOME=%s/jre\' %s' % (java_home, pathfile))  # JRE_HOME
        sudo('sed -i \'2a\export JAVA_HOME=%s\' %s' % (java_home, pathfile))  # JAVA_HOME
