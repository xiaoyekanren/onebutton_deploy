# coding=utf-8
from fabric.api import *


def addlist_hosts(first_host, step):
    """
    取first_host传进来的ip地址的第四段，按照step的数量递增1，返回一个包含step个ip地址的list
    :param first_host:预先定义的IP地址，起始的IP地址
    :param step:即有多少台主机(例：step=20,则会生成20个每次递增1的IP地址)
    :return:返回一个包含step个ip地址的list
    """
    aaa = list()
    aaa.append(first_host)
    # head是ip地址的前三段
    head = ".".join(first_host.split('.')[:-1])
    # tail是ip地址的第四段
    tail = first_host.split('.')[-1]
    i = 1
    while i < step:
        the_next_host = head + '.' + bytes(int(tail)+i)
        aaa.append(the_next_host)
        i += 1
    return aaa


# 定义
env.user = 'ubuntu'
env.password = 'Dwf12345'
sudouser = 'ubuntu'
sudouser_passwd = 'Dwf12345'
# # 主机名
# env.hosts = ['192.168.3.91']
the_first_host = {'first_host': '192.168.3.1', 'step': 10}
env.hosts = addlist_hosts(first_host=the_first_host['first_host'], step=the_first_host['step'])
# 定义参数
tomcat_document = 'apache-tomcat-9.0.37'


def modify():
    # 修改/etc/rc.local
    sudo("sed -i 's:sh /home/ubuntu/startup.sh:su - ubuntu -c /home/ubuntu/startup.sh:g' /etc/rc.local")
    # 修改/opt的所有权为ubuntu
    sudo("chown -R ubuntu:ubuntu /opt")
    # 修改/home/ubuntu/startup.sh脚本，去掉sudo启动tomcat
    run("sed -i 's:sudo nohup ./startup.sh \\&:nohup ./startup.sh \\&:g' /home/ubuntu/startup.sh")
    # 修改/home/ubuntu/startup.sh脚本，修改Tomcat_INSTALL_DIR
    run("sed -i '/^Tomcat_INSTALL_DIR/cTomcat_INSTALL_DIR=\"/opt/apache-tomcat-*\"' /home/ubuntu/startup.sh")
    # 上传tomcat新版本到根目录
    put('Tools\\apache-tomcat-9.0.37.tar.gz', 'tomcat.tar.gz')
    # 解压
    run('tar -zxvf tomcat.tar.gz')
    # 删除新tomcat的webapps
    run('rm -rf /home/ubuntu/apache-tomcat-9.0.37/webapps/')
    # 删除压缩文件
    run('rm -rf tomcat.tar.gz')
    with cd('/opt'):
        # 备份DWF
        run('tar -zcvf dwf_bak_apache-tomcat-8.5.34.tar.gz apache-tomcat-8.5.34')
        # 移动新版tomcat到/opt
        run('mv /home/ubuntu/' + tomcat_document + ' /opt/')
        # 移动旧版tomcat的webapps到新dwf
        run('mv /opt/apache-tomcat-8.5.34/webapps /opt/apache-tomcat-9.0.37/')
        # 删除老tomcat文件夹
        run('rm -rf /opt/apache-tomcat-8.5.34')
    # sudo('reboot')

# 执行方式
# 修改fab -f dwf_switch_tomcat.py modify
# 当前作废