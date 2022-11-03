# coding=UTF-8
import fabfile
from fabric.api import *

section = 'mount_disk'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts = cf.get(section, 'hosts').split(',')
env.user = cf.get(section, 'sudouser')
env.password = cf.get(section, 'sudouser_passwd')
sudouser = cf.get(section, 'sudouser')
sudouser_passwd = cf.get(section, 'sudouser_passwd')


# 安装
def install():
    sudo('parted /dev/vdc mklabel gpt')
    sudo('parted /dev/vdc mkpart primary 2048s 100%')
    sudo('mkfs.ext4 /dev/vdc1')
    sudo('mkdir /data')
    sudo('mount /dev/vdc1 /data')
    sudo('chown -R cluster:cluster /data')
    uuid = str(sudo('blkid /dev/vdc1 | awk \'{print $2}\'')).split('"')[1]
    sudo('echo "%s" >> /etc/fstab' % str("UUID=" + uuid + "\t/data\text4\tdefaults\t1\t1"))  # UUID=abc / ext4 defaults 1 1



