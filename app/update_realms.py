from app.db import database
from app.models import realms
from app.blizz_api import get_access_token, fetch_connected_realm_index, fetch_connected_realm_detail

# Upsert realms into your DB
async def upsert_realm(realm_id, realm_name):
    query = """
        INSERT INTO realms (realm_id, realm_name)
        VALUES (:realm_id, :realm_name)
        ON CONFLICT (realm_id) DO UPDATE SET realm_name = :realm_name
    """
    values = {"realm_id": realm_id, "realm_name": realm_name}
    await database.execute(query, values)

# Master function to update all connected realms into DB
async def update_realms_in_db():
    token = await get_access_token()
    connected_realms = await fetch_connected_realm_index(token)

    for realm_entry in connected_realms:
        try:
            connected_realm_url = realm_entry["href"]
            connected_realm_data = await fetch_connected_realm_detail(connected_realm_url, token)
            connected_realm_id = connected_realm_data["id"]

            # Collect all realm names for the connected realm group
            realm_names = [r["name"]["en_US"] for r in connected_realm_data["realms"]]
            realm_name = " / ".join(realm_names)

            await upsert_realm(connected_realm_id, realm_name)
            print(f"Updated connected realm {connected_realm_id}: {realm_name}")

        except Exception as e:
            print(f"Failed to update connected realm entry: {e}")
