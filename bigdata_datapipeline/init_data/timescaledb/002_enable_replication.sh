#!/bin/bash

echo "wal_level=logical" >> ${POSTGRESQL_CONF_DIR}/postgresql.conf

psql -U "${POSTGRES_USER}" "${POSTGRES_DB}" -c "CREATE TABLE conditions (time TIMESTAMPTZ NOT NULL, location TEXT NOT NULL, temperature DOUBLE PRECISION NULL, humidity DOUBLE PRECISION NULL); SELECT create_hypertable('conditions', 'time'); INSERT INTO conditions VALUES(NOW(), 'Prague', 22.8,  53.3); CREATE PUBLICATION dbz_publication FOR ALL TABLES WITH (publish = 'insert, update');" 

psql -U "${POSTGRES_USER}" "${POSTGRES_DB}" -c "create database homecamera;"

psql -U "${POSTGRES_USER}" homecamera -c "CREATE USER hadoop_user WITH PASSWORD 'hadoop124\$@!' REPLICATION; GRANT CONNECT ON DATABASE homecamera TO hadoop_user; CREATE SCHEMA IF NOT EXISTS data; SET search_path TO data; CREATE TABLE pricing ( order_id VARCHAR, transaction_id VARCHAR, account_id VARCHAR, phone_number VARCHAR, purchase_date_time TIMESTAMPTZ, start_date_time TIMESTAMPTZ, end_date_time TIMESTAMPTZ, payment_method VARCHAR, price INTEGER, package_type VARCHAR, package_id VARCHAR, camera_sn VARCHAR, service VARCHAR, info_service_en VARCHAR, info_service_noteEn VARCHAR, info_service_noteVi VARCHAR, info_service_vi VARCHAR, service_status INTEGER ); SET search_path TO public; select create_hypertable('data.pricing', 'purchase_date_time', migrate_data => true); CREATE PUBLICATION hadoop_publication FOR TABLE data.pricing WITH (publish = 'insert, update'); GRANT USAGE ON SCHEMA data to hadoop_user; GRANT SELECT ON TABLE data.pricing TO hadoop_user; GRANT USAGE ON SCHEMA _timescaledb_internal TO hadoop_user; GRANT SELECT ON ALL TABLES IN SCHEMA _timescaledb_internal TO hadoop_user;"
