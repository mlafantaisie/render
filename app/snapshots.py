from datetime import datetime
from app.db import database
from app.models import users, auction_snapshots, snapshot_sessions
from app.blizz_api import get_access_token, fetch_auction_data

async def save_snapshot(realm_id, auctions):
    # Upsert into snapshot_sessions (overwrite any previous session for realm)
    query = """
        INSERT INTO snapshot_sessions (realm_id, scanned_at)
        VALUES (:realm_id, :scanned_at)
        ON CONFLICT (realm_id) DO UPDATE SET scanned_at = :scanned_at
        RETURNING id
    """
    values = {"realm_id": realm_id, "scanned_at": datetime.utcnow()}
    snapshot_id = await database.fetch_val(query, values=values)

    # Delete existing auctions for this snapshot
    delete_query = auction_snapshots.delete().where(auction_snapshots.c.snapshot_id == snapshot_id)
    await database.execute(delete_query)

    # Insert new auctions (bulk insert strongly recommended here!)
    auction_values = []
    for auction in auctions:
        auction_values.append({
            "snapshot_id": snapshot_id,
            "auction_id": auction["id"],
            "item_id": auction["item"]["id"],
            "quantity": auction["quantity"],
            "unit_price": auction.get("unit_price", 0),
            "buyout": auction.get("buyout", 0),
            "time_left": auction.get("time_left", "")
        })

    async with database.transaction():
        query = auction_snapshots.insert()
        await database.execute_many(query, auction_values)

async def take_snapshot(realm_id):
    token = await get_access_token()
    data = await fetch_auction_data(realm_id, token)
    auctions = data.get('auctions', [])
    await save_snapshot(realm_id, auctions)
