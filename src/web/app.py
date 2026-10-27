"""Stage 4/5 — Render + Personalize entrypoints (FastAPI).

"Shape" — Interactive Defensive Positioning Trainer. The client drags the
ball and runs its own deterministic shape physics (see static/app.js); this
server is only called once per "moment" (drag end / periodic tick), never
per frame, to run the rubric-compliance pipeline: Interpret (DuckDB) ->
Explain (local template / Foundry) -> Render (Adaptive Card) -> Personalize
(coach/player/fan).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.agent import agent_runner
from src.analytics import metrics

app = FastAPI(title="Shape — Defensive Positioning Trainer")

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

_CARD_COLOR = {"red": "Attention", "yellow": "Warning", "green": "Good"}


class PointIn(BaseModel):
    x: float
    y: float


class DefenderIn(BaseModel):
    id: str
    x: float
    y: float


class MomentIn(BaseModel):
    scenario_id: str = "central_overload"
    ball: PointIn
    defenders: list[DefenderIn]
    persona: str = "coach"


@app.get("/")
def index():
    index_html = STATIC_DIR / "index.html"
    if index_html.exists():
        return FileResponse(index_html)
    return {"status": "skeleton", "hint": "static/index.html missing"}


@app.get("/healthz")
def healthz():
    """Liveness — process is up."""
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    """Readiness — seed data loads and DuckDB answers a query."""
    try:
        metrics.list_scenarios()
    except Exception as exc:  # surfaced as 503, not swallowed
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {"status": "ready"}


@app.get("/api/scenarios")
def api_scenarios():
    """List the seeded starting formations (ingest stage)."""
    scenarios = metrics.list_scenarios()
    return {"scenarios": [metrics.get_scenario(s["scenario_id"]) for s in scenarios]}


@app.get("/api/metrics")
def api_metrics(scenario_id: str = Query("central_overload"), persona: str = Query("coach")):
    """Interpret stage over a scenario's *starting* formation."""
    try:
        scenario = metrics.get_scenario(scenario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    facts = metrics.compute_facts({"ball": scenario["ball"], "defenders": scenario["defenders"]})
    response: dict[str, Any] = {"scenario_id": scenario_id, "flag": facts["flag"]}
    if persona == "coach":
        response["facts"] = facts
    return response


@app.post("/api/chat")
def api_chat(moment: MomentIn):
    """Interpret + Explain + Render for one dragged "moment"."""
    try:
        facts = metrics.compute_facts(
            {
                "ball": moment.ball.model_dump(),
                "defenders": [d.model_dump() for d in moment.defenders],
            }
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    explanation = agent_runner.explain(facts, persona=moment.persona)
    return {
        "scenario_id": moment.scenario_id,
        "sentence": explanation["sentence"],
        "flag": explanation["flag"],
        "facts": explanation.get("facts"),
        "card": _render_card(explanation["sentence"], explanation["label"], explanation["flag"]),
    }


def _render_card(sentence: str, label: str, flag: str) -> dict[str, Any]:
    return {
        "type": "AdaptiveCard",
        "version": "1.6",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "body": [
            {
                "type": "TextBlock",
                "text": label,
                "weight": "Bolder",
                "size": "Medium",
                "color": _CARD_COLOR[flag],
            },
            {"type": "TextBlock", "text": sentence, "wrap": True},
        ],
    }
