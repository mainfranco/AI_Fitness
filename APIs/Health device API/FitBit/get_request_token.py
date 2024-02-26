import base64
import hashlib
import os
import json


def get_request_token(client_name):
    code_verifier = base64.urlsafe_b64encode(os.urandom(64)).rstrip(b'=').decode('utf-8')
    sha256_of_verifier = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_of_verifier).rstrip(b'=').decode('utf-8')

    params = {
        "client_id": "23RQZC",
        "response_type": "code",
        "scope": "heartrate sleep weight respiratory_rate activity oxygen_saturation temperature",
        "redirect_uri": "https://localhost:3000/callback",
        "code_challenge": code_challenge,
        "code_challenge_method": "S256"
    }

    # Construct the full URL with parameters
    from urllib.parse import urlencode
    full_url = f"https://www.fitbit.com/oauth2/authorize?{urlencode(params)}"

    # Output the URL
    print('Visit this URL in your web browser to authorize:', full_url)
    request_token = input("Paste Request Token: ")

    data = {
        "request_token": request_token,
        "code_verifier": code_verifier,
        "code_challenge": code_challenge,
        "client_name": client_name
    }

    with open(f'request_token_{client_name}.json', 'w') as json_file:
        json.dump(data, json_file)

    return code_verifier, code_challenge, request_token

