import sqlite3

# Connect to the SQLite database file
conn = sqlite3.connect("fitness_app.db") 


# Commit the changes and close the connection
conn.commit()
conn.close()

def list_tables(db_path):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        for table in tables:
            print(table[0])

# Usage
list_tables('fitness_app.db')
