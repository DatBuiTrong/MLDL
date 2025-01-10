import requests
from pprint import pprint
from utils.config import connect_config


# init variables
BASE_URL = connect_config(filename='./config/authorization.ini', section='production_url')['url']
LOGIN_ACCOUNT = connect_config(filename='./config/authorization.ini', section='production_login')


# Function to perform login and retrieve the token
def get_auth_token():
    login_url = BASE_URL + '/login'
    login_payload = LOGIN_ACCOUNT
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


# # Get pricing
# if auth_token:
#     url = BASE_URL + '/pricing/payment/bill?limit=10&offset=0&user_id=Admin&order=1'
#     headers = {
#         'Authorization': f'Bearer {auth_token}'
#     }

#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         data = response.json()
#         print({data['data']['total']})
#         if data['code'] == 200:
#             # Access the relevant data
#             bill_data = data['data']['data']
#             # Process or print first 10 rows
#             for item in bill_data[:10]:
#                 pprint(item)
#                 # break
#         else:
#             print(f"Error: {data['msg']}")
#     else:
#         print(f"Error: {response.status_code}")
#         print(response.text)


# # Get users
# if auth_token:
#     # có thể bỏ thời gian!!!
#     url = BASE_URL + '/users?offset=0&limit=3400&expand=true&has_devices=true&get_attributes=true&start=1673142744&end=1704703944&project_id=912e5599-70e4-4d54-b14b-049a1efe889d'
#     headers = {
#         'Authorization': f'Bearer {auth_token}'
#     }

#     response = requests.get(url, headers=headers)

#     if response.status_code == 200:
#         data = response.json()
#         pprint(data['total'])
#         # pprint(len(data['users']['attributes']))
#         # Access the relevant data
#         bill_data = data['users']
#         # Process or print first 10 rows
#         for item in bill_data[:10]:
#             pprint(item)
#             # break
#     else:
#         print(f"Error: {response.status_code}")
#         print(response.text)


# get devices:
if auth_token:
    url = BASE_URL + '/devices/attributes'
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }

    data = {
        "type": "AND",
        "entity_type": "DEVICE",
        "queries": [
            {
                "value": "",
                "key": "type"
            }
        ],
        "sort": [],
        "project_id": "912e5599-70e4-4d54-b14b-049a1efe889d",
        "limit": 1,
        "offset": 0
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        json_data = response.json()
        pprint(json_data)
        # Serializing json
        # import json
        # json_object = json.dumps(json_data['devices'], indent=4)
        
        # # Writing to sample.json
        # with open("devices.json", "w") as outfile:
        #     outfile.write(json_object)

    else:
        print(f"Error: {response.status_code}")
        print(response.text)