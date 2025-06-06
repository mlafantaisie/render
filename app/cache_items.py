from app.db import database
from app.models import auction_snapshots, items
from app.blizz_api import get_access_token, fetch_item_name

async def update_item_cache():
    token = await get_access_token()

    # Get all distinct item_ids from auction_snapshots
    query = "SELECT DISTINCT item_id FROM auction_snapshots"
    rows = await database.fetch_all(query)
    item_ids = [row['item_id'] for row in rows]

    for item_id in item_ids:
        # Check if we already have the item
        existing = await database.fetch_one("SELECT id FROM items WHERE id = :id", {"id": item_id})
        if existing:
            continue

        name = await fetch_item_name(item_id, token)
        if name:
            await database.execute(
                "INSERT INTO items (id, name) VALUES (:id, :name)",
                {"id": item_id, "name": name}
            )
            print(f"Cached item {item_id}: {name}")
