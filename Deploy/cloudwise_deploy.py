# coding=UTF-8
import fabfile
from fabric.api import *
import json

section = 'cloudwise_deploy'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)  # 取得主机列表、用户&密码、sudo用户&密码
software_home = fabfile.get_software_home(section)  # 通过section或者软件home
# config.ini指定的软件配置
licensekey = cf.get(section, 'licensekey')
received_hosts = cf.get(section, 'received_hosts')


# 安装
def install():
    fabfile.check_user(env.user)  # 检查是否是root用户，是就退出
    upload_file = fabfile.upload(section)  # 上传
    fabfile.decompress(upload_file)  # 解压,无返回值
    # 正式开始安装
    # 开始配置
    with cd(software_home + '/conf'):
        run('cp app.conf app.conf_bak')  # 备份
        with open('app.conf') as f:
            aaa = json.load(f)
            print aaa
# {
# "frequency":"60",
# "service_name":"OS",
# "LicenseKey":"LicenseKey",
# "ConfigDomain":"http://data.toushibao.com",
# "SendDomain":"http://data.toushibao.com",
# "Qualifier":"",
# "mem":"1",
# "cpuBurden":"1",
# "cpuUsage":"1",
# "proces":"1",
# "netItf":"1",
# "tcp":"1"
# }

# 全部开始
def start():
    with cd(software_home + '/bin'):
        run('rm -f nohup.out')


if __name__ == '__main__':
    install()