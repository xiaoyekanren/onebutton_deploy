# onebutton_deploy
一键部署脚本，fabric
## python==2.7
## python依赖
> * fabric==1.14.1
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
> * 多对多免密钥登录
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
