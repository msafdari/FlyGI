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
from collections import Counter
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


def _policy_summary(records: list[Any], *, decision_seed: int | None = None) -> dict[str, Any]:
    """Behavioral diagnostics that remain informative when the score is zero."""

    if not records:
        return {"turns": 0, "decision_seed": decision_seed}
    readout_std = np.asarray([record.readout_std for record in records], dtype=np.float64)
    state_mean = np.asarray([record.state_mean_abs for record in records], dtype=np.float64)
    changed = np.asarray([record.changed_cells for record in records], dtype=np.float64)
    decided = [record for record in records if not record.forced_reset]
    ties = sum(1 for record in decided if not record.argmax_unique)
    sampled = [
        record for record in decided if getattr(record, "action_entropy_bits", None) is not None
    ]
    action_entropies = np.asarray(
        [record.action_entropy_bits for record in sampled], dtype=np.float64
    )
    selected_probabilities = np.asarray(
        [record.action_probability for record in sampled], dtype=np.float64
    )
    coordinates = [
        (int(record.coordinate_x), int(record.coordinate_y))
        for record in records
        if getattr(record, "coordinate_x", None) is not None
        and getattr(record, "coordinate_y", None) is not None
    ]
    coordinate_methods = Counter(
        str(record.coordinate_method)
        for record in records
        if getattr(record, "coordinate_method", None) is not None
    )
    loop_records = [
        record for record in records if getattr(record, "loop_escape_state_key", None) is not None
    ]
    selected_loop_biases = [
        float(record.loop_escape_selected_bias)
        for record in loop_records
        if getattr(record, "loop_escape_selected_bias", None) is not None
    ]
    return {
        "turns": len(records),
        "decision_seed": decision_seed,
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
        "sampler": {
            "sampled_turns": len(sampled),
            "mean_action_entropy_bits": (float(action_entropies.mean()) if sampled else None),
            "median_selected_action_probability": (
                float(np.median(selected_probabilities)) if sampled else None
            ),
        },
        "coordinates": {
            "draws": len(coordinates),
            "unique": len(set(coordinates)),
            "methods": dict(sorted(coordinate_methods.items())),
        },
        "graph_advanced_turns": sum(1 for record in records if record.graph_advanced),
        "loop_escape": {
            "enabled": bool(loop_records),
            "recorded_turns": len(loop_records),
            "revisited_decisions": sum(
                int(getattr(record, "loop_escape_attempts_before", 0) or 0) > 0
                for record in loop_records
            ),
            "prior_unchanged_failures": sum(
                bool(getattr(record, "loop_escape_prior_choice_failed", False))
                for record in loop_records
            ),
            "bias_changed_argmax_turns": sum(
                bool(getattr(record, "loop_escape_bias_changed_argmax", False))
                for record in loop_records
            ),
            "mean_selected_bias": (
                float(np.mean(selected_loop_biases)) if selected_loop_biases else None
            ),
        },
    }


def _attach_loop_escape_trace(records: list[Any], trace: list[dict[str, Any]]) -> None:
    """Persist every loop-memory input and bias beside the action it affected."""

    if len(records) != len(trace):
        raise RuntimeError(
            f"policy emitted {len(records)} records for {len(trace)} completed decisions"
        )
    for record, entry in zip(records, trace, strict=True):
        state_key = getattr(record, "loop_escape_state_key", None)
        if state_key is None:
            continue
        entry["loop_escape"] = {
            "state_key": state_key,
            "standardized_bias": list(record.loop_escape_standardized_bias),
            "selected_bias": record.loop_escape_selected_bias,
            "attempts_before": record.loop_escape_attempts_before,
            "unchanged_failures_before": record.loop_escape_unchanged_failures_before,
            "attempt_counts": list(record.loop_escape_attempt_counts),
            "unchanged_failure_counts": list(record.loop_escape_unchanged_failure_counts),
            "prior_choice_failed": record.loop_escape_prior_choice_failed,
            "bias_changed_argmax": record.loop_escape_bias_changed_argmax,
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
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="append each completed row here; pass the same path with --resume",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="skip (seed, game) rows already present in --checkpoint",
    )
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
    decision_rng = dict(interface["decision_rng"])
    decision_rng.pop("seed", None)
    decision_rng.update(
        {
            "seed_policy": "derived independently for each experiment-seed/game row",
            "per_row_seed_field": "rows[].policy_diagnostics.decision_seed",
        }
    )
    interface["decision_rng"] = decision_rng
    print(
        f"loaded {bundle.node_count:,} nodes / {bundle.edge_count:,} edges | "
        f"sensory {assembled.sensory_indices.size} | readout {assembled.readout_indices.size} | "
        f"K={assembled.policy.internal_steps} | ablated={bool(args.ablate_graph)}",
        flush=True,
    )

    def policy_factory(policy_seed: int) -> Any:
        # A fresh policy per row implements "reset neural state on a new
        # environment"; the graph and projection objects are reused unchanged.
        fresh = build_connectome_policy(
            config,
            runtime.GameAction,
            runtime_dir=args.runtime_dir,
            bundle=bundle,
            projection=projection,
            ablate_graph=bool(args.ablate_graph),
            internal_steps=args.internal_steps,
            decision_seed=policy_seed,
        )
        policy_factory.current = fresh.policy  # type: ignore[attr-defined]
        return fresh.policy

    # A laptop sleeps, crashes and reboots, and a full matrix is hours of work.
    # Each completed row is appended immediately so an interrupted run resumes
    # from where it stopped instead of discarding everything.
    checkpoint = args.checkpoint
    if checkpoint is None and args.output is not None:
        checkpoint = args.output.with_suffix(".rows.jsonl")
    elif checkpoint is None:
        checkpoint = DEFAULT_RESULTS_DIR / f"{args.condition}.rows.jsonl"

    rows: list[dict[str, Any]] = []
    done: set[tuple[int, str]] = set()
    if args.resume and checkpoint.is_file():
        for line in checkpoint.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            saved = json.loads(line)
            rows.append(saved)
            done.add((int(saved["seed"]), str(saved["game_id"])))
        print(f"resumed {len(rows)} completed rows from {checkpoint}", flush=True)

    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    for seed in args.seeds:
        for game in games:
            if (seed, game.game_id) in done:
                continue
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
            records = list(current.records) if current is not None else []
            _attach_loop_escape_trace(records, row["trace"])
            row["policy_diagnostics"] = _policy_summary(
                records,
                decision_seed=(current.decision_seed if current is not None else None),
            )
            rows.append(row)
            with checkpoint.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True) + "\n")
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
    overall = summaries.get("overall", {})
    print(json.dumps({"output": str(output), "gate": gate}, indent=2, sort_keys=True))
    print(f"mean score={overall.get('mean_score')} max={overall.get('max_score')} rows={len(rows)}")
    return 0 if gate.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
