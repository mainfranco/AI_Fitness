import requests
from requests.auth import HTTPBasicAuth
from get_request_token import get_request_token
import json

def access_refresh_tokens(client_name):
    with open(f'request_token_{client_name}.json', 'r') as json_file:
        data = json.load(json_file)

    request_token = data["request_token"]
    code_verifier = data["code_verifier"]


    client_id = "23RQZC"
    client_secret = "16d65560c4ba5c04a8a6d6aaf60fbadc"
    url = "https://api.fitbit.com/oauth2/token"

    payload = {
        'code': request_token,
        "code_verifier": code_verifier,
        'grant_type': 'authorization_code',
        'redirect_uri': 'https://localhost:3000/callback'
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    # Make the POST request with Basic Auth
    response = requests.post(url, auth=HTTPBasicAuth(client_id, client_secret), data=payload, headers=headers).json()
    # Assuming the response is in JSON format and contains access_token and refresh_token
    data = {
    "access_token" : response.get('access_token'),
    "refresh_token" : response.get('refresh_token'),
    "user_id" : response.get('user_id'),
    "client_name": client_name
    }


    with open(f'access_refresh_tokens_{client_name}.json', 'w') as json_file:
        json.dump(data, json_file) 


access_refresh_tokens('Mark')

