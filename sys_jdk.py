# coding=utf-8
import fabfile
from fabric.api import env, sudo, run, settings

section = 'jdk'  # 指定config.ini的section名称
cf = fabfile.cf  # 读取fabfile文件的cf参数
# config.ini指定的通用参数
env.hosts, env.user, env.password, sudouser, sudouser_passwd = fabfile.get_common_var(section)
env.host = str(env.host)
software_home = fabfile.get_software_home(section)
# 需定义的参数
java_home = software_home


def install():
    local_file, file_name, upload_folder, upload_file = fabfile.get_upload_path(section)
    fabfile.put_file(section, env.host, env.hosts, env.user, env.password, upload_folder, upload_file)
    fabfile.decompress(section, upload_file, software_home, env.user, sudouser, sudouser_passwd)  # 解压到install_path(在函数decompress里面定义),无返回值
    # 正式开始配置
    path_file = fabfile.get_path_file(section, env.user, env.password)
    sudo('sed -i \'2a\export PATH=$JAVA_HOME/bin:$JRE_HOME/bin:$PATH\' %s' % path_file)  # PATH
    sudo('sed -i \'2a\export CLASSPATH=.:$JAVA_HOME/lib:$JRE_HOME/lib:$CLASSPATH\' %s' % path_file)  # CLASSPATH
    sudo('sed -i \'2a\export JRE_HOME=%s/jre\' %s' % (java_home, path_file))  # JRE_HOME
    sudo('sed -i \'2a\export JAVA_HOME=%s\' %s' % (java_home, path_file))  # JAVA_HOME
    # 输出注意事项：
    # 输出结果,输出host类型是list必须带",".join(),否则会显示[u]
    print('--------------------------------------\nfinish install jdk\n--------------------------------------')
    print('JAVA_HOME is \'%s\' and the system path have been written to %s' % (software_home, path_file))
    print('--------------------------------------')
    print('If you want to use JDK from root or use sudo,\nyou should execute\'sudo source /etc/profile\' in current shell')
