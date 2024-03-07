import sqlite3


def new_sql_tables():
    with sqlite3.connect('fitness_app.db') as conn:
        cursor = conn.cursor()


        users_query = '''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )'''

        create_food_log_query = '''
        CREATE TABLE IF NOT EXISTS food_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            food_name TEXT NOT NULL,
            calories INTEGER,
            protein DECIMAL,
            carbs DECIMAL,
            fat DECIMAL,
            cholesterol DECIMAL,
            sodium DECIMAL,
            potassium DECIMAL,
            sugars DECIMAL,
            entry_date DATE,
            img TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )'''
        
        create_exercise_log_query = '''
        CREATE TABLE IF NOT EXISTS exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            exercise_name TEXT,
            notes TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )'''


        create_sets_log_query = '''
        CREATE TABLE IF NOT EXISTS exercise_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_id INTEGER NOT NULL,
            weight DECIMAL,
            reps DECIMAL,
            user_id TEXT,
            FOREIGN KEY(exercise_id) REFERENCES exercises(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
            )'''      


        create_tokens_codes_log_query = '''
        CREATE TABLE IF NOT EXISTS tokens_codes_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            last_date TEXT NOT NULL,
            fitbit_access_token TEXT,
            fitbit_refresh_token TEXT,
            fitbit_user_id TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )'''


        create_fitbit_requests_log_query = '''
        CREATE TABLE IF NOT EXISTS request_tokens_fitbit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            fitbit_request_token TEXT,   
            fitbit_code_verifier TEXT,
            fitbit_code_challenge TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )'''


        sleep_data_log_query = '''
        CREATE TABLE IF NOT EXISTS sleep_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            date TEXT,
            duration_ms INTEGER,
            efficiency INTEGER,
            start_time TEXT,
            end_time TEXT,
            time_in_bed INTEGER,
            minutes_asleep INTEGER,
            minutesToFallAsleep INTEGER,
            minutes_awake INTEGER,
            log_id INTEGER,
            info_code INTEGER,
            IsMainSleep BOOLEAN,
            deep_sleep_count INTEGER,
            deep_sleep_minutes INTEGER,
            deep_sleep_30dayAvgMin INTEGER,
            light_sleep_count INTEGER,
            light_sleep_minutes INTEGER,
            light_sleep_30dayAvgMin INTEGER,
            rem_sleep_count INTEGER,
            rem_sleep_minutes INTEGER,
            rem_sleep_30dayAvgMin INTEGER,
            wake_count INTEGER,
            wake_minutes INTEGER,
            wake_30dayAvgMin INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id))'''

        # Execute the create table query
        cursor.execute(create_food_log_query)
        cursor.execute(create_exercise_log_query)
        cursor.execute(create_tokens_codes_log_query)
        cursor.execute(users_query)
        cursor.execute(create_sets_log_query)
        cursor.execute(sleep_data_log_query)
        cursor.execute(create_fitbit_requests_log_query)
        


new_sql_tables()