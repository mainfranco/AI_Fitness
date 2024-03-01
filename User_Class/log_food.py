from nutritionix_nlp_food import get_nutrition
from nutritionix_get_one_item import get_item_options
import sqlite3


def log_food_entry(query):
    if query == 'q' or query == "Q":
        print("Quit program")
        return 
    else:
        pass

    more_food = True
    while more_food:

        food_choice = get_item_options(query)
        if food_choice is None:
            break
        nutrition = get_nutrition(food_choice)


        while True:

            try:
            
                print("Your selection: ", nutrition['food_name'])
                print("Calories: ", nutrition['calories'])
                print("Protein: ", nutrition['protein'])
                print("Carbs: ", nutrition['carbs'])
                print("Fats: ", nutrition['fat'])
                print("Serving grams: ", nutrition['serving_weight_grams'])
                print("Serving unit: ", nutrition['serving_unit'])
                print('------------------------------')
                print('------------------------------')

                quantity = input("1 for grams | 2 for serving units:  ")
                if quantity == 'q' or quantity == 'Q':
                    print("Quit program")
                    return
                
                if quantity not in ["1", "2"]:  # Check if the input is not "1" or "2"
                    raise ValueError("Invalid choice")

                if quantity == "1" and nutrition['serving_weight_grams'] != 0:
                    grams = float(input(f'How many grams?: '))
                    serving_weight_grams = nutrition['serving_weight_grams']
                    servings = grams / serving_weight_grams

                    entry_log = {}
                    entry_log['food_name'] = nutrition['food_name']
                    entry_log['entry_date'] = nutrition['date']
                    entry_log['img'] = nutrition['photo']

                    # replacing None values with 0
                    for i in nutrition.keys():
                        if nutrition[i] == None:
                            nutrition[i] = float(0)
                    
                    # total_calories = servings * calories
                    for i in ['calories','fat','carbs','protein','cholesterol','sodium','sugars','potassium']:
                        entry_log[i] = round(servings * nutrition[i],2)
                    break
                                
                                
                elif quantity == "2" or (quantity == "1" and nutrition['serving_weight_grams'] == 0):
                    entry_log = {}
                    entry_log['food_name'] = nutrition['food_name']
                    entry_log['entry_date'] = nutrition['date']
                    entry_log['img'] = nutrition['photo']
                    
                    if nutrition['serving_weight_grams'] == 0:
                        print('serving grams not available. Use servings')

                    print(f"1 Serving is {nutrition['serving_quantity']}: {nutrition['serving_unit']}")
                    while True:
                        try:
                            serving_amount = float(input("How many servings?: "))
                        
                            break
                        except ValueError:
                            print("You must enter a number for the serving amount.")

                            
                   
                    for i in ['calories','fat','carbs','protein','cholesterol','sodium','sugars','potassium']:
                        entry_log[i] = round(serving_amount * nutrition[i], 2)


                break
            
            except ValueError as e:
                print("please enter an integer. Error: ", e)
        print('-----------------------')
        print('-----------------------')
        



     
        with sqlite3.connect("C:/Users/mainf/OneDrive/Desktop/Data Science Projects/Fitness Data Project/APIs/fitness_app.db") as conn:
            cursor = conn.cursor()

            
            
            cursor.execute('''INSERT INTO food_log (food_name, calories, protein, carbs, fat, cholesterol, sodium, potassium, sugars, entry_date, img) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                        (entry_log['food_name'],
                        entry_log['calories'],
                        entry_log['protein'],
                        entry_log['carbs'],
                        entry_log['fat'],
                        entry_log['cholesterol'],
                        entry_log['sodium'],
                        entry_log['potassium'],
                        entry_log['sugars'],
                        entry_log['entry_date'],
                        entry_log['img']))

            
         # Formatting the output
            output = (
                f"{entry_log['food_name']}, "
                f"calories: {entry_log['calories']}, "
                f"protein: {entry_log['protein']}, "
                f"carbs: {entry_log['carbs']}, "
                f"fats: {entry_log['fat']}, "
                f"cholesterol: {entry_log['cholesterol']}, "
                f"sodium: {entry_log['sodium']}, "
                f"potassium: {entry_log['potassium']}, "
                f"sugar: {entry_log['sugars']}, "
                f"date: {entry_log['entry_date']}, "
                f"img: {entry_log['img']}"
)

                    
            
            
            print('Entry Log')
            print('-------------------------')
            for key, value in entry_log.items():
                print(f"{key}: {value}")
            print('-------------------------')
            print('Food logged successfully')
            print('-------------------------')

            
        while True:
            keep_going = input('Do you want to log another item: Y or N: ').upper().strip()
            
            if keep_going == 'Y':
                query = input('Search Food: ')
                break  # Break out of the loop if the user wants to continue
            
            elif keep_going == 'N':
                more_food = False
                break  # Break out of the loop if the user does not want to continue
            
            else:
                print("Invalid input. Please enter 'Y' for yes or 'N' for no.")
    print("exited program")
            
print("Food Tracker")
print("Press q to quit the program at any time")
print("Or press s to return the Search screen at any time")
log_food_entry(input("Search food: "  ))




