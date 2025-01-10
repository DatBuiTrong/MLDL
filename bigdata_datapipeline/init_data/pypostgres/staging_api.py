import requests
from pprint import pprint
from utils.config import connect_config

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
            bill_data = data['data']['data']

            # Process or print first 10 rows
            for item in bill_data[:10]:
                pprint(item)
                # break
        else:
            print(f"Error: {data['msg']}")
    else:
        print(f"Error: {response.status_code}")
