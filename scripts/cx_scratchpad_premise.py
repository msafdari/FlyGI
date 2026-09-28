#!/usr/bin/env python3
"""H-CX-SCRATCHPAD premise-killer: can the EPG ring hold one bit UNDER LOAD?

HYPOTHESIS (registered 2026-09-27, before the run): H-CX-RING-ATTRACTOR
measured the project's only anatomy-specific dynamical asset -- EPG bump
persistence for 120+ steps at the deployed gain 2.0 -- but only in DARKNESS
after a seeded arc. A deployed agent never has darkness: the visual pathway
drives the same network every turn. The last untested use of the compass is
a one-bit context scratchpad (which program phase / which archetype), and it
requires the bump to survive REAL visual drive, not silence.

PREREGISTERED DESIGN:
  * Network: the deployed gain-2.0 compiled runtime with the bio-eye
    encoder (configs/literal_rate_bioeye_lc.yaml), full 166,700 nodes.
  * Write: from zeros, advance WRITE_STEPS with external drive confined to
    the EPG cells of a contiguous 90-degree wedge span centred on angle A
    (or B = A + 180deg). Wedge angles come from the anatomy: EPG instance
    labels carry PB wedge ids L1-L8/R1-R8, 22.5 degrees apart.
  * Hold: advance N in {10, 50, 120} steps under one of two conditions --
    DARKNESS (zero drive; the measured-positive replication arm) or VISUAL
    (the bio-eye drive of successive random-play frames from the shared
    recognizer capture, a different game per trial).
  * Read: EPG population-vector angle; classify A-vs-B by nearest target.
    20 trials per condition per N. Also record final EPG mass.
  * TRIVIAL ALTERNATIVE (named): a Python variable holds one bit for free
    and forever. The scratchpad can therefore never be a score lever on
    its own; this is a measured claim about what the anatomy supports, and
    even a positive buys no score without an invented read/write mapping.

KILL CONDITION, stated before the run: VISUAL-condition read-back accuracy
at N=50 <= 0.6 (chance 0.5) closes the scratchpad: the one circuit whose
wiring measurably matters holds state only in a silence the agent never
gets. EXPECTED tier note: the score-conversion base rate of this
repository's expected-tier predictions is 0 for 11.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

WRITE_STEPS = 20
WRITE_SCALE = 1.0  # defaults; overridable while validating the write against the measured darkness baseline
WEDGE_SPAN_DEG = 90.0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default="configs/literal_rate_bioeye_lc.yaml")
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--write-steps", type=int, default=WRITE_STEPS)
    parser.add_argument("--write-scale", type=float, default=WRITE_SCALE)
    parser.add_argument("--settle-map", action="store_true")
    parser.add_argument("--holds", default="10,50,120")
    parser.add_argument(
        "--capture-file",
        type=Path,
        default=ROOT / "results" / "diagnostics" / "recognizer_frames.npz",
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results" / "cx_scratchpad_premise.json"
    )
    args = parser.parse_args()

    import numpy as np

    from flygi.arc.factory import build_connectome_policy
    from flygi.config import load_config
    from flygi.encoding.features import encode_observation

    class _NullActions:
        RESET = 0

        @staticmethod
        def from_id(identifier: int) -> int:
            return identifier

    class _Frame:
        def __init__(self, g: Any) -> None:
            self.frame = [g]

    config = load_config(ROOT / args.config)
    assembled = build_connectome_policy(config, _NullActions)
    network = assembled.policy._network
    internal_steps = assembled.policy.internal_steps
    projection = assembled.projection
    node_count = network.initial_state().shape[0]

    with np.load(
        Path(config.graph.output_dir) / "node_metadata.npz", allow_pickle=False
    ) as archive:
        types = archive["type"].astype("U")
        instances = archive["instance"].astype("U")
    epg = np.flatnonzero(types == "EPG")
    # ESTABLISHED (connectome annotation): EPG instances carry protocerebral
    # bridge wedge ids; L1-L8 and R1-R8 tile the ring. ASSUMPTION: the
    # standard mapping of 16 wedges onto 360 degrees (22.5 deg each, L and R
    # interleaved); wrong only up to a fixed rotation, which cancels in an
    # A-vs-B readback.
    angles = np.full(epg.size, np.nan)
    for i, name in enumerate(instances[epg]):
        match = re.search(r"_([LR])(\d)", name)
        if match:
            side, wedge = match.group(1), int(match.group(2))
            index = (wedge - 1) * 2 + (0 if side == "L" else 1)
            angles[i] = index * (360.0 / 16.0)
    keep = ~np.isnan(angles)
    epg, angles = epg[keep], angles[keep]
    radians = np.deg2rad(angles)
    print(f"EPG with wedge labels: {epg.size}", flush=True)

    with np.load(args.capture_file) as archive:
        games = {k: archive[k] for k in archive.files}
    game_names = list(games.keys())

    def visual_drive(grid: Any) -> Any:
        features = encode_observation(
            _Frame(grid),
            previous_grid=None,
            previous_action_id=None,
            available_action_ids=(6,),
        )
        return projection.drive_features(features)

    def write_bump(target_deg: float) -> Any:
        drive = np.zeros(node_count, dtype=np.float32)
        distance = np.abs((angles - target_deg + 180.0) % 360.0 - 180.0)
        drive[epg[distance <= WEDGE_SPAN_DEG / 2.0]] = np.float32(args.write_scale)
        state = network.initial_state()
        for _ in range(args.write_steps):
            state = network.advance(state, drive, internal_steps=internal_steps)
        return state

    def read_angle(state: Any) -> tuple[float, float]:
        activity = np.maximum(state[epg], 0.0)
        mass = float(activity.sum())
        if mass <= 1e-9:
            return float("nan"), mass
        vector = np.sum(activity * np.exp(1j * radians))
        return float(np.rad2deg(np.angle(vector)) % 360.0), mass

    if args.settle_map:
        # STRUCTURAL PROBE, registered 2026-09-27 after the first runs: write
        # scale 3 and 8 produced bit-identical outcomes (tanh saturation) and
        # darkness readback sat at exactly chance, so before any scratchpad
        # verdict the prior question is whether the settled bump angle DEPENDS
        # on the write angle at all. Eight write angles, two write styles
        # (sustained drive, and direct state injection then release), settled
        # angle read after 50 darkness steps. If the settled angle is
        # independent of the write angle, the compiled ring sustains ACTIVITY
        # but not POSITION -- a single fixed attractor, no memory substrate --
        # and H-CX-SCRATCHPAD is refuted structurally, visual drive unneeded.
        table: dict[str, dict[str, Any]] = {}
        zero = np.zeros(node_count, dtype=np.float32)
        for style in ("drive", "inject"):
            rows: dict[str, Any] = {}
            for write_deg in np.arange(0.0, 360.0, 45.0):
                if style == "drive":
                    state = write_bump(float(write_deg))
                else:
                    state = network.initial_state().copy()
                    distance = np.abs((angles - write_deg + 180.0) % 360.0 - 180.0)
                    state[epg[distance <= WEDGE_SPAN_DEG / 2.0]] = 1.0
                for _ in range(50):
                    state = network.advance(state, zero, internal_steps=internal_steps)
                settled, mass = read_angle(state)
                rows[str(write_deg)] = {"settled": settled, "mass": mass}
                print(f"{style} write {write_deg:5.1f} -> settled {settled:7.2f} mass {mass:.4f}", flush=True)
            table[style] = rows
        args.output.write_text(json.dumps({"settle_map": table}, indent=2))
        return 0

    holds = [int(v) for v in args.holds.split(",")]
    rng = np.random.default_rng(20260927)
    results: dict[str, Any] = {
        "write_steps": args.write_steps,
        "write_scale": args.write_scale,
        "conditions": {},
    }
    for condition in ("darkness", "visual"):
        per_hold: dict[str, Any] = {}
        for hold in holds:
            correct = 0
            masses = []
            for trial in range(args.trials):
                target = 22.5 if trial % 2 == 0 else 202.5
                state = write_bump(target)
                if condition == "visual":
                    game = game_names[int(rng.integers(0, len(game_names)))]
                    frames = games[game]
                    for step in range(hold):
                        drive = visual_drive(frames[step % len(frames)])
                        state = network.advance(
                            state, drive, internal_steps=internal_steps
                        )
                else:
                    zero = np.zeros(node_count, dtype=np.float32)
                    for _ in range(hold):
                        state = network.advance(
                            state, zero, internal_steps=internal_steps
                        )
                angle, mass = read_angle(state)
                masses.append(mass)
                if not np.isnan(angle):
                    error_a = abs((angle - 22.5 + 180.0) % 360.0 - 180.0)
                    error_b = abs((angle - 202.5 + 180.0) % 360.0 - 180.0)
                    predicted = 22.5 if error_a < error_b else 202.5
                    if predicted == target:
                        correct += 1
            per_hold[str(hold)] = {
                "accuracy": correct / args.trials,
                "mean_epg_mass": float(np.mean(masses)),
            }
            print(f"{condition} N={hold}: {per_hold[str(hold)]}", flush=True)
        results["conditions"][condition] = per_hold
    results["kill_condition_met"] = (
        results["conditions"]["visual"]["50"]["accuracy"] <= 0.6
    )
    args.output.write_text(json.dumps(results, indent=2))
    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
