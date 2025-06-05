import os
import sqlalchemy
import bcrypt
from app.db import engine, metadata
from sqlalchemy import Table, select

# Load models (so metadata knows about tables)
from app import models

# Reference to 'users' table
users = models.users

# Create a DB connection
connection = engine.connect()

# Admin credentials
admin_username = os.getenv("ADMIN_USER")
admin_password_plain = os.getenv("ADMIN_PASSWORD")

# Hash the password using bcrypt
hashed_password = bcrypt.hashpw(admin_password_plain.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Check if user exists
select_stmt = select(users).where(users.c.username == admin_username)
result = connection.execute(select_stmt).fetchone()

if result:
    print(f"Admin user '{admin_username}' already exists.")
else:
    # Insert new admin user
    insert_stmt = users.insert().values(username=admin_username, password=hashed_password)
    connection.execute(insert_stmt)
    connection.commit()
    print(f"Admin user '{admin_username}' has been created successfully.")

# Close connection
connection.close()
