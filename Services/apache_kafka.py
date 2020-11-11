# coding=UTF-8
import fabfile
from fabric.api import *
import os

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('kafka', 'localuser')
env.password = cf.get('kafka', 'localuser_passwd')
env.hosts = cf.get('kafka', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('kafka', 'sudouser')
sudouser_passwd = cf.get('kafka', 'sudouser_passwd')
# 定义软件参数
kafka_local_file = cf.get('kafka', 'kafka_local_file')
kafka_folder = cf.get('kafka', 'kafka_folder')
log_dirs = cf.get('kafka', 'log_dirs')
zookeeper_hosts = cf.get('kafka', 'zookeeper_hosts').split(',')
# 需要拼接的字符串
kafka_upload_file_path = os.path.join('/home', env.user, 'kafka.tgz').replace('\\', '/')
kafka_home = os.path.join('/home', env.user, kafka_folder).replace('\\', '/')
kafka_config_folder = os.path.join(kafka_home, 'config').replace('\\', '/')
# config
brokerid = 0


# 安装
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(kafka_local_file, kafka_upload_file_path)
    # 解压&删除
    run('tar -zxvf kafka.tgz && rm -f kafka.tgz')
    # 使用sudo用户，创建目录并授权给kafka所属用户
    with settings(user=sudouser, password=sudouser_passwd):
        for log in log_dirs.split(','):
            sudo('mkdir -p ' + log)
            sudo('chown -R ' + env.user + ':' + env.user + ' ' + log)
    # 开始配置kafka
    with cd(kafka_config_folder):
        # server.properties
        global brokerid
        run('sed -i "s:broker.id=0:broker.id=' + bytes(brokerid) + ':" server.properties')  # broker.id
        brokerid += 1
        #
        i = 0
        g = ''
        while i < len(zookeeper_hosts) - 1:  # zookeeper.connect
            g = g + bytes(zookeeper_hosts[i]) + ':2181' + ','
            i += 1
        g = g + bytes(zookeeper_hosts[i])
        run('sed -i "s/localhost:2181/' + g + '/g" server.properties')
        #
        run('sed -i "s:/tmp/kafka-logs:' + log_dirs + ':g" server.properties')  # log_dirs
        run('echo "" >> server.properties')  # 输出空行
        run('echo "listeners=PLAINTEXT://' + env.host + ':9092" >> server.properties')  # listeners


# 启动
def start():
    with cd(kafka_home + '/bin'):
        run('rm -f nohup.out')
        run('rm -f start.sh')
        run('touch start.sh')
        run('chmod 755 start.sh')
        run('echo "#/bin/bash" >>start.sh')
        run('echo "nohup ./kafka-server-start.sh ../config/server.properties 1>nohup.out 2>nohup.out &" >>start.sh')
        run('sh start.sh && sleep 0.1')


# 停止
def stop():
    kafka_path = os.path.join('/home/', env.user, cf.get('kafka', 'kafka_folder')).replace('\\', '/')
    with cd(kafka_path + '/bin'):
        run('./kafka-server-stop.sh')
    # fab -w可以跳过失败的


def test():
    print 'Start Test~~~~~~~~'
