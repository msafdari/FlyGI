#!/usr/bin/env python3
"""Train the Track B action head on a frozen connectome with CEM.

The graph, encoder, descending population and standardizer are frozen. Only the
520-parameter head moves, so whatever it learns it learns *through* the
connectome's dynamics.

**Objective.** Raw ARC score is far too sparse to learn from: across 75 rows of
the 500-action sweep the real agent completed two levels. The declared training
objective is therefore dense,

    J = mean over rows of ( unique_observations + level_bonus * levels_completed )

Unique-observation count is the measured deficit -- the real agent reached 213.3
against random legal play's 335.2 -- and the condition that explores most also
completes most levels. The level bonus keeps actual progress dominant when it
occurs.

**Honesty constraints.** This trains on public games and is the specification's
"public-ARC development" regime. It is not evidence of zero-shot generality and
must never be described as such. The same budget and the same trainer must be
offered to the no-recurrent-graph bypass before any claim that the connectome
deserves credit; that comparison is deferred, not cancelled.

A trace-ablation diagnostic is recorded at the end: the winning parameters are
re-evaluated with the descending trace zeroed. If the objective barely drops,
the head has learned to ignore the connectome and the result is an interface
result, not a connectome result.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

DEFAULT_CONFIG = ROOT / "configs/literal_rate_signed_loop_escape.yaml"
DEFAULT_RESULTS_DIR = ROOT / "results" / "head_training"
DEFAULT_PARAMS_DIR = ROOT / "results" / "manifests"

_WORKER: dict[str, Any] = {}


def _worker_init(config_path: str, games: list[str], budget: int, feature_dim: int) -> None:
    """Load the frozen graph once per worker, not once per candidate."""

    os.environ.setdefault("OPERATION_MODE", "offline")
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "_flygi_baseline_evaluator", ROOT / "scripts" / "evaluate_random_baseline.py"
    )
    assert spec is not None and spec.loader is not None
    baseline = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = baseline
    spec.loader.exec_module(baseline)

    from flygi.config import load_config

    runtime = baseline.load_arc_runtime()
    _WORKER.update(
        {
            "baseline": baseline,
            "runtime": runtime,
            "config": load_config(config_path),
            "games": baseline.discover_games(
                runtime, baseline.DEFAULT_ENVIRONMENTS_DIR.resolve(), games
            ),
            "budget": int(budget),
            "feature_dim": int(feature_dim),
            "environments_dir": baseline.DEFAULT_ENVIRONMENTS_DIR.resolve(),
        }
    )


def _evaluate(payload: tuple[int, list[float], int, float, bool]) -> dict[str, Any]:
    """Score one candidate parameter vector. Never raises to the parent."""

    index, values, seed, level_bonus, ablate_trace = payload
    try:
        from flygi.arc.factory import build_connectome_policy

        baseline = _WORKER["baseline"]
        runtime = _WORKER["runtime"]
        parameters = np.asarray(values, dtype=np.float32)

        unique_total = 0.0
        levels_total = 0
        rows = 0
        for game in _WORKER["games"]:

            def policy_factory(policy_seed: int, _game: Any = game) -> Any:
                assembled = build_connectome_policy(
                    _WORKER["config"],
                    runtime.GameAction,
                    trained_head_parameters=parameters,
                    trained_head_feature_dim=_WORKER["feature_dim"],
                    ablate_trace=ablate_trace,
                )
                return assembled.policy

            row = baseline.evaluate_one(
                runtime,
                game,
                seed,
                _WORKER["budget"],
                _WORKER["environments_dir"],
                policy_factory=policy_factory,
            )
            if row["status"] != "success":
                return {"index": index, "objective": float("-inf"), "failed": True}
            unique_total += float(row["observations"]["unique"])
            levels_total += int((row["official"] or {}).get("levels_completed") or 0)
            rows += 1

        objective = (unique_total + level_bonus * levels_total) / max(rows, 1)
        return {
            "index": index,
            "objective": float(objective),
            "mean_unique_observations": unique_total / max(rows, 1),
            "levels_completed": levels_total,
            "failed": False,
        }
    except Exception as exc:  # A failed candidate must not kill the run.
        return {
            "index": index,
            "objective": float("-inf"),
            "failed": True,
            "error": f"{type(exc).__name__}: {exc}",
        }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--games", nargs="+", default=["all"])
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--action-budget", type=int, default=200)
    parser.add_argument("--feature-dim", type=int, default=48)
    parser.add_argument("--population", type=int, default=16)
    parser.add_argument("--elites", type=int, default=4)
    parser.add_argument("--generations", type=int, default=20)
    parser.add_argument("--sigma", type=float, default=0.5)
    parser.add_argument("--sigma-decay", type=float, default=0.93)
    parser.add_argument("--level-bonus", type=float, default=500.0)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--cem-seed", type=int, default=20260922)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    if args.elites >= args.population:
        raise SystemExit("--elites must be smaller than --population")

    from flygi.decoding.trained_head import TrainedHeadSpec

    spec = TrainedHeadSpec(readout_size=1314, feature_dim=args.feature_dim)
    dimension = spec.parameter_count
    generator = np.random.default_rng(args.cem_seed)
    mean = np.zeros(dimension, dtype=np.float64)
    sigma = np.full(dimension, float(args.sigma), dtype=np.float64)

    history: list[dict[str, Any]] = []
    best = {"objective": float("-inf"), "parameters": mean.tolist(), "generation": -1}
    started = datetime.now(UTC)

    with ProcessPoolExecutor(
        max_workers=args.workers,
        initializer=_worker_init,
        initargs=(str(args.config), list(args.games), args.action_budget, args.feature_dim),
    ) as pool:
        for generation in range(args.generations):
            samples = generator.normal(mean, sigma, size=(args.population, dimension))
            payloads = [
                (i, samples[i].tolist(), args.seed, args.level_bonus, False)
                for i in range(args.population)
            ]
            results = sorted(pool.map(_evaluate, payloads), key=lambda r: r["index"])
            objectives = np.asarray([r["objective"] for r in results], dtype=np.float64)
            finite = np.isfinite(objectives)
            if not finite.any():
                raise SystemExit(f"generation {generation}: every candidate failed")

            order = np.argsort(-np.where(finite, objectives, -np.inf))
            elite = samples[order[: args.elites]]
            mean = elite.mean(axis=0)
            sigma = np.maximum(elite.std(axis=0), 1e-3) * 1.0
            sigma *= args.sigma_decay

            top = int(order[0])
            if objectives[top] > best["objective"]:
                best = {
                    "objective": float(objectives[top]),
                    "parameters": samples[top].tolist(),
                    "generation": generation,
                }
            record = {
                "generation": generation,
                "best_objective": float(objectives[top]),
                "mean_objective": float(objectives[finite].mean()),
                "elite_objective": float(objectives[order[: args.elites]].mean()),
                "failed_candidates": int((~finite).sum()),
                "mean_sigma": float(sigma.mean()),
                "best_mean_unique_observations": results[top].get("mean_unique_observations"),
                "best_levels_completed": results[top].get("levels_completed"),
            }
            history.append(record)
            print(json.dumps(record, sort_keys=True), flush=True)

        # Trace ablation: does the winner actually use the connectome?
        ablation = _evaluate((0, best["parameters"], args.seed, args.level_bonus, True))

    result = {
        "schema": "flygi.head-training",
        "schema_version": 1,
        "started_utc": started.isoformat(),
        "finished_utc": datetime.now(UTC).isoformat(),
        "trains_on_public_games": True,
        "is_zero_shot_evidence": False,
        "objective": "mean(unique_observations + level_bonus * levels_completed)",
        "settings": {
            key: (str(value) if isinstance(value, Path) else value)
            for key, value in sorted(vars(args).items())
        },
        "parameter_count": dimension,
        "history": history,
        "best": best,
        "trace_ablation": ablation,
    }
    output = args.output or (
        DEFAULT_RESULTS_DIR
        / f"{datetime.now(UTC).strftime('%Y%m%dT%H%M%S.%fZ')}-head-training.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x", encoding="utf-8") as handle:
        handle.write(json.dumps(result, indent=2, sort_keys=True) + "\n")

    params_path = DEFAULT_PARAMS_DIR / "trained_head_parameters.json"
    params_path.write_text(
        json.dumps(
            {
                "schema": "flygi.trained-head-parameters",
                "parameter_count": dimension,
                "feature_dim": args.feature_dim,
                "objective": best["objective"],
                "generation": best["generation"],
                "trains_on_public_games": True,
                "parameters": best["parameters"],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "parameters": str(params_path),
                "best_objective": best["objective"],
                "trace_ablation_objective": ablation.get("objective"),
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
