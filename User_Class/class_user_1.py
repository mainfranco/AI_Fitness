import requests
from datetime import datetime, timedelta
import pandas as pd
import json
import base64
import hashlib
import os
from requests.auth import HTTPBasicAuth
import sqlite3
from dotenv import load_dotenv



class User:

    load_dotenv(dotenv_path='secrets.env')
    fitbit_client_secret = os.getenv('CLIENT_SECRET_FITBIT')
    ninjas_api = os.getenv('API_NINJAS_KEY')
    fitbit_client_id = os.getenv('CLIENT_ID_FITBIT')

    nutritionix_api = os.getenv('NUTRITIONIX_API')
    nutritionix_app_id = os.getenv('NUTRITIONIX_APP_ID')

    database_path = os.getenv('fitness_app.db')

    
    def __init__(self, name, user_id=None):  # Add user_id as an optional parameter
        self.name = name
        self.db_path = 'fitness_app.db'
        self.id = user_id  # Set id to the provided user_id if it's not None

        if user_id is None:  # Only insert into the DB if user_id wasn't provided
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO users (name) VALUES (?)
                ''', (self.name,))
                self.id = cursor.lastrowid
                conn.commit()

    @classmethod
    def login(cls, name):
        db_path = 'fitness_app.db'
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id FROM users WHERE name = ?
            ''', (name,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
                return cls(name=name, user_id=user_id)  # Now this line should work
            else:
                print("User not found.")
                return None



    def save_to_db(self, table):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO {table} (name) VALUES (?)
            ''', (self.name,))
            self.id = cursor.lastrowid

        # Commit the changes and close the connection
        conn.commit()
        conn.close()




    # EXERCISE LOGGER METHODS

    def search_exercise(self,search_exercise):

        url = f'https://api.api-ninjas.com/v1/exercises'

        headers = {
            'X-Api-Key': self.ninjas_api
        }

        params = {

            'name': search_exercise
        }

        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print('Good Request')

        elif response.status_code == 401:
            print('Authorization Problem')
            return None
        
        elif response.status_code == 400:
            print('Bad Request')
            return None

        response = response.json()
        choice = 1
        for i in response:
            print(f'[{choice}]', i['name'])
            choice += 1

        exercise_choice = int(input('choose exercise: '))

        print(response[exercise_choice - 1]['name'])
        return response[exercise_choice - 1]['name']




    def log_exercise(self, exercise_name):

        date = datetime.now().strftime('%Y-%m-%d')
        exercise = self.search_exercise(exercise_name)
        
        notes = 'Your notes here' 
        user_id = self.id 

        # Insert the exercise into the exercises table
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert the exercise record and get its ID
            cursor.execute(f'''INSERT INTO exercises (date, exercise_name, notes, user_id) 
                            VALUES (?, ?, ?, ?)''', (date, exercise, notes, user_id))
            exercise_id = cursor.lastrowid  # Retrieve the ID of the newly inserted exercise
            
            # Prompt the user for set details and insert each set into the exercise_sets table
            while True:
                weight = input('Weight for the set (lbs): ')
                reps = input('Reps: ')
                
                cursor.execute(f'''INSERT INTO exercise_sets (exercise_id, weight, reps, user_id) 
                                VALUES (?, ?, ?, ?)''', (exercise_id, weight, reps, self.id))
                
                if input('Add another set? (y/n): ').lower() == 'n':
                    break
        
        conn.commit()  # Commit outside the loop
        print('Exercise logged successfully.')






    #FITBIT FITNESS WATCH METHODS

    def get_request_token_fitbit(self):
        date = datetime.now()
        code_verifier = base64.urlsafe_b64encode(os.urandom(64)).rstrip(b'=').decode('utf-8')
        sha256_of_verifier = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        code_challenge = base64.urlsafe_b64encode(sha256_of_verifier).rstrip(b'=').decode('utf-8')

        params = {
            "client_id": self.fitbit_client_id,
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


        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO request_tokens_fitbit (user_id, date, fitbit_request_token, fitbit_code_verifier, fitbit_code_challenge) 
                            VALUES (?, ?, ?, ?, ?)''', (self.id, date, request_token, code_verifier, code_challenge))


        print('code_verifier, code_challenge and request token saved succesfully')


    
    def access_refresh_tokens_fitbit(self):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT fitbit_request_token 
                            FROM request_tokens_fitbit 
                            WHERE user_id = ? 
                            ORDER BY date DESC
                            LIMIT 1''', (self.id,))  # Note the comma to make it a tuple
            
            result = cursor.fetchone()
            request_token = result[0] if result else None  # Check if result is not None

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT fitbit_code_verifier 
                            FROM request_tokens_fitbit 
                            WHERE user_id = ? 
                            ORDER BY date DESC
                            LIMIT 1''', (self.id,))  # Note the comma to make it a tuple
            
            result = cursor.fetchone()
            code_verifier = result[0] if result else None  # Check if result is not None




        client_id = self.fitbit_client_id
        client_secret = self.fitbit_client_secret
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
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f'''INSERT INTO tokens_codes_log (last_date, fitbit_access_token, fitbit_refresh_token, fitbit_user_id, user_id) 
                            VALUES (?, ?, ?, ?, ?)''',
                        (datetime.now(),
                            response.get('access_token'),
                            response.get('refresh_token'),
                            response.get('user_id'),
                            self.id,))

    


    def new_access_refresh_tokens_fitbit(self):
        # Connect to the SQLite database
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query to select the most recent refresh_token for the user
            cursor.execute('''
                SELECT fitbit_refresh_token FROM tokens_codes_log 
                WHERE user_id = ? 
                ORDER BY last_date DESC 
                LIMIT 1
            ''', (self.id,))
            
            # Fetch the result
            result = cursor.fetchone()
            
            # If there's a result, update the refresh_token, otherwise, handle the absence
            if result:
                refresh_token = result[0]
            else:
                print("No existing tokens found for user.")
                return
        client_id = self.fitbit_client_id
        client_secret = self.fitbit_client_secret

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

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(f'''INSERT INTO tokens_codes_log (last_date, fitbit_access_token, fitbit_refresh_token, fitbit_user_id, user_id) 
                        VALUES (?, ?, ?, ?, ?)''',
                    (datetime.now(),
                    response.get('access_token'),
                    response.get('refresh_token'),
                    response.get('user_id'),
                    self.id,)) 



    def get_sleep_data(self, after_date, amount=100):

        stop_loop = False
        fitbit_user_id, fitbit_access_token = self.pull_fitbit_access_and_userid()

        while True:

            url = f"https://api.fitbit.com/1.2/user/{fitbit_user_id}/sleep/list.json"
            params = {
                # 'beforeDate': None,  # Omit if not required or handled dynamically within the loop
                'afterDate': after_date,
                'sort': 'asc',
                'limit': amount,
                'offset': 0
            }
            headers = {
                "Authorization": f'Bearer {fitbit_access_token}'
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
                    return None

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
                "user_id": self.id,
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


            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for sleep_data in sleep_data_entries:
                    placeholders = ', '.join(['?'] * len(sleep_data))
                    columns = ', '.join(sleep_data.keys())
                    values = tuple(sleep_data.values())
                    cursor.execute(f"INSERT INTO sleep_data ({columns}) VALUES ({placeholders})", values)



    def get_heart_data(self):
    # Get today's date
        today = datetime.today()

        # Calculate the date one week before today
        one_week_ago = today - timedelta(days=7)
        one_week_ago = one_week_ago.strftime('%Y-%m-%d')
        today = datetime.now()


        stop_loop = False
        while True:
            
            fitbit_user_id, fitbit_access_token = self.pull_fitbit_access_and_userid()

            url = f"https://api.fitbit.com/1/user/{fitbit_user_id}/activities/heart/date/{one_week_ago}/today.json"

            headers = {
                "Authorization": f'Bearer {fitbit_access_token}'
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
        fitbit_user_id, fitbit_access_token = self.pull_fitbit_access_and_userid()
        while True:

            url = f"https://api.fitbit.com/1/user/{fitbit_user_id}/activities/list.json"

            params = {
                'afterDate': after_date,
                'sort': 'asc',
                'limit': amount,
                'offset': 0
            }

            headers = {
                "Authorization": f'Bearer {fitbit_access_token}'
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
            'x-app-id': self.nutritionix_app_id,
            'x-app-key': self.nutritionix_api
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
            'x-app-id': self.nutritionix_app_id,
            'x-app-key': self.nutritionix_api,
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

                
                
                cursor.execute(f'''INSERT INTO food_log (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, entry_date, img, user_id) 
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


    def pull_data(self):
        while True:
            action = input("Enter 'l' to show all tables, a table name to query it, or 'e' to quit: ").strip()
            if action.lower() == 'e':  # Allow the user to exit
                print("Exiting function.")
                return
            
            try:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()

                if action.lower() == 'l':  # List all table names
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    tables = cursor.fetchall()
                    print("Tables in the database:")
                    for table in tables:
                        print(table[0])
                else:
                    # Query the database for all entries in the specified table
                    cursor.execute(f'SELECT * FROM {action} LIMIT 20')

                    # Fetch all rows from the query
                    rows = cursor.fetchall()

                    # Check if rows are empty
                    if not rows:
                        print(f"No data found in table '{action}'.")
                    else:
                        # Iterate over the rows and print them
                        for row in rows:
                            print(row)
                    
                    # User queried a specific table, so break after showing the data
                    break

            except sqlite3.OperationalError as e:
                if "no such table" in str(e):
                    print(f"No table with the name '{action}' exists. Please try again.")
                else:
                    print(f"An error occurred: {e}")
            
            finally:
                if conn:
                    conn.close()




    def dump_data(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Get the table name from the user
            table_name = input("Enter the table name you want to dump data into or 'exit' to quit: ").strip()
            if table_name.lower() == 'exit':
                print("Exiting function.")
                return

            try:
                # Get the column names from the specified table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns_info = cursor.fetchall()
                if not columns_info:
                    print(f"No table named '{table_name}' found.")
                    return

                columns = [info[1] for info in columns_info]  # Column names are at index 1
                print(f"Columns in '{table_name}': {', '.join(columns)}")

                # Prompt the user for each column value
                values = []

                for column in columns:
                    # Skip id or any autoincrement column

                    if column.endswith('_id'):
                        values.append(self.id)

                    if column != 'id' and not column.endswith('_id'):  
                        value = input(f"Enter value for {column}: ")
                        values.append(value)

                # Construct the INSERT statement dynamically
                placeholders = ', '.join(['?'] * len(values))
                cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns[1:])}) VALUES ({placeholders})", values)

                print(f"Data has been successfully dumped into '{table_name}'.")
                
                # Fetch all rows from the table to display them
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                for row in rows:
                    print(row)

            except sqlite3.OperationalError as e:
                print(f"An error occurred: {e}")



    def pull_fitbit_access_and_userid(self): 
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor() 
            cursor.execute('''SELECT fitbit_user_id, fitbit_access_token 
                            FROM tokens_codes_log
                            WHERE user_id = ?
                            ORDER BY last_date DESC
                            LIMIT 1''', (self.id,))  # Use a parameterized query
            
            result = cursor.fetchone()  # Use fetchone() since we expect at most one row
            if result:
                fitbit_user_id, access_token = result  # Unpack the tuple
            else:
                fitbit_user_id = None
                access_token = None
            
            return fitbit_user_id, access_token
