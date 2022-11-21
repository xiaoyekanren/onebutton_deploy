# coding=utf-8
import fabfile
from fabric.api import *
import os

section = 'jdk'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)
env.host = str(env.host)
software_home = fabfile.get_software_home(section)
# config.ini指定的软件配置
install_for = cf.get(section, 'install_for')
# 需定义的参数
java_home = software_home


def install():
    user_home = str(sudo('cat /etc/passwd | grep \'%s\'' % env.user)).split(':')[-2]
    if install_for == 'alone':
        if env.user == 'root':
            pathfile = '~/.bashrc'
        else:
            pathfile = os.path.join(user_home, '.bashrc')
    elif install_for == 'public':
        pathfile = '/etc/profile'
    else:
        print ("'install_for' can only be 'alone' or 'public' ")
        exit()
    # 检查是否是root用户，是就退出
    # fabfile.check_user(env.user)  # jdk无所谓拿什么安装
    # 上传
    upload_file = fabfile.upload(section)  # 返回upload_file
    # 解压
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压到install_path(在函数decompress里面定义),无返回值
    # 正式开始安装
    sudo('sed -i \'2a\export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH\' %s' % pathfile)  # PATH
    sudo('sed -i \'2a\export CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH\' %s' % pathfile)  # CLASSPATH
    sudo('sed -i \'2a\export JRE_HOME=%s/jre\' %s' % (java_home, pathfile))  # JRE_HOME
    sudo('sed -i \'2a\export JAVA_HOME=%s\' %s' % (java_home, pathfile))  # JAVA_HOME
    # 输出注意事项：
    # 输出结果,输出host类型是list必须带",".join(),否则会显示[u]
    print '--------------------------------------\nfinish install jdk\n--------------------------------------'

    print 'already install for %s' % env.user
    print '--------------------------------------'

    print 'JAVA_HOME is \'%s\' and the system path have been written' % software_home
    print '--------------------------------------'

    print 'If you want to use JDK from root or use sudo,\nyou should execute\'sudo source /etc/profile\' in current shell'
    print 'or add a line to /root/.bashrc, \'source /etc/profile\''
    print '--------------------------------------'
