# coding=utf-8
from fabric.api import *


def addlist_hosts(first_host, step):
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
    bbb = list()  # 指定[]会有警告，但是不影响使用；指定这个就没警告了
    bbb.append(first_port)
    i = 1
    while i <= step:
        bbb.append(first_port+i)
        i += 1
    return bbb


def replace(filename, old_value, new_value):
    run("sed -i 's:" + bytes(old_value) + ":" + bytes(new_value) + ":g' " + filename)


env.user = 'ubuntu'
env.password = 'Dwf12345'
sudouser = 'ubuntu'
sudouser_passwd = 'Dwf12345'

default_host = {'front_page': 8180, 'model_manage': 6060, 'service_manage': 9090, 'object_manage': 7070}
the_first_host = {'first_host': '192.168.1.101', 'front_page': 8401, 'model_manage': 6281, 'service_manage': 9311, 'object_manage': 7291, 'step': 1}
replace_files = ['/opt/apache-tomcat-8.5.34/webapps/modeler-web/config.js', '/opt/apache-tomcat-8.5.34/webapps/app-web/config.js']

env.hosts = addlist_hosts(first_host=the_first_host['first_host'], step=the_first_host['step'])
port_front_page_list = addlist_port(first_port=the_first_host['front_page'], step=the_first_host['step'])
port_model_manage_list = addlist_port(first_port=the_first_host['model_manage'], step=the_first_host['step'])
port_service_manage_list = addlist_port(first_port=the_first_host['service_manage'], step=the_first_host['step'])
port_object_manage_list = addlist_port(first_port=the_first_host['object_manage'], step=the_first_host['step'])


def modify():
    index_place = env.hosts.index(env.host)
    with settings(user=sudouser, password=sudouser_passwd):
        for file in replace_files:
            replace(filename=file, old_value=default_host['model_manage'], new_value=port_model_manage_list[index_place])
            replace(filename=file, old_value=default_host['service_manage'], new_value=port_service_manage_list[index_place])
            replace(filename=file, old_value=default_host['object_manage'], new_value=port_object_manage_list[index_place])



