# BUILD.md — Next Inside the Game MVP (`hackaton-next-3`)

Practical build guide for this folder. The app is still a **generic skeleton**; you pick the domain idea, then fill the four extension points. Reference copies of prior projects live under `_imported/` (do not treat that tree as the runtime app).

| Import bucket | Use for |
|---|---|
| `_imported/from-coach-desk/` | Working Coach Training Desk patterns: env template, `azure.yaml`, Adaptive Card template, empty package `__init__.py`s |
| `_imported/from-premier-kopija/` | Fuller azd/`azure.yaml` + `infra/main.parameters.json`, MVP `_template` agent stubs, richer `.env.example` (placeholders only) |
| `_imported/from-hackatonfiles/` | Skeleton instructions, `PROJECT_SPEC_TEMPLATE.md`, project1–5 `.env.example` / `azure.yaml`, **project4 Player Lens stubs** (`NotImplementedError`) |

**Do not copy or commit real secrets.** Use empty templates only. Ignore any real `.env` under `_imported/` if present.

---

## What to build

A single FastAPI service that runs **offline-first** and follows the mandatory pipeline:

1. **Ingest** — synthetic or local JSON/Parquet (`src/ingest/`)
2. **Interpret** — deterministic DuckDB metrics (`src/analytics/`)
3. **Explain** — grounded narrative from facts only (`src/agent/`); local template first, Foundry later
4. **Render** — dashboard + Adaptive Cards 1.6 (`src/web/`)
5. **Personalize** — persona toggle (e.g. coach / player / fan)

**Lean MVP features (implement these):**

- Health endpoints: `/healthz`, `/readyz`
- One clear UI workflow (visual-first, not a raw data dump)
- Deterministic numbers in DuckDB **before** any LLM text
- Local explain path that never invents stats
- Persona switch on API + UI
- Tests that hit real seed data (`pytest`)
- Optional later: Azure ACA via Bicep/`azd` (keyless managed identity)

Fill a short pitch with `_imported/from-hackatonfiles/PROJECT_SPEC_TEMPLATE.md` before coding domain logic.

---

## Setup

Requirements: **Python 3.12** (not 3.14 — DuckDB/pydantic wheels), PowerShell, optional Azure CLI + `azd` + Docker for deploy.

```powershell
cd C:\Users\mike\Desktop\hackaton-next-3

& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

Dependencies (already in `requirements.txt`): FastAPI, uvicorn, duckdb, pydantic, pytest. Azure SDKs stay commented until Foundry is wired.

---

## Environment (safe templates only)

```powershell
copy .env.example .env
# optional: compare richer placeholder lists (still no secrets):
#   _imported\from-coach-desk\.env.example
#   _imported\from-premier-kopija\.env.example
#   _imported\from-hackatonfiles\project1\.env.example
```

Leave Azure values **blank** for offline mode. When you later enable cloud explain, set only placeholders you own, for example:

| Variable | Purpose |
|---|---|
| `AZURE_AI_PROJECT_ENDPOINT` | Foundry project endpoint (Coach Desk / skeleton style) |
| `AZURE_AI_MODEL_DEPLOYMENT` | Deployed model name |
| `FOUNDRY_KNOWLEDGE_BASE_NAME` | Optional knowledge base name |
| `ALLOWED_CIDRS` | Ingress allow-list for ACA (deploy-time) |

Prefer **DefaultAzureCredential / managed identity** over API keys. Do not paste keys from `_imported/from-premier-kopija/.env` into this project.

---

## Run the dev server

After stubs are filled enough to boot:

```powershell
.\demo\scripts\demo.ps1 local
# same as:
.\.venv\Scripts\python.exe -m uvicorn src.web.app:app --reload --port 8080
```

Open http://127.0.0.1:8080

```powershell
.\demo\scripts\demo.ps1 test    # pytest
.\demo\scripts\demo.ps1 check   # az bicep build on infra/
```

---

## Implementation order (extension points)

1. **Spec** — complete `PROJECT_SPEC_TEMPLATE` for your idea; check anti-patterns in hackatonfiles docs if needed.
2. **Ingest** — `src/ingest/loader.py` (+ optional `seed.py`). For a sensor-style idea, mirror shapes in `_imported/from-hackatonfiles/project4/src/ingest/seed.py`.
3. **Analytics** — `src/analytics/db.py` + `metrics.py`: real SQL/math, form flags / readiness, no LLM.
4. **Explain** — `src/agent/agent_runner.py`: implement `_explain_local` first (facts only). Keep Foundry behind env flag.
5. **UI / cards** — `src/web/app.py` + `src/web/static/`; start from `_imported/from-coach-desk/src/web/static/card_template.json` or project5’s copy.
6. **Prompts / tools** — fill `prompts/system_prompt_v1.txt` and `prompts/tool_definitions.json` when the agent path is ready.
7. **Verify** — pytest green; curl `/healthz`, `/readyz`, and your main `/api/...` routes with real seed data.

Coach Desk (`hackaton-next-2`) is the best end-to-end reference for UI + session/squad patterns. Premier `_imported/.../mvps/_template/` is useful for agent/MCP stub shape. Project4 stubs show the expected “raise until implemented” skeleton style.

---

## Deploy (when the offline MVP works)

1. Align root `azure.yaml` with a working example (`_imported/from-coach-desk/azure.yaml` or premier’s).
2. Validate: `az bicep build --file infra/main.bicep`
3. `azd env new <name>` → set location/subscription → `azd up` (Docker required).
4. Keep Foundry optional until the subscription has model access; app must still run with local explain.

See `docs/DEPLOYMENT.md` and imported `infra/main.parameters.json` files for parameter shape (env name, location — no secrets).

---

## Done when

- [ ] Idea + scope written (spec template)
- [ ] Seed data + DuckDB metrics return real numbers
- [ ] Local explain + Adaptive Card / UI demo path works offline
- [ ] `pytest` passes; health/ready endpoints OK
- [ ] Persona toggle works
- [ ] (Optional) ACA deploy healthy without embedding credentials in git
