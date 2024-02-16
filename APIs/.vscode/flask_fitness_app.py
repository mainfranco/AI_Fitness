from nutritionix_nlp_food import get_nutrition
from nutritionix_get_one_item import get_item_options
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/mainf/OneDrive/Desktop/Data Science Projects/Fitness Data Project/APIs/Fitness_app.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route('/')
def home():
    return 'Food Tracker'

@app.route('/search/<item_name>')
def food_options(item_name):
    return get_item_options(item_name)

@app.route('/nutrition/<item_name>')
def fnutrition(item_name):
    return get_nutrition(item_name)



if __name__ == '__main__':
    app.run(debug=True)