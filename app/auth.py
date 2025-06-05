from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse
from app.models import users
from app.db import database
from starlette.responses import HTMLResponse
from starlette.templating import Jinja2Templates
import bcrypt

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

async def get_user(username: str):
    query = users.select().where(users.c.username == username)
    return await database.fetch_one(query)

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
