import sqlite3

# Connect to the SQLite database file
conn = sqlite3.connect("C:/Users/mainf/OneDrive/Desktop/Data Science Projects/Fitness Data Project/APIs/fitness_app.db") 

# Create a cursor object
cursor = conn.cursor()

# Execute the CREATE TABLE statement
columns = [
    "food_name TEXT NOT NULL",
    "entry_date TEXT NOT NULL", 
    "img TEXT",
    "calories REAL",
    "fat REAL",
    "carbs REAL",
    "protein REAL",
    "cholesterol REAL",
    "sodium REAL",
    "sugars REAL",
    "potassium REAL"
]

# Create a table
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS food_log (
        {" , ".join(columns)}
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()
