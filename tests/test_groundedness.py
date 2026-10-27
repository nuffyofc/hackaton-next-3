"""Groundedness — explain() must only narrate precomputed facts, never invent numbers."""
from src.agent import agent_runner
from src.analytics import metrics


def _facts_for(ball, defenders):
    return metrics.compute_facts({"ball": ball, "defenders": defenders})


def test_explain_fan_persona_omits_raw_facts():
    facts = _facts_for(
        {"x": 52.5, "y": 34.0},
        [
            {"id": "d1", "x": 88.0, "y": 24.0},
            {"id": "d2", "x": 88.0, "y": 30.0},
            {"id": "d3", "x": 88.0, "y": 36.0},
            {"id": "d4", "x": 88.0, "y": 42.0},
        ],
    )
    result = agent_runner.explain(facts, persona="fan")
    assert "facts" not in result
    assert result["flag"] == facts["flag"]
    assert isinstance(result["sentence"], str) and result["sentence"]


def test_explain_coach_persona_includes_raw_facts():
    facts = _facts_for(
        {"x": 52.5, "y": 34.0},
        [
            {"id": "d1", "x": 88.0, "y": 10.0},
            {"id": "d2", "x": 90.0, "y": 26.0},
            {"id": "d3", "x": 90.0, "y": 50.0},
            {"id": "d4", "x": 88.0, "y": 58.0},
        ],
    )
    result = agent_runner.explain(facts, persona="coach")
    assert result["facts"] == facts


def test_explain_sentence_cites_the_same_gap_number_as_the_facts():
    facts = _facts_for(
        {"x": 52.5, "y": 34.0},
        [
            {"id": "d1", "x": 88.0, "y": 10.0},
            {"id": "d2", "x": 90.0, "y": 26.0},
            {"id": "d3", "x": 90.0, "y": 50.0},
            {"id": "d4", "x": 88.0, "y": 58.0},
        ],
    )
    result = agent_runner.explain(facts, persona="fan")
    assert str(facts["biggest_gap_m"]) in result["sentence"]
