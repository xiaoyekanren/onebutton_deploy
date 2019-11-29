# onebutton_deploy
一键部署脚本，fabfile
## python==2.7
## python依赖
> * fabric==1.14.1
## 部署说明
### 可部署软件
> * hadoop
> * spark
> * cassandra
> * kafka
> * zookeeper
### 可部署的依赖性软件
> * jdk==1.8。*
> * scala
> * 多对多免密钥登录
> * 多对多增加hosts
> * 允许root进行ssh(没什么卵用)
## 配置文件
在passwd.ini文件里修改各个软件的服务器、配置等参数，多软件不冲突
## 使用方式
例如：

``` shell
fab -f apache_cassandra.py install
使用 -w 可跳过失败
```