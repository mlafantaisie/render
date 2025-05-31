import sqlalchemy
from sqlalchemy import text
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import os
from tsm_api import get_access_token, get_moon_guard_ah_id, get_auction_data
from models import db, AuctionSnapshot, Item
import time
from blizzard_api import get_blizzard_access_token, get_item_data

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "supersecretkey")
db.init_app(app)

with app.app_context():
    # Connect directly to DB
    connection = db.engine.connect()
    try:
        # Attempt to add the column; ignore if exists
        connection.execute(text("""
            ALTER TABLE items ADD COLUMN IF NOT EXISTS last_attempt TIMESTAMP;
        """))
        print("✅ last_attempt column ensured")
    except Exception as e:
        print(f"⚠ Failed to alter table: {e}")
    finally:
        connection.close()

@app.route('/')
def index():
    recent = AuctionSnapshot.query.order_by(AuctionSnapshot.timestamp.desc()).limit(100).all()
    return render_template("index.html", snapshots=recent)

@app.route('/refresh')
def refresh():
    import sys
    print("Refreshing Auction House data...", file=sys.stderr)

    access_token = get_access_token()
    print("Access token obtained.", file=sys.stderr)

    ah_id = get_moon_guard_ah_id(access_token)
    print(f"Auction House ID for Moon Guard: {ah_id}", file=sys.stderr)

    auction_data = get_auction_data(access_token, ah_id)
    print(f"Number of items received: {len(auction_data)}", file=sys.stderr)

    inserted = 0
    for item in auction_data:
        if not item.get('itemId'):
            continue
        
        snapshot = AuctionSnapshot(
            item_id=item['itemId'],
            quantity=item['quantity'],
            min_price=item['minBuyout'],
            market_value=item['marketValue'],
            historical=item['historical']
        )
        db.session.add(snapshot)
        inserted += 1

    db.session.commit()
    print(f"Inserted {inserted} items into the database.", file=sys.stderr)
    return "Refreshed!"

@app.route('/enrich-items')
def enrich_items():
    access_token = get_blizzard_access_token()
    unique_item_ids = db.session.query(AuctionSnapshot.item_id).distinct().all()
    existing_item_ids = {item.id for item in Item.query.all()}

    new_items = 0
    for (item_id,) in unique_item_ids:
        if item_id is None or item_id in existing_item_ids:
            continue

        try:
            item_name = get_item_data(item_id, access_token)
            if item_name:
                db.session.add(Item(id=item_id, name=item_name))
                new_items += 1

            # Be nice to Blizzard servers: throttle ~10/sec
            time.sleep(0.1)

        except Exception as e:
            print(f"Failed to load item {item_id}: {e}")

    db.session.commit()
    return f"Enrichment complete: {new_items} new items loaded"
