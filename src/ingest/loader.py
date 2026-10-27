"""Stage 1 — Ingest.

"Shape" has no external data source: a handful of named starting defensive
formations are the seed data, expressed in the same 105m x 68m pitch
coordinate system as synthetic_data_and_azure_databases.md. They're written
to Parquet once so the Interpret stage reads them through DuckDB like any
other dataset, rather than importing a Python dict directly.

Every formation defends the same goal, at x=105 (the right edge) — the ball
always starts on the attacking (left) side of the defenders, so dragging it
toward x=105 is "attacking the goal."
"""
from __future__ import annotations

from pathlib import Path

import duckdb

PITCH_W = 105.0
PITCH_H = 68.0

# Defenders are listed back-to-front is not implied by order; only x/y matter.
SCENARIOS: dict[str, dict] = {
    "central_overload": {
        "name": "Central Overload",
        "description": "A striker drives straight at a flat back four — watch whether the presser opens a gap for the rest.",
        "ball": {"x": 52.5, "y": 34.0},
        "defenders": [
            {"id": "d1", "x": 88.0, "y": 10.0},
            {"id": "d2", "x": 90.0, "y": 26.0},
            {"id": "d3", "x": 90.0, "y": 42.0},
            {"id": "d4", "x": 88.0, "y": 58.0},
        ],
    },
    "wide_overlap": {
        "name": "Wide Overlap",
        "description": "The ball swings wide — see whether the back four slides across together or leaves the far side exposed.",
        "ball": {"x": 70.0, "y": 60.0},
        "defenders": [
            {"id": "d1", "x": 86.0, "y": 8.0},
            {"id": "d2", "x": 88.0, "y": 24.0},
            {"id": "d3", "x": 88.0, "y": 40.0},
            {"id": "d4", "x": 84.0, "y": 56.0},
        ],
    },
    "counter_numbers_up": {
        "name": "Counter-Attack Numbers-Up",
        "description": "Only three defenders are back to track a ball breaking forward — less cover, bigger gaps open faster.",
        "ball": {"x": 45.0, "y": 34.0},
        "defenders": [
            {"id": "d1", "x": 75.0, "y": 20.0},
            {"id": "d2", "x": 80.0, "y": 34.0},
            {"id": "d3", "x": 75.0, "y": 48.0},
        ],
    },
    "back_three_high_line": {
        "name": "Back Three — High Line",
        "description": "A back three holds a high line near halfway — aggressive, but thin if the ball slips past one of them.",
        "ball": {"x": 55.0, "y": 40.0},
        "defenders": [
            {"id": "d1", "x": 70.0, "y": 15.0},
            {"id": "d2", "x": 72.0, "y": 34.0},
            {"id": "d3", "x": 70.0, "y": 53.0},
        ],
    },
    "back_five_low_block": {
        "name": "Back Five — Low Block",
        "description": "Five defenders sit deep right in front of goal — the hardest shape to break open, but slow to press out.",
        "ball": {"x": 60.0, "y": 34.0},
        "defenders": [
            {"id": "d1", "x": 95.0, "y": 6.0},
            {"id": "d2", "x": 97.0, "y": 20.0},
            {"id": "d3", "x": 98.0, "y": 34.0},
            {"id": "d4", "x": 97.0, "y": 48.0},
            {"id": "d5", "x": 95.0, "y": 62.0},
        ],
    },
}


def load_and_write_parquet(
    source: Path | None = None,
    output_dir: Path | None = None,
) -> Path:
    """Write the seeded formations to Parquet; return the written file path.

    `source` is unused (no external file for this domain) but kept in the
    signature so this stays a drop-in replacement for a real loader.
    """
    output_dir = output_dir or Path(__file__).resolve().parents[2] / "data" / "sample"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows: list[tuple[str, str, str, str, str, float, float]] = []
    for scenario_id, scenario in SCENARIOS.items():
        ball = scenario["ball"]
        rows.append(
            (scenario_id, scenario["name"], scenario["description"], "ball", "ball", ball["x"], ball["y"])
        )
        for defender in scenario["defenders"]:
            rows.append(
                (
                    scenario_id,
                    scenario["name"],
                    scenario["description"],
                    "defender",
                    defender["id"],
                    defender["x"],
                    defender["y"],
                )
            )

    out_path = output_dir / "formations.parquet"
    con = duckdb.connect(database=":memory:")
    try:
        con.execute(
            """
            CREATE TABLE formations (
                scenario_id VARCHAR,
                scenario_name VARCHAR,
                scenario_description VARCHAR,
                role VARCHAR,
                entity_id VARCHAR,
                x DOUBLE,
                y DOUBLE
            )
            """
        )
        con.executemany("INSERT INTO formations VALUES (?, ?, ?, ?, ?, ?, ?)", rows)
        # COPY TO doesn't support a parameterized path; out_path is a local,
        # code-controlled path (not user input), so inlining it is safe.
        escaped_path = str(out_path).replace("'", "''")
        con.execute(f"COPY formations TO '{escaped_path}' (FORMAT PARQUET)")
    finally:
        con.close()
    return out_path
