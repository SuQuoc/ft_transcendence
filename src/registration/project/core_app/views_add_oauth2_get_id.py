#!/usr/bin/env python3

import requests

CLIENT_ID = 'u-s4t2ud-'
CLIENT_SECRET = 's-s4t2ud-'

AUTHORIZE_URL = 'https://api.intra.42.fr/oauth/authorize'
TOKEN_URL = 'https://api.intra.42.fr/oauth/token'
REDIRECT_URI = 'https://localhost:8000/callback'
SCOPE = 'public'
STATE = '123456'
RESPONSE_TYPE = 'code'

def request_42_authorization_from_user(client_id):

    authorization_url = requests.Request('GET', AUTHORIZE_URL, params={
        'client_id': client_id,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'state': STATE,
        'response_type': RESPONSE_TYPE
    }).prepare().url
    print(f"Visit this URL to authorize the application: {authorization_url}")

def exchange_code_for_access_token(client_id, client_secret, code):
    response = requests.post(TOKEN_URL, data={
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret,
        'code': code,
        'redirect_uri': REDIRECT_URI
    })
    response.raise_for_status()
    return response.json().get('access_token')

def fetch_my_details(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    me_url = 'https://api.intra.42.fr/v2/me'
    response = requests.get(me_url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():

    request_42_authorization_from_user(CLIENT_ID)
    
    code = input("Enter the authorization code you received: ").strip()
    access_token = exchange_code_for_access_token(CLIENT_ID, CLIENT_SECRET, code)
    
    my_details = fetch_my_details(access_token)
    print(my_details.get('id'), my_details.get('login'))

if __name__ == "__main__":
    main()
