from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from app.db import database, users
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
import hashlib

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def fake_hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

async def get_user(username: str):
    query = users.select().where(users.c.username == username)
    return await database.fetch_one(query)

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = await get_user(username)
    if not user or user["password"] != fake_hash_password(password):
        return RedirectResponse("/login", status_code=303)
    request.session["user"] = dict(user)
    return RedirectResponse("/dashboard", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
