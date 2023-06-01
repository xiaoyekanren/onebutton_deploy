# coding=UTF-8
import os.path
import fabfile
from fabric.api import *

section = 'iotdb-cluster'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudo_password = fabfile.get_common_var(section)
software_home = fabfile.get_software_home(section)
# config.ini指定的软件配置
first_confignode = cf.get(section, 'first_confignode')
config_node = cf.get(section, 'config_node')
data_node = cf.get(section, 'data_node')
# 修改配置参数
section_common_config = 'iotdb-common-config'  # iotdb-common.properties
section_confignode_config = 'iotdb-confignode-config'  # iotdb-confignode.properties
section_datanode_config = 'iotdb-datanode-config'  # iotdb-datanode.properties


# 安装
def install():
    local_file, file_name, upload_folder, upload_file = fabfile.get_upload_path(section)  # get file info
    fabfile.put_file(section, env.host, env.hosts, env.user, env.password, upload_folder, upload_file)  # upload
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudo_password)  # 解压到install_path(在函数decompress里面定义),无返回值

    # 配置文件
    with cd(os.path.join(software_home, 'conf').replace('\\', '/')):

        # 可选参数
        # iotdb-common.properties
        common_config_list = cf.items(section_common_config)
        if common_config_list:
            for i in common_config_list:
                print('replace %s=.* to %s=%s' % (str(i[0]), str(i[0]), str(i[1])))
                run('sed -i -e "s:^# %s=.*:%s=%s:" iotdb-common.properties' % (str(i[0]), str(i[0]), str(i[1])))
        # iotdb-confignode.properties
        confignode_config_list = cf.items(section_confignode_config)
        if confignode_config_list:
            for i in confignode_config_list:
                print('replace %s=.* to %s=%s' % (str(i[0]), str(i[0]), str(i[1])))
                run('sed -i -e "s:^# %s=.*:%s=%s:" iotdb-confignode.properties' % (str(i[0]), str(i[0]), str(i[1])))
        # iotdb-datanode.properties
        datanode_config_list = cf.items(section_datanode_config)
        if datanode_config_list:
            for i in datanode_config_list:
                print('replace %s=.* to %s=%s' % (str(i[0]), str(i[0]), str(i[1])))
                run('sed -i -e "s:^# %s=.*:%s=%s:" iotdb-datanode.properties' % (str(i[0]), str(i[0]), str(i[1])))

        # 必填项：
        cn_internal_port = run('cat iotdb-confignode.properties | grep -e "^cn_internal_port" | awk -F= {\'print $2\'}')
        # iotdb-confignode.properties
        run('sed -i -e "s:^cn_internal_address=.*:cn_internal_address=%s:" iotdb-confignode.properties' % env.host)  # cn_internal_address
        run('sed -i -e "s/^cn_target_config_node_list=.*/cn_target_config_node_list=%s:%s/" iotdb-confignode.properties' % (first_confignode, cn_internal_port))  # cn_target_config_node_list
        # iotdb-datanode.properties
        run('sed -i -e "s:^dn_rpc_address=.*:dn_rpc_address=%s:" iotdb-datanode.properties' % env.host)  # dn_rpc_address
        run('sed -i -e "s:^dn_internal_address=.*:dn_internal_address=%s:" iotdb-datanode.properties' % env.host)  # dn_internal_address
        run('sed -i -e "s/^dn_target_config_node_list=.*/dn_target_config_node_list=%s:%s/" iotdb-datanode.properties' % (first_confignode, cn_internal_port))  # dn_target_config_node_list


def start():
    put('dependences/iotdb-start.sh', os.path.join(software_home, 'sbin').replace('\\', '/'))
    with cd(os.path.join(software_home, 'sbin').replace('\\', '/')):
        if env.host == first_confignode:
            run('bash iotdb-start.sh confignode && sleep 5')
        if env.host != first_confignode and env.host in config_node:
            run('bash iotdb-start.sh confignode && sleep 1')
        if env.host in data_node:
            run('bash iotdb-start.sh datanode && sleep 1')


def stop():
    with cd(os.path.join(software_home, 'sbin').replace('\\', '/')):
        if env.host in config_node:
            run('./stop-confignode.sh')
        if env.host in data_node:
            run('./stop-datanode.sh')


def clear():
    with cd(software_home):
        run('rm -rf data logs')
