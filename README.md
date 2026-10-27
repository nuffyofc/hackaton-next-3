# Generic Hackathon Skeleton

Domain-agnostic starter for a Microsoft × Premier League "Inside the Game"
style build. Scaffolded from `CLAUDE_GENERIC_SKELETON_INSTRUCTIONS.md`.

**Status:** empty starter — no domain logic yet. Fill the four extension points
once you choose an idea:

1. `src/ingest/loader.py` — data schema & ingest
2. `src/analytics/metrics.py` — deterministic math / SQL
3. `src/agent/` + `prompts/` — tools & system prompt
4. `src/web/static/` — Adaptive Cards / UI

## Stack

- Python 3.12, FastAPI, DuckDB over Parquet
- Adaptive Cards 1.6
- Azure: Bicep (ACA + Foundry + Entra ID managed identity)
- Offline-first: local template explain until Foundry endpoint is set

## 5-stage pipeline

| Stage | Module |
|---|---|
| Ingest | `src/ingest/loader.py` |
| Interpret | `src/analytics/` |
| Explain | `src/agent/` |
| Render | `src/web/` |
| Personalize | persona param (wire when implementing) |

## Local setup (when you are ready)

```powershell
# Use Python 3.12 (not 3.14) for duckdb/pydantic wheels
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\demo\scripts\demo.ps1 local
```

Do not run until domain stubs are filled.
