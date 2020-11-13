# coding=UTF-8
import fabfile
from fabric.api import *
import os

section = 'cassandra'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)  # 取得主机列表、用户&密码、sudo用户&密码
software_home = fabfile.get_software_home(section)  # 通过section或者软件home
# config.ini指定的软件配置
listening_Method = cf.get('cassandra', 'listening_Method')
listening_interface_name = cf.get('cassandra', 'listening_interface_name')
rpc_Method = cf.get('cassandra', 'rpc_Method')
rpc_interface_name = cf.get('cassandra', 'rpc_interface_name')
# listing_interface是集群互相访问的端口，rpc_interface是对外提供服务的端口，两个IP地址，屏蔽掉就行
# directory配置
data_directory = cf.get('cassandra', 'data_directory').split(',')
saved_caches = os.path.join(software_home, 'data', 'saved_caches').replace('\\', '/')
commitlog_directory = os.path.join(software_home, 'data', 'commitlog').replace('\\', '/')
hints_directory = os.path.join(software_home, 'data', 'hints').replace('\\', '/')


# 安装
def install():
    fabfile.check_user(env.user)  # 检查是否是root用户，是就退出
    upload_file = fabfile.upload(section)  # 上传
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压,无返回值
    # 正式开始安装
    fabfile.mkdir(commitlog_directory, env.user, sudouser, sudouser_passwd)  # 创建commitlog_directory
    fabfile.mkdir(hints_directory, env.user, sudouser, sudouser_passwd)  # 创建hints_directory
    fabfile.mkdir(saved_caches, env.user, sudouser, sudouser_passwd)  # 创建saved_caches
    for data in data_directory:
        fabfile.mkdir(data, env.user, sudouser, sudouser_passwd)  # 创建commitlog_directory
    # 开始配置
    with cd(software_home + '/conf'):
        # 修改cassandra.yaml文件
        run('sed -i  \'s/Test Cluster/Cassandra Cluster/\' cassandra.yaml')  # 修改集群名称
        run('echo "data_file_directories:" >> cassandra.yaml')  # 配置数据文件路径
        for folder in data_directory:  # 考虑多路径的情况
            run('echo "     - %s" >> cassandra.yaml' % folder)
        run('echo "commitlog_directory: %s" >> cassandra.yaml' % commitlog_directory)  # Commitlog日志路径
        run('echo "saved_caches_directory: %s" >> cassandra.yaml' % saved_caches)  # saved_caches缓存路径
        run('echo "hints_directory: %s" >> cassandra.yaml' % hints_directory)  # hints_directory缓存路径
        run('sed -i \'s/commitlog_segment_size_in_mb: 32/commitlog_segment_size_in_mb: 256/\' cassandra.yaml')  # commitlog_segment_size大小
        # run("sed -i 's/" + 'seeds: "127.0.0.1"/seeds: "' + ','.join(env.hosts) + '"' + "/' cassandra.yaml")  # 配置seeds，即把全部主机添加进来，使用<','.join(env.hosts)>将list转为str
        run('sed -i \'s/seeds: "127.0.0.1"/seeds: \"%s\"/\' cassandra.yaml' % ','.join(env.hosts))  # 配置seeds，即把全部主机添加进来，使用<','.join(env.hosts)>将list转为str

        if listening_Method == "listen_address":
            run('sed -i \'s/listen_address: localhost/listen_address: %s/\' cassandra.yaml' % env.host)  # 指定当前IP为listen_address
        elif listening_Method == "listen_interface":
            if listening_interface_name == "":
                print ("listening_interface_name can't empty")
                exit()
            run('sed -i ' + "'s/listen_address: localhost/#listen_address: localhost/' cassandra.yaml")  # 屏蔽掉listen_address
            run('sed -i ' + "'s/# listen_interface: eth0/listen_interface: %s/' cassandra.yaml" % listening_interface_name)  # 指定网卡名称为listen_interface，同上面的listen_address冲突
        else:
            print ('Must specify listening_Method is "listen_address" or "listen_interface"')
            exit()

        run('sed -i \'s/start_rpc: false/start_rpc: true/\' cassandra.yaml')  # 开启rpc
        if rpc_Method == "rpc_address":
            run('sed -i \'s/rpc_address: localhost/rpc_address: 0.0.0.0/\' cassandra.yaml')  # 指定0.0.0.0为rpc_address
            run('sed -i \'s/# broadcast_rpc_address: 1.2.3.4/broadcast_rpc_address: %s/\' cassandra.yaml' % env.host)
        elif rpc_Method == "rpc_interface":
            if rpc_interface_name == "":
                print ("listening_interface_name can't empty")
                exit()
            run('sed -i \'s/rpc_address: localhost/# rpc_address: localhost/\' cassandra.yaml')  # 屏蔽掉rpc_address
            run('sed -i \'s/# rpc_interface: eth1/rpc_interface: %s/\' cassandra.yaml' % rpc_interface_name)  # 指定rpc_interface的网卡名称,同上面rpc_address冲突
        else:
            print ('Must specify rpc_Method is "rpc_address" or "rpc_interface"')
            exit()

        run('sed -i \'s/#memtable_flush_writers: 2/memtable_flush_writers: 4/\' cassandra.yaml')
        run('sed -i \'s/thrift_framed_transport_size_in_mb: 15/thrift_framed_transport_size_in_mb: 200/\' cassandra.yaml')
        run('sed -i \'s/read_request_timeout_in_ms: 5000/read_request_timeout_in_ms: 20000/\' cassandra.yaml')
        run('sed -i \'s/range_request_timeout_in_ms: 10000/range_request_timeout_in_ms: 120000/\' cassandra.yaml')
        run('sed -i \'s/write_request_timeout_in_ms: 2000/write_request_timeout_in_ms: 300000/\' cassandra.yaml')

        # 修改logback.xml文件
        run('sed -i \'s/20MB/50MB/\' cassandra.yaml')  # 修改system和debug日志文件大小
        # run("sed -i '" + 's:<appender-ref ref="' + 'ASYNCDEBUGLOG"' + ' /> <!--:<!--appender-ref ref="' + 'ASYNCDEBUGLOG' + '"' + ' --> <!--:' + "' logback.xml")  # 屏蔽ASYNC DEBUG LOG日志
        run('sed -i \'s:<appender-ref ref="ASYNCDEBUGLOG" /> <!--:<!--appender-ref ref="ASYNCDEBUGLOG" --> <!--:\' logback.xml')
        # run("sed -i '" + '$i\  <logger name="' + 'org.apache.cassandra.utils.StatusLogger"' + ' level="' + 'OFF"/>' + "' logback.xml")  # 增加到倒数第二行
        run('sed -i \'$i\  <logger name="org.apache.cassandra.utils.StatusLogger" level="OFF"/>\' logback.xml')
        # run("sed -i '" + "$i\  <!--Status log very very more and more-->'" + " logback.xml")
        run('sed -i \'$i\  <!--Status log very very more and more-->\' logback.xml')

        # 修改cassandra-env.sh文件
        run('sed -i \'s/#MAX_HEAP_SIZE="4G"/MAX_HEAP_SIZE="4G"/\' cassandra-env.sh')
        run('sed -i \'s/#HEAP_NEWSIZE="800M"/HEAP_NEWSIZE="800M"/\' cassandra-env.sh')
        run('sed -i \'s/JVM_OPTS="$JVM_OPTS -Xss256k"/JVM_OPTS="$JVM_OPTS -Xss228k"/\' cassandra-env.sh')


# 全部开始
def start():
    with cd(software_home + '/bin'):
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
