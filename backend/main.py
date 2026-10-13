"""Feature Store Mini — FastAPI backend + Jinja UI."""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .llm import complete

ROOT = Path(__file__).resolve().parent
DATA = ROOT.parent / "data" / "store.json"
FIELDS = ['entity', 'name', 'dtype']

app = FastAPI(title="Feature Store Mini", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")
templates = Jinja2Templates(directory=str(ROOT / "templates"))


def load_store() -> dict:
    if not DATA.exists():
        DATA.parent.mkdir(parents=True, exist_ok=True)
        payload = {"features": [
  {
    "id": "fs1",
    "entity": "user",
    "name": "orders_30d",
    "dtype": "int"
  }
]}
        DATA.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return json.loads(DATA.read_text(encoding="utf-8"))


def save_store(store: dict) -> None:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(store, indent=2), encoding="utf-8")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "feature-store-mini", "llm_mode": settings.llm_mode}


@app.get("/api/features")
def list_items() -> dict:
    store = load_store()
    return {"features": store.get("features", [])}


@app.post("/api/features")
def create_item(payload: dict) -> dict:
    store = load_store()
    item = {"id": uuid.uuid4().hex[:8]}
    for key in FIELDS:
        item[key] = payload.get(key)
    store.setdefault("features", []).insert(0, item)
    save_store(store)
    return item


@app.post("/api/serve")
def run_action(payload: dict) -> dict:
    """Serve online features for an entity key."""
    prompt = (
        "You are the AI engine for Feature Store Mini.\n"
        "Task: Serve online features for an entity key.\n"
        f"Input JSON: {json.dumps(payload)[:4000]}"
    )
    text = complete(prompt)
    return {"ok": True, "action": "serve", "result": text, "mode": settings.llm_mode}


@app.get("/", response_class=HTMLResponse)
def home(request: Request, last_result: str | None = None) -> HTMLResponse:
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Feature Store Mini",
            "description": "Mini feature store with entity keys, online/offline views, and catalog UI.",
            "resource": "features",
            "action": "serve",
            "action_desc": "Serve online features for an entity key",
            "items": store.get("features", []),
            "llm_mode": settings.llm_mode,
            "last_result": last_result,
        },
    )


@app.post("/ui/create", response_class=HTMLResponse)
async def ui_create(request: Request) -> HTMLResponse:
    form = await request.form()
    data = {k: form.get(k) for k in FIELDS}
    create_item(data)
    return home(request)


@app.post("/ui/action", response_class=HTMLResponse)
async def ui_action(request: Request, prompt: str = Form("demo")) -> HTMLResponse:
    result = run_action({"prompt": prompt})
    store = load_store()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Feature Store Mini",
            "description": "Mini feature store with entity keys, online/offline views, and catalog UI.",
            "resource": "features",
            "action": "serve",
            "action_desc": "Serve online features for an entity key",
            "items": store.get("features", []),
            "llm_mode": settings.llm_mode,
            "last_result": result.get("result"),
        },
    )
