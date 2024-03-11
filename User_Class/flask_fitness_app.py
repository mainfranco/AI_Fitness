
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from Flask_User import User_Flask
import sqlite3
from datetime import datetime
from datetime import date
import re 
import json
from openai import OpenAI
import os


user = User_Flask('Mark Infranco', 1)


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



import base64
from flask import request, jsonify
from openai import OpenAI

@app.route('/upload-image', methods=['GET', 'POST'])
def process_food_image():
    if 'image' in request.files:
        img = request.files['image']
        img_path = 'temp_img.jpg'
        img.save(img_path)

        with open(img_path, 'rb') as file:
            img_data = file.read()

        # Encode the image data as base64
        img_base64 = base64.b64encode(img_data).decode('utf-8')

        client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Give an estimate of the entire nutrition facts of this food. The format of your response must be the following. food_name: '', total_calories: '', total_protein: '', total_carbs: '', total_fats:''. Please provide one number for each entry in calories, proteins etc and dont include ranges. Only one singular numeric value without any g attached the end. Ex. 'calories': 150 "
                        },
                        {
                            "type": "image",
                            "image": img_base64,
                        },
                    ],
                }
            ],
            max_tokens=1000,
        )

        response_data = {
            'content': response.choices[0].message.content,
            'finish_reason': response.choices[0].finish_reason,
            'index': response.choices[0].index
        }
        
        food_data = user.format_food_img_data(response_data)
        food_name = food_data['food_name']
        calories = food_data['total_calories']
        protein = food_data['total_protein']
        carbs = food_data['total_carbs']
        fat = food_data['total_fats']
        cholesterol = 0
        sodium = 0
        potassium = 0
        sugars = 0
        today = date.today()
        formatted_date = today.strftime("%Y-%m-%d")
        user_id = user.id

        with sqlite3.connect('fitness_app.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO food_log (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, entry_date, img, user_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, formatted_date, 'No Image', user_id))

        return render_template('manual_food_log_result.html', 
                        food_name=food_name, 
                        calories=calories, 
                        protein=protein, 
                        carbs=carbs, 
                        fat=fat, 
                        cholesterol=cholesterol, 
                        sodium=sodium, 
                        potassium=potassium, 
                        sugars=sugars, 
                        entry_date=formatted_date, 
                        img=img, 
                        user_id=user_id)
    else:
        return 'No image found in the request'




@app.route('/manual-entry', methods=['GET', 'POST'])
def enter_food_manually():

    today = date.today()
    formatted_date = today.strftime("%Y-%m-%d")

    if request.method == 'GET':
        return render_template('enter_food_manually.html')

    # Assuming `user.id` is defined elsewhere and is accessible
    user_id = user.id

    food_name = request.form.get('food_name')
    calories = request.form.get('calories')
    protein = request.form.get('protein')
    carbs = request.form.get('carbs')
    fat = request.form.get('fats')
    cholesterol = 0  # or from form, if available
    sodium = 0  # or from form, if available
    potassium = 0  # or from form, if available
    sugars = 0  # or from form, if available
    img = "NA"  # or handle file upload

    # Insert data into database
    with sqlite3.connect('fitness_app.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO food_log (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, entry_date, img, user_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, formatted_date, img, user_id))

    # Pass the entered values to the template
    return render_template('manual_food_log_result.html', 
                           food_name=food_name, 
                           calories=calories, 
                           protein=protein, 
                           carbs=carbs, 
                           fat=fat, 
                           cholesterol=cholesterol, 
                           sodium=sodium, 
                           potassium=potassium, 
                           sugars=sugars, 
                           entry_date=formatted_date, 
                           img=img, 
                           user_id=user_id)





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
        print(servings)
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
    entry_date = request.form.get('date') 

    totals = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 
              'cholesterol': 0, 'sodium': 0, 'potassium': 0, 'sugars': 0}

    if request.method == 'POST':
        with sqlite3.connect('fitness_app.db') as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM food_log WHERE user_id = ? AND entry_date = ?"
            cursor.execute(query, (user.id, entry_date))
            data = cursor.fetchall()

            for entry in data:
                totals['calories'] += entry[3]
                totals['protein'] += entry[4]
                totals['carbs'] += entry[5]
                totals['fat'] += entry[6]
                totals['cholesterol'] += entry[7]
                totals['sodium'] += entry[8]
                totals['potassium'] += entry[9]
                totals['sugars'] += entry[10]

            for i in totals.keys():
                totals[i] = round(totals[i],2)

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



@app.route('/my_workouts')
def my_workouts():
    if request.method == 'GET':
        # Fetch the workouts for the current user
        workouts = user.get_user_workouts()

        # Clean workout names and convert to list of dictionaries
        cleaned_workouts = [{'name': re.sub(r'[^a-zA-Z\s]', '', workout[0]), 'id': workout[1]} for workout in workouts]

        return render_template('choose_workout.html', workouts=cleaned_workouts)



@app.route('/my_workouts/<int:workout_id>')  # Use an integer converter for workout_id
def exercise_choice(workout_id):
    print('This is the first workout id', workout_id)
    with sqlite3.connect(user.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT exercise_name, sets, rep_range
                          FROM workout_exercises
                          WHERE workout_id = ?
                       ''', (workout_id,)) 

        exercises = cursor.fetchall()


    return render_template('selected_workout.html', workout_id=workout_id, exercises=exercises)


@app.route('/start_tracking', methods=['POST'])
def start_tracking():

    now = datetime.now()
    today_date = now.strftime("%Y-%m-%d")

    workout_id = request.form.get('workout_id')
    print(workout_id)
    # Assuming you've set up a database connection somewhere
    conn = sqlite3.connect('fitness_app.db')
    cur = conn.cursor()
    
    cur.execute("SELECT id, exercise_name, sets, rep_range FROM workout_exercises WHERE workout_id = ?", (workout_id,))
    exercises = cur.fetchall()
    print(exercises)

    exercise_tracking = {}
    for exercise_id, name, sets, rep_range in exercises:
        exercise_tracking[name] = {
            'exercise_id': exercise_id,
            'sets': sets,
            'rep_range': rep_range,
            'sets_data': [{'set_number': i + 1, 'weight': '', 'reps': ''} for i in range(sets)]
        }

    return render_template('tracking_workouts.html', exercise_tracking=exercise_tracking, today_date = today_date)


@app.route('/submit_workout', methods=['POST'])
def submit_workout():

    today_date = request.form.get('workout_date')
  
    # Iterate through the form data
    for key, value in request.form.items():

        # Check if the current form input is for 'weight' and has a value
        if 'weight' in key and value:
            parts = key.split('_')
            # Assuming the format of the key is 'exercise<exercise_id>_set<set_number>_weight'
            exercise_id = int(parts[0].replace('exercise', ''))
            set_number = int(parts[1].replace('set', ''))
            
            # Construct the key for the 'reps' using the same 'exercise_id' and 'set_number'
            reps_key = f'exercise{exercise_id}_set{set_number}_reps'
            reps = request.form.get(reps_key)
            
            weight_key = f'exercise{exercise_id}_set{set_number}_weight'
            weight = request.form.get(weight_key)
            

            print('exercise id', exercise_id)
            print('set number', set_number)
            print('weight', weight)
            print('reps', reps)
            # Only proceed if both 'reps' and 'weight' are provided
            if reps and weight:
                print('Triggered succesfully')
                # Insert the data into the 'exercise_sets' table
                try:
                    with sqlite3.connect('fitness_app.db') as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            INSERT INTO exercise_sets (exercise_id, set_number, weight, reps, date_performed) 
                            VALUES (?, ?, ?, ?, ?)
                        ''', (exercise_id, set_number, float(weight), int(reps), today_date))
                         
                        print('SQL insert was triggered')
                except sqlite3.Error as e:
                    print(f"An error occurred: {e}")
                    # Handle the error, such as returning an error message to the user
                    return "An error occurred during database insertion."

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
    # After successful insertion, redirect to a confirmation page
    return render_template('display_workout_log.html')








@app.route('/log_exercise', methods=['GET', 'POST'])
def log_exercises():
    return render_template('log_exercises.html')




@app.route('/logs', methods=['GET', 'POST'])
def choose_log():
    return render_template('choose_log.html')




@app.route('/exercise_logs', methods=['GET', 'POST'])
def view_exercise_log():
    selected_date = None
    data = [] 
    exercises_entry = {}  # Initialize here to ensure it's always defined

    if request.method == 'POST':
        selected_date = request.form.get('date')
        if selected_date:
            with sqlite3.connect('fitness_app.db') as conn:
                cursor = conn.cursor()
                query = '''SELECT e.exercise_name, es.set_number, es.reps, es.weight
                           FROM workout_exercises e
                           JOIN exercise_sets es ON e.id = es.exercise_id
                           WHERE es.date_performed = ?  
                           GROUP BY es.exercise_id, es.weight, es.reps'''
                cursor.execute(query, (selected_date,))
                data = cursor.fetchall()

                for i in data:
                    exercise_name, set_num, reps, weight = i  # Simplified assignment
                    weight_rep_dict = {f'set_{set_num}': [weight, reps]}

                    if exercise_name not in exercises_entry:
                        exercises_entry[exercise_name] = [weight_rep_dict]
                    else:
                        exercises_entry[exercise_name].append(weight_rep_dict)

                print(exercises_entry)
    return render_template('workout_log.html', date=selected_date, data=exercises_entry)



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