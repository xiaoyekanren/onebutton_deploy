# coding=UTF-8
import fabfile
from fabric.api import *

section = 'keyfree_login'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)  # 取得主机列表、用户&密码、sudo用户&密码
# 需要拼接的字符
dict = {}  # 定义字典


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
# 1、生成id.rsa之后
# 2、get到本地
# 3、在install里面套一个install2，
# 3.1、在install2里面从第一个env.host开始执行
# 3.2、读每个host命名的文件内容，赋值给变量，通过run→echo到authorized_keys
# 4、删除get到的那些文件