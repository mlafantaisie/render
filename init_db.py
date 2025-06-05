from app.db import metadata, engine
from app import models

def initialize_database():
    print("Starting database initialization...")
    metadata.create_all(engine)
    print("Database initialized successfully.")

initialize_database()
