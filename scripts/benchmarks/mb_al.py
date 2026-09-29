#!/usr/bin/env python3
"""Biological benchmark suite -- MUSHROOM BODY + ANTENNAL LOBE group.

Part of the fly-module verdict program, requirement 1 (physiology and
validation). Before any module verdict counts, the compiled MaleCNS rate
model (166,700 nodes, 24,994,595 signed edges; h <- (1-a)h + a*tanh(g*W*h +
input)) must reproduce this module's published fly results somewhere in
operating-point space. These are COMPUTATIONAL ANALOGUES of the published
findings, not replications: the model is a leaky signed tanh rate network,
"activity" is the positive lobe of a tanh state, and every mapping from an
experimental quantity onto a model quantity below is an ASSUMPTION declared
where it lives.

OPERATING GRID (fixed, shared across all benchmark groups):
  recurrent_gain in {0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5}
  x leak in {0.1, 0.3, 0.6}; internal_steps = 4 (deployed convention);
  bias 0. 21 points, swept SEQUENTIALLY in one process, one graph load.

================================ PREREGISTRATION ==============================
Everything in this block was fixed and committed BEFORE the sweep ran.
Misses are reported as misses; no band moves after results exist.

--- Benchmark M1: KC sparse coding -------------------------------------------
CITATIONS (Established): Turner GC, Bazhenov M, Laurent G (2008)
  "Olfactory representations by Drosophila mushroom body neurons",
  J Neurophysiol 99:734-746 -- KC odor responses are sparse (~5-10% of the
  population per odor). Honegger KS, Campbell RAA, Turner GC (2011)
  "Cellular-resolution population imaging reveals robust sparse coding in
  the Drosophila mushroom body", J Neurosci 31:11772-11785 -- ~5-10% KCs
  responsive per odor, robust across odors and concentrations.
  Lin AC, Bygrave AM, de Calignon A, Lee T, Miesenboeck G (2014)
  "Sparse, decorrelated odor coding in the mushroom body enhances learned
  odor discrimination", Nat Neurosci 17:559-568 -- APL feedback inhibition
  maintains KC sparseness; removing APL inhibition broadens KC activation,
  so MORE APL inhibition must not INCREASE the KC active fraction.
PROTOCOL (fixed):
  * Populations, resolved from node_metadata.npz exactly as the repo's
    mushroom-body bus does (src/flygi/encoding/mb_bus.py): PN = type
    contains one of ('adPN','lPN','vPN','ilPN','lvPN','l2PN'); KC = type
    startswith 'KC'; APL = type == 'APL'. Measured before preregistration:
    627 PNs across 162 glomerular types, 4,064 KCs, 2 APL,
    4,633 APL->KC edges (all negative), 22,581 PN->KC edges.
  * Odors: 7 distinct sparse patterns. Each odor = 24 of the 162 PN
    glomerular types (~15%), drawn without replacement by
    np.random.default_rng(20260929); every PN of a selected type is driven
    at amplitude A, all other input zero. ASSUMPTION: an "odor" is a
    uniform-amplitude subset of glomerular PN channels. Concentration is a
    nuisance parameter of the protocol, not of the claim, so A sweeps a
    FIXED ladder {0.02, 0.05, 0.1, 0.2, 0.5} declared here.
  * Stimulus: from the all-zeros state, hold the drive for 8 macro-steps
    (advance with internal_steps=4, i.e. 32 internal steps, matching the
    repo's step-32 readout convention); read the final state.
  * Baseline (per grid point, per network condition): initial_state(seed=
    20260929, scale=0.01), zero drive, 8 macro-steps; mu_b and sigma_b are
    the mean and std over the 4,064 KC positive-lobe activities of the
    final state. ASSUMPTION: the deterministic network needs a seeded
    epsilon initial state to expose its spontaneous-activity floor; with
    a literal zero state the pre-stimulus baseline is exactly zero by
    construction and a 2-sigma criterion is degenerate.
  * Active: KC i counts as responsive to an odor iff
    max(h_i, 0) > max(mu_b + 2*sigma_b, 1e-4)   (positive lobe only; the
    1e-4 floor guards sigma_b = 0). Per amplitude, the statistic is the
    MEDIAN active fraction across the 7 odors.
PASS BAND (preregistered): a grid point passes M1 iff the median active
  fraction lies in [0.03, 0.15] at >= 1 amplitude of the fixed ladder.
  best_value = the in-band median closest to 0.075 (the 5-10% band center)
  by |log(median/0.075)|; best_point = its grid point.

--- Benchmark M1b: APL directional check -------------------------------------
CITATION (Established): Lin et al. 2014 (above). Prior repo measurement
  (WORKLOG, H-APL, 2026-09-23, gain 2.0 / leak 0.3, histogram bus): on the
  positive lobe APL x2 -> 0.098, x4 -> 0.078 -- inhibition sparsifies, as
  Lin predicts. Re-measured here at every grid point with this protocol.
PROTOCOL (fixed): rebuild the network on a matrix whose 4,633 APL->KC
  weights are scaled x4 (fresh data array, shared indices/indptr -- the
  exact H-APL pattern from src/flygi/arc/factory.py; the original matrix is
  never mutated). Same 7 odors, same ladder, same baseline rule (recomputed
  on the scaled network -- ASSUMPTION: each "preparation" is measured
  against its own baseline, as in physiology).
PASS BAND (preregistered): an amplitude is EVALUABLE at a grid point iff
  the x1 median active fraction >= 0.01 there. The point passes M1b iff it
  has >= 1 evaluable amplitude and, at EVERY evaluable amplitude,
  median_x4 <= median_x1 + 0.005 (tolerance for numerical noise). Points
  with no evaluable amplitude are recorded as not-evaluable, not passes.
  best_value = mean over evaluable amplitudes of (median_x1 - median_x4),
  maximized over passing points (the most Lin-like sparsification).

--- Benchmark M2: PN sublinear gain normalization -----------------------------
CITATIONS (Established): Olsen SR, Wilson RI (2008) "Lateral presynaptic
  inhibition mediates gain control in an olfactory circuit", Nature
  452:956-960 -- PN responses saturate with increasing ORN input.
  Olsen SR, Bhandawat V, Wilson RI (2010) "Divisive normalization in
  olfactory population codes", Neuron 66:287-299 -- the PN input-output
  function is compressive/divisively normalized. NOTE: the program task
  cites "Olsen & Wilson 2010, Nature"; that citation conflates these two
  papers, and this header records the discrepancy rather than hiding it.
PROTOCOL (fixed):
  * ORNs: type startswith 'ORN' (measured before preregistration: 2,635
    across 53 glomerular types; 31,640 ORN->PN edges, all positive). The
    M2 odor = the ORNs of 10 glomeruli drawn by
    np.random.default_rng(20260930) from the 50 glomeruli that have both
    ORNs and uniglomerular PNs in this graph; every ORN of a selected
    glomerulus is driven at intensity I.
  * Intensities: I in {1, 2, 4, 8} x A0 for each base amplitude A0 in the
    FIXED ladder {0.01, 0.05, 0.2}.
  * Response: R(I) = mean positive-lobe activity over the COGNATE PNs (the
    PNs whose glomerular prefix is one of the 10 stimulated glomeruli) at
    the final state of the same 8-macro-step stimulus, minus the same
    statistic in that grid point's baseline run. ASSUMPTION: cognate-PN
    positive-lobe mean is the model analogue of the recorded PN firing
    response of a stimulated glomerulus.
PASS BAND (preregistered): a grid point passes M2 iff for >= 1 base
  amplitude A0 all three hold:
    (a) R(A0)   > 1e-4                    (detectable evoked response),
    (b) R(8*A0) < 4.0 * R(A0)             (sublinear: 8x input < 4x resp.),
    (c) R(8*A0) > 1.01 * R(A0)            (still rising -- a dead or pinned
                                           response must not pass (b)).
  best_value = the smallest ratio R(8*A0)/R(A0) among (a)+(c)-satisfying
  base amplitudes over passing points (strongest compression while
  responsive); best_point = its grid point.
===============================================================================

Budget note: measured before the sweep, one macro-step costs ~0.05 s, so a
grid point costs ~35 s and the full 21-point grid ~15 min -- no protocol
coarsening needed. Partial results are written to the output JSON after
every grid point.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

import numpy as np  # noqa: E402
from scipy import sparse  # noqa: E402

from flygi.dynamics.rate import RateParameters, ScipyRateNetwork  # noqa: E402
from flygi.dynamics.runtime import load_runtime_connectome  # noqa: E402

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"

# --- The shared operating grid (fixed) ---------------------------------------
GAINS = (0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5)
LEAKS = (0.1, 0.3, 0.6)
INTERNAL_STEPS = 4
BIAS = 0.0

# --- Preregistered protocol constants (see header; do not tune) --------------
PN_TYPE_PATTERNS = ("adPN", "lPN", "vPN", "ilPN", "lvPN", "l2PN")  # mb_bus.py
ODOR_COUNT = 7
GLOMERULI_PER_ODOR = 24
ODOR_SEED = 20260929
M1_AMPLITUDES = (0.02, 0.05, 0.1, 0.2, 0.5)
STIM_MACRO_STEPS = 8
BASELINE_SEED = 20260929
BASELINE_SCALE = 0.01
ACTIVE_FLOOR = 1e-4
M1_BAND = (0.03, 0.15)
M1_BAND_CENTER = 0.075
APL_SCALE = 4.0
M1B_EVALUABLE_MIN = 0.01
M1B_TOLERANCE = 0.005
M2_ORN_SEED = 20260930
M2_GLOMERULI = 10
M2_BASE_AMPLITUDES = (0.01, 0.05, 0.2)
M2_INTENSITY_FACTORS = (1, 2, 4, 8)
M2_FLOOR = 1e-4
M2_MAX_RATIO = 4.0
M2_MIN_RISE = 1.01


def positive(vector: np.ndarray) -> np.ndarray:
    return np.maximum(vector, 0.0)


def run_stimulus(network: ScipyRateNetwork, drive: np.ndarray) -> np.ndarray:
    state = network.initial_state()
    for _ in range(STIM_MACRO_STEPS):
        state = network.advance(state, drive, internal_steps=INTERNAL_STEPS)
    return state


def run_baseline(network: ScipyRateNetwork) -> np.ndarray:
    state = network.initial_state(seed=BASELINE_SEED, scale=BASELINE_SCALE)
    zero = np.zeros(network.node_count, dtype=np.float32)
    for _ in range(STIM_MACRO_STEPS):
        state = network.advance(state, zero, internal_steps=INTERNAL_STEPS)
    return state


def scale_apl_to_kc(
    matrix: sparse.csr_matrix, kc: np.ndarray, apl: np.ndarray, factor: float
) -> tuple[sparse.csr_matrix, int]:
    """The exact H-APL pattern from arc/factory.py: fresh data, shared topology.

    The original matrix is never mutated; only the 4,633 APL->KC weights are
    scaled on a private copy of the data array.
    """

    is_apl = np.zeros(matrix.shape[1], dtype=bool)
    is_apl[apl] = True
    candidate = np.flatnonzero(is_apl[matrix.indices])
    rows = np.searchsorted(matrix.indptr, candidate, side="right") - 1
    is_kc = np.zeros(matrix.shape[0], dtype=bool)
    is_kc[kc] = True
    target = candidate[is_kc[rows]]
    if target.size == 0:
        raise RuntimeError("no APL->KC edges found; wrong graph for the APL check")
    scaled = sparse.csr_matrix(matrix.shape, dtype=matrix.dtype)
    scaled.data = matrix.data.copy()
    scaled.indices = matrix.indices
    scaled.indptr = matrix.indptr
    scaled.data[target] *= np.float32(factor)
    return scaled, int(target.size)


def median_active_fraction(
    network: ScipyRateNetwork,
    kc: np.ndarray,
    odor_drives: list[np.ndarray],
    amplitude: float,
    threshold: float,
) -> tuple[float, list[float]]:
    fractions = []
    for unit_drive in odor_drives:
        state = run_stimulus(network, (unit_drive * np.float32(amplitude)).astype(np.float32))
        active = positive(state[kc]) > threshold
        fractions.append(float(active.mean()))
    return float(np.median(fractions)), fractions


def main() -> int:
    parser = argparse.ArgumentParser(description="MB+AL biological benchmarks")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results" / "benchmarks" / "mb_al.json"
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    t_start = time.time()
    bundle = load_runtime_connectome(RUNTIME_DIR)
    matrix = bundle.matrix
    node_count = int(matrix.shape[0])
    print(f"graph loaded: {node_count} nodes, {matrix.nnz} edges", flush=True)

    with np.load(RUNTIME_DIR / "node_metadata.npz", allow_pickle=False) as archive:
        types = archive["type"].astype("U")

    # Populations, resolved exactly as preregistered. Counts asserted loudly
    # against the values measured before preregistration.
    pn_mask = np.zeros(types.size, dtype=bool)
    for pattern in PN_TYPE_PATTERNS:
        pn_mask |= np.char.find(types, pattern) >= 0
    pn = np.flatnonzero(pn_mask)
    kc = np.flatnonzero(np.char.startswith(types, "KC"))
    apl = np.flatnonzero(types == "APL")
    orn = np.flatnonzero(np.char.startswith(types, "ORN"))
    if pn.size != 627 or kc.size != 4064 or apl.size != 2 or orn.size != 2635:
        raise RuntimeError(
            f"population counts changed: PN {pn.size} (expect 627), KC {kc.size} "
            f"(expect 4064), APL {apl.size} (expect 2), ORN {orn.size} (expect 2635)"
        )

    # M1 odors: 24 of the 162 PN glomerular types each, seeded.
    pn_type_names = sorted(set(types[pn].tolist()))
    if len(pn_type_names) != 162:
        raise RuntimeError(f"expected 162 PN glomerular types, found {len(pn_type_names)}")
    rng = np.random.default_rng(ODOR_SEED)
    odor_drives: list[np.ndarray] = []
    odor_types: list[list[str]] = []
    for _ in range(ODOR_COUNT):
        chosen = rng.choice(len(pn_type_names), size=GLOMERULI_PER_ODOR, replace=False)
        chosen_names = {pn_type_names[i] for i in chosen}
        drive = np.zeros(node_count, dtype=np.float32)
        member = np.isin(types[pn], sorted(chosen_names))
        drive[pn[member]] = 1.0  # unit drive; amplitude applied per ladder step
        odor_drives.append(drive)
        odor_types.append(sorted(chosen_names))

    # M2 odor: ORNs of 10 glomeruli that have both ORNs and cognate PNs.
    orn_glomeruli = sorted({name.split("_", 1)[1] for name in types[orn]})
    pn_glomeruli = {name.split("_", 1)[0] for name in types[pn]}
    both = sorted(set(orn_glomeruli) & pn_glomeruli)
    if len(both) != 50:
        raise RuntimeError(f"expected 50 shared glomeruli, found {len(both)}")
    rng2 = np.random.default_rng(M2_ORN_SEED)
    m2_glomeruli = sorted(rng2.choice(both, size=M2_GLOMERULI, replace=False).tolist())
    orn_selected = np.array(
        [i for i in orn if types[i].split("_", 1)[1] in m2_glomeruli], dtype=np.int64
    )
    cognate_pn = np.array(
        [i for i in pn if types[i].split("_", 1)[0] in m2_glomeruli], dtype=np.int64
    )
    if orn_selected.size == 0 or cognate_pn.size == 0:
        raise RuntimeError("M2 stimulus or readout population is empty")
    m2_unit_drive = np.zeros(node_count, dtype=np.float32)
    m2_unit_drive[orn_selected] = 1.0
    print(
        f"M2 odor: {len(m2_glomeruli)} glomeruli, {orn_selected.size} ORNs driven, "
        f"{cognate_pn.size} cognate PNs read: {m2_glomeruli}",
        flush=True,
    )

    apl_matrix, apl_edges = scale_apl_to_kc(matrix, kc, apl, APL_SCALE)
    if apl_edges != 4633:
        raise RuntimeError(f"expected 4633 APL->KC edges, scaled {apl_edges}")
    print(f"APL x{APL_SCALE} matrix prepared ({apl_edges} edges)", flush=True)

    results: dict[str, Any] = {
        "script": "scripts/benchmarks/mb_al.py",
        "group": "mushroom_body_antennal_lobe",
        "runtime_dir": str(RUNTIME_DIR),
        "grid": {"gains": GAINS, "leaks": LEAKS, "internal_steps": INTERNAL_STEPS, "bias": BIAS},
        "preregistration": {
            "M1_band_median_active_fraction": list(M1_BAND),
            "M1_amplitude_ladder": list(M1_AMPLITUDES),
            "M1b_rule": "median_x4 <= median_x1 + 0.005 at every amplitude with median_x1 >= 0.01",
            "M2_rule": "R(A0)>1e-4 and R(8A0)<4*R(A0) and R(8A0)>1.01*R(A0) at >=1 base amplitude",
            "M2_base_amplitudes": list(M2_BASE_AMPLITUDES),
        },
        "populations": {
            "pn": int(pn.size),
            "pn_glomerular_types": len(pn_type_names),
            "kc": int(kc.size),
            "apl": int(apl.size),
            "orn": int(orn.size),
            "apl_to_kc_edges_scaled": apl_edges,
            "m2_glomeruli": m2_glomeruli,
            "m2_orns_driven": int(orn_selected.size),
            "m2_cognate_pns": int(cognate_pn.size),
        },
        "odor_types": odor_types,
        "points": [],
    }

    def save() -> None:
        tmp = args.output.with_suffix(".tmp")
        tmp.write_text(json.dumps(results, indent=2))
        os.replace(tmp, args.output)

    save()

    for gain in GAINS:
        for leak in LEAKS:
            t_point = time.time()
            params = RateParameters(
                internal_steps=INTERNAL_STEPS, leak=leak, recurrent_gain=gain, bias=BIAS
            )
            network = ScipyRateNetwork(matrix, params, copy_connectivity=False)
            point: dict[str, Any] = {"gain": gain, "leak": leak}

            # --- shared baseline (x1 network) --------------------------------
            baseline_state = run_baseline(network)
            kc_base = positive(baseline_state[kc])
            mu_b, sigma_b = float(kc_base.mean()), float(kc_base.std())
            threshold = max(mu_b + 2.0 * sigma_b, ACTIVE_FLOOR)
            point["baseline"] = {"kc_mu": mu_b, "kc_sigma": sigma_b, "threshold": threshold}

            # --- M1: KC sparse coding ---------------------------------------
            m1: dict[str, Any] = {}
            for amplitude in M1_AMPLITUDES:
                median, fractions = median_active_fraction(
                    network, kc, odor_drives, amplitude, threshold
                )
                m1[str(amplitude)] = {"median": median, "fractions": fractions}
            point["m1_x1"] = m1

            # --- M1b: APL x4, same protocol, own baseline --------------------
            apl_network = ScipyRateNetwork(apl_matrix, params, copy_connectivity=False)
            apl_base = positive(run_baseline(apl_network)[kc])
            apl_threshold = max(
                float(apl_base.mean()) + 2.0 * float(apl_base.std()), ACTIVE_FLOOR
            )
            m1b: dict[str, Any] = {"threshold": apl_threshold}
            for amplitude in M1_AMPLITUDES:
                median, fractions = median_active_fraction(
                    apl_network, kc, odor_drives, amplitude, apl_threshold
                )
                m1b[str(amplitude)] = {"median": median, "fractions": fractions}
            point["m1_x4"] = m1b

            # --- M2: PN gain normalization ----------------------------------
            pn_base = float(positive(baseline_state[cognate_pn]).mean())
            m2: dict[str, Any] = {"pn_baseline": pn_base}
            for base_amplitude in M2_BASE_AMPLITUDES:
                responses = {}
                for factor in M2_INTENSITY_FACTORS:
                    intensity = base_amplitude * factor
                    state = run_stimulus(
                        network, (m2_unit_drive * np.float32(intensity)).astype(np.float32)
                    )
                    responses[str(factor)] = (
                        float(positive(state[cognate_pn]).mean()) - pn_base
                    )
                m2[str(base_amplitude)] = responses
            point["m2"] = m2

            point["seconds"] = round(time.time() - t_point, 1)
            results["points"].append(point)
            save()
            print(
                f"grid point gain={gain} leak={leak}: "
                f"m1 medians {[round(m1[str(a)]['median'], 4) for a in M1_AMPLITUDES]} "
                f"x4 {[round(m1b[str(a)]['median'], 4) for a in M1_AMPLITUDES]} "
                f"m2@0.05 {[round(m2['0.05'][str(f)], 6) for f in M2_INTENSITY_FACTORS]} "
                f"({point['seconds']}s)",
                flush=True,
            )

    # --- Verdicts against the preregistered bands (mechanical) ---------------
    verdicts: dict[str, Any] = {}

    m1_pass, m1_best = [], None
    for point in results["points"]:
        in_band = []
        for amplitude in M1_AMPLITUDES:
            median = point["m1_x1"][str(amplitude)]["median"]
            if M1_BAND[0] <= median <= M1_BAND[1]:
                in_band.append((amplitude, median))
        if in_band:
            m1_pass.append([point["gain"], point["leak"]])
            for amplitude, median in in_band:
                distance = abs(np.log(median / M1_BAND_CENTER))
                if m1_best is None or distance < m1_best["distance"]:
                    m1_best = {
                        "point": [point["gain"], point["leak"]],
                        "amplitude": amplitude,
                        "median": median,
                        "distance": distance,
                    }
    verdicts["m1"] = {"pass_points": m1_pass, "best": m1_best}

    m1b_pass, m1b_not_evaluable, m1b_best = [], [], None
    for point in results["points"]:
        evaluable = [
            a
            for a in M1_AMPLITUDES
            if point["m1_x1"][str(a)]["median"] >= M1B_EVALUABLE_MIN
        ]
        if not evaluable:
            m1b_not_evaluable.append([point["gain"], point["leak"]])
            continue
        deltas = [
            point["m1_x1"][str(a)]["median"] - point["m1_x4"][str(a)]["median"]
            for a in evaluable
        ]
        if all(delta >= -M1B_TOLERANCE for delta in deltas):
            m1b_pass.append([point["gain"], point["leak"]])
            effect = float(np.mean(deltas))
            if m1b_best is None or effect > m1b_best["mean_sparsification"]:
                m1b_best = {
                    "point": [point["gain"], point["leak"]],
                    "mean_sparsification": effect,
                    "evaluable_amplitudes": evaluable,
                }
    verdicts["m1b"] = {
        "pass_points": m1b_pass,
        "not_evaluable_points": m1b_not_evaluable,
        "best": m1b_best,
    }

    m2_pass, m2_best = [], None
    for point in results["points"]:
        passing = []
        for base_amplitude in M2_BASE_AMPLITUDES:
            responses = point["m2"][str(base_amplitude)]
            r1, r8 = responses["1"], responses["8"]
            if r1 > M2_FLOOR and r8 < M2_MAX_RATIO * r1 and r8 > M2_MIN_RISE * r1:
                passing.append((base_amplitude, r8 / r1))
        if passing:
            m2_pass.append([point["gain"], point["leak"]])
            for base_amplitude, ratio in passing:
                if m2_best is None or ratio < m2_best["ratio_8x"]:
                    m2_best = {
                        "point": [point["gain"], point["leak"]],
                        "base_amplitude": base_amplitude,
                        "ratio_8x": ratio,
                    }
    verdicts["m2"] = {"pass_points": m2_pass, "best": m2_best}

    results["verdicts"] = verdicts
    results["total_seconds"] = round(time.time() - t_start, 1)
    save()
    print(json.dumps(verdicts, indent=2), flush=True)
    print(f"done in {results['total_seconds']}s -> {args.output}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
