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
        

        create_predefined_workouts_query = '''
        CREATE TABLE IF NOT EXISTS predefined_workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            workout_name TEXT NOT NULL,
            description TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)  -- Assuming there's a users table with id as the primary key
        )

        '''

        create_workout_exercises_query = '''
        CREATE TABLE IF NOT EXISTS workout_exercises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_id INTEGER NOT NULL,
            exercise_name TEXT NOT NULL,
            sets INTEGER,  -- Assuming you want to store the total number of sets here
            rep_range TEXT,  -- Storing rep range as TEXT, e.g., "8-12", or you could split it into min_reps and max_reps if needed
            FOREIGN KEY(workout_id) REFERENCES predefined_workouts(id)
        )
        '''


        create_exercise_sets_query = '''
        CREATE TABLE IF NOT EXISTS exercise_sets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_id INTEGER NOT NULL,  -- This should link back to workout_exercises
            set_number INTEGER,  -- To identify the set number within an exercise
            weight DECIMAL,
            reps INTEGER,
            FOREIGN KEY(exercise_id) REFERENCES workout_exercises(id)
        )
        '''




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
        cursor.execute(create_tokens_codes_log_query)
        cursor.execute(users_query)
        cursor.execute(create_predefined_workouts_query)
        cursor.execute(sleep_data_log_query)
        cursor.execute(create_fitbit_requests_log_query)
        cursor.execute(create_exercise_sets_query)
        cursor.execute(create_workout_exercises_query)


new_sql_tables()