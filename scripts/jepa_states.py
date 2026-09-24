#!/usr/bin/env python3
"""Drive the frozen connectome through captured streams and record N_t.

H-JEPA-SPONTANEOUS state collection. For each captured game stream
(scripts/jepa_capture.py), the network is reset, then advanced one observation
at a time exactly as the agent's fly does: bio-eye colour drive, gain-2.0
signed operating point, the configured internal steps per observation. After
each advance the state restricted to the measured populations is recorded.

Registered assumption (c): state features are the measured populations --
retinotopy (23,720, from retinotopy.npz node_indices), LC (4,257, type prefix
"LC"), DN (1,314, superclass descending_neuron). The selector definitions are
stored beside the states so the probe can subset or ablate by segment.

Conditions:
  real    -- the MaleCNS graph (default runtime dir)
  null    -- the degree-preserving null graph (B3): same in/out degrees,
             shuffled targets; if it matches the real graph, structure beyond
             degree sequence is doing nothing
  bypass  -- no recurrence (B4): the identical ScipyRateNetwork code path with
             an EMPTY connectivity matrix, so states are pure leaky encodings
             of the drive; if it matches, the graph itself is doing nothing

ASSUMPTION (registered as part of (a)): drive is purely visual. The champion's
efference copy is off in the bio-eye base config, so N_t here measures what
vision plus intrinsic dynamics provide; action-conditioned probes reconstruct
actions from the stored streams instead.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STREAMS = ROOT / "results" / "jepa" / "streams"
OUT = ROOT / "results" / "jepa" / "states"
CONFIG = ROOT / "configs" / "literal_rate_bioeye_t4t5.yaml"
# The design red-team's blocking find (2026-09-24): the bio-eye gain-2.0
# config loads literal-rate-signed-MODULATORS, so B3 must rewire THAT graph.
# The literal-rate-signed null (435,540 fewer edges) is superseded here.
NULL_DIR = (
    ROOT
    / "data"
    / "processed"
    / "male-cns-v1.0"
    / "literal-rate-signed-modulators"
    / "nulls"
    / "degree_preserving"
    / "seed-20260921"
)


class _NullActions:
    """State collection never emits an action, so it needs no factory."""

    RESET = 0

    @staticmethod
    def from_id(identifier: int) -> int:
        return identifier


def _selectors(runtime_dir: Path) -> dict[str, np.ndarray]:
    with np.load(runtime_dir / "retinotopy.npz", allow_pickle=False) as archive:
        retinotopy = np.asarray(archive["node_indices"], dtype=np.int64)
    with np.load(runtime_dir / "node_metadata.npz", allow_pickle=False) as archive:
        types = archive["type"]
        superclass = archive["superclass"]
    lc = np.flatnonzero(np.char.startswith(types, "LC")).astype(np.int64)
    dn = np.flatnonzero(superclass == "descending_neuron").astype(np.int64)
    return {"retinotopy": retinotopy, "lc": lc, "dn": dn}


def _build_network(condition: str, config: Any) -> tuple[Any, Any, Any]:
    """Return (network, projection, internal_steps) for one condition."""

    from flygi.arc.factory import build_connectome_policy

    runtime_dir = NULL_DIR if condition == "null" else None
    assembled = build_connectome_policy(config, _NullActions, runtime_dir=runtime_dir)
    network = assembled.policy._network
    projection = assembled.projection
    if condition == "bypass":
        from scipy import sparse

        from flygi.dynamics.rate import ScipyRateNetwork

        n = network.node_count
        empty = sparse.csr_matrix((n, n), dtype=np.float32)
        empty.sort_indices()
        network = ScipyRateNetwork(empty, network.parameters, copy_connectivity=False)
    return network, projection, int(config.dynamics.internal_steps)


def collect_condition(condition: str, config: Any, streams: list[Path]) -> None:
    from flygi.encoding.features import encode_observation
    from flygi.telemetry import run_or_null

    telemetry = run_or_null()
    network, projection, internal_steps = _build_network(condition, config)
    runtime_dir = NULL_DIR if condition == "null" else Path(config.graph.output_dir)
    selectors = _selectors(runtime_dir)
    order = np.concatenate([selectors["retinotopy"], selectors["lc"], selectors["dn"]])
    if np.unique(order).size != order.size:
        raise RuntimeError("population selectors overlap; segments must be disjoint")
    out_dir = OUT / condition
    out_dir.mkdir(parents=True, exist_ok=True)
    meta = {
        "condition": condition,
        "config": str(CONFIG.relative_to(ROOT)),
        "runtime_dir": str(runtime_dir),
        "internal_steps": internal_steps,
        "segments": {
            "retinotopy": [0, int(selectors["retinotopy"].size)],
            "lc": [
                int(selectors["retinotopy"].size),
                int(selectors["retinotopy"].size + selectors["lc"].size),
            ],
            "dn": [
                int(selectors["retinotopy"].size + selectors["lc"].size),
                int(order.size),
            ],
        },
        "dtype": "float16",
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2) + "\n")

    class _Frame:
        def __init__(self, g: np.ndarray) -> None:
            self.frame = [g]

    for stream_path in streams:
        out_path = out_dir / stream_path.name
        if out_path.exists():
            print(f"{condition}/{stream_path.stem}: already collected, skipping", flush=True)
            continue
        with np.load(stream_path) as archive:
            grids = np.asarray(archive["grids"], dtype=np.int8)
        state = network.initial_state()
        previous = None
        rows = np.empty((grids.shape[0], order.size), dtype=np.float16)
        for index in range(grids.shape[0]):
            grid = grids[index]
            features = encode_observation(
                _Frame(grid),
                previous_grid=previous,
                previous_action_id=None,
                available_action_ids=(),
            )
            drive = projection.drive_features(features)
            state = network.advance(state, drive, internal_steps=internal_steps)
            rows[index] = state[order].astype(np.float16)
            previous = features.grid
        np.savez_compressed(out_path, states=rows)
        telemetry.info(
            "jepa.states.game",
            condition=condition,
            game=stream_path.stem,
            frames=int(grids.shape[0]),
        )
        print(f"{condition}/{stream_path.stem}: {grids.shape[0]} frames", flush=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--conditions", nargs="+", default=["real"])
    args = parser.parse_args(argv)

    from flygi.config import load_config

    config = load_config(CONFIG)
    streams = sorted(STREAMS.glob("*.npz"))
    if not streams:
        raise RuntimeError(f"no captured streams under {STREAMS}; run jepa_capture.py first")
    for condition in args.conditions:
        if condition not in {"real", "null", "bypass"}:
            raise ValueError(f"unknown condition {condition!r}")
        collect_condition(condition, config, streams)
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("jepa_states", main))
