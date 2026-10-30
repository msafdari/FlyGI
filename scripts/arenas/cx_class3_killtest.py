#!/usr/bin/env python3
"""H-CX-CLASS3-COMPASS -- the Task 9 reopening class-3 kill test.

PREREGISTRATION (EXPERIMENTS.yaml H-CX-CLASS3-COMPASS and docs/arenas/
task9_cx_latent/killtest_design_reopening.md, both frozen 2026-10-11
BEFORE this file existed, jointly with the seeding probe; restated,
not changed):

  - MODEL CLASS ("class 3 (CX)"): the Kakaria & de Bivort 2017 /
    Pisokas, Heinze & Webb 2020 template-LIF -- the published model
    class where idealized fly-topology ring attractors work. CODE
    parameter values (the registered sweep measured a paper-vs-code
    discrepancy; the code set is pinned): Cm 20 nF, Rm 1 MOhm
    (tau_m 20 ms), V_rest -52 mV, threshold -45 mV, 2.2 ms AP
    template ending at -72 mV (acts as refractory), unitary PSC =
    quarter-sine rise 2 ms + exponential decay half-life 5 ms, peak
    5 nA, truncated at 7 half-lives; equal-magnitude opposite-sign
    inhibition; forward Euler dt 1e-4 s; background Poisson 5 Hz;
    heading drive von Mises kappa 3*pi/4, min 5 Hz, peak 190 Hz.
    (AP template SHAPE between its pinned endpoints is the
    instrument's operationalization -- the literature marks it
    cosmetic; its duration and -72 mV endpoint are the pinned parts.)
  - SUBSTRATE: the standalone 148-neuron MaleCNS CX (AC-8), weights =
    |synapse count| x signed per-connection-class scale (AC-6): scale
    chosen so the class MEAN total drive per postsynaptic cell per
    presynaptic spike equals Pisokas's optimized fly class weight
    (unitary-PSC equivalents): E-PG->P-EN/P-EG 99.968, E-PG->Delta7
    47.917, P-EN/P-EG->E-PG 6.072, Delta7->P-EN/P-EG -35.677,
    Delta7->Delta7 -19.336. Role map: PEN_a and PEN_b -> P-EN; PEG ->
    P-EG; classes absent from their 4-type circuit get unit magnitude
    6.072 (the smallest excitatory scale) with the compiled NT sign.
    Nothing is fitted.
  - VARIANT GRID (declared, all reported): global synaptic scale in
    {0.5, 1.0, 2.0} x inhibitory-class scale in {1.0, 2.0}.
  - GATE per grid point, real wiring: G1 -- 8 write angles every
    45 deg (1 s von Mises drive, 2 s darkness on background);
    read = EPG spike counts, final 250 ms vs the 250 ms at release;
    angle passes iff retention >= 0.05, circvar <= 0.6, PVA within
    45 deg of the write angle; G1 passes iff >= 6 of 8. G2 -- from
    settled states, one-hemisphere PEN_a Poisson drive (190 Hz peak)
    left vs right for 1 s -> opposite-signed PVA rotation, both
    |rate| >= 9 deg/s.
  - NULL BAR: at every real-passing point, all 3 degree-preserving
    rewires of the standalone matrix (seeds 4242+0..2) fail G1 there.
  - PASS iff >= 1 point clears G1+G2 with all rewires failing G1.
  - BLOCKED: runtime absent; composition != 46/20/22/42/18;
    non-finite membrane in > 20% of runs in any arm; or the IN-CLOUD
    VALIDATION GATE failing -- the engine must reproduce the
    published Pisokas 60-neuron fly bump (their connectivity labels
    and weights verbatim, tests/data/pisokas_fly_connectivity.npz):
    bump forms, persists 2 s of darkness with PVA within 45 deg and
    circvar <= 0.6 on every declared trial seed, and the trial-MEAN
    bump width sits in 60-120 deg (their Table 1: 88.3) under the
    PUBLISHED estimator (dated pre-data-contact amendment 2026-10-11:
    their Table-1 width is computed by measureBump1 on the
    left-hemisphere P-EN raster columns, (k-1)/8*360 deg, over their
    100 ms window, and is itself a trial mean of that 45-deg-quantized
    statistic -- see killtest_design_reopening.md). Asserted by unit
    test BEFORE any data contact.

Run:    python scripts/arenas/cx_class3_killtest.py
Output: results/arenas/cx_class3_killtest.json (+ .log)
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

# --- frozen physiology (Kakaria/Pisokas CODE values; do not tune) -----------
DT_S = 1e-4
CM_F = 2e-8                 # 20 nF (code value; paper text says 2 nF)
RM_OHM = 1e6                # 1 MOhm (code value; paper text says 10 MOhm)
V_REST = -52e-3
V_THRESH = -45e-3
AP_MS = 2.2                 # realized template length (22 samples)
AP_END = -72e-3             # undershoot = effective reset
AP_PEAK = 20e-3
PSC_RISE_MS = 2.0
PSC_HALF_MS = 5.0
PSC_HALFLIVES = 7
PSC_PEAK_A = 5e-9
BG_HZ = 5.0
DRIVE_PEAK_HZ = 190.0
VM_KAPPA = 3.0 * np.pi / 4.0

# --- frozen protocol/gate constants (killtest_design_reopening.md) ----------
WRITE_S = 1.0
DARK_S = 2.0
READ_S = 0.25
STEER_S = 1.0
G1_ANGLES = tuple(22.5 + 45.0 * k for k in range(8))
G1_MIN_PASS = 6
RETENTION_MIN = 0.05
CIRCVAR_MAX = 0.6
ERR_MAX_DEG = 45.0
STEER_RATE_MIN_DEG_S = 9.0
GRID = tuple((g, i) for g in (0.5, 1.0, 2.0) for i in (1.0, 2.0))
REWIRE_SEED_BASE = 4242
REWIRE_SEEDS = (0, 1, 2)
MAX_UNSTABLE_FRACTION = 0.20
RUN_SEED_BASE = 20261011
# validation-gate trials (declared; the published Table-1 width is a
# trial MEAN, and the estimator is 45-deg-quantized, so the gate
# statistic is the mean over these fixed seeds)
VALIDATION_SEEDS = (7, 8, 9, 10, 11)

PISOKAS_WEIGHTS = {
    ("E-PG", "P-EN"): 99.9680554605268,
    ("E-PG", "P-EG"): 99.9680554605268,
    ("E-PG", "Delta7"): 47.9173822984772,
    ("P-EN", "E-PG"): 6.07203896674184,
    ("P-EG", "E-PG"): 6.07203896674184,
    ("Delta7", "P-EN"): -35.6772759590409,
    ("Delta7", "P-EG"): -35.6772759590409,
    ("Delta7", "Delta7"): -19.3358579258735,
}
FALLBACK_MAGNITUDE = 6.07203896674184
ROLE = {"EPG": "E-PG", "PEN_a(PEN1)": "P-EN", "PEN_b(PEN2)": "P-EN",
        "PEG": "P-EG", "Delta7": "Delta7"}
CX_TYPES = tuple(ROLE)
EXPECTED_COUNTS = {"EPG": 46, "PEN_a(PEN1)": 20, "PEN_b(PEN2)": 22,
                   "Delta7": 42, "PEG": 18}

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
FIXTURE = ROOT / "tests/data/pisokas_fly_connectivity.npz"
OUT_JSON = ROOT / "results/arenas/cx_class3_killtest.json"
WEDGE_RE = re.compile(r"_([LR])(\d)")


# ---------------------------------------------------------------------------
# Templates and engine (pure numpy; validated against the published
# Pisokas circuit in-cloud before any data contact)
# ---------------------------------------------------------------------------

def ap_template() -> np.ndarray:
    """2.2 ms voltage template from threshold: half-cosine rise to
    +20 mV (10 samples) then half-cosine fall to -72 mV (12 samples).
    Shape between endpoints is the declared operationalization."""
    up = V_THRESH + (AP_PEAK - V_THRESH) * (
        1 - np.cos(np.linspace(0, np.pi, 10))) / 2
    down = AP_PEAK + (AP_END - AP_PEAK) * (
        1 - np.cos(np.linspace(0, np.pi, 12))) / 2
    return np.concatenate([up, down])


def psc_template() -> np.ndarray:
    """Unitary PSC: quarter-sine rise over 2 ms to 5 nA, exponential
    decay with 5 ms half-life, truncated at 7 half-lives."""
    rise_n = int(round(PSC_RISE_MS * 1e-3 / DT_S))
    fall_n = int(round(PSC_HALFLIVES * PSC_HALF_MS * 1e-3 / DT_S))
    rise = PSC_PEAK_A * np.sin(np.linspace(0, np.pi / 2, rise_n,
                                           endpoint=False))
    t = np.arange(fall_n) * DT_S * 1e3
    fall = PSC_PEAK_A * np.power(2.0, -t / PSC_HALF_MS)
    return np.concatenate([rise, fall])


class TemplateLIF:
    """The Kakaria/Pisokas current-based LIF with AP/PSC templates.
    W[post, pre] in unitary-PSC equivalents per presynaptic spike."""

    def __init__(self, W: np.ndarray, seed: int):
        self.W = np.asarray(W, dtype=np.float64)
        self.n = self.W.shape[0]
        self.rng = np.random.default_rng(seed)
        self.ap = ap_template()
        self.psc = psc_template()
        self.L = self.psc.size
        self.v = np.full(self.n, V_REST)
        self.phase = np.full(self.n, -1, dtype=np.int64)   # AP playback pos
        self.buf = np.zeros((self.L, self.n))              # future currents
        self.ptr = 0
        self.unstable = False

    def step(self, ext_rate_hz: np.ndarray) -> np.ndarray:
        """One dt. ext_rate_hz: per-neuron Poisson input rate; each
        external spike injects one unitary PSC. Returns spike mask."""
        ext = self.rng.random(self.n) < ext_rate_hz * DT_S
        if ext.any():
            idx = (self.ptr + np.arange(self.L)) % self.L
            self.buf[idx[:, None], np.flatnonzero(ext)[None, :]] += \
                self.psc[:, None]
        current = self.buf[self.ptr].copy()
        self.buf[self.ptr] = 0.0
        self.ptr = (self.ptr + 1) % self.L

        playing = self.phase >= 0
        free = ~playing
        dv = ((V_REST - self.v[free]) / RM_OHM + current[free]) * (DT_S / CM_F)
        self.v[free] = self.v[free] + dv
        self.v[playing] = self.ap[self.phase[playing]]
        self.phase[playing] += 1
        done = self.phase >= self.ap.size
        self.v[done] = AP_END
        self.phase[done] = -1

        spikes = (self.v >= V_THRESH) & (self.phase < 0)
        if spikes.any():
            for j in np.flatnonzero(spikes):
                col = self.W[:, j]
                nz = np.flatnonzero(col)
                if nz.size:
                    idx = (self.ptr + np.arange(self.L)) % self.L
                    self.buf[idx[:, None], nz[None, :]] += \
                        np.outer(self.psc, col[nz])
            self.phase[spikes] = 0
            self.v[spikes] = self.ap[0]
        if not np.all(np.isfinite(self.v)):
            self.unstable = True
        return spikes


def circular_stats(activity, radians):
    mass = float(activity.sum())
    if mass <= 1e-9:
        return mass, float("nan"), 1.0
    vector = complex(np.sum(activity * np.exp(1j * radians)))
    angle = float(np.rad2deg(np.angle(vector)) % 360.0)
    return mass, angle, float(1.0 - abs(vector) / mass)


def circ_err_deg(a, b):
    if np.isnan(a) or np.isnan(b):
        return float("nan")
    return abs((a - b + 180.0) % 360.0 - 180.0)


def von_mises_rates(angles_deg: np.ndarray, center_deg: float) -> np.ndarray:
    """Per-cell drive rate: min-max-normalized von Mises mapped onto
    [BG_HZ, DRIVE_PEAK_HZ] (the Pisokas convention)."""
    x = np.exp(VM_KAPPA * np.cos(np.deg2rad(angles_deg - center_deg)))
    x = (x - x.min()) / max(x.max() - x.min(), 1e-12)
    return BG_HZ + (DRIVE_PEAK_HZ - BG_HZ) * x


def pisokas_block_angles(cells_per_block: int) -> np.ndarray:
    """Column angles for ONE hemisphere block under the published fly
    convention (ESTABLISHED; PBexperimentModified.m:259-269): the EB
    has 8 azimuth columns 45 deg apart; block cell j sits at column
    (j mod 8), so a 9-cell E-PG block's 9th cell duplicates column 1
    (their ``p = [p; p(1)]``). Both hemisphere blocks are identical."""
    return 45.0 * (np.arange(cells_per_block) % 8)


def measure_bump1_deg(column_activity: np.ndarray,
                      circular: bool = True) -> float:
    """The PUBLISHED width estimator (ESTABLISHED; measureBump1.m,
    called by collect_stats_long_run.m:1697-1703 on the first 8 raster
    columns): threshold at (max-min)/2 strictly, take a contiguous
    above-threshold run of k columns, width = (k-1)/8 * 360 deg.
    Verbatim (circular=False) takes the FIRST run, which splits a bump
    wrapping the column boundary; circular=True takes the longest
    CIRCULAR run and equals the verbatim value whenever the bump does
    not wrap. 0.0 when no column clears threshold (their 'no bump')."""
    act = np.asarray(column_activity, dtype=np.float64)
    above = act > (act.max() - act.min()) / 2.0
    if not above.any():
        return 0.0
    if above.all():
        return 360.0
    if circular:
        # rotate a below-threshold column to the boundary, then the
        # longest linear run is the longest circular run
        shift = int(np.flatnonzero(~above)[0]) + 1
        above = np.roll(above, -shift)
        runs, k = [], 0
        for flag in above:
            k = k + 1 if flag else 0
            runs.append(k)
        best = max(runs)
        return (best - 1) / 8.0 * 360.0
    first = int(np.flatnonzero(above)[0])
    k = 0
    for flag in above[first:]:
        if not flag:
            break
        k += 1
    return (k - 1) / 8.0 * 360.0


def run_bump_protocol(engine: TemplateLIF, drive_idx: np.ndarray,
                      drive_angles: np.ndarray, read_idx: np.ndarray,
                      read_radians: np.ndarray, write_deg: float,
                      width_window: tuple[int, int] | None = None):
    """1 s von Mises drive + 2 s darkness; returns release/final reads
    and the final-window spike counts. width_window, used only by the
    validation gate, additionally accumulates counts over dark steps
    [lo, hi) -- the published width-measurement window."""
    n = engine.n
    rates = np.full(n, BG_HZ)
    rates[drive_idx] = von_mises_rates(drive_angles, write_deg)
    write_steps = int(round(WRITE_S / DT_S))
    dark_steps = int(round(DARK_S / DT_S))
    read_steps = int(round(READ_S / DT_S))

    counts = np.zeros(n)
    for k in range(write_steps):
        s = engine.step(rates)
        if k >= write_steps - read_steps:
            counts += s
    release = counts[read_idx].copy()

    bg = np.full(n, BG_HZ)
    counts = np.zeros(n)
    wcounts = np.zeros(n) if width_window is not None else None
    for k in range(dark_steps):
        s = engine.step(bg)
        if k >= dark_steps - read_steps:
            counts += s
        if width_window is not None and width_window[0] <= k < width_window[1]:
            wcounts += s
    final = counts[read_idx].copy()
    rel_mass, rel_angle, _ = circular_stats(release, read_radians)
    fin_mass, fin_angle, fin_cv = circular_stats(final, read_radians)
    retention = fin_mass / rel_mass if rel_mass > 1e-9 else 0.0
    out = {"retention": retention, "final_angle": fin_angle,
           "final_circvar": fin_cv,
           "err_deg": circ_err_deg(fin_angle, write_deg),
           "final_counts": final, "release_angle": rel_angle}
    if wcounts is not None:
        out["width_window_counts"] = wcounts
    return out


def g1_angle_pass(row) -> bool:
    return (row["retention"] >= RETENTION_MIN
            and row["final_circvar"] <= CIRCVAR_MAX
            and np.isfinite(row["err_deg"])
            and row["err_deg"] <= ERR_MAX_DEG)


def assemble_point_verdict(g1_rows: list, steer: dict) -> dict:
    n_pass = sum(g1_angle_pass(r) for r in g1_rows)
    g1 = n_pass >= G1_MIN_PASS
    g2 = bool(steer and np.isfinite(steer.get("rate_left", np.nan))
              and np.isfinite(steer.get("rate_right", np.nan))
              and steer["rate_left"] * steer["rate_right"] < 0
              and min(abs(steer["rate_left"]),
                      abs(steer["rate_right"])) >= STEER_RATE_MIN_DEG_S)
    return {"g1_n_pass": n_pass, "g1": bool(g1), "g2": g2}


def class_scales(counts_matrix, types: np.ndarray) -> dict:
    """AC-6: per-(pre-role, post-role) scale so the class MEAN total
    |count| drive per postsynaptic cell maps to the Pisokas class
    weight; fallback magnitude for unlisted role pairs (sign applied
    from the compiled matrix at expansion time)."""
    A = np.abs(np.asarray(counts_matrix.todense()
                          if hasattr(counts_matrix, "todense")
                          else counts_matrix, dtype=np.float64))
    roles = np.array([ROLE[t] for t in types])
    scales = {}
    for (pre_r, post_r), w in PISOKAS_WEIGHTS.items():
        pre_m = roles == pre_r
        post_m = roles == post_r
        block = A[np.ix_(post_m, pre_m)]
        per_post = block.sum(axis=1)
        mean_drive = float(per_post[per_post > 0].mean()) \
            if (per_post > 0).any() else 0.0
        scales[(pre_r, post_r)] = (w / mean_drive) if mean_drive > 0 else 0.0
    return scales


def expand_weights(signed_counts, types: np.ndarray) -> np.ndarray:
    """Per-edge weight = |count| x class scale (signed by the Pisokas
    class for mapped pairs; by the compiled sign at fallback unit
    magnitude otherwise, normalized per the same mean-drive rule)."""
    S = np.asarray(signed_counts.todense()
                   if hasattr(signed_counts, "todense")
                   else signed_counts, dtype=np.float64)
    A = np.abs(S)
    roles = np.array([ROLE[t] for t in types])
    scales = class_scales(S, types)
    W = np.zeros_like(A)
    role_names = sorted(set(roles.tolist()))
    for pre_r in role_names:
        pre_m = roles == pre_r
        for post_r in role_names:
            post_m = roles == post_r
            block = A[np.ix_(post_m, pre_m)]
            if not block.any():
                continue
            if (pre_r, post_r) in scales and scales[(pre_r, post_r)] != 0.0:
                W[np.ix_(post_m, pre_m)] = block * scales[(pre_r, post_r)]
            else:
                per_post = block.sum(axis=1)
                mean_drive = float(per_post[per_post > 0].mean())
                unit = FALLBACK_MAGNITUDE / mean_drive
                signs = np.sign(S[np.ix_(post_m, pre_m)])
                W[np.ix_(post_m, pre_m)] = block * unit * signs
    return W


def validate_engine_on_pisokas(seeds: tuple = VALIDATION_SEEDS) -> dict:
    """THE IN-CLOUD VALIDATION GATE: run the published 60-neuron fly
    circuit (their labels, their weights) through this engine; per
    trial the bump must form, persist 2 s, land within 45 deg,
    circvar <= 0.6; the MEAN bump width over the declared trials must
    sit in 60-120 deg under the PUBLISHED estimator (Table 1: 88.3
    deg, itself a trial mean of a 45-deg-quantized statistic).

    Geometry and estimator are the published code's own (dated
    amendment 2026-10-11, killtest_design_reopening.md; all
    ESTABLISHED, code-verified): neuron order [P-EN 16, P-EG 18,
    E-PG 18, Delta7 8] (collect_stats_long_run.m:328-332); the von
    Mises drive is sampled at the 8 EB column angles and the same
    profile is applied to both 9-cell E-PG hemisphere blocks, the 9th
    cell duplicating column 1 (PBexperimentModified.m:259-282); their
    Table-1 width is measureBump1 over the raster's first 8 columns =
    the LEFT-hemisphere P-ENs, one 45-deg column each
    (collect_stats_long_run.m:1697), averaged over their window of
    dark steps [end-2000, end-1000) (collect_stats_long_run.m:1701).
    Write center 120 deg = their default stim_neuron_list [4]:
    (4-1)/9*360."""
    z = np.load(FIXTURE, allow_pickle=False)
    labels = z["labels_post_pre"].astype(np.float64)
    W = np.zeros_like(labels)
    for lab, val in zip(z["weight_labels"], z["weight_values"]):
        W[np.isclose(labels, lab)] = val
    epg = z["epg_idx"]
    penpeg = z["penpeg_idx"]
    assert epg.size == 18 and penpeg.size == 34
    # ESTABLISHED layout: P-EN occupy indices 0..15, left hemisphere
    # first (their raster columns 1:8 are the width-readout population)
    assert (penpeg[:16] == np.arange(16)).all()
    pen_left = penpeg[:8]
    angles = np.concatenate([pisokas_block_angles(9),
                             pisokas_block_angles(9)])
    radians = np.deg2rad(angles)
    write_deg = 120.0
    dark_steps = int(round(DARK_S / DT_S))
    window = (dark_steps - 2000, dark_steps - 1000)
    trials, widths, bars_ok, unstable = [], [], [], False
    for seed in seeds:
        engine = TemplateLIF(W, seed=seed)
        row = run_bump_protocol(engine, epg, angles, epg, radians,
                                write_deg, width_window=window)
        pen_counts = row["width_window_counts"][pen_left]
        width = measure_bump1_deg(pen_counts, circular=True)
        widths.append(width)
        bars_ok.append(row["retention"] >= RETENTION_MIN
                       and row["final_circvar"] <= CIRCVAR_MAX
                       and np.isfinite(row["err_deg"])
                       and row["err_deg"] <= ERR_MAX_DEG)
        unstable = unstable or engine.unstable
        trials.append({
            "seed": seed, "retention": row["retention"],
            "err_deg": row["err_deg"], "circvar": row["final_circvar"],
            "width_deg": width,
            "width_verbatim_deg": measure_bump1_deg(pen_counts,
                                                    circular=False),
            "pen_left_counts": pen_counts.tolist()})
    mean_width = float(np.mean(widths))
    return {"trials": trials, "mean_width_deg": mean_width,
            "unstable": unstable,
            "pass": bool(all(bars_ok) and not unstable
                         and 60.0 <= mean_width <= 120.0)}


def check_prerequisites() -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not FIXTURE.exists():
        missing.append(f"validation fixture: {FIXTURE}")
    for mod in ("scipy",):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    return missing


# ---------------------------------------------------------------------------
# Data-gated assembly (local host only)
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-CX-CLASS3-COMPASS kill test (data-gated)")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites()
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        return 3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    gate = validate_engine_on_pisokas()
    log("validation gate (published Pisokas fly circuit): "
        f"pass={gate['pass']} mean_width={gate['mean_width_deg']:.1f}")
    for t in gate["trials"]:
        log(f"  seed {t['seed']}: retention {t['retention']:.3f} "
            f"err {t['err_deg']:.1f} circvar {t['circvar']:.3f} "
            f"width {t['width_deg']:.1f}")
    if not gate["pass"]:
        log("BLOCKED: the engine does not reproduce the published "
            "circuit -- invalid instrument, nothing claimed")
        return 3

    from flygi.connectome.subcircuit import extract_subcircuit, select_nodes
    from flygi.connectome.nulls import degree_preserving_rewire
    indices = select_nodes(RUNTIME_DIR,
                           type_patterns=("EPG", "PEN_a*", "PEN_b*",
                                          "Delta7", "PEG"))
    sub = extract_subcircuit(RUNTIME_DIR, indices)
    counts = {t: int((sub.types == t).sum()) for t in EXPECTED_COUNTS}
    log(f"subcircuit: {sub.node_count} nodes, composition {counts}")
    if counts != EXPECTED_COUNTS:
        log(f"BLOCKED: composition deviates from {EXPECTED_COUNTS}")
        return 3

    types = sub.types.astype("U")
    epg = np.flatnonzero(types == "EPG")
    wedge = np.full(epg.size, np.nan)
    for i, name in enumerate(sub.instances[epg].astype("U")):
        match = WEDGE_RE.search(name)
        if match:
            wedge[i] = ((int(match.group(2)) - 1) * 2
                        + (0 if match.group(1) == "L" else 1)) * 22.5
    keep = ~np.isnan(wedge)
    epg, epg_angles = epg[keep], wedge[keep]
    epg_radians = np.deg2rad(epg_angles)
    pen_a = np.flatnonzero(types == "PEN_a(PEN1)")
    pen_l, pen_r = [], []
    for idx, name in zip(pen_a, sub.instances[pen_a].astype("U")):
        match = WEDGE_RE.search(name)
        if match:
            (pen_l if match.group(1) == "L" else pen_r).append(int(idx))
    pen_l, pen_r = np.asarray(pen_l), np.asarray(pen_r)

    W_real = expand_weights(sub.matrix, types)
    unstable_runs = {"real": [0, 0], "null": [0, 0]}

    def bump_row(W, write_deg, seed, arm):
        engine = TemplateLIF(W, seed=seed)
        row = run_bump_protocol(engine, epg, epg_angles, epg, epg_radians,
                                write_deg)
        unstable_runs[arm][1] += 1
        unstable_runs[arm][0] += int(engine.unstable)
        return row

    def steering(W, seed):
        """Settle a bump at 22.5 then 1 s hemisphere PEN_a drive."""
        out = {}
        for label, idx in (("left", pen_l), ("right", pen_r)):
            engine = TemplateLIF(W, seed=seed)
            rates = np.full(engine.n, BG_HZ)
            rates[epg] = von_mises_rates(epg_angles, 22.5)
            for _ in range(int(round(WRITE_S / DT_S))):
                engine.step(rates)
            drive = np.full(engine.n, BG_HZ)
            if idx.size:
                drive[idx] = DRIVE_PEAK_HZ
            read_steps = int(round(READ_S / DT_S))
            window, angles_seq = np.zeros(engine.n), []
            for k in range(int(round(STEER_S / DT_S))):
                s = engine.step(drive)
                window += s
                if (k + 1) % read_steps == 0:
                    _, ang, _ = circular_stats(window[epg], epg_radians)
                    angles_seq.append(ang)
                    window[:] = 0.0
            deltas = [(b - a + 180.0) % 360.0 - 180.0
                      for a, b in zip(angles_seq, angles_seq[1:])
                      if not (np.isnan(a) or np.isnan(b))]
            out[f"rate_{label}"] = (float(np.mean(deltas)) / READ_S
                                    if len(deltas) >= 2 else float("nan"))
        return out

    grid_report = []
    verdict = "KILL"
    for gi, (g_scale, i_scale) in enumerate(GRID):
        W = W_real * g_scale
        inhib = W < 0
        W = np.where(inhib, W * i_scale, W)
        rows = [bump_row(W, a, RUN_SEED_BASE + gi * 100 + k, "real")
                for k, a in enumerate(G1_ANGLES)]
        steer = steering(W, RUN_SEED_BASE + gi * 100 + 50)
        point = assemble_point_verdict(rows, steer)
        entry = {"global_scale": g_scale, "inhib_scale": i_scale,
                 "g1_rows": [{k: v for k, v in r.items()
                              if k != "final_counts"} for r in rows],
                 "steer": steer, **point}
        log(f"[grid {g_scale}x/{i_scale}x] g1 {point['g1_n_pass']}/8 "
            f"g2={point['g2']} steer L {steer.get('rate_left', 'nan')} "
            f"R {steer.get('rate_right', 'nan')}")
        if point["g1"] and point["g2"]:
            null_fails = []
            for s in REWIRE_SEEDS:
                rw, _ = degree_preserving_rewire(
                    sub.matrix, seed=REWIRE_SEED_BASE + s)
                Wn = expand_weights(rw, types) * g_scale
                Wn = np.where(Wn < 0, Wn * i_scale, Wn)
                nrows = [bump_row(Wn, a, RUN_SEED_BASE + gi * 100 + k,
                                  "null") for k, a in enumerate(G1_ANGLES)]
                npoint = assemble_point_verdict(nrows, {})
                null_fails.append(not npoint["g1"])
                entry.setdefault("nulls", []).append(
                    {"seed": REWIRE_SEED_BASE + s,
                     "g1_n_pass": npoint["g1_n_pass"], "g1": npoint["g1"]})
                log(f"  null{s}: g1 {npoint['g1_n_pass']}/8")
            if all(null_fails):
                verdict = "PASS"
                entry["decisive"] = True
        grid_report.append(entry)

    worst = max(u[0] / u[1] for u in unstable_runs.values() if u[1])
    if worst > MAX_UNSTABLE_FRACTION:
        log(f"BLOCKED: unstable fraction {worst:.2f}")
        return 3

    record = {"hypothesis": "H-CX-CLASS3-COMPASS",
              "validation_gate": gate, "grid": grid_report,
              "verdict": verdict,
              "unstable": {k: (u[0] / u[1] if u[1] else 0.0)
                           for k, u in unstable_runs.items()},
              "elapsed_s": round(time.time() - started, 1)}
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(json.dumps({k: v for k, v in record.items() if k != "grid"},
                   indent=2, default=float))
    log(f"VERDICT: {verdict}")
    handle.close()
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
