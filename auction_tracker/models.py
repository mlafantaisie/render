from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AuctionSnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.BigInteger, nullable=False)
    min_price = db.Column(db.BigInteger, nullable=False)
    market_value = db.Column(db.BigInteger, nullable=False)
    historical = db.Column(db.BigInteger, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
