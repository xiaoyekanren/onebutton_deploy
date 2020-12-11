# 问题
1、fabfile新增一个sed的循环
循环判断给的参数：一一排除可以用来替换的分隔符，最后确定可以使用的分隔符，来做替换功能  
2、对于某些为空的值，不应该执行替换，应该做判断若非必填且为空，就跳过  
3、flink，增加on yarn  
YARN_CONF_DIR，HADOOP_CONF_DIR或者HADOOP_CONF_PATH配置以下path  
4、flink集群模式，不会写slaves
5、增加判断，tar.gz 和zip的包的解压缩方式不通
5.2、将tar.gz和tgz的上传之后统一为tgz修改下
6、kafka的brokerid，能否通过确定env.host在env.hosts的顺序来确定是几
7、kafka拼zookeeper的方式是否可以简化？
8、增加flink on yarn


# 已升级
sys_keyfree_login  
sys_jdk  
apache_zookeeper  
db_pg  
apache_cassandra  
apache_hadoop  
apache_spark  
apache_kafka  
apache_flink  
# 未升级
apache_maven  
apache_scala  
apache_storm  
dwf_deploy  
dwf_modify_config  
dwf_switch_tomcat  
sys_hostname__  
