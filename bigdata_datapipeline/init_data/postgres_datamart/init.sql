-- init.sql
CREATE TABLE typeOfCar (
    id INTEGER,
    customer_id INTEGER,
    order_total_usd DOUBLE PRECISION,
    make VARCHAR(255),
    model VARCHAR(255),
    delivery_city VARCHAR(255),
    delivery_company VARCHAR(255),
    delivery_address VARCHAR(255),
    CREATE_TS TIMESTAMP,
    UPDATE_TS TIMESTAMP
);

CREATE TABLE pricing (
    order_id VARCHAR,
    transaction_id VARCHAR,
    account_id VARCHAR,
    phone_number VARCHAR,
    purchase_date_time TIMESTAMP,
    start_date_time TIMESTAMP,
    end_date_time TIMESTAMP,
    payment_method VARCHAR,
    price INTEGER,
    package_type VARCHAR,
    package_id VARCHAR,
    camera_sn VARCHAR,
    service VARCHAR,
    info_service_en VARCHAR,
    info_service_noteEn VARCHAR,
    info_service_noteVi VARCHAR,
    info_service_vi VARCHAR,
    service_status INTEGER
);