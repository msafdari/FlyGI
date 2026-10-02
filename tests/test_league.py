"""The league must refuse the mistakes this project has already made.

The two that matter: issuing a verdict from a partial, seed-ordered run (a
41-row partial once showed +10.6% that the full matrix erased), and comparing
across operating regimes (a dead-network number is not a baseline for a live
one).
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

_SPEC = importlib.util.spec_from_file_location(
    "_flygi_league", Path(__file__).resolve().parents[1] / "scripts" / "league.py"
)
league_module = importlib.util.module_from_spec(_SPEC)
sys.modules["_flygi_league"] = league_module
_SPEC.loader.exec_module(league_module)


def _row(seed: int, game: str, score: float, levels: int, condition: str) -> dict:
    return {
        "seed": seed,
        "game_id": game,
        "condition": condition,
        "official": {"score": score, "levels_completed": levels},
        "final_levels_completed": levels,
    }


def _bundle(directory: Path, condition: str, rows: list[dict]) -> None:
    (directory / f"{condition}.json").write_text(json.dumps({"condition": condition, "rows": rows}))


@pytest.fixture()
def arena(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    results = tmp_path / "results"
    results.mkdir()
    registry = tmp_path / "EXPERIMENTS.yaml"
    monkeypatch.setattr(league_module, "RESULTS", results)
    monkeypatch.setattr(league_module, "REGISTRY", registry)
    return tmp_path


def _write_registry(arena: Path, experiments: dict) -> None:
    (arena / "EXPERIMENTS.yaml").write_text(
        yaml.safe_dump(
            {"schema_version": 1, "hypotheses": {}, "regimes": {}, "experiments": experiments}
        )
    )


GAMES = [f"g{i:02d}" for i in range(12)]


def test_complete_pairs_get_a_verdict_partials_never_do(arena: Path) -> None:
    results = arena / "results"
    base = [_row(s, g, 0.10, 0, "base") for s in (0, 1) for g in GAMES]
    better = [_row(s, g, 0.30, 1, "treat") for s in (0, 1) for g in GAMES]
    _bundle(results, "base", base)
    _bundle(results, "treat", better)
    # a partial: checkpoint only, half the rows
    partial_rows = better[: len(better) // 2]
    (results / "part.rows.jsonl").write_text(
        "\n".join(json.dumps({**r, "condition": "part"}) for r in partial_rows)
    )
    _write_registry(
        arena,
        {
            "base": {"regime": "live", "baseline": None, "tests": []},
            "treat": {"regime": "live", "baseline": "base", "tests": []},
            "part": {"regime": "live", "baseline": "base", "tests": []},
        },
    )
    league = league_module.build_league(resamples=500)
    by = {e["condition"]: e for e in league["entries"]}
    assert by["treat"]["comparison"]["verdict"] == "HELPS"
    assert by["part"]["comparison"]["verdict"] == "partial"
    assert "no verdict" in by["part"]["comparison"]["warning"]


def test_cross_regime_pairs_are_refused(arena: Path) -> None:
    results = arena / "results"
    _bundle(results, "dead", [_row(0, g, 0.5, 1, "dead") for g in GAMES])
    _bundle(results, "live", [_row(0, g, 0.1, 0, "live") for g in GAMES])
    _write_registry(
        arena,
        {
            "dead": {"regime": "gain0.9-dead", "baseline": None, "tests": []},
            "live": {"regime": "gain2.0", "baseline": "dead", "tests": []},
        },
    )
    league = league_module.build_league(resamples=500)
    by = {e["condition"]: e for e in league["entries"]}
    assert "cross-regime" in by["live"]["comparison"]["warning"]


def test_unregistered_bundles_are_surfaced(arena: Path) -> None:
    results = arena / "results"
    _bundle(results, "orphan", [_row(0, "g00", 0.1, 0, "orphan")])
    _write_registry(arena, {})
    league = league_module.build_league(resamples=100)
    assert league["unregistered_conditions"] == ["orphan"]


def test_the_real_registry_is_coherent() -> None:
    """Every baseline resolves, every tested hypothesis exists, statuses are legal."""

    registry = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "EXPERIMENTS.yaml").read_text()
    )
    experiments = registry["experiments"]
    hypotheses = registry["hypotheses"]
    legal = {"open", "null", "refuted", "supported", "invalidated", "retired"}
    for name, spec in hypotheses.items():
        assert spec.get("status") in legal, f"{name}: illegal status {spec.get('status')}"
        assert spec.get("statement"), f"{name}: no statement"
    for condition, spec in experiments.items():
        baseline = spec.get("baseline")
        assert baseline is None or baseline in experiments, f"{condition}: baseline {baseline}?"
        for hypothesis in spec.get("tests") or []:
            assert hypothesis in hypotheses, f"{condition}: unknown hypothesis {hypothesis}"
        assert spec.get("regime") in registry["regimes"], f"{condition}: unknown regime"


def test_gzipped_results_are_read_like_plain_ones(arena: Path) -> None:
    """Result files over 10MB are gzipped in place to save disk; the league
    must still see them, or a regeneration silently drops those arms."""

    import gzip

    results = arena / "results"
    rows = [_row(0, "g00", 0.5, 1, "zipped")]
    with gzip.open(results / "zipped.json.gz", "wt", encoding="utf-8") as handle:
        handle.write(json.dumps({"condition": "zipped", "rows": rows}))
    with gzip.open(results / "zipped-cp.rows.jsonl.gz", "wt", encoding="utf-8") as handle:
        handle.write(json.dumps(_row(0, "g00", 0.5, 1, "zipped-cp")) + "\n")
    _write_registry(arena, {"zipped-cp": {"regime": "r", "baseline": None}})
    league = league_module.build_league(resamples=100)
    assert "zipped" in league["unregistered_conditions"]
    by = {e["condition"]: e for e in league["entries"]}
    assert by["zipped-cp"]["rows"] == 1  # read from the gzipped checkpoint
