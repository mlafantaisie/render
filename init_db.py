import os
from sqlalchemy import create_engine
from app.db import metadata
from app import models

# Get database URL from env
DATABASE_URL = os.getenv("DATABASE_URL")

# Now models.py has loaded all tables into shared metadata
metadata.create_all(engine)

print("Database initialized successfully.")
