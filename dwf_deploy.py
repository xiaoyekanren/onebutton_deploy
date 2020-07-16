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
# 定义sudo用户参数
sudouser = cf.get('dwf', 'sudouser')
sudouser_passwd = cf.get('dwf', 'sudouser_passwd')
dwf_url = cf.get('dwf', 'dwf_url')

if cf.get('dwf', 'user_home'):
    user_home = cf.get('dwf', 'user_home')
else:
    user_home = os.path.join('/home' + env.user).replace('\\', '/')


# 杀死当前全部java进程，虽然是新机器
def killpid():
    with settings(user=sudouser, password=sudouser_passwd):
        run("ps aux | grep '[d]wf-modeler' | awk '{print $2}' | xargs kill -9")
        run("ps aux | grep '[d]wf-app' | awk '{print $2}' | xargs sudo kill -9")
        run("ps aux | grep '[d]wf-monitor' | awk '{print $2}' | xargs kill -9")
        run("ps aux | grep '[p]ostgres' | awk '{print $2}' | xargs sudo kill -9")
        run("ps aux | grep '[t]omcat' | awk '{print $2}' | xargs sudo kill -9")




def upload():







# 安装
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 下载
    run('wget -O dwf.tar.gz %s ' % dwf_url)
    # 解压&删除
    run('tar -zxvf dwf.tar.gz')
    #  && rm -f hadoop.tar.gz')

    # 创建opt目录
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建文件夹并授权给hadoop所属用户
        sudo('mkdir -p /opt')

    # 修改配置文件
    with cd(hadoop_config_folder):
        # hadoop-env.sh
        run(
            "sed -i 's:export JAVA_HOME=.*:export JAVA_HOME=" + java_home + ":g' hadoop-env.sh")  # 修改hadoop-env.sh的jdk路径
        # slaves