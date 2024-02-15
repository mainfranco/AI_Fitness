import requests
import json

url = 'https://trackapi.nutritionix.com/v2/search/instant'

params = {
    'query': 'turkey burger'
}

headers = {
    'x-app-id': 'bc4373cf',
    'x-app-key': '68593b7a0aed2aa8b56021e5030ef5a4'
}

response = requests.get(url,params,headers=headers).json()


#print(response.text)

print(response)