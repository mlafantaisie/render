import httpx
import os
import requests
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
        return response.json().get("access_token")

async def fetch_auction_data(realm_id, access_token):
    url = f"https://us.api.blizzard.com/data/wow/connected-realm/{realm_id}/auctions"
    params = {"namespace": "dynamic-us", "locale": "en_US"}
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        return response.json()

def fetch_realm_index(token):
    response = requests.get(
        REALM_INDEX_URL,
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()["realms"]

async def upsert_realm(realm_id, realm_name):
    query = """
        INSERT INTO realms (realm_id, realm_name)
        VALUES (:realm_id, :realm_name)
        ON CONFLICT (realm_id) DO UPDATE SET realm_name = :realm_name
    """
    values = {"realm_id": realm_id, "realm_name": realm_name}
    await database.execute(query, values)

async def update_realms_in_db():
    token = get_access_token()
    realms_list = fetch_realm_index(token)

    for realm in realms_list:
        await upsert_realm(realm["id"], realm["name"])

