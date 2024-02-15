import requests
import json

url = 'https://trackapi.nutritionix.com/v2/natural/nutrients'

data = {
    'query': 'Chicken, rice and brocoli'

}

# Convert the dictionary to a JSON string
json_data = json.dumps(data)

headers = {
    'x-app-id': 'bc4373cf',
    'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4'
}


response = requests.post(url, data=json_data, headers=headers).json()

# Print the response with headers
print(response)

