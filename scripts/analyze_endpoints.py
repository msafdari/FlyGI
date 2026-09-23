#!/usr/bin/env python3
"""Preregistered endpoint analysis for one treatment/baseline pair.

The smallest deterministic analyzer the ARC closure handoff asks for: it reads
the named endpoint definitions from `EXPERIMENTS.yaml` (never a duplicated
list), filters treatment and baseline to identical game identities, runs the
repository's game-clustered paired statistics, and always emits primary,
secondary, and full-set results together. It refuses a verdict when either
side's coverage of an endpoint is incomplete.

    uv run python scripts/analyze_endpoints.py sg-bioeye-lc-retdec
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "EXPERIMENTS.yaml"
RESULTS = ROOT / "results" / "connectome_agent"


class EndpointError(RuntimeError):
    pass


def load_rows(condition: str) -> list[dict[str, Any]]:
    bundle = RESULTS / f"{condition}.json"
    if not bundle.is_file():
        raise EndpointError(f"no final bundle for {condition}; a checkpoint is not a result")
    return json.loads(bundle.read_text())["rows"]


def base_game(row: dict[str, Any]) -> str:
    return str(row["game_id"]).split("-")[0]


def analyze(condition: str, resamples: int = 10_000) -> dict[str, Any]:
    registry = yaml.safe_load(REGISTRY.read_text())
    spec = registry["experiments"].get(condition)
    if not spec:
        raise EndpointError(f"{condition} is not registered")
    baseline = spec.get("baseline")
    if not baseline:
        raise EndpointError(f"{condition} declares no baseline")
    declared = spec.get("preregistered_endpoints") or {
        "primary": "full_25",
        "full_set": "reported_alongside",
    }
    endpoints = registry["endpoints"]

    treatment_rows = load_rows(condition)
    baseline_rows = load_rows(baseline)

    from flygi.evaluation import compare

    report: dict[str, Any] = {
        "condition": condition,
        "baseline": baseline,
        "declared": declared,
        "results": {},
    }
    names = [declared.get("primary"), declared.get("secondary"), "full_25"]
    for name in [n for n in names if n and n in endpoints]:
        games = set(endpoints[name]["games"])
        t = [r for r in treatment_rows if base_game(r) in games]
        b = [r for r in baseline_rows if base_game(r) in games]
        t_games = {base_game(r) for r in t}
        b_games = {base_game(r) for r in b}
        if t_games != games or b_games != games:
            report["results"][name] = {
                "verdict": "NO VERDICT",
                "reason": (
                    f"incomplete coverage: treatment has {len(t_games)}/{len(games)} games, "
                    f"baseline {len(b_games)}/{len(games)}"
                ),
            }
            continue
        result = compare(t, b, metric="score", resamples=resamples)
        verdict = "null"
        if result.bootstrap_low > 0:
            verdict = "HELPS"
        elif result.bootstrap_high < 0:
            verdict = "HURTS"
        report["results"][name] = {
            "games": len(games),
            "rows": len(t),
            "delta_score": result.mean_difference,
            "ci_low": result.bootstrap_low,
            "ci_high": result.bootstrap_high,
            "p": result.permutation_p,
            "levels_treatment": sum(int(r.get("final_levels_completed") or 0) for r in t),
            "levels_baseline": sum(int(r.get("final_levels_completed") or 0) for r in b),
            "verdict": verdict,
        }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition")
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)

    from flygi.telemetry import run_or_null

    report = analyze(args.condition, resamples=args.resamples)
    run_or_null().info(
        "endpoints.analyzed",
        condition=args.condition,
        verdicts={k: v.get("verdict") for k, v in report["results"].items()},
    )
    if args.as_json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    print(f"{report['condition']}  vs  {report['baseline']}")
    for name, res in report["results"].items():
        if res.get("verdict") == "NO VERDICT":
            print(f"  {name:>18}: NO VERDICT -- {res['reason']}")
            continue
        print(
            f"  {name:>18}: {res['delta_score']:+.4f} "
            f"[{res['ci_low']:+.3f},{res['ci_high']:+.3f}] p={res['p']:.3f} "
            f"levels {res['levels_treatment']} vs {res['levels_baseline']} -> {res['verdict']}"
        )
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("analyze_endpoints", main))
