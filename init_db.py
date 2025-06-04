from sqlalchemy import create_engine
from app.db import metadata
from app import models  # <-- force tables to register

import os
import urllib.parse

# Get database URL from env
DATABASE_URL = os.getenv("DATABASE_URL")

# Adjust URL for SQLAlchemy sync engine
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Parse SSL parameters
engine = create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"}  # Critical on Render!
)

# Create all tables
metadata.create_all(engine)

print("Database initialized.")
