# coding=UTF-8
import fabfile
from fabric.api import *

section = 'kafka'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)  # 取得主机列表、用户&密码、sudo用户&密码
software_home = fabfile.get_software_home(section)  # 通过section或者软件home
# config.ini指定的软件配置
log_dirs = cf.get('kafka', 'log_dirs')
zookeeper_hosts = cf.get('kafka', 'zookeeper_hosts').split(',')
brokerid = 0


# 安装
def install():
    fabfile.check_user(env.user)  # 检查是否是root用户，是就退出
    upload_file = fabfile.upload(section)  # 上传
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压,无返回值
    # 正式开始安装
    # 使用sudo用户，创建目录并授权给kafka所属用户
    with settings(user=sudouser, password=sudouser_passwd):
        for log in log_dirs.split(','):
            sudo('mkdir -p %s' % log)
            sudo('chown -R %s:%s %s' % (env.user, env.user, log))
    # 开始配置kafka
    with cd(software_home + '/config'):
        # server.properties
        global brokerid
        run('sed -i "s:broker.id=0:broker.id=%s:" server.properties' % bytes(brokerid))  # broker.id
        brokerid += 1
        # 开始拼zookeeper的hosts
        i = 0
        g = ''
        while i < len(zookeeper_hosts) - 1:  # zookeeper.connect
            g = g + bytes(zookeeper_hosts[i]) + ':2181' + ','
            i += 1
        g = g + bytes(zookeeper_hosts[i])
        run('sed -i "s/localhost:2181/%s/g" server.properties' % g)
        #
        run('sed -i "s:/tmp/kafka-logs:%s:g" server.properties' % log_dirs)  # log_dirs
        run('echo "" >> server.properties')  # 输出空行
        run('echo "listeners=PLAINTEXT://%s:9092" >> server.properties' % env.host)  # listeners


# 启动
def start():
    with cd(software_home + '/bin'):
        run('rm -f nohup.out')
        run('rm -f start.sh')
        run('touch start.sh')
        run('chmod 755 start.sh')
        run('echo "#/bin/bash" >>start.sh')
        run('echo "nohup ./kafka-server-start.sh ../config/server.properties 1>nohup.out 2>nohup.out &" >>start.sh')
        run('sh start.sh && sleep 0.1')


# 停止
def stop():
    with cd(software_home + '/bin'):
        run('./kafka-server-stop.sh')
    # fab -w可以跳过失败的
