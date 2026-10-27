"""Stage 3 — Explain.

Local template by default; Foundry Agent when AZURE_AI_PROJECT_ENDPOINT is
set. Either path only narrates the facts dict produced by
src.analytics.metrics.compute_facts — it never computes or guesses a number.
"""
from __future__ import annotations

import os
from typing import Any

FLAG_LABELS = {
    "red": "Gap open",
    "yellow": "Shape stretching",
    "green": "Shape holding",
}


def explain(facts: dict[str, Any], persona: str = "fan") -> dict[str, Any]:
    """Grounded narrative from precomputed facts only.

    Flow: User drags ball -> DuckDB facts (Interpret) -> this function
    (Explain) -> Adaptive Card / UI panel (Render).
    """
    if os.getenv("AZURE_AI_PROJECT_ENDPOINT"):
        return _explain_with_foundry(facts, persona=persona)
    return _explain_local(facts, persona=persona)


def _explain_local(facts: dict[str, Any], persona: str) -> dict[str, Any]:
    """Deterministic offline template — no LLM, no numbers invented."""
    flag = facts["flag"]
    gap = facts["biggest_gap_m"]
    compactness = facts["compactness_m"]
    presser_distance = facts["presser_distance_m"]
    gap_between = facts.get("gap_between") or []
    gap_desc = " and ".join(gap_between) if gap_between else "the back line"

    if flag == "red":
        sentence = (
            f"That's a {gap}m gap between {gap_desc} — a clear lane through, "
            f"even with the presser only {presser_distance}m off the ball."
        )
    elif flag == "yellow":
        sentence = (
            f"Shape is stretching: {gap}m has opened between {gap_desc}, "
            f"worth tightening before it's exploited."
        )
    else:
        sentence = (
            f"Shape is holding — defenders stay {compactness}m apart on "
            f"average and no gap is wider than {gap}m."
        )

    result: dict[str, Any] = {"sentence": sentence, "flag": flag, "label": FLAG_LABELS[flag]}
    if persona == "coach":
        result["facts"] = facts
    return result


def _explain_with_foundry(facts: dict[str, Any], persona: str) -> dict[str, Any]:
    """Azure AI Foundry path via DefaultAzureCredential (shared pass later)."""
    raise NotImplementedError("Wire Foundry Agent after offline path works")
