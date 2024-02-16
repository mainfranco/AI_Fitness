from nutritionix_nlp_food import get_nutrition
from nutritionix_get_one_item import get_item_options
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


def log_food_entry(query):

    entry_log = {}
    
    nutrition = get_item_options('grilled chicken')
    print(nutrition)
    grams = int(input(f'How many grams: '))
    # math and logic here
    serving_weight_grams = nutrition[0]['serving_weight_grams']
    calories = nutrition[0]['calories']
    protein = nutrition[0]['protein']
    carbs= nutrition[0]['carbs']
    fats = nutrition[0]['fat']

    servings = grams / int(serving_weight_grams)


    total_calories = servings * calories
    total_protein = servings * protein
    total_carbs = servings * carbs
    total_fats = servings * fats

    entry_log['calories'] = round(total_calories)
    entry_log['protein'] = round(total_protein,2)
    entry_log['carbs'] = round(total_carbs,2)
    entry_log['fat'] = round(total_fats,2)

    return entry_log



meal_log = log_food_entry('grilled chicken')

print(meal_log)


