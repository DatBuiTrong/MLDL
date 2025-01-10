import requests
import psycopg2
from utils.config import connect_config
from datetime import datetime, timezone, timedelta
from tqdm import tqdm
import json


# Function to insert data into PostgreSQL
def insert_data_into_postgres(data):
    # read connection parameters
    param = connect_config(filename='./config/authorization.ini', section='postgresql')

    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**param)
    print('Connect OK!')

    # create a cursor
    cursor = conn.cursor()

    # Set timezone to GMT+7
    gmt7_timezone = timezone(timedelta(hours=7))

    print('Adding data ...')
    for item in tqdm(data):
        # convert info_service from string to json
        item['info_service'] = json.loads(item['info_service'])

        # Assuming you have a table named pricing with corresponding columns
        query = """
            INSERT INTO data.pricing (
                order_id, transaction_id, account_id, phone_number, purchase_date_time, 
                start_date_time, end_date_time, payment_method, price, package_type,
                package_id, camera_sn, service,
                info_service_en, info_service_noteEn, info_service_noteVi, info_service_vi,
                service_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        # Convert timestamp seconds to datetime and set timezone to GMT+7
        purchase_date_time = datetime.fromtimestamp(int(item['purchase_date_time']), tz=gmt7_timezone)
        start_date_time = datetime.fromtimestamp(int(item['start_date_time']), tz=gmt7_timezone)
        end_date_time = datetime.fromtimestamp(int(item['end_date_time']), tz=gmt7_timezone)

        # bỏ money_source, merchant, invitation_code, user_id
        if item['price'] == 'null':
            item['price'] = None

        values = (
            item['order_id'], item['transaction_id'], item['account_id'], item['phone_number'],
            purchase_date_time, start_date_time, end_date_time,
            item['payment_method'], item['price'], item['package_type'],
            item['package_id'], item['camera_sn'], item['service'],
            item['info_service']['en'], item['info_service']['noteEn'],
            item['info_service']['noteVi'], item['info_service']['vi'],
            item['service_status']
        )
        cursor.execute(query, values)

    conn.commit()
    cursor.close()
    conn.close()

# read json data from file
with open('./json_data/payments.json', 'r') as f:
    data = json.load(f)

insert_data_into_postgres(data)
