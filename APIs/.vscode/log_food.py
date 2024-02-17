from nutritionix_nlp_food import get_nutrition
from nutritionix_get_one_item import get_item_options
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import sqlite3

def log_food_entry(query):

    more_food = True
    while more_food:

        nutrition = get_item_options(query)
        print(nutrition)
        grams = int(input(f'How many grams: '))
        print('-----------------------')
        print('-----------------------')
        
        serving_weight_grams = nutrition[0]['serving_weight_grams']
        calories = nutrition[0]['calories']
        protein = nutrition[0]['protein']
        carbs = nutrition[0]['carbs']
        fats = nutrition[0]['fat']

        servings = grams / int(serving_weight_grams)

        total_calories = servings * calories
        total_protein = servings * protein
        total_carbs = servings * carbs
        total_fats = servings * fats

        entry_log = {
            'food_name': nutrition[0]['food_name'],
            'calories': round(total_calories),
            'protein': round(total_protein, 2),
            'carbs': round(total_carbs, 2),
            'fat': round(total_fats, 2)
        }

        # Use context manager for database connection
        with sqlite3.connect('fitness_app.db') as conn:
            cursor = conn.cursor()
            # Update the CREATE TABLE statement to include food_name
            cursor.execute('''CREATE TABLE IF NOT EXISTS food_entries
                            (food_name TEXT, calories INTEGER, protein REAL, carbs REAL, fat REAL)''')
            # Update the INSERT INTO statement to include food_name
            cursor.execute('''INSERT INTO food_entries (food_name, calories, protein, carbs, fat) 
                            VALUES (?, ?, ?, ?, ?)''',
                        (entry_log['food_name'], entry_log['calories'], entry_log['protein'], entry_log['carbs'], entry_log['fat']))

        # Formatting the output
            output = f"{entry_log['food_name']}, calories: {entry_log['calories']}, protein: {entry_log['protein']}, carbs: {entry_log['carbs']}, 'fats': {entry_log['fat']}"
            print(f'Final Nutrients: {output}')
            print('-------------------------')
            print('-------------------------')
            print('Food logged succesfully')
            print('-------------------------')
        keep_going = input('Do you want to log another item: Y or N: ').upper()
        if keep_going == 'Y':
            query = input('Search Food: ')

        else:
            more_food = False
            





log_food_entry(input('search food: '))


