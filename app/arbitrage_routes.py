from fastapi import APIRouter, Request, Query, Form
from fastapi.responses import HTMLResponse, JSONResponse
from app.db import database
from app.templates_env import templates
from app.utils import format_price

router = APIRouter()

templates.env.filters['format_price'] = format_price

@router.get("/arbitrage", response_class=HTMLResponse)
async def arbitrage_page(request: Request):
    # Just render empty page first
    return templates.TemplateResponse("arbitrage.html", {
        "request": request
    })

@router.post("/arbitrage_query")
async def run_arbitrage(request: Request, limit: int = Form(10), min_spread: int = Form(0)):
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
        min_prices AS (
            SELECT ip.item_id, ip.item_name, ip.realm_name AS low_realm, ip.unit_price AS low_price
            FROM item_prices ip
            JOIN (
                SELECT item_id, MIN(unit_price) AS min_price
                FROM item_prices
                GROUP BY item_id
            ) minp ON ip.item_id = minp.item_id AND ip.unit_price = minp.min_price
        ),
        max_prices AS (
            SELECT ip.item_id, ip.item_name, ip.realm_name AS high_realm, ip.unit_price AS high_price
            FROM item_prices ip
            JOIN (
                SELECT item_id, MAX(unit_price) AS max_price
                FROM item_prices
                GROUP BY item_id
            ) maxp ON ip.item_id = maxp.item_id AND ip.unit_price = maxp.max_price
        ),
        combined AS (
            SELECT 
                min_prices.item_id,
                min_prices.item_name,
                min_prices.low_realm,
                min_prices.low_price,
                max_prices.high_realm,
                max_prices.high_price,
                max_prices.high_price - min_prices.low_price AS price_diff
            FROM min_prices
            JOIN max_prices ON min_prices.item_id = max_prices.item_id
            WHERE max_prices.high_price > min_prices.low_price
        )
        SELECT *
        FROM combined
        WHERE price_diff >= :min_spread
        ORDER BY price_diff DESC
        LIMIT :limit;
    """

    rows = await database.fetch_all(query, values={"min_spread": min_spread, "limit": limit})
    opportunities = [dict(row) for row in rows]

    return JSONResponse(opportunities)
