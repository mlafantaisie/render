from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.db import database
from app.templates_env import templates
from app.utils import format_price

router = APIRouter()

# Register Jinja filter for price formatting
templates.env.filters['format_price'] = format_price

@router.get("/arbitrage", response_class=HTMLResponse)
async def arbitrage(request: Request):
    query = """
        WITH latest_snapshots AS (
            SELECT s.realm_id, s.id AS snapshot_id
            FROM snapshot_sessions s
            INNER JOIN (
                SELECT realm_id, MAX(scanned_at) AS latest_scan
                FROM snapshot_sessions
                GROUP BY realm_id
            ) latest ON latest.realm_id = s.realm_id AND latest.latest_scan = s.scanned_at
        ),
        item_prices AS (
            SELECT 
                a.item_id,
                i.name AS item_name,
                s.realm_id,
                r.realm_name,
                a.unit_price
            FROM auction_snapshots a
            JOIN latest_snapshots s ON a.snapshot_id = s.snapshot_id
            JOIN realms r ON s.realm_id = r.realm_id
            JOIN items i ON a.item_id = i.id
        ),
        item_stats AS (
            SELECT 
                item_id,
                item_name,
                MIN(unit_price) AS lowest_price,
                MAX(unit_price) AS highest_price,
                MAX(unit_price) - MIN(unit_price) AS price_diff
            FROM item_prices
            GROUP BY item_id, item_name
            HAVING MAX(unit_price) > MIN(unit_price)
        )
        SELECT item_id, item_name, lowest_price, highest_price, price_diff
        FROM item_stats
        ORDER BY price_diff DESC
        LIMIT 10;
    """

    rows = await database.fetch_all(query)
    opportunities = [dict(row) for row in rows]

    return templates.TemplateResponse("arbitrage.html", {
        "request": request,
        "opportunities": opportunities
    })
