from nutritionix_nlp_food import get_nutrition
from nutritionix_get_one_item import get_item_options
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from log_food import log_food_entry
import sqlite3

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/mainf/OneDrive/Desktop/Data Science Projects/Fitness Data Project/APIs/fitness_app.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def create_food_entries_table():
    # Connect to your database
    conn = sqlite3.connect('fitness_app.db')
    c = conn.cursor()

    # Execute a command: this creates a new table
    c.execute('''CREATE TABLE IF NOT EXISTS FINAL_FOOD_LOG (
                 food_name TEXT NOT NULL,
                 calories REAL,
                 protein REAL,
                 carbs REAL,
                 fat REAL,
                 cholestoral REAL,
                 sodium REAL,
                 potassium REAL,
                 sugars REAL
                 date TEXT,
                 img TEXT
                 )''')
    # Commit the changes and close the connection
    conn.commit()
    conn.close()

@app.route('/create-table')
def create_table():
    create_food_entries_table()
    return "Table created successfully!"


@app.route('/')
def home():
    html_content = '<h1>Food Tracker</h1><img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" alt="Food Image">'
    return html_content

@app.route('/food/<item_name>')
def food_options(item_name):
    return log_food_entry(item_name)




if __name__ == '__main__':
    app.run(debug=True)