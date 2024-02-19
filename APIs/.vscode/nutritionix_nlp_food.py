import requests
import json
from flask import jsonify

#This code takes a food name and a weight in grams and returns nutrition facts a date and food image.

def get_nutrition(food_item):
    url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'
    data = {'query': food_item}

    headers = {
        'x-app-id': 'bc4373cf',
        'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4'
    }

  
    response = requests.post(url, json=data, headers=headers).json()

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
        'date' : response['foods'][0]['consumed_at'],
        'photo': response['foods'][0]['photo']['thumb']}






    try:
        return jsonify(nutrition_details)
    
    except:
        return nutrition_details
    
