# coding=utf-8
from fabric.api import *
import fabfile
import os

# 读取fabfile文件的cf参数,读取passwd.ini文件
cf = fabfile.cf
# 定义env
env.user = cf.get('dwf', 'localuser')
env.password = cf.get('dwf', 'localuser_passwd')
env.hosts = cf.get('dwf', 'hosts').split(',')
# 定义sudo用户参数
sudouser = cf.get('dwf', 'sudouser')
sudouser_passwd = cf.get('dwf', 'sudouser_passwd')
dwf_url = cf.get('dwf', 'dwf_url')
user_home = cf.get('dwf', 'user_home')
if not user_home:
    user_home = os.path.join('/home', env.user).replace('\\', '/')

# --define--
dpath = user_home
FILE_PATH = "%s/setupfiles" % dpath
SETUP_FILE = "%s/setupfiles.tar.gz" % dpath
# JDK路径设置
JDK_INSTALL_DIR = "/opt/jdk1.8.0_181"
JDK_PATH = "%s/jdk1.8.0_181" % FILE_PATH
# maven路径设置
Maven_INSTALL_DIR = "/opt/maven-3.6.1"
Maven_PATH = "%s/maven-3.6.1" % FILE_PATH
# Node路径设置
NODE_INSTALL_DIR = "/opt/node-v10.16.0"
NODE_PATH = "%s/node-v10.16.0" % FILE_PATH
# Tomcat路径设置
Tomcat_INSTALL_DIR = "/opt/apache-tomcat"
Tomcat_PATH = "%s/apache-tomcat" % FILE_PATH
# Pg路径设置
PG_INSTALL_DIR = "/opt/pgsql"
PG_PATH = "%s/pgsql" % FILE_PATH
# dwf
DWF_INSTALL_DIR = "/opt/dwf3.0-deploy"
DWF_PATH = "%s/dwf3.0-deploy" % FILE_PATH


def check_user():
    if env.user == 'root':
        print ("can't install by root")
        exit()


# 杀死当前全部java进程，虽然是新机器
def killpid():
    sudo("ps aux | grep '[d]wf-modeler' | awk '{print $2}' | xargs kill -9")
    sudo("ps aux | grep '[d]wf-app' | awk '{print $2}' | xargs sudo kill -9")
    sudo("ps aux | grep '[d]wf-monitor' | awk '{print $2}' | xargs kill -9")
    sudo("ps aux | grep '[p]ostgres' | awk '{print $2}' | xargs sudo kill -9")
    sudo("ps aux | grep '[t]omcat' | awk '{print $2}' | xargs sudo kill -9")


def upload_release():
    # 下载
    # run('wget -O setupfiles.tar.gz %s' % dwf_url)
    # 解压&删除
    run('tar -zxf %s' % SETUP_FILE)
    # 删除
    # run('rm -f %s' % SETUP_FILE)


# 安装
def mkdir():
    with settings(user=sudouser, password=sudouser_passwd):
        # 创建opt目录
        sudo('mkdir -p /opt')
        sudo('chown -R %s:%s /opt' % (env.user, env.user))


def install_jdk():
    run('mv %s /opt/' % JDK_PATH)
    sudo("sed -i '$a export JAVA_HOME=/opt/jdk1.8.0_181' /etc/profile")
    sudo("sed -i '$a export CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH' /etc/profile")
    sudo("sed -i '$a export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH' /etc/profile")
    sudo("update-alternatives --install /usr/bin/java java %s/bin/java 300" % JDK_INSTALL_DIR)
    sudo("update-alternatives --install /usr/bin/javac javac %s/bin/javac 300" % JDK_INSTALL_DIR)
    sudo("update-alternatives --install /usr/bin/jar jar %s/bin/jar 300" % JDK_INSTALL_DIR)
    sudo("update-alternatives --install /usr/bin/javah javah %s/bin/javah 300" % JDK_INSTALL_DIR)
    sudo("update-alternatives --install /usr/bin/javap javap %s/bin/javap 300" % JDK_INSTALL_DIR)
    sudo("update-alternatives --install /usr/bin/jps jps %s/bin/jps 300" % JDK_INSTALL_DIR)
    sudo("update-alternatives --config java")


def install_mvn():
    run('mv %s /opt/' % Maven_PATH)
    sudo("sed -i '$a export MVN_HOME=/opt/maven-3.6.1' /etc/profile")
    sudo("sed -i '$a export CLASSPATH=.:$MVN_HOME/lib:$CLASSPATH' /etc/profile")
    sudo("sed -i '$a export PATH=$MVN_HOME/bin:$PATH' /etc/profile")
    sudo("")


def install_node():
    run('mv %s /opt/' % NODE_PATH)
    sudo("sed -i '$a export NODE_HOME=/opt/node-v10.16.0' /etc/profile")
    sudo("sed -i '$a export CLASSPATH=.:$NODE_HOME/lib:$CLASSPATH' /etc/profile")
    sudo("sed -i '$a export PATH=$NODE_HOME/bin:$PATH' /etc/profile")
    sudo("sed -i '$a export NODE_OPTIONS=--max_old_space_size=4096' /etc/profile")
    sudo("update-alternatives --install /usr/bin/node node %s/bin/node 300" % NODE_INSTALL_DIR)
    sudo("update-alternatives --install /usr/bin/npm npm %s/bin/npm 300" % NODE_INSTALL_DIR)


def install_tomcat():
    run('mv %s %s' % (Tomcat_PATH, Tomcat_INSTALL_DIR))
    sudo("sed -i 's/8080/8180/' %s/conf/server.xml" % Tomcat_INSTALL_DIR)


def install_pg():
    # 增加该行用来静默安装
    sudo("sed -i '$a export DEBIAN_FRONTEND=noninteractive' /etc/profile")
    with cd(PG_PATH):
        sudo("dpkg -i libssl1.1_1.1.1-1ubuntu2.1_18.04.4_amd64.deb")
        sudo("dpkg -i libpq5_10.10-0ubuntu0.18.04.1_amd64.deb")
        sudo("dpkg -i libkrb5support0_1.16-2ubuntu0.1_amd64.deb")
        sudo("dpkg -i libkrb5-3_1.16-2ubuntu0.1_amd64.deb")
        sudo("dpkg -i libicu60_60.2-3ubuntu3_amd64.deb")
        sudo("dpkg -i libgssapi-krb5-2_1.16-2ubuntu0.1_amd64.deb")
        sudo("dpkg -i postgresql-client-common_190_all.deb")
        sudo("dpkg -i ssl-cert_1.0.39_all.deb")
        sudo("dpkg -i postgresql-common_190_all.deb")
        sudo("dpkg -i postgresql-client-10_10.10-0ubuntu0.18.04.1_amd64.deb")
        sudo("dpkg -i postgresql-10_10.10-0ubuntu0.18.04.1_amd64.deb")
        # ----------
        sudo("sudo -u postgres /usr/lib/postgresql/10/bin/psql -d postgres -w -c \"ALTER USER postgres WITH SUPERUSER PASSWORD '123456'\"")
        sudo('sudo -u postgres /usr/lib/postgresql/10/bin/psql -d postgres -w -c "CREATE DATABASE dataway OWNER postgres"')
        sudo('sudo -u postgres /usr/lib/postgresql/10/bin/psql -d dataway < %s/db-pure.sql' % FILE_PATH)
        # ----------
        sudo('sed -i "s/^#listen_addresses =.*$/listen_addresses = \'*\'/g" /etc/postgresql/10/main/postgresql.conf')
        sudo('sed -i "s/^max_connections.*$/max_connections=1000/g" /etc/postgresql/10/main/postgresql.conf')
        sudo('sed -i \'$a host all all 0.0.0.0 0.0.0.0 md5\' /etc/postgresql/10/main/pg_hba.conf')
        # ----------startup
        sudo('sudo -u postgres /usr/lib/postgresql/10/bin/pg_ctl restart -D /var/lib/postgresql/10/main ')
    # 删除本函数首行
    sudo("sed -i '/export DEBIAN_FRONTEND=noninteractive/d' /etc/profile")


def startup():
    # with cd('%s/bin' % Tomcat_INSTALL_DIR):
    #     run('nohup ./startup.sh >> /dev/null 2>&1 &')
    pass


def install():
    check_user()
    upload_release()
    mkdir()
    install_jdk()
    install_mvn()
    install_node()
    install_tomcat()
    install_pg()


# # 要新增的功能
# 新增maven源
# 新增node源
# 启动tomcat
# ubuntu支持中文


# # 完成功能
# ubuntu中文乱码（临时通过解压不显示log解决）
