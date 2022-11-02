# coding=UTF-8
import fabfile
from fabric.api import *

section = 'adduser'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts = cf.get(section, 'hosts').split(',')
env.user = cf.get(section, 'sudouser')
env.password = cf.get(section, 'sudouser_passwd')
new_user = cf.get(section, 'new_user')
new_user_passwd = cf.get(section, 'new_user_passwd')


# 安装
def install():
    sudo('adduser %s' % new_user)
    with settings(prompts={
        'New password: ': new_user_passwd,
        'Retype new password: ': new_user_passwd},
    ):
        run('passwd %s' % new_user)


# if __name__ == '__main__':
#     c = []
#     a = '172.16.2.'
#     b = 2
#     while b < 34:
#         c.append(a+str(b))
#         print a+str(b)
#         b += 1
#     print ','.join(c)
