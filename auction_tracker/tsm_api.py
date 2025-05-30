import requests
import os

# Use env variable for your TSM API key
TSM_API_KEY = os.getenv("TSM_API_KEY")
CLIENT_ID = "c260f00d-1071-409a-992f-dda2e5498536"

def get_access_token():
    url = "https://auth.tradeskillmaster.com/oauth2/token"
    payload = {
        "client_id": CLIENT_ID,
        "grant_type": "api_token",
        "scope": "app:realm-api app:pricing-api",
        "token": TSM_API_KEY
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()['access_token']

def get_moon_guard_ah_id():
    url = "https://realm-api.tradeskillmaster.com/realms"
    response = requests.get(url)
    response.raise_for_status()

    realms = response.json()
    for realm in realms['realms']:
        if realm['realmSlug'] == 'moon-guard':
            return realm['auctionHouseId']
    raise Exception("Moon Guard not found")

def get_auction_data(access_token, auction_house_id):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(f"https://api.tradeskillmaster.com/v1/ah/{auction_house_id}", headers=headers)
    response.raise_for_status()
    return response.json()
