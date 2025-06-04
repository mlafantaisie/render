# init_db.py

from app.db import engine, metadata
from app import models  # load all tables

metadata.create_all(engine)
