
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from Flask_User import User_Flask
import sqlite3
from datetime import datetime



user = User_Flask('Mark', 2)
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///fitness_app.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



@app.route('/')
def home():
   
    return render_template('home_screen.html')



@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        food_item = request.form.get('food_search')
        results = user.get_item_options(food_item)
        return render_template('results.html', results=results)
    return render_template('search_form.html')


@app.route('/get_nutrition', methods=['POST'])
def nutrition_info():
    food_name = request.form.get('food_name')
    tag_id = request.form.get('tag_id')
    is_branded = request.form.get('is_branded') == 'True'

    # Construct the argument for get_nutrition based on whether it's a branded item
    if is_branded and tag_id:
        food_item = (food_name, tag_id, True)
    else:
        food_item = (food_name, '', False)  # or just (food_name,) for non-branded items
    
    nutrition_details = user.get_nutrition(food_item)
    
    # Render a template to display the nutrition details
    return render_template('nutrition_facts.html', nutrition=nutrition_details)




@app.route('/process_input_choice', methods=['POST'])
def process_input_choice():
    measurement_type = request.form['measurement_type']
    food_name = request.form['food_name']
    food_id = request.form.get('food_id', None) 

    date = request.form.get('date')
    print(date)
    date_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    date_formatted = date_obj.strftime('%Y-%m-%d')

    serving_size = request.form.get('serving_size')
    serving_unit = request.form.get('serving_unit')
    weight_per_serving = request.form.get('weight_per_serving', '0')

    grams_input = request.form.get('grams', '0')
    servings_input = request.form.get('servings', '0')
    grams = float(grams_input) if grams_input else 0
    servings = float(servings_input) if servings_input else 0

    weight_per_serving = float(weight_per_serving) if weight_per_serving else 1  # Avoid division by zero

    nutrition_dict = {
        'calories': round(float(request.form.get('calories', '0')),2),
        'protein': round(float(request.form.get('protein', '0')),2),
        'carbs': round(float(request.form.get('carbs', '0')),2),
        'fat': round(float(request.form.get('fat', '0')),2),
        'cholesterol': round(float(request.form.get('cholesterol', '0')),2),
        'sodium': round(float(request.form.get('sodium', '0')),2),
        'sugar': round(float(request.form.get('sugars', '0')),2),
        'potassium': round(float(request.form.get('potassium', '0')),2)
    }

    if measurement_type == 'Grams':
        servings = grams / weight_per_serving
    elif measurement_type == 'Servings':

        pass  

    # Adjust values in nutrition_dict based on servings
    for key in nutrition_dict.keys():
        nutrition_dict[key] = round(nutrition_dict[key] * servings, 2)


    nutrition_dict['food_name'] = food_name
    nutrition_dict['grams'] = grams
    nutrition_dict['servings'] = round(servings,2)

    img_url = "placeholder_for_image_url"  

    try:
        with sqlite3.connect('fitness_app.db') as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO food_log (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, entry_date, img, user_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                food_name,
                nutrition_dict['calories'],
                nutrition_dict['protein'],
                nutrition_dict['carbs'],
                nutrition_dict['fat'],
                nutrition_dict['cholesterol'],
                nutrition_dict['sodium'],
                nutrition_dict['potassium'],
                nutrition_dict['sugar'], 
                date_formatted,
                img_url,  
                user.id  
            ))
    except Exception as e:
        print(f"An error occurred: {e}")
        # Handle or log the error as needed

    return render_template('final_food_log.html', nutrition=nutrition_dict)


from flask import request, render_template
import sqlite3

@app.route('/view_food_log', methods=['GET', 'POST'])
def view_food_log():
    # Default or user-specified entry date
    entry_date = request.form.get('date', '2024-03-06')  # Providing a fallback default date

    totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 
              'cholesterol': 0, 'sodium': 0, 'potassium': 0, 'sugars': 0}

    if request.method == 'POST':
        with sqlite3.connect('fitness_app.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM food_log WHERE user_id = ? AND entry_date = ?"
            cursor.execute(query, (user.id, entry_date))
            data = cursor.fetchall()

            # Assuming the indexes start from 1 for food name, and nutrients start from index 3 to 10
            # Adjust the indices based on your actual data structure
            for entry in data:
                totals['calories'] += entry[3]
                totals['protein'] += entry[4]
                totals['carbs'] += entry[5]
                totals['fat'] += entry[6]
                totals['cholesterol'] += entry[7]
                totals['sodium'] += entry[8]
                totals['potassium'] += entry[9]
                totals['sugars'] += entry[10]

    else:  # If it's a GET request
        data = []  # Ensure data is defined even if it's empty

    # Include totals in the template rendering
    return render_template('food_log.html', food_log=data, totals=totals, selected_date=entry_date)



@app.route('/search_exercises', methods=['GET', 'POST'])
def exercise_options():
    # If it's a POST request, we will process the form data
    if request.method == 'POST':
        # Extracting the 'query' from the form data
        query = request.form.get('query')
        
        search_results = user.search_exercise(query)

        return render_template('exercise_results.html', search_results=search_results)

    # If it's a GET request, just render the search form
    return render_template('search_exercises.html')



@app.route('/log_exercise', methods=['GET', 'POST'])
def log_exercises():
    return render_template('log_exercises.html')




@app.route('/logs', methods=['GET', 'POST'])
def choose_log():
    return render_template('choose_log.html')




@app.route('/exercise_logs', methods=['GET', 'POST'])
def view_exercise_log():
    selected_date = None
    data = []  # Initialize data as empty, suitable for a GET request

    if request.method == 'POST':
        # User submitted the form, so fetch the selected date
        selected_date = request.form.get('date')  # Use .get() for safer access

        if selected_date:  # Only query the database if a date is set
            with sqlite3.connect('fitness_app.db') as conn:
                cursor = conn.cursor()
                query = '''SELECT e.exercise_name, es.reps, es.weight, COUNT(es.id) as sets
                            FROM exercises e
                            JOIN exercise_sets es ON e.id = es.exercise_id
                            WHERE e.user_id = ?  
                            AND e.date = ?  
                            GROUP BY es.exercise_id, es.weight, es.reps'''

                cursor.execute(query, (user.id, selected_date))
                data = cursor.fetchall()

    # For a GET request or a POST request without a date, this will render the page without exercise data
    # For a POST request with a date, it will render the page with the queried data
    return render_template('workout_log.html', date=selected_date, exercises=data)


@app.route('/sleep_logs', methods=['GET', 'POST'])
def view_sleep_log():

    selected_date = None
    data = []  # Initialize data as empty, suitable for a GET request

    if request.method == 'POST':
        # User submitted the form, so fetch the selected date
        selected_date = request.form.get('date')  # Use .get() for safer access

        if selected_date:  # Only query the database if a date is set
            with sqlite3.connect('fitness_app.db') as conn:
                cursor = conn.cursor()
                query = '''SELECT efficiency, start_time, end_time, time_in_bed, minutes_asleep, minutesToFallAsleep, minutes_awake
                            FROM sleep_data
                            WHERE user_id = ?  
                            AND date = ?  
                            '''

                cursor.execute(query, (user.id, selected_date))
                data = cursor.fetchall()

    return render_template('sleep_log.html', sleep_logs =data)


if __name__ == '__main__':
    app.run(debug=True)