from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class AuctionSnapshot(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    min_price = db.Column(db.Integer)
    market_value = db.Column(db.Integer)
    historical = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
