#!/usr/bin/env python3
"""Run the closed-loop FlyGI connectome agent on cached public ARC games.

This is Gate 2. It reuses the Gate 0 evaluator's harness unchanged -- the same
strict-offline arcade, the same exact action ceiling, the same legality and
coordinate checks, the same immutable result contract -- and swaps only the
policy. Matched ``(game, seed)`` rows are therefore directly comparable with the
random chance control.

One loaded graph serves every row. The runtime bundle is hash-verified once and
the sensory projection is built once, so the interface is provably identical
across rows and, when ``--runtime-dir`` points at a null, across graph
conditions.

A positive score is not a pass criterion. This gate checks that the agent
survives every public game without an exception, illegal action, invalid
coordinate, or budget violation, and it records what the fly actually did.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

DEFAULT_CONFIG = ROOT / "configs/literal_rate_signed.yaml"
DEFAULT_RESULTS_DIR = ROOT / "results" / "connectome_agent"
SCHEMA = "flygi.connectome-agent"


def _load_baseline_module() -> ModuleType:
    """Import the Gate 0 evaluator so its harness is reused, not reimplemented."""

    path = ROOT / "scripts" / "evaluate_random_baseline.py"
    spec = importlib.util.spec_from_file_location("_flygi_baseline_evaluator", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    # Register before executing: dataclasses resolve cls.__module__ through
    # sys.modules, and slots=True fails on an unregistered module.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASELINE = _load_baseline_module()


def _policy_summary(records: list[Any]) -> dict[str, Any]:
    """Behavioral diagnostics that remain informative when the score is zero."""

    if not records:
        return {"turns": 0}
    readout_std = np.asarray([record.readout_std for record in records], dtype=np.float64)
    state_mean = np.asarray([record.state_mean_abs for record in records], dtype=np.float64)
    changed = np.asarray([record.changed_cells for record in records], dtype=np.float64)
    decided = [record for record in records if not record.forced_reset]
    ties = sum(1 for record in decided if not record.argmax_unique)
    return {
        "turns": len(records),
        "decided_turns": len(decided),
        "forced_resets": len(records) - len(decided),
        "silent_readout_turns": sum(1 for record in records if record.readout_silent),
        "argmax_ties": ties,
        "argmax_tie_rate": ties / len(decided) if decided else None,
        "readout_std": {
            "min": float(readout_std.min()),
            "median": float(np.median(readout_std)),
            "max": float(readout_std.max()),
        },
        "state_mean_abs": {
            "first": float(state_mean[0]),
            "median": float(np.median(state_mean)),
            "last": float(state_mean[-1]),
            "max": float(state_mean.max()),
        },
        "changed_cells": {
            "median": float(np.median(changed)),
            "max": float(changed.max()),
            "zero_change_turns": int(np.count_nonzero(changed == 0)),
        },
        "graph_advanced_turns": sum(1 for record in records if record.graph_advanced),
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument(
        "--runtime-dir",
        type=Path,
        default=None,
        help="compiled runtime to evaluate; defaults to the config's graph.output_dir",
    )
    parser.add_argument("--condition", default="real", help="label recorded in the result")
    parser.add_argument("--seeds", type=int, nargs="+", required=True)
    parser.add_argument("--games", nargs="+", default=["all"])
    parser.add_argument("--action-budget", type=int, default=80)
    parser.add_argument("--internal-steps", type=int, default=None)
    parser.add_argument(
        "--ablate-graph",
        action="store_true",
        help="preregistered control: keep the interface, remove the graph's contribution",
    )
    parser.add_argument("--environments-dir", type=Path, default=BASELINE.DEFAULT_ENVIRONMENTS_DIR)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.action_budget <= 0:
        raise SystemExit("--action-budget must be positive")
    if len(set(args.seeds)) != len(args.seeds):
        raise SystemExit("--seeds must not contain duplicates")

    from flygi.arc.factory import build_connectome_policy
    from flygi.config import load_config

    config = load_config(args.config)
    runtime = BASELINE.load_arc_runtime()
    try:
        games = BASELINE.discover_games(runtime, args.environments_dir.resolve(), args.games)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    # Build once. Every row and every graph condition shares this interface.
    assembled = build_connectome_policy(
        config,
        runtime.GameAction,
        runtime_dir=args.runtime_dir,
        ablate_graph=bool(args.ablate_graph),
        internal_steps=args.internal_steps,
    )
    bundle = assembled.bundle
    projection = assembled.projection
    interface = assembled.describe()
    print(
        f"loaded {bundle.node_count:,} nodes / {bundle.edge_count:,} edges | "
        f"sensory {assembled.sensory_indices.size} | readout {assembled.readout_indices.size} | "
        f"K={assembled.policy.internal_steps} | ablated={bool(args.ablate_graph)}",
        flush=True,
    )

    def policy_factory(policy_seed: int) -> Any:
        # A fresh policy per row implements "reset neural state on a new
        # environment"; the graph and projection objects are reused unchanged.
        del policy_seed
        fresh = build_connectome_policy(
            config,
            runtime.GameAction,
            runtime_dir=args.runtime_dir,
            bundle=bundle,
            projection=projection,
            ablate_graph=bool(args.ablate_graph),
            internal_steps=args.internal_steps,
        )
        policy_factory.current = fresh.policy  # type: ignore[attr-defined]
        return fresh.policy

    rows: list[dict[str, Any]] = []
    for seed in args.seeds:
        for game in games:
            policy_factory.current = None  # type: ignore[attr-defined]
            row = BASELINE.evaluate_one(
                runtime,
                game,
                seed,
                args.action_budget,
                args.environments_dir.resolve(),
                policy_factory=policy_factory,
                extra_row_fields={"condition": args.condition},
            )
            current = getattr(policy_factory, "current", None)
            row["policy_diagnostics"] = _policy_summary(
                list(current.records) if current is not None else []
            )
            rows.append(row)
            official = row.get("official") or {}
            print(
                f"  {game.game_id} seed={seed} status={row['status']} "
                f"score={official.get('score')} levels={official.get('levels_completed')} "
                f"actions={row['actions_completed']} "
                f"entropy={row['action_entropy_bits']:.3f}",
                flush=True,
            )

    replay_check = BASELINE._deterministic_replay_check(
        runtime,
        games,
        args.seeds,
        args.action_budget,
        args.environments_dir.resolve(),
        rows,
        policy_factory=policy_factory,
    )
    result = BASELINE.build_result(
        games=games,
        seeds=args.seeds,
        action_budget=args.action_budget,
        rows=rows,
        replay_check=replay_check,
        schema=SCHEMA,
        policy_label="flygi-connectome-literal",
        extra={
            "condition": args.condition,
            "interface": interface,
            "config_path": str(args.config),
            "config_sha256": BASELINE.sha256_file(args.config),
            "runtime_dir": str(
                args.runtime_dir if args.runtime_dir is not None else config.graph.output_dir
            ),
            "ablate_graph": bool(args.ablate_graph),
        },
    )
    output = args.output or (
        DEFAULT_RESULTS_DIR
        / f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S.%fZ')}-{args.condition}.json"
    )
    BASELINE.write_json_exclusive(output, result)

    gate = result["checks"]["gate"]
    summaries = result["summaries"]
    print(json.dumps({"output": str(output), "gate": gate}, indent=2, sort_keys=True))
    print(
        f"mean score={summaries.get('mean_score')} "
        f"max={summaries.get('max_score')} rows={len(rows)}"
    )
    return 0 if gate.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
