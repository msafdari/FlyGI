#!/usr/bin/env python3
"""H-CX-HEADING-LATENT -- the Task 9 Stage-B (dynamical) kill test.

PREREGISTRATION (EXPERIMENTS.yaml H-CX-HEADING-LATENT and
docs/arenas/task9_cx_latent/killtest_design.md, both frozen 2026-10-10
in the SAME commit as Stage A, before Stage A ran, so this design was
not tuned on Stage A's PASS; restated, not changed):

  - Regime: class-1 rate dynamics on the FULL compiled graph at
    gain 1.5 / leak 0.3 -- the regime where opposite-sign PEN steering
    is MEASURED (H-CX-RING-ATTRACTOR regime sweep) and position
    storage was never tested. cx_ring.py machinery verbatim: loading,
    wedge drive (90-deg span, scale 1.0, 20 write steps), PVA read,
    rotation rate, INTERNAL_STEPS 4, 10-step settle.
  - Angles: 22.5 (CALIBRATION) and 112.5 / 202.5 / 292.5 (HELD OUT).
    Darkness window: 200 steps = 2 simulated seconds under the
    fc2_eb_ring 10 ms/step-equivalent (ASSUMED conversion, carried).
  - Arms: REAL / CX-REWIRED x3 -- degree-preserving rewire of the
    CX-internal 148x148 block ONLY (AC-5; EPG/PEN_a/PEN_b/Delta7/PEG,
    composition asserted 46/20/22/42/18), rest of the graph intact,
    seeds 4242+0..2, identical drives.
  - Tracking: 3 preregistered command sequences (seed 20261010, 6
    segments x 200 steps, commands in {L, R, off}), decoded against
    the command integral using the rotation-rate calibration measured
    on the CALIBRATION angle only. OPERATIONALIZATION of the
    registration's singular "the rotation-rate calibration": the REAL
    arm's calibrated left/right rates define the commands' ground
    truth for EVERY arm -- the command means "rotate at the measured
    rate", so an arm that cannot steer accumulates error against it.
  - PASS iff (1) CONTINUUM: all three held-out angles end within
    45 deg of their own seed with circular variance <= 0.6 after the
    200-step darkness; (2) TRACKING: mean final |error| over the 3
    sequences <= 45 deg; (3) WIRING-SPECIFIC: real beats every
    rewired arm on mean final tracking error AND no rewired arm
    passes bars 1+2. Engineered 2-variable integrator = ceiling
    context, not a bar.
  - BLOCKED (exit 3): the calibration angle fails its persistence
    precheck (retention >= 0.05 and circvar <= 0.6 at 1.5/0.3 -- the
    AC-2 regime-transplant gate); runtime absent; NaN/overflow in
    > 20% of runs in any arm. INSTRUMENT-LEVEL GUARD, added at build
    time and labeled as such (not in the registration): same-signed
    or sub-threshold calibration rates (|rate| < 0.05 deg/step) also
    BLOCK, because the command integral is undefined without a signed
    rate basis -- the measured regime property failing to reproduce,
    the same class as the AC-2 gate.

Data gate: runs where the compiled runtime lives. Pure parts
(sequences, integration, circular stats, block rewire, verdict) are
unit-tested in-cloud.

Run:    python scripts/arenas/cx_heading_killtest.py
Output: results/arenas/cx_heading_killtest.json (+ .log)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- frozen constants (killtest_design.md + cx_ring conventions) ------------
GAIN = 1.5
LEAK = 0.3
INTERNAL_STEPS = 4
CAL_ANGLE = 22.5
HELDOUT_ANGLES = (112.5, 202.5, 292.5)
WEDGE_SPAN_DEG = 90.0
WRITE_STEPS = 20
WRITE_SCALE = 1.0
SETTLE_STEPS = 10
DARK_STEPS = 200          # 2 s at the fc2_eb_ring 10 ms/step equivalence
ROTATION_STEPS = 30
PEN_DRIVE_SCALE = 1.0
MIN_VALID_DELTAS = 15
DEAD_MASS = 1e-9
TRACK_SEED = 20261010
N_SEQUENCES = 3
SEGMENTS = 6
SEGMENT_STEPS = 200
RETENTION_MIN = 0.05
CIRCVAR_MAX = 0.6
RATE_MIN_DEG_PER_STEP = 0.05
ERR_MAX_DEG = 45.0
REWIRE_SEED_BASE = 4242
REWIRE_SEEDS = (0, 1, 2)
MAX_UNSTABLE_FRACTION = 0.20
CX_TYPES = ("EPG", "PEN_a(PEN1)", "PEN_b(PEN2)", "Delta7", "PEG")
EXPECTED_COUNTS = {"EPG": 46, "PEN_a(PEN1)": 20, "PEN_b(PEN2)": 22,
                   "Delta7": 42, "PEG": 18}
CONFIG = "configs/literal_rate_bioeye_lc.yaml"   # cx_ring's config, verbatim

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
OUT_JSON = ROOT / "results/arenas/cx_heading_killtest.json"

WEDGE_RE = re.compile(r"_([LR])(\d)")


# ---------------------------------------------------------------------------
# Pure plumbing (unit-tested in-cloud)
# ---------------------------------------------------------------------------

def circular_stats(activity, radians):
    """cx_ring verbatim: positive-lobe mass, PVA angle (deg), circvar."""
    mass = float(activity.sum())
    if mass <= DEAD_MASS:
        return mass, float("nan"), 1.0
    vector = complex(np.sum(activity * np.exp(1j * radians)))
    angle = float(np.rad2deg(np.angle(vector)) % 360.0)
    circvar = float(1.0 - abs(vector) / mass)
    return mass, angle, circvar


def circ_err_deg(a: float, b: float) -> float:
    """|smallest signed difference| in degrees; NaN-propagating."""
    if np.isnan(a) or np.isnan(b):
        return float("nan")
    return abs((a - b + 180.0) % 360.0 - 180.0)


def make_sequences(seed: int = TRACK_SEED):
    """The 3 preregistered command sequences: 6 segments each, commands
    in {'L', 'R', 'off'}, deterministic in the frozen seed."""
    rng = np.random.default_rng(seed)
    return [[("L", "R", "off")[int(rng.integers(0, 3))]
             for _ in range(SEGMENTS)] for _ in range(N_SEQUENCES)]


def integrate_commands(sequence, rate_left: float, rate_right: float,
                       steps_per_segment: int = SEGMENT_STEPS) -> float:
    """Ground-truth heading change (deg) of a command sequence under
    the calibrated rates (the operationalization in the docstring)."""
    total = 0.0
    for command in sequence:
        if command == "L":
            total += rate_left * steps_per_segment
        elif command == "R":
            total += rate_right * steps_per_segment
    return total


def cx_block_rewire(full_matrix, cx_idx: np.ndarray, seed: int):
    """Degree-preserving rewire of the CX-internal block ONLY (AC-5):
    the induced cx_idx x cx_idx block is rewired, every other entry of
    the full matrix is untouched."""
    from scipy import sparse
    from flygi.connectome.nulls import degree_preserving_rewire
    block = sparse.csr_matrix(full_matrix[cx_idx][:, cx_idx])
    rewired_block, _ = degree_preserving_rewire(block, seed=seed)
    out = sparse.lil_matrix(full_matrix.copy())
    out[np.ix_(cx_idx, cx_idx)] = rewired_block.todense()
    return sparse.csr_matrix(out)


def assemble_verdict(continuum: dict, tracking: dict) -> dict:
    """The frozen three-bar rule. continuum maps arm -> {angle ->
    {err_deg, circvar}}; tracking maps arm -> list of final |error|
    (deg, NaN = lost bump). Arms: 'real', 'rw0', 'rw1', 'rw2'."""
    def bar1(arm):
        rows = continuum[arm]
        return all(np.isfinite(v["err_deg"]) and v["err_deg"] <= ERR_MAX_DEG
                   and v["circvar"] <= CIRCVAR_MAX for v in rows.values())

    def mean_err(arm):
        errs = [e if np.isfinite(e) else 180.0 for e in tracking[arm]]
        return float(np.mean(errs)) if errs else float("nan")

    def bar2(arm):
        return bool(np.isfinite(mean_err(arm))
                    and mean_err(arm) <= ERR_MAX_DEG)

    real_err = mean_err("real")
    rewired = [a for a in continuum if a != "real"]
    bars = {
        "continuum": bool(bar1("real")),
        "tracking": bool(bar2("real")),
        "wiring_specific": bool(
            all(real_err < mean_err(a) for a in rewired)
            and not any(bar1(a) and bar2(a) for a in rewired)),
    }
    return {
        "bars": bars,
        "mean_tracking_err": {a: mean_err(a) for a in continuum},
        "verdict": "PASS" if all(bars.values()) else "KILL",
    }


def check_prerequisites() -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not (ROOT / CONFIG).exists():
        missing.append(f"config: {CONFIG}")
    for mod in ("scipy",):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    return missing


# ---------------------------------------------------------------------------
# Data-gated assembly (local host only; cx_ring loading verbatim)
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-CX-HEADING-LATENT kill test (data-gated)")
    parser.add_argument("--config", default=CONFIG)
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites()
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("Run where the compiled runtime lives "
              "(docs/arenas/task9_cx_latent/runbook.md).")
        return 3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    from flygi.arc.factory import build_connectome_policy
    from flygi.config import load_config
    from flygi.dynamics.rate import RateParameters, ScipyRateNetwork

    class _NullActions:
        RESET = 0

        @staticmethod
        def from_id(identifier: int) -> int:
            return identifier

    config = load_config(ROOT / args.config)
    assembled = build_connectome_policy(config, _NullActions)
    connectivity = assembled.policy._network.connectivity
    node_count = assembled.policy._network.node_count
    metadata_dir = Path(config.graph.output_dir)
    if not metadata_dir.is_absolute():
        metadata_dir = ROOT / metadata_dir
    with np.load(metadata_dir / "node_metadata.npz", allow_pickle=False) as z:
        types = z["type"].astype("U")
        instances = z["instance"].astype("U")
    log(f"graph loaded: {node_count} nodes in {time.time() - started:.1f}s")

    # CX indices + composition gate (BLOCKED on mismatch).
    cx_idx = np.flatnonzero(np.isin(types, CX_TYPES))
    counts = {t: int((types == t).sum()) for t in EXPECTED_COUNTS}
    log(f"CX block: {cx_idx.size} nodes, composition {counts}")
    if counts != EXPECTED_COUNTS:
        log(f"BLOCKED: composition deviates from {EXPECTED_COUNTS}")
        return 3

    # EPG wedge angles + PEN_a hemispheres (cx_ring verbatim).
    epg = np.flatnonzero(types == "EPG")
    angles = np.full(epg.size, np.nan)
    for i, name in enumerate(instances[epg]):
        match = WEDGE_RE.search(name)
        if match:
            side, wedge = match.group(1), int(match.group(2))
            angles[i] = ((wedge - 1) * 2 + (0 if side == "L" else 1)) * 22.5
    keep = ~np.isnan(angles)
    epg, angles = epg[keep], angles[keep]
    radians = np.deg2rad(angles)
    pen_a = np.flatnonzero(types == "PEN_a(PEN1)")
    pen_left, pen_right = [], []
    for idx, name in zip(pen_a, instances[pen_a]):
        match = WEDGE_RE.search(name)
        if match:
            (pen_left if match.group(1) == "L" else pen_right).append(int(idx))
    pen_left = np.asarray(pen_left, dtype=np.int64)
    pen_right = np.asarray(pen_right, dtype=np.int64)

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

    unstable = {a: [0, 0] for a in ("real", "rw0", "rw1", "rw2")}

    def advance(network, state, drive, steps, arm):
        for _ in range(steps):
            state = network.advance(state, drive,
                                    internal_steps=INTERNAL_STEPS)
        unstable[arm][1] += 1
        if not np.all(np.isfinite(state)):
            unstable[arm][0] += 1
        return state

    def rotation_rate(network, state, drive, steps, arm):
        _, previous, _ = read(state)
        deltas = []
        for _ in range(steps):
            state = network.advance(state, drive,
                                    internal_steps=INTERNAL_STEPS)
            _, angle, _ = read(state)
            if not (np.isnan(angle) or np.isnan(previous)):
                deltas.append((angle - previous + 180.0) % 360.0 - 180.0)
            previous = angle
        unstable[arm][1] += 1
        if len(deltas) < MIN_VALID_DELTAS:
            return float("nan")
        return float(np.mean(deltas))

    def build_network(matrix):
        return ScipyRateNetwork(
            matrix,
            RateParameters(internal_steps=INTERNAL_STEPS, leak=LEAK,
                           recurrent_gain=GAIN, bias=0.0),
            copy_connectivity=False,
        )

    def seeded_settled(network, target_deg, arm):
        state = network.initial_state()
        state = advance(network, state, wedge_drive(target_deg),
                        WRITE_STEPS, arm)
        return advance(network, state, zero, SETTLE_STEPS, arm)

    sequences = make_sequences()
    log(f"sequences (seed {TRACK_SEED}): {sequences}")

    # --- PRECHECK + calibration on the REAL arm (AC-2 gate) -----------------
    real_net = build_network(connectivity)
    state = seeded_settled(real_net, CAL_ANGLE, "real")
    release_mass, _, _ = read(state)
    state = advance(real_net, state, zero, DARK_STEPS - SETTLE_STEPS, "real")
    final_mass, final_angle, final_cv = read(state)
    retention = final_mass / release_mass if release_mass > DEAD_MASS else 0.0
    log(f"precheck (cal {CAL_ANGLE}): retention {retention:.4f}, "
        f"circvar {final_cv:.3f}, angle {final_angle:.1f}")
    if retention < RETENTION_MIN or final_cv > CIRCVAR_MAX:
        log("BLOCKED: calibration-angle persistence precheck failed "
            "(AC-2: the measured gain-1.5 regime did not reproduce)")
        return 3

    cal_state = seeded_settled(real_net, CAL_ANGLE, "real")
    rate_left = rotation_rate(real_net, cal_state.copy(), pen_left_drive,
                              ROTATION_STEPS, "real")
    rate_right = rotation_rate(real_net, cal_state.copy(), pen_right_drive,
                               ROTATION_STEPS, "real")
    log(f"calibrated rates: L {rate_left:.3f}, R {rate_right:.3f} deg/step")
    if (np.isnan(rate_left) or np.isnan(rate_right)
            or rate_left * rate_right >= 0
            or min(abs(rate_left), abs(rate_right)) < RATE_MIN_DEG_PER_STEP):
        log("BLOCKED (instrument-level guard, labeled in the docstring): "
            "no signed rate basis -- the measured steering regime did not "
            "reproduce, so the command integral is undefined")
        return 3

    # --- arms ----------------------------------------------------------------
    arms: dict[str, Any] = {"real": real_net}
    for s in REWIRE_SEEDS:
        log(f"building CX-block rewire seed {REWIRE_SEED_BASE + s}...")
        arms[f"rw{s}"] = build_network(
            cx_block_rewire(connectivity, cx_idx, REWIRE_SEED_BASE + s))

    continuum: dict[str, Any] = {}
    tracking: dict[str, Any] = {}
    for arm, network in arms.items():
        rows = {}
        for target in HELDOUT_ANGLES:
            state = seeded_settled(network, target, arm)
            state = advance(network, state, zero, DARK_STEPS - SETTLE_STEPS,
                            arm)
            _, angle, cv = read(state)
            rows[str(target)] = {"final_angle": angle, "circvar": cv,
                                 "err_deg": circ_err_deg(angle, target)}
        continuum[arm] = rows
        errs = []
        for sequence in sequences:
            state = seeded_settled(network, CAL_ANGLE, arm)
            _, start_angle, _ = read(state)
            for command in sequence:
                drive = {"L": pen_left_drive, "R": pen_right_drive,
                         "off": zero}[command]
                state = advance(network, state, drive, SEGMENT_STEPS, arm)
            _, end_angle, _ = read(state)
            predicted = (start_angle + integrate_commands(
                sequence, rate_left, rate_right)) % 360.0
            errs.append(circ_err_deg(end_angle, predicted))
        tracking[arm] = errs
        log(f"[{arm}] continuum "
            + " ".join(f"{a}:{v['err_deg']:.1f}d/cv{v['circvar']:.2f}"
                       for a, v in rows.items())
            + " | tracking " + " ".join(f"{e:.1f}" for e in errs))

    worst = max(u[0] / u[1] for u in unstable.values() if u[1])
    if worst > MAX_UNSTABLE_FRACTION:
        log(f"BLOCKED: unstable fraction {worst:.2f} exceeds "
            f"{MAX_UNSTABLE_FRACTION}")
        return 3

    out = assemble_verdict(continuum, tracking)
    record = {
        "hypothesis": "H-CX-HEADING-LATENT",
        "gain": GAIN, "leak": LEAK,
        "precheck": {"retention": retention, "circvar": final_cv},
        "calibrated_rates": {"left": rate_left, "right": rate_right},
        "sequences": sequences,
        "continuum": continuum,
        "tracking": tracking,
        "mean_tracking_err": out["mean_tracking_err"],
        "unstable": {a: u[0] / u[1] if u[1] else 0.0
                     for a, u in unstable.items()},
        "bars": out["bars"],
        "verdict": out["verdict"],
        "elapsed_s": round(time.time() - started, 1),
    }
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(json.dumps(record, indent=2, default=float))
    log(f"VERDICT: {out['verdict']}")
    handle.close()
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
