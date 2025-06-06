from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime

from app.db import database
from app.models import auction_snapshots, snapshot_sessions
from app.blizz_api import get_access_token, fetch_auction_data
from app.templates_env import templates

router = APIRouter()

async def save_snapshot(realm_id, auctions):
    snapshot_query = """
        INSERT INTO snapshot_sessions (realm_id, scanned_at)
        VALUES (:realm_id, :scanned_at)
        ON CONFLICT (realm_id) DO UPDATE SET scanned_at = :scanned_at
        RETURNING id
    """
    values = {"realm_id": realm_id, "scanned_at": datetime.utcnow()}
    snapshot_id = await database.fetch_val(snapshot_query, values=values)

    delete_query = auction_snapshots.delete().where(auction_snapshots.c.snapshot_id == snapshot_id)
    await database.execute(delete_query)

    auction_values = [
        {
            "snapshot_id": snapshot_id,
            "auction_id": auction["id"],
            "item_id": auction["item"]["id"],
            "quantity": auction["quantity"],
            "unit_price": auction.get("unit_price", 0),
            "buyout": auction.get("buyout", 0),
            "time_left": auction.get("time_left", "")
        }
        for auction in auctions
    ]

    async with database.transaction():
        insert_query = auction_snapshots.insert()
        await database.execute_many(insert_query, auction_values)

async def take_snapshot(realm_id):
    token = await get_access_token()

    try:
        data = await fetch_auction_data(realm_id, token)
    except Exception as e:
        print(f"Failed to fetch auction data: {e}")
        raise  # Bubble up to fail the scan

    auctions = data.get('auctions', [])

    if not auctions:
        print(f"No auctions found for realm_id {realm_id}")
        # Optional: You could raise an error here too, if you want scans to only succeed if data is found

    await save_snapshot(realm_id, auctions)

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
        # Lookup realm name
        name_query = "SELECT realm_name FROM realms WHERE realm_id = :realm_id"
        realm_name = await database.fetch_val(name_query, values={"realm_id": scanned_realm_id})
        message = f"Scan completed for realm {realm_name}."

    return templates.TemplateResponse("scans.html", {
        "request": request,
        "realms": realms,
        "message": message
    })

@router.get("/scan_form", response_class=HTMLResponse)
async def scan_form(request: Request):
    query = "SELECT realm_id, realm_name FROM realms ORDER BY realm_name"
    rows = await database.fetch_all(query)
    realms = [dict(row) for row in rows]

    return templates.TemplateResponse("scan_form.html", {
        "request": request,
        "realms": realms
    })

@router.post("/scan")
async def scan_post(request: Request, realm_id: int = Form(...)):
    try:
        await take_snapshot(realm_id)
        return RedirectResponse(url=f"/scans?scanned_realm_id={realm_id}", status_code=303)
    except Exception as e:
        print(f"Scan failed: {e}")
        return HTMLResponse(f"Failed to scan realm {realm_id}: {e}", status_code=500)
