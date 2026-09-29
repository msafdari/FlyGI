#!/usr/bin/env python3
"""Fidelity-CLASS-2 benchmark -- KC SPARSE CODING (fly-module verdict program).

Class-1 context (measured): the frozen uniform tanh rate model FAILED benchmark
M1 (KC sparse coding) at all 21 operating points -- results/benchmarks/
mb_al.json, verdicts.m1.pass_points == [] (scripts/benchmarks/mb_al.py,
preregistered 2026-09-29). Class 2 changes the MODEL (per-type LIF temporal
dynamics on the same anatomy); THE BAND DOES NOT CHANGE.

================================ PREREGISTRATION ==============================
Fixed before this sweep ran. Misses are reported as misses; no band moves.

BAND (verbatim from class-1 M1, scripts/benchmarks/mb_al.py):
  "a grid point passes M1 iff the median active fraction lies in [0.03, 0.15]"
  -- here: the median KC active fraction across the 7 HELD-OUT odors must lie
  in [0.03, 0.15]. best_value = the in-band median closest to 0.075 (the 5-10%
  band center) by |log(median/0.075)| (class-1 selection rule, verbatim).
LIN CONTROL (unchanged M1b direction; Lin et al. 2014 Nat Neurosci 17:559-568):
  reducing/blocking APL output must DENSIFY the code. Here the manipulation is
  the shibire analog (APL output gain -> 0, same calibrated thresholds, same
  Poisson realizations); the config passes iff
  median_blocked >= median_intact + 0.005 (the class-1 M1b tolerance, direction
  reversed because the manipulation is reversed: class 1 scaled APL x4 and
  required sparsification; blocking must densify).
A CONFIG PASSES iff (band holds on held-out) AND (Lin control densifies).

CITATIONS (Established):
  Turner, Bazhenov, Laurent 2008 J Neurophysiol 99:734-746 (KC sparseness
    ~6+-5%; high threshold; single-claw input subthreshold);
  Honegger, Campbell, Turner 2011 J Neurosci 31:11772-11785 (~5-10% KCs/odor);
  Lin et al. 2014 Nat Neurosci 17:559-568 (APL blockade densifies KC code);
  Gruntman & Turner 2013 Nat Neurosci 16:1821-1829 (6-8 claws; more than half
    must be coactive to spike);
  Litwin-Kumar et al. 2017 Neuron 93:1153-1164 (threshold calibration to
    coding level f=0.1; subtractive APL feedback tuned to cancel mean
    excitation);
  Amin et al. 2020 eLife 9:e56954 (APL is non-spiking -> graded unit);
  Shiu et al. 2024 (whole-brain LIF precedent: canonical params tau_m 20 ms,
    rest-to-threshold gap 7 mV [-52 -> -45], v_reset = v_rest, refractory
    2.2 ms, tau_syn 5 ms; the engine's defaults, src/flygi/dynamics/spiking.py).
  Domain parameter table: docs/fidelity2/mb_cx_regimes.md (Part A).

MODEL (class 2):
  Subcircuit (induced subgraph, signed raw synapse counts, modulators zeroed;
  src/flygi/connectome/subcircuit.py): PN types (class-1 patterns adPN/lPN/
  vPN/ilPN/lvPN/l2PN as substrings; asserted 627 across 162 glomerular types)
  + KC* (asserted 4064) + APL (asserted 2, both GABA) + MBON* (count recorded).
  KCs: spiking LIF, Shiu canonical baseline; tau_m_KC and tau_syn_KC swept
    (rows A6/A13 are ASSUMED). Threshold theta: CALIBRATED (below).
  APL: GRADED non-spiking unit (ESTABLISHED, Amin 2020), leaky integrator,
    output relu(v)*alpha fed back through the connectome's APL->out weights.
    Feedback form: SUBTRACTIVE, per Litwin-Kumar 2017 -- chosen because (a) the
    engine's current-based synapses implement subtraction natively, and (b) the
    threshold-calibration procedure scored here is Litwin-Kumar's, so form and
    procedure come from the same validated model spec. Prisco 2021 divisive
    normalization is the declared untested alternative (A12: form choice
    ASSUMED).
  PNs: clamped Poisson spike sources (outputs overwritten each step; their
    LIF params are moot). ASSUMED rates: background 5 Hz all PNs; odor-member
    PNs 100 Hz sustained (mid-range of PN odor-evoked rates, Bhandawat 2007;
    background per Kakaria & de Bivort 2017 convention). Fixed, not swept
    (declared timebox coarsening; theta calibration absorbs rate scale to
    first order).
  MBONs: spiking LIF at Shiu defaults; not scored; rates recorded.
  dt = 0.1 ms (docs/fidelity2/mb_cx_regimes.md timestep guidance).
  Weight plumbing (declared, fixed a priori, not fit to any output):
    w_scale = 1 / mean(PN->KC edge synapse count) so the mean claw EPSP is the
    unit of drive. This is normalization, not calibration: it sets units only;
    theta calibration below is the only fit to activity.

ODOR SETS (class-1 odor model: an odor = 24 of the 162 PN glomerular types,
  every PN of a chosen type driven):
  HELD-OUT (scored): the EXACT 7 class-1 M1 odors -- same draw, seed 20260929,
    from sorted PN type names (asserted 162).
  CALIBRATION: 5 fresh draws, seed 20261001, same procedure; asserted disjoint
    from every held-out odor as a set.
  Trial: 200 ms settle (background only) then 500 ms odor. A KC is RESPONSIVE
    iff it fires >= 2 spikes in the 500 ms odor window (ASSUMED analog of the
    Turner/Honegger reliability criterion for a single trial; the >=1-spike
    fraction is reported alongside, unscored). Active fraction = responsive
    KCs / 4064 (all KCs, class-1 denominator convention). Per-trial Poisson
    seeds are fixed per (arm, odor); intact and blocked held-out arms share
    realizations (paired comparison, class-1 M1b analog).

CALIBRATION (DECLARED; performed on calibration stimuli only, scored on
  held-out only -- never on the scored measurement):
  1. theta seed: one free-potential run (all spiking thresholds at +inf) on 2
     calibration odors; theta0 = 90th percentile of pooled per-KC per-odor
     peak free potentials (targets coding level f ~ 0.1, Litwin-Kumar A9).
  2. APL gain scale (one scalar per sign class, allowed by the discipline
     rule): one probe trial (calibration odor #0, theta0, APL feedback open)
     measures mean net non-APL synaptic current onto KCs (i_exc) and the
     open-loop APL graded levels; alpha_bal = the APL output gain at which
     mean APL feedback current onto KCs equals i_exc (Litwin-Kumar
     subtractive balancing). The swept knob is beta = alpha/alpha_bal.
  3. theta: geometric bisection (<= 8 evals, each = 5 calibration odors) to
     median calibration active fraction 0.10 +- 0.015, loop closed at the
     config's alpha. GLOBAL scalar theta (doc Part A knob 1): heterogeneity
     must come from the anatomy, not from per-cell fitted thresholds.

OPERATING GRID (swept ASSUMED parameters; everything else fixed above):
  tau_m_KC in {8, 20} ms          (A6 ASSUMED range ends)
  tau_syn_KC in {5, 10} ms        (A13 IPSP tau range; single synaptic channel
                                   per node in this engine, so EPSP and IPSP
                                   tau on KCs move together -- declared
                                   engine-limitation confound)
  beta in {0.5, 1.0, 2.0}         (APL loop gain vs mean-excitation balance;
                                   beta=1 is Litwin-Kumar's tuning)
  = 12 configs, swept SEQUENTIALLY in one process. Declared coarsening rule if
  the timebox threatens: if elapsed > 120 min at a config boundary, remaining
  tau_syn_KC=10 configs are dropped (the grid coarsens, NEVER the band); loop
  is ordered tau_syn 5 first so the primary plane completes first.

TRIVIAL ALTERNATIVE (mandatory; named before the run):
  T1 (PRIMARY): same circuit, same plumbing (w_scale), uniform Shiu-canonical
    thresholds copied unchanged (theta - rest = 7 units), NO calibration, NO
    APL feedback (alpha=0). The class-1 move -- one uniform operating point,
    no threshold separate from gain, no functional APL loop -- at spiking
    fidelity. Expected dense or silent.
  T2 (reported): as T1 but raw synapse counts (w_scale=1) -- the fully literal
    parameter copy.
  ATTRIBUTION holds iff the best passing config holds the band + Lin control
  on held-out odors AND T1's held-out median lies outside the band.

STRUCTURAL CHECKS (report alongside, not scored; Gruntman & Turner 2013):
  On the best config's calibrated parameters, passive single-KC integration
  (no recurrence, no APL -- the isolated-cell measurement analog), 200 sampled
  KCs with >= 3 excitatory claws (claw = presynaptic PN with positive weight),
  sustained 100 Hz regular trains, 500 ms: (a) ONE claw driven -> peak v vs
  theta (want subthreshold); (b) floor(n_claws/2)+1 claws driven (majority
  coincidence) -> peak v vs theta (want suprathreshold).
  Cross-stimulus stability: per-odor held-out fractions (min/max/IQR) and mean
  pairwise Pearson correlation of binary KC activation vectors, intact vs
  blocked (Lin 2014: blockade raises inter-odor correlation).

RESOURCES (measured before launch, 2026-09-29): 16 GB RAM, ~4.6 GB
  reclaimable; probe peak RSS 1237 MB (extraction-dominated) -- under the 3 GB
  lane. Probe step cost ~1.0 ms -> ~7 s per 700 ms trial; ~55 trials/config
  x 12 configs ~ 80 min, inside the ~2.5 h timebox. Partial results are saved
  after every config.
===============================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import resource
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

import numpy as np  # noqa: E402

from flygi.connectome.subcircuit import Subcircuit, extract_subcircuit, select_nodes  # noqa: E402
from flygi.dynamics.spiking import ParameterTable, SpikingNetwork, TypeParams  # noqa: E402

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"

# --- Preregistered constants (see header; do not tune) ------------------------
PN_SUBSTRINGS = ("adPN", "lPN", "vPN", "ilPN", "lvPN", "l2PN")  # class-1 M1
PN_FNMATCH = tuple(f"*{s}*" for s in PN_SUBSTRINGS)
BAND = (0.03, 0.15)                  # class-1 M1 band, verbatim
BAND_CENTER = 0.075                  # class-1 selection rule, verbatim
LIN_MARGIN = 0.005                   # class-1 M1b tolerance, direction reversed
TARGET_F = 0.10                      # Litwin-Kumar 2017 coding level (A9)
CAL_TOL = 0.015
MAX_BISECT = 8
DT_MS = 0.1
SETTLE_MS = 200.0
ODOR_MS = 500.0
RATE_BG_HZ = 5.0                     # ASSUMED (K&dB 2017 background convention)
RATE_ACTIVE_HZ = 100.0               # ASSUMED (mid-range PN odor-evoked rate)
RESPONSIVE_MIN_SPIKES = 2            # ASSUMED single-trial reliability analog
HELDOUT_SEED = 20260929              # class-1 M1 odors, verbatim
HELDOUT_COUNT = 7
CAL_SEED = 20261001
CAL_COUNT = 5
GLOMERULI_PER_ODOR = 24
STRUCT_SEED = 20261002
STRUCT_SAMPLE = 200
SHIU_GAP = 7.0                       # -45 - (-52) mV, Shiu canonical
TAU_M_APL = 20.0                     # ASSUMED, fixed (declared coarsening)
GRID_TAU_M = (8.0, 20.0)             # A6 ASSUMED
GRID_TAU_SYN = (5.0, 10.0)           # A13 ASSUMED (shared-channel confound)
GRID_BETA = (0.5, 1.0, 2.0)          # APL balance knob, beta=1 = Litwin-Kumar
COARSEN_AFTER_MIN = 120.0
DRIVE_SEED_CAL = 777
DRIVE_SEED_TEST = 888                # shared by intact/blocked/trivial (paired)

SETTLE_STEPS = int(round(SETTLE_MS / DT_MS))
ODOR_STEPS = int(round(ODOR_MS / DT_MS))

LOG_PATH = ROOT / "results" / "benchmarks" / "fc2_kc_sparse.log"


def log(message: str) -> None:
    stamp = time.strftime("%H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    with LOG_PATH.open("a") as handle:
        handle.write(line + "\n")


def build_subcircuit() -> Subcircuit:
    indices = select_nodes(RUNTIME_DIR, type_patterns=PN_FNMATCH + ("KC*", "APL", "MBON*"))
    return extract_subcircuit(RUNTIME_DIR, indices)


def make_odors(pn_type_names: list[str], seed: int, count: int) -> list[list[str]]:
    """Class-1 M1 odor draw, verbatim: 24 of the 162 PN glomerular types each."""
    rng = np.random.default_rng(seed)
    odors: list[list[str]] = []
    for _ in range(count):
        chosen = rng.choice(len(pn_type_names), size=GLOMERULI_PER_ODOR, replace=False)
        odors.append(sorted({pn_type_names[i] for i in chosen}))
    return odors


def build_table(theta_kc: float, alpha: float, tau_m_kc: float, tau_syn_kc: float) -> ParameterTable:
    """Per-type params. Default (PNs -- moot, clamped -- and MBONs): Shiu canonical."""
    return ParameterTable(
        default=TypeParams(
            tau_m_ms=20.0, v_thresh=SHIU_GAP, tau_syn_ms=5.0,
            provenance="ESTABLISHED (Shiu 2024 canonical: tau_m 20 ms, gap 7 mV, tau_syn 5 ms, refractory 2.2 ms)",
        ),
        rules=[
            ("APL", TypeParams(
                tau_m_ms=TAU_M_APL, v_thresh=1e9, provenance=(
                    "graded ESTABLISHED (Amin 2020); tau_m ASSUMED 20 ms fixed; "
                    "gain = alpha (swept via beta)"
                ), graded=True, graded_gain=alpha,
            )),
            ("KC*", TypeParams(
                tau_m_ms=tau_m_kc, v_thresh=theta_kc, tau_syn_ms=tau_syn_kc,
                provenance=(
                    "tau_m ASSUMED (A6, swept 8/20); tau_syn ASSUMED (A13, swept 5/10); "
                    "theta CALIBRATED (Litwin-Kumar procedure, calibration odors only)"
                ),
            )),
        ],
    )


def run_trial(
    sub: Subcircuit,
    pn_idx: np.ndarray,
    kc_idx: np.ndarray,
    apl_idx: np.ndarray,
    mbon_idx: np.ndarray,
    member_mask: np.ndarray,
    table: ParameterTable,
    w_scale: float,
    drive_seed: tuple[int, ...],
    collect_probe: bool = False,
) -> dict[str, Any]:
    """One 200 ms settle + 500 ms odor trial with clamped Poisson PN outputs.

    PN nodes are spike SOURCES: after each engine step their outputs are
    overwritten with Bernoulli(rate*dt) draws (their own LIF dynamics are
    irrelevant; the overwrite happens before the next step reads last_output).
    This lives here, not in src/, per the class-2 engine discipline.
    """
    net = SpikingNetwork(sub.matrix, sub.types, table, dt_ms=DT_MS, w_scale=w_scale)
    rng = np.random.default_rng(drive_seed)
    p_bg = RATE_BG_HZ * DT_MS / 1000.0
    p_active = RATE_ACTIVE_HZ * DT_MS / 1000.0
    probability = np.full(pn_idx.size, p_bg, dtype=np.float64)

    kc_settle = np.zeros(kc_idx.size, dtype=np.int64)
    kc_odor = np.zeros(kc_idx.size, dtype=np.int64)
    mbon_odor = np.zeros(mbon_idx.size, dtype=np.int64)
    apl_out_sum = 0.0
    i_exc_sum = 0.0
    apl_free_sum = np.zeros(apl_idx.size, dtype=np.float64)

    for step in range(SETTLE_STEPS + ODOR_STEPS):
        if step == SETTLE_STEPS:
            probability = np.where(member_mask, p_active, p_bg)
        out = net.step(None)
        in_odor = step >= SETTLE_STEPS
        kc_out = out[kc_idx] > 0
        if in_odor:
            kc_odor += kc_out
            mbon_odor += out[mbon_idx] > 0
            apl_out_sum += float(out[apl_idx].sum())
            if collect_probe:
                i_exc_sum += float(net.i_syn[kc_idx].mean())
                apl_free_sum += np.maximum(net.v[apl_idx], 0.0)
        else:
            kc_settle += kc_out
        # Clamp: PN outputs are external Poisson spike trains.
        net.last_output[pn_idx] = (rng.random(pn_idx.size) < probability).astype(np.float32)

    result: dict[str, Any] = {
        "frac2": float((kc_odor >= RESPONSIVE_MIN_SPIKES).mean()),
        "frac1": float((kc_odor >= 1).mean()),
        "kc_rate_hz": float(kc_odor.mean() / (ODOR_MS / 1000.0)),
        "kc_settle_rate_hz": float(kc_settle.mean() / (SETTLE_MS / 1000.0)),
        "mbon_rate_hz": float(mbon_odor.mean() / (ODOR_MS / 1000.0)),
        "apl_mean_output": apl_out_sum / (ODOR_STEPS * apl_idx.size),
        "kc_odor_spikes": kc_odor,
    }
    if collect_probe:
        result["i_exc_mean"] = i_exc_sum / ODOR_STEPS
        result["apl_free_mean"] = apl_free_sum / ODOR_STEPS
    return result


def free_potential_peaks(
    sub: Subcircuit,
    pn_idx: np.ndarray,
    kc_idx: np.ndarray,
    member_mask: np.ndarray,
    tau_m_kc: float,
    tau_syn_kc: float,
    w_scale: float,
    drive_seed: tuple[int, ...],
) -> np.ndarray:
    """Per-KC peak free membrane potential (all spiking thresholds at +inf)."""
    table = ParameterTable(
        default=TypeParams(tau_m_ms=20.0, v_thresh=1e9, tau_syn_ms=5.0, provenance="free run"),
        rules=[
            ("APL", TypeParams(tau_m_ms=TAU_M_APL, v_thresh=1e9, provenance="free run",
                               graded=True, graded_gain=0.0)),
            ("KC*", TypeParams(tau_m_ms=tau_m_kc, v_thresh=1e9, tau_syn_ms=tau_syn_kc,
                               provenance="free run")),
        ],
    )
    net = SpikingNetwork(sub.matrix, sub.types, table, dt_ms=DT_MS, w_scale=w_scale)
    rng = np.random.default_rng(drive_seed)
    p_bg = RATE_BG_HZ * DT_MS / 1000.0
    p_active = RATE_ACTIVE_HZ * DT_MS / 1000.0
    probability = np.full(pn_idx.size, p_bg, dtype=np.float64)
    peaks = np.zeros(kc_idx.size, dtype=np.float32)
    for step in range(SETTLE_STEPS + ODOR_STEPS):
        if step == SETTLE_STEPS:
            probability = np.where(member_mask, p_active, p_bg)
        net.step(None)
        if step >= SETTLE_STEPS:
            np.maximum(peaks, net.v[kc_idx], out=peaks)
        net.last_output[pn_idx] = (rng.random(pn_idx.size) < probability).astype(np.float32)
    return peaks


def main() -> int:
    parser = argparse.ArgumentParser(description="Class-2 KC sparse-coding benchmark")
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "results" / "benchmarks" / "fc2_kc_sparse.json",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    LOG_PATH.write_text("")

    t_start = time.time()
    sub = build_subcircuit()
    types = sub.types
    pn_mask = np.zeros(types.size, dtype=bool)
    for substring in PN_SUBSTRINGS:
        pn_mask |= np.char.find(types, substring) >= 0
    pn_idx = np.flatnonzero(pn_mask)
    kc_idx = np.flatnonzero(np.char.startswith(types, "KC"))
    apl_idx = np.flatnonzero(types == "APL")
    mbon_idx = np.flatnonzero(np.char.startswith(types, "MBON"))
    if pn_idx.size != 627 or kc_idx.size != 4064 or apl_idx.size != 2:
        raise RuntimeError(
            f"population counts changed: PN {pn_idx.size} (expect 627), "
            f"KC {kc_idx.size} (expect 4064), APL {apl_idx.size} (expect 2)"
        )
    pn_type_names = sorted(set(types[pn_idx].tolist()))
    if len(pn_type_names) != 162:
        raise RuntimeError(f"expected 162 PN glomerular types, found {len(pn_type_names)}")
    apl_block = np.abs(np.asarray(sub.matrix[kc_idx][:, apl_idx].todense(), dtype=np.float64))
    if int((apl_block > 0).sum()) != 4633:
        raise RuntimeError(f"expected 4633 APL->KC edges, found {(apl_block > 0).sum()}")

    pn_kc = sub.matrix[kc_idx][:, pn_idx]
    mean_claw_weight = float(pn_kc.data[pn_kc.data > 0].mean())
    w_scale = 1.0 / mean_claw_weight
    excitatory_claws = np.asarray((pn_kc > 0).sum(axis=1)).ravel()

    log(
        f"subcircuit: {sub.node_count} nodes ({pn_idx.size} PN / {kc_idx.size} KC / "
        f"{apl_idx.size} APL / {mbon_idx.size} MBON), {sub.matrix.nnz} edges, "
        f"dropped modulatory {sub.dropped_modulatory_edges}, unsigned {sub.unsigned_edges}; "
        f"mean PN->KC claw weight {mean_claw_weight:.2f} -> w_scale {w_scale:.5f}"
    )

    heldout_odors = make_odors(pn_type_names, HELDOUT_SEED, HELDOUT_COUNT)
    cal_odors = make_odors(pn_type_names, CAL_SEED, CAL_COUNT)
    heldout_sets = [frozenset(o) for o in heldout_odors]
    for odor in cal_odors:
        if frozenset(odor) in heldout_sets:
            raise RuntimeError("calibration odor duplicates a held-out odor")

    def member(odor: list[str]) -> np.ndarray:
        return np.isin(types[pn_idx], odor)

    heldout_masks = [member(o) for o in heldout_odors]
    cal_masks = [member(o) for o in cal_odors]

    results: dict[str, Any] = {
        "script": "scripts/benchmarks/fc2_kc_sparse.py",
        "benchmark": "fc2_kc_sparse",
        "fidelity_class": 2,
        "band_verbatim": "median KC active fraction in [0.03, 0.15] on held-out stimuli",
        "lin_control": "median_blocked >= median_intact + 0.005 (blocking APL must densify)",
        "class1_result": "M1 pass_points == [] at all 21 operating points (results/benchmarks/mb_al.json)",
        "runtime_dir": str(RUNTIME_DIR),
        "subcircuit": {
            "nodes": int(sub.node_count),
            "pn": int(pn_idx.size), "kc": int(kc_idx.size),
            "apl": int(apl_idx.size), "mbon": int(mbon_idx.size),
            "edges": int(sub.matrix.nnz),
            "dropped_modulatory_edges": int(sub.dropped_modulatory_edges),
            "unsigned_edges": int(sub.unsigned_edges),
            "pn_kc_edges": int(pn_kc.nnz),
            "mean_claw_weight": mean_claw_weight,
            "w_scale": w_scale,
            "mean_excitatory_claws": float(excitatory_claws.mean()),
            "zero_claw_kcs": int((excitatory_claws == 0).sum()),
        },
        "protocol": {
            "dt_ms": DT_MS, "settle_ms": SETTLE_MS, "odor_ms": ODOR_MS,
            "rate_bg_hz": RATE_BG_HZ, "rate_active_hz": RATE_ACTIVE_HZ,
            "responsive_min_spikes": RESPONSIVE_MIN_SPIKES,
            "target_f": TARGET_F, "cal_tol": CAL_TOL,
            "heldout_seed": HELDOUT_SEED, "cal_seed": CAL_SEED,
            "apl_form": "subtractive (Litwin-Kumar 2017); divisive (Prisco 2021) = declared untested alternative",
        },
        "grid": {
            "tau_m_kc_ms": list(GRID_TAU_M),
            "tau_syn_kc_ms": list(GRID_TAU_SYN),
            "beta": list(GRID_BETA),
        },
        "heldout_odors": heldout_odors,
        "cal_odors": cal_odors,
        "configs": [],
    }

    def save() -> None:
        tmp = args.output.with_suffix(".tmp")
        tmp.write_text(json.dumps(results, indent=2, default=float))
        os.replace(tmp, args.output)

    save()

    def trial(theta: float, alpha: float, tau_m: float, tau_syn: float,
              mask: np.ndarray, seed: tuple[int, ...], probe: bool = False) -> dict[str, Any]:
        table = build_table(theta, alpha, tau_m, tau_syn)
        return run_trial(sub, pn_idx, kc_idx, apl_idx, mbon_idx, mask, table,
                         w_scale, seed, collect_probe=probe)

    def median_frac(theta: float, alpha: float, tau_m: float, tau_syn: float,
                    masks: list[np.ndarray], seed_base: int, cfg_id: int) -> tuple[float, list[float]]:
        fracs = [
            trial(theta, alpha, tau_m, tau_syn, mask, (seed_base, cfg_id, odor_id))["frac2"]
            for odor_id, mask in enumerate(masks)
        ]
        return float(np.median(fracs)), fracs

    # --- Sweep (sequential, one process) -------------------------------------
    configs = [
        {"tau_syn_kc": ts, "tau_m_kc": tm, "beta": b}
        for ts in GRID_TAU_SYN for tm in GRID_TAU_M for b in GRID_BETA
    ]
    coarsened = False
    for cfg_id, cfg in enumerate(configs):
        elapsed_min = (time.time() - t_start) / 60.0
        if cfg["tau_syn_kc"] == GRID_TAU_SYN[1] and elapsed_min > COARSEN_AFTER_MIN:
            if not coarsened:
                log(f"COARSENING: {elapsed_min:.0f} min elapsed; dropping remaining tau_syn=10 configs (declared rule)")
                coarsened = True
                results["coarsened"] = "tau_syn_kc=10 configs dropped after 120 min (declared rule)"
            continue
        t_cfg = time.time()
        tau_m, tau_syn, beta = cfg["tau_m_kc"], cfg["tau_syn_kc"], cfg["beta"]
        entry: dict[str, Any] = dict(cfg)

        # 1. theta seed from free potentials (2 calibration odors).
        peaks = np.concatenate([
            free_potential_peaks(sub, pn_idx, kc_idx, cal_masks[i], tau_m, tau_syn,
                                 w_scale, (DRIVE_SEED_CAL, cfg_id, i))
            for i in range(2)
        ])
        theta0 = float(np.quantile(peaks, 1.0 - TARGET_F))
        entry["theta0_free_quantile"] = theta0
        if theta0 <= 0:
            entry["failed"] = "free potentials never positive"
            results["configs"].append(entry)
            save()
            continue

        # 2. alpha_bal probe: open APL loop (gain 0), theta0; measure i_exc and
        #    open-loop APL graded level (relu(v) = output at gain 1).
        probe = trial(theta0, 0.0, tau_m, tau_syn, cal_masks[0], (DRIVE_SEED_CAL, cfg_id, 0), probe=True)
        i_exc = probe["i_exc_mean"]
        apl_free = np.asarray(probe["apl_free_mean"], dtype=np.float64)
        feedback_per_gain = float((apl_block @ apl_free).mean()) * w_scale * tau_syn / DT_MS
        entry["probe"] = {
            "i_exc_mean": i_exc,
            "apl_free_mean": apl_free.tolist(),
            "probe_frac2": probe["frac2"],
        }
        if i_exc <= 0 or feedback_per_gain <= 1e-12:
            entry["failed"] = "APL undriven or nonpositive excitatory current at theta0"
            results["configs"].append(entry)
            save()
            log(f"cfg {cfg_id} {cfg}: FAILED probe (i_exc {i_exc:.4g}, fb/gain {feedback_per_gain:.4g})")
            continue
        alpha_bal = i_exc / feedback_per_gain
        alpha = beta * alpha_bal
        entry["alpha_bal"] = alpha_bal
        entry["alpha"] = alpha

        # 3. theta bisection, loop closed at alpha, on calibration odors only.
        lo, hi = theta0 / 4.0, theta0 * 4.0
        history = []
        theta = theta0
        best = None
        for _ in range(MAX_BISECT):
            med, fracs = median_frac(theta, alpha, tau_m, tau_syn, cal_masks, DRIVE_SEED_CAL, cfg_id)
            history.append({"theta": theta, "median": med, "fractions": fracs})
            if best is None or abs(med - TARGET_F) < abs(best[1] - TARGET_F):
                best = (theta, med)
            if abs(med - TARGET_F) <= CAL_TOL:
                break
            if med > TARGET_F:
                lo = theta
            else:
                hi = theta
            theta = float(np.sqrt(lo * hi))
        theta, cal_median = best
        entry["calibration"] = {
            "history": history,
            "theta": theta,
            "cal_median": cal_median,
            "hit_target": bool(abs(cal_median - TARGET_F) <= CAL_TOL),
        }

        # 4. Score on held-out odors: intact and APL-blocked, paired seeds.
        intact_trials = [
            trial(theta, alpha, tau_m, tau_syn, mask, (DRIVE_SEED_TEST, odor_id))
            for odor_id, mask in enumerate(heldout_masks)
        ]
        blocked_trials = [
            trial(theta, 0.0, tau_m, tau_syn, mask, (DRIVE_SEED_TEST, odor_id))
            for odor_id, mask in enumerate(heldout_masks)
        ]
        intact_fracs = [t["frac2"] for t in intact_trials]
        blocked_fracs = [t["frac2"] for t in blocked_trials]
        med_intact = float(np.median(intact_fracs))
        med_blocked = float(np.median(blocked_fracs))

        def correlation(trials: list[dict[str, Any]]) -> float:
            binary = np.stack([
                (t["kc_odor_spikes"] >= RESPONSIVE_MIN_SPIKES).astype(np.float64) for t in trials
            ])
            keep = binary.std(axis=1) > 0
            if keep.sum() < 2:
                return float("nan")
            c = np.corrcoef(binary[keep])
            return float(c[np.triu_indices_from(c, k=1)].mean())

        in_band = BAND[0] <= med_intact <= BAND[1]
        lin_ok = med_blocked >= med_intact + LIN_MARGIN
        entry["heldout"] = {
            "intact_fractions": intact_fracs,
            "intact_median": med_intact,
            "intact_frac1": [t["frac1"] for t in intact_trials],
            "intact_kc_rate_hz": float(np.mean([t["kc_rate_hz"] for t in intact_trials])),
            "intact_settle_rate_hz": float(np.mean([t["kc_settle_rate_hz"] for t in intact_trials])),
            "intact_mbon_rate_hz": float(np.mean([t["mbon_rate_hz"] for t in intact_trials])),
            "intact_apl_output": float(np.mean([t["apl_mean_output"] for t in intact_trials])),
            "intact_pairwise_corr": correlation(intact_trials),
            "blocked_fractions": blocked_fracs,
            "blocked_median": med_blocked,
            "blocked_pairwise_corr": correlation(blocked_trials),
            "iqr_intact": float(np.subtract(*np.percentile(intact_fracs, [75, 25]))),
        }
        entry["pass_band"] = bool(in_band)
        entry["pass_lin"] = bool(lin_ok)
        entry["pass"] = bool(in_band and lin_ok)
        entry["seconds"] = round(time.time() - t_cfg, 1)
        results["configs"].append(entry)
        save()
        log(
            f"cfg {cfg_id} tau_m {tau_m} tau_syn {tau_syn} beta {beta}: theta {theta:.2f} "
            f"(cal {cal_median:.4f}, {len(history)} evals) held-out intact {med_intact:.4f} "
            f"blocked {med_blocked:.4f} band={in_band} lin={lin_ok} ({entry['seconds']}s)"
        )

    # --- Trivial alternatives (named in header) -------------------------------
    trivial: dict[str, Any] = {}
    for name, tw_scale in (("T1_shiu_uniform", w_scale), ("T2_raw_counts", 1.0)):
        fracs, frac1s = [], []
        table = build_table(SHIU_GAP, 0.0, 20.0, 5.0)
        for odor_id, mask in enumerate(heldout_masks):
            t = run_trial(sub, pn_idx, kc_idx, apl_idx, mbon_idx, mask, table,
                          tw_scale, (DRIVE_SEED_TEST, odor_id))
            fracs.append(t["frac2"])
            frac1s.append(t["frac1"])
        trivial[name] = {
            "w_scale": tw_scale,
            "theta": SHIU_GAP,
            "fractions": fracs,
            "median": float(np.median(fracs)),
            "frac1": frac1s,
            "in_band": bool(BAND[0] <= float(np.median(fracs)) <= BAND[1]),
        }
        log(f"trivial {name}: held-out median {trivial[name]['median']:.4f} in_band={trivial[name]['in_band']}")
    results["trivial"] = trivial
    save()

    # --- Verdict (mechanical) -------------------------------------------------
    passing = [c for c in results["configs"] if c.get("pass")]
    best_cfg = None
    if passing:
        best_cfg = min(passing, key=lambda c: abs(np.log(c["heldout"]["intact_median"] / BAND_CENTER)))
    results["verdict"] = {
        "pass_configs": [
            {k: c[k] for k in ("tau_m_kc", "tau_syn_kc", "beta")} for c in passing
        ],
        "passed": bool(passing),
        "best": None if best_cfg is None else {
            "tau_m_kc": best_cfg["tau_m_kc"], "tau_syn_kc": best_cfg["tau_syn_kc"],
            "beta": best_cfg["beta"], "theta": best_cfg["calibration"]["theta"],
            "alpha": best_cfg["alpha"],
            "heldout_median": best_cfg["heldout"]["intact_median"],
            "blocked_median": best_cfg["heldout"]["blocked_median"],
        },
        "attribution_holds": bool(passing) and not trivial["T1_shiu_uniform"]["in_band"],
    }
    save()

    # --- Structural checks (report alongside, not scored) ---------------------
    ref = best_cfg if best_cfg is not None else (
        min(results["configs"], key=lambda c: abs(np.log(max(c.get("heldout", {}).get("intact_median", 1e-6), 1e-6) / BAND_CENTER))
            ) if any("heldout" in c for c in results["configs"]) else None
    )
    if ref is not None and "calibration" in ref:
        theta = ref["calibration"]["theta"]
        tau_m, tau_syn = ref["tau_m_kc"], ref["tau_syn_kc"]
        rng = np.random.default_rng(STRUCT_SEED)
        eligible = np.flatnonzero(excitatory_claws >= 3)
        sample = rng.choice(eligible, size=min(STRUCT_SAMPLE, eligible.size), replace=False)
        pn_kc_csr = pn_kc.tocsr()
        interval = int(round(10.0 / DT_MS))  # 100 Hz regular train
        steps = ODOR_STEPS

        def passive_peak(weights: np.ndarray) -> float:
            i_syn, v, peak = 0.0, 0.0, 0.0
            total_w = float(weights.sum()) * w_scale
            for s in range(steps):
                i_syn += (DT_MS / tau_syn) * (-i_syn)
                if s % interval == 0:
                    i_syn += total_w
                v += (DT_MS / tau_m) * (-v) + DT_MS * i_syn
                peak = max(peak, v)
            return peak

        single_peaks, majority_peaks = [], []
        for kc_row in sample:
            row = pn_kc_csr[kc_row]
            claw_weights = row.data[row.data > 0]
            order = rng.permutation(claw_weights.size)
            single_peaks.append(passive_peak(claw_weights[order[:1]]))
            k = claw_weights.size // 2 + 1
            majority_peaks.append(passive_peak(claw_weights[order[:k]]))
        single_peaks = np.array(single_peaks)
        majority_peaks = np.array(majority_peaks)
        results["structural"] = {
            "reference_config": {"tau_m_kc": tau_m, "tau_syn_kc": tau_syn,
                                 "theta": theta, "is_best_passing": ref is best_cfg},
            "sampled_kcs": int(sample.size),
            "single_claw_subthreshold_fraction": float((single_peaks < theta).mean()),
            "majority_claw_suprathreshold_fraction": float((majority_peaks >= theta).mean()),
            "single_peak_over_theta_median": float(np.median(single_peaks) / theta),
            "majority_peak_over_theta_median": float(np.median(majority_peaks) / theta),
        }
        log(
            f"structural: single-claw sub {results['structural']['single_claw_subthreshold_fraction']:.3f}, "
            f"majority supra {results['structural']['majority_claw_suprathreshold_fraction']:.3f}"
        )

    results["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20)
    results["total_seconds"] = round(time.time() - t_start, 1)
    save()
    log(json.dumps(results["verdict"], indent=2))
    log(f"done in {results['total_seconds']}s, peak RSS {results['peak_rss_mb']} MB -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
