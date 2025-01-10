rm -rf app_data/hadoop_*

rm -rf app_data/kafka_*

rm -rf app_data/superset_*

rm -rf app_data/nifi

rm -rf app_data/postgres*

rm -rf app_data/mongo*

docker volume prune -af
