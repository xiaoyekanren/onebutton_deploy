# coding=UTF-8
import fabfile
from fabric.api import *

section = 'zookeeper'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)
software_home = fabfile.get_software_home(section)
# config.ini指定的软件配置
dataDir = cf.get('zookeeper', 'dataDir')
dataLogDir = cf.get('zookeeper', 'dataLogDir')
# 需定义的参数
myid = 1


# 安装
def install():
    # 检查是否是root用户，是就退出
    fabfile.check_user(env.user)
    # 上传
    upload_file = fabfile.upload(section)
    # 解压
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压到install_path(在函数decompress里面定义),无返回值
    # 正式开始安装
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建zookeeper相关文件夹并授权给zookeeper所属用户
        sudo('mkdir -p ' + dataDir)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + dataDir)
        sudo('mkdir -p ' + dataLogDir)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + dataLogDir)
    with cd(software_home + '/conf'):  # 进入配置文件目录
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
    with cd(software_home):
        run('bin/zkServer.sh start')


# 停止
def stop():
    with cd(software_home):
        run('bin/zkServer.sh stop')
