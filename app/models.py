from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData, BigInteger, ForeignKey, Index
from datetime import datetime

metadata = MetaData()

# Existing users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
)

# New table: auction_snapshots
auction_snapshots = Table(
    "auction_snapshots",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("realm_id", Integer, nullable=False),  # Blizzard Connected Realm ID
    Column("scanned_at", DateTime, default=datetime.utcnow),
    Column("auction_id", BigInteger, nullable=False),  # Blizzard Auction ID (unique per realm)
    Column("item_id", Integer, nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", BigInteger, nullable=False),  # Blizzard prices are always in copper
    Column("buyout", BigInteger, nullable=True),  # sometimes buyout is missing
    Column("time_left", String, nullable=True),  # Blizzard's time_left field
)

# Add useful indexes for faster querying later
Index("ix_snapshot_realm_item", auction_snapshots.c.realm_id, auction_snapshots.c.item_id)
Index("ix_snapshot_scanned_at", auction_snapshots.c.scanned_at)
