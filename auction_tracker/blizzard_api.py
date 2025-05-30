import requests
import os

BLIZZARD_CLIENT_ID = os.getenv("BLIZZARD_CLIENT_ID")
BLIZZARD_CLIENT_SECRET = os.getenv("BLIZZARD_CLIENT_SECRET")

def get_blizzard_access_token():
    url = "https://us.battle.net/oauth/token"
    response = requests.post(
        url, 
        data={"grant_type": "client_credentials"}, 
        auth=(BLIZZARD_CLIENT_ID, BLIZZARD_CLIENT_SECRET)
    )
    response.raise_for_status()
    return response.json()['access_token']

def get_item_data(item_id, access_token):
    url = f"https://us.api.blizzard.com/data/wow/item/{item_id}?namespace=static-us&locale=en_US"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 404:
        return None
    response.raise_for_status()
    
    data = response.json()
    return data.get("name")
