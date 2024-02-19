import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('fitness_app.db')
cursor = conn.cursor()

# Query the database for all entries in food_logs
cursor.execute('SELECT * FROM food_log')

# Fetch all rows from the query
rows = cursor.fetchall()

# Iterate over the rows and print them
for row in rows:
    print(row)

# Close the connection
conn.close()