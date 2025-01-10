import requests
import psycopg2
from utils.config import connect_config
from datetime import datetime
from tqdm import tqdm

# Function to perform login and retrieve the token
def get_auth_token():
    login_url = 'https://stg-iotapi.viettel.io/api/login'
    login_payload = connect_config(filename='./config/authorization.ini', section='staging_apis')
    login_headers = {'Content-Type': 'application/json'}

    login_response = requests.post(login_url, json=login_payload, headers=login_headers)

    if login_response.status_code == 200:
        login_data = login_response.json()
        return login_data.get('token')
    else:
        print(f"Login Error: {login_response.status_code}")
        return None

# Function to insert data into PostgreSQL
def insert_data_into_postgres(data):
    # read connection parameters
    param = connect_config(filename='./config/authorization.ini', section='postgresql')

    # connect to the PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**param)

    # create a cursor
    cursor = conn.cursor()
    
    print('Adding data ...')
    for item in tqdm(data):
        # Assuming you have a table named payment with corresponding columns
        query = """
            INSERT INTO data.pricing (
                order_id, transaction_id, account_id, phone_number, purchase_date_time, 
                start_date_time, end_date_time, payment_method, price, package_type,
                package_id, camera_sn, service, money_source, merchant, invitation_code,
                user_id, info_service_en, info_service_noteEn, info_service_noteVi, info_service_vi,
                service_status
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            values = (
                item['order_id'], item['transaction_id'], item['account_id'], item['phone_number'],
                datetime.fromtimestamp(item['purchase_date_time']), datetime.fromtimestamp(item['start_date_time']), datetime.fromtimestamp(item['end_date_time']),
                item['payment_method'], item['price'], item['package_type'],
                item['package_id'], item['camera_sn'], item['service'], item['money_source'],
                item['merchant'], item['invitation_code'], item['user_id'],
                item['info_service']['en'], item['info_service']['noteEn'],
                item['info_service']['noteVi'], item['info_service']['vi'],
                item['service_status']
            )
        except:
            values = (
                item['order_id'], item['transaction_id'], item['account_id'], item['phone_number'],
                datetime.fromtimestamp(item['purchase_date_time']), datetime.fromtimestamp(item['start_date_time']), datetime.fromtimestamp(item['end_date_time']),
                item['payment_method'], item['price'], item['package_type'],
                item['package_id'], item['camera_sn'], item['service'], item['money_source'],
                item['merchant'], item['invitation_code'], item['user_id'],
                None, None, None, None,
                item['service_status']
            )
        cursor.execute(query, values)

    conn.commit()
    cursor.close()
    conn.close()

# Get the token
auth_token = get_auth_token()

if auth_token:
    url = 'https://stg-iotapi.viettel.io/api/pricing/payment/bill?limit=2000&offset=0&user_id=Admin&order=1'
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data['code'] == 200:
            # Access the relevant data
            total = data['data']['total']
            print(f'Total: {total}')
            pricing_data = data['data']['data']
            # pricing_data = pricing_data[:1]

            # # Process or print the data as needed
            # for item in pricing_data:
            #     pprint(item)

            insert_data_into_postgres(pricing_data)

        else:
            print(f"Error: {data['msg']}")
    else:
        print(f"Error: {response.status_code}")
