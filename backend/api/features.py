from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db import get_db
from backend.services import features as svc

class EntityIn(BaseModel):
    name: str = Field(min_length=2)
    description: str = ""

class DefIn(BaseModel):
    entity_name: str
    name: str
    dtype: str = "float"
    lineage: str = ""

class ValueIn(BaseModel):
    entity_name: str
    entity_key: str
    feature_name: str
    value: float

router = APIRouter()

@router.post("/entities")
async def entities(payload: EntityIn, db: AsyncSession = Depends(get_db)):
    e = await svc.ensure_entity(db, payload.name, payload.description)
    return {"id": e.id, "name": e.name}

@router.get("/entities")
async def list_entities(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_entities(db)
    return {"entities": [{"id": e.id, "name": e.name} for e in rows]}

@router.post("/defs")
async def defs(payload: DefIn, db: AsyncSession = Depends(get_db)):
    f = await svc.register_feature(db, payload.entity_name, payload.name, payload.dtype, payload.lineage)
    return {"id": f.id}

@router.get("/defs")
async def list_defs(db: AsyncSession = Depends(get_db)):
    rows = await svc.list_defs(db)
    return {"defs": [{"id": f.id, "entity_name": f.entity_name, "name": f.name, "lineage": f.lineage} for f in rows]}

@router.post("/values")
async def set_value(payload: ValueIn, db: AsyncSession = Depends(get_db)):
    v = await svc.set_value(db, payload.entity_name, payload.entity_key, payload.feature_name, payload.value)
    return {"id": v.id, "value": v.value}

@router.get("/online")
async def online(entity_name: str = Query(...), entity_key: str = Query(...), db: AsyncSession = Depends(get_db)):
    return {"features": await svc.get_online(db, entity_name, entity_key)}
