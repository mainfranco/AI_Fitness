import sqlite3

# Connect to the SQLite database file
conn = sqlite3.connect("C:/Users/mainf/OneDrive/Desktop/Data Science Projects/Fitness Data Project/APIs/fitness_app.db") 

# Create a cursor object
cursor = conn.cursor()

# Execute the CREATE TABLE statement
columns = []

# Create a table
cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS health_log (
        {" , ".join(columns)}
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()