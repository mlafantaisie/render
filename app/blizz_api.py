import httpx
import os

BLIZZ_CLIENT_ID = os.getenv("BLIZZ_CLIENT_ID")
BLIZZ_CLIENT_SECRET = os.getenv("BLIZZ_CLIENT_SECRET")
TOKEN_URL = "https://oauth.battle.net/token"

async def get_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(BLIZZ_CLIENT_ID, BLIZZ_CLIENT_SECRET),
        )
        return response.json().get("access_token")

async def fetch_auction_data(realm_id, access_token):
    url = f"https://us.api.blizzard.com/data/wow/connected-realm/{realm_id}/auctions"
    params = {"namespace": "dynamic-us", "locale": "en_US"}
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()
