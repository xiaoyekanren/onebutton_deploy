# coding=UTF-8
import sys
sys.path.append("..")
import fabfile
from fabric.api import *
import json

section = 'deploy_cloudwise'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)  # 取得主机列表、用户&密码、sudo用户&密码
software_home = fabfile.get_software_home(section)  # 通过section或者软件home
# config.ini指定的软件配置
licensekey = cf.get(section, 'licensekey')
received_hosts = cf.get(section, 'received_hosts')


# 安装
def install():
    """
    json.loads()：将json数据转化成dict数据
    json.load()：读取json文件，转成dict数据
    json.dumps()：将dict数据转化成json数据
    json.dump()：将dict数据转化成json数据后写入json文件
    """
    upload_file = fabfile.upload(section)  # 上传
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压,无返回值
    # 正式开始安装
    # 开始配置
    with cd(software_home + '/conf'):
        g = json.loads(run('cat app.conf'))
        g['LicenseKey'] = licensekey
        g['ConfigDomain'] = received_hosts
        g['SendDomain'] = received_hosts
        g = json.dumps(g)
        run('echo \'%s\' > app.conf' % g)


# 全部开始
def start():
    with cd(software_home):
        run('sh OSAgent.sh start')
