# Architecture — generic skeleton

Single FastAPI process implementing the mandatory 5-stage pipeline.
Domain logic not filled in yet.

```
Client
  │  GET /health  POST /api/metrics  POST /api/chat
  ▼
FastAPI (src/web/app.py)
  ├─ Ingest      src/ingest/loader.py
  ├─ Interpret   src/analytics/db.py + metrics.py   (DuckDB over Parquet)
  ├─ Explain     src/agent/agent_runner.py + mcp_tools.py
  ├─ Render      src/web/static/  (Adaptive Cards 1.6)
  └─ Personalize persona query param (wire when implementing)
```

Pillars: zero-hallucination DuckDB math, keyless Entra ID, Foundry agent
(optional offline template fallback), azure-ai-evaluation hooks in tests.
