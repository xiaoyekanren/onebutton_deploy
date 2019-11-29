# coding=UTF-8
from fabric.api import *
import fabfile
import os

# 读取fabfile文件的cf参数,读取passwd.ini文件
cf = fabfile.cf
# 定义env
env.user = cf.get('hadoop', 'localuser')
env.password = cf.get('hadoop', 'localuser_passwd')
env.hosts = cf.get('hadoop', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('hadoop', 'sudouser')
sudouser_passwd = cf.get('hadoop', 'sudouser_passwd')
# 定义软件参数
hadoop_local_file = cf.get('hadoop', 'hadoop_local_file')
hadoop_folder = cf.get('hadoop', 'hadoop_folder')  # 即解压之后的文件夹名称
data_folder = cf.get('hadoop', 'data_folder').split(',')
java_home = cf.get('hadoop', 'java_home')
dfs_replication = cf.get('hadoop', 'dfs_replication')
# 需要拼接的字符串
hadoop_upload_file_path = os.path.join('/home', env.user, 'hadoop.tar.gz').replace('\\', '/')
hadoop_home = os.path.join('/home', env.user, hadoop_folder).replace('\\', '/')
hadoop_config_folder = os.path.join(hadoop_home, 'etc/hadoop').replace('\\', '/')
master_ip = cf.get('hadoop', 'master_ip')
slaves = cf.get('hadoop', 'slaves').split(',')


# 安装
def install():
    if env.user == 'root':
        print ("can't install by root")
        exit()
    # 上传
    put(hadoop_local_file, hadoop_upload_file_path)
    # 解压&删除
    run('tar -zxvf hadoop.tar.gz && rm -f hadoop.tar.gz')
    # run('rm -rf ' + hadoop_folder + ' && tar -zxvf hadoop.tar.gz')  # 测试使用，可以免删除
    # 创建目录
    run('mkdir -p ' + hadoop_home + '/tmp')
    with settings(user=sudouser, password=sudouser_passwd):  # 使用sudo用户，创建文件夹并授权给hadoop所属用户
        for folder in data_folder:
            sudo('mkdir -p ' + folder)
            sudo('chown -R ' + env.user + ':' + env.user + ' ' + folder)
    # 修改配置文件
    with cd(hadoop_config_folder):
        # hadoop-env.sh
        run("sed -i 's:export JAVA_HOME=.*:export JAVA_HOME=" + java_home + ":g' hadoop-env.sh")  # 修改hadoop-env.sh的jdk路径
        # slaves
        run("cat /dev/null > slaves")  # 清空
        for slave in slaves:
            run("echo " + slave + ">> slaves")  # 依次写入
        # core-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-common/core-default.xml
        run("sed -i '$i\<property>' core-site.xml")
        run("sed -i '$i\<name>hadoop.tmp.dir</name>' core-site.xml")  # A base for other temporary directories.其他临时目录的基础，本脚本除了数据目录外未配置其他临时目录，若不配置数据目录则数据目录会在此目录下
        run("sed -i '$i\<value>" + hadoop_home + '/tmp' + "</value>' core-site.xml ")
        run("sed -i '$i\</property>' core-site.xml")

        run("sed -i '$i\<property>' core-site.xml")
        run("sed -i '$i\<name>fs.default.name</name>' core-site.xml")  # 真实的hdfs的链接+端口
        run("sed -i '$i\<value>hdfs://" + master_ip + ":9000</value>' core-site.xml ")
        run("sed -i '$i\</property>' core-site.xml")

        run("sed -i '$i\<property>' core-site.xml")
        run("sed -i '$i\<name>hadoop.proxyuser." + env.user + ".hosts</name>' core-site.xml")  # 配置访问用户的代理用户是env.user，其他程序调用hdfs的时候需要
        run("sed -i '$i\<value>*</value>' core-site.xml")
        run("sed -i '$i\</property>' core-site.xml")

        run("sed -i '$i\<property>' core-site.xml")
        run("sed -i '$i\<name>hadoop.proxyuser." + env.user + ".groups</name>' core-site.xml")  # 同上
        run("sed -i '$i\<value>*</value>' core-site.xml")
        run("sed -i '$i\</property>' core-site.xml")
        # hdfs-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-project-dist/hadoop-hdfs/hdfs-default.xml
        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.datanode.data.dir</name>' hdfs-site.xml")  # 修改hdfs数据目录，支持多或单挂载路径
        run("sed -i '$i\<value>' hdfs-site.xml")
        run("sed -i '$i" + cf.get('hadoop', 'data_folder') + "' hdfs-site.xml")
        run("sed -i '$i\</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.http.address</name>' hdfs-site.xml")  # namenode web管理链接+端口
        run("sed -i '$i\<value>" + master_ip + ":50070</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.namenode.secondary.http-address</name>' hdfs-site.xml")  # SecondaryNameNode链接+端口
        run("sed -i '$i\<value>" + master_ip + ":50090</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.replication</name>' hdfs-site.xml")  # 存储数据的副本数量
        run("sed -i '$i\<value>" + dfs_replication + "</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.permissions</name>' hdfs-site.xml")  # hdfs的权限验证，没有特殊要求关闭即可，这个地方如果开启会造成除env.user外的用户访问hdfs会没有权限
        run("sed -i '$i\<value>false</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")

        run("sed -i '$i\<property>' hdfs-site.xml")
        run("sed -i '$i\<name>dfs.webhdfs.enabled</name>' hdfs-site.xml")  # 打开这个，否则访问50070的web浏览数据时会报错
        run("sed -i '$i\<value>true</value>' hdfs-site.xml")
        run("sed -i '$i\</property>' hdfs-site.xml")
        # 写mapred-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-mapreduce-client/hadoop-mapreduce-client-core/mapred-default.xml
        run('cp mapred-site.xml.template  mapred-site.xml')
        run("sed -i '$i\<property>' mapred-site.xml")
        run("sed -i '$i\<name>mapreduce.jobtracker.http.address</name>' mapred-site.xml")  # 作业跟踪管理器的HTTP服务器访问端口和地址
        run("sed -i '$i\<value>" + master_ip + ":50030</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")

        run("sed -i '$i\<property>' mapred-site.xml")
        run("sed -i '$i\<name>mapreduce.jobtracker.handler.count</name>' mapred-site.xml")  # jobtracker的线程数
        run("sed -i '$i\<value>10</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")

        run("sed -i '$i\<property>' mapred-site.xml")
        run("sed -i '$i\<name>mapreduce.tasktracker.map.tasks.maximum</name>' mapred-site.xml")  # map的最大tasks，这个地方和下面的reduce的tasks仅仅是最大值，实际值可在运行的程序里设置
        run("sed -i '$i\<value>16</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")

        run("sed -i '$i\<property>' mapred-site.xml")
        run("sed -i '$i\<name>mapreduce.tasktracker.reduce.tasks.maximum</name>' mapred-site.xml")  # reduce的最大tasks，一般设置成服务器的核心数，校内一般不使用mapreduce功能，故不作修改
        run("sed -i '$i\<value>16</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")

        run("sed -i '$i\<property>' mapred-site.xml")
        run("sed -i '$i\<name>mapreduce.framework.name</name>' mapred-site.xml")  # 执行MapReduce作业的运行时框架。Can be one of local, classic or yarn.
        run("sed -i '$i\<value>yarn</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")

        run("sed -i '$i\<property>' mapred-site.xml")
        run("sed -i '$i\<name>mapreduce.jobhistory.address</name>' mapred-site.xml")   # JobHistory-IPC的IP+端口
        run("sed -i '$i\<value>" + master_ip + ":10020</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")
        run("sed -i '$i\<property>' mapred-site.xml")
        run("sed -i '$i\<name>mapreduce.jobhistory.webapp.address</name>' mapred-site.xml")   # JobHistory的IP+端口
        run("sed -i '$i\<value>" + master_ip + ":19888</value>' mapred-site.xml")
        run("sed -i '$i\</property>' mapred-site.xml")
        # 写yarn-site.xml
        # https://hadoop.apache.org/docs/r2.7.7/hadoop-yarn/hadoop-yarn-common/yarn-default.xml
        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.address</name>' yarn-site.xml")  # The address of the applications manager interface in the RM. resourcemanager的IP+端口
        run("sed -i '$i\<value>" + master_ip + ":8032</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.scheduler.address</name>' yarn-site.xml")  # The address of the scheduler interface.调度程序接口的地址。
        run("sed -i '$i\<value>" + master_ip + ":8030</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.webapp.address</name>' yarn-site.xml")  # RM web application的地址，即yarn的web
        run("sed -i '$i\<value>" + master_ip + ":8088</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.admin.address</name>' yarn-site.xml")  # The address of the RM admin interface.RM管理界面的地址
        run("sed -i '$i\<value>" + master_ip + ":8033</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.nodemanager.webapp.address</name>' yarn-site.xml")  # nodemanager的IP+端口
        run("sed -i '$i\<value>" + master_ip + ":8042</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.nodemanager.aux-services</name>' yarn-site.xml")  # 貌似是yarn任务的命名方式？？？
        run("sed -i '$i\<value>mapreduce_shuffle</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.log-aggregation-enable</name>' yarn-site.xml")  # 日志聚合，开启后可自动把yarn日志保存到hdfs的/tmp/logs下，通过配置yarn.nodemanager.remote-app-log-dir来修改日志路径
        run("sed -i '$i\<value>true</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.nodemanager.resource.memory-mb</name>' yarn-site.xml")  # 当前节点yarn可用的内存总量
        run("sed -i '$i\<value>8192</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.nodemanager.resource.cpu-vcores</name>' yarn-site.xml")  # 当前节点yarn可用的CPU核心数量
        run("sed -i '$i\<value>8</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.scheduler.minimum-allocation-mb</name>' yarn-site.xml")  # 单个任务可申请内存的最小值
        run("sed -i '$i\<value>1024</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.scheduler.maximum-allocation-mb</name>' yarn-site.xml")  # 单个任务可申请内存的最大值
        run("sed -i '$i\<value>8096</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.scheduler.minimum-allocation-vcores</name>' yarn-site.xml")  # 单个任务可申请CPU的最小值
        run("sed -i '$i\<value>1</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.scheduler.maximum-allocation-vcores</name>' yarn-site.xml")  # 单个任务可申请CPU的最大值
        run("sed -i '$i\<value>4</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        run("sed -i '$i\<property>' yarn-site.xml")
        run("sed -i '$i\<name>yarn.resourcemanager.am.max-attempts</name>' yarn-site.xml")  # MapReduce application master在集群中的最大尝试次数
        run("sed -i '$i\<value>4</value>' yarn-site.xml")
        run("sed -i '$i\</property>' yarn-site.xml")

        if env.host == master_ip:  # 格式化namenode，只格式化master节点
            with cd(hadoop_home):
                run('bin/hdfs namenode -format')


def start():
    if env.host == master_ip:
        with cd(hadoop_home):
            run('sbin/start-all.sh')
            run('sbin/mr-jobhistory-daemon.sh start historyserver')


def stop():
    if env.host == master_ip:
        with cd(hadoop_home):
            run('sbin/stop-all.sh')
            run('sbin/mr-jobhistory-daemon.sh stop historyserver')
