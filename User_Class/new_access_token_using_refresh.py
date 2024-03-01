import requests
from requests.auth import HTTPBasicAuth
import json

def new_access_refresh_tokens(client_name):

    with open(f'access_refresh_tokens_{client_name}.json', 'r') as json_file:
        data = json.load(json_file)

    access_token = data['access_token']
    refresh_token = data['refresh_token']
    user_id = data['user_id']

    client_id = "23RQZC"
    client_secret = "16d65560c4ba5c04a8a6d6aaf60fbadc"

    payload = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }

    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    url = f"https://api.fitbit.com/oauth2/token"
    auth= HTTPBasicAuth(client_id, client_secret)

    response = requests.post(url, auth=auth,data=payload, headers=headers).json()

    data = {
        "access_token" : response['access_token'],
        "refresh_token": response['refresh_token'],
        "user_id": response['user_id'],
        "client_name": client_name


    }

    with open(f'access_refresh_tokens_{client_name}.json', 'w') as json_file:
        json.dump(data, json_file)

