# coding=UTF-8
import fabfile
import os
from fabric.api import *

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('flink', 'localuser')
env.password = cf.get('flink', 'localuser_passwd')
env.hosts = cf.get('flink', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('flink', 'sudouser')
sudouser_passwd = cf.get('flink', 'sudouser_passwd')
# 定义软件参数
flink_local_file = cf.get('flink', 'flink_local_file')
flink_folder = cf.get('flink', 'flink_folder')
# 需要拼接的字符串
flink_upload_file_path = os.path.join('/home', env.user, 'flink.tar.gz').replace('\\', '/')
flink_home = os.path.join('/home', env.user, flink_folder).replace('\\', '/')
flink_config_folder = os.path.join(flink_home, 'conf').replace('\\', '/')
# 依赖
master_ip = cf.get('flink', 'master_ip')
slaves_ip = cf.get('flink', 'slaves_ip').split(',')


# 安装
# 最简单的安装，单master
# 后期可根据需要增加on yarn;zookeeper高可用;log写hdfs;等配置参数
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(flink_local_file, flink_upload_file_path)
    # 解压&删除
    run('tar -zxvf flink.tar.gz && rm -f flink.tar.gz')
    # 开始配置flink
    with cd(flink_config_folder):
        run('cat /dev/null > masters')
        run('cat /dev/null > slaves')
        run('sed -i "s/jobmanager.rpc.address: localhost/' + 'jobmanager.rpc.address: ' + master_ip + '/g" flink-conf.yaml')  # flink-conf.yaml
        for slave in slaves_ip:
            run('echo ' + slave + '>> slaves')
        run('echo "' + master_ip + ':8081" > masters')


# start
def start():
    if env.host == master_ip:
        with cd(flink_home):
            with settings(prompts={
                'Are you sure you want to continue connecting (yes/no)? ': 'yes'
            }):
                run('sbin/start-cluster.sh')


# stop
def stop():
    if env.host == master_ip:
        with cd(flink_home):
            run('sbin/stop-cluster.sh')
