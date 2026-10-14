from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import features as svc

router = APIRouter()
templates = Jinja2Templates(directory="backend/templates")

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, entity_name: str = "user", entity_key: str = "u1", db: AsyncSession = Depends(get_db)):
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Feature Store Mini",
            "entities": await svc.list_entities(db),
            "defs": await svc.list_defs(db),
            "online": await svc.get_online(db, entity_name, entity_key),
            "entity_name": entity_name,
            "entity_key": entity_key,
        },
    )

@router.post("/ui/entities")
async def ui_e(name: str = Form(...), description: str = Form(""), db: AsyncSession = Depends(get_db)):
    await svc.ensure_entity(db, name, description)
    return RedirectResponse("/", status_code=303)

@router.post("/ui/defs")
async def ui_d(entity_name: str = Form(...), name: str = Form(...), lineage: str = Form(""), db: AsyncSession = Depends(get_db)):
    await svc.register_feature(db, entity_name, name, lineage=lineage)
    return RedirectResponse("/", status_code=303)

@router.post("/ui/values")
async def ui_v(entity_name: str = Form(...), entity_key: str = Form(...), feature_name: str = Form(...), value: float = Form(...), db: AsyncSession = Depends(get_db)):
    await svc.set_value(db, entity_name, entity_key, feature_name, value)
    return RedirectResponse(f"/?entity_name={entity_name}&entity_key={entity_key}", status_code=303)
