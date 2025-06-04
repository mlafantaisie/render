from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from app.auth import router as auth_router
from app.db import database
from app.blizz_api import get_access_token, fetch_auction_data

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your_secret_key")
templates = Jinja2Templates(directory="app/templates")

app.include_router(auth_router)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return HTMLResponse("Unauthorized", status_code=401)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.post("/snapshot")
async def snapshot(realm_id: int, request: Request):
    access_token = await get_access_token()
    data = await fetch_auction_data(realm_id, access_token)
    # Process or save 'data' to DB later
    return {"status": "success", "auction_count": len(data.get('auctions', []))}

