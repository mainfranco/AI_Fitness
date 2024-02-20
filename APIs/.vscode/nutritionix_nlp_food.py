import requests
import json
from flask import jsonify
from nutritionix_get_one_item import get_item_options
from datetime import datetime

#This code takes a food name and a weight in grams and returns nutrition facts a date and food image.

def get_nutrition(food_item):
    headers = {
        'x-app-id': 'bc4373cf',
        'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4',
    }

    if isinstance(food_item, tuple):
        print("Branded Food")
        url = 'https://trackapi.nutritionix.com/v2/search/item'
        response = requests.get(url, headers=headers, params={'nix_item_id': food_item[0]}).json()
        

    else:
        print('Common Food')
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
    
