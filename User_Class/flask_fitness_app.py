
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from Flask_User import User_Flask
import sqlite3



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
                date,
                img_url,  
                user.id  
            ))
    except Exception as e:
        print(f"An error occurred: {e}")
        # Handle or log the error as needed

    return render_template('final_food_log.html', nutrition=nutrition_dict)


@app.route('/view_food_log')
def view_food_log():

    data = []
    with sqlite3.connect('fitness_app.db') as conn:
        cursor = conn.cursor()
        query = "SELECT * FROM food_log WHERE user_id = ?"
        cursor.execute(query, (user.id,))
        data = cursor.fetchall()
    
    return render_template('food_log.html', food_log=data)


@app.route('/search_exercises', methods=['GET', 'POST'])
def exercise_options():
    # If it's a POST request, we will process the form data
    if request.method == 'POST':
        # Extracting the 'query' from the form data
        query = request.form.get('query')
        
        # Perform the search using the user's `search_exercise` method
        # which should return the search results or handle the search internally
        search_results = user.search_exercise(query)

        # Render a template to display the search results
        # You would need to create an HTML template that expects `search_results`
        return render_template('exercise_results.html', search_results=search_results)

    # If it's a GET request, just render the search form
    return render_template('search_exercises.html')







if __name__ == '__main__':
    app.run(debug=True)