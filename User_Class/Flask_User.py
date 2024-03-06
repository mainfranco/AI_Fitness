
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
                        'tag_id': entry.get('tag_id'),  # Common items might not have a tag_id
                        'serving_unit': entry.get('serving_unit'),  # Serving details might not be available
                        'serving_qty': entry.get('serving_qty'),
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
        data = []
        for i in response:
            data.append(i['name'])

        return data
        
# user = User_Flask('test', 100)

# print(user.search_exercise('bench'))