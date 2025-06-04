import os
from sqlalchemy import create_engine
from app.db import metadata
from app import models  # <-- THIS is the key

# Get database URL from env
DATABASE_URL = os.getenv("DATABASE_URL")

# Adjust URL for SQLAlchemy sync engine
if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}
)

# Now models.py has loaded all tables into shared metadata
metadata.create_all(engine)

print("✅ Database initialized successfully.")
