import httpx
import os
from app.db import database
from app.models import realms

BLIZZ_CLIENT_ID = os.getenv("BLIZZ_CLIENT_ID")
BLIZZ_CLIENT_SECRET = os.getenv("BLIZZ_CLIENT_SECRET")
TOKEN_URL = "https://oauth.battle.net/token"
REALM_INDEX_URL = "https://us.api.blizzard.com/data/wow/realm/index?namespace=dynamic-us&locale=en_US"

async def get_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(BLIZZ_CLIENT_ID, BLIZZ_CLIENT_SECRET),
        )
        response.raise_for_status()
        return response.json().get("access_token")

async def fetch_auction_data(realm_id, access_token):
    url = f"https://us.api.blizzard.com/data/wow/connected-realm/{realm_id}/auctions"
    params = {"namespace": "dynamic-us", "locale": "en_US"}
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

async def fetch_realm_index(token):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(REALM_INDEX_URL, headers=headers)
        response.raise_for_status()
        return response.json()["realms"]
