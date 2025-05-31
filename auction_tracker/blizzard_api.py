import os
import requests

BLIZZARD_CLIENT_ID = os.getenv("BLIZZARD_CLIENT_ID")
BLIZZARD_CLIENT_SECRET = os.getenv("BLIZZARD_CLIENT_SECRET")

def get_blizzard_access_token():
    token_url = "https://us.battle.net/oauth/token"
    response = requests.post(
        token_url,
        auth=(BLIZZARD_CLIENT_ID, BLIZZARD_CLIENT_SECRET),
        data={'grant_type': 'client_credentials'}
    )
    response.raise_for_status()
    return response.json()['access_token']


def get_item_data(item_id, access_token):
    url = f"https://us.api.blizzard.com/data/wow/item/{item_id}"
    params = {
        "namespace": "static-us",
        "locale": "en_US",
        "access_token": access_token
    }
    response = requests.get(url, params=params)

    if response.status_code == 404:
        return None  # Item may no longer exist
    response.raise_for_status()

    data = response.json()
    return data.get("name")
