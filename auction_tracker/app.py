from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from tsm_api import get_access_token, get_moon_guard_ah_id, get_auction_data
from models import db, AuctionSnapshot

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
db.init_app(app)

@app.route('/')
def index():
    recent = AuctionSnapshot.query.order_by(AuctionSnapshot.timestamp.desc()).limit(100).all()
    return render_template("index.html", snapshots=recent)

@app.route('/refresh')
def refresh():
    access_token = get_access_token()
    ah_id = get_moon_guard_ah_id(access_token)
    auction_data = get_auction_data(access_token, ah_id)

    for item in auction_data['items']:
        snapshot = AuctionSnapshot(
            item_id=item['itemId'],
            quantity=item['quantity'],
            min_price=item['minBuyout'],
            market_value=item['marketValue'],
            historical=item['historical']
        )
        db.session.add(snapshot)

    db.session.commit()
    return "Refreshed!"
