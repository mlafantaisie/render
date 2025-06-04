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
