import databases
import sqlalchemy
import os

DATABASE_URL = os.getenv("DATABASE_URL")

DATABASE_URL = "postgresql://" + DATABASE_URL

if DATABASE_URL.startswith("postgresql+asyncpg://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1)

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

print("Your database URL is: " + DATABASE_URL)

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    echo=True
)
