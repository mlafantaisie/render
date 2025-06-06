from fastapi import APIRouter, Request, Query
from fastapi.responses import HTMLResponse

from app.db import database
from app.templates_env import templates
from app.utils import format_price

router = APIRouter()

templates.env.filters['format_price'] = format_price

@router.get("/arbitrage", response_class=HTMLResponse)
async def arbitrage(
    request: Request,
    limit: int = Query(10, description="Number of items to show"),
    min_spread: int = Query(0, description="Minimum gold spread required")
):
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
        ranked_min AS (
            SELECT item_id, item_name, realm_name AS low_realm, unit_price AS low_price,
                ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY unit_price ASC, realm_name ASC) AS rn
            FROM item_prices
        ),
        ranked_max AS (
            SELECT item_id, item_name, realm_name AS high_realm, unit_price AS high_price,
                ROW_NUMBER() OVER (PARTITION BY item_id ORDER BY unit_price DESC, realm_name ASC) AS rn
            FROM item_prices
        ),
        min_prices AS (
            SELECT item_id, item_name, low_realm, low_price
            FROM ranked_min
            WHERE rn = 1
        ),
        max_prices AS (
            SELECT item_id, item_name, high_realm, high_price
            FROM ranked_max
            WHERE rn = 1
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

    return templates.TemplateResponse("arbitrage.html", {
        "request": request,
        "opportunities": opportunities,
        "limit": limit,
        "min_spread": min_spread
    })
