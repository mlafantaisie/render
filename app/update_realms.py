import os
import httpx
from app.db import database
from app.models import realms
import asyncio

BLIZZ_CLIENT_ID = os.getenv("BLIZZ_CLIENT_ID")
BLIZZ_CLIENT_SECRET = os.getenv("BLIZZ_CLIENT_SECRET")

TOKEN_URL = "https://oauth.battle.net/token"
CONNECTED_REALM_INDEX_URL = "https://us.api.blizzard.com/data/wow/connected-realm/index?namespace=dynamic-us&locale=en_US"
CONNECTED_REALM_DETAIL_URL = "https://us.api.blizzard.com/data/wow/connected-realm/{id}?namespace=dynamic-us&locale=en_US"

async def get_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(BLIZZ_CLIENT_ID, BLIZZ_CLIENT_SECRET),
        )
        response.raise_for_status()
        return response.json().get("access_token")

async def fetch_connected_realm_index(token):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(CONNECTED_REALM_INDEX_URL, headers=headers)
        response.raise_for_status()
        return response.json()["connected_realms"]

async def fetch_connected_realm_detail(connected_realm_url, token):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(connected_realm_url, headers=headers)
        response.raise_for_status()
        return response.json()

async def upsert_realm(connected_realm_id, realm_name):
    query = """
        INSERT INTO realms (realm_id, realm_name)
        VALUES (:realm_id, :realm_name)
        ON CONFLICT (realm_id) DO UPDATE SET realm_name = :realm_name
    """
    values = {"realm_id": connected_realm_id, "realm_name": realm_name}
    await database.execute(query, values)

async def update_realms_in_db():
    await database.connect()

    token = await get_access_token()
    connected_realms = await fetch_connected_realm_index(token)

    for realm_entry in connected_realms:
        connected_realm_url = realm_entry["href"]
        connected_realm_data = await fetch_connected_realm_detail(connected_realm_url, token)

        connected_realm_id = connected_realm_data["id"]
        # Take the first realm name in the list
        first_realm = connected_realm_data["realms"][0]
        realm_name = first_realm["name"]

        await upsert_realm(connected_realm_id, realm_name)
        print(f"Updated connected realm {connected_realm_id}: {realm_name}")

    await database.disconnect()
    print("Realm update completed.")
