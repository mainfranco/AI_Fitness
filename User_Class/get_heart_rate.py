from new_access_token_using_refresh import new_access_refresh_tokens
from datetime import datetime, timedelta
from new_access_token_using_refresh import new_access_refresh_tokens
import requests
import json

def get_heart_data(client_name):
# Get today's date
    today = datetime.today()

    # Calculate the date one week before today
    one_week_ago = today - timedelta(days=7)
    one_week_ago = one_week_ago.strftime('%Y-%m-%d')
    today = datetime.now()


    stop_loop = False
    while True:
        with open(f'access_refresh_tokens_{client_name}.json', 'r') as json_file:
            data = json.load(json_file)
            access_token = data['access_token']
            refresh_token = data['refresh_token']
            user_id = data['user_id']

        url = f"https://api.fitbit.com/1/user/{user_id}/activities/heart/date/{one_week_ago}/today.json"

        headers = {
            "Authorization": f'Bearer {access_token}'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print('Good request')
            return response.json()

        elif response.status_code == 401:  # Handle expired or invalid token
            print("Token might be expired, refreshing...")

            if stop_loop == True:
                print("Different issue")
                break
            new_access_refresh_tokens(client_name=client_name)
            stop_loop = True


response = get_heart_data('Whitney')

print(response['activities-heart'][0])