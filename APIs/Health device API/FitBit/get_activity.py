import requests
import json
import pandas as pd

def get_activity(client_name):
    stop_loop = False
    while True:
        with open(f'access_refresh_tokens_{client_name}.json', 'r') as json_file:
            data = json.load(json_file)
            access_token = data['access_token']
            refresh_token = data['refresh_token']
            user_id = data['user_id']

        url = f"https://api.fitbit.com/1/user/{user_id}/activities/list.json"

        params = {
            'afterDate': '2024-01-19',
            'sort': 'asc',
            'limit': 100,
            'offset': 0
        }

        headers = {
            "Authorization": f'Bearer {access_token}'
        }

        response = requests.get(url, params=params, headers=headers).json()

        # for i in response['activities']:
        #     print(i)
        #     print('---------------------')
        #     print('---------------------')
        activity_entries = []

        for entry in response['activities']:
            activity_data = {
            'activeDuration': entry.get('activeDuration'),
            'activity_type': entry.get('activityName'),
            'activity_id': entry.get('activityTypeId'),
            'avg_hr': entry.get('averageHeartRate'),
            'calorie_burn': entry.get('calories'),
            'duration': entry.get('duration'),
            'original_duration': entry.get('originalDuration'),
            'start_time': entry.get('startTime'),
            'steps': entry.get('steps'),
            'total_minutes_for_activity': entry.get('activeZoneMinutes',{}).get('totalMinutes',{})
            }

            activity_entries.append(activity_data)

        activity_types = []

        for entry in response['activities']:
            for i in entry['activityLevel']:
                data = {
                "activity_type" : i.get('name'),
                "minutes": i.get('minutes'),
                "log_Id": entry['logId']
                }
                activity_types.append(data)

        heart_rate_zones = []

        for entry in response['activities']:
            for i in entry['heartRateZones']:
                data = {
                "caloriesOut" : i.get('caloriesOut'),
                "max": i.get('max'),
                "min": i.get('min'),
                "minutes":i.get('minutes'),
                "name" : i.get('name'),
                "log_Id": entry.get('logId')
                }
                heart_rate_zones.append(data)            

        df_activity_entries = pd.DataFrame(activity_entries)
        df_activity_types = pd.DataFrame(activity_types)
        df_hr_zones = pd.DataFrame(heart_rate_zones)

        print(df_activity_entries)
        print('----------------------')
        print(df_activity_types)
        print('----------------------')
        print(df_hr_zones)

        df_activity_entries.to_csv(f"{client_name}_activity_entries.csv")
        df_activity_types.to_csv(f"{client_name}_activity_types.csv")
        df_hr_zones.to_csv(f"{client_name}_hr_zones.csv")





        break

get_activity("Whitney")