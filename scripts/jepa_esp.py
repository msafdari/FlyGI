#!/usr/bin/env python3
"""ESP / washout test for H-JEPA-SPONTANEOUS (protocol item: run before probes).

Echo-state property: two trajectories of the SAME network under the SAME
drive, started from different initial states (zeros -- the registered
trajectory -- and a seeded random state), must converge; the washout W is the
last frame at which any game's normalized state distance is still >= 1e-3
(sustained-below criterion, 5 consecutive frames). If any game has not
converged by frame 50, the registered fallback applies: results become
per-trajectory and the claim language weakens.

Perturbation growth: at a mid-stream frame a 1e-6 perturbation is injected
and its growth tracked for 20 frames -- a largest-Lyapunov-style proxy. A
positive per-frame log growth rate with late convergence would mean the
gain-2.0 regime is effectively chaotic and every probe number is
trajectory-specific.
"""

from __future__ import annotations

import argparse
import importlib.util
import itertools
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STREAMS = ROOT / "results" / "jepa" / "streams"
OUT = ROOT / "results" / "jepa" / "esp.json"

CONVERGENCE_THRESHOLD = 1e-3
SUSTAIN_FRAMES = 5
FALLBACK_FRAME = 50
PERTURB_FRAME = 60
PERTURB_SCALE = 1e-6
PERTURB_TRACK = 20


def _load_states_module():
    spec = importlib.util.spec_from_file_location(
        "jepa_states", ROOT / "scripts" / "jepa_states.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--frames", type=int, default=120)
    parser.add_argument("--init-seed", type=int, default=20260924)
    parser.add_argument("--init-scale", type=float, default=0.1)
    args = parser.parse_args(argv)

    from flygi.config import load_config
    from flygi.encoding.features import encode_observation
    from flygi.telemetry import run_or_null

    telemetry = run_or_null()
    js = _load_states_module()
    config = load_config(js.CONFIG)
    network, projection, internal_steps = js._build_network("real", config)

    class _Frame:
        def __init__(self, g: np.ndarray) -> None:
            self.frame = [g]

    rng = np.random.default_rng(args.init_seed)
    report: dict[str, dict] = {}
    for stream_path in sorted(STREAMS.glob("*.npz")):
        with np.load(stream_path) as archive:
            grids = np.asarray(archive["grids"], dtype=np.int8)[: args.frames]
        state_a = network.initial_state()
        state_b = network.initial_state(seed=int(rng.integers(2**31)), scale=args.init_scale)
        previous = None
        distances: list[float] = []
        growth: list[float] = []
        perturbed = None
        for index in range(grids.shape[0]):
            features = encode_observation(
                _Frame(grids[index]),
                previous_grid=previous,
                previous_action_id=None,
                available_action_ids=(),
            )
            drive = projection.drive_features(features)
            state_a = network.advance(state_a, drive, internal_steps=internal_steps)
            state_b = network.advance(state_b, drive, internal_steps=internal_steps)
            previous = features.grid
            norm_a = float(np.linalg.norm(state_a))
            distances.append(float(np.linalg.norm(state_a - state_b)) / (norm_a + 1e-12))
            if index == PERTURB_FRAME:
                perturbed = state_a + rng.normal(0.0, PERTURB_SCALE, state_a.shape).astype(
                    np.float32
                )
            elif perturbed is not None and len(growth) < PERTURB_TRACK:
                perturbed = network.advance(perturbed, drive, internal_steps=internal_steps)
                gap = float(np.linalg.norm(perturbed - state_a))
                growth.append(gap)
        arr = np.asarray(distances)
        below = arr < CONVERGENCE_THRESHOLD
        converged_at = None
        for start in range(len(below) - SUSTAIN_FRAMES + 1):
            if bool(below[start : start + SUSTAIN_FRAMES].all()):
                converged_at = start
                break
        # Per-frame log growth of the injected perturbation while it is still
        # small; saturation at the tanh bound makes later frames meaningless.
        rates = []
        for a, b in itertools.pairwise(growth):
            if a > 0 and b > 0 and b < 1.0:
                rates.append(float(np.log(b / a)))
        report[stream_path.stem] = {
            "converged_at": converged_at,
            "final_distance": float(arr[-1]),
            "max_distance": float(arr.max()),
            "perturbation_log_growth_per_frame": (float(np.mean(rates)) if rates else None),
        }
        telemetry.info("jepa.esp.game", game=stream_path.stem, converged_at=converged_at)
        print(
            f"{stream_path.stem}: converged_at={converged_at} "
            f"final={arr[-1]:.2e} growth={report[stream_path.stem]['perturbation_log_growth_per_frame']}",
            flush=True,
        )

    convergences = [g["converged_at"] for g in report.values()]
    all_converged = all(c is not None and c <= FALLBACK_FRAME for c in convergences)
    washout = max((c for c in convergences if c is not None), default=None)
    summary = {
        "all_converged_by_fallback": all_converged,
        "recommended_washout": washout,
        "criterion": {
            "threshold": CONVERGENCE_THRESHOLD,
            "sustain_frames": SUSTAIN_FRAMES,
            "fallback_frame": FALLBACK_FRAME,
        },
        "games": report,
    }
    OUT.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"ESP: all_converged={all_converged} washout={washout} -> {OUT}")
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("jepa_esp", main))
