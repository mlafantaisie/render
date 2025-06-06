from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import database, metadata, engine
from app.auth_routes import require_admin
from app.update_realms import update_realms_in_db
from app.templates_env import templates
from app.cache_items import update_item_cache
from app.blizz_api import get_access_token, fetch_item_detail

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)

@router.get("", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@router.post("/clear_realms")
async def clear_realms():
    await database.execute("DELETE FROM realms;")
    return {"status": "Realms cleared"}

@router.post("/clear_scans")
async def clear_scans():
    await database.execute("DELETE FROM auction_snapshots;")
    await database.execute("DELETE FROM snapshot_sessions;")
    return {"status": "Scans cleared"}

@router.post("/update_items")
async def update_items():
    await update_item_cache()
    return {"status": "Item cache updated"}

@router.get("/item_cache_summary")
async def item_cache_summary():
    # How many distinct item_ids we have in auction_snapshots
    auction_items_query = "SELECT COUNT(DISTINCT item_id) FROM auction_snapshots"
    auction_items = await database.fetch_val(auction_items_query)

    # How many items we've cached
    cached_items_query = "SELECT COUNT(*) FROM items"
    cached_items = await database.fetch_val(cached_items_query)

    return {
        "auction_items": auction_items,
        "cached_items": cached_items,
        "missing": auction_items - cached_items
    }

@router.post("/update_realms")
async def update_realms_route():
    await update_realms_in_db()
    return {"status": "Realms updated"}

@router.post("/update_tables")
async def update_tables():
    metadata.create_all(engine)
    return {"status": "Tables updated"}

@router.post("/fetch_missing_items")
async def fetch_missing_items():
    # Find item_ids we have in auction_snapshots that aren't cached yet
    query = """
        SELECT DISTINCT a.item_id
        FROM auction_snapshots a
        LEFT JOIN items i ON a.item_id = i.id
        WHERE i.id IS NULL
        LIMIT 1000
    """
    rows = await database.fetch_all(query)
    missing_items = [row['item_id'] for row in rows]

    if not missing_items:
        return {"status": "No missing items found."}

    token = await get_access_token()

    for item_id in missing_items:
        try:
            item_data = await fetch_item_detail(item_id, token)
            name = item_data["name"]["en_US"]

            insert_query = "INSERT INTO items (id, name) VALUES (:id, :name) ON CONFLICT DO NOTHING"
            await database.execute(insert_query, {"id": item_id, "name": name})
            print(f"Cached item {item_id}: {name}")

        except Exception as e:
            print(f"Failed to fetch item {item_id}: {e}")

    return {"status": f"Cached {len(missing_items)} missing items."}

@router.post("/execute_sql")
async def execute_sql(query: str = Form(...)):
    try:
        await database.execute(query)
        return {"status": "Query executed successfully."}
    except Exception as e:
        return {"status": f"Error: {str(e)}"}
