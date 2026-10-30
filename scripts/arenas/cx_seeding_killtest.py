#!/usr/bin/env python3
"""H-CX-SEEDING-PROTOCOL -- the Task 9 reopening seeding probe.

PREREGISTRATION (EXPERIMENTS.yaml H-CX-SEEDING-PROTOCOL and docs/
arenas/task9_cx_latent/killtest_design_reopening.md, both frozen
2026-10-11 BEFORE this file existed, jointly with the class-3 design;
restated, not changed):

  - PREMISE: Stage B's failure was PROTOCOL-bound, not regime-bound --
    at an operating point with measured steering, some declared
    seeding protocol yields darkness persistence of a localized,
    POSITION-FAITHFUL bump in the real CX that the CX-block rewires
    lack.
  - MACHINERY: cx_heading_killtest.py's loading/drive/read VERBATIM
    (class-1 rate dynamics, full compiled graph, INTERNAL_STEPS 4) --
    enforced here by importing that module and calling its functions.
  - OPERATING POINTS (frozen): (gain 1.5, leak 0.3) and (gain 2.0,
    leak 0.3) -- the two points with measured C2 steering passes in
    the tracked cx_ring grid (git 09a998a).
  - PROTOCOLS (frozen; P1 is the built-in reproduction control,
    measured dead):
      P1 wedge-write, 20 steps, scale 1.0 (cx_ring verbatim)
      P2 wedge-write, 100 steps, scale 1.0 (sustained write)
      P3 wedge-write, 20 steps, scale 3.0 (the fc2_eb_ring declared
         STIM_AMP_FACTOR)
      P4 direct state injection: EPG state 1.0 inside the 90-deg
         wedge, 0.0 outside, all other nodes at initial_state; release
  - ANGLES: 22.5 (calibration, reported) + 112.5/202.5/292.5 (held
    out, decisional). Darkness 200 steps; release read after the
    10-step settle, final read at darkness end (Stage-B convention).
  - CELL PASS RULE (per operating point x protocol): at >= 2 of 3
    held-out angles -- retention >= 0.05 AND circvar <= 0.6 AND PVA
    within 45 deg of the seed angle.
  - WIRING BAR: at every real-passing cell, the 3 CX-block rewires
    (seeds 4242+0..2, Stage-B cx_block_rewire) must ALL fail the same
    rule. Evaluation order frozen for cost honesty: real arms on all
    8 cells first; rewires only at real-passing cells.
  - PASS iff >= 1 cell passes both bars. Every cell x arm run is
    reported in full. CONTEXT, non-decisional: at passing cells the
    Stage-B tracking sequences are run and reported -- the
    heading-latent VERDICT stays with a re-registered Stage B; this
    probe only decides whether such a re-registration is licensed and
    with which declared protocol.
  - BLOCKED (exit 3): runtime absent; CX composition !=
    46/20/22/42/18; instability (non-finite states) in > 20% of runs
    in any arm.

Data gate: runs where the compiled runtime lives. Pure parts
(protocol table, injection, cell rule, verdict) are unit-tested
in-cloud with a stub network.

Run:    python scripts/arenas/cx_seeding_killtest.py
Output: results/arenas/cx_seeding_killtest.json (+ .log)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- Stage-B machinery, imported VERBATIM (the registration's clause) --------
_HK_PATH = ROOT / "scripts/arenas/cx_heading_killtest.py"
_spec = importlib.util.spec_from_file_location("cx_heading_killtest",
                                               _HK_PATH)
hk = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("cx_heading_killtest", hk)
_spec.loader.exec_module(hk)

circular_stats = hk.circular_stats
circ_err_deg = hk.circ_err_deg
cx_block_rewire = hk.cx_block_rewire
make_sequences = hk.make_sequences
integrate_commands = hk.integrate_commands

INTERNAL_STEPS = hk.INTERNAL_STEPS
CAL_ANGLE = hk.CAL_ANGLE
HELDOUT_ANGLES = hk.HELDOUT_ANGLES
WEDGE_SPAN_DEG = hk.WEDGE_SPAN_DEG
SETTLE_STEPS = hk.SETTLE_STEPS
DARK_STEPS = hk.DARK_STEPS
ROTATION_STEPS = hk.ROTATION_STEPS
PEN_DRIVE_SCALE = hk.PEN_DRIVE_SCALE
MIN_VALID_DELTAS = hk.MIN_VALID_DELTAS
DEAD_MASS = hk.DEAD_MASS
RETENTION_MIN = hk.RETENTION_MIN
CIRCVAR_MAX = hk.CIRCVAR_MAX
ERR_MAX_DEG = hk.ERR_MAX_DEG
RATE_MIN_DEG_PER_STEP = hk.RATE_MIN_DEG_PER_STEP
REWIRE_SEED_BASE = hk.REWIRE_SEED_BASE
REWIRE_SEEDS = hk.REWIRE_SEEDS
MAX_UNSTABLE_FRACTION = hk.MAX_UNSTABLE_FRACTION
CX_TYPES = hk.CX_TYPES
EXPECTED_COUNTS = hk.EXPECTED_COUNTS
CONFIG = hk.CONFIG
RUNTIME_DIR = hk.RUNTIME_DIR
WEDGE_RE = hk.WEDGE_RE

# --- probe-specific frozen design (killtest_design_reopening.md) -------------
OPERATING_POINTS = ((1.5, 0.3), (2.0, 0.3))
PROTOCOLS = {
    "P1": {"kind": "wedge", "steps": 20, "scale": 1.0},
    "P2": {"kind": "wedge", "steps": 100, "scale": 1.0},
    "P3": {"kind": "wedge", "steps": 20, "scale": 3.0},
    "P4": {"kind": "inject"},
}
CELL_MIN_ANGLES = 2
OUT_JSON = ROOT / "results/arenas/cx_seeding_killtest.json"


# ---------------------------------------------------------------------------
# Pure plumbing (unit-tested in-cloud)
# ---------------------------------------------------------------------------

def wedge_mask(angles: np.ndarray, target_deg: float) -> np.ndarray:
    """cx_ring verbatim: EPG cells whose wedge angle lies within the
    90-deg span centered on the target."""
    distance = np.abs((angles - target_deg + 180.0) % 360.0 - 180.0)
    return distance <= WEDGE_SPAN_DEG / 2.0


def injected_state(initial_state: np.ndarray, epg: np.ndarray,
                   angles: np.ndarray, target_deg: float) -> np.ndarray:
    """P4 (registration verbatim): EPG state 1.0 inside the wedge,
    0.0 outside, all other nodes left at initial_state."""
    state = np.array(initial_state, copy=True)
    inside = wedge_mask(angles, target_deg)
    state[epg[inside]] = 1.0
    state[epg[~inside]] = 0.0
    return state


def seed_state(network, protocol: dict, target_deg: float,
               node_count: int, epg: np.ndarray, angles: np.ndarray,
               advance) -> np.ndarray:
    """Produce the seeded state for one protocol at one angle.
    advance(network, state, drive, steps) is the caller's stepping
    closure (carries instability accounting)."""
    if protocol["kind"] == "wedge":
        drive = np.zeros(node_count, dtype=np.float32)
        drive[epg[wedge_mask(angles, target_deg)]] = \
            np.float32(protocol["scale"])
        state = network.initial_state()
        return advance(network, state, drive, protocol["steps"])
    if protocol["kind"] == "inject":
        return injected_state(network.initial_state(), epg, angles,
                              target_deg)
    raise ValueError(f"unknown protocol kind: {protocol['kind']}")


def run_cell(network, protocol: dict, node_count: int, epg: np.ndarray,
             angles: np.ndarray, radians: np.ndarray, advance) -> dict:
    """One (operating point x protocol) arm: calibration angle
    (context) + the 3 held-out angles (decisional). Stage-B read
    convention: release after the 10-step settle, final at darkness
    end; retention = final mass / release mass."""
    zero = np.zeros(node_count, dtype=np.float32)

    def read(state):
        return circular_stats(np.maximum(state[epg], 0.0), radians)

    rows = {}
    for target in (CAL_ANGLE,) + tuple(HELDOUT_ANGLES):
        state = seed_state(network, protocol, target, node_count, epg,
                           angles, advance)
        state = advance(network, state, zero, SETTLE_STEPS)
        release_mass, _, _ = read(state)
        state = advance(network, state, zero, DARK_STEPS - SETTLE_STEPS)
        final_mass, final_angle, final_cv = read(state)
        retention = (final_mass / release_mass
                     if release_mass > DEAD_MASS else 0.0)
        rows[str(target)] = {
            "retention": retention, "circvar": final_cv,
            "final_angle": final_angle,
            "err_deg": circ_err_deg(final_angle, target),
            "held_out": target != CAL_ANGLE}
    return rows


def cell_pass(rows: dict) -> bool:
    """The frozen cell rule: >= 2 of the 3 HELD-OUT angles with
    retention >= 0.05 AND circvar <= 0.6 AND PVA within 45 deg."""
    held = [r for r in rows.values() if r.get("held_out")]
    good = sum(1 for r in held
               if r["retention"] >= RETENTION_MIN
               and r["circvar"] <= CIRCVAR_MAX
               and np.isfinite(r["err_deg"])
               and r["err_deg"] <= ERR_MAX_DEG)
    return good >= CELL_MIN_ANGLES


def assemble_verdict(cells: list) -> str:
    """PASS iff >= 1 cell has the real arm passing AND every rewire
    failing the same rule (wiring bar). Cells without rewire runs
    cannot be decisive."""
    for cell in cells:
        if cell.get("real_pass") and cell.get("rewires") and \
                all(not rw["pass"] for rw in cell["rewires"]) and \
                len(cell["rewires"]) == len(REWIRE_SEEDS):
            return "PASS"
    return "KILL"


def check_prerequisites() -> list[str]:
    return hk.check_prerequisites()


# ---------------------------------------------------------------------------
# Data-gated assembly (local host only; Stage-B loading verbatim)
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-CX-SEEDING-PROTOCOL probe (data-gated)")
    parser.add_argument("--config", default=CONFIG)
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites()
    if missing:
        print("BLOCKED -- the probe cannot run here. Missing:")
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

    cx_idx = np.flatnonzero(np.isin(types, CX_TYPES))
    counts = {t: int((types == t).sum()) for t in EXPECTED_COUNTS}
    log(f"CX block: {cx_idx.size} nodes, composition {counts}")
    if counts != EXPECTED_COUNTS:
        log(f"BLOCKED: composition deviates from {EXPECTED_COUNTS}")
        return 3

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
    pen_left_drive = np.zeros(node_count, dtype=np.float32)
    pen_left_drive[pen_left] = np.float32(PEN_DRIVE_SCALE)
    pen_right_drive = np.zeros(node_count, dtype=np.float32)
    pen_right_drive[pen_right] = np.float32(PEN_DRIVE_SCALE)

    unstable = {a: [0, 0] for a in
                ("real",) + tuple(f"rw{s}" for s in REWIRE_SEEDS)}

    def make_advance(arm):
        def advance(network, state, drive, steps):
            for _ in range(steps):
                state = network.advance(state, drive,
                                        internal_steps=INTERNAL_STEPS)
            unstable[arm][1] += 1
            if not np.all(np.isfinite(state)):
                unstable[arm][0] += 1
            return state
        return advance

    def build_network(matrix, gain, leak):
        return ScipyRateNetwork(
            matrix,
            RateParameters(internal_steps=INTERNAL_STEPS, leak=leak,
                           recurrent_gain=gain, bias=0.0),
            copy_connectivity=False,
        )

    def read(state):
        return circular_stats(np.maximum(state[epg], 0.0), radians)

    def rotation_rate(network, state, drive, advance):
        _, previous, _ = read(state)
        deltas = []
        for _ in range(ROTATION_STEPS):
            state = network.advance(state, drive,
                                    internal_steps=INTERNAL_STEPS)
            _, angle, _ = read(state)
            if not (np.isnan(angle) or np.isnan(previous)):
                deltas.append((angle - previous + 180.0) % 360.0 - 180.0)
            previous = angle
        if len(deltas) < MIN_VALID_DELTAS:
            return float("nan")
        return float(np.mean(deltas))

    def tracking_context(network, protocol, advance):
        """CONTEXT, non-decisional (registration): the Stage-B
        sequences on a passing cell, seeded by ITS protocol. Reported
        only; the heading-latent verdict stays with a re-registered
        Stage B."""
        cal = seed_state(network, protocol, CAL_ANGLE, node_count, epg,
                         angles, advance)
        cal = advance(network, cal, zero, SETTLE_STEPS)
        rate_left = rotation_rate(network, cal.copy(), pen_left_drive,
                                  advance)
        rate_right = rotation_rate(network, cal.copy(), pen_right_drive,
                                   advance)
        out = {"rate_left": rate_left, "rate_right": rate_right}
        if (np.isnan(rate_left) or np.isnan(rate_right)
                or rate_left * rate_right >= 0
                or min(abs(rate_left), abs(rate_right))
                < RATE_MIN_DEG_PER_STEP):
            out["note"] = ("no signed rate basis at this cell; "
                           "sequences not run")
            return out
        sequences = make_sequences()
        errs = []
        for sequence in sequences:
            state = seed_state(network, protocol, CAL_ANGLE, node_count,
                               epg, angles, advance)
            state = advance(network, state, zero, SETTLE_STEPS)
            _, start_angle, _ = read(state)
            for command in sequence:
                drive = {"L": pen_left_drive, "R": pen_right_drive,
                         "off": zero}[command]
                state = advance(network, state, drive, hk.SEGMENT_STEPS)
            _, end_angle, _ = read(state)
            predicted = (start_angle + integrate_commands(
                sequence, rate_left, rate_right)) % 360.0
            errs.append(circ_err_deg(end_angle, predicted))
        out["sequences"] = sequences
        out["final_errors_deg"] = errs
        return out

    # --- real arms on ALL 8 cells first (frozen evaluation order) -----------
    real_advance = make_advance("real")
    cells: list[dict[str, Any]] = []
    real_nets = {}
    for gain, leak in OPERATING_POINTS:
        real_nets[(gain, leak)] = build_network(connectivity, gain, leak)
        for pname, protocol in PROTOCOLS.items():
            rows = run_cell(real_nets[(gain, leak)], protocol, node_count,
                            epg, angles, radians, real_advance)
            passed = cell_pass(rows)
            cells.append({"gain": gain, "leak": leak, "protocol": pname,
                          "real_rows": rows, "real_pass": bool(passed)})
            held = {a: r for a, r in rows.items() if r["held_out"]}
            log(f"[real {gain}/{leak} {pname}] pass={passed} "
                + " ".join(f"{a}: ret {r['retention']:.4f} cv "
                           f"{r['circvar']:.3f} err {r['err_deg']:.1f}"
                           for a, r in held.items()))

    # --- rewires at real-passing cells only (decision-identical) ------------
    rewired_matrices = {}
    passing = [c for c in cells if c["real_pass"]]
    if passing:
        for s in REWIRE_SEEDS:
            log(f"building CX-block rewire seed {REWIRE_SEED_BASE + s}...")
            rewired_matrices[s] = cx_block_rewire(
                connectivity, cx_idx, REWIRE_SEED_BASE + s)
    for cell in passing:
        key = (cell["gain"], cell["leak"])
        protocol = PROTOCOLS[cell["protocol"]]
        cell["rewires"] = []
        for s in REWIRE_SEEDS:
            net = build_network(rewired_matrices[s], *key)
            rows = run_cell(net, protocol, node_count, epg, angles,
                            radians, make_advance(f"rw{s}"))
            rw_pass = cell_pass(rows)
            cell["rewires"].append({"seed": REWIRE_SEED_BASE + s,
                                    "rows": rows, "pass": bool(rw_pass)})
            log(f"[rw{s} {key[0]}/{key[1]} {cell['protocol']}] "
                f"pass={rw_pass}")
        cell["wiring_bar"] = all(not rw["pass"] for rw in cell["rewires"])
        cell["decisive"] = bool(cell["wiring_bar"])
        if cell["decisive"]:
            log(f"tracking context at decisive cell {key} "
                f"{cell['protocol']}...")
            cell["tracking_context"] = tracking_context(
                real_nets[key], protocol, real_advance)

    worst = max(u[0] / u[1] for u in unstable.values() if u[1])
    if worst > MAX_UNSTABLE_FRACTION:
        log(f"BLOCKED: unstable fraction {worst:.2f} exceeds "
            f"{MAX_UNSTABLE_FRACTION}")
        return 3

    verdict = assemble_verdict(cells)
    record = {
        "hypothesis": "H-CX-SEEDING-PROTOCOL",
        "operating_points": [list(p) for p in OPERATING_POINTS],
        "protocols": {k: dict(v) for k, v in PROTOCOLS.items()},
        "cells": cells,
        "unstable": {a: u[0] / u[1] if u[1] else 0.0
                     for a, u in unstable.items()},
        "verdict": verdict,
        "elapsed_s": round(time.time() - started, 1),
    }
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(json.dumps({k: v for k, v in record.items() if k != "cells"},
                   indent=2, default=float))
    log(f"VERDICT: {verdict}")
    handle.close()
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
