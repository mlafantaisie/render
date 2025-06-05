import os
from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from contextlib import asynccontextmanager

from app.auth import router as auth_router
from app.db import database, engine, metadata
from app import models
from app.snapshots import take_snapshot
from app.utils import format_price
from app.pagination import get_pagination_window

SECRET_KEY = os.getenv("SESSION_SECRET")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)
templates = Jinja2Templates(directory="app/templates")
templates.env.filters['format_price'] = format_price

app.include_router(auth_router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return HTMLResponse("Unauthorized", status_code=401)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/realm/{realm_id}", response_class=HTMLResponse)
async def realm_snapshots(request: Request, realm_id: int, page: int = 1):
    query = """
        SELECT id, scanned_at FROM snapshot_sessions 
        WHERE realm_id = :realm_id ORDER BY scanned_at DESC LIMIT 1
    """
    snapshot = await database.fetch_one(query, values={"realm_id": realm_id})
    if not snapshot:
        return HTMLResponse("No snapshots found", status_code=404)

    # Pagination setup
    page_size = 100
    offset = (page - 1) * page_size

    auction_query = """
        SELECT * FROM auction_snapshots
        WHERE snapshot_id = :snapshot_id
        ORDER BY id
        LIMIT :limit OFFSET :offset
    """
    auctions = await database.fetch_all(
        auction_query,
        values={"snapshot_id": snapshot.id, "limit": page_size, "offset": offset}
    )

    # Convert auctions to list of dicts
    auctions = [dict(row) for row in auctions]

    # Total count for pagination
    count_query = "SELECT COUNT(*) FROM auction_snapshots WHERE snapshot_id = :snapshot_id"
    total_count = await database.fetch_val(count_query, values={"snapshot_id": snapshot.id})
    total_pages = (total_count + page_size - 1) // page_size

    pagination = get_pagination_window(page, total_pages)
    
    return templates.TemplateResponse("realm.html", {
        "request": request,
        "realm_id": realm_id,
        "snapshot": dict(snapshot),
        "auctions": auctions,
        "page": page,
        "total_pages": total_pages,
        "pagination": pagination
    })

@app.get("/snapshots", response_class=HTMLResponse)
async def snapshots(request: Request):
    query = "SELECT realm_id, COUNT(*) as count FROM snapshot_sessions GROUP BY realm_id"
    rows = await database.fetch_all(query)

    # Convert rows to list of dicts for easy Jinja2 access
    realms = [dict(row) for row in rows]

    return templates.TemplateResponse("snapshots.html", {"request": request, "realms": realms})

# New route to take a snapshot manually
@app.post("/snapshot")
async def snapshot_post(request: Request, realm_id: int = Form(...)):
    await take_snapshot(realm_id)
    return HTMLResponse(f"Snapshot taken for realm {realm_id}", status_code=200)
