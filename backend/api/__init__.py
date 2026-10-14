from fastapi import APIRouter
from backend.api import health, features, ui
api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(features.router, prefix="/api", tags=["features"])
api_router.include_router(ui.router, tags=["ui"])
