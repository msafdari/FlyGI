#!/usr/bin/env python3
"""H-T4T5-CLASS3-DS -- the Task 10 item-2 kill test (class-3 spiking
physiology on T4/T5).

PREREGISTRATION (docs/arenas/task10_menu/killtest_design.md section 2,
frozen 2026-10-23 BEFORE this file existed; restated, not changed):

  PREMISE: at spiking class-3 physiology, the specific MaleCNS T4/T5
  wiring produces Maisak-band direction selectivity where its
  degree-preserving rewires do not. First direct real-vs-rewire
  comparison on the DS statistic at any fidelity.

  - SUBSTRATE: the fc2/fc25 patch verbatim -- 2,701 nodes / 507 driven
    (L1/L2/L3 at histaminergic sign) / 498 scored T4-T5 / 169 columns;
    13x13 input window centered on the right-eye Mi1 median column
    (19,20); scored on the inner 9x9.
  - ENGINE: TemplateLIF extended three ways (declared engineering, not
    tuning): (1) per-type membrane tau via per-neuron Cm with Rm fixed
    (tau = Rm*Cm; trained taus from
    docs/fidelity2/flyvis_trained_params.json), (2) two-state
    exponential synapses per kernel class in place of the ring-buffer
    PSC (long kernels make the template buffer ~450 MB/class -- O(N)
    exponential states; unitary-PSC-equivalent normalization: each
    synapse's time-integrated current for one spike equals the Pisokas
    unitary PSC area scaled by |W|, unit-tested against psc_template),
    (3) signed external drive (histaminergic L1/L2/L3 injection is
    inhibitory). Everything else (V_rest, threshold, AP template, dt,
    background) carried verbatim from cx_class3_killtest.py's pinned
    physiology.
  - WEIGHT MAPPING (AT-2): W_ij = curated_sign(pre) x
    alpha_trained(pre->post) x N_ij x g with ONE global calibrated g
    (fc2's held-out calibration: +45-deg diagonal at 5 col/s, both
    polarities, log grid, target median peak response; scoring never
    feeds back). Secondary declared config, reported: Shiu uniform
    conversion |w| = N x 0.275 mV with NT signs (class-blind; context).
  - STIMULUS + STATISTIC, fc2/fc25 verbatim: moving ON and OFF edges,
    4 directions, speeds {2.5, 5, 10} col/s; evoked = spike count in
    the v2 crossing-locked window (opens 2.0 columns before the front
    reaches the cell, closes 0.75 s after it passes) minus the
    background-rate expectation; DSI = (R_pref - R_anti)/(R_pref +
    R_anti), pref = argmax over directions of speed-pooled response.
  - MAISAK BAND: asserted equal to fc2.BAND_TEXT (pooled per-cell
    median DSI >= 0.30, T4 on ON / T5 on OFF, >= 3 distinct preferred
    directions among T4a-d AND among T5a-d, defined fraction >= 0.5).
  - VARIANT GRID: calibrated g* x global scale {0.5, 1.0, 2.0}.
  - NULL BAR: at every real-passing grid point, all 3 rewires of the
    patch (seeds 4242+0..2) fail the band. Cost-honest order: real
    arms first, rewires only at real-passing points.
  - ATTRIBUTION CONTEXT (reported, non-decisional): uniform-tau
    (50 ms) spiking twin at the same strengths.
  - PASS iff >= 1 grid point clears the band on real with all 3
    rewires failing there; KILL otherwise (given valid gates).
  - GATE A (engine capacity, in-cloud, decisive; idealized circuit
    ASSUMED, anchors ESTABLISHED): an idealized 2-3-arm delay-line
    correlator at the pinned spiking physiology (~1-column offset
    arms; hand-set fast 10-40 ms vs slow 100-300 ms kernels) must
    reach DSI >= 0.30 under the same edge protocol with its
    temporal-frequency optimum inside 0.5-2 Hz, AND collapse to
    DSI < 0.05 with arm taus equalized. Gate A failing = BLOCKED,
    recorded as a measured absence result about the spiking model
    class, never a fly verdict.
  - GATE B (continuity): patch dims reproduce 2,701/507/498/169 and
    the declared fc25-reference values reproduce on the verdict
    machine (v2 median DSI 0.3216) before any class-3 arm runs.
  - BLOCKED floors: (1) runtime or annotations feather absent;
    (2) patch composition deviates; (3) run-time sign audit disagrees
    with the curated I6 table; (4) non-finite membrane in > 20% of
    runs in any arm; (5) Gate A fail; (6) Gate B fail.
  - SCOPE (AT-1): every close sentence is about the spiking model
    class under the declared mapping, never "the fly's T4/T5".

CONSERVATIVE RESOLUTIONS of points the frozen text leaves open (each
also flagged at its code site; none is a tuned constant):
  R1 calibration target: the registration pins the fc2 PROCEDURE but
     the fc2 target (0.5 a.u. graded output) has no spiking unit.
     Resolved: target median evoked rate in the crossing window =
     geometric midpoint of the pinned input-rate band
     sqrt(BG_HZ * DRIVE_PEAK_HZ) ~= 30.8 Hz, log-grid argmin as fc2.
  R2 kernel classes: the 133-300 ms / ~450 MB motivation (133.2 ms =
     Tm2's trained tau) only binds if real synapses carry long
     kernels; resolved as kernel class = presynaptic type, decay tau =
     that type's trained tau, rise = the pinned 2 ms.
  R3 temporal-frequency mapping: fc2's header establishes the speeds
     {2.5,5,10} col/s bracket the ~1 Hz optimum, i.e. TF = {0.5,1,2}
     Hz (ASSUMED lambda ~ 5 columns); "optimum inside 0.5-2 Hz" read
     strictly: the response optimum must sit at the interior point.
  R4 Gate A detectors are declared T4-analogs and scored on ON edges
     (the band's T4 rule); equalization sets both arms to the fast
     kernel (keeps the statistic defined; removes the fast/slow
     asymmetry, which is the manipulated variable).
  R5 Gate B reference tolerance +/-0.02 borrowed from the sibling
     registration's G0 (killtest_design.md section 5), which declared
     it for the same 0.3216 reference; only the primary trained_subset
     value is re-run (cost-honest).
  R6 the twin runs at every real-passing grid point (scale 1.0 if
     none pass); evoked is clamped at 0 (fc2's evoked convention);
     baseline = final 1 s of the settle.

Run:    python scripts/arenas/t4t5_class3_killtest.py
Output: results/arenas/t4t5_class3_killtest.json (+ .log)
Exit:   0 PASS / 1 KILL / 3 BLOCKED
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Single sources of truth: the pinned template-LIF physiology (cx) and
# the frozen patch/stimulus/band machinery (fc2), plus fc25's AT-2
# weight mapping and extended calibration grid.
cx = _load("cx_class3_killtest", ROOT / "scripts/arenas/cx_class3_killtest.py")
fc2 = _load("fc2_visual_ds", ROOT / "scripts/benchmarks/fc2_visual_ds.py")
fc25 = _load("fc25_visual_ds", ROOT / "scripts/benchmarks/fc25_visual_ds.py")

# --- frozen physiology, carried verbatim from the cx pinned set -------------
DT_S = cx.DT_S                      # 1e-4 s
RM_OHM = cx.RM_OHM                  # 1 MOhm, FIXED; per-type tau via Cm
V_REST = cx.V_REST
V_THRESH = cx.V_THRESH
AP_END = cx.AP_END
BG_HZ = cx.BG_HZ                    # background Poisson 5 Hz
DRIVE_PEAK_HZ = cx.DRIVE_PEAK_HZ    # 190 Hz, the pinned drive scale
PISOKAS_TAU_M_MS = 20.0             # the pinned uniform membrane (Cm 20 nF)
# The Pisokas unitary PSC area: the frozen normalization anchor for
# every two-state kernel class (discrete area of the published
# template at the pinned dt).
PISOKAS_UNIT_AREA = float(np.sum(cx.psc_template()) * DT_S)
PSC_RISE_TAU_MS = cx.PSC_RISE_MS    # 2 ms -- reused as the two-state rise tau
PSC_DECAY_TAU_MS = cx.PSC_HALF_MS / math.log(2.0)   # 5 ms half-life -> tau

# --- frozen protocol/statistic constants (fc2/fc25 verbatim) ----------------
BAND_TEXT = (
    "PASS iff pooled per-cell median DSI >= 0.3 (T4 on ON bar, T5 on OFF bar) "
    "AND T4a-d distinct preferred directions >= 3 AND T5a-d distinct >= 3 AND "
    "defined-DSI fraction >= 0.5; preregistered before the sweep"
)
assert BAND_TEXT == fc2.BAND_TEXT, "band drifted from fc2 -- refuse to run"

SPEEDS = fc2.SPEEDS                     # (2.5, 5.0, 10.0) col/s
DIRECTIONS = fc2.DIRECTIONS             # ("+x", "-x", "+y", "-y")
OPPOSITE = fc2.OPPOSITE
DIR_VECTORS = fc2.DIR_VECTORS
CAL_DIRECTION = fc2.CAL_DIRECTION       # held-out +45 deg diagonal
CAL_SPEED = fc2.CAL_SPEED               # 5 col/s
EDGE_MARGIN = fc2.EDGE_MARGIN           # 1 column each side
WINDOW_BEFORE_COL = fc2.WINDOW_BEFORE_COL   # v2 opens 2.0 columns early
WINDOW_AFTER_S = fc2.WINDOW_AFTER_S         # v2 closes 0.75 s after front
SETTLE_S = fc2.SETTLE_MS / 1000.0       # 2.5 s
TAIL_S = fc2.TAIL_MS / 1000.0           # 0.8 s
INPUT_DRIVE_SIGN = -1.0                 # fc2 INPUT_DRIVE: histaminergic sign
assert fc2.INPUT_DRIVE == INPUT_DRIVE_SIGN

# ASSUMPTION (R6): per-cell background expectation uses the rate
# measured over the final 1 s of the settle; the registration pins the
# subtraction, not the estimation window. Wrong if 1 s is too short to
# estimate a 5 Hz-scale rate -- the expectation then carries sampling
# noise into every evoked count symmetrically across arms.
BASELINE_S = 1.0

GRID_SCALES = (0.5, 1.0, 2.0)
REWIRE_SEED_BASE = 4242
REWIRE_SEEDS = (0, 1, 2)
MAX_UNSTABLE_FRACTION = 0.20
RUN_SEED_BASE = 20261023
UNIFORM_TAU_MS = 50.0                   # the twin's tau (fc2/fc25 control)
SHIU_MV_PER_SYNAPSE = 0.275             # Shiu secondary conversion, context

EXPECTED_DIMS = {"nodes": 2701, "driven": 507, "scored": 498, "columns": 169}
GAIN_GRID = fc25.EXTENDED_GAIN_GRID     # fc2 grid continued, {1,3}x10^k

# ASSUMPTION (R1): the spiking calibration target. fc2 targets median
# peak evoked OUTPUT 0.5 a.u.; graded a.u. have no spiking unit, so the
# target is restated as a median evoked RATE in the crossing-locked
# window, pinned to the geometric midpoint of the engine's own declared
# input-rate band [BG_HZ, DRIVE_PEAK_HZ] = sqrt(5*190) ~= 30.8 Hz.
# Wrong if the informative operating point sits far from this rate; the
# log grid still brackets it and every candidate is recorded.
CAL_TARGET_HZ = math.sqrt(BG_HZ * DRIVE_PEAK_HZ)

# ASSUMPTION (R3): temporal-frequency mapping for the gate's optimum
# check. fc2's header (ESTABLISHED there as the design rationale) maps
# speeds {2.5, 5, 10} col/s onto 12.5-50 deg/s "bracketing the ~1 Hz
# optimum", i.e. TF = {0.5, 1.0, 2.0} Hz (lambda ~ 5 columns ~ 25 deg,
# ASSUMED). "Optimum inside 0.5-2 Hz" is read strictly: the argmax over
# the three speeds must be the interior point (1 Hz = 5 col/s).
SPEED_TO_TF_HZ = {2.5: 0.5, 5.0: 1.0, 10.0: 2.0}
GATE_DSI_MIN = 0.30
GATE_COLLAPSE_MAX = 0.05
GATE_TF_BAND_HZ = (0.5, 2.0)

FC25_REFERENCE_DSI = 0.3216             # measured, fc25 trained_subset, v2
FC25_REFERENCE_TOL = 0.02               # R5: sibling G0's declared tolerance

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
ANNOTATIONS = ROOT / "data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather"
PARAMS_JSON = ROOT / "docs/fidelity2/flyvis_trained_params.json"
OUT_JSON = ROOT / "results/arenas/t4t5_class3_killtest.json"


# ---------------------------------------------------------------------------
# Engine: TemplateLIF extended with per-neuron Cm (per-type membrane
# tau), two-state exponential synapses per kernel class, and signed
# external drive. AP template, threshold, reset, dt and background are
# the cx pinned physiology, verbatim.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SynKernel:
    """One synaptic kernel class: difference of exponentials with rise
    and decay time constants (ms). The template's quarter-sine rise is
    operationalized as an exponential rise with the pinned 2 ms rise
    time (shape between endpoints is cosmetic in the source literature,
    as with the cx AP template); the kernel AREA is exact (see
    injection_scale)."""

    rise_tau_ms: float
    decay_tau_ms: float

    def __post_init__(self) -> None:
        if not (self.decay_tau_ms > self.rise_tau_ms > 0.0):
            raise ValueError("SynKernel requires decay_tau > rise_tau > 0")


PISOKAS_KERNEL = SynKernel(PSC_RISE_TAU_MS, PSC_DECAY_TAU_MS)


def injection_scale(kernel: SynKernel) -> float:
    """Per-spike state increment q such that the DISCRETE time-integrated
    current of one spike at |W| = 1 equals the Pisokas unitary PSC area
    (the frozen unitary-PSC-equivalent normalization). The injected pair
    (P += q, R += q) yields current q*(ad^k - ar^k) on the k-th step
    after injection; sum_k>=1 q*(ad^k - ar^k)*dt is matched to
    sum(psc_template)*dt exactly."""
    ad = math.exp(-DT_S / (kernel.decay_tau_ms * 1e-3))
    ar = math.exp(-DT_S / (kernel.rise_tau_ms * 1e-3))
    unit_area = DT_S * (ad / (1.0 - ad) - ar / (1.0 - ar))
    return PISOKAS_UNIT_AREA / unit_area


class TwoStateLIF:
    """Current-based LIF with the cx AP template and O(N)-state
    difference-of-exponential synapses.

    projections: list of (SynKernel, W) with W[post, pre] in
    unitary-PSC equivalents per presynaptic spike (parallel projections
    may share (post, pre) pairs -- needed by the ideal correlator's
    push-pull transient stage). tau_m_ms: per-neuron membrane time
    constant; Cm_i = tau_i / Rm with Rm FIXED at the pinned 1 MOhm
    (tau = Rm * Cm, the declared per-type-membrane extension).

    External drive is signed: step() takes independent excitatory and
    inhibitory Poisson rate vectors; each event injects one +/- unitary
    PSC through the pinned Pisokas kernel class."""

    def __init__(self, projections, tau_m_ms, seed: int):
        from scipy import sparse

        tau = np.asarray(tau_m_ms, dtype=np.float64)
        self.n = tau.size
        self.cm = tau * 1e-3 / RM_OHM      # tau = Rm*Cm  =>  Cm = tau/Rm
        self.proj = []
        for kernel, W in projections:
            Wc = sparse.csc_matrix(W, dtype=np.float64)
            if Wc.shape != (self.n, self.n):
                raise ValueError("projection shape mismatch")
            colnnz = np.diff(Wc.indptr) > 0
            self.proj.append((kernel, Wc, injection_scale(kernel), colnnz))
        kernels = [PISOKAS_KERNEL] + [p[0] for p in self.proj]
        self.dec_d = np.array(
            [math.exp(-DT_S / (k.decay_tau_ms * 1e-3)) for k in kernels])
        self.dec_r = np.array(
            [math.exp(-DT_S / (k.rise_tau_ms * 1e-3)) for k in kernels])
        self.q_ext = injection_scale(PISOKAS_KERNEL)
        self.P = np.zeros((len(kernels), self.n))
        self.R = np.zeros((len(kernels), self.n))
        self.ap = cx.ap_template()
        self.v = np.full(self.n, V_REST)
        self.phase = np.full(self.n, -1, dtype=np.int64)
        self.rng = np.random.default_rng(seed)
        self.unstable = False

    def snapshot(self) -> dict:
        return {"v": self.v.copy(), "phase": self.phase.copy(),
                "P": self.P.copy(), "R": self.R.copy(),
                "rng": self.rng.bit_generator.state,
                "unstable": self.unstable}

    def restore(self, snap: dict) -> None:
        self.v = snap["v"].copy()
        self.phase = snap["phase"].copy()
        self.P = snap["P"].copy()
        self.R = snap["R"].copy()
        self.rng = np.random.default_rng()
        self.rng.bit_generator.state = snap["rng"]
        self.unstable = snap["unstable"]

    def step(self, exc_rate_hz: np.ndarray,
             inh_rate_hz: np.ndarray) -> np.ndarray:
        """One dt. Signed external drive: two independent Poisson
        streams; an excitatory event injects +1 unitary PSC, an
        inhibitory event -1 (extension 3; the histaminergic L1/L2/L3
        stimulus runs on the inhibitory stream)."""
        ext_e = self.rng.random(self.n) < exc_rate_hz * DT_S
        ext_i = self.rng.random(self.n) < inh_rate_hz * DT_S
        self.P *= self.dec_d[:, None]
        self.R *= self.dec_r[:, None]
        if ext_e.any() or ext_i.any():
            inc0 = self.q_ext * (ext_e.astype(np.float64)
                                 - ext_i.astype(np.float64))
            self.P[0] += inc0
            self.R[0] += inc0
        current = (self.P - self.R).sum(axis=0)

        playing = self.phase >= 0
        free = ~playing
        dv = ((V_REST - self.v[free]) / RM_OHM + current[free]) \
            * (DT_S / self.cm[free])
        self.v[free] = self.v[free] + dv
        self.v[playing] = self.ap[self.phase[playing]]
        self.phase[playing] += 1
        done = self.phase >= self.ap.size
        self.v[done] = AP_END
        self.phase[done] = -1

        spikes = (self.v >= V_THRESH) & (self.phase < 0)
        if spikes.any():
            cols = np.flatnonzero(spikes)
            for k, (_, Wc, q, colnnz) in enumerate(self.proj):
                if not colnnz[cols].any():
                    continue
                inc = q * np.asarray(Wc[:, cols].sum(axis=1)).ravel()
                self.P[k + 1] += inc
                self.R[k + 1] += inc
            self.phase[spikes] = 0
            self.v[spikes] = self.ap[0]
        if not np.all(np.isfinite(self.v)):
            self.unstable = True
        return spikes


def two_state_unit_response(kernel: SynKernel, weight: float,
                            n_steps: int) -> np.ndarray:
    """The discrete current waveform one presynaptic spike produces
    through one synapse of weight `weight` (used by the normalization
    unit test against cx.psc_template)."""
    q = injection_scale(kernel) * weight
    ad = math.exp(-DT_S / (kernel.decay_tau_ms * 1e-3))
    ar = math.exp(-DT_S / (kernel.rise_tau_ms * 1e-3))
    k = np.arange(1, n_steps + 1, dtype=np.float64)
    return q * (np.power(ad, k) - np.power(ar, k))


def unitary_psp_mv(tau_m_ms: float = PISOKAS_TAU_M_MS) -> float:
    """Peak subthreshold depolarization (mV) of ONE unitary PSC on the
    pinned membrane: the DERIVED unit bridge for the Shiu secondary
    conversion (|w| = N x 0.275 mV). ASSUMPTION: Shiu's per-synapse mV
    is mapped through the pinned Pisokas membrane, not Shiu's own
    engine constants -- the bridge is the declared class-blind context
    conversion, not a fit."""
    psc = cx.psc_template()
    cm_f = tau_m_ms * 1e-3 / RM_OHM
    v = 0.0                                  # relative to rest
    peak = 0.0
    for k in range(psc.size + int(10 * tau_m_ms * 1e-3 / DT_S)):
        current = psc[k] if k < psc.size else 0.0
        v += (-v / RM_OHM + current) * (DT_S / cm_f)
        peak = max(peak, v)
    return peak * 1e3


# ---------------------------------------------------------------------------
# Weight mapping and parameter tables
# ---------------------------------------------------------------------------

def load_trained_params() -> dict:
    return json.loads(PARAMS_JSON.read_text())


def membrane_tau_vector(types: np.ndarray, params: dict,
                        which: str = "subset",
                        uniform_ms: float | None = None) -> np.ndarray:
    """Per-neuron membrane tau (ms). ASSUMPTION (AT-2 companion): the
    flyvis trained per-type time constants, fitted to GRADED dynamics,
    are imported as spiking MEMBRANE time constants via Cm = tau/Rm at
    fixed Rm (the registration's extension 1). The bridge is untested
    by construction; the uniform-tau twin measures whether it is
    load-bearing."""
    if uniform_ms is not None:
        return np.full(types.size, float(uniform_ms))
    table = params["types"]
    missing = sorted(set(types.tolist()) - set(table))
    if missing:
        raise KeyError(f"types without trained tau: {missing}")
    return np.array([table[t]["tau_ms"][f"{which}_mean"] for t in types])


def synapse_projections(W, types: np.ndarray, params: dict,
                        which: str = "subset",
                        uniform_ms: float | None = None) -> list:
    """Split W[post, pre] into per-kernel-class projections.

    ASSUMPTION (R2 / AT-2 companion): the registration's "two-state
    exponential synapses per kernel class" with its 133-300 ms / ~450
    MB-per-class motivation (133.2 ms is exactly Tm2's trained tau) is
    resolved as: kernel class = presynaptic type, decay tau = that
    type's trained tau, rise tau = the pinned 2 ms, area = Pisokas
    unitary x |W| (frozen normalization). A presynaptic type's trained
    tau therefore shapes both its own membrane and its outgoing PSC.
    To check: a registered variant separating the two placements.
    What breaks if wrong: the effective temporal filtering per pathway
    is doubled relative to the graded flyvis form -- a model-class
    statement risk (AT-1 scope), not a wiring-comparison risk, because
    every arm (real, rewires, twin) shares the identical rule."""
    from scipy import sparse

    coo = sparse.coo_matrix(W)
    if uniform_ms is not None:
        kern = SynKernel(PSC_RISE_TAU_MS, float(uniform_ms))
        return [(kern, sparse.csc_matrix(W))]
    pre_types = types[coo.col]
    out = []
    for t in sorted(set(pre_types.tolist())):
        sel = pre_types == t
        if not sel.any():
            continue
        tau = params["types"][t]["tau_ms"][f"{which}_mean"]
        kern = SynKernel(PSC_RISE_TAU_MS, float(tau))
        Wt = sparse.csc_matrix(
            (coo.data[sel], (coo.row[sel], coo.col[sel])), shape=W.shape)
        out.append((kern, Wt))
    return out


def at2_weight_matrix(patch_like: dict, params: dict,
                      which: str = "subset"):
    """AT-2 (ASSUMPTION, register row AT-2): W_ij = curated_sign(pre) x
    alpha_trained(pre->post) x N_ij x g. The trained alphas are GRADED
    per-pair unitary strengths (flyvis flow/0000) imported across a
    dynamics tier into unitary-PSC-equivalent spiking weights; no
    published per-class spiking weight set exists for this circuit, so
    the mapping is an invention whose global scale is absorbed by the
    calibrated g and whose relative per-pair scale is uncorrected.
    Implemented by fc25.trained_weight_matrix (single source of truth;
    pairs absent from the trained set get flyvis's init rho/<N>)."""
    alpha = {p: v[f"{which}_mean"] for p, v in params["pairs"].items()}
    return fc25.trained_weight_matrix(fc2, patch_like, alpha)


def shiu_weight_matrix(patch_like: dict):
    """Secondary declared config (context, non-decisional): Shiu
    uniform conversion |w| = N x 0.275 mV with NT signs, class-blind.
    The mV -> unitary-PSC bridge is DERIVED (unitary_psp_mv), not
    fitted. Shiu never tested vision; carried as context only."""
    from scipy import sparse

    coo = patch_like["raw_counts"].tocoo()
    types = patch_like["types"]
    pre_types = types[coo.col]
    curated = np.array([fc2.CURATED_SIGNS.get(t, 0) for t in pre_types])
    signs = np.where(curated != 0, curated, np.sign(coo.data))
    unit = SHIU_MV_PER_SYNAPSE / unitary_psp_mv()
    weight = signs * np.abs(coo.data) * unit
    return sparse.csc_matrix((weight, (coo.row, coo.col)),
                             shape=patch_like["raw_counts"].shape)


# ---------------------------------------------------------------------------
# The frozen stimulus/statistic machinery, spiking side
# ---------------------------------------------------------------------------

def traverse_geometry(x: np.ndarray, y: np.ndarray, dvec, speed: float):
    """fc2.run_sweep's traverse rule, verbatim: same traverse length
    for every direction at a given speed."""
    dx, dy = dvec
    proj = x * dx + y * dy
    extent = float(max(np.ptp(x), np.ptp(y),
                       np.ptp(x * (2 ** -0.5) + y * (2 ** -0.5))))
    front0 = float(proj.min()) - EDGE_MARGIN
    travel = extent + 2 * EDGE_MARGIN
    steps = int(round((travel / speed + TAIL_S) / DT_S))
    return proj, front0, steps


def settle_arm(engine: TwoStateLIF, driven_idx: np.ndarray,
               polarity: str, drive_sign: float):
    """2.5 s settle on background + the pre-edge luminance (dark before
    an ON edge, bright before an OFF edge); background rate measured
    over the final BASELINE_S. Returns (baseline_hz, stable)."""
    lum = 1.0 if polarity == "off" else 0.0
    exc = np.full(engine.n, BG_HZ)
    inh = np.zeros(engine.n)
    rate = DRIVE_PEAK_HZ * lum
    if drive_sign < 0:
        inh[driven_idx] = rate
    else:
        exc[driven_idx] += rate
    steps = int(round(SETTLE_S / DT_S))
    base_steps = int(round(BASELINE_S / DT_S))
    counts = np.zeros(engine.n)
    for k in range(steps):
        s = engine.step(exc, inh)
        if k >= steps - base_steps:
            counts += s
    return counts / BASELINE_S, not engine.unstable


def run_edge_sweep(engine: TwoStateLIF, snap: dict, x: np.ndarray,
                   y: np.ndarray, driven_idx: np.ndarray,
                   score_idx: np.ndarray, baseline_hz: np.ndarray,
                   dvec, speed: float, polarity: str, drive_sign: float):
    """One moving-edge sweep from the settled snapshot. Evoked per
    scored cell = spike count in its v2 crossing-locked window minus
    the background-rate expectation over the window steps actually
    inside the sweep, clamped at 0 (fc2's evoked convention, R6).
    Returns (evoked, window_s, stable)."""
    engine.restore(snap)
    proj, front0, steps = traverse_geometry(x, y, dvec, speed)
    driven_proj = proj[driven_idx]
    crossing = (proj[score_idx] - front0) / speed
    w_open = crossing - WINDOW_BEFORE_COL / speed
    w_close = crossing + WINDOW_AFTER_S
    exc = np.full(engine.n, BG_HZ)
    inh = np.zeros(engine.n)
    counts = np.zeros(score_idx.size)
    win_steps = np.zeros(score_idx.size)
    check_every = max(1, int(round(0.005 / DT_S)))
    for k in range(steps):
        t = k * DT_S
        behind = driven_proj <= front0 + speed * t
        lum = behind if polarity == "on" else ~behind
        rate = DRIVE_PEAK_HZ * lum.astype(np.float64)
        if drive_sign < 0:
            inh[driven_idx] = rate
        else:
            exc[driven_idx] = BG_HZ + rate
        s = engine.step(exc, inh)
        inw = (t >= w_open) & (t <= w_close)
        counts += np.where(inw & s[score_idx], 1.0, 0.0)
        win_steps += inw
        if k % check_every == 0 and engine.unstable:
            break
    window_s = win_steps * DT_S
    evoked = np.maximum(counts - baseline_hz[score_idx] * window_s, 0.0)
    return evoked, window_s, not engine.unstable


def protocol_responses(make_engine, x, y, driven_idx, score_idx, seed,
                       drive_sign, polarities=("on", "off"), log=None):
    """The full fc2 protocol (4 directions x 3 speeds per polarity)
    through the spiking engine. Returns (acc, acc_speed, n_unstable,
    n_runs) with acc[pol] shape (4, m) speed-pooled evoked and
    acc_speed[pol] shape (3, 4, m) -- the exact inputs
    fc2.band_metrics expects."""
    m = score_idx.size
    acc = {p: np.zeros((len(DIRECTIONS), m)) for p in ("on", "off")}
    acc_speed = {p: np.zeros((len(SPEEDS), len(DIRECTIONS), m))
                 for p in ("on", "off")}
    n_unstable, n_runs = 0, 0
    for pi, pol in enumerate(polarities):
        engine = make_engine(seed + pi)
        baseline_hz, ok = settle_arm(engine, driven_idx, pol, drive_sign)
        n_runs += 1
        n_unstable += int(not ok)
        if not ok:
            continue
        snap = engine.snapshot()
        for si, speed in enumerate(SPEEDS):
            for di, dname in enumerate(DIRECTIONS):
                evoked, _, ok = run_edge_sweep(
                    engine, snap, x, y, driven_idx, score_idx,
                    baseline_hz, DIR_VECTORS[dname], speed, pol,
                    drive_sign)
                n_runs += 1
                n_unstable += int(not ok)
                acc[pol][di] += evoked
                acc_speed[pol][si, di] = evoked
        if log is not None:
            log(f"    {pol}: median pooled evoked "
                f"{float(np.median(acc[pol].sum(axis=0))):.2f}")
    return acc, acc_speed, n_unstable, n_runs


def dsi_from_responses(resp: np.ndarray, per_speed: np.ndarray):
    """Per-cell DSI from a (4, m) speed-pooled response table and the
    (3, 4, m) per-speed table: the frozen formula (pref = argmax of
    speed-pooled response, anti = opposite, DSI = (P-A)/(P+A)).
    Returns (dsi, defined, pref_idx, speed_pref (3, m))."""
    m = resp.shape[1]
    pref = np.argmax(resp, axis=0)
    anti = np.array([DIRECTIONS.index(OPPOSITE[DIRECTIONS[p]])
                     for p in pref])
    cells = np.arange(m)
    r_p, r_a = resp[pref, cells], resp[anti, cells]
    denom = r_p + r_a
    defined = denom > 1e-9
    dsi = np.full(m, np.nan)
    dsi[defined] = (r_p[defined] - r_a[defined]) / denom[defined]
    speed_pref = per_speed[:, pref, cells]
    return dsi, defined, pref, speed_pref


# ---------------------------------------------------------------------------
# GATE A -- engine capacity (in-cloud, decisive; asserted by unit test)
# ---------------------------------------------------------------------------
# ABSENCE FINDING (recorded in the registration): no published spiking
# motion detector with pinned parameters exists to reproduce; the
# honest fallback is this idealized correlator. HYPOTHESIS under test
# by the gate itself: the pinned spiking physiology can express a
# fast-vs-slow delay-line code at all. The circuit below is ASSUMED
# (hand-set); its anchors are ESTABLISHED (fast/slow interneuron
# classes: Behnia 2014, Arenz 2017, Borst 2025; HRC ~1 Hz optimum).
#
# Architecture (2-arm delay line, ~1-column offsets):
#   X cells (GATE_NX per column, Poisson-driven by luminance through
#     the signed external drive at the pinned 190 Hz scale) ->
#   T cells (GATE_NT per column): push-pull transient stage, fast
#     excitation minus DOMINANT slower inhibition from the same X
#     population, so the steady state is net suppressive and a
#     sustained edge yields a strictly transient, stereotyped burst
#     (the fc2 v1 standing-DC lesson, applied at design time) ->
#   D detectors: slow kernel from the LEADING column's T (the delay
#     arm) + fast kernel from the HOME column's T (the direct arm);
#     threshold coincidence. 3 detectors per direction x 4 directions.
#
# Hand-set values below are the gate circuit's own parameters (the
# idealized-circuit ASSUMPTION), not instrument constants: the frozen
# bars are DSI >= 0.30, strict-interior TF optimum, collapse < 0.05.
# Kernel time constants sit inside the registered bands (fast 10-40 ms,
# slow 100-300 ms).

GATE_SEED = 7
GATE_NX = 24                      # X cells per column (Poisson smoothing)
GATE_NT = 2                       # transient cells per column
GATE_FAST_KERNEL = SynKernel(2.0, 20.0)      # direct arm (10-40 ms band)
GATE_SLOW_KERNEL = SynKernel(150.0, 300.0)   # delay arm (100-300 ms band)
GATE_TGEN_EXC_KERNEL = SynKernel(2.0, 20.0)  # transient stage, fast half
GATE_TGEN_INH_KERNEL = SynKernel(2.0, 100.0)  # transient stage, slow half
GATE_W_XT = 10.0                  # X -> T excitation (per X cell)
GATE_W_XT_INH = 13.0              # X -> T inhibition: > excitation, so the
#                                   steady state is net suppressive and T is
#                                   strictly transient (the fc2-v1 standing-
#                                   DC lesson applied at design time)
GATE_W_ARM_SLOW = 8.0             # T(lead) -> D, slow kernel (summed/column)
GATE_W_ARM_FAST = 1.7             # T(home) -> D, fast kernel (summed/column)
GATE_N_DETECTORS_PER_DIR = 3


def build_ideal_correlator(equalized: bool) -> dict:
    """Build the gate circuit. equalized=True is the gate's own trivial
    alternative: both delay-line arms carry the SAME kernel (the fast
    one, R4), removing the fast/slow asymmetry while keeping every
    weight, position and the transient stage identical."""
    from scipy import sparse

    columns: list[tuple[float, float]] = []
    for k in range(-3, 4):
        columns.append((float(k), 0.0))
    for k in range(-3, 4):
        if k != 0:
            columns.append((0.0, float(k)))
    col_of = {c: i for i, c in enumerate(columns)}
    n_cols = len(columns)
    n_x = n_cols * GATE_NX
    n_t = n_cols * GATE_NT
    detectors = []                      # (position, direction name)
    for dname in DIRECTIONS:
        dx, dy = DIR_VECTORS[dname]
        for o in range(GATE_N_DETECTORS_PER_DIR):
            pos = (-dx * o, -dy * o)
            lead = (pos[0] - dx, pos[1] - dy)
            detectors.append({"pos": pos, "dir": dname,
                              "home_col": col_of[pos],
                              "lead_col": col_of[lead]})
    n_d = len(detectors)
    n = n_x + n_t + n_d
    x = np.zeros(n)
    y = np.zeros(n)
    for ci, (cx_, cy_) in enumerate(columns):
        for j in range(GATE_NX):
            x[ci * GATE_NX + j] = cx_
            y[ci * GATE_NX + j] = cy_
        for j in range(GATE_NT):
            x[n_x + ci * GATE_NT + j] = cx_
            y[n_x + ci * GATE_NT + j] = cy_
    for di, det in enumerate(detectors):
        x[n_x + n_t + di], y[n_x + n_t + di] = det["pos"]

    W_tgen_e = sparse.lil_matrix((n, n))
    W_tgen_i = sparse.lil_matrix((n, n))
    for ci in range(n_cols):
        for jt in range(GATE_NT):
            for j in range(GATE_NX):
                W_tgen_e[n_x + ci * GATE_NT + jt,
                         ci * GATE_NX + j] = GATE_W_XT
                W_tgen_i[n_x + ci * GATE_NT + jt,
                         ci * GATE_NX + j] = -GATE_W_XT_INH
    # arm weight is the column total, split over the column's T cells
    W_slow = sparse.lil_matrix((n, n))
    W_fast = sparse.lil_matrix((n, n))
    for di, det in enumerate(detectors):
        for jt in range(GATE_NT):
            W_slow[n_x + n_t + di, n_x + det["lead_col"] * GATE_NT + jt] = \
                GATE_W_ARM_SLOW / GATE_NT
            W_fast[n_x + n_t + di, n_x + det["home_col"] * GATE_NT + jt] = \
                GATE_W_ARM_FAST / GATE_NT
    slow_kernel = GATE_FAST_KERNEL if equalized else GATE_SLOW_KERNEL
    projections = [
        (GATE_TGEN_EXC_KERNEL, W_tgen_e.tocsc()),
        (GATE_TGEN_INH_KERNEL, W_tgen_i.tocsc()),   # push-pull transient
        (slow_kernel, W_slow.tocsc()),
        (GATE_FAST_KERNEL, W_fast.tocsc()),
    ]
    return {
        "projections": projections,
        # the gate runs AT THE PINNED SPIKING PHYSIOLOGY: uniform
        # 20 ms membrane (Cm 20 nF at Rm 1 MOhm), per the registration
        "tau_m_ms": np.full(n, PISOKAS_TAU_M_MS),
        "x": x, "y": y,
        "driven_idx": np.arange(n_x),
        "score_idx": np.arange(n_x + n_t, n),
        "detector_dirs": [d["dir"] for d in detectors],
    }


def run_gate_a(seed: int = GATE_SEED, log=None) -> dict:
    """GATE A, the decisive in-cloud engine-capacity gate. Scored on ON
    edges only (R4: the detectors are declared T4-analogs and the band
    scores T4 on ON edges). Drive sign is positive for the ideal input
    cells (the histaminergic inversion is a property of the real
    lamina, not of the idealized detector)."""
    report: dict[str, Any] = {
        "seed": seed,
        "circuit": {
            "nx_per_column": GATE_NX, "nt_per_column": GATE_NT,
            "detectors_per_direction": GATE_N_DETECTORS_PER_DIR,
            "w_xt_exc": GATE_W_XT, "w_xt_inh": GATE_W_XT_INH,
            "w_arm_slow": GATE_W_ARM_SLOW, "w_arm_fast": GATE_W_ARM_FAST,
            "fast_kernel_ms": (GATE_FAST_KERNEL.rise_tau_ms,
                               GATE_FAST_KERNEL.decay_tau_ms),
            "slow_kernel_ms": (GATE_SLOW_KERNEL.rise_tau_ms,
                               GATE_SLOW_KERNEL.decay_tau_ms),
            "tgen_exc_kernel_ms": (GATE_TGEN_EXC_KERNEL.rise_tau_ms,
                                   GATE_TGEN_EXC_KERNEL.decay_tau_ms),
            "tgen_inh_kernel_ms": (GATE_TGEN_INH_KERNEL.rise_tau_ms,
                                   GATE_TGEN_INH_KERNEL.decay_tau_ms),
            "membrane_tau_ms": PISOKAS_TAU_M_MS,
        },
    }
    for label, equalized in (("delay_line", False), ("equalized", True)):
        circuit = build_ideal_correlator(equalized)

        def make_engine(s, _c=circuit):
            return TwoStateLIF(_c["projections"], _c["tau_m_ms"], seed=s)

        acc, acc_speed, n_unstable, n_runs = protocol_responses(
            make_engine, circuit["x"], circuit["y"],
            circuit["driven_idx"], circuit["score_idx"], seed,
            drive_sign=+1.0, polarities=("on",), log=None)
        dsi, defined, pref, speed_pref = dsi_from_responses(
            acc["on"], acc_speed["on"])
        median_dsi = float(np.median(dsi[defined])) if defined.any() \
            else float("nan")
        med_per_speed = [float(np.median(speed_pref[si][defined]))
                         if defined.any() else float("nan")
                         for si in range(len(SPEEDS))]
        arm = {
            "median_dsi": median_dsi,
            "defined_fraction": float(defined.mean()),
            "per_cell_dsi": [round(float(v), 4) for v in dsi],
            "preferred": [DIRECTIONS[p] for p in pref],
            "designed": circuit["detector_dirs"],
            "median_pref_response_per_speed": med_per_speed,
            "unstable_runs": n_unstable, "runs": n_runs,
        }
        if label == "delay_line":
            opt_idx = int(np.argmax(med_per_speed))
            tf = SPEED_TO_TF_HZ[SPEEDS[opt_idx]]
            arm["tf_optimum_hz"] = tf
            arm["tf_inside_band"] = bool(
                GATE_TF_BAND_HZ[0] < tf < GATE_TF_BAND_HZ[1])
        report[label] = arm
        if log is not None:
            log(f"  gate A {label}: median DSI {median_dsi:.4f} "
                f"defined {arm['defined_fraction']:.2f} "
                f"per-speed {['%.1f' % v for v in med_per_speed]}")
    dl, eq = report["delay_line"], report["equalized"]
    report["pass"] = bool(
        np.isfinite(dl["median_dsi"])
        and dl["median_dsi"] >= GATE_DSI_MIN
        and dl["tf_inside_band"]
        and np.isfinite(eq["median_dsi"])
        and eq["median_dsi"] < GATE_COLLAPSE_MAX
        and dl["unstable_runs"] == 0 and eq["unstable_runs"] == 0)
    return report


# ---------------------------------------------------------------------------
# GATE B -- continuity (data-gated, runs locally before any class-3 arm)
# ---------------------------------------------------------------------------

def patch_column_count(x: np.ndarray, y: np.ndarray) -> int:
    """Distinct occupied hex columns of the patch. The plane embedding
    is inverted back to axial coordinates and rounded to the nearest
    integer column (ASSUMPTION: the frozen 169 = full occupancy of the
    13x13 input window under nearest-column assignment)."""
    h2 = y / (3 ** 0.5 / 2.0)
    h1 = x - 0.5 * h2
    cols = {(int(round(a)), int(round(b))) for a, b in zip(h1, h2)}
    return len(cols)


def gate_b_dims(patch: dict, driven_count: int, scored_count: int) -> dict:
    measured = {
        "nodes": int(patch["node_count"]),
        "driven": int(driven_count),
        "scored": int(scored_count),
        "columns": patch_column_count(patch["x"], patch["y"]),
    }
    return {"measured": measured, "expected": EXPECTED_DIMS,
            "pass": measured == EXPECTED_DIMS}


def run_gate_b_fc25(patch: dict, params: dict, score_idx: np.ndarray,
                    score_types: np.ndarray, handle) -> dict:
    """Reproduce the declared fc25 reference (trained_subset, v2 median
    DSI 0.3216) on the verdict machine: the identical fc25 code path
    (fc2 graded dynamics, extended calibration grid, fc2.score_config).
    R5: tolerance +/-0.02; the uniform twin reference (0.3365) is
    recorded but not re-run (cost-honest)."""
    fc2.GAIN_GRID = fc25.EXTENDED_GAIN_GRID
    matrix, coverage = at2_weight_matrix(patch, params, "subset")
    patch["matrix"] = matrix
    table = fc25.trained_table(fc2, params, "subset", None)
    cal = fc2.calibrate(patch, table, score_idx, score_types, handle)
    out = {"coverage": coverage, "calibration_chosen_gain":
           cal["chosen_gain"], "reference_dsi": FC25_REFERENCE_DSI,
           "tolerance": FC25_REFERENCE_TOL,
           "twin_reference_not_rerun": 0.3365}
    if cal["chosen_gain"] is None:
        out.update({"measured_dsi": None, "pass": False,
                    "blocker": "no stable nonzero gain"})
        return out
    result = fc2.score_config(patch, table, cal["chosen_gain"],
                              score_idx, score_types, handle)
    if result is None:
        out.update({"measured_dsi": None, "pass": False,
                    "blocker": "settle diverged at calibrated gain"})
        return out
    dsi = result["readout_v2_crossing_window"]["median_dsi_pooled"]
    out["measured_dsi"] = dsi
    out["pass"] = bool(np.isfinite(dsi)
                       and abs(dsi - FC25_REFERENCE_DSI)
                       <= FC25_REFERENCE_TOL)
    return out


# ---------------------------------------------------------------------------
# Calibration and arms (data-gated)
# ---------------------------------------------------------------------------

def calibrate_gain(base_W, patch: dict, params: dict,
                   score_idx: np.ndarray, score_types: np.ndarray,
                   seed: int, log) -> dict:
    """fc2's declared held-out calibration, spiking side: one global g,
    chosen on the +45-deg diagonal at 5 col/s in both polarities;
    metric = median evoked rate in the crossing window over
    T4-on-ON u T5-on-OFF (the scoring's own population and response);
    log-grid argmin |log(metric / CAL_TARGET_HZ)| subject to stability.
    Scoring never feeds back (frozen)."""
    is_t4 = np.array([t.startswith("T4") for t in score_types])
    types = patch["types"]
    x, y = patch["x"], patch["y"]
    driven_idx = np.flatnonzero(patch["driven_mask"])
    curve, best = [], None
    for g in GAIN_GRID:
        projections = synapse_projections(base_W * g, types, params)
        tau = membrane_tau_vector(types, params)

        def make_engine(s, _p=projections, _t=tau):
            return TwoStateLIF(_p, _t, seed=s)

        rates, stable = [], True
        for pi, (pol, member) in enumerate((("on", is_t4),
                                            ("off", ~is_t4))):
            engine = make_engine(seed + pi)
            baseline_hz, ok = settle_arm(engine, driven_idx, pol,
                                         INPUT_DRIVE_SIGN)
            if not ok:
                stable = False
                break
            snap = engine.snapshot()
            evoked, window_s, ok = run_edge_sweep(
                engine, snap, x, y, driven_idx, score_idx, baseline_hz,
                CAL_DIRECTION, CAL_SPEED, pol, INPUT_DRIVE_SIGN)
            stable &= ok
            rates.append((evoked / np.maximum(window_s, 1e-9))[member])
        if not stable or not rates:
            curve.append({"gain": g, "stable": False})
            log(f"  cal gain {g:g}: unstable")
            continue
        med = float(np.median(np.concatenate(rates)))
        curve.append({"gain": g, "stable": True,
                      "median_evoked_hz": med})
        log(f"  cal gain {g:g}: median evoked {med:.3f} Hz")
        if med > 1e-9:
            loss = abs(math.log10(med / CAL_TARGET_HZ))
            if best is None or loss < best[0]:
                best = (loss, g, med)
    return {"curve": curve,
            "chosen_gain": best[1] if best else None,
            "chosen_median_evoked_hz": best[2] if best else None,
            "target_median_evoked_hz": CAL_TARGET_HZ,
            "held_out_stimulus": "edge along +45deg diagonal, 5 col/s, "
                                 "both polarities; metric = median "
                                 "evoked rate in the v2 window over "
                                 "T4-on-ON u T5-on-OFF"}


def score_class3_arm(W, patch: dict, params: dict, seed: int,
                     tau_uniform_ms: float | None,
                     kernel_uniform_ms: float | None, log) -> dict:
    """One full class-3 arm at a fixed weight matrix: the frozen
    protocol through the spiking engine, verdict by fc2.band_metrics
    (the frozen verdict machine, v2 statistic)."""
    types = patch["types"]
    x, y = patch["x"], patch["y"]
    driven_idx = np.flatnonzero(patch["driven_mask"])
    score_mask = np.isin(types, fc2.T4_SUBTYPES + fc2.T5_SUBTYPES)
    score_idx = np.flatnonzero(score_mask)
    score_types = types[score_idx]
    is_t4 = np.array([t.startswith("T4") for t in score_types])
    projections = synapse_projections(W, types, params,
                                      uniform_ms=kernel_uniform_ms)
    tau = membrane_tau_vector(types, params, uniform_ms=tau_uniform_ms)

    def make_engine(s, _p=projections, _t=tau):
        return TwoStateLIF(_p, _t, seed=s)

    acc, acc_speed, n_unstable, n_runs = protocol_responses(
        make_engine, x, y, driven_idx, score_idx, seed,
        INPUT_DRIVE_SIGN, log=log)
    band = fc2.band_metrics(acc, acc_speed, score_types, is_t4)
    return {"band": band, "unstable_runs": n_unstable, "runs": n_runs}


def check_prerequisites() -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not ANNOTATIONS.exists():
        missing.append(f"raw annotations feather: {ANNOTATIONS}")
    if not PARAMS_JSON.exists():
        missing.append(f"trained params JSON: {PARAMS_JSON}")
    for mod in ("scipy", "pyarrow"):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    return missing


# ---------------------------------------------------------------------------
# Data-gated assembly (local host only)
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-T4T5-CLASS3-DS kill test (data-gated)")
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
    record: dict[str, Any] = {
        "hypothesis": "H-T4T5-CLASS3-DS",
        "band": BAND_TEXT, "citation": fc2.CITATION,
        # AT-1 (ASSUMPTION, register row AT-1): spiking-tier scope.
        # Every sentence below is about the SPIKING MODEL CLASS under
        # the declared mapping, never "the fly's T4/T5"; the graded/
        # conductance rung is declined, recorded in the registration.
        "scope_at1": "spiking model class (template-LIF tier) under the "
                     "AT-2 mapping; never a statement about the fly's "
                     "T4/T5",
        "pinned_physiology": {
            "dt_s": DT_S, "rm_ohm": RM_OHM, "v_rest": V_REST,
            "v_thresh": V_THRESH, "ap_end": AP_END, "bg_hz": BG_HZ,
            "drive_peak_hz": DRIVE_PEAK_HZ,
            "pisokas_unit_area_C": PISOKAS_UNIT_AREA,
        },
    }

    # GATE A first (pre-data; also asserted in-cloud by the unit test).
    gate_a = run_gate_a(log=log)
    record["gate_a"] = gate_a
    log(f"gate A pass={gate_a['pass']} "
        f"(delay-line median DSI {gate_a['delay_line']['median_dsi']:.4f}, "
        f"tf {gate_a['delay_line'].get('tf_optimum_hz')} Hz, equalized "
        f"{gate_a['equalized']['median_dsi']:.4f})")
    if not gate_a["pass"]:
        log("BLOCKED: gate A failed -- a measured absence result about "
            "the spiking model class ('spiking discretization destroys "
            "the delay code'), never a fly verdict")
        record["verdict"] = "BLOCKED"
        args.output.write_text(json.dumps(record, indent=2, default=float))
        return 3

    # Patch (fc2 verbatim) + dims + sign-audit floors.
    patch = fc2.build_patch()
    types = patch["types"]
    patch["driven_mask"] = np.isin(types, fc2.DRIVEN_TYPES)
    score_mask = np.isin(types, fc2.T4_SUBTYPES + fc2.T5_SUBTYPES)
    score_idx = np.flatnonzero(score_mask)
    score_types = types[score_idx]
    dims = gate_b_dims(patch, int(patch["driven_mask"].sum()),
                       int(score_idx.size))
    record["gate_b_dims"] = dims
    log(f"gate B dims: {dims['measured']} pass={dims['pass']}")
    if not dims["pass"]:
        log("BLOCKED: patch composition deviates from the frozen dims")
        record["verdict"] = "BLOCKED"
        args.output.write_text(json.dumps(record, indent=2, default=float))
        return 3

    audit = patch["sign_audit"]
    record["sign_audit"] = audit
    log(f"sign audit: {audit}")
    if audit["edges_flipped_by_curation"] != 0:
        log("BLOCKED: run-time sign audit disagrees with the curated "
            "I6 table -- instrument fault")
        record["verdict"] = "BLOCKED"
        args.output.write_text(json.dumps(record, indent=2, default=float))
        return 3

    params = load_trained_params()
    gate_b = run_gate_b_fc25(patch, params, score_idx, score_types, handle)
    record["gate_b_fc25_reference"] = gate_b
    log(f"gate B fc25 reference: measured {gate_b.get('measured_dsi')} "
        f"vs {FC25_REFERENCE_DSI} +/- {FC25_REFERENCE_TOL} "
        f"pass={gate_b['pass']}")
    if not gate_b["pass"]:
        log("BLOCKED: the fc25 reference does not reproduce -- "
            "continuity gate failed, nothing claimed")
        record["verdict"] = "BLOCKED"
        args.output.write_text(json.dumps(record, indent=2, default=float))
        return 3

    # AT-2 weights + calibration (held out; scoring never feeds back).
    base_W, coverage = at2_weight_matrix(patch, params, "subset")
    record["at2_coverage"] = coverage
    log(f"AT-2 coverage: {coverage['pairs_trained']}/"
        f"{coverage['pairs_total']} pairs trained, synapse mass "
        f"{coverage['synapse_mass_trained_fraction']:.4f}")
    cal = calibrate_gain(base_W, patch, params, score_idx, score_types,
                         RUN_SEED_BASE, log)
    record["calibration"] = cal
    if cal["chosen_gain"] is None:
        log("BLOCKED: no stable nonzero gain on the calibration grid "
            "(instrument statement, not a verdict)")
        record["verdict"] = "BLOCKED"
        args.output.write_text(json.dumps(record, indent=2, default=float))
        return 3
    g_star = cal["chosen_gain"]
    log(f"calibrated g* = {g_star:g} (median evoked "
        f"{cal['chosen_median_evoked_hz']:.2f} Hz, target "
        f"{CAL_TARGET_HZ:.2f})")

    from flygi.connectome.nulls import degree_preserving_rewire

    unstable = {"real": [0, 0], "null": [0, 0], "context": [0, 0]}

    def tally(arm_family: str, row: dict) -> None:
        unstable[arm_family][0] += row["unstable_runs"]
        unstable[arm_family][1] += row["runs"]

    # Variant grid, cost-honest order: real arms first; rewires only
    # at real-passing points.
    grid_report = []
    verdict = "KILL"
    passing_scales = []
    for gi, scale in enumerate(GRID_SCALES):
        W = base_W * (g_star * scale)
        log(f"[grid scale {scale}x] real arm")
        row = score_class3_arm(W, patch, params,
                               RUN_SEED_BASE + 100 * (gi + 1),
                               None, None, log)
        tally("real", row)
        entry = {"scale": scale, "gain": g_star * scale,
                 "real": row["band"],
                 "real_unstable_runs": row["unstable_runs"]}
        band = row["band"]
        log(f"  real: median DSI {band['median_dsi_pooled']:.4f} "
            f"defined {band['defined_fraction']:.2f} distinct "
            f"T4 {band['t4_distinct_preferred']} "
            f"T5 {band['t5_distinct_preferred']} pass={band['pass']}")
        if band["pass"]:
            passing_scales.append(scale)
            null_fails = []
            entry["nulls"] = []
            for s in REWIRE_SEEDS:
                rw, _ = degree_preserving_rewire(
                    patch["raw_counts"], seed=REWIRE_SEED_BASE + s)
                Wn, cov_n = at2_weight_matrix(
                    {"raw_counts": rw, "types": types}, params, "subset")
                nrow = score_class3_arm(
                    Wn * (g_star * scale), patch, params,
                    RUN_SEED_BASE + 100 * (gi + 1) + 10 + s, None, None,
                    log)
                tally("null", nrow)
                nband = nrow["band"]
                null_fails.append(not nband["pass"])
                entry["nulls"].append(
                    {"seed": REWIRE_SEED_BASE + s, "band": nband,
                     "coverage": cov_n,
                     "unstable_runs": nrow["unstable_runs"]})
                log(f"  null{s}: median DSI "
                    f"{nband['median_dsi_pooled']:.4f} "
                    f"pass={nband['pass']}")
            if all(null_fails):
                verdict = "PASS"
                entry["decisive"] = True
        grid_report.append(entry)
    record["grid"] = grid_report

    # Context, non-decisional: uniform-tau (50 ms) twin at the same
    # strengths (R6: at every real-passing point, else scale 1.0; the
    # twin equalizes BOTH membrane taus and kernel-class decays --
    # ASSUMPTION: "uniform-tau" ablates every trained time constant).
    twin_scales = passing_scales or [1.0]
    twins = []
    for scale in twin_scales:
        log(f"[twin uniform-tau 50 ms, scale {scale}x]")
        row = score_class3_arm(base_W * (g_star * scale), patch, params,
                               RUN_SEED_BASE + 900, UNIFORM_TAU_MS,
                               UNIFORM_TAU_MS, log)
        tally("context", row)
        twins.append({"scale": scale, "band": row["band"],
                      "unstable_runs": row["unstable_runs"]})
        log(f"  twin: median DSI "
            f"{row['band']['median_dsi_pooled']:.4f}")
    record["uniform_tau_twin"] = twins

    # Context, non-decisional: the Shiu secondary conversion.
    log("[Shiu uniform-conversion context arm]")
    W_shiu = shiu_weight_matrix(patch)
    row = score_class3_arm(W_shiu, patch, params, RUN_SEED_BASE + 950,
                           None, None, log)
    tally("context", row)
    record["shiu_context"] = {
        "mv_per_synapse": SHIU_MV_PER_SYNAPSE,
        "unitary_psp_mv": unitary_psp_mv(),
        "band": row["band"], "unstable_runs": row["unstable_runs"]}
    log(f"  shiu: median DSI {row['band']['median_dsi_pooled']:.4f}")

    fractions = {k: (u[0] / u[1] if u[1] else 0.0)
                 for k, u in unstable.items()}
    record["unstable_fractions"] = fractions
    worst = max(fractions.values())
    if worst > MAX_UNSTABLE_FRACTION:
        log(f"BLOCKED: non-finite membrane in {worst:.0%} of runs "
            f"(floor {MAX_UNSTABLE_FRACTION:.0%})")
        record["verdict"] = "BLOCKED"
        args.output.write_text(json.dumps(record, indent=2, default=float))
        return 3

    record["verdict"] = verdict
    record["elapsed_s"] = round(time.time() - started, 1)
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(f"VERDICT: {verdict} (scope AT-1: spiking model class under "
        f"the AT-2 mapping)")
    handle.close()
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
