# coding=utf-8
from fabric.api import *


def addlist_hosts(first_host, step):
    """
    取first_host传进来的ip地址的第四段，按照step的数量递增1，返回一个包含step个ip地址的list
    :param first_host:预先定义的IP地址，起始的IP地址
    :param step:即有多少台主机(例：step=20,则会生成20个每次递增1的IP地址)
    :return:返回一个包含step个ip地址的list
    """
    aaa = []
    head = ".".join(first_host.split('.')[:-1])
    tail = first_host.split('.')[-1]
    aaa.append(first_host)
    i = 1
    while i <= step:
        the_next_host = head + '.' + bytes(int(tail)+i)
        aaa.append(the_next_host)
        i += 1
    return aaa


def addlist_port(first_port, step):
    """
    从first_port这个数开始，将+1的结果存入list，返回一个包含step个端口的list
    :param first_port:一个数字，正确的值应该是1~65535
    :param step:即循环多少次，即要生成多少个递增1的数
    :return:
    """
    bbb = list()  # 指定[]会有警告，但是不影响使用；指定这个就没警告了
    bbb.append(first_port)
    i = 1
    while i <= step:
        bbb.append(first_port+i)
        i += 1
    return bbb


def replace(filename, old_value, new_value):
    """
    将文件filename中的old_value替换为new_value
    :param filename:文件名
    :param old_value:替换之前的值
    :param new_value:替换之后的值
    :return:无返回值，仅仅是执行
    """
    run("sed -i 's:" + bytes(old_value) + ":" + bytes(new_value) + ":g' " + filename)


# # 以下都是需要修改的内容
# # <!-------------------------
# 普通用户账号密码
env.user = 'ubuntu'
env.password = 'Dwf12345'
# sudo权限账号密码
sudouser = 'ubuntu'
sudouser_passwd = 'Dwf12345'

# 这个是默认的三个端口
default_host = {'front_page': 8180, 'model_manage': 6060, 'service_manage': 9090, 'object_manage': 7070}
# 这个修改成第一台主机，以及映射出来的3个端口。默认IP递增1，step为有多少台主机
the_first_host = {'first_host': '192.168.3.1', 'front_page': 8501, 'model_manage': 6381, 'service_manage': 9411, 'object_manage': 7391, 'step': 60}
# 修改的2个配置文件，将这两个配置文件的值全部替换，
replace_files = ['/opt/apache-tomcat-8.5.34/webapps/modeler-web/config.js', '/opt/apache-tomcat-8.5.34/webapps/app-web/config.js']
# # --------------------------->


# 生成step个ip地址列表，step个8180列表，step个6060列表，step个7070列表，step个9090列表
env.hosts = addlist_hosts(first_host=the_first_host['first_host'], step=the_first_host['step'])
port_front_page_list = addlist_port(first_port=the_first_host['front_page'], step=the_first_host['step'])
port_model_manage_list = addlist_port(first_port=the_first_host['model_manage'], step=the_first_host['step'])
port_service_manage_list = addlist_port(first_port=the_first_host['service_manage'], step=the_first_host['step'])
port_object_manage_list = addlist_port(first_port=the_first_host['object_manage'], step=the_first_host['step'])


def modify():
    """
    主函数，执行这个
    :return:
    """
    index_place = env.hosts.index(env.host)
    with settings(user=sudouser, password=sudouser_passwd):
        for file in replace_files:
            replace(filename=file, old_value=default_host['model_manage'], new_value=port_model_manage_list[index_place])
            replace(filename=file, old_value=default_host['service_manage'], new_value=port_service_manage_list[index_place])
            replace(filename=file, old_value=default_host['object_manage'], new_value=port_object_manage_list[index_place])


# 修改配置项：
#   list(the_first_host)
# 执行命令
# fab -f dwf_modify_config.py modify
