# coding=UTF-8
import fabfile
from fabric.api import *

section = 'flink'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)  # 取得主机列表、用户&密码、sudo用户&密码
software_home = fabfile.get_software_home(section)  # 通过section或者软件home
# config.ini指定的软件配置
master_ip = cf.get('flink', 'master_ip')
slaves_ip = cf.get('flink', 'slaves_ip').split(',')
java_home = cf.get('flink', 'java_home')


# 安装
def install():
    fabfile.check_user(env.user)  # 检查是否是root用户，是就退出
    upload_file = fabfile.upload(section)  # 上传
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压,无返回值
    # 正式开始安装
    with cd(software_home + '/conf'):
        run('cat /dev/null > masters')
        run('cat /dev/null > slaves')
        run('sed -i "s/jobmanager.rpc.address: localhost/' + 'jobmanager.rpc.address: %s/g" flink-conf.yaml' % master_ip)  # flink-conf.yaml
        for slave in slaves_ip:
            run('echo %s>> slaves' % slave)
        run('echo "%s:8081" > masters' % master_ip)
        run('echo "env.java.home: %s" >> flink-conf.yaml' % java_home)


# start
def start():
    if env.host == master_ip:
        with cd(software_home):
            with settings(prompts={
                'Are you sure you want to continue connecting (yes/no)? ': 'yes'
            }):
                run('sbin/start-cluster.sh')


# stop
def stop():
    if env.host == master_ip:
        with cd(software_home):
            run('sbin/stop-cluster.sh')
