import requests
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth1
import numpy as np
import time

url = 'https://platform.fatsecret.com/rest/server.api?method=food_entries.get_month.v2'

consumer_key = '6f55b416751a43b6ab185d3b6400b9d0'        
consumer_secret = 'efb7e81b47a8428bb475645411a5fc62'  
access_token = 'fdee7e119f7c4a90a9c5ed27671beb6f'      
token_secret = '0ca6b91e09c04ab58097090d1b4e0f64'   
signature_method = 'HMAC-SHA1'
current_time = time.time()

params = {
    'oauth_signature_method':'HMAC-SHA1',
    'oauth_consumer_key':'6f55b416751a43b6ab185d3b6400b9d0',
    'oauth_nonce':np.random,
    'oauth_timestamp': current_time,
    'oauth_signature': 'hi'

}

auth = OAuth1(consumer_key, consumer_secret, access_token, token_secret,signature_method=signature_method,nonce='hello',timestamp=current_time)
response = requests.get(url, auth=auth,params=params)

print(response.status_code)
if response.status_code == 200:
    print('Success!')
    print(response.text)  
else:
    print('Failed to retrieve data.')
