# coding=UTF-8
import fabfile
from fabric.api import *

section = ''  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)  # 取得主机列表、用户&密码、sudo用户&密码
software_home = fabfile.get_software_home(section)  # 通过section或者软件home
# config.ini指定的软件配置
# a =
# b =
# c =
# 需定义的参数
# d =
# e =


# 安装
def install():
    fabfile.check_user(env.user)  # 检查是否是root用户，是就退出
    upload_file = fabfile.upload(section)  # 上传
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压,无返回值
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
