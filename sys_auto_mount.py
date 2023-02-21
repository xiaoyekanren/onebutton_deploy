# coding=UTF-8
import os.path
import time
import fabfile
from fabric.api import *

section = 'auto_mount'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts = cf.get(section, 'hosts').split(',')
env.user = cf.get(section, 'user')
env.password = cf.get(section, 'user_passwd')
#
mount_dev = cf.get(section, 'mount_dev').split(',')
mount_to_path = cf.get(section, 'mount_to_path').split(',')


# 安装
def install():
    # mkdir
    for i in mount_to_path:
        sudo('mkdir -p %s' % i)
    # parted && format
    for i in mount_dev:
        with settings(prompts={
            "Warning: The existing disk label on /dev/vdb will be destroyed and all data on this disk will be lost. Do you want to continue? \nYes/No? ": 'Yes',
            "Yes/No?": 'Yes'
        }):
            sudo('parted %s mklabel gpt' % i)
        sudo('parted %s mkpart primary 2048s 100%%' % i)
    # get dev partition
    mount_dev_partition = []
    for i in mount_dev:
        dev_partition = i + sudo('parted %s print | grep "Number  Start" -A1 | tail -n 1 | awk {\'print $1\'}' % i)
        mount_dev_partition.append(dev_partition)
    # format
    for i in mount_dev_partition:
        sudo('mkfs.ext4 %s' % i)
    # write to fstab
    for i in mount_dev_partition:
        blkid = sudo('blkid %s | awk \'{print $2}\' | awk -F = \'{print $2}\' |sed \'s:"::g\'' % i)
        sudo('echo UUID=%s %s ext4 defaults 0 0 >> /etc/fstab' % (str(blkid), str(mount_to_path[mount_dev_partition.index(i)])))
    # mount
    for i in mount_dev_partition:
        sudo('mount %s %s' % (i, str(mount_to_path[mount_dev_partition.index(i)])))
