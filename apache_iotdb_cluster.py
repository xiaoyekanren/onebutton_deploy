# coding=UTF-8
import os.path
import time
import fabfile
from fabric.api import *

section = 'iotdb-cluster'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)
software_home = fabfile.get_software_home(section)
# config.ini指定的软件配置
first_confignode = cf.get(section, 'first_confignode')
config_node = cf.get(section, 'config_node')
data_node = cf.get(section, 'data_node')
# iotdb-common.properties
section_config = 'iotdb-cluster-config'


# 安装
def install():
    # 检查是否是root用户，是就退出
    fabfile.check_user(env.user)
    # 上传
    if env.host == env.hosts[0]:
        upload_file = fabfile.upload(section)
    else:
        local_file, file_name, upload_folder, upload_file = fabfile.get_upload_path(section)
        run('mkdir -p %s' % upload_folder)  # 创建上传文件夹
        with settings(prompts={
            "%s@%s's password: " % (env.user, env.hosts[0]): env.password
        }):
            run('scp %s@%s:%s %s' % (env.user, env.hosts[0], upload_file, upload_file))
    # 解压
    sudo('rm -rf %s' % software_home)
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压到install_path(在函数decompress里面定义),无返回值
    # 正式开始安装
    # 创建目录
    sudo('mkdir -p %s' % software_home)
    # 配置文件
    with cd(os.path.join(software_home, 'conf')):
        cn_internal_port = run('cat iotdb-confignode.properties | grep -e "^cn_internal_port" | awk -F= {\'print $2\'}')
        # iotdb-confignode.properties
        run('sed -i -e "s:^cn_internal_address=.*:cn_internal_address=%s:" iotdb-confignode.properties' % env.host)  # cn_internal_address
        run('sed -i -e "s/^cn_target_config_node_list=.*/cn_target_config_node_list=%s:%s/" iotdb-confignode.properties' % (first_confignode, cn_internal_port))  # cn_target_config_node_list
        # iotdb-datanode.properties
        run('sed -i -e "s:^dn_rpc_address=.*:dn_rpc_address=%s:" iotdb-datanode.properties' % env.host)  # dn_rpc_address
        run('sed -i -e "s:^dn_internal_address=.*:dn_internal_address=%s:" iotdb-datanode.properties' % env.host)  # dn_internal_address
        run('sed -i -e "s/^dn_target_config_node_list=.*/dn_target_config_node_list=%s:%s/" iotdb-datanode.properties' % (first_confignode, cn_internal_port))  # dn_target_config_node_list
        # iotdb-common.properties
        config_list = cf.items(section_config)
        for i in config_list:
            print('replace %s=.* to %s=%s' % (str(i[0]), str(i[0]), str(i[1])))
            run('sed -i -e "s:^# %s=.*:%s=%s:" iotdb-common.properties' % (str(i[0]), str(i[0]), str(i[1])))


def start():
    with cd(os.path.join(software_home, 'sbin')):
        put('dependences/iotdb-start.sh', os.path.join(software_home, 'sbin'))
        if env.host == first_confignode:
            run('bash iotdb-start.sh confignode && sleep 5')
        if env.host != first_confignode and env.host in config_node:
            run('bash iotdb-start.sh confignode && sleep 1')
        if env.host in data_node:
            run('bash iotdb-start.sh datanode && sleep 1')


def stop():
    with cd(os.path.join(software_home, 'sbin')):
        if env.host in config_node:
            run('./stop-confignode.sh')
        if env.host in data_node:
            run('./stop-datanode.sh')
