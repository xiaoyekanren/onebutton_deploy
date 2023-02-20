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
# config
package_url = cf.get(section,'package_url')
zabbix_server = cf.get(section, 'zabbix_server')
zabbix_package = package_url.split('/')[-1]
zabbix_service = '-'.join(zabbix_package.split('-')[0:2])


def install():
    with settings(warn_only=False):
        run('yum remove zabbix-agent zabbix-agent2')
        run('wget %s' % package_url)
        run('rpm -ivh %s' % zabbix_package)
        run('sed -i "s/^Server=.*/Server=%s/g" /etc/zabbix/zabbix_agent2.conf' % zabbix_server)
        run('sed -i "s/^ServerActive=.*/ServerActive=%s/g" /etc/zabbix/zabbix_agent2.conf' % zabbix_server)
        run('sed -i "s/^Hostname=.*/Hostname=%s/g" /etc/zabbix/zabbix_agent2.conf' % env.host)
        run('systemctl enable %s' % zabbix_service)
        run('systemctl restart %s' % zabbix_service)
        run('systemctl stop firewalld; systemctl disable firewalld')
