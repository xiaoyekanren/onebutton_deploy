# coding=UTF-8
# Must already install [sshpass]
import fabfile
from fabric.api import *

# 读取fabfile文件的cf参数
cf = fabfile.cf
# 定义env
env.user = cf.get('keyfree_login', 'localuser')
env.password = cf.get('keyfree_login', 'localuser_passwd')
env.hosts = cf.get('keyfree_login', 'hosts').split(",")
# 定义sudo用户参数
sudouser = cf.get('keyfree_login', 'sudouser')
sudouser_passwd = cf.get('keyfree_login', 'sudouser_passwd')
# 需要拼接的字符串
hostsum = len(env.hosts)


# 安装
def install():
    run('rm -rf ~/.ssh')  # 删除已有的公钥私钥
    run('ssh-keygen -t rsa -f ~/.ssh/id_rsa -P ""')  # 生成公钥新的公钥私钥
    if env.host == env.hosts[-1]:  # 即在最后一个主机运行的时候，此时全部主机已经生成了id_rsa，通过scp将全部公钥拿到最后这个主机上，生成authorized_keys文件，并scp传到其他全部主机上
        with settings(user=sudouser, password=sudouser_passwd):  # 安装sshpass
            sudo('apt install sshpass -y')
        i = 0
        run('echo > ~/.ssh/authorized_keys')  # 创建或清空authorized_keys
        while i < hostsum:  # 通过scp将全部公钥拿到最后这个主机上，全部存入authorized_keys文件，将传过来的文件删除
            run('sshpass -p ' + env.password + ' scp ' + env.user + '@' + env.hosts[i] + ':~/.ssh/id_rsa.pub ./' + env.hosts[i] + ' && cat ' + env.hosts[i] + ' >> ~/.ssh/authorized_keys' + ' && rm -f ' + env.hosts[i])
            i = i+1
        i = 0
        while i < hostsum:  # scp传到其他全部主机上
            run('sshpass -p ' + env.password + ' scp ~/.ssh/authorized_keys ' + env.user + '@' + env.hosts[i] + ':~/.ssh/authorized_keys')
            i = i+1


# 卸载
def uninstall():
    run('rm -fr ~/.ssh')
