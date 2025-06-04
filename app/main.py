from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from app.auth import router as auth_router
from app.db import database, engine
from app.blizz_api import get_access_token, fetch_auction_data

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router)

@app.on_event("startup")
async def startup():
    # Connect and create tables
    await database.connect()
    metadata.create_all(engine)  # THIS will create tables if they don't exist

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return HTMLResponse("Unauthorized", status_code=401)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/realm/{realm_id}", response_class=HTMLResponse)
async def realm_snapshots(request: Request, realm_id: int):
    # Get latest snapshot
    query = f"""
        SELECT id, scanned_at FROM snapshot_sessions 
        WHERE realm_id = :realm_id ORDER BY scanned_at DESC LIMIT 1
    """
    snapshot = await database.fetch_one(query, values={"realm_id": realm_id})
    if not snapshot:
        return HTMLResponse("No snapshots found", status_code=404)

    auction_query = f"""
        SELECT * FROM auction_snapshots
        WHERE snapshot_id = :snapshot_id LIMIT 100
    """
    auctions = await database.fetch_all(auction_query, values={"snapshot_id": snapshot.id})
    
    return templates.TemplateResponse("realm.html", {
        "request": request,
        "realm_id": realm_id,
        "snapshot": snapshot,
        "auctions": auctions
    })

@app.get("/snapshots", response_class=HTMLResponse)
async def snapshots(request: Request):
    query = "SELECT realm_id, COUNT(*) as count FROM snapshot_sessions GROUP BY realm_id"
    rows = await database.fetch_all(query)
    return templates.TemplateResponse("snapshots.html", {"request": request, "realms": rows})
