import os
import httpx

# Load Blizzard API credentials from environment variables
BLIZZ_CLIENT_ID = os.getenv("BLIZZ_CLIENT_ID")
BLIZZ_CLIENT_SECRET = os.getenv("BLIZZ_CLIENT_SECRET")

# Blizzard API Base URLs
TOKEN_URL = "https://oauth.battle.net/token"
BASE_URL = "https://us.api.blizzard.com"

# Blizzard API Endpoints
CONNECTED_REALM_INDEX_URL = f"{BASE_URL}/data/wow/connected-realm/index?namespace=dynamic-us&locale=en_US"
REALM_INDEX_URL = f"{BASE_URL}/data/wow/realm/index?namespace=dynamic-us&locale=en_US"
CONNECTED_REALM_DETAIL_URL = f"{BASE_URL}/data/wow/connected-realm/{{realm_id}}"
AUCTION_URL = f"{BASE_URL}/data/wow/connected-realm/{{realm_id}}/auctions"

# Get Blizzard OAuth token
async def get_access_token():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(BLIZZ_CLIENT_ID, BLIZZ_CLIENT_SECRET),
        )
        response.raise_for_status()
        return response.json().get("access_token")

# Fetch list of connected realm IDs
async def fetch_connected_realm_index(token):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(CONNECTED_REALM_INDEX_URL, headers=headers)
        response.raise_for_status()
        return response.json()["connected_realms"]

# Fetch details for a connected realm group
async def fetch_connected_realm_detail(url, token):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()

# Fetch auction data for a connected realm ID
async def fetch_auction_data(realm_id, token):
    url = AUCTION_URL.format(realm_id=realm_id)
    params = {"namespace": "dynamic-us", "locale": "en_US"}
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

# Fetch item name only
async def fetch_item_name(item_id, token):
    url = f"{BASE_URL}/data/wow/item/{item_id}?namespace=static-us&locale=en_US"
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get("name", None)
        else:
            print(f"Failed to fetch item {item_id}: {response.status_code}")
            return None

# Fetch item detail
async def fetch_item_detail(item_id, token):
    url = f"{BASE_URL}/data/wow/item/{item_id}?namespace={NAMESPACE}&locale={LOCALE}"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
