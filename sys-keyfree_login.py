# coding=UTF-8
from configparser import ConfigParser
from fabric.api import env, run, settings
import fabfile
from os import system


# 读取配置文件
cf = fabfile.cf
# 定义env
env.user = cf.get('keyfree_login', 'localuser')
env.password = cf.get('keyfree_login', 'localuser_passwd')
env.hosts = cf.get('keyfree_login', 'hosts').split(",")
# 需要拼接的字符串
hostsum = len(env.hosts)
# 定义字典
dict = {}


# 卸载
def uninstall():
    run('rm -rf ~/.ssh/*;')  # 删除已有的公钥私钥


# 安装
def install():
    uninstall()  # 清空现有所有密钥

    run('ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""')  # 生成公钥新的公钥私钥

    dict[env.host] = run('cat ~/.ssh/id_rsa.pub')  # 主机名:公钥  放入字典

    if env.host == env.hosts[-1]:  # 即在最后一个主机运行的时候，此时全部主机已经生成了id_rsa，然后执行install2
        install2()


def install2():
    for x in env.hosts:  # 遍历env.hosts
        with settings(host_string=x):  # 根据env.hosts在执行一遍，即强行改host_string为第一个env.host，从头执行
            for y in dict.keys():  # 将字典写入authorized_keys
                run('echo "' + dict[y] + '" >> .ssh/authorized_keys')
            run('chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh')  # 给文件夹权限


# # 老版本
# 安装
# def install():
#     run('rm -rf ~/.ssh/id_rsa*')  # 删除已有的公钥私钥
#     run('ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""')  # 生成公钥新的公钥私钥
#
#     current_path = "".join(os.path.dirname(os.path.abspath('sys-keyfree_login.py')))  # 获取当前的路径
#     current_file_path = os.path.join(current_path, "".join(env.host)).replace('\\', '/')  # 写一个路径+文件名，为下一步骤get提供本地路径+文件名
#     get('.ssh/id_rsa.pub', current_file_path)  # 将公钥拿到本地
#
#     if env.host == env.hosts[-1]:  # 即在最后一个主机运行的时候，此时全部主机已经生成了id_rsa，然后执行install2
#         os.system('fab -f sys-keyfree_login.py install2')
#
#
# def install2():
#     run('echo "' + addrsa() + '" > .ssh/authorized_keys')
#     if env.host == env.hosts[-1]:
#         os.system('fab -f sys-keyfree_login.py rmlocalfile')
#     run('chmod 600 ~/.ssh/authorized_keys')
#     run('chmod 700 ~/.ssh')
#
#
# def addrsa():
#     rsa_global = ''
#     i = 0
#     while i < hostsum:
#         rsa = open(env.hosts[i]).read()
#         rsa_global = rsa_global + rsa
#         i += 1
#     return rsa_global
#
#
# def rmlocalfile():
#     os.remove(env.host)
