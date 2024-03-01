import requests
from datetime import datetime, timedelta
import pandas as pd
import json
import base64
import hashlib
import os
from requests.auth import HTTPBasicAuth
import sqlite3
import pickle

class User:
    def __init__(self, name, id,db_path='fitness_app.db'):

        self.name = name
        self.id = id
        self.db_path = db_path
        self.new_sql_tables()
        self.save_to_db()



    def new_sql_tables(self):

        conn = sqlite3.connect(self.db_path) 
        cursor = conn.cursor()


        users_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT,
            data BLOB  -- Column for storing pickled User objects
        )'''

        create_food_log_query = f'''
        CREATE TABLE IF NOT EXISTS food_log_{self.id} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT NOT NULL,
            calories INTEGER,
            protein DECIMAL,
            carbs DECIMAL,
            fat DECIMAL,
            cholesterol DECIMAL,
            sodium DECIMAL,
            potassium DECIMAL,
            sugars DECIMAL,
            entry_date DATE,
            img TEXT,
            user_id TEXT
        )'''
        
        create_workout_log_query = f'''
        CREATE TABLE IF NOT EXISTS workout_log_{self.id} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            exercise_name TEXT,
            weight_set_1 DECIMAL,
            reps_set_1 DECIMAL,
            weight_set_2 DECIMAL,
            reps_set_2 DECIMAL,
            weight_set_3 DECIMAL,
            reps_set_3 DECIMAL,
            weight_set_4 DECIMAL,
            reps_set_4 DECIMAL,
            notes TEXT,
            user_id TEXT
        )''' 

        create_tokens_codes_log_query = f'''
        CREATE TABLE IF NOT EXISTS tokens_codes_log_{self.id} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_date TEXT NOT NULL,
            fitbit_request_token TEXT,
            fitbit_access_token TEXT,
            fitbit_refresh_token TEXT,
            user_id TEXT
        )'''

        # Execute the create table query
        cursor.execute(create_food_log_query)
        cursor.execute(create_workout_log_query)
        cursor.execute(create_tokens_codes_log_query)
        cursor.execute(users_query)
        
        # Commit the changes and close the connection
        conn.commit()
        conn.close()



    def save_to_db(self):

        pickled_user = pickle.dumps(self)

        # Connect to the SQLite database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Insert/Update the pickled User object into the users table
        cursor.execute('''
            INSERT INTO users (id, name, data) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET name = excluded.name, data = excluded.data
        ''', (self.id, self.name, pickled_user))

        # Commit the changes and close the connection
        conn.commit()
        conn.close()




    # EXERCISE LOGGER METHODS

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




    #FITBIT FITNESS WATCH METHODS

    def get_request_token_fitbit(self):
        date = datetime.now()
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


        self.fitbit_request_token = request_token
        self.fitbit_code_verifier = code_verifier
        self.fitbit_code_challenge = code_challenge

        # Saves the object to db with its new attributes
        self.save_to_db()


        print('code_verifier, code_challenge and request token saved succesfully')


    
    def access_refresh_tokens_fitbit(self):
        # Check if either attribute does not exist
        if not hasattr(self, 'fitbit_request_token') or not hasattr(self, 'fitbit_code_verifier'):
            print("Need request token and or code verifier")
            return None


        request_token = self.fitbit_request_token
        code_verifier = self.fitbit_code_verifier


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
            print(response.json())
            print('Failed')
            return None
        
        response = response.json()

        self.access_token_fitbit = response.get('access_token')
        self.refresh_token_fitbit = response.get('refresh_token')
        self.user_id_fitbit = response.get('user_id')

        # Saves the object to db with its new attributes
        self.save_to_db()       




    def new_access_refresh_tokens_fitbit(self):


        refresh_token = self.refresh_token_fitbit
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

        self.refresh_token_fitbit = response['refresh_token']
        self.access_token_fitbit = response['access_token']

        # Saves the object to db with its new attributes
        self.save_to_db()



    def get_sleep_data(self, after_date, amount=100):

        stop_loop = False
        while True:

            access_token = self.access_token_fitbit
            user_id = self.user_id_fitbit

            url = f"https://api.fitbit.com/1.2/user/{user_id}/sleep/list.json"
            params = {
                # 'beforeDate': None,  # Omit if not required or handled dynamically within the loop
                'afterDate': after_date,
                'sort': 'asc',
                'limit': amount,
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

                #This updates access and refresh tokens
                self.new_access_refresh_tokens_fitbit()
                stop_loop = True  


            else:
                print(f"Unhandled status code received: {response.status_code}")
                print("Response Content:", response.text)
                break  # Exit the loop on other errors

        response = response.json()

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

            print(sleep_data)  

    def get_heart_data(self):
    # Get today's date
        today = datetime.today()

        # Calculate the date one week before today
        one_week_ago = today - timedelta(days=7)
        one_week_ago = one_week_ago.strftime('%Y-%m-%d')
        today = datetime.now()


        stop_loop = False
        while True:
            
            access_token = self.access_token_fitbit
            user_id = self.user_id_fitbit

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
                self.new_access_refresh_tokens_fitbit()
                stop_loop = True


        response = response.json()

        print(response['activities-heart'][0])    


    def get_activity(self, after_date,amount=100):
        stop_loop = False
        while True:

            access_token = self.access_token_fitbit
            user_id = self.user_id_fitbit

            url = f"https://api.fitbit.com/1/user/{user_id}/activities/list.json"

            params = {
                'afterDate': after_date,
                'sort': 'asc',
                'limit': amount,
                'offset': 0
            }

            headers = {
                "Authorization": f'Bearer {access_token}'
            }

            response = requests.get(url, params=params, headers=headers).json()

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
                'total_minutes_for_activity': entry.get('activeZoneMinutes',{}).get('totalMinutes',{}),
                'logId':entry.get('logId')
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

            break 






        
    #NUTRITONIX FOOD DATABASE METHODS

    def get_item_options(self,food_item):

        url = 'https://trackapi.nutritionix.com/v2/search/instant'

        params = {
            'query': food_item
        }

        headers = {
            'x-app-id': 'bc4373cf',
            'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4'
        }
        while True:
            try:
                params = {'query': food_item}
                response = requests.get(url, params, headers=headers).json()

                
                if any(response[key] for key in response):
                    break


            except requests.exceptions.RequestException as e:
                print('Error making request:', e)
            except Exception as e:
                print('An unexpected error occurred:', e)

            print('No options found. Please try another search.')
            food_item = input('Search food: ')


        items = []  # List to hold the food items
        for entry in response['branded'][:10]:
            item_details = {
                'food_name': entry['brand_name_item_name'],
                'tag_id': entry['nix_item_id'],
                'serving_unit': entry['serving_unit'],
                'serving_qty': entry['serving_qty'],
                'calories': entry['nf_calories'],
                'brand': True
            }
            items.append(item_details)
        for entry in response['common'][:10]:

            item_details = {
                'food_name': entry['food_name'],
                'tag_id': entry['tag_id'],
                'serving_unit': entry['serving_unit'],
                'serving_qty': entry['serving_qty'],
                'calories': None,
                'brand' : False
                
            }
            items.append(item_details)


        count = 1
        for i in items:
            name = i['food_name']
            tag_id = i['tag_id']
            serving_unit = i['serving_unit']
            serving_quantity = round(i['serving_qty'],2)
            calories = i['calories']

            print(f'option: {count}')
            print(name)
            print('tag id:',tag_id)
            print('serving unit:',serving_unit)
            print('serving quantity:',serving_quantity)
            print('calories per serving:', calories)
            print('-----------------------')
            print('-----------------------')
            count += 1

        while True:
            try:
                choice = input('Choice #: or press q to exit ')
                print('----------------------------')
                print('----------------------------')
                if choice == 'q' or choice == 'Q':
                    print("Quit program")
                    return
                
                if choice.isdigit():
                    choice = int(choice)
                    food_choice = (items[choice - 1]['food_name'], items[choice - 1]['tag_id'], items[choice - 1]['brand'])
                    break
                elif choice == 'q' or choice == 'Q':
                    food_choice = ("Empty", "Exit Program", "HIII")
                    break


                        
                
            except ValueError:
                print("Input an integer from 1-20")
            except IndexError:
                print("Please choose a number within the valid range.")


        # Returns the name of the food if not a brand name   
        if food_choice[2] == False:
            return (food_choice[0])
        
        # Returns the brand_id if its a brand name and a True statement that can be parsed later on
        elif food_choice[2] == True:
            return (food_choice[1], True)


    def get_nutrition(self,food_item):
        headers = {
            'x-app-id': 'bc4373cf',
            'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4',
        }

        if isinstance(food_item, tuple):

            url = 'https://trackapi.nutritionix.com/v2/search/item'
            response = requests.get(url, headers=headers, params={'nix_item_id': food_item[0]}).json()
            

        else:

            url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
            data = {'query': food_item}
            response = requests.post(url, headers=headers, json=data).json()
            
        nutrition_details = {
                
            'food_name': response['foods'][0]['food_name'],
            'serving_quantity': response['foods'][0]['serving_qty'],
            'serving_unit': response['foods'][0]['serving_unit'],
            'serving_weight_grams': response['foods'][0]['serving_weight_grams'],
            'calories': response['foods'][0]['nf_calories'],
            'fat': response['foods'][0]['nf_total_fat'],
            'carbs': response['foods'][0]['nf_total_carbohydrate'],
            'protein': response['foods'][0]['nf_protein'],
            'cholesterol': response['foods'][0]['nf_cholesterol'],
            'sodium': response['foods'][0]['nf_sodium'],
            'sugars': response['foods'][0]['nf_sugars'],
            'potassium': response['foods'][0]['nf_potassium'],
            'brand': response['foods'][0]['nix_brand_name'],
            'date' : str(datetime.now()),
            'photo': response['foods'][0]['photo']['thumb']}

        for i in nutrition_details:
            if nutrition_details[i] is None:
                nutrition_details[i] = 0
        


        return nutrition_details


    def log_food_entry(self,query):
        if query == 'q' or query == "Q":
            print("Quit program")
            return 
        else:
            pass

        more_food = True
        while more_food:

            food_choice = self.get_item_options(query)
            if food_choice is None:
                break
            nutrition = self.get_nutrition(food_choice)


            while True:

                try:
                
                    print("Your selection: ", nutrition['food_name'])
                    print("Calories: ", nutrition['calories'])
                    print("Protein: ", nutrition['protein'])
                    print("Carbs: ", nutrition['carbs'])
                    print("Fats: ", nutrition['fat'])
                    print("Serving grams: ", nutrition['serving_weight_grams'])
                    print("Serving unit: ", nutrition['serving_unit'])
                    print('------------------------------')
                    print('------------------------------')

                    quantity = input("1 for grams | 2 for serving units:  ")
                    if quantity == 'q' or quantity == 'Q':
                        print("Quit program")
                        return
                    
                    if quantity not in ["1", "2"]:  # Check if the input is not "1" or "2"
                        raise ValueError("Invalid choice")

                    if quantity == "1" and nutrition['serving_weight_grams'] != 0:
                        grams = float(input(f'How many grams?: '))
                        serving_weight_grams = nutrition['serving_weight_grams']
                        servings = grams / serving_weight_grams

                        entry_log = {}
                        entry_log['food_name'] = nutrition['food_name']
                        entry_log['entry_date'] = nutrition['date']
                        entry_log['img'] = nutrition['photo']

                        # replacing None values with 0
                        for i in nutrition.keys():
                            if nutrition[i] == None:
                                nutrition[i] = float(0)
                        
                        # total_calories = servings * calories
                        for i in ['calories','fat','carbs','protein','cholesterol','sodium','sugars','potassium']:
                            entry_log[i] = round(servings * nutrition[i],2)
                        break
                                    
                                    
                    elif quantity == "2" or (quantity == "1" and nutrition['serving_weight_grams'] == 0):
                        entry_log = {}
                        entry_log['food_name'] = nutrition['food_name']
                        entry_log['entry_date'] = nutrition['date']
                        entry_log['img'] = nutrition['photo']
                        
                        if nutrition['serving_weight_grams'] == 0:
                            print('serving grams not available. Use servings')

                        print(f"1 Serving is {nutrition['serving_quantity']}: {nutrition['serving_unit']}")
                        while True:
                            try:
                                serving_amount = float(input("How many servings?: "))
                            
                                break
                            except ValueError:
                                print("You must enter a number for the serving amount.")

                                
                    
                        for i in ['calories','fat','carbs','protein','cholesterol','sodium','sugars','potassium']:
                            entry_log[i] = round(serving_amount * nutrition[i], 2)


                    break
                
                except ValueError as e:
                    print("please enter an integer. Error: ", e)
            print('-----------------------')
            print('-----------------------')
            



        
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                
                
                cursor.execute(f'''INSERT INTO food_log_{self.id} (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, entry_date, img, user_id) 
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                            (entry_log['food_name'],
                            entry_log['calories'],
                            entry_log['protein'],
                            entry_log['carbs'],
                            entry_log['fat'],
                            entry_log['cholesterol'],
                            entry_log['sodium'],
                            entry_log['potassium'],
                            entry_log['sugars'],
                            entry_log['entry_date'],
                            entry_log['img'],
                            self.id))


                                      
                print('Entry Log')
                print('-------------------------')
                for key, value in entry_log.items():
                    print(f"{key}: {value}")
                print('-------------------------')
                print('Food logged successfully')
                print('-------------------------')

                
            while True:
                keep_going = input('Do you want to log another item: Y or N: ').upper().strip()
                
                if keep_going == 'Y':
                    query = input('Search Food: ')
                    break  # Break out of the loop if the user wants to continue
                
                elif keep_going == 'N':
                    more_food = False
                    break  # Break out of the loop if the user does not want to continue
                
                else:
                    print("Invalid input. Please enter 'Y' for yes or 'N' for no.")
        print("exited program")



    # PULLING DATA

    def pull_data(self, table):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Query the database for all entries in food_logs
        cursor.execute(f'SELECT * FROM {table}')

        # Fetch all rows from the query
        rows = cursor.fetchall()

        # Iterate over the rows and print them
        for row in rows:
            print(row)

        # Close the connection
        conn.close()