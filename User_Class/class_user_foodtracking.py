import requests
from datetime import datetime
import pandas as pd
import json
import base64
import hashlib
import os
from requests.auth import HTTPBasicAuth

class User:
    def __init__(self, name, id):

        self.name = name
        self.id = id


    def search_exercise(self,search_exercise):

        url = f'https://api.api-ninjas.com/v1/exercises'

        headers = {
            'X-Api-Key': 'p4CCOHW0yaZsa/wRWHHAyA==d7tJ0bJnkYVnEKoZ'
        }

        params = {

            'name': search_exercise
        }

        response = requests.get(url, headers=headers, params=params).json()



        choice = 1
        for i in response:
            print(f'[{choice}]', i['name'])
            choice += 1

        exercise_choice = int(input('choose exercise: '))

        print(response[exercise_choice - 1]['name'])

        return response[exercise_choice - 1]['name']




    def log_exercise(self, exercise):


        date = datetime.now()
        date = date.strftime('%Y-%m-%d')

        exercise = self.search_exercise(exercise)

        log = [exercise]
        set_num = 1
        while True:
            
            data = {
            f'set_{set_num}_weight' :input('weight: '),
            f'reps_{set_num}' :input('reps: ')

            }

            log.append(data)

            set_num +=1

            if input('stop, y or n') == 'y':

                log.append(date)
                break

        print(log)


    def get_request_token(self):
        code_verifier = base64.urlsafe_b64encode(os.urandom(64)).rstrip(b'=').decode('utf-8')
        sha256_of_verifier = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(sha256_of_verifier).rstrip(b'=').decode('utf-8')

        params = {
            "client_id": "23RQZC",
            "response_type": "code",
            "scope": "heartrate sleep weight respiratory_rate activity oxygen_saturation temperature",
            "redirect_uri": "https://localhost:3000/callback",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256"
        }

        # Construct the full URL with parameters
        from urllib.parse import urlencode
        full_url = f"https://www.fitbit.com/oauth2/authorize?{urlencode(params)}"

        # Output the URL
        print('Visit this URL in your web browser to authorize:', full_url)
        request_token = input("Paste Request Token: ")


        self.nutritionix_request_token = request_token
        self.nutritionix_code_verifier = code_verifier
        self.nutritionix_code_challenge = code_challenge


        return code_verifier, code_challenge, request_token
    
    def access_refresh_tokens_nutritionix(self):

        if not self.nutritionix_request_token or not self.nutritionix_code_verifier:
            print("Need request token and or code verifier")
            return None

        print('request token',self.nutritionix_request_token)
        print('code verifier',self.nutritionix_code_verifier)

        request_token = self.nutritionix_request_token
        code_verifier = self.nutritionix_code_verifier


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

        
        response = requests.post(url, auth=HTTPBasicAuth(client_id, client_secret), data=payload, headers=headers)

        if response.status_code == 200:
            print('Succesfull')

        else:
            print(response.status_code)
            print('Failed')
            return None
        
        response = response.json()

        self.access_token_nutritionix = response.get('access_token')
        self.refresh_token_nutritionix = response.get('refresh_token')
        self.user_id_nutritionix = response.get('user_id')

    def new_access_refresh_tokens(self):


        refresh_token = self.refresh_token_nutritionix
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

        self.refresh_token_nutritionix = response['refresh_token']
        self.access_token_nutritionix = response['access_token']








mark = User('Mark', '001')

mark.get_request_token()

mark.access_refresh_tokens_nutritionix()

print('access token',mark.access_token_nutritionix)
print('refresh token',mark.refresh_token_nutritionix)
