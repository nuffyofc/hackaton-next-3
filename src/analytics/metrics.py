"""Stage 2 — Interpret.

Every number here comes from a DuckDB query over the submitted defender/ball
snapshot. The client's drag physics are deterministic geometry too, but this
module is the rubric-compliance boundary: nothing downstream (Explain) is
allowed to compute or guess a number — it only narrates what's here.
"""
from __future__ import annotations

from typing import Any

from src.analytics import db

GAP_FLAG_YELLOW_M = 10.0
GAP_FLAG_RED_M = 18.0


def list_scenarios() -> list[dict[str, Any]]:
    """Return the seeded starting formations (ingest-sourced, via DuckDB)."""
    return db.query("SELECT DISTINCT scenario_id, scenario_name FROM formations ORDER BY scenario_id")


def get_scenario(scenario_id: str) -> dict[str, Any]:
    """Return one named formation's starting ball + defender positions."""
    rows = db.query(
        "SELECT scenario_name, scenario_description, role, entity_id, x, y "
        "FROM formations WHERE scenario_id = ?",
        [scenario_id],
    )
    if not rows:
        raise ValueError(f"Unknown scenario_id: {scenario_id}")
    ball = next(r for r in rows if r["role"] == "ball")
    defenders = [r for r in rows if r["role"] == "defender"]
    return {
        "scenario_id": scenario_id,
        "scenario_name": rows[0]["scenario_name"],
        "scenario_description": rows[0]["scenario_description"],
        "ball": {"x": ball["x"], "y": ball["y"]},
        "defenders": [{"id": d["entity_id"], "x": d["x"], "y": d["y"]} for d in defenders],
    }


def shape_flag(biggest_gap_m: float) -> str:
    if biggest_gap_m >= GAP_FLAG_RED_M:
        return "red"
    if biggest_gap_m >= GAP_FLAG_YELLOW_M:
        return "yellow"
    return "green"


def compute_facts(moment: dict[str, Any]) -> dict[str, Any]:
    """Score one "moment": `{"ball": {"x","y"}, "defenders": [{"id","x","y"}, ...]}`.

    Returns compactness_m (avg pairwise defender distance), the biggest
    adjacent gap between neighbours ordered along the line, and how far the
    nearest defender (the presser) is standing off the ball. All three are
    plain DuckDB SQL over the snapshot — add domain-specific formulas here,
    never in the explain stage.
    """
    ball = moment["ball"]
    defenders = moment["defenders"]
    if len(defenders) < 2:
        raise ValueError("Need at least two defenders to score a shape")

    con = db.connect()
    try:
        con.execute("CREATE OR REPLACE TEMP TABLE moment_defenders(id VARCHAR, x DOUBLE, y DOUBLE)")
        con.executemany(
            "INSERT INTO moment_defenders VALUES (?, ?, ?)",
            [(d["id"], float(d["x"]), float(d["y"])) for d in defenders],
        )
        con.execute("CREATE OR REPLACE TEMP TABLE moment_ball(x DOUBLE, y DOUBLE)")
        con.execute("INSERT INTO moment_ball VALUES (?, ?)", [float(ball["x"]), float(ball["y"])])

        (compactness_m,) = con.execute(
            """
            SELECT avg(sqrt(pow(a.x - b.x, 2) + pow(a.y - b.y, 2)))
            FROM moment_defenders a, moment_defenders b
            WHERE a.id <> b.id
            """
        ).fetchone()

        presser_id, presser_distance_m = con.execute(
            """
            SELECT d.id, sqrt(pow(d.x - b.x, 2) + pow(d.y - b.y, 2)) AS dist
            FROM moment_defenders d, moment_ball b
            ORDER BY dist ASC
            LIMIT 1
            """
        ).fetchone()

        gap_row = con.execute(
            """
            WITH ordered AS (
                SELECT id, y, row_number() OVER (ORDER BY y) AS rn
                FROM moment_defenders
            )
            SELECT o_low.id, o_high.id, (o_high.y - o_low.y) AS gap_m
            FROM ordered o_low
            JOIN ordered o_high ON o_high.rn = o_low.rn + 1
            ORDER BY gap_m DESC
            LIMIT 1
            """
        ).fetchone()
    finally:
        con.close()

    biggest_gap_m = round(gap_row[2], 2) if gap_row else 0.0
    facts: dict[str, Any] = {
        "compactness_m": round(compactness_m, 2),
        "presser_id": presser_id,
        "presser_distance_m": round(presser_distance_m, 2),
        "biggest_gap_m": biggest_gap_m,
        "gap_between": [gap_row[0], gap_row[1]] if gap_row else None,
        "defender_count": len(defenders),
    }
    facts["flag"] = shape_flag(biggest_gap_m)
    return facts
