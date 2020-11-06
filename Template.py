# coding=UTF-8
import fabfile
from fabric.api import *

section = ''  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd, local_file, software_folder, install_path = fabfile.get_common_var(section)
# config.ini指定的软件配置
# a =
# b =
# c =
# 需定义的参数
# d =
# e =


# 安装
def install():
    # 检查是否是root用户，是就退出
    fabfile.check_user(env.user)
    # 上传
    upload_file = fabfile.upload(section)
    # 解压
    fabfile.decompress(section, upload_file)
    # 正式开始安装
    # 1
    # 2
    # 3


# 启动
def start():
    pass


# 停止
def stop():
    pass
