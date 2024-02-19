from nutritionix_nlp_food import get_nutrition
from nutritionix_get_one_item import get_item_options
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import sqlite3

def log_food_entry(query):

    more_food = True
    while more_food:

        food_choice = get_item_options(query)
        nutrition = get_nutrition(food_choice)
        print(nutrition)


        print(food_choice)

        while True:

            try:
                grams = int(input(f'How many grams: '))
                break
            
            except ValueError:
                print("please enter an integer")
        print('-----------------------')
        print('-----------------------')
        
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

        print(entry_log)

     
        with sqlite3.connect('fitness_app.db') as conn:
            cursor = conn.cursor()

            
            
            cursor.execute('''INSERT INTO food_log (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, entry_date, img) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
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
                        entry_log['img']))

            
         # Formatting the output
            output = f"{entry_log['food_name']}, calories: {entry_log['calories']},\
                  protein: {entry_log['protein']}, carbs: {entry_log['carbs']}, 'fats': {entry_log['fat']}, \
                  cholesterol: {entry_log['cholesterol']}, sodium: {entry_log['sodium']}, potassium: {entry_log['potassium']}, \
                  sugar: {entry_log['sugars']},date: {entry_log['entry_date']} , img: {entry_log['img']}"
                    
            
            
            print(f'Final Nutrients: {output}')
            print('-------------------------')
            print('-------------------------')
            print('Food logged succesfully')
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

            
query = input('Search for Food: ')
log_food_entry(query)





