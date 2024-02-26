
import requests

#This code lists food options based on a search query and then returns the name of that food item
#The food item named will be passed into get_nutrition to get nutrition data.

def get_item_options(food_item):

    url = 'https://trackapi.nutritionix.com/v2/search/instant'

    params = {
        'query': food_item
    }

    headers = {
        'x-app-id': 'bc4373cf',
        'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4'
    }
    while True:
        try:
            params = {'query': food_item}
            response = requests.get(url, params, headers=headers).json()

            # Work on adding branded foods to the returned list 
            # Check to see if the nutrients are taken from the correct food item from this code.
            
            if any(response[key] for key in response):
                break


        except requests.exceptions.RequestException as e:
            print('Error making request:', e)
        except Exception as e:
            print('An unexpected error occurred:', e)

        print('No options found. Please try another search.')
        food_item = input('Search food: ')




    items = []  # List to hold the food items
    for entry in response['branded'][:10]:
        item_details = {
            'food_name': entry['brand_name_item_name'],
            'tag_id': entry['nix_item_id'],
            'serving_unit': entry['serving_unit'],
            'serving_qty': entry['serving_qty'],
            'calories': entry['nf_calories'],
            'brand': True
        }
        items.append(item_details)
    for entry in response['common'][:10]:

        item_details = {
            'food_name': entry['food_name'],
            'tag_id': entry['tag_id'],
            'serving_unit': entry['serving_unit'],
            'serving_qty': entry['serving_qty'],
            'calories': None,
            'brand' : False
            
        }
        items.append(item_details)


    count = 1
    for i in items:
        name = i['food_name']
        tag_id = i['tag_id']
        serving_unit = i['serving_unit']
        serving_quantity = round(i['serving_qty'],2)
        calories = i['calories']

        print(f'option: {count}')
        print(name)
        print('tag id:',tag_id)
        print('serving unit:',serving_unit)
        print('serving quantity:',serving_quantity)
        print('calories per serving:', calories)
        print('-----------------------')
        print('-----------------------')
        count += 1

    while True:
        try:
            choice = input('Choice #: or press q to exit ')
            print('----------------------------')
            print('----------------------------')
            if choice == 'q' or choice == 'Q':
                print("Quit program")
                return
            
            if choice.isdigit():
                choice = int(choice)
                food_choice = (items[choice - 1]['food_name'], items[choice - 1]['tag_id'], items[choice - 1]['brand'])
                break
            elif choice == 'q' or choice == 'Q':
                food_choice = ("Empty", "Exit Program", "HIII")
                break


                    
              
        except ValueError:
            print("Input an integer from 1-20")
        except IndexError:
            print("Please choose a number within the valid range.")


    # Returns the name of the food if not a brand name   
    if food_choice[2] == False:
        return (food_choice[0])
    
    # Returns the brand_id if its a brand name and a True statement that can be parsed later on
    elif food_choice[2] == True:
        return (food_choice[1], True)
    


# print(get_item_options('grapes'))


