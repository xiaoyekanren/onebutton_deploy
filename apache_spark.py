# coding=UTF-8
import fabfile
from fabric.api import *
import os

section = 'spark'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)
software_home = fabfile.get_software_home(section)
# config.ini指定的软件配置
# 定义软件参数
master_ip = cf.get(section, 'master_ip')
master_public_ip = cf.get(section, 'master_public_ip')
slaves = cf.get(section, 'slaves').split(',')
spark_worker_dir = cf.get(section, 'spark_worker_dir')
spark_work_opts = '"-Dspark.worker.cleanup.enabled=true -Dspark.worker.cleanup.interval=1800 -Dspark.worker.cleanup.appDataTtl=3600" '
spark_master_opts = '"-Dspark.master.rest.enabled=true"'
# 依赖
java_home = cf.get('spark', 'java_home')
hadoop_home = cf.get('spark', 'hadoop_home')
ld_library_path = os.path.join(hadoop_home, 'lib/native').replace('\\', '/')


# 安装
def install():
    # 检查是否是root用户，是就退出
    fabfile.check_user(env.user)
    # 上传
    upload_file = fabfile.upload(section)
    # 解压
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser,
                       sudouser_passwd)  # 解压到install_path(在函数decompress里面定义),无返回值
    # 正式开始安装
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建SPARK_WORKER_DIR文件夹并授权给spark所属用户
        sudo('mkdir -p %s' % spark_worker_dir)
        sudo('chown -R %s:%s %s' % (env.user, env.user, spark_worker_dir))

    # 开始配置spark
    with cd(software_home + '/conf'):  # 进入配置文件目录
        run('cp slaves.template slaves')
        run("cat /dev/null > slaves")  # 清空slaves文件
        for slave in slaves:  # 写Slaves文件
            run("echo %s>> slaves" % slave)
        # spark-env.sh
        run('cp spark-env.sh.template spark-env.sh')
        run("echo 'SPARK_MASTER_PORT=7077' >> spark-env.sh")  # spark默认端口
        run("echo 'SPARK_MASTER_HOST=%s' >> spark-env.sh" % master_ip)  # spark Master节点IP
        run("echo 'SPARK_LOCAL_IP=%s' >> spark-env.sh" % env.host)  # SPARK_LOCAL_IP
        # SPARK_HOME
        run("echo 'SPARK_HOME=%s' >> spark-env.sh" % software_home)
        # JAVA_HOME
        run("echo 'JAVA_HOME=%s' >> spark-env.sh" % java_home)
        # SPARK_WORKER_DIR
        run("echo 'SPARK_WORKER_DIR=%s' >> spark-env.sh" % spark_worker_dir)
        # SPARK_WORKER_OPTS
        run("echo 'SPARK_WORKER_OPTS=%s' >> spark-env.sh" % spark_work_opts)
        # SPARK_MASTER_OPTS
        run("echo 'SPARK_MASTER_OPTS=%s' >> spark-env.sh" % spark_master_opts)
        # LD_LIBRARY_PATH
        if hadoop_home != '':
            run("echo 'LD_LIBRARY_PATH=%s' >> spark-env.sh" % ld_library_path)


def start():
    with cd(software_home):
        if env.host == master_public_ip:
            with settings(prompts={
                'Are you sure you want to continue connecting (yes/no)? ': 'yes'
            }):
                run('sbin/start-all.sh')


def stop():
    with cd(software_home):
        if env.host == master_public_ip:
            run('sbin/stop-all.sh')


