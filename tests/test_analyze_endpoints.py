"""The endpoint analyzer: membership from the registry, coverage, no partial verdicts."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest
import yaml

_SPEC = importlib.util.spec_from_file_location(
    "_flygi_endpoints", Path(__file__).resolve().parents[1] / "scripts" / "analyze_endpoints.py"
)
module = importlib.util.module_from_spec(_SPEC)
sys.modules["_flygi_endpoints"] = module
_SPEC.loader.exec_module(module)


GAMES = [f"g{i:02d}" for i in range(6)]


def _rows(condition: str, games: list[str], score: float) -> list[dict]:
    return [
        {
            "seed": seed,
            "game_id": f"{game}-deadbeef",
            "condition": condition,
            "official": {"score": score, "levels_completed": 0},
            "final_levels_completed": 1 if score > 0.2 else 0,
        }
        for seed in (0, 1)
        for game in games
    ]


@pytest.fixture()
def arena(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    results = tmp_path / "results"
    results.mkdir()
    monkeypatch.setattr(module, "RESULTS", results)
    monkeypatch.setattr(module, "REGISTRY", tmp_path / "EXPERIMENTS.yaml")
    (tmp_path / "EXPERIMENTS.yaml").write_text(
        yaml.safe_dump(
            {
                "endpoints": {
                    "clicky": {"games": GAMES[:4]},
                    "full_25": {"games": GAMES},
                },
                "experiments": {
                    "base": {"baseline": None},
                    "treat": {
                        "baseline": "base",
                        "preregistered_endpoints": {"primary": "clicky"},
                    },
                },
            }
        )
    )
    return tmp_path


def _bundle(arena: Path, condition: str, rows: list[dict]) -> None:
    (arena / "results" / f"{condition}.json").write_text(
        json.dumps({"condition": condition, "rows": rows})
    )


def test_membership_comes_from_the_registry_and_both_endpoints_report(arena: Path) -> None:
    _bundle(arena, "base", _rows("base", GAMES, 0.1))
    _bundle(arena, "treat", _rows("treat", GAMES, 0.4))
    report = module.analyze("treat", resamples=300)
    assert set(report["results"]) == {"clicky", "full_25"}, (
        "primary and full set must ship together"
    )
    assert report["results"]["clicky"]["games"] == 4
    assert report["results"]["full_25"]["verdict"] == "HELPS"


def test_incomplete_coverage_refuses_a_verdict(arena: Path) -> None:
    _bundle(arena, "base", _rows("base", GAMES, 0.1))
    _bundle(arena, "treat", _rows("treat", GAMES[:3], 0.4))  # a clicky game missing
    report = module.analyze("treat", resamples=300)
    assert report["results"]["clicky"]["verdict"] == "NO VERDICT"
    assert "incomplete coverage" in report["results"]["clicky"]["reason"]


def test_a_checkpoint_is_not_a_result(arena: Path) -> None:
    _bundle(arena, "base", _rows("base", GAMES, 0.1))
    (arena / "results" / "treat.rows.jsonl").write_text("{}")
    with pytest.raises(module.EndpointError, match="checkpoint is not a result"):
        module.analyze("treat", resamples=100)
