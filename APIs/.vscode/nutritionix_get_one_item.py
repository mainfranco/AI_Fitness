import requests
import json
from flask import jsonify
from nutritionix_nlp_food import get_nutrition

#This code lists food options based on a search query and then returns the name of that food item
#The food item named will be passed into get_nutrition to get nutrition data.

def get_item_options(food_item):

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
            
            if response.get('common'):
                break

        except requests.exceptions.RequestException as e:
            print('Error making request:', e)
        except Exception as e:
            print('An unexpected error occurred:', e)

        print('No options found. Please try another search.')
        food_item = input('Search food: ')




    items = []  # List to hold the food items

    for entry in response['common']:
        item_details = {
            'food_name': entry['food_name'],
            'tag_id': entry['tag_id'],
            'serving_unit': entry['serving_unit'],
            'serving_quantity': entry['serving_qty']
        }
        items.append(item_details)

    try:
        return jsonify(items)
    
    except:
        count = 1
        for i in items:
            name = i['food_name']
            tag_id = i['tag_id']
            serving_unit = i['serving_unit']
            serving_quantity = i['serving_quantity']
            print(f'option: {count}')
            print(name)
            print('tag id:',tag_id)
            print('serving unit:',serving_unit)
            print('serving quantity:',serving_quantity)
            print('-----------------------')
            print('-----------------------')
            count += 1

        while True:
            try:
                choice = int(input('choice: '))
                food_choice = items[choice - 1]['food_name']
                break  
            except ValueError:
                print("Input an integer from 1-20")
            except IndexError:
                print("Please choose a number within the valid range.")


        
        
    
    return food_choice






