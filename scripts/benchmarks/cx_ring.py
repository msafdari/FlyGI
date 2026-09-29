#!/usr/bin/env python3
"""BIOLOGICAL BENCHMARK SUITE -- group CENTRAL COMPLEX (EB ring).

These are COMPUTATIONAL ANALOGUES of published fly results, run on the
compiled MaleCNS leaky rate model (166,700 nodes, 24.99M signed edges,
h <- (1-a)h + a*tanh(g*W*h + input)). A pass means the simulation
reproduces the published phenomenon's computational signature at that
operating point; it is not a claim about the fly, and a miss at every
point is a model-class limit (UNVALIDATABLE-AT-THIS-FIDELITY), not a
finding about the biology.

OPERATING GRID (fixed, shared across all benchmark groups):
    recurrent_gain in {0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5}
    leak           in {0.1, 0.3, 0.6}
    internal_steps = 4 (deployed convention), bias 0.
    21 points, swept sequentially in one process (one graph load).

=========================== PREREGISTRATION ===========================
Registered in this header BEFORE any sweep ran. The bands below are
final; misses are reported as misses.

BENCHMARK C1 -- EB bump formation and persistence in darkness.
  Citation: Seelig JD & Jayaraman V (2015) "Neural dynamics for landmark
  orientation and angular path integration." Nature 521:186-191.
  (A single localized activity bump in the EPG/E-PG ring persists in
  darkness, i.e. without visual input.)
  Protocol (per grid point): for each of 4 preregistered seed angles
  {22.5, 112.5, 202.5, 292.5} deg: sustained external drive (scale 1.0)
  confined to EPG cells within a 90-deg wedge centred on the angle for
  20 steps; release; 50 darkness steps (zero drive). Readout: positive
  lobe of EPG state; population-vector angle; mass = sum of positive
  EPG activity; circular variance cv = 1 - |R|/mass.
  PREREGISTERED PASS BAND (C1): the point passes iff for AT LEAST ONE of
  the 4 seed angles, after the 50 darkness steps:
      retention = final_mass / release_mass >= 0.05
      AND final circular variance <= 0.6.
  (Band anchored on the repo's own gain-1.5 measurement in
  results/cx_ring_regime_sweep.json: circvar 0.516-0.531 with surviving
  mass at 1.5/{0.3,0.6}; dead ring at 0.9. "At least one angle" because
  H-CX-SCRATCHPAD measured (2026-09-27) that writes on half the ring die
  at gain 2.0 -- persistence anywhere on the ring is the benchmark;
  position memory is recorded separately as n_angles_pass, a diagnostic
  that is NOT part of the band.)

BENCHMARK C2 -- opposite-signed PEN rotation of the bump.
  Citations: Turner-Evans D et al. (2017) "Angular velocity integration
  in a fly heading circuit." eLife 6:e23496. Green J et al. (2017) "A
  neural circuit architecture for angular integration in Drosophila."
  Nature 546:101-106. (Asymmetric P-EN activity rotates the EPG bump;
  left- vs right-side P-EN drive rotates it in OPPOSITE directions.)
  Protocol (per grid point): write a bump at 22.5 deg (20 steps, as C1),
  settle 10 darkness steps -> settled state s0. From the SAME s0, three
  arms of 30 steps each: (a) darkness control (intrinsic drift,
  diagnostic only); (b) constant drive scale 1.0 on left-side
  PEN_a(PEN1) cells (instance suffix _L#); (c) same on right-side
  (_R#). Signed rotation rate = mean of unwrapped per-step
  population-vector angle deltas (deg/step); a step with dead readout
  (mass <= 1e-9) yields no delta; the rate is NaN if fewer than 15 of
  30 deltas are valid.
  PREREGISTERED PASS BAND (C2): the point passes iff
      sign(rot_left) != sign(rot_right), both nonzero and non-NaN,
      AND |rot_left| >= 0.05 deg/step AND |rot_right| >= 0.05 deg/step,
  computed on the RAW rates (no drift subtraction -- matching how the
  repo's prior regime sweep scored it). Drift-corrected rates
  (rot - drift) are recorded as a preregistered DIAGNOSTIC only.

AUX MAP (not a pass/fail benchmark; the deployment-relevant condition,
expected to fail per H-CX-SCRATCHPAD, worth the measured map):
  From the same settled s0, 50 steps of ONGOING bio-eye visual drive
  (successive random-play frames from the shared recognizer capture,
  results/diagnostics/recognizer_frames.npz; the 2 first game names in
  sorted order, one run each). Recorded per game: retention vs s0 mass
  and final circvar; survived_visual iff BOTH runs have
  retention >= 0.05 AND circvar <= 0.6 (same thresholds as C1).

AMENDMENT (registered 2026-09-29 after ONE smoke point -- gain 2.0 /
leak 0.3 -- and BEFORE the grid sweep; the pass bands above are
UNCHANGED). The smoke point measured the C2 precondition failing
mechanically: the registered 22.5-deg seed is on the half of the ring
whose writes die (H-CX-SCRATCHPAD, 2026-09-27), so its settled state
had mass 0.0 and the left/right "rotation" rates (-5.89/+0.89
deg/step) were PEN-driven re-ignition of a dead network, not rotation
of a settled bump -- a spurious pass, worse than a miss. Amended C2 and
visual-aux seeding rule, fixed and outcome-blind: seed the C2/visual
settled state from the angle with the HIGHEST C1 retention at that
point (ties -> first in SEED_ANGLES order), captured at settle step 10
of the same C1 run. The original 22.5-seed arm is STILL measured and
recorded at every point (c2_original_seed) with the same band applied,
so the amendment hides nothing. c2.settled_mass is recorded per point;
a pass with settled_mass ~ 0 measures re-ignition, not rotation, and
the notes must say so.

PRIOR REPO CONTEXT (to REPRODUCE, not assume -- from
results/cx_ring_regime_sweep.json, protocol details of that sweep not
preserved in-repo, so agreement is expected in sign pattern, not
numerically): 1.5/0.3 and 1.5/0.6 passed both C1-like and C2-like
gates; 2.0/* failed C2 same-signed (rotL 0.55-0.58, rotR 0.34-0.36);
0.9 died (mass 0.0).

ASSUMPTION (plumbing constants, chosen because something had to be
chosen; wrong values would move magnitudes, not the sign structure the
bands test): wedge write scale 1.0 over a 90-deg span for 20 steps
(the cx_scratchpad_premise.py defaults), PEN drive scale 1.0, 30-step
rotation window, 10-step settle. ESTABLISHED (connectome annotation):
EPG instance labels carry PB wedge ids L1-L8/R1-R8; ASSUMPTION (same as
cx_scratchpad_premise.py): the standard 16-wedge mapping onto 360 deg,
22.5 deg per wedge, L/R interleaved -- wrong only up to a fixed
rotation, which cancels in every within-run comparison used here.
======================================================================

Writes results/benchmarks/cx_ring.json, saving partial results after
every grid point.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

GAINS = (0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5)
LEAKS = (0.1, 0.3, 0.6)
INTERNAL_STEPS = 4

SEED_ANGLES = (22.5, 112.5, 202.5, 292.5)
WEDGE_SPAN_DEG = 90.0
WRITE_STEPS = 20
WRITE_SCALE = 1.0
DARK_HOLD = 50
SETTLE_STEPS = 10
ROTATION_STEPS = 30
PEN_DRIVE_SCALE = 1.0
VISUAL_HOLD = 50
VISUAL_GAMES = 2

C1_RETENTION_MIN = 0.05
C1_CIRCVAR_MAX = 0.6
C2_RATE_MIN_DEG_PER_STEP = 0.05
DEAD_MASS = 1e-9
MIN_VALID_DELTAS = 15


def circular_stats(activity, radians):
    """Positive-lobe mass, population-vector angle (deg), circular variance."""
    import numpy as np

    mass = float(activity.sum())
    if mass <= DEAD_MASS:
        return mass, float("nan"), 1.0
    vector = complex(np.sum(activity * np.exp(1j * radians)))
    angle = float(np.rad2deg(np.angle(vector)) % 360.0)
    circvar = float(1.0 - abs(vector) / mass)
    return mass, angle, circvar


def main() -> int:
    parser = argparse.ArgumentParser(description="CX ring benchmark sweep")
    parser.add_argument("--config", default="configs/literal_rate_bioeye_lc.yaml")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results" / "benchmarks" / "cx_ring.json"
    )
    parser.add_argument(
        "--points",
        default="",
        help="optional comma list gain:leak to restrict the grid (smoke runs)",
    )
    parser.add_argument(
        "--capture-file",
        type=Path,
        default=ROOT / "results" / "diagnostics" / "recognizer_frames.npz",
    )
    args = parser.parse_args()

    import numpy as np

    from flygi.arc.factory import build_connectome_policy
    from flygi.config import load_config
    from flygi.dynamics.rate import RateParameters, ScipyRateNetwork
    from flygi.encoding.features import encode_observation

    class _NullActions:
        RESET = 0

        @staticmethod
        def from_id(identifier: int) -> int:
            return identifier

    class _Frame:
        def __init__(self, g: Any) -> None:
            self.frame = [g]

    t0 = time.time()
    config = load_config(ROOT / args.config)
    assembled = build_connectome_policy(config, _NullActions)
    base_network = assembled.policy._network
    projection = assembled.projection
    connectivity = base_network.connectivity  # frozen CSR; never mutated
    node_count = base_network.node_count
    print(f"graph loaded: {node_count} nodes in {time.time() - t0:.1f}s", flush=True)

    metadata_dir = Path(config.graph.output_dir)
    if not metadata_dir.is_absolute():
        metadata_dir = ROOT / metadata_dir
    with np.load(metadata_dir / "node_metadata.npz", allow_pickle=False) as archive:
        types = archive["type"].astype("U")
        instances = archive["instance"].astype("U")

    # EPG ring with wedge angles (machinery reused from cx_scratchpad_premise.py).
    epg = np.flatnonzero(types == "EPG")
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

    # PEN_a populations split by hemisphere from instance suffix _L#/_R#.
    pen_a = np.flatnonzero(types == "PEN_a(PEN1)")
    pen_left, pen_right = [], []
    for idx, name in zip(pen_a, instances[pen_a]):
        match = re.search(r"_([LR])(\d)", name)
        if match:
            (pen_left if match.group(1) == "L" else pen_right).append(int(idx))
    pen_left = np.asarray(pen_left, dtype=np.int64)
    pen_right = np.asarray(pen_right, dtype=np.int64)
    print(
        f"EPG with wedge labels: {epg.size}; PEN_a left {pen_left.size}, right {pen_right.size}",
        flush=True,
    )

    # Visual drives: precompute one drive vector per frame for the two fixed
    # game sequences (projection is static plumbing, independent of gain/leak).
    with np.load(args.capture_file) as archive:
        game_names = sorted(archive.files)[:VISUAL_GAMES]
        visual_drives = {}
        for game in game_names:
            frames = archive[game]
            drives = []
            for step in range(VISUAL_HOLD):
                features = encode_observation(
                    _Frame(frames[step % len(frames)]),
                    previous_grid=None,
                    previous_action_id=None,
                    available_action_ids=(6,),
                )
                drives.append(
                    np.asarray(projection.drive_features(features), dtype=np.float32)
                )
            visual_drives[game] = drives
    print(f"visual sequences prepared: {game_names}", flush=True)

    zero = np.zeros(node_count, dtype=np.float32)

    def wedge_drive(target_deg: float):
        drive = np.zeros(node_count, dtype=np.float32)
        distance = np.abs((angles - target_deg + 180.0) % 360.0 - 180.0)
        drive[epg[distance <= WEDGE_SPAN_DEG / 2.0]] = np.float32(WRITE_SCALE)
        return drive

    pen_left_drive = np.zeros(node_count, dtype=np.float32)
    pen_left_drive[pen_left] = np.float32(PEN_DRIVE_SCALE)
    pen_right_drive = np.zeros(node_count, dtype=np.float32)
    pen_right_drive[pen_right] = np.float32(PEN_DRIVE_SCALE)

    def read(state):
        return circular_stats(np.maximum(state[epg], 0.0), radians)

    def rotation_rate(network, state, drive, steps):
        """Signed mean unwrapped PVA delta (deg/step) over `steps` advances."""
        _, previous_angle, _ = read(state)
        deltas = []
        for _ in range(steps):
            state = network.advance(state, drive, internal_steps=INTERNAL_STEPS)
            _, angle, _ = read(state)
            if not (np.isnan(angle) or np.isnan(previous_angle)):
                deltas.append((angle - previous_angle + 180.0) % 360.0 - 180.0)
            previous_angle = angle
        if len(deltas) < MIN_VALID_DELTAS:
            return float("nan"), state
        return float(np.mean(deltas)), state

    if args.points:
        grid = []
        for token in args.points.split(","):
            gain_s, leak_s = token.split(":")
            grid.append((float(gain_s), float(leak_s)))
    else:
        grid = [(g, k) for g in GAINS for k in LEAKS]

    results: dict[str, Any] = {
        "group": "central_complex",
        "config": args.config,
        "internal_steps": INTERNAL_STEPS,
        "preregistration": {
            "C1": (
                "pass iff >=1 of 4 seed angles has retention "
                f">= {C1_RETENTION_MIN} and circvar <= {C1_CIRCVAR_MAX} after "
                f"{DARK_HOLD} darkness steps (Seelig & Jayaraman 2015)"
            ),
            "C2": (
                "pass iff sign(rot_left) != sign(rot_right) and both "
                f"|rot| >= {C2_RATE_MIN_DEG_PER_STEP} deg/step, raw rates "
                f"over {ROTATION_STEPS} steps (Turner-Evans 2017; Green 2017)"
            ),
            "visual_aux": (
                f"map only: survived iff both game runs retain >= {C1_RETENTION_MIN} "
                f"with circvar <= {C1_CIRCVAR_MAX} after {VISUAL_HOLD} visual steps"
            ),
            "amendment": (
                "C2/visual seed = highest-retention C1 angle (fixed rule), "
                "registered after the 2.0/0.3 smoke point measured the "
                "22.5-deg seed dead (settled mass 0.0) and before the grid "
                "sweep; bands unchanged; original 22.5-deg arm recorded as "
                "c2_original_seed at every point"
            ),
        },
        "grid": [],
    }

    for gain, leak in grid:
        point_t0 = time.time()
        network = ScipyRateNetwork(
            connectivity,
            RateParameters(
                internal_steps=INTERNAL_STEPS,
                leak=leak,
                recurrent_gain=gain,
                bias=0.0,
            ),
            copy_connectivity=False,
        )
        row: dict[str, Any] = {"gain": gain, "leak": leak}

        # ---- C1: formation + darkness persistence, 4 seed angles ----
        per_angle = {}
        settled_states: dict[str, Any] = {}
        for target in SEED_ANGLES:
            drive = wedge_drive(target)
            state = network.initial_state()
            for _ in range(WRITE_STEPS):
                state = network.advance(state, drive, internal_steps=INTERNAL_STEPS)
            release_mass, release_angle, release_cv = read(state)
            # 50 darkness steps; capture every angle's settled state at step
            # SETTLE_STEPS -- the C2/visual seeds draw from these (amendment).
            for step in range(DARK_HOLD):
                state = network.advance(state, zero, internal_steps=INTERNAL_STEPS)
                if step + 1 == SETTLE_STEPS:
                    settled_states[str(target)] = state.copy()
            final_mass, final_angle, final_cv = read(state)
            retention = (
                final_mass / release_mass if release_mass > DEAD_MASS else 0.0
            )
            per_angle[str(target)] = {
                "release_mass": release_mass,
                "release_angle": release_angle,
                "final_mass": final_mass,
                "final_angle": final_angle,
                "final_circvar": final_cv,
                "retention": retention,
                "angle_pass": bool(
                    retention >= C1_RETENTION_MIN and final_cv <= C1_CIRCVAR_MAX
                ),
            }
        passing = [a for a, v in per_angle.items() if v["angle_pass"]]
        best_angle = max(per_angle, key=lambda a: per_angle[a]["retention"])
        row["c1"] = {
            "per_angle": per_angle,
            "n_angles_pass": len(passing),
            "best_angle": best_angle,
            "best_retention": per_angle[best_angle]["retention"],
            "best_circvar": per_angle[best_angle]["final_circvar"],
            "pass": bool(passing),
        }

        # ---- C2: opposite-signed PEN rotation from the settled bump ----
        def measure_c2(s0):
            s0_mass, s0_angle, s0_cv = read(s0)
            drift, _ = rotation_rate(network, s0.copy(), zero, ROTATION_STEPS)
            rot_left, _ = rotation_rate(
                network, s0.copy(), pen_left_drive, ROTATION_STEPS
            )
            rot_right, _ = rotation_rate(
                network, s0.copy(), pen_right_drive, ROTATION_STEPS
            )
            both_valid = not (np.isnan(rot_left) or np.isnan(rot_right))
            return {
                "settled_mass": s0_mass,
                "settled_angle": s0_angle,
                "settled_circvar": s0_cv,
                "drift_degstep": drift,
                "rot_left_degstep": rot_left,
                "rot_right_degstep": rot_right,
                "rot_left_drift_corrected": (
                    rot_left - drift
                    if both_valid and not np.isnan(drift)
                    else float("nan")
                ),
                "rot_right_drift_corrected": (
                    rot_right - drift
                    if both_valid and not np.isnan(drift)
                    else float("nan")
                ),
                "opposite_signed": bool(both_valid and rot_left * rot_right < 0.0),
                "pass": bool(
                    both_valid
                    and rot_left * rot_right < 0.0
                    and abs(rot_left) >= C2_RATE_MIN_DEG_PER_STEP
                    and abs(rot_right) >= C2_RATE_MIN_DEG_PER_STEP
                ),
            }

        # AMENDED primary seed: highest-retention C1 angle (fixed rule,
        # outcome-blind w.r.t. C2); original 22.5-deg arm recorded alongside.
        seed_angle = max(
            (str(a) for a in SEED_ANGLES),
            key=lambda a: per_angle[a]["retention"],
        )
        row["c2"] = {"seed_angle": float(seed_angle)}
        row["c2"].update(measure_c2(settled_states[seed_angle]))
        row["c2_original_seed"] = {"seed_angle": 22.5}
        row["c2_original_seed"].update(measure_c2(settled_states["22.5"]))
        c2_pass = row["c2"]["pass"]
        s0 = settled_states[seed_angle]
        s0_mass = row["c2"]["settled_mass"]
        rot_left = row["c2"]["rot_left_degstep"]
        rot_right = row["c2"]["rot_right_degstep"]
        drift = row["c2"]["drift_degstep"]

        # ---- AUX: bump survival under ongoing bio-eye visual drive ----
        visual = {}
        for game in game_names:
            state = s0.copy()
            for drive in visual_drives[game]:
                state = network.advance(state, drive, internal_steps=INTERNAL_STEPS)
            v_mass, v_angle, v_cv = read(state)
            v_retention = v_mass / s0_mass if s0_mass > DEAD_MASS else 0.0
            visual[game] = {
                "retention_vs_settled": v_retention,
                "final_circvar": v_cv,
                "final_angle": v_angle,
                "run_pass": bool(
                    v_retention >= C1_RETENTION_MIN and v_cv <= C1_CIRCVAR_MAX
                ),
            }
        row["visual_aux"] = {
            "per_game": visual,
            "survived_visual": bool(all(v["run_pass"] for v in visual.values())),
        }

        row["elapsed_s"] = round(time.time() - point_t0, 1)
        results["grid"].append(row)
        network.spmv.close()

        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(results, indent=2))
        print(
            f"gain {gain} leak {leak}: C1 {'PASS' if row['c1']['pass'] else 'miss'} "
            f"(best ret {row['c1']['best_retention']:.3f} cv "
            f"{row['c1']['best_circvar']:.3f}, {row['c1']['n_angles_pass']}/4 angles) | "
            f"C2 {'PASS' if c2_pass else 'miss'} (seed {seed_angle} mass {s0_mass:.3f} "
            f"L {rot_left:+.3f} R {rot_right:+.3f} drift {drift:+.3f}) | visual "
            f"{'survived' if row['visual_aux']['survived_visual'] else 'died'} "
            f"[{row['elapsed_s']}s]",
            flush=True,
        )

    results["total_elapsed_s"] = round(time.time() - t0, 1)
    args.output.write_text(json.dumps(results, indent=2))
    print(f"done in {results['total_elapsed_s']}s -> {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
