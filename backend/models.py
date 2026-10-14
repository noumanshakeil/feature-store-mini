from __future__ import annotations
from datetime import datetime
from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.db import Base

def utcnow(): return datetime.utcnow()

class FeatureEntity(Base):
    __tablename__ = "feature_entities"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, default="")

class FeatureDef(Base):
    __tablename__ = "feature_defs"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    entity_name: Mapped[str] = mapped_column(String(80), index=True)
    name: Mapped[str] = mapped_column(String(80), index=True)
    dtype: Mapped[str] = mapped_column(String(32), default="float")
    lineage: Mapped[str] = mapped_column(Text, default="")

class FeatureValue(Base):
    __tablename__ = "feature_values"
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    entity_name: Mapped[str] = mapped_column(String(80), index=True)
    entity_key: Mapped[str] = mapped_column(String(80), index=True)
    feature_name: Mapped[str] = mapped_column(String(80), index=True)
    value: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)
