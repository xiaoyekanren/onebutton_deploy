# coding=UTF-8
import fabfile
import os
from fabric.api import *

# 读取fabfile文件的cf参数,读取passwd.ini文件
cf = fabfile.cf
# 定义env
env.user = cf.get('scala', 'localuser')
env.password = cf.get('scala', 'localuser_passwd')
env.hosts = cf.get('scala', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('scala', 'sudouser')
sudouser_passwd = cf.get('scala', 'sudouser_passwd')
# 定义软件参数
scala_local_file = cf.get('scala', 'scala_local_file')
scala_folder = cf.get('scala', 'scala_folder')  # 即解压之后的文件夹名称
# 需要拼接的字符串
scala_upload_file_path = os.path.join('/home', env.user, 'scala.tgz').replace('\\', '/')  # Windows's os.path.join会出现反斜杠，用replace将反斜杠替换成斜杠
scala_home = os.path.join('/home', env.user, scala_folder).replace('\\', '/')  # JAVA_HOME  # Windows's os.path.join会出现反斜杠，用replace将反斜杠替换成斜杠
scala_home_global = '/usr/local/' + scala_folder  # 全局的JAVA_HOME


# 安装
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(scala_local_file, scala_upload_file_path)
    # 解压&删除
    run('tar -zxvf scala.tgz && rm -f scala.tgz')
    sudo('echo "">>/etc/profile')
    sudo('echo "# scala_path" >> ~/.bashrc')
    sudo('echo "">>/etc/profile')
    sudo('echo "export SCALA_HOME=' + scala_home + '" >> ~/.bashrc')
    sudo("echo 'export PATH=$SCALA_HOME/bin:$PATH' >> ~/.bashrc")
    sudo('source ~/.bashrc')


def install_global():
    # 上传
    put(scala_local_file, scala_upload_file_path)
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户
        # 移动文件夹
        sudo('mv ' + scala_upload_file_path + ' /usr/local/')
        with cd('/usr/local'):  # 进入该目录
            sudo('tar -zxvf scala.tgz && rm -f scala.tgz')  # 解压&删除
        # 写入
        sudo('echo "">> /etc/profile')  # 输出空行
        sudo('echo "">> /etc/profile')  # 输出空行
        sudo('echo "export SCALA_HOME=' + scala_home_global + '" >> /etc/profile')  # JAVA_HOME
        sudo("echo 'export PATH=$SCALA_HOME/bin:$PATH' >>/etc/profile")  # PATH  # 输出$环境变量必须用单引号
        sudo('source /etc/profile')  # 立刻生效  # 输出$环境变量必须用单引号