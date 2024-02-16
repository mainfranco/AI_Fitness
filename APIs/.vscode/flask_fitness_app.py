from nutritionix_nlp_food import get_nutrition
from nutritionix_get_one_item import get_item_options
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///C:/Users/mainf/OneDrive/Desktop/Data Science Projects/Fitness Data Project/APIs/Fitness_app.db"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)




@app.route('/')
def home():
    html_content = '<h1>Food Tracker</h1><img src="https://images.unsplash.com/photo-1504674900247-0877df9cc836?q=80&w=1470&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" alt="Food Image">'
    return html_content

@app.route('/search/<item_name>')
def food_options(item_name):
    return get_item_options(item_name)

@app.route('/test')
def test():
    return render_template('angel.htm')


@app.route('/nutrition/<item_name>')
def nutrition(item_name):
    return get_nutrition(item_name)



if __name__ == '__main__':
    app.run(debug=True)