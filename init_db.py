from app.db import metadata, engine, database
from app import models

# Now models.py has loaded all tables into shared metadata
metadata.create_all(engine)

print("Database initialized successfully.")
