# coding=UTF-8
import os.path

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


# test
def test():
    abc = cf.get(section_config)
    print(type(abc.split()))
    print(abc.split())


# 安装
def install():
    # 检查是否是root用户，是就退出
    fabfile.check_user(env.user)
    # 上传
    upload_file = fabfile.upload(section)
    # 解压
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压到install_path(在函数decompress里面定义),无返回值
    # 正式开始安装
    # 创建目录
    sudo('mkdir -p %s' % software_home)
    # 配置文件
    with cd(os.path.join(software_home, 'sbin')):
        # iotdb-confignode.properties
        run('sed -i -e "s:^cn_internal_address=.*:cn_internal_address=%s:" iotdb-confignode.properties' % env.host)  # cn_internal_address
        run('sed -i -e "s:^cn_target_config_node_list=.*:cn_target_config_node_list=%s:" iotdb-confignode.properties' % first_confignode)  # cn_target_config_node_list
        # iotdb-datanode.properties
        run('sed -i -e "s:^dn_rpc_address=.*:dn_rpc_address=%s:" iotdb-datanode.properties' % env.host)  # dn_rpc_address
        run('sed -i -e "s:^dn_internal_address=.*:dn_internal_address=%s:" iotdb-datanode.properties' % env.host)  # dn_internal_address
        run('sed -i -e "s:^dn_target_config_node_list=.*:dn_target_config_node_list=%s:" iotdb-datanode.properties' % first_confignode)  # dn_target_config_node_list
        # iotdb-common.properties


def start():
    if env.host == master_ip:
        with cd(software_home):
            with settings(prompts={
                'Are you sure you want to continue connecting (yes/no)? ': 'yes'
            }):
                run('sbin/start-all.sh')
                # run('sbin/mr-jobhistory-daemon.sh start historyserver')


def stop():
    if env.host == master_ip:
        with cd(software_home):
            run('sbin/stop-all.sh')
            # run('sbin/mr-jobhistory-daemon.sh stop historyserver')


if __name__ == '__main__':
    test()
