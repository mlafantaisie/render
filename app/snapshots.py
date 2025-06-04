from app.db import database
from app.models import snapshot_sessions, auction_snapshots
from app.blizz_api import get_access_token, fetch_auction_data

# Your existing save_snapshot stays
async def save_snapshot(realm_id, auctions):
    # Create snapshot session
    snapshot_query = snapshot_sessions.insert().values(
        realm_id=realm_id,
    )
    snapshot_id = await database.execute(snapshot_query)

    # Insert auction records
    query_list = []
    for auction in auctions:
        query = auction_snapshots.insert().values(
            snapshot_id=snapshot_id,
            auction_id=auction["id"],
            item_id=auction["item"]["id"],
            quantity=auction["quantity"],
            unit_price=auction.get("unit_price", 0),
            buyout=auction.get("buyout", 0),
            time_left=auction.get("time_left", "")
        )
        query_list.append(query)

    async with database.transaction():
        for query in query_list:
            await database.execute(query)

# This is the orchestration function you will call from main.py
async def take_snapshot(realm_id):
    token = await get_access_token()
    data = await fetch_auction_data(realm_id, token)
    auctions = data.get('auctions', [])
    await save_snapshot(realm_id, auctions)
