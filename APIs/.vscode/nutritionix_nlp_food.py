import requests
import json

url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'

data = {
    'query': 'pepparoni pizza'

}

# Convert the dictionary to a JSON string
json_data = json.dumps(data)

headers = {
    'x-app-id': 'bc4373cf',
    'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4'
}


response = requests.post(url, data=json_data, headers=headers).json()


for i in response['foods']:
    name = i['food_name']
    serving_qty = i['serving_qty']
    serving_unit = i['serving_unit']
    serving_weight_grams = i['serving_weight_grams']
    calories = i['nf_calories']
    fat = i['nf_total_fat']
    carbs = i['nf_total_carbohydrate']
    protein = i['nf_protein']

    print(name)
    print('serving_quantity',serving_qty)
    print('calories:', calories)
    print('protein:', protein)
    print('total fat:', fat)
    print('carbs:', carbs)
    print('')
