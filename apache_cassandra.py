#!/usr/bin/env python
# encoding: utf-8
from fabric.api import *
import fabfile
import os

# 读取fabfile文件的cf参数,读取passwd.ini文件
cf = fabfile.cf
# 定义env
env.user = cf.get('cassandra', 'localuser')
env.password = cf.get('cassandra', 'localuser_passwd')
env.hosts = cf.get('cassandra', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('cassandra', 'sudouser')
sudouser_passwd = cf.get('cassandra', 'sudouser_passwd')
# 定义软件参数
cassandra_local_file = cf.get('cassandra', 'cassandra_local_file')
cassandra_folder = cf.get('cassandra', 'cassandra_folder')  # 即解压之后的文件夹名称
data_directory = cf.get('cassandra', 'data_directory').split(',')
listening_Method = cf.get('cassandra', 'listening_Method')
listening_interface_name = cf.get('cassandra', 'listening_interface_name')
rpc_Method = cf.get('cassandra', 'rpc_Method')
rpc_interface_name = cf.get('cassandra', 'rpc_interface_name')
# 需要拼接的字符串
cassandra_upload_file_path = os.path.join('/home', env.user, 'cassandra.tar.gz').replace('\\', '/')
cassandra_home = os.path.join('/home', env.user, cassandra_folder).replace('\\', '/')
cassandra_config_folder = os.path.join(cassandra_home, 'conf').replace('\\', '/')
# system_log = os.path.join(cassandra_home, 'system_log').replace('\\', '/')  # 这个还是不要配置了，默认吧
saved_caches = os.path.join(cassandra_home, 'data', 'saved_caches').replace('\\', '/')
commitlog_directory = os.path.join(cassandra_home, 'data', 'commitlog').replace('\\', '/')
hints_directory = os.path.join(cassandra_home, 'data', 'hints').replace('\\', '/')


# listing_interface是集群互相访问的端口，rpc_interface是对外提供服务的端口，两个IP地址，屏蔽掉就行
# 以后每次部署，这个地方要改正
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(cassandra_local_file, cassandra_upload_file_path)
    # 解压&删除
    run('tar -zxvf cassandra.tar.gz && rm -f cassandra.tar.gz')
    # 创建文件夹
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建文件夹并授权给cassandra所属用户
        for folder in data_directory:
            sudo('mkdir -p ' + folder)
            sudo('chown -R ' + env.user + ':' + env.user + ' ' + folder)
    run('mkdir -p ' + commitlog_directory)
    run('mkdir -p ' + hints_directory)
    run('mkdir -p ' + saved_caches)
    # run('mkdir -p ' + system_log)
    # 开始配置
    with cd(cassandra_config_folder):
        # 修改cassandra.yaml文件
        run('sed -i ' + "'s/Test Cluster/Cassandra Cluster/'" + ' cassandra.yaml')  # 修改集群名称
        run('echo "data_file_directories:" >> cassandra.yaml')  # 配置数据文件路径
        for folder in data_directory:  # 考虑多路径的情况
            run('echo "     - ' + folder + '" >> cassandra.yaml')
        run('echo "commitlog_directory: ' + commitlog_directory + '" >> cassandra.yaml')  # Commitlog日志路径
        run('echo "saved_caches_directory: ' + saved_caches + '" >> cassandra.yaml')  # saved_caches缓存路径
        run('echo "hints_directory: ' + hints_directory + '" >> cassandra.yaml')  # hints_directory缓存路径
        run('sed -i ' + "'s/commitlog_segment_size_in_mb: 32/commitlog_segment_size_in_mb: 256/'" + ' cassandra.yaml')  # commitlog_segment_size大小
        run("sed -i 's/" + 'seeds: "127.0.0.1"/seeds: "' + ','.join(env.hosts) + '"' + "/' cassandra.yaml")  # 配置seeds，即把全部主机添加进来，使用<','.join(env.hosts)>将list转为str

        if listening_Method == "listen_address":
            run('sed -i ' + "'s/listen_address: localhost/listen_address: " + env.host + "/' cassandra.yaml")  # 指定当前IP为listen_address
        elif listening_Method == "listen_interface":
            if listening_interface_name == "":
                print ("listening_interface_name can't empty")
                exit()
            run('sed -i ' + "'s/listen_address: localhost/#listen_address: localhost/' cassandra.yaml")  # 屏蔽掉listen_address
            run('sed -i ' + "'s/# listen_interface: eth0/listen_interface: " + listening_interface_name + "/' cassandra.yaml")  # 指定网卡名称为listen_interface，同上面的listen_address冲突
        else:
            print ('Must specify listening_Method is "listen_address" or "listen_interface"')
            exit()

        run('sed -i ' + "'s/start_rpc: false/start_rpc: true/'" + ' cassandra.yaml')  # 开启rpc
        if rpc_Method == "rpc_address":
            run('sed -i ' + "'s/rpc_address: localhost/rpc_address: 0.0.0.0/' cassandra.yaml")  # 指定0.0.0.0为rpc_address
            run('sed -i ' + "'s/# broadcast_rpc_address: 1.2.3.4/broadcast_rpc_address: " + env.host + "/' cassandra.yaml")
        elif rpc_Method == "rpc_interface":
            if rpc_interface_name == "":
                print ("listening_interface_name can't empty")
                exit()
            run('sed -i ' + "'s/rpc_address: localhost/# rpc_address: localhost/' cassandra.yaml")  # 屏蔽掉rpc_address
            run('sed -i ' + "'s/# rpc_interface: eth1/rpc_interface: " + rpc_interface_name + "/' cassandra.yaml")  # 指定rpc_interface的网卡名称,同上面rpc_address冲突
        else:
            print ('Must specify rpc_Method is "rpc_address" or "rpc_interface"')
            exit()

        run('sed -i ' + "'s/#memtable_flush_writers: 2/memtable_flush_writers: 4/'" + ' cassandra.yaml')
        run('sed -i ' + "'s/thrift_framed_transport_size_in_mb: 15/thrift_framed_transport_size_in_mb: 200/'" + ' cassandra.yaml')
        run('sed -i ' + "'s/read_request_timeout_in_ms: 5000/read_request_timeout_in_ms: 20000/'" + ' cassandra.yaml')
        run('sed -i ' + "'s/range_request_timeout_in_ms: 10000/range_request_timeout_in_ms: 120000/'" + ' cassandra.yaml')
        run('sed -i ' + "'s/write_request_timeout_in_ms: 2000/write_request_timeout_in_ms: 300000/'" + ' cassandra.yaml')

        # 修改logback.xml文件
        run('sed -i ' + "'s/20MB/50MB/'" + ' cassandra.yaml')  # 修改system和debug日志文件大小
        run("sed -i '" + 's:<appender-ref ref="' + 'ASYNCDEBUGLOG"' + ' /> <!--:<!--appender-ref ref="' + 'ASYNCDEBUGLOG' + '"' + ' --> <!--:' + "' logback.xml")  # 屏蔽ASYNC DEBUG LOG日志
        run("sed -i '" + '$i\  <logger name="' + 'org.apache.cassandra.utils.StatusLogger"' + ' level="' + 'OFF"/>' + "' logback.xml")  # 增加到倒数第二行
        run("sed -i '" + "$i\  <!--Status log very very more and more-->'" + " logback.xml")

        # 修改cassandra-env.sh文件
        run("sed -i 's/#MAX_HEAP_SIZE=" + '"4G"/MAX_HEAP_SIZE="4G"/' + "' cassandra-env.sh")
        run("sed -i 's/#HEAP_NEWSIZE=" + '"800M"/HEAP_NEWSIZE="800M"/' + "' cassandra-env.sh")
        run("sed -i 's/JVM_OPTS=" + '"$JVM_OPTS -Xss256k"/JVM_OPTS="$JVM_OPTS -Xss228k"/' + "' cassandra-env.sh")


# 全部开始
def start():
    with cd(cassandra_home + '/bin'):
        run('rm -f nohup.out')
        run('rm -f start.sh')
        run('touch start.sh')
        run('chmod 755 start.sh')
        run('echo "#/bin/bash" >>start.sh')
        run('echo "nohup ./cassandra >./nohup.output 2>&1 &" >>start.sh')
        run('sh start.sh && sleep 0.1')


# 全部停止
# fab -f apache_cassandra.py stop -w
# 此地需要增加-w参数，否则会报错退出
def stop():
    with settings(user=sudouser, password=sudouser_passwd):
        sudo('pgrep -u ' + env.user + ' -f cassandra | xargs kill -9')


# 增大普通用户最大进程数
def modify_system():
    with settings(user=sudouser, password=sudouser_passwd):
        sudo('echo ' + "'* soft nofile 32768\n* hard nofile 65535'" + ' >> /etc/security/limits.conf')  # 最大文件句柄数设置
        sudo('sysctl -w vm.max_map_count=131072')  # 修改mmap file 线程数
        sudo('echo ' + "'vm.max_map_count=131072'" + ' >> /etc/sysctl.conf')
        # sudo('ulimit -a')  # 查看所有限制值
