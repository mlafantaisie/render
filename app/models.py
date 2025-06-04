from app.db import metadata
from sqlalchemy import Table, Column, Integer, String, Float, DateTime, MetaData, BigInteger, ForeignKey, Index
from datetime import datetime

metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
)

auction_snapshots = Table(
    "auction_snapshots",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("snapshot_id", Integer, ForeignKey("snapshot_sessions.id")),
    Column("auction_id", BigInteger, nullable=False),
    Column("item_id", Integer, nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", BigInteger, nullable=False),
    Column("buyout", BigInteger, nullable=True),
    Column("time_left", String, nullable=True),
)

snapshot_sessions = Table(
    "snapshot_sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("realm_id", Integer, nullable=False),
    Column("scanned_at", DateTime, default=datetime.utcnow),
)

# Add useful indexes for faster querying later
Index("ix_snapshot_sessions_realm", snapshot_sessions.c.realm_id)
Index("ix_auction_snapshots_item", auction_snapshots.c.item_id)
Index("ix_auction_snapshots_snapshot", auction_snapshots.c.snapshot_id)
