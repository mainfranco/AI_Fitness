
import requests
from dotenv import load_dotenv
import os
import sqlite3
from datetime import datetime



class User_Flask:
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




    def get_item_options(self, food_item):
            url = 'https://trackapi.nutritionix.com/v2/search/instant'
            params = {'query': food_item}
            headers = {
                'x-app-id': self.nutritionix_app_id,
                'x-app-key': self.nutritionix_api
            }

            try:
                response = requests.get(url, headers=headers, params=params)
                response.raise_for_status()  # This will raise an error for HTTP error responses
                data = response.json()

                items = []  # List to hold the food items
                # Process branded items
                for entry in data.get('branded', [])[:10]:
                    items.append({
                        'food_name': entry.get('food_name', 'Unknown'),
                        'tag_id': entry.get('nix_item_id', 'N/A'),
                        'serving_unit': entry.get('serving_unit', 'N/A'),
                        'serving_qty': entry.get('serving_qty', 'N/A'),
                        'calories': entry.get('nf_calories', 'N/A'),
                        'brand': True
                    })
                # Process common items
                for entry in data.get('common', [])[:10]:
                    items.append({
                        'food_name': entry.get('food_name', 'Unknown'),
                        'tag_id': 'N/A',  # Common items might not have a tag_id
                        'serving_unit': 'N/A',  # Serving details might not be available
                        'serving_qty': 'N/A',
                        'calories': 'N/A',
                        'brand': False
                    })

                return items

            except requests.RequestException as e:
                print(f"Request exception: {e}")
                return None
            

    def get_nutrition(self,food_item):
        headers = {
            'x-app-id': self.nutritionix_app_id,
            'x-app-key': self.nutritionix_api,
        }

        if food_item[2] == True:

            url = 'https://trackapi.nutritionix.com/v2/search/item'
            response = requests.get(url, headers=headers, params={'nix_item_id': food_item[1]}).json()
            

        else:

            url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
            data = {'query': food_item[0]}
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