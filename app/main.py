import os
from fastapi import FastAPI, Request, Depends, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from contextlib import asynccontextmanager
from datetime import datetime

from app.auth_routes import router as auth_router, require_admin
from app.admin_routes import router as admin_router
from app.scan_routes import router as scan_router
from app.realm_routes import router as realm_router
from app.arbitrage_routes import router as arbitrage_router
from app.db import database, engine, metadata
from app import models
from app.scan_routes import take_snapshot
from app.utils import format_price
from app.pagination import get_pagination_window
from app.update_realms import update_realms_in_db
from app.templates_env import templates

SECRET_KEY = os.getenv("SESSION_SECRET")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(scan_router)
app.include_router(realm_router)
app.include_router(arbitrage_router)

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    user = request.session.get("user")
    if not user:
        return HTMLResponse("Unauthorized", status_code=401)
    return templates.TemplateResponse("dashboard.html", {"request": request})
