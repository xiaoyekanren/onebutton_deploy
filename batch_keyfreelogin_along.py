# coding=UTF-8
from configparser import ConfigParser
from fabric.api import env, run, settings
from os import system

# python==2.7
# fabfirc==1.14.1
# pyinstaller=3.6
# pypiwin32
# pyinstaller -F batch_keyfreelogin_along.py
# -F, –onefile	打包一个单个文件
# 适用于新机器部署，会清理掉其他已存在的密钥
# 完全体命令:python -m fabric -f batch_keyfreelogin_along.py install

# 读取配置文件password.ini
cf = ConfigParser()
cf.read('config.ini')

# 定义env
env.user = cf.get('keyfree_login', 'localuser')
env.password = cf.get('keyfree_login', 'localuser_passwd')
env.hosts = cf.get('keyfree_login', 'hosts').split(",")
# 需要拼接的字符串
hostsum = len(env.hosts)
# 定义字典
dict = {}
alllist = env.hosts


# 卸载
def uninstall():
    run('rm -rf ~/.ssh/*;')  # 删除已有的公钥私钥


# 安装
def install():
    uninstall()
    run('ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""')  # 生成公钥新的公钥私钥

    dict[env.host] = run('cat ~/.ssh/id_rsa.pub')  # 主机名:公钥  放入字典

    if env.host == env.hosts[-1]:  # 即在最后一个主机运行的时候，此时全部主机已经生成了id_rsa，然后执行install2
        # system('fab -f sys-keyfree_login.py install2')
        install2()
    # # ----------输出-----
    # print ('finish')
    # # 用来防止程序自动退出
    # system('pause')


def install2():
    for x in env.hosts:  # 遍历env.hosts
        with settings(host_string=x):  # 根据env.hosts在执行一遍
            for y in dict.keys():  # 将字典写入authorized_keys
                run('echo "' + dict[y] + '" >> .ssh/authorized_keys')
            run('chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh')  # 给文件夹权限


if __name__ == '__main__':
    install()
