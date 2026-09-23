"""Does mushroom-body output reach the neurons this agent reads out from?

A published mushroom-body lesion control found that cutting MB output left
behaviour completely unchanged: the MB never reached the readout, so no amount
of KC->MBON plasticity could have altered a single decision. That is a cheap
failure to inherit and an expensive one to discover late, so it is measured
here directly.

The test zeroes every outgoing MBON edge and compares the resulting descending
neuron trace against the intact graph on identical input. Reported as an
effect size, not a verdict: a small but nonzero reach still permits learning,
it only bounds how much learning can do.

    uv run python scripts/mb_reach_test.py --config configs/literal_rate_mb_learning.yaml
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "configs" / "literal_rate_mb_learning.yaml"


def _populations(runtime_dir: Path) -> dict[str, np.ndarray]:
    meta = np.load(runtime_dir / "node_metadata.npz", allow_pickle=True)
    types = meta["type"]
    superclass = meta["superclass"]
    return {
        "kenyon_cells": np.flatnonzero(np.char.startswith(types, "KC")),
        "mbons": np.flatnonzero(np.char.startswith(types, "MBON")),
        "pam": np.flatnonzero(np.char.startswith(types, "PAM")),
        "ppl": np.flatnonzero(np.char.startswith(types, "PPL")),
        "readout": np.flatnonzero(superclass == "descending_neuron"),
    }


def _traces(config: Any, runtime_dir: Path, *, lesion: bool, turns: int, seed: int) -> np.ndarray:
    from flygi.controller.fly_tiebreak import FlyTiebreaker

    fly = FlyTiebreaker(config, runtime_dir=runtime_dir)
    if lesion:
        # Zero every outgoing MBON edge. The matrix is W[post, pre], so the
        # MBON columns are its outputs. Structure is preserved -- only the
        # weights go to zero -- so the comparison isolates MB influence rather
        # than changing the graph the dynamics run on.
        matrix = fly._network.connectivity
        # A lesion is a deliberate weight edit, so plasticity is declared for it
        # exactly as the learning site declares it. Topology is untouched.
        matrix.data.flags.writeable = True
        mbons = _populations(runtime_dir)["mbons"]
        matrix.data[np.isin(matrix.indices, mbons)] = 0.0

    rng = np.random.default_rng(seed)
    grid = rng.integers(0, 16, (64, 64), dtype=np.int8)
    collected = []
    for _ in range(turns):
        grid = grid.copy()
        grid[rng.integers(0, 58) :][:6, :6] = rng.integers(0, 16)
        fly.observe(grid, (1, 2, 3, 4, 5, 6))
        collected.append(np.asarray(fly._trace, dtype=np.float64).copy())
    return np.asarray(collected)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--turns", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)

    from flygi.config import load_config

    config = load_config(args.config)
    runtime_dir = Path(config.graph.output_dir)
    populations = _populations(runtime_dir)

    intact = _traces(config, runtime_dir, lesion=False, turns=args.turns, seed=args.seed)
    lesioned = _traces(config, runtime_dir, lesion=True, turns=args.turns, seed=args.seed)

    difference = np.abs(intact - lesioned)
    scale = float(np.abs(intact).mean())
    relative = float(difference.mean() / scale) if scale > 0 else 0.0
    changed = float((difference > 1e-12).mean())
    per_turn = difference.mean(axis=1) / (np.abs(intact).mean(axis=1) + 1e-30)

    report = {
        "config": str(args.config),
        "runtime_dir": str(runtime_dir),
        "turns": args.turns,
        "recurrent_gain": float(config.dynamics.recurrent_gain),
        "mbon_count": int(populations["mbons"].size),
        "readout_count": int(populations["readout"].size),
        "mean_absolute_readout": scale,
        "mean_absolute_difference": float(difference.mean()),
        "relative_effect": relative,
        "readout_entries_changed": changed,
        "relative_effect_by_turn": [float(x) for x in per_turn],
    }
    print(json.dumps(report, indent=2))
    print(
        f"\nMB reach: lesioning every MBON output changes the readout by "
        f"{100 * relative:.3f}% of its own magnitude, touching "
        f"{100 * changed:.1f}% of readout entries."
    )
    if args.output is not None:
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("mb_reach_test", main))
