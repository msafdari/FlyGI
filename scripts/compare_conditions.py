#!/usr/bin/env python3
"""Compare FlyGI result bundles as matched pairs and print an honest table.

Takes two or more immutable result artifacts, treats the first as the reference,
and reports every other condition against it on identical ``(seed, game)`` rows.
Uncertainty is clustered on the game, never on the row, because a deterministic
policy produces identical traces across seeds and would otherwise claim evidence
it does not have.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

METRICS = ("score", "levels_completed", "unique_observations", "action_entropy_bits")


def _load(path: Path) -> tuple[str, list[dict[str, Any]], dict[str, Any]]:
    document = json.loads(path.read_text(encoding="utf-8"))
    label = str(
        document.get("condition") or document.get("parameters", {}).get("policy") or path.stem
    )
    return label, list(document["rows"]), document


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", type=Path, nargs="+", help="reference first")
    parser.add_argument("--metrics", nargs="+", default=list(METRICS))
    parser.add_argument("--budget", type=int, default=None, help="for censored summaries")
    parser.add_argument("--resamples", type=int, default=10_000)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    if len(args.artifacts) < 2:
        raise SystemExit("give at least two artifacts; the first is the reference")

    from flygi.evaluation import censored_summary, compare, extract_metric

    loaded = [_load(path) for path in args.artifacts]
    reference_label, reference_rows, _ = loaded[0]

    print(f"reference: {reference_label}  ({len(reference_rows)} rows)\n")
    header = f"{'condition':<26}" + "".join(f"{m[:18]:>20}" for m in args.metrics)
    print(header)
    for label, rows, _ in loaded:
        line = f"{label:<26}"
        for metric in args.metrics:
            values = [extract_metric(r, metric) for r in rows]
            line += f"{sum(values) / max(len(values), 1):20.6f}"
        print(line)

    comparisons: list[dict[str, Any]] = []
    for label, rows, _ in loaded[1:]:
        print(f"\n--- {label} minus {reference_label} ---")
        for metric in args.metrics:
            try:
                result = compare(rows, reference_rows, metric=metric, resamples=args.resamples)
            except Exception as exc:
                print(f"  {metric:<24} could not be compared: {exc}")
                continue
            record = {"condition": label, **result.as_dict()}
            comparisons.append(record)
            print(
                f"  {metric:<24} mean_diff={result.mean_difference:+.6f}  "
                f"95% CI [{result.bootstrap_low:+.6f}, {result.bootstrap_high:+.6f}]  "
                f"p={result.permutation_p:.4f}  nonzero_games={result.nonzero_clusters}"
                f"/{result.clusters}"
            )
            for warning in result.warnings:
                print(f"      ! {warning}")

    censored: dict[str, Any] = {}
    if args.budget:
        print(f"\n--- actions to completion, right-censored at {args.budget} ---")
        for label, rows, _ in loaded:
            summary = censored_summary(rows, budget=args.budget)
            censored[label] = summary
            print(
                f"  {label:<26} completed={summary['completed']}/{summary['rows']}  "
                f"rate={summary['completion_rate']:.3f}  "
                f"restricted_mean={summary['restricted_mean_actions']:.1f}  "
                f"completer_only={summary['completer_only_mean_actions']}"
            )

    if args.output:
        payload = {
            "schema": "flygi.paired-comparison",
            "created_at": datetime.now(UTC).isoformat(),
            "reference": reference_label,
            "artifacts": [str(p) for p in args.artifacts],
            "comparisons": comparisons,
            "censored": censored,
            "uncertainty_clustered_on": "game",
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"\nwrote {args.output}")
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("compare_conditions", main))
