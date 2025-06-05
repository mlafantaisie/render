from sqlalchemy import (
    Table, Column, Integer, String, Float, DateTime, BigInteger,
    ForeignKey, Index, UniqueConstraint
)
from datetime import datetime
from app.db import metadata

# Users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
)

# Snapshots table (one snapshot per realm)
snapshot_sessions = Table(
    "snapshot_sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("realm_id", Integer, nullable=False, unique=True),  # Unique realm snapshot
    Column("scanned_at", DateTime, default=datetime.utcnow),
)

# Auction snapshots table
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
    UniqueConstraint("snapshot_id", "auction_id", name="uq_snapshot_auction")
)

# Realms table (Connected Realm IDs)
realms = Table(
    "realms",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("realm_id", Integer, unique=True, nullable=False),  # Connected Realm ID
    Column("realm_name", String, nullable=False),
)
