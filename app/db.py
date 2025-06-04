import databases
import sqlalchemy
import os

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    DATABASE_URL,
    connect_args={"sslmode": "require"},
    echo=True
)

print("Engine dialect in use:", engine.dialect.dbapi)
