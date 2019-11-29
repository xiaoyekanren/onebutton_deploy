# coding=UTF-8
import fabfile
import os
import time
import fileinput
from fabric.api import *

# 读取fabfile文件的cf参数,读取passwd.ini文件
cf = fabfile.cf
# 定义env
env.user = cf.get('storm', 'localuser')
env.password = cf.get('storm', 'localuser_passwd')
env.hosts = cf.get('storm', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('storm', 'sudouser')
sudouser_passwd = cf.get('storm', 'sudouser_passwd')
# 定义软件参数
storm_local_file = cf.get('storm', 'storm_local_file')
storm_folder = cf.get('storm', 'storm_folder')  # 即解压之后的文件夹名称
# 需要拼接的字符串
storm_upload_file_path = os.path.join('/home', env.user, 'storm.tar.gz').replace('\\', '/')
storm_home = os.path.join('/home', env.user, storm_folder).replace('\\', '/')
storm_config_folder = os.path.join(storm_home, 'conf').replace('\\', '/')
# 依赖
nimbus_host = cf.get('storm', 'nimbus_host')
zookeeper_hosts = cf.get('storm', 'zookeeper_hosts').split(',')
nimbus_seeds = cf.get('storm', 'nimbus_seeds').split(',')
storm_data = cf.get('storm', 'storm_data')
slots_ports_num = cf.get('storm', 'supervisor_slots_ports_num')
slots_ports_1st = 6700


# 安装
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(storm_local_file, storm_upload_file_path)
    print('A file called "storm.tar.gz" will be created for storm')
    # 解压&删除
    run('tar -zxvf storm.tar.gz && rm -f storm.tar.gz')
    #
    with cd(storm_config_folder):
        # ----
        run('echo "storm.zookeeper.servers: " >>storm.yaml')
        for zookeeper in zookeeper_hosts:
            # run('echo ' + '"    - ' + zookeeper + '" >> storm.yaml')
            run('echo ' + "'    '" + '''-' "''' + zookeeper + '''"' ''' + '>> storm.yaml')
        run('echo "" >>storm.yaml')
        # ----
        b = 'nimbus.seeds: ['
        for a in range(len(nimbus_seeds)):
            b = b + "'" + '"' + nimbus_seeds[a] + '"' + "'" + ','
        b = b[:-1] + ']'
        run('echo ' + b + '>> storm.yaml')
        run('echo "" >>storm.yaml')
        # ----
        run('echo "supervisor.slots.ports: " >>storm.yaml')
        num = 1
        while num <= int(slots_ports_num):
            run('echo ' + '"    - "' + bytes(slots_ports_1st + num) + '>> storm.yaml')
            num += 1
        run('echo "" >>storm.yaml')
        # ----
        # run('echo " ui.port: 8080" >>storm.yaml')
        # run('echo "" >>storm.yaml')
        # ----
        run("echo storm.local.dir: '" + '"' + storm_data + '"' + "' >>storm.yaml")
        run('echo "" >>storm.yaml')

    with settings(user=sudouser, password=sudouser_passwd):
        sudo('mkdir -p ' + storm_data)
        sudo('chown -R ' + env.user + ':' + env.user + ' ' + storm_data)


# 启动
def start():
    with cd(storm_home + '/bin'):
        run('rm -rf ./start.sh')
        run('touch start.sh')
        run('chmod +x ./start.sh')
        run('echo "#/bin/bash" >>./start.sh')
        if env.host == nimbus_host:
            run('echo "nohup ./storm nimbus >./nimbus.output 2>&1 &" >>start.sh')
            run('echo "nohup ./storm ui >./ui.output 2>&1 &" >>start.sh')
        run('echo "nohup ./storm supervisor >./supervisor.output 2>&1 &" >>start.sh')
        run('echo "nohup ./storm logviewer >./logviewer.output 2>&1 &" >>start.sh')
        run('sh start.sh && sleep 2')


# 停止
def stop():
    run("jps -l|grep 'org.apache.storm.daemon.supervisor.Supervisor'|awk '{print $1}'|xargs kill -9")
    run("jps -l|grep 'org.apache.storm.daemon.nimbus'|awk '{print $1}'|xargs kill -9")
    run("jps -l|grep 'org.apache.storm.ui.core'|awk '{print $1}'|xargs kill -9")
    run("jps -l|grep 'org.apache.storm.daemon.logviewer'|awk '{print $1}'|xargs kill -9")

