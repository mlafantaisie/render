from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from app.db import database
from app.models import snapshot_sessions, auction_snapshots
from app.pagination import get_pagination_window
from app.templates_env import templates

router = APIRouter()

# View auctions for a specific realm snapshot
@router.get("/realm/{realm_id}", response_class=HTMLResponse)
async def realm_snapshots(request: Request, realm_id: int, page: int = 1):
    # Get the most recent snapshot for this realm
    snapshot_query = """
        SELECT id, scanned_at FROM snapshot_sessions 
        WHERE realm_id = :realm_id ORDER BY scanned_at DESC LIMIT 1
    """
    snapshot = await database.fetch_one(snapshot_query, values={"realm_id": realm_id})
    if not snapshot:
        return HTMLResponse("No snapshots found", status_code=404)

    snapshot = dict(snapshot)
    snapshot_id = snapshot["id"]

    # Pagination setup
    page_size = 100
    offset = (page - 1) * page_size

    # Fetch paginated auctions
    auction_query = """
        SELECT a.id, a.item_id, i.name as item_name, a.quantity, a.unit_price, a.buyout, a.time_left
        FROM auction_snapshots a
        LEFT JOIN items i ON a.item_id = i.id
        WHERE a.snapshot_id = :snapshot_id
        ORDER BY a.id
        LIMIT :limit OFFSET :offset
    """
    auctions = await database.fetch_all(
        auction_query,
        values={"snapshot_id": snapshot_id, "limit": page_size, "offset": offset}
    )
    auctions = [dict(row) for row in auctions]

    # Count total for pagination
    count_query = "SELECT COUNT(*) FROM auction_snapshots WHERE snapshot_id = :snapshot_id"
    total_count = await database.fetch_val(count_query, values={"snapshot_id": snapshot_id})
    total_pages = (total_count + page_size - 1) // page_size

    pagination = get_pagination_window(page, total_pages)

    return templates.TemplateResponse("realm.html", {
        "request": request,
        "realm_id": realm_id,
        "snapshot": snapshot,
        "auctions": auctions,
        "page": page,
        "total_pages": total_pages,
        "pagination": pagination
    })
