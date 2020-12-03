# 问题
1、fabfile新增一个sed的循环
循环判断给的参数：一一排除可以用来替换的分隔符，最后确定可以使用的分隔符，来做替换功能  
2、对于某些为空的值，不应该执行替换，应该做判断若非必填且为空，就跳过  
3、flink，增加on yarn  
YARN_CONF_DIR，HADOOP_CONF_DIR或者HADOOP_CONF_PATH配置以下path  
4、hadoop  
增加yarn的配置（否则yarn可能会报错(虽然不一定用)）  
```xml
<property>
<name>yarn.nodemanager.aux-services</name>
<value>mapreduce_shuffle</value>
</property>
<property>
<name>yarn.nodemanager.aux-services.mapreduce.shuffle.class</name>
<value>org.apache.hadoop.mapred.ShuffleHandler</value>
</property>
<property>
<name>yarn.resourcemanager.hostname</name>
<value>172.16.50.2</value>
</property>
<property>
<name>yarn.resourcemanager.am.max-attempts</name>
<value>4</value>
<description>The maximum number of application master execution attempts</description>
</property>
<property>
<name>yarn.nodemanager.vmem-check-enabled</name>
<value>false</value>
</property>
```



# 已解决
安装jdk，public版本的，写/etc/profile，对root用户不生效  
在安装完成之后，追加print几行，说明该情况，  
在/root/.bashrc下，行首增加source /etc/profile





# 已升级
sys_keyfree_login  
sys_jdk  
apache_zookeeper  
db_pg  
apache_cassandra  
  
# 未升级
apache_flink  
apache_hadoop  
apache_kafka  
apache_maven  
apache_scala  
apache_spark  
apache_storm  
dwf_deploy  
dwf_modify_config  
dwf_switch_tomcat  
sys_hostname__  
