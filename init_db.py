import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, BigInteger, ForeignKey
from datetime import datetime

# Get database URL from env
DATABASE_URL = os.getenv("DATABASE_URL")

# Adjust URL for SQLAlchemy sync engine (remove asyncpg for sync engine)
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)

# Create sync engine with Render's SSL
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# Create unified metadata object
metadata = MetaData()

# Users table
users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("password", String, nullable=False),
)

# Snapshot sessions table
snapshot_sessions = Table(
    "snapshot_sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("realm_id", Integer, nullable=False),
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
)

# Create indexes for performance
from sqlalchemy import Index

Index("ix_snapshot_sessions_realm", snapshot_sessions.c.realm_id)
Index("ix_auction_snapshots_item", auction_snapshots.c.item_id)
Index("ix_auction_snapshots_snapshot", auction_snapshots.c.snapshot_id)

# Finally: Create all tables
metadata.create_all(engine)

print("✅ Database initialized successfully.")
