import requests
import json
from flask import jsonify

def get_nutrition(food_item):
    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    data = {'query': food_item}

    headers = {
        'x-app-id': 'bc4373cf',
        'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4'
    }

  
    response = requests.post(url, json=data, headers=headers).json()

    nutrients_list = []  # List to accumulate the nutrition data

    for item in response['foods']:
        nutrition_details = {
            'food_name': item['food_name'],
            'serving_quantity': item['serving_qty'],
            'serving_unit': item['serving_unit'],
            'serving_weight_grams': item['serving_weight_grams'],
            'calories': item['nf_calories'],
            'fat': item['nf_total_fat'],
            'carbs': item['nf_total_carbohydrate'],
            'protein': item['nf_protein']
        }
        nutrients_list.append(nutrition_details)

    try:
        return jsonify(nutrients_list)
    
    except:
        return nutrients_list

