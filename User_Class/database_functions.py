import sqlite3

# Connect to the SQLite database file
conn = sqlite3.connect("fitness_app.db") 


# Commit the changes and close the connection
conn.commit()
conn.close()
