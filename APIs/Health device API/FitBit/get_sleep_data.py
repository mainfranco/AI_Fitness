import requests
import json
from new_access_token_using_refresh import new_access_refresh_tokens
import pandas as pd

def get_sleep_data(client_name):

    stop_loop = False
    while True:
        with open(f'access_refresh_tokens_{client_name}.json', 'r') as json_file:
            data = json.load(json_file)
            access_token = data['access_token']
            refresh_token = data['refresh_token']
            user_id = data['user_id']

        url = f"https://api.fitbit.com/1.2/user/{user_id}/sleep/list.json"
        params = {
            # 'beforeDate': None,  # Omit if not required or handled dynamically within the loop
            'afterDate': '2023-11-19',
            'sort': 'asc',
            'limit': 100,
            'offset': 0
        }
        headers = {
            "Authorization": f'Bearer {access_token}'
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            print('Good request')
            return response.json()
              # Exit the loop on success
        elif response.status_code == 401:  # Handle expired or invalid token
            print("Token might be expired, refreshing...")

            if stop_loop == True:
                print("Different problem")
                break
            new_access_refresh_tokens()
            stop_loop = True  


        else:
            print(f"Unhandled status code received: {response.status_code}")
            print("Response Content:", response.text)
            break  # Exit the loop on other errors

response = get_sleep_data("Whitney")

sleep_data_entries = []

# Loop through each sleep entry
for entry in response['sleep']:
    # Using `.get(key, default)` to avoid KeyError if key doesn't exist
    sleep_data = {
        "date": entry.get('dateOfSleep'),
        "duration_ms": entry.get('duration'),
        "efficiency": entry.get('efficiency'),
        "start_time": entry.get('startTime'),
        "end_time": entry.get('endTime'),
        "time_in_bed": entry.get('timeInBed'),
        "minutes_asleep": entry.get('minutesAsleep'),
        "minutesToFallAsleep": entry.get('minutesToFallAsleep'),
        "minutes_awake": entry.get('minutesAwake'),
        "log_id": entry.get('logId'),
        "info_code": entry.get('infoCode'),
        "IsMainSleep": entry.get('isMainSleep'),
        "deep_sleep_count": entry.get('levels', {}).get('summary', {}).get('deep', {}).get('count'),
        "deep_sleep_minutes": entry.get('levels', {}).get('summary', {}).get('deep', {}).get('minutes'),
        "deep_sleep_30dayAvgMin": entry.get('levels', {}).get('summary', {}).get('deep', {}).get('thirtyDayAvgMinutes'),
        "light_sleep_count": entry.get('levels', {}).get('summary', {}).get('light', {}).get('count'),
        "light_sleep_minutes": entry.get('levels', {}).get('summary', {}).get('light', {}).get('minutes'),
        "light_sleep_30dayAvgMin": entry.get('levels', {}).get('summary', {}).get('light', {}).get('thirtyDayAvgMinutes'),
        "rem_sleep_count": entry.get('levels', {}).get('summary', {}).get('rem', {}).get('count'),
        "rem_sleep_minutes": entry.get('levels', {}).get('summary', {}).get('rem', {}).get('minutes'),
        "rem_sleep_30dayAvgMin": entry.get('levels', {}).get('summary', {}).get('rem', {}).get('thirtyDayAvgMinutes'),
        "wake_count": entry.get('levels', {}).get('summary', {}).get('wake', {}).get('count'),
        "wake_minutes": entry.get('levels', {}).get('summary', {}).get('wake', {}).get('minutes'),
        "wake_30dayAvgMin": entry.get('levels', {}).get('summary', {}).get('wake', {}).get('thirtyDayAvgMinutes'),
    }
    sleep_data_entries.append(sleep_data)

# Create the DataFrame from the list of entries
df = pd.DataFrame(sleep_data_entries)

print(df)

df.to_csv("whitney_sleep_data_4.csv")


#These are the different sleep states throughout the night
# sleep_stages = response['sleep'][4]['levels']['data']




 

