# 问题
1、fabfile新增一个sed的循环
循环判断给的参数：一一排除可以用来替换的分隔符，最后确定可以使用的分隔符，来做替换功能  
2、对于某些为空的值，不应该执行替换，应该做判断若非必填且为空，就跳过



# 已解决
## 安装jdk，public版本的，写/etc/profile，对root用户不生效
在安装完成之后，追加print几行，说明该情况，  
在/root/.bashrc下，行首增加source /etc/profile





# 已升级
sys_keyfree_login  
sys_jdk  
apache_zookeeper  
db_pg  
  
# 未升级
apache_cassandra  
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
sys_hostname  
