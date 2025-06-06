from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.db import database, metadata, engine
from app.auth_routes import require_admin
from app.update_realms import update_realms_in_db
from app.templates_env import templates

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)

@router.get("", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin.html", {"request": request})

@router.post("/clear_realms")
async def clear_realms():
    await database.execute("DELETE FROM realms;")
    return {"status": "Realms cleared"}

@router.post("/clear_scans")
async def clear_scans():
    await database.execute("DELETE FROM auction_snapshots;")
    await database.execute("DELETE FROM snapshot_sessions;")
    return {"status": "Scans cleared"}

@router.post("/update_realms")
async def update_realms_route():
    await update_realms_in_db()
    return {"status": "Realms updated"}

@router.post("/update_tables")
async def update_tables():
    metadata.create_all(engine)
    return {"status": "Tables updated"}
