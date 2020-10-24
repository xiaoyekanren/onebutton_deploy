# coding=UTF-8
import os
import fabfile
from fabric.api import *

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('maven', 'localuser')
env.password = cf.get('maven', 'localuser_passwd')
env.hosts = cf.get('maven', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('maven', 'sudouser')
sudouser_passwd = cf.get('maven', 'sudouser_passwd')
# 定义软件参数
user_home = cf.get('maven', 'user_home')
mvn_local_file = cf.get('maven', 'mvn_local_file')
mvn_folder = cf.get('maven', 'mvn_folder')
# 需要拼接的字符串
mvn_upload_file_path = os.path.join(user_home, 'mvn.tar.gz').replace('\\', '/')
mvn_home = os.path.join(user_home, mvn_folder).replace('\\', '/')
mvn_home_global = '/usr/local/' + mvn_folder  # 全局的JAVA_HOME


# local
def install():
    # 上传
    put(mvn_local_file, mvn_upload_file_path)
    # 解压&删除
    run('tar -zxvf mvn.tar.gz && rm -f mvn.tar.gz')
    # 写入
    run('echo "">> ~/.bashrc')  # 输出空行
    run('echo "">> ~/.bashrc')  # 输出空行
    run('echo "export MAVEN_HOME=' + mvn_home + '" >> ~/.bashrc')  # MAVEN_HOME
    run("echo 'export PATH=$MAVEN_HOME/bin:$PATH' >>~/.bashrc")  # PATH  # 输出$环境变量必须用单引号
    run('source ~/.bashrc')  # 立刻生效
    print('mvn already install at ' + mvn_home)


# global
def install_global():
    # 上传
    put(mvn_local_file, mvn_upload_file_path)
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户
        # 移动文件夹
        sudo('mv ' + mvn_upload_file_path + ' /usr/local/')
        with cd('/usr/local'):  # 进入该目录
            # 解压&删除
            sudo('tar -zxvf mvn.tar.gz && rm -f mvn.tar.gz')
        # 写入
        sudo('echo "">> /etc/profile')  # 输出空行
        sudo('echo "">> /etc/profile')  # 输出空行
        sudo('echo "export MAVEN_HOME=' + mvn_home_global + '" >> /etc/profile')  # MAVEN_HOME
        sudo("echo 'export PATH=$MAVEN_HOME/bin:$PATH' >>/etc/profile")  # PATH  # 输出$环境变量必须用单引号
        sudo('source /etc/profile')  # 立刻生效  # 输出$环境变量必须用单引号
        print('mvn already install at ' + mvn_home_global)


def modify_mirror():
    exist_mvn_home = run('echo $MAVEN_HOME')
    print exist_mvn_home
    with cd(exist_mvn_home + '/conf'):
        with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户
            line = run("cat -n settings.xml |grep '  <mirrors>'|awk {'print $1'}")
            run('sed -i "' + line + 'a/    <mirror>" settings.xml')

