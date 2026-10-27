"""Unit tests for the Ingest + Interpret stages — real seeded formations."""
from src.analytics import metrics
from src.ingest import loader


def test_load_and_write_parquet(tmp_path):
    out = loader.load_and_write_parquet(output_dir=tmp_path)
    assert out.exists()
    assert out.name == "formations.parquet"


def test_list_scenarios_returns_seeded_formations():
    scenario_ids = {s["scenario_id"] for s in metrics.list_scenarios()}
    assert {"central_overload", "wide_overlap", "counter_numbers_up"} <= scenario_ids


def test_get_scenario_returns_ball_and_defenders():
    scenario = metrics.get_scenario("central_overload")
    assert scenario["ball"] == {"x": 52.5, "y": 34.0}
    assert len(scenario["defenders"]) == 4


def test_get_scenario_unknown_id_raises():
    try:
        metrics.get_scenario("not-a-real-scenario")
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown scenario_id")


def test_compute_facts_detects_biggest_gap():
    moment = {
        "ball": {"x": 52.5, "y": 34.0},
        "defenders": [
            {"id": "d1", "x": 88.0, "y": 10.0},
            {"id": "d2", "x": 90.0, "y": 26.0},
            {"id": "d3", "x": 90.0, "y": 50.0},  # 24m gap vs d2 — the widest
            {"id": "d4", "x": 88.0, "y": 58.0},
        ],
    }
    facts = metrics.compute_facts(moment)
    assert facts["biggest_gap_m"] == 24.0
    assert set(facts["gap_between"]) == {"d2", "d3"}
    assert facts["flag"] == "red"


def test_compute_facts_tight_line_is_green():
    moment = {
        "ball": {"x": 52.5, "y": 34.0},
        "defenders": [
            {"id": "d1", "x": 88.0, "y": 24.0},
            {"id": "d2", "x": 88.0, "y": 30.0},
            {"id": "d3", "x": 88.0, "y": 36.0},
            {"id": "d4", "x": 88.0, "y": 42.0},
        ],
    }
    facts = metrics.compute_facts(moment)
    assert facts["flag"] == "green"
    assert facts["presser_distance_m"] > 0


def test_compute_facts_requires_at_least_two_defenders():
    try:
        metrics.compute_facts({"ball": {"x": 1, "y": 1}, "defenders": [{"id": "d1", "x": 2, "y": 2}]})
    except ValueError:
        return
    raise AssertionError("expected ValueError for fewer than two defenders")
