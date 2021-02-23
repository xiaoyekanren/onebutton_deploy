# coding=UTF-8
# fabfirc==1.14.1
import os
from time import strftime
import sys

import configparser
from fabric.api import *

# 读取配置文件password.ini
cf = configparser.ConfigParser()
cf.read('config.ini')  # sys.path[0]→主程序路径,os.path.abspath→变成绝对路径(有问题，暂时不用)


# 读取password.ini的全部section内容
# print cf.sections()
# 读取password.ini里面的"server"的内容
# print cf.options("hadoop")

# 定义一些常量：
# upload_folder = 上传的文件夹，一般在/tmp/date_zzm下
# upload_file = upload_folder + file_name
# local_file = local_folder + file_name 就是本地安装包的路径+名称
# software_folder = 该软件解压之后的文件名
# install_path = 安装路径
# software_home = install_path + software_folder


def get_common_var(section):
    """
    :param section:
    :return:env.hosts, env.user, env.password, sudouser, sudouser_passwd
    """
    try:
        print os.path.join(os.path.abspath(sys.path[0]), 'config.ini')
        env.user = cf.get(section, 'localuser')
    except:
        print 'you must specify localuser at config.ini'
        exit()

    try:
        env.password = cf.get(section, 'localuser_passwd')
    except:
        print 'you must specify localuser_passwd at config.ini'
        exit()

    try:
        env.hosts = cf.get(section, 'hosts').split(',')
    except:
        print 'you must specify hosts in config.ini'
        exit()

    try:
        sudouser = cf.get(section, 'sudouser')
    except:
        sudouser = ''

    try:
        sudouser_passwd = cf.get(section, 'sudouser_passwd')
    except:
        sudouser_passwd = ''
    return env.hosts, env.user, env.password, sudouser, sudouser_passwd


def check_user(user):
    if user == 'root':
        print ("can't install by root")
        exit()


def check_file_extension(file_path):
    file_name = os.path.basename(file_path)
    file_extension = os.path.splitext(file_path)[-1]
    return file_name, file_extension


def upload(section):  # 上传，返回上传文件的path
    """
    :param section:
    :return:upload_file
    """
    local_file = cf.get(section, 'local_file')
    file_name, file_extension = check_file_extension(local_file)
    upload_folder = os.path.join('/tmp', 'zzm_' + strftime("%Y%m%d")).replace('\\', '/')  # 定义上传文件夹
    run('mkdir -p %s' % upload_folder)  # 创建上传文件夹
    upload_file = os.path.join(upload_folder, file_name).replace('\\', '/')  # 定义上传文件，file_path+file_name
    put(local_file, upload_file)  # 上传
    return upload_file  # 返回上传file_path+file_name


def get_software_home(section):  # 获得软件的安装路径
    """
    :param section:
    :return:software_home
    """
    install_path = cf.get(section, 'install_path')  # 获取安装路径
    software_folder = cf.get(section, 'software_folder')  # 获取压缩包解压后的名称
    software_home = os.path.join(install_path, software_folder).replace('\\', '/')  # 拼出软件的路径
    return software_home


def decompress(section, upload_file, software_home, user, sudouser, sudouser_passwd):  # 只是用于tar.gz或者tgz的压缩包，其他格式的压缩包不能用，需要后面增加判断
    file_name, file_extension = check_file_extension(upload_file)
    print file_extension
    install_path = cf.get(section, 'install_path')  # 获取安装路径
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户
        sudo('mkdir -p %s' % install_path)  # 避免没有该路径，先mkdir一下
        if file_extension == '.gz':
            sudo('tar -zxf %s -C%s' % (upload_file, install_path))  # 为防止没有权限，使用sudo解压
        elif file_extension == '.zip':
            sudo('unzip %s -d %s' % (upload_file, install_path))  # 为防止没有权限，使用sudo解压
        else:
            print 'can not check file extension,please mush special zip or gz'
            exit()
        sudo('chown -R %s:%s %s' % (user, user, software_home))  # 将文件夹权限还给env.user


def mkdir(path_, user, sudouser, sudouser_passwd):
    with settings(user=sudouser, passwd=sudouser_passwd):
        sudo('mkdir -p %s' % path_)
        sudo('chown -R %s:%s %s' % (user, user, path_))
