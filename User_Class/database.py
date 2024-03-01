import sqlite3

# Connect to the SQLite database file
conn = sqlite3.connect("fitness_app.db") 

conn.commit()
conn.close()