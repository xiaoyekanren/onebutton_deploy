# coding=UTF-8
import fabfile
from fabric.api import *

section = 'zabbix_agent'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts = cf.get(section, 'hosts').split(',')
env.user = cf.get(section, 'sudouser')
env.password = cf.get(section, 'sudouser_passwd')
sudouser = cf.get(section, 'sudouser')
sudouser_passwd = cf.get(section, 'sudouser_passwd')


# 安装
def install():
    with settings(warn_only=False):
        run('yum install pcre2 -y')
        run('wget https://mirrors.tuna.tsinghua.edu.cn/zabbix/zabbix/6.2/rhel/7/x86_64/zabbix-agent2-6.2.4-release1.el7.x86_64.rpm --no-check-certificate')
        run('wget https://mirrors.tuna.tsinghua.edu.cn/zabbix/zabbix/6.2/rhel/7/x86_64/zabbix-agent2-6.2.4-release1.el7.x86_64.rpm --no-check-certificate')
        run('rpm -ivh zabbix-agent2-6.2.4-release1.el7.x86_64.rpm')
        run('sed -i "s/Server=127.0.0.1/Server=166.111.130.101/g" /etc/zabbix/zabbix_agent2.conf')
        run('sed -i "s/# ListenPort=10050/ListenPort=10050/g" /etc/zabbix/zabbix_agent2.conf')
        run('sed -i "s/ServerActive=127.0.0.1/ServerActive=166.111.130.101/g" /etc/zabbix/zabbix_agent2.conf')
        run('sed -i "s/Hostname=Zabbix server/Hostname=`ifconfig -a | grep inet | grep -v inet6 | grep -v 127 | awk \'{print $2}\' | tr -d "addr:" | sed -n \'1p\'`/g" /etc/zabbix/zabbix_agent2.conf')
        run('systemctl enable zabbix-agent2')
        run('systemctl restart zabbix-agent2')
    pass



