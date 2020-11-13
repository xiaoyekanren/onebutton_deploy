# coding=UTF-8
import fabfile
from fabric.api import *
from os import path
from time import strftime

section = 'pg'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)  # 取得主机列表、用户&密码、sudo用户&密码
software_home = fabfile.get_software_home(section)  # 通过section或者软件home
# ==============
data_path = cf.get('pg', 'data_path')
max_connections = cf.get('pg', 'max_connections')
superuser = cf.get('pg', 'superuser')
superuser_passwd = cf.get('pg', 'superuser_passwd')


# 安装
def install():
    fabfile.check_user(env.user)  # 检查是否是root用户，是就退出
    upload_file = fabfile.upload(section)  # 上传,返回path+filename
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压,无返回值

    # 开始配置pg
    fabfile.mkdir(data_path, env.user, sudouser, sudouser_passwd)  # 创建文件夹
    with cd(software_home + '/bin'):  # 进入pg目录
        run('./initdb -D  %s' % data_path)  # 初始化
    # 修改默认参数
    with cd(data_path):
        run('sed -i "s:max_connections = 100:max_connections = %s:g" postgresql.conf' % max_connections)
        run('sed -i "s/#listen_addresses =.*/listen_addresses =\'*\'/g" postgresql.conf')
        run('sed -i "s:#port = 5432:port = 5432:g" postgresql.conf')
        run('echo "host    all             all             0.0.0.0/0               trust" >> pg_hba.conf')
    # 启动pg
    with settings(warn_only=True):
        with cd(software_home):
            run('bin/pg_ctl -D %s start' % data_path)
    # 新建超级用户
    with cd(software_home + '/bin'):
        with settings(prompts={
            'Enter password for new role: ': superuser_passwd,
            'Enter it again: ': superuser_passwd
        }):
            run('./createuser -dlrs ' + superuser + ' -P')
            # -dlrs
            # d="role can create new databases"
            # l="role can login (default)"
            # r="role can create new roles"
            # s="role will be superuser"
    with settings(warn_only=True):
        run("ps -ef|grep 'postgres'|awk '{print $2}'|xargs kill -9;echo 'already killed'")  # 杀了PG
    # 输出结果,输出host类型是list必须带",".join(),否则会显示[u]
    print '--------------------------------------\nfinish install pg\n--------------------------------------'
    print 'host is %s,\npg user is %s,\npassword is %s' % (",".join(env.hosts), superuser, superuser_passwd)
    print '--------------------------------------'
    print 'start way:(must use user ==> %s)\n%s/bin/pg_ctl -D %s start' % (env.user, software_home, data_path)
    print '--------------------------------------'
    print 'start cli:\n%s/bin/psql -U %s -d postgres' % (software_home, superuser)
    print '--------------------------------------'


def start():
    with settings(warn_only=True):
        with cd(software_home):
            run('bin/pg_ctl -D %s start' % data_path)


def stop():
    with settings(warn_only=True):
        run("ps -ef|grep 'postgres'|awk '{print $2}'|xargs kill -9")
