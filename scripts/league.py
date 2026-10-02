#!/usr/bin/env python3
"""The experiment league: what helps, what hurts, what is still running.

Joins three sources that already exist -- immutable result bundles, live
checkpoint files, and `EXPERIMENTS.yaml` -- into one table. The registry owns
the *why* (baseline, regime, hypothesis); the artifacts own every number. This
tool derives; it never stores, so it cannot drift from reality.

    uv run python scripts/league.py               # the table
    uv run python scripts/league.py --hypotheses  # hypothesis statuses
    uv run python scripts/league.py --json        # machine-readable everything
    uv run python scripts/league.py --write-md LEAGUE.md

Reading rules, learned the hard way and enforced here:

- A verdict (HELPS / HURTS / null) is issued only for COMPLETE matched pairs,
  from the clustered bootstrap CI on score. Partial runs get a delta labelled
  `partial:` and no verdict: this repository once read +10.6% off a 41-row
  seed-ordered partial that the full matrix erased entirely.
- Comparisons cross regimes only when one side is `controller-only` (which uses
  no connectome). A gain0.9 number is a measurement of a numerically dead
  network and is never a baseline for a live one.
- A bundle whose condition is not registered is listed loudly at the bottom.
  Unregistered experiments are how ablation records rot.
"""

from __future__ import annotations

import argparse
import gzip
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "EXPERIMENTS.yaml"
RESULTS = ROOT / "results" / "connectome_agent"
RUNNING_IF_TOUCHED_WITHIN_S = 30 * 60


def _read_text(path: Path) -> str:
    # Result files over 10MB are gzipped in place to save disk (WORKLOG
    # operational note, 2026-09-28/30); read both forms transparently.
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            return handle.read()
    return path.read_text()


def _result_paths(pattern: str) -> list[Path]:
    return sorted([*RESULTS.glob(pattern), *RESULTS.glob(pattern + ".gz")])


def _load_bundles() -> dict[str, dict[str, Any]]:
    bundles: dict[str, dict[str, Any]] = {}
    for path in _result_paths("*.json"):
        try:
            bundle = json.loads(_read_text(path))
        except (OSError, EOFError, json.JSONDecodeError):
            continue
        condition = bundle.get("condition") or (bundle.get("parameters") or {}).get("condition")
        if not condition or "rows" not in bundle:
            continue
        # Keep the newest bundle per condition; older ones remain on disk.
        bundles[str(condition)] = {"path": path, "bundle": bundle}
    return bundles


def _load_checkpoints() -> dict[str, dict[str, Any]]:
    checkpoints: dict[str, dict[str, Any]] = {}
    for path in _result_paths("*.rows.jsonl"):
        rows: list[dict[str, Any]] = []
        try:
            for line in _read_text(path).splitlines():
                if line.strip():
                    rows.append(json.loads(line))
        except (OSError, EOFError, json.JSONDecodeError):
            continue
        if not rows:
            continue
        stem = path.name.removesuffix(".gz").removesuffix(".rows.jsonl")
        condition = str(rows[0].get("condition", stem))
        age = time.time() - path.stat().st_mtime
        checkpoints[condition] = {"path": path, "rows": rows, "age_s": age}
    return checkpoints


def _summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    scores = [float((r.get("official") or {}).get("score") or 0.0) for r in rows]
    return {
        "rows": len(rows),
        "mean_score": sum(scores) / max(len(scores), 1),
        "levels": sum(int(r.get("final_levels_completed") or 0) for r in rows),
        "progress_games": len(
            {r["game_id"] for r in rows if (r.get("final_levels_completed") or 0) > 0}
        ),
        "seeds": sorted({r.get("seed") for r in rows}),
    }


def _matched_delta(rows: list[dict], base_rows: list[dict]) -> dict[str, Any] | None:
    base = {(r.get("seed"), r.get("game_id")): r for r in base_rows}
    pairs = [(base[k], r) for r in rows if (k := (r.get("seed"), r.get("game_id"))) in base]
    if not pairs:
        return None
    d_score = sum(
        float((b.get("official") or {}).get("score") or 0.0)
        - float((a.get("official") or {}).get("score") or 0.0)
        for a, b in pairs
    ) / len(pairs)
    d_levels = sum(
        int(b.get("final_levels_completed") or 0) - int(a.get("final_levels_completed") or 0)
        for a, b in pairs
    )
    return {"pairs": len(pairs), "delta_score": d_score, "delta_levels": d_levels}


def _full_comparison(rows: list[dict], base_rows: list[dict], resamples: int) -> dict[str, Any]:
    from flygi.evaluation import compare

    result = compare(rows, base_rows, metric="score", resamples=resamples)
    verdict = "null"
    if result.bootstrap_low > 0:
        verdict = "HELPS"
    elif result.bootstrap_high < 0:
        verdict = "HURTS"
    return {
        "delta_score": result.mean_difference,
        "ci_low": result.bootstrap_low,
        "ci_high": result.bootstrap_high,
        "p": result.permutation_p,
        "verdict": verdict,
    }


def build_league(resamples: int = 5000) -> dict[str, Any]:
    registry = yaml.safe_load(REGISTRY.read_text())
    bundles = _load_bundles()
    checkpoints = _load_checkpoints()
    experiments = registry.get("experiments", {})
    entries: list[dict[str, Any]] = []

    def rows_for(condition: str) -> tuple[list[dict], str]:
        if condition in bundles:
            return bundles[condition]["bundle"]["rows"], "complete"
        if condition in checkpoints:
            fresh = checkpoints[condition]["age_s"] < RUNNING_IF_TOUCHED_WITHIN_S
            return checkpoints[condition]["rows"], ("running" if fresh else "stale")
        return [], "missing"

    for condition, spec in experiments.items():
        rows, status = rows_for(condition)
        if spec.get("status_override"):
            status = str(spec["status_override"])
        entry: dict[str, Any] = {
            "condition": condition,
            "regime": spec.get("regime"),
            "baseline": spec.get("baseline"),
            "tests": list(spec.get("tests") or []),
            "status": status,
            "note": spec.get("note", "").strip(),
            **(_summary(rows) if rows else {"rows": 0}),
        }
        baseline = spec.get("baseline")
        if baseline and rows:
            base_rows, base_status = rows_for(baseline)
            base_spec = experiments.get(baseline, {})
            cross = spec.get("regime") != base_spec.get("regime") and "controller-only" not in (
                spec.get("regime"),
                base_spec.get("regime"),
            )
            if cross:
                entry["comparison"] = {"warning": "cross-regime; not compared"}
            elif base_rows:
                if status == "complete" and base_status == "complete":
                    try:
                        entry["comparison"] = _full_comparison(rows, base_rows, resamples)
                    except Exception as exc:
                        entry["comparison"] = {"warning": f"compare failed: {exc}"}
                else:
                    delta = _matched_delta(rows, base_rows)
                    if delta:
                        entry["comparison"] = {
                            **delta,
                            "verdict": "partial",
                            "warning": "seed-ordered partial; biased sample, no verdict",
                        }
        entries.append(entry)

    registered = set(experiments)
    unregistered = sorted(set(bundles) - registered - {c for c in bundles if c.startswith("probe")})
    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "entries": entries,
        "hypotheses": registry.get("hypotheses", {}),
        "regimes": registry.get("regimes", {}),
        "unregistered_conditions": unregistered,
    }


def _fmt_comparison(comparison: dict[str, Any] | None) -> str:
    if not comparison:
        return ""
    if "warning" in comparison and "verdict" not in comparison:
        return comparison["warning"]
    if comparison.get("verdict") == "partial":
        return (
            f"partial: {comparison['delta_score']:+.4f} ({comparison['pairs']} pairs, no verdict)"
        )
    return (
        f"{comparison['delta_score']:+.4f} "
        f"[{comparison['ci_low']:+.3f},{comparison['ci_high']:+.3f}] "
        f"p={comparison['p']:.3f} -> {comparison['verdict']}"
    )


def render_table(league: dict[str, Any]) -> str:
    lines = [
        f"{'condition':24} {'status':9} {'rows':>5} {'score':>9} {'lvl':>4} "
        f"{'vs baseline':38} baseline",
        "-" * 110,
    ]
    for entry in league["entries"]:
        lines.append(
            f"{entry['condition']:24} {entry['status']:9} {entry.get('rows', 0):>5} "
            f"{entry.get('mean_score', 0):>9.4f} {entry.get('levels', 0):>4} "
            f"{_fmt_comparison(entry.get('comparison')):38} {entry.get('baseline') or '-'}"
        )
    if league["unregistered_conditions"]:
        lines.append("")
        lines.append(
            "UNREGISTERED bundles (add to EXPERIMENTS.yaml or they rot): "
            + ", ".join(league["unregistered_conditions"])
        )
    return "\n".join(lines)


def render_hypotheses(league: dict[str, Any]) -> str:
    lines = [f"{'hypothesis':22} {'status':12} statement", "-" * 100]
    for name, spec in league["hypotheses"].items():
        statement = " ".join(str(spec.get("statement", "")).split())
        lines.append(f"{name:22} {spec.get('status')!s:12} {statement[:70]}")
        for item in spec.get("evidence", []):
            lines.append(f"{'':22} {'':12}   - {' '.join(str(item).split())[:80]}")
    return "\n".join(lines)


def render_markdown(league: dict[str, Any]) -> str:
    out = [
        "# Experiment league",
        "",
        f"Generated {league['generated_at']} by `scripts/league.py`. Do not edit;",
        "edit `EXPERIMENTS.yaml` and regenerate. Verdicts come from clustered",
        "bootstrap CIs on complete matched pairs only; partial runs never get one.",
        "",
        "| condition | regime | status | rows | score | levels | vs baseline | baseline |",
        "| --- | --- | --- | ---: | ---: | ---: | --- | --- |",
    ]
    for e in league["entries"]:
        out.append(
            f"| {e['condition']} | {e.get('regime', '')} | {e['status']} | {e.get('rows', 0)} "
            f"| {e.get('mean_score', 0):.4f} | {e.get('levels', 0)} "
            f"| {_fmt_comparison(e.get('comparison')) or '—'} | {e.get('baseline') or '—'} |"
        )
    out += ["", "## Hypotheses", ""]
    out += ["| id | status | statement |", "| --- | --- | --- |"]
    for name, spec in league["hypotheses"].items():
        statement = " ".join(str(spec.get("statement", "")).split())
        out.append(f"| {name} | {spec.get('status')} | {statement} |")
    if league["unregistered_conditions"]:
        out += ["", "**Unregistered bundles:** " + ", ".join(league["unregistered_conditions"])]
    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--hypotheses", action="store_true")
    parser.add_argument("--write-md", type=Path, default=None)
    parser.add_argument("--resamples", type=int, default=5000)
    args = parser.parse_args(argv)

    from flygi.telemetry import run_or_null

    telemetry = run_or_null()
    with telemetry.phase("league.build"):
        league = build_league(resamples=args.resamples)
    telemetry.info(
        "league.summary",
        experiments=len(league["entries"]),
        running=sum(1 for e in league["entries"] if e["status"] == "running"),
        complete=sum(1 for e in league["entries"] if e["status"] == "complete"),
        unregistered=len(league["unregistered_conditions"]),
    )

    if args.as_json:
        print(json.dumps(league, indent=2, sort_keys=True, default=str))
        return 0
    if args.write_md:
        args.write_md.write_text(render_markdown(league))
        print(f"wrote {args.write_md}")
    print(render_table(league))
    if args.hypotheses:
        print()
        print(render_hypotheses(league))
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("league", main))
