# Start over
1. remove volumes docker (use with caution):
```
docker volume prune -af
```
2. remove all app_data (use with caution):
```
rm -rf app_data/hadoop_*
rm -rf app_data/kafka_*
rm -rf app_data/nifi
```
or simply use `bash start_over.sh` commad

# first give full access to app_data folder
```
sudo chown -R 1001:1001 app_data
```
# start docker compose:
```
docker compose -f docker-compose-cluster.yml up
```
# Wait for Kafka Connect to be started: 
```
bash -c ' \
echo -e "\n\n=============\nWaiting for Kafka Connect to start listening on localhost ...\n=============\n"
while [ $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) -ne 200 ] ; do
  echo -e "\t" $(date) " Kafka Connect listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) " (waiting for 200)"
  sleep 5
done
echo -e $(date) "\n\n--------------\n\o/ Kafka Connect is ready! Listener HTTP state: " $(curl -s -o /dev/null -w %{http_code} http://localhost:8083/connectors) "\n--------------\n"
'
```

# Make sure that the Debezium connectors are available:
```
curl -s localhost:8083/connector-plugins|jq '.[].class'|egrep 'MySqlConnector|MongoDbConnector'
```

# Get a MySQL prompt:
```
docker exec -it mysql bash -c 'mysql -u root -p$MYSQL_ROOT_PASSWORD demo'
```
```
SELECT * FROM ORDERS ORDER BY CREATE_TS DESC LIMIT 1\G
```

# data generator:
```
docker exec mysql /data/02_populate_more_orders.sh
```

# check new rows:
```
watch -n 1 -x docker exec -t mysql bash -c 'echo "SELECT * FROM ORDERS ORDER BY CREATE_TS DESC LIMIT 1 \G" | mysql -u root -p$MYSQL_ROOT_PASSWORD demo'
```

# create new connector:
```
curl -i -X PUT -H  "Content-Type:application/json" \
    http://localhost:8083/connectors/source-debezium-orders-00/config \
    -d '{
            "connector.class": "io.debezium.connector.mysql.MySqlConnector",
            "database.hostname": "mysql",
            "database.port": "3306",
            "database.user": "debezium",
            "database.password": "dbz",
            "database.server.id": "42",
            "database.server.name": "alo123",
            "table.whitelist": "demo.orders",
            "database.history.kafka.bootstrap.servers": "kafka-0:9092,kafka-1:9092,kafka-2:9092",
            "database.history.kafka.topic": "dbhistory.demo" ,
            "decimal.handling.mode": "double",
            "include.schema.changes": "true",
            "tombstones.on.delete": "true",
            "transforms": "unwrap,addTopicPrefix",
            "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState",
            "transforms.addTopicPrefix.type":"org.apache.kafka.connect.transforms.RegexRouter",
            "transforms.addTopicPrefix.regex":"(.*)",
            "transforms.addTopicPrefix.replacement":"mysql-debezium-$1"
    }'
```

# check connector status (also reveal username and password):
```
curl -s "http://localhost:8083/connectors?expand=info&expand=status" | \
       jq '. | to_entries[] | [ .value.info.type, .key, .value.status.connector.state,.value.status.tasks[].state,.value.info.config."connector.class"]|join(":|:")' | \
       column -s : -t| sed 's/\"//g'| sort
```

# view the topic using kafkacat
```
docker exec kafkacat kafkacat \
        -b kafka-0:9092,kafka-1:9092,kafka-2:9092 \
        -r http://schema-registry:8081 \
        -s avro \
        -t timescaledb.data.pricing \
        -C -o -10 -q | jq '.id, .CREATE_TS.string'
```

# if you don't want to wait for downloading jars, use the following command (solved the permission problem by add user:root in docker compose):
```
docker cp backup_ivy2/.ivy2 spark-master-1:/root/
docker cp backup_ivy2/.ivy2 spark-master-2:/root/
```
backup ivy2 folder command: `docker cp spark-master-2:/root/.ivy2 backup_ivy2/`

# spark-submit command
first install requests
```
docker exec spark-master-1 pip install requests
docker exec spark-master-2 pip install requests
```

## Testing
```
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 /opt/bitnami/spark/work/calculate_sum.py
```

## load with --packages
ok
```
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /opt/bitnami/spark/work/simple_sparkdf.py
```
```
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0 /opt/bitnami/spark/work/avro_example.py
```
To run below command, you `must` have player.csv in all machines (in this case: 1 master, 2 workers), and `must` in the same path, or it will error (file doesn't not exist)!!! (Simple solution: send it to hdfs, then process it)
```
docker cp spark_submits/simple_real_world_case/player.csv namenode:/root
```
```
docker exec namenode hdfs dfs -put /root/player.csv /
```
```
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 /opt/bitnami/spark/work/simple_real_world_case/manipulate_pyspark.py
```
## load with --jars (often has many errors, should not be used, only for learning purpose)
```
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 --conf spark.driver.host=localhost --jars /root/.ivy2/jars/org.apache.spark_spark-sql-kafka-0-10_2.12-3.5.0.jar,/root/.ivy2/jars/org.apache.spark_spark-streaming-kafka-0-10_2.12-3.5.0.jar /opt/bitnami/spark/work/simple_real_world_case/manipulate_pyspark.py
```

# Example save parquet file to HDFS
get address of Hadoop components
```
bash hadoop_setup/get_address.sh bigdata_draft1_default
```

create folder /output in HDFS
```
docker exec namenode hdfs dfs -mkdir /output
```

write to HDFS
```
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 /opt/bitnami/spark/work/learn_parquet/write_parquet.py
```

read back parquet file from HDFS
```
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 /opt/bitnami/spark/work/learn_parquet/read_parquet.py
```

# Save kafka streaming file parquet to HDFS
you need to modify from line 51
```
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0 /opt/bitnami/spark/work/read_stream_mysql.py
```

# Read Parquet file from HDFS and write to PostgreSQL
based on this [stackoverflow answer](https://stackoverflow.com/a/40822115/18448121), we can use this:
```
docker exec spark-master-2 spark-submit --master spark://spark-master-2:27077 --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0,org.postgresql:postgresql:42.7.0 /opt/bitnami/spark/work/read_parquet_hdfs_to_postgre.py
```
access Postgres, password: `password123`
```
docker exec -it postgres-datamart psql -U my_user -d car_database
```
start query
```
select * from typeofcar limit 10;
```
count records
```
select count(*) from typeofcar;
```

# Superset
This assume you have been turned off all the other services in this project

To connect to superset, first, `uncomment the last 2 rows of postgresql service`

Then `use the following command`:
```
IP_ADDRESS=$(ip addr show | grep "\binet\b.*\bdocker0\b" | awk '{print $2}' | cut -d '/' -f 1)

docker compose -f docker-compose-cluster.yml up postgresql
```

After the postgresql service started up, go to superset `localhost:8088`

Click +, Data -> Connect database -> PostgreSQL and fill the following information:
```
Host: find the ip address of postgres-datamart
Port: 5432
Database name: car_database
Username: my_user
Password: password123
```

Use this [link](https://superset.apache.org/docs/creating-charts-dashboards/creating-your-first-dashboard/) to create new dashboard

# Test the system:
First, use the following command to show docker stats:
```
bash docker_stats.sh
```

After triggered the Debezium connector, and populate more data into MySQL, using the following command to count Record per Second in MySQL:
```
bash mysql_records_per_second.sh 
```

Count new offsets per second in specific Kafka Topic:
```
bash kafka_offsets_per_second.sh
```

# Connect MongoDB
## Setup pure MongoDB (not yet, gặp lỗi dùng mongosh mà không cần xác thực)
After the container has started up, acess the mongodb container:
```
docker exec -it mongo1 bash
```
and use the following command:
```
mongosh --eval "rs.initiate({_id:'dbrs', members: [{_id:0, host: 'mongo1:27017'},{_id:1, host: 'mongo2:27017'},{_id:2, host: 'mongo3:27017'}]})"
```
, then create admin account:
```
mongosh admin
```
```
db.createUser(
  {
    user: "root",
    pwd: "123456",
    roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]
  }
)
```
Press `Ctrl + D` to exit

Access admin database to create user:
```
mongosh -u root -p 123456 admin
```
## Setup with bitnami image (hiện tại đang gặp lỗi Heartbeat failed after max retries):
After the container has started up, acess the mongodb container:
```
docker exec -it mongo1 bash
```
Access admin database to create user:
```
mongosh -u $MONGODB_ROOT_USER -p $MONGODB_ROOT_PASSWORD admin
```
---
Create a user
```
db.createUser(
 {
   user: "flink", // cái này a tạo cho em tên bất kì
   pwd: "flinkpw",  // cái này cũng vậy
   roles: []
 }
);
```
Create roles: flink_role and readOplog
```
db.createRole(
   {
     role: "flink_role", 
     privileges: [
        { resource: { db: "", collection: "" }, actions: [ "find", "changeStream" ] }
     ],
     roles: []
   }
);

db.createRole({
  role: "readOplog",
  privileges: [
    { resource: { db: "local", collection: "oplog.rs" }, actions: ["find"] }
  ],
  roles: []
});
```
Grant a role to a user
```
db.grantRolesToUser(
    "flink",
    [
      // Note：db refers to the db when the role is created. Roles created under admin can have access permissions on different databases
      { role: "flink_role", db: "admin" },
      { role: "readOplog", db: "admin" },
      { role: "read", db: "inventory" }
    ]
);
```

Go to Compass, enter credenticals
Create new database `inventory`
```
use inventory;
```

Create new collection `trips`
```
db.createCollection("trips");
```

Add data to `trips` collection using trips.json

## Setup Connector
Find IP addresses of mongodb containers
```
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mongo1
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mongo2
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mongo3
```
Add connector (this ok now)
```shell
curl -i -X PUT -H  "Content-Type:application/json" \
    http://localhost:8083/connectors/mongo-kafka-source-00/config \
    -d '{
        "connector.class" : "io.debezium.connector.mongodb.MongoDbConnector",
        "topic.prefix" : "trips-inventory",
        "mongodb.connection.string" : "mongodb://mongo1:27017/?replicaSet=rs0&directConnection=true&authSource=admin",
        "mongodb.user" : "flink",
        "mongodb.password" : "flinkpw",
        "database.include.list" : "inventory",
        "schema.history.internal.kafka.bootstrap.servers" : "kafka-0:9092,kafka-1:9092,kafka-2:9092",
        "transforms": "route",
        "transforms.route.type" : "org.apache.kafka.connect.transforms.RegexRouter",
        "transforms.route.regex" : "([^.]+)\\.([^.]+)\\.([^.]+)",
        "transforms.route.replacement" : "$3"
    }'
```

This ok, but reveal the password!!! (can solve this problem)
```shell
curl -i -X PUT -H  "Content-Type:application/json" \
    http://localhost:8083/connectors/mongo-kafka-source-01/config \
    -d '{
        "connector.class" : "com.mongodb.kafka.connect.MongoSourceConnector",
        "connection.uri": "mongodb://flink:flinkpw@mongo1:27017/?replicaSet=rs0",
        "topic.prefix": "tripsdata",
        "database": "inventory",
        "collection": "trips",
        "copy.existing": "true"
    }'
```

# Connect PostgreSQL (example)
Require: `wal_level=logical`

Basic command with pre-created table:
```
psql -U "${POSTGRES_USER}" "${POSTGRES_DB}" -c "CREATE TABLE conditions (time TIMESTAMPTZ NOT NULL, location TEXT NOT NULL, temperature DOUBLE PRECISION NULL, humidity DOUBLE PRECISION NULL); SELECT create_hypertable('conditions', 'time'); INSERT INTO conditions VALUES(NOW(), 'Prague', 22.8,  53.3); CREATE PUBLICATION dbz_publication FOR ALL TABLES WITH (publish = 'insert, update')"
```

Add connector:
```
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-timescaledb.json
```

register-timescaledb.json:
```
{
    "name": "inventory-connector",
    "config": {
        "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
        "tasks.max": "1",
        "database.hostname": "timescaledb",
        "database.port": "5432",
        "database.user": "postgres",
        "database.password": "postgres",
        "database.dbname": "postgres",
        "plugin.name": "pgoutput",
        "publication.name": "dbz_publication",
        "slot.name" : "debezium",
        "topic.prefix": "dbserver1",
        "schema.include.list": "_timescaledb_internal",
        "transforms": "timescaledb",
        "transforms.timescaledb.type": "io.debezium.connector.postgresql.transforms.timescaledb.TimescaleDb",
        "transforms.timescaledb.database.hostname": "timescaledb",
        "transforms.timescaledb.database.port": "5432",
        "transforms.timescaledb.database.user": "postgres",
        "transforms.timescaledb.database.password": "postgres",
        "transforms.timescaledb.database.dbname": "postgres"
    }
}
```

# connector Timescaledb
add data:
```bash
cd ./init_data/pypostgres
python handle_production_json.py
```
```bash
cd ./connector
curl -i -X POST -H "Accept:application/json" -H  "Content-Type:application/json" http://localhost:8083/connectors/ -d @register-timescaledb_hadoop.json
```

# kafka -> spark -> parquet
```bash
docker exec spark-master-1 spark-submit --master spark://spark-master-1:17077 --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0 /opt/bitnami/spark/work/read_stream_timescaledb.py
```

# parquet -> spark -> postgres_datamart
```bash
docker exec spark-master-2 spark-submit --master spark://spark-master-2:27077 --packages org.apache.spark:spark-streaming-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.spark:spark-avro_2.12:3.5.0,org.postgresql:postgresql:42.7.0 /opt/bitnami/spark/work/read_parquet_hdfs_to_postgre.py
```

get address postgres_datamart
```bash
bash hadoop_setup/get_address.sh bigdata_draft1_default
```

<!-- # Quick start Hive
## Copy csv to HDFS
Copy breweries.csv to the namenode.
```
docker cp spark_submits/breweries.csv namenode:breweries.csv
```
Go to the bash shell on the namenode with that same Container ID of the namenode.
```
docker exec -it namenode bash
```
Create a HDFS directory /data/openbeer/breweries.
```
hdfs dfs -mkdir -p /data/openbeer/breweries
```
Copy breweries.csv to HDFS:
```
hdfs dfs -put /breweries.csv /data/openbeer/breweries/breweries.csv
```

## Start spark-submit
Go to the command line of the Spark master and start spark-submit.
```
docker exec -it spark-master-1 bash
```
```
spark-submit --master spark://spark-master-1:17077 /opt/bitnami/spark/work/read_csv.py 
```

## Quick Start Hive
Go to the command line of the Hive server and start hiveserver2
```
docker exec -it hive-server bash

hiveserver2
```
Maybe a little check that something is listening on port 10000 now
```
netstat -anp | grep 10000
```
Okay. Beeline is the command line interface with Hive. Let's connect to hiveserver2 now.
```
beeline -u jdbc:hive2://localhost:10000 -n root

!connect jdbc:hive2://127.0.0.1:10000 scott tiger
```
Not a lot of databases here yet by showing the databases.
```
show databases;
```
Let's change that.
```
create database openbeer;

use openbeer;
```
And let's create a table.
```
CREATE EXTERNAL TABLE IF NOT EXISTS breweries(
    NUM INT,
    NAME CHAR(100),
    CITY CHAR(100),
    STATE CHAR(100),
    ID INT )
ROW FORMAT DELIMITED
FIELDS TERMINATED BY ','
STORED AS TEXTFILE
location '/data/openbeer/breweries';
```
And have a little select statement going.
```
select name from breweries limit 10;
```
=> There you go: your private Hive server to play with. -->

