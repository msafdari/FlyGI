#!/usr/bin/env python3
"""Measure the MBON->DAN second-order learning loop (RSI deep dive).

The loop is ALREADY implemented by construction: MushroomBody.gate() reads
dopaminergic activity from the network state, the plastic KC->MBON block
lives inside the network the state advances through, and the compiled graph
carries 2,589 MBON->DAN feedback edges (measured 2026-09-24). So learning
can, in principle, modify its own teaching signal through fly anatomy alone.

This experiment measures whether it actually DOES, at measured learning
scales, and ablates the feedback in the only clean way: a frozen twin.

Protocol (preregistered in EXPERIMENTS.yaml under the RSI record):
  * Twin trajectories through the SAME captured stream: A learns (dense-style
    schedule: reward if the frame changed, punishment if not, every Nth
    transition), B is weight-frozen. Both advance through identical drive.
  * SECOND-ORDER COMPONENT per reinforcement = relative difference between
    the gate A actually receives and the counterfactual gate computed from
    B's state (identical machinery, learning-free dynamics). B *is* the
    severed-feedback ablation: the only path by which A's gate can differ is
    A's own weight changes propagating KC->MBON->...->DAN.
  * Also reported: raw DAN-activity divergence, MBON divergence, first-order
    sanity (weights must actually move), eligibility spread.

Expected at tier (EXPECTED, base rate 12 failed bridges): the anatomy
premise measured the feedback at ~2% of DAN input and one update's effect
at ~2e-5 of DAN drive, so the loop is predicted dynamically inert. The
point of running is to replace that prediction with a measurement.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STREAMS = ROOT / "results" / "jepa" / "streams"
OUT = ROOT / "results" / "mb_second_order.json"
CONFIG = ROOT / "configs" / "literal_rate_mb_learning.yaml"

REINFORCE_EVERY = 10
REWARD = 1.0


def run_game(stream_path: Path, config) -> dict:
    from flygi.controller.fly_tiebreak import FlyTiebreaker

    # Each twin loads its own graph. Sharing one bundle with
    # copy_connectivity=False would alias the weight arrays, so the
    # learner's updates would silently leak into the "frozen" twin and
    # the second-order comparison would measure nothing. (The read-only
    # guard caught exactly this on the first attempt.)
    learner = FlyTiebreaker(config, learning=True)
    frozen = FlyTiebreaker(config, learning=False)
    a = learner._network.connectivity.data
    b = frozen._network.connectivity.data
    if np.shares_memory(a, b):
        raise RuntimeError("twin networks share weight memory; comparison invalid")
    mb = learner._mushroom_body
    assert mb is not None

    with np.load(stream_path) as archive:
        grids = np.asarray(archive["grids"], dtype=np.int8)

    gate_rel_diffs: list[float] = []
    dan_rel_diffs: list[float] = []
    mbon_rel_diffs: list[float] = []
    events = 0
    for index in range(grids.shape[0]):
        grid = grids[index]
        learner.observe(grid, legal_action_ids=(0, 6))
        frozen.observe(grid, legal_action_ids=(0, 6))
        if index == 0 or index % REINFORCE_EVERY:
            continue
        changed = bool((grids[index] != grids[index - 1]).any())
        valence = REWARD if changed else -REWARD
        # The gate A actually receives, vs the counterfactual gate from the
        # frozen twin's state. Compute BOTH before A's update mutates weights.
        gate_a = mb.gate(learner._state, valence)
        gate_b = mb.gate(frozen._state, valence)
        dan_a = mb.dopaminergic_activity(learner._state)
        dan_b = mb.dopaminergic_activity(frozen._state)
        mbon_a = mb.mbon_activity(learner._state)
        mbon_b = mb.mbon_activity(frozen._state)

        def rel(a: np.ndarray, b: np.ndarray) -> float:
            denom = float(np.linalg.norm(a))
            return float(np.linalg.norm(a - b)) / denom if denom > 0 else 0.0

        gate_rel_diffs.append(rel(gate_a, gate_b))
        dan_rel_diffs.append(rel(dan_a, dan_b))
        mbon_rel_diffs.append(rel(mbon_a, mbon_b))
        learner.reinforce(valence)
        events += 1

    report = {
        "game": stream_path.stem,
        "reinforcements": events,
        "first_order_absolute_weight_change": float(learner._absolute_weight_change),
        "second_order_gate_rel_diff": {
            "mean": float(np.mean(gate_rel_diffs)),
            "max": float(np.max(gate_rel_diffs)),
            "final": float(gate_rel_diffs[-1]),
        },
        "dan_state_rel_diff_final": float(dan_rel_diffs[-1]),
        "mbon_state_rel_diff_final": float(mbon_rel_diffs[-1]),
        "trajectory": {
            "gate_rel_diff_first5": [float(v) for v in gate_rel_diffs[:5]],
            "gate_rel_diff_last5": [float(v) for v in gate_rel_diffs[-5:]],
        },
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", nargs="+", default=["lp85", "cd82", "vc33"])
    args = parser.parse_args(argv)

    from flygi.config import load_config

    config = load_config(CONFIG)

    reports = []
    for token in args.games:
        matches = sorted(STREAMS.glob(f"{token}*.npz"))
        if not matches:
            raise SystemExit(f"no captured stream for {token}")
        report = run_game(matches[0], config)
        reports.append(report)
        print(json.dumps(report, indent=2), flush=True)
    OUT.write_text(json.dumps(reports, indent=2) + "\n")
    print(f"wrote {OUT}")
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("mb_second_order", main))
