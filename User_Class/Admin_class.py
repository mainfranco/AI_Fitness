from class_user_1 import User
import sqlite3


class Admin(User):
    def __init__(self, name, user_id=None):
        super().__init__(name, user_id)


    

    def make_workout(self):
        workout_name = input('Workout Name: ')
        description = input('Workout Description: ')
        user_id = input('Which user is this workout for: ')

        workout_details = []
        while True:
            exercise_name = input('Exercise Name or E to stop: ').upper()
            if exercise_name == 'E':
                break
            exercise_sets = input('Number of Sets or E to stop: ').upper()
            if exercise_sets == 'E':
                break
            rep_range = input('Rep range or E to stop: ').upper()
            if rep_range == 'E':
                break

            data = {
                'exercise_name': exercise_name,
                'exercise_sets': exercise_sets,
                'rep_range': rep_range
            }

            workout_details.append(data)

        print(workout_details)

        with sqlite3.connect('fitness_app.db') as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO predefined_workouts (user_id, workout_name, description) VALUES (?,?,?) ''',
                        (user_id, workout_name, description))

            workout_id = cursor.lastrowid  # Retrieve the ID of the last inserted workout

            for i in workout_details:
                # Make sure to insert the workout_id for each exercise
                cursor.execute('''INSERT INTO workout_exercises (workout_id, exercise_name, sets, rep_range) VALUES (?,?,?,?) ''',
                            (workout_id, i['exercise_name'], i['exercise_sets'], i['rep_range']))


            
        
