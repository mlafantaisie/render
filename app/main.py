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

@app.get("/snapshots", response_class=HTMLResponse)
async def snapshots(request: Request):
    query = "SELECT realm_id, COUNT(*) as count FROM snapshot_sessions GROUP BY realm_id"
    rows = await database.fetch_all(query)
    return templates.TemplateResponse("snapshots.html", {"request": request, "realms": rows})
