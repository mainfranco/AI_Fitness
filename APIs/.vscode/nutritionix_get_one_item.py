import requests
import json
from flask import jsonify

def get_item_options(food_item):

    url = 'https://trackapi.nutritionix.com/v2/search/instant'

    params = {
        'query': food_item
    }

    headers = {
        'x-app-id': 'bc4373cf',
        'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4'
    }

    response = requests.get(url,params,headers=headers).json()

    items = []  # List to hold the food items

    for entry in response['common']:
        item_details = {
            'food_name': entry['food_name'],
            'tag_id': entry['tag_id'],
            'serving_unit': entry['serving_unit'],
            'serving_quantity': entry['serving_qty']
        }
        items.append(item_details)

    return jsonify(items)

    