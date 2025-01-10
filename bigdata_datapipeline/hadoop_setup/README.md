# Hadoop Docker (version 3.2.4)

## Quick Start
### First, build the hadoop base:
```bash
docker build -t my_hadoop_3.2.4:base ./base/
```

, or if you don't want to build from scratch, you can use these commands:
```bash
docker pull danchoi2001/my_hadoop_3.2.4:base
```
```bash
docker image tag danchoi2001/my_hadoop_3.2.4:base my_hadoop_3.2.4:base 
```

### To deploy an example HDFS cluster, run:
```bash
docker compose -f docker-compose_one_datanode.yml -p one_datanode up
```

### Run example wordcount job:
```bash
for f in test_wordcount/*; do docker cp $f namenode:/root; done
```

```bash
docker exec -it namenode bash
```

```bash
bash run-wordcount.sh
```

`docker compose` creates a docker network that can be found by running `docker network list`, e.g. `docker-hadoop_hadoop_network`.

### Run `docker network inspect` on the network (e.g. `dockerhadoop_default`) to find the IP the hadoop interfaces are published on. Access these interfaces with the following URLs:

* Namenode: http://<dockerhadoop_IP_address>:9870/dfshealth.html#tab-overview
* History server: http://<dockerhadoop_IP_address>:8188/applicationhistory
* Datanode: http://<dockerhadoop_IP_address>:9864/
* Nodemanager: http://<dockerhadoop_IP_address>:8042/node
* Resource manager: http://<dockerhadoop_IP_address>:8088/

### To quickly get address of these components, run:
```bash
bash get_address.sh your_network_name
```
Replace `your_network_name` with the actual name of the network you want to inspect.
## Configure Environment Variables

The configuration parameters can be specified in the hadoop.env file or as environmental variables for specific services (e.g. namenode, datanode etc.):
```
  CORE_CONF_fs_defaultFS=hdfs://namenode:8020
```

CORE_CONF corresponds to core-site.xml. fs_defaultFS=hdfs://namenode:8020 will be transformed into:
```
  <property><name>fs.defaultFS</name><value>hdfs://namenode:8020</value></property>
```
To define `dash` inside a configuration parameter, use `triple underscore`, such as YARN_CONF_yarn_log___aggregation___enable=true (yarn-site.xml):
```
  <property><name>yarn.log-aggregation-enable</name><value>true</value></property>
```

The available configurations are:
* /etc/hadoop/core-site.xml CORE_CONF
* /etc/hadoop/hdfs-site.xml HDFS_CONF
* /etc/hadoop/yarn-site.xml YARN_CONF
* /etc/hadoop/httpfs-site.xml HTTPFS_CONF
* /etc/hadoop/kms-site.xml KMS_CONF
* /etc/hadoop/mapred-site.xml  MAPRED_CONF

### If you need to extend some other configuration file, refer to [base/entrypoint.sh](base/entrypoint.sh) bash script.

## Testing and Benchmarking
- Fault tolerance test [here](https://nathan-torento.medium.com/distributed-systems-fault-tolerance-tutorial-78b825f8cada)
- Benchmarking [here](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-common/Benchmarking.html)
