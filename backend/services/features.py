from __future__ import annotations
import uuid
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models import FeatureDef, FeatureEntity, FeatureValue

async def ensure_entity(session: AsyncSession, name: str, description: str = "") -> FeatureEntity:
    name = name.strip().lower()
    row = (await session.execute(select(FeatureEntity).where(FeatureEntity.name == name))).scalar_one_or_none()
    if row:
        return row
    row = FeatureEntity(id=uuid.uuid4().hex[:10], name=name, description=description)
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def register_feature(
    session: AsyncSession, entity_name: str, name: str, dtype: str = "float", lineage: str = ""
) -> FeatureDef:
    await ensure_entity(session, entity_name)
    fd = FeatureDef(
        id=uuid.uuid4().hex[:10],
        entity_name=entity_name.strip().lower(),
        name=name.strip().lower(),
        dtype=dtype,
        lineage=lineage,
    )
    session.add(fd)
    await session.commit()
    await session.refresh(fd)
    return fd

async def set_value(
    session: AsyncSession, entity_name: str, entity_key: str, feature_name: str, value: float
) -> FeatureValue:
    entity_name = entity_name.strip().lower()
    feature_name = feature_name.strip().lower()
    row = (
        await session.execute(
            select(FeatureValue).where(
                FeatureValue.entity_name == entity_name,
                FeatureValue.entity_key == entity_key,
                FeatureValue.feature_name == feature_name,
            )
        )
    ).scalar_one_or_none()
    if row:
        row.value = float(value)
        row.updated_at = datetime.utcnow()
    else:
        row = FeatureValue(
            id=uuid.uuid4().hex[:12],
            entity_name=entity_name,
            entity_key=entity_key,
            feature_name=feature_name,
            value=float(value),
        )
        session.add(row)
    await session.commit()
    await session.refresh(row)
    return row

async def get_online(session: AsyncSession, entity_name: str, entity_key: str) -> dict:
    rows = list(
        (
            await session.execute(
                select(FeatureValue).where(
                    FeatureValue.entity_name == entity_name.lower(),
                    FeatureValue.entity_key == entity_key,
                )
            )
        ).scalars()
    )
    return {r.feature_name: r.value for r in rows}

async def list_defs(session: AsyncSession) -> list[FeatureDef]:
    return list((await session.execute(select(FeatureDef))).scalars())

async def list_entities(session: AsyncSession) -> list[FeatureEntity]:
    return list((await session.execute(select(FeatureEntity))).scalars())
