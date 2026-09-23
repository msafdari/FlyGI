#!/usr/bin/env python3
"""The handoff's 12-point artifact validation for one condition.

uv run python scripts/validate_closure.py sg-bioeye-t4t5 --baseline sg-t4t5
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "connectome_agent"
EXPECTED_SEEDS = {0, 1, 2}


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("condition")
    parser.add_argument("--baseline", default=None)
    args = parser.parse_args(argv)

    bundle_path = RESULTS / f"{args.condition}.json"
    checkpoint_path = RESULTS / f"{args.condition}.rows.jsonl"
    problems: list[str] = []
    bundle = json.loads(bundle_path.read_text())
    rows = bundle["rows"]

    keys = [(r["seed"], r["game_id"]) for r in rows]
    duplicate = [k for k, c in Counter(keys).items() if c > 1]
    games = {str(r["game_id"]).split("-")[0] for r in rows}
    seeds = {r["seed"] for r in rows}
    if len(rows) != 75:
        problems.append(f"rows={len(rows)} not 75")
    if duplicate:
        problems.append(f"duplicate keys: {duplicate[:3]}")
    if seeds != EXPECTED_SEEDS:
        problems.append(f"seeds={sorted(seeds)}")
    if len(games) != 25:
        problems.append(f"games={len(games)} not 25")
    bad = [r for r in rows if r.get("status") != "success" or r.get("failure")]
    if bad:
        problems.append(f"{len(bad)} non-success rows")
    illegal = sum(int(r.get("illegal_action_count") or 0) for r in rows)
    if illegal:
        problems.append(f"illegal actions: {illegal}")
    over = [r for r in rows if (r.get("actions_completed") or 0) > (r.get("action_budget") or 600)]
    if over:
        problems.append(f"{len(over)} rows over budget")
    hashes = {r.get("replay_trace_sha256") for r in rows}
    seed_diverse = len(hashes) == len(rows)

    coverage = None
    if args.baseline:
        base = json.loads((RESULTS / f"{args.baseline}.json").read_text())["rows"]
        base_keys = {(r["seed"], r["game_id"]) for r in base}
        missing = [k for k in keys if k not in base_keys]
        coverage = f"matched {len(keys) - len(missing)}/{len(keys)}"
        if missing:
            problems.append(f"baseline missing {len(missing)} keys")

    report = {
        "condition": args.condition,
        "bundle": str(bundle_path),
        "bundle_sha256": sha(bundle_path),
        "checkpoint_sha256": sha(checkpoint_path) if checkpoint_path.exists() else None,
        "rows": len(rows),
        "seed_diverse_traces": seed_diverse,
        "baseline_coverage": coverage,
        "problems": problems,
        "PASS": not problems,
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not problems else 1


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("validate_closure", main))
