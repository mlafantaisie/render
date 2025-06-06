from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
import bcrypt

from app.models import users
from app.db import database
from app.templates_env import templates

router = APIRouter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_user(username: str):
    query = users.select().where(users.c.username == username)
    return await database.fetch_one(query)

async def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user

async def require_admin(request: Request):
    user = request.session.get("user")
    if not user or user.get("username") != "garguscrayzon":  # Replace 'admin' with your actual admin username if different
        raise HTTPException(status_code=401, detail="Admin access required")
    return user

@router.get("/login", response_class=HTMLResponse)
async def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    user = await get_user(username)
    if not user or not verify_password(password, user["password"]):
        return RedirectResponse("/login", status_code=303)
    request.session["user"] = dict(user)
    return RedirectResponse("/dashboard", status_code=303)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=303)
