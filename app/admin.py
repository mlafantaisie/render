from fastapi import APIRouter, Depends
from app.db import database, metadata, engine
from app.auth import require_admin
from app.update_realms import update_realms_in_db

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)]
)

@router.post("/clear_realms")
async def clear_realms():
    await database.execute("TRUNCATE TABLE realms;")
    return {"status": "Realms cleared"}

@router.post("/update_realms")
async def update_realms_route():
    await update_realms_in_db()
    return {"status": "Realms updated"}

@router.post("/update_tables")
async def update_tables():
    metadata.create_all(engine)
    return {"status": "Tables updated"}
