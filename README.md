# onebutton_deploy
一键部署脚本，fabric
## python==2.7
## python依赖
> * fabric==1.14.1
> * paramiko
> * configparser
## 部署说明
### 可部署软件
> * cassandra==3.0.18
> * flink==1.7.2
> * hadoop>=2.7.7 && <=2.8.5
> * kafka==2.12-2.3.0
> * spark==2.2.3
> * storm==1.2.3
> * zookeeper==3.4.13
> * postgresql==10.10-2
### 可部署的依赖性软件
> * scala==2.12.8
> * 多对多增加hosts
> * jdk==1.8.*
> * 多对多免密钥登录,适用于新机器部署，会清理掉其他已存在的密钥
## 配置文件
在passwd.ini文件里修改各个软件的服务器、配置等参数，多软件不冲突
## 方法
> * install
> * start
> * stop
## 使用方式
例如：
加入我要安装jdk，首先需要打开passwd.ini修改jdk's section的相关参数，之后执行:
``` shell
fab -f sys-jdk_install.py install
使用 -w 可跳过失败
```
就可以了
## 注意
# fab 隐藏输出
```shell script
fab -f test_fabric.py start --hide stdout,user,aborts,warnings,stderr
```
省略所有输出  

--hide stdout 省略脚本原本打印在屏幕上的内容，比如ls，echo的内容，都不会输出  
--hide running省略输出要执行的命令  
--hide status 省略输出脚本执行完后的状态信息，如Done、Disconnecting from 218.241.103.123... done.等  
--hide user   省略用户自定义生成的输出。比如：使用 fastprint 或者 puts 函数产生的输出。  
--hide aborts 终止信息。和状态信息一样，只有当 Fabric 做为库使用的时候才可能应该关闭，而且还并不一定。注意，即使该输出集被关闭了，并不能阻止程序退出——你只会得不到任何 Fabric 退出的原因。  
--hide warning 警报信息。通常在预计指定操作失败时会将其关闭，比如说你可能使用grep来测试文件中是否有特定文字。如果设置env.warn_only为True会导致远程程序执行失败时完全没有警报信息。和aborts一样，这项设置本身并不控制警报行为，仅用于是否输出警报信息。  
--hide stderr 省略脚本原本打印在屏幕上的错误报警内容，比如ls，echo的内容，都不会输出  