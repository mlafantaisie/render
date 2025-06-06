from fastapi import APIRouter, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from datetime import datetime

from app.db import database
from app.models import auction_snapshots, snapshot_sessions, realms
from app.blizz_api import get_access_token, fetch_auction_data
from app.templates_env import templates
from app.utils import format_datetime

router = APIRouter()

CHUNK_SIZE = 500

# Register Jinja2 Jinja filters
templates.env.filters['format_datetime'] = format_datetime

# View list of all scans
@router.get("/scans", response_class=HTMLResponse)
async def scans(request: Request, scanned_realm_id: int = None):
    query = """
        SELECT s.realm_id, s.scanned_at, r.realm_name
        FROM snapshot_sessions s
        JOIN realms r ON s.realm_id = r.realm_id
        ORDER BY r.realm_name ASC
    """
    rows = await database.fetch_all(query)
    realms = [dict(row) for row in rows]

    message = None
    if scanned_realm_id:
        # Lookup realm name to show in message
        name_query = "SELECT realm_name FROM realms WHERE realm_id = :realm_id"
        realm_name = await database.fetch_val(name_query, values={"realm_id": scanned_realm_id})
        message = f"Scan completed for realm {realm_name}."

    return templates.TemplateResponse("scans.html", {
        "request": request,
        "realms": realms,
        "message": message
    })

# Form to launch a scan
@router.get("/scan_form", response_class=HTMLResponse)
async def scan_form(request: Request):
    query = "SELECT realm_id, realm_name FROM realms ORDER BY realm_name"
    rows = await database.fetch_all(query)
    realms = [dict(row) for row in rows]

    return templates.TemplateResponse("scan_form.html", {
        "request": request,
        "realms": realms
    })

# Initiate scan for selected realm
@router.post("/scan")
async def scan_post(request: Request, background_tasks: BackgroundTasks, realm_id: int = Form(...)):
    try:
        background_tasks.add_task(take_snapshot, realm_id)
        return RedirectResponse(url=f"/scans?scanned_realm_id={realm_id}", status_code=303)
    except Exception as e:
        print(f"Scan failed: {e}")
        return HTMLResponse(f"Failed to scan realm {realm_id}: {e}", status_code=500)

# Orchestrator function for full snapshot
async def take_snapshot(realm_id):
    print(f"Starting snapshot for realm {realm_id}")
    await save_snapshot(realm_id)

# Full snapshot saving logic (overwrite pattern)
async def save_snapshot(realm_id):
    # 1️⃣ Create or update snapshot session
    snapshot_query = """
        INSERT INTO snapshot_sessions (realm_id, scanned_at)
        VALUES (:realm_id, :scanned_at)
        ON CONFLICT (realm_id) DO UPDATE SET scanned_at = :scanned_at
        RETURNING id
    """
    values = {"realm_id": realm_id, "scanned_at": datetime.utcnow()}
    snapshot_id = await database.fetch_val(snapshot_query, values=values)

    # 2️⃣ Delete any existing auctions for this snapshot immediately
    delete_query = auction_snapshots.delete().where(auction_snapshots.c.snapshot_id == snapshot_id)
    await database.execute(delete_query)

    # 3️⃣ Fetch auction data from Blizzard API
    token = await get_access_token()
    data = await fetch_auction_data(realm_id, token)
    auctions = data.get('auctions', [])

    if not auctions:
        print(f"No auctions found for realm {realm_id}. Nothing to insert.")
        return

    # 4️⃣ Build auction values in batches and insert
    async with database.transaction():
        batch = []
        for auction in auctions:
            batch.append({
                "snapshot_id": snapshot_id,
                "auction_id": auction["id"],
                "item_id": auction["item"]["id"],
                "quantity": auction["quantity"],
                "unit_price": auction.get("unit_price", 0),
                "buyout": auction.get("buyout", 0),
                "time_left": auction.get("time_left", "")
            })

            if len(batch) >= CHUNK_SIZE:
                await database.execute_many(auction_snapshots.insert(), batch)
                batch = []  # reset batch

        # Insert any remaining rows after final batch
        if batch:
            await database.execute_many(auction_snapshots.insert(), batch)

    print(f"Snapshot completed for realm {realm_id} with {len(auctions)} auctions.")
