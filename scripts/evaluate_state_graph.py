#!/usr/bin/env python3
"""Evaluate the generic controller on cached ARC-AGI-3 games.

The runner reuses Gate 0's strict-offline environment, exact action ceiling,
trace, scorecard, legality, coordinate, and deterministic-replay contracts.  It
changes only the policy factory.  No connectome assets or game identities are
available to the controller-only condition.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections.abc import Mapping, Sequence
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

DEFAULT_CONFIG = ROOT / "configs" / "state_graph_controller.yaml"
DEFAULT_FLY_CONFIG = ROOT / "configs" / "literal_rate_signed_nocentroid.yaml"
DEFAULT_RESULTS_DIR = ROOT / "results" / "state_graph_controller"
SCHEMA = "flygi.state-graph-controller"
RANDOM_500_MEAN_SCORE = 0.097568
MINIMUM_PROGRESS_GAMES = 3


def _load_baseline_module() -> ModuleType:
    path = ROOT / "scripts" / "evaluate_random_baseline.py"
    spec = importlib.util.spec_from_file_location("_flygi_controller_evaluator", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASELINE = _load_baseline_module()


def promotion_check(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Apply the frozen Phase 1 score gate to completed result rows."""

    official_rows = [row for row in rows if row.get("official") is not None]
    scores = [float(row["official"]["score"]) for row in official_rows]
    progress_games = sorted(
        {
            str(row["game_id"])
            for row in official_rows
            if int(row["official"]["levels_completed"]) > 0
        }
    )
    mean_score = fmean(scores) if scores else None
    issues: list[str] = []
    if mean_score is None:
        issues.append("no official score rows")
    elif mean_score <= RANDOM_500_MEAN_SCORE:
        issues.append(
            f"mean score {mean_score:.9f} did not exceed random {RANDOM_500_MEAN_SCORE:.6f}"
        )
    if len(progress_games) < MINIMUM_PROGRESS_GAMES:
        issues.append(
            f"progress appeared in {len(progress_games)} games; "
            f"required at least {MINIMUM_PROGRESS_GAMES}"
        )
    return {
        "passed": not issues,
        "issues": issues,
        "random_500_mean_score": RANDOM_500_MEAN_SCORE,
        "mean_score": mean_score,
        "minimum_progress_games": MINIMUM_PROGRESS_GAMES,
        "progress_games": progress_games,
    }


def _policy_diagnostics(policy: Any | None) -> dict[str, Any]:
    if policy is None:
        return {"available": False}
    diagnostics = getattr(policy, "diagnostics", None)
    if callable(diagnostics):
        result = diagnostics()
        if not isinstance(result, dict):
            raise TypeError("controller diagnostics() must return a dictionary")
        return {"available": True, **result}
    records = list(getattr(policy, "records", ()))
    return {"available": True, "turns": len(records)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--condition", default="controller-only")
    parser.add_argument("--seeds", type=int, nargs="+", required=True)
    parser.add_argument("--games", nargs="+", default=["all"])
    parser.add_argument("--action-budget", type=int, default=500)
    parser.add_argument("--environments-dir", type=Path, default=BASELINE.DEFAULT_ENVIRONMENTS_DIR)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument(
        "--checkpoint",
        type=Path,
        default=None,
        help="append every completed row here; pass the same path with --resume",
    )
    parser.add_argument("--resume", action="store_true")
    parser.add_argument(
        "--fly",
        choices=("none", "real", "null", "grid_hash"),
        default="none",
        help=(
            "who breaks ties the controller cannot break: nobody (a constant "
            "digest), the real connectome, a degree-preserving rewiring of it, or "
            "a state-dependent digest carrying no anatomy"
        ),
    )
    parser.add_argument(
        "--fly-config",
        type=Path,
        default=DEFAULT_FLY_CONFIG,
        help="connectome configuration used when --fly is real or null",
    )
    parser.add_argument(
        "--fly-runtime-dir",
        type=Path,
        default=None,
        help=(
            "compiled graph directory for the tiebreaker; required with --fly null, "
            "where it must point at a degree-preserving null bundle"
        ),
    )
    parser.add_argument(
        "--require-promotion",
        action="store_true",
        help="return nonzero unless the frozen random/progress score gate passes",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.action_budget <= 0:
        raise SystemExit("--action-budget must be positive")
    if len(set(args.seeds)) != len(args.seeds):
        raise SystemExit("--seeds must not contain duplicates")

    from flygi.config import load_config
    from flygi.controller import StateGraphPolicy

    config = load_config(args.config)
    if not config.controller.enabled:
        raise SystemExit(f"controller is disabled in {args.config}")

    runtime = BASELINE.load_arc_runtime()
    try:
        games = BASELINE.discover_games(
            runtime,
            args.environments_dir.resolve(),
            args.games,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    output = args.output or (
        DEFAULT_RESULTS_DIR
        / f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S.%fZ')}-{args.condition}.json"
    )
    output = output.resolve()
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing result: {output}")
    checkpoint = (
        args.checkpoint.resolve()
        if args.checkpoint is not None
        else output.with_suffix(".rows.jsonl")
    )
    if checkpoint.exists() and not args.resume:
        raise SystemExit(
            f"checkpoint already exists; pass --resume or choose another: {checkpoint}"
        )

    rows: list[dict[str, Any]] = []
    done: set[tuple[int, str]] = set()
    if args.resume and checkpoint.is_file():
        for line in checkpoint.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            identity = (int(row["seed"]), str(row["game_id"]))
            if identity in done:
                raise SystemExit(f"duplicate checkpoint row: {identity}")
            rows.append(row)
            done.add(identity)
        print(f"resumed {len(rows)} completed rows from {checkpoint}", flush=True)

    fly_description: dict[str, Any] = {"kind": "tie_digest", "connectome": False}
    fly_tiebreaker = None
    if args.fly == "grid_hash":
        from flygi.controller.fly_tiebreak import GridHashTiebreaker

        fly_tiebreaker = GridHashTiebreaker(seed=config.controller.mask_freeze_after)
        fly_description = {"connectome": False, **fly_tiebreaker.describe()}
        print("fly=grid_hash (no connectome; state-dependent control)", flush=True)
    elif args.fly != "none":
        from flygi.controller.fly_tiebreak import FlyTiebreaker

        if args.fly == "null" and args.fly_runtime_dir is None:
            raise SystemExit("--fly null requires --fly-runtime-dir pointing at a null bundle")
        fly_config = load_config(args.fly_config)
        # One tiebreaker is assembled once and reset per game. Rebuilding it per
        # game would reload 24.5M edges 75 times for an identical frozen graph.
        fly_tiebreaker = FlyTiebreaker(fly_config, runtime_dir=args.fly_runtime_dir)
        fly_description = {
            "kind": args.fly,
            "connectome": True,
            "config_path": str(args.fly_config),
            "config_sha256": BASELINE.sha256_file(args.fly_config),
            "runtime_dir": str(args.fly_runtime_dir) if args.fly_runtime_dir else None,
            **fly_tiebreaker.describe(),
        }
        print(
            f"fly={args.fly} nodes={fly_description['nodes']:,} "
            f"edges={fly_description['edges']:,} readout={fly_description['readout']}",
            flush=True,
        )

    def policy_factory(policy_seed: int) -> StateGraphPolicy:
        if fly_tiebreaker is not None:
            fly_tiebreaker.reset()
        policy = StateGraphPolicy(
            runtime.GameAction,
            config.controller,
            decision_seed=policy_seed,
            fly=fly_tiebreaker,
        )
        policy_factory.current = policy  # type: ignore[attr-defined]
        return policy

    checkpoint.parent.mkdir(parents=True, exist_ok=True)
    total = len(args.seeds) * len(games)
    position = len(rows)
    for seed in args.seeds:
        for game in games:
            identity = (seed, game.game_id)
            if identity in done:
                continue
            position += 1
            print(f"[{position}/{total}] seed={seed} game={game.game_id}", flush=True)
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
            row["policy_diagnostics"] = _policy_diagnostics(
                getattr(policy_factory, "current", None)
            )
            rows.append(row)
            with checkpoint.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True, allow_nan=False) + "\n")
            official = row.get("official") or {}
            print(
                f"  {row['status']}: actions={row['actions_completed']} "
                f"levels={official.get('levels_completed')} score={official.get('score')} "
                f"states={row['policy_diagnostics'].get('states_discovered')}",
                flush=True,
            )

    replay = BASELINE._deterministic_replay_check(
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
        replay_check=replay,
        schema=SCHEMA,
        policy_label="generic-state-effect-controller",
        extra={
            "condition": args.condition,
            "config_path": str(args.config),
            "config_sha256": BASELINE.sha256_file(args.config),
            "controller": asdict(config.controller),
            "fly": fly_description,
            "algorithm_references": {
                "frugal_explorer": "7dccef15650fa00ef1db1c21cc7279adcf4a9e2a",
                "blind_squirrel": "641c00ef6b149527e5268927a664a6a6d6bb13fa",
                "implementation": "native-clean-room",
            },
        },
    )
    result["checks"]["promotion"] = promotion_check(rows)
    BASELINE.write_json_exclusive(output, result)

    engineering = result["checks"]["gate"]
    promotion = result["checks"]["promotion"]
    summary = result["summaries"]["overall"]
    print(
        f"Wrote {output} | engineering={engineering['passed']} "
        f"promotion={promotion['passed']} mean_score={summary['mean_score']} "
        f"progress_games={promotion['progress_games']}",
        flush=True,
    )
    if not engineering["passed"]:
        return 1
    if args.require_promotion and not promotion["passed"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
