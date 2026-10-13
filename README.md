# Feature Store Mini

Mini feature store with entity keys, online/offline views, and catalog UI.

## Stack

- **Backend:** FastAPI + Jinja UI (full-stack single service)
- **LLM:** mock provider by default; optional OpenAI / Ollama via env
- **Packaging:** Docker + docker-compose
- **Tests:** pytest API smoke tests

## Architecture

```text
Browser UI ──► FastAPI routes ──► domain store (JSON)
                   │
                   └──► llm.complete() (mock | openai | ollama)
```

## Quick start (local)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn backend.main:app --reload --port 8000
```

Open http://127.0.0.1:8000

## Docker

```bash
docker compose up --build
```

## API

- `GET /health`
- `GET /api/features`
- `POST /api/features`
- `POST /api/serve` — Serve online features for an entity key

## Tests

```bash
pytest -q
```

## Notes

Production-shaped learning app: real routes, UI, Docker, and tests. Swap `LLM_MODE=openai` or `ollama` when you have credentials/models.
