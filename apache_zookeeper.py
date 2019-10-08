# coding=UTF-8
import fabfile
import os
from fabric.api import *

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('zookeeper', 'localuser')
env.password = cf.get('zookeeper', 'localuser_passwd')
env.hosts = cf.get('zookeeper', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('zookeeper', 'sudouser')
sudouser_passwd = cf.get('zookeeper', 'sudouser_passwd')
# 定义软件参数
zookeeper_local_file = cf.get('zookeeper', 'zookeeper_local_file')
zookeeper_folder = cf.get('zookeeper', 'zookeeper_folder')
# 需要拼接的字符串
zookeeper_upload_file_path = os.path.join('/home', env.user, 'zookeeper.tar.gz').replace('\\', '/')
zookeeper_home = os.path.join('/home', env.user, zookeeper_folder).replace('\\', '/')
zookeeper_config_folder = os.path.join(zookeeper_home, 'conf').replace('\\', '/')
# 依赖
dataDir = cf.get('zookeeper', 'dataDir')
dataLogDir = cf.get('zookeeper', 'dataLogDir')
myid = 1


# 安装
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(zookeeper_local_file, zookeeper_upload_file_path)
    # 解压&删除
    run('tar -zxvf zookeeper.tar.gz && rm -f zookeeper.tar.gz')
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建zookeeper相关文件夹并授权给zookeeper所属用户
        sudo('mkdir -p ' + dataDir)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + dataDir)
        sudo('mkdir -p ' + dataLogDir)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + dataLogDir)
    # 开始配置zookeeper
    with cd(zookeeper_config_folder):  # 进入配置文件目录
        run('touch zoo.cfg')
        run('echo "tickTime=2000" >> zoo.cfg')
        run('echo "initLimit=10" >> zoo.cfg')
        run('echo "syncLimit=5" >> zoo.cfg')
        run('echo "clientPort=2181" >> zoo.cfg')
        run('echo "dataDir=' + dataDir + '" >> zoo.cfg')
        run('echo "dataLogDir=' + dataLogDir + '" >> zoo.cfg')
        i = 1
        while i <= len(env.hosts):
            run('echo "server.' + bytes(i) + '=' + env.hosts[i-1] + ':2888:3888" >>zoo.cfg')
            i += 1
    with cd(dataDir):
        global myid
        run('touch myid')
        run('echo ' + bytes(myid) + ' > myid')
        myid += 1


# 启动
def start():
    with cd(zookeeper_home):
        run('bin/zkServer.sh start')


# 停止
def stop():
    with cd(zookeeper_home):
        run('bin/zkServer.sh stop')
