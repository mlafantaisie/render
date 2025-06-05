import os
import requests
from app.db import database, engine, metadata
from app.models import realms
import asyncio

# Load Blizzard credentials from environment variables
BLIZZ_CLIENT_ID = os.getenv("BLIZZ_CLIENT_ID")
BLIZZ_CLIENT_SECRET = os.getenv("BLIZZ_CLIENT_SECRET")

# Blizzard API endpoints
TOKEN_URL = "https://oauth.battle.net/token"
REALM_INDEX_URL = "https://us.api.blizzard.com/data/wow/realm/index?namespace=dynamic-us&locale=en_US"
REALM_DETAIL_URL = "https://us.api.blizzard.com/data/wow/realm/{realm_slug}?namespace=dynamic-us&locale=en_US"

# Get Blizzard access token
def get_access_token():
    response = requests.post(
        TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(BLIZZ_CLIENT_ID, BLIZZ_CLIENT_SECRET),
    )
    response.raise_for_status()
    return response.json()["access_token"]

# Fetch realm index (list of realms)
def fetch_realm_index(token):
    response = requests.get(
        REALM_INDEX_URL,
        headers={"Authorization": f"Bearer {token}"}
    )
    response.raise_for_status()
    return response.json()["realms"]

# Insert or update realm in database
async def upsert_realm(realm_id, realm_name):
    query = """
        INSERT INTO realms (realm_id, realm_name)
        VALUES (:realm_id, :realm_name)
        ON CONFLICT (realm_id) DO UPDATE SET realm_name = :realm_name
    """
    values = {"realm_id": realm_id, "realm_name": realm_name}
    await database.execute(query, values)

async def update_realms():
    await database.connect()
    metadata.create_all(engine)  # Ensure table exists

    token = get_access_token()
    realms_list = fetch_realm_index(token)

    for realm in realms_list:
        realm_id = realm["id"]
        realm_name = realm["name"]
        await upsert_realm(realm_id, realm_name)
        print(f"Updated realm {realm_id}: {realm_name}")

    await database.disconnect()
    print("Realm update completed.")

if __name__ == "__main__":
    asyncio.run(update_realms())
