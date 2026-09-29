#!/usr/bin/env python3
"""FIDELITY CLASS 2 -- BENCHMARK V1 RERUN: T4/T5 direction selectivity.

Class-1 result this reruns (results/benchmarks/visual_motion.json, commit
lineage 25410a5..98c0d78): the frozen uniform tanh rate model FAILED V1 at
all 21 operating points (best pooled median DSI 0.288 at gain 0.8 / leak
0.1, zero pass points). Class 2 changes the MODEL ONLY: per-type temporal
dynamics (graded leaky integrators, flyvision model form) on an anatomical
spatial patch of the right optic lobe with signed raw MaleCNS synapse
counts. THE BAND DOES NOT CHANGE.

===========================================================================
PREREGISTERED PASS BAND -- verbatim from class-1 scripts/benchmarks/
visual_motion.py (BENCHMARK V1), fixed before any class-2 dynamics ran:

  CITATION: Maisak, M.S., Haag, J., Ammer, G., et al. "A directional
  tuning map of Drosophila elementary motion detectors." Nature 500,
  212-216 (2013).

  "PASS iff pooled per-cell median DSI >= 0.3 (T4 on ON bar, T5 on OFF
  bar) AND T4a-d distinct preferred directions >= 3 AND T5a-d distinct
  >= 3 AND defined-DSI fraction >= 0.5; preregistered before the sweep"

  Restated operationally for this script's 4-direction protocol:
    (a) pooled per-cell MEDIAN DSI >= 0.30 (T4 cells scored on moving ON
        edges, T5 cells on moving OFF edges; cells with
        R_pref + R_anti > 1e-9 only);
    (b) population preferred directions of T4a-d cover >= 3 distinct
        stimulus directions, and likewise T5a-d >= 3;
    (c) >= 50% of T4/T5 cells have a defined DSI.
  DSI per cell = (R_pref - R_anti) / (R_pref + R_anti), pref = argmax
  over the 4 directions of speed-pooled evoked response, anti = opposite.
===========================================================================

MODEL (docs/fidelity2/optic_lobe_temporal.md section 1, the verified
flyvision/Lappalainen 2024 form -- ESTABLISHED as the model class that
recovers T4/T5 DS from connectome wiring):

    tau_i dV_i/dt = -(V_i - Vrest_i) + g * sum_j sign_j alpha_tj->ti N_ij relu(V_j) + x_i(t)

  - ALL types graded (no spikes/threshold/reset -- doc R2: spiking
    discretization would destroy the sub-spike-interval delay code);
    relu applied to the PRESYNAPTIC state at the synapse.
  - N_ij: signed raw MaleCNS synapse counts (flygi.connectome.subcircuit),
    modulators zeroed (this extraction: zero modulatory/unsigned edges).
  - sign per presynaptic type, curated per doc section 2 (I6): Mi9 -> minus
    (Glu/GluClA), Mi4 -> minus (GABA), Mi1/Tm1/Tm2/Tm3/Tm4/Tm9/T4*/T5* ->
    plus (ACh). MEASURED MaleCNS consensus_nt agrees with every curated
    row (audited below at run time; L1 glutamate -> minus is the
    ESTABLISHED ON-pathway sign inversion and is kept as measured).
  - alpha per connected (pre-type, post-type) pair = 0.01 * mean nonzero
    synapse count of the pair (ESTABLISHED as flyvision's init per the
    doc; computed over the extracted patch, and FROZEN -- untrained --
    which is ASSUMED, doc risk R4/R3).
  - Vrest = 0.5 a.u. for every type (ESTABLISHED as flyvision's init
    mean; using it untrained and without per-type jitter is ASSUMED).
    Tonic release at rest (relu(0.5) > 0) gives Mi9/Tm9 the baseline
    drive the doc's leading-side mechanism requires; measured baselines
    are recorded per type.
  - Integration: forward Euler, dt = 2 ms (doc I2: dt <= 5 ms), tau
    clamped >= dt as flyvision does.

PER-TYPE TAU (doc section 3): fast/slow CLASS is ESTABLISHED (Arenz 2017;
Borst 2025; Behnia 2014); every specific millisecond is ASSUMED and the
load-bearing ones are SWEPT (doc I5): tau_slow in {100,150,200,300} ms
applied to Mi4/Mi9/L3 with Tm9 = (4/3)*tau_slow (doc's 200:150 ratio,
ASSUMED), crossed with fast_scale in {1.0, 2.0} on all fast types
(resulting values stay inside every doc range). Fast starts: L1/L2 15,
L4 20, L5 25, Mi1 20, Tm3 12, Tm1 20, Tm2 12, Tm4 20, T4a-d 20,
T5a-d 20 ms.

SUBCIRCUIT (spatial patch, doc I7): right optic lobe (chosen because the
right side carries complete assignedOlHex coverage for L3 and Tm4).
Types L1-L5, Mi1, Mi4, Mi9, Tm1, Tm2, Tm3, Tm4, Tm9 over a 13x13 hex
window centered on the right-eye Mi1 median column (19,20); T4a-d/T5a-d
scored over the inner 9x9 so every scored cell keeps a >= 2-column ring
of intact input. Columns: assignedOlHex1/2 from the raw annotations
feather where assigned; Tm3, L4 and T4/T5 carry no hex assignment, so
their column is the |W|-weighted centroid of their hex-assigned synaptic
partners (METHOD VALIDATED before this run: on hex-assigned cells the
same estimator reproduces the true column with median error 0.06
columns, 90th pct 0.30 -- measured, prototype 2026-09-29).
CT1 IS EXCLUDED (declared): in MaleCNS it is 2 point cells, one per
hemisphere; unsplit it sums the whole visual field and kills local
trailing inhibition (doc R1/I4). Consequence stated up front: T4 keeps
its Mi4 trailing inhibition; T5 loses CT1(Lo1) trailing inhibition and
must get DS from the slow-Tm9-leading / fast-center asymmetry alone.
C2/C3/TmY15 are likewise outside the task's type list (recorded).

STIMULUS (retinotopic, doc I7): hex axial coords embedded in the plane
with basis e1=(1,0), e2=(1/2, sqrt(3)/2) (unit column spacing; the
embedding's rotation vs the fly's visual axes is ASSUMED unknown --
exactly why the band asks for >= 3 DISTINCT preferred directions, not
their identity; same assumption as class-1). Moving ON edge (dark
background -> bright half-plane) and OFF edge (bright -> dark) sweep the
patch in 4 directions (+x,-x,+y,-y) at speeds {2.5, 5, 10} columns/s
(at ~5 deg inter-ommatidial angle: 12.5-50 deg/s, bracketing the ~1 Hz
optimum; ASSUMED mapping). Photoreceptors are not in the graph, so
luminance drives L1/L2/L3 with NEGATIVE sign, x = -1.0 * L(column, t)
(the histaminergic R1-6 -> lamina inversion, ESTABLISHED sign,
ASSUMED magnitude 1.0 a.u.). Every direction uses the same traverse
length (max patch extent + 2 margins) so sweep durations are identical
across directions at a given speed. Background is settled 2.5 s once
per (config, polarity) and the settled state is reused for each sweep.

CALIBRATION (declared; doc R3): ONE global scalar gain g per model
configuration (including the trivial control), chosen on a HELD-OUT
stimulus -- an edge moving along the +45 degree DIAGONAL (a direction
that is not among the four scored cardinals) at 5 columns/s, run in
both polarities -- as the g in a fixed log grid whose median peak
evoked output over {T4 cells under the ON edge} u {T5 cells under the
OFF edge} (the same population matching the scoring uses) is closest
to 0.5 a.u. (the resting-release scale; target ASSUMED), subject to
stability (max |V| <= 1e3, finite). Nothing else is fitted. Scoring
runs never feed back into g.

TRIVIAL ALTERNATIVE (mandatory, named in advance): the IDENTICAL run --
same patch, same signs, same alpha, same Vrest, same calibration
procedure -- with ONE UNIFORM tau (50 ms, flyvision's init) for every
type. Class-1 measured that a temporally uniform model has no DS;
attribution of any class-2 pass to per-type temporal heterogeneity
requires heterogeneous-tau DSI >> uniform-tau DSI (which must stay
near 0). ">>" is operationalized IN ADVANCE as: best heterogeneous
pooled median DSI >= 2x the uniform-tau value AND the absolute margin
>= 0.10.

READOUT -- INSTRUMENT HISTORY (band unchanged throughout):
  v1 (whole-sweep integral), as first preregistered: evoked =
  max(output - settled baseline, 0) integrated over the ENTIRE sweep.
  MEASURED RESULT of the full v1 run (2026-09-29, archived in this
  file's first committed JSON): all 8 heterogeneous configs fail
  (pooled median DSI 0.104-0.107, distinct directions 2/2) AND the
  uniform-tau control scores 0.1072 -- as high as every heterogeneous
  config. The uniform control therefore ESTABLISHED (measured) that
  the v1 statistic is tau-independent: it is not the temporal
  correlator. Mechanical cause, measured by a trace probe (tau_slow
  150, gain 0.03, +x ON sweep, 5 col/s, 2 s tail): a moving edge is a
  permanent luminance step per column, the graded integrator's DC
  gain is 1 at every tau, and a MEDIAN 84.6% (10th pct 81.6, 90th pct
  86.9) of each cell's whole-sweep evoked integral is standing
  post-transient DC (>0.75 s after that cell's own edge crossing).
  The direction-selective transient is ~5:1 swamped by a
  tau-independent offset: a readout artifact, the readout-side twin
  of the class-1 scrambled-input lesson.
  v2 (crossing-locked window), adopted BEFORE any v2 number was seen:
  same dynamics, same sweeps, same band, same calibration; evoked is
  integrated only inside the per-cell stimulus-locked window from
  (edge front 2.0 columns before the cell's position) to (0.75 s
  after the front passes the cell) -- window sizes ASSUMED, and
  direction-symmetric BY CONSTRUCTION because they are defined
  relative to each cell's own crossing time. Both readouts are scored
  and saved from the same simulations; v2 is the corrected
  instrument, v1 is retained as the recorded artifact.

TIER DISCIPLINE: every number this script prints or saves is Measured
under this protocol. The only Expected claim, stated with its base
rate: this repo's expected-to-help changes are 0 for 11; whether the
frozen-parameter flyvision recipe passes on MaleCNS counts is open
until this runs.

Run:  python scripts/benchmarks/fc2_visual_ds.py
Output: results/benchmarks/fc2_visual_ds.json (saved after every config)
        results/benchmarks/fc2_visual_ds.log (console mirror)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
ANNOTATIONS = ROOT / "data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather"

# --- preregistered band (class-1 V1, verbatim constants) -------------------
BAND_MEDIAN_DSI = 0.30
BAND_DISTINCT_DIRECTIONS = 3
BAND_DEFINED_FRACTION = 0.50
BAND_TEXT = (
    "PASS iff pooled per-cell median DSI >= 0.3 (T4 on ON bar, T5 on OFF bar) "
    "AND T4a-d distinct preferred directions >= 3 AND T5a-d distinct >= 3 AND "
    "defined-DSI fraction >= 0.5; preregistered before the sweep"
)
CITATION = "Maisak et al. 2013, Nature 500:212-216"

# --- patch / protocol constants (fixed before any dynamics ran) ------------
INPUT_TYPES = ("L1", "L2", "L3", "L4", "L5", "Mi1", "Mi4", "Mi9",
               "Tm1", "Tm2", "Tm3", "Tm4", "Tm9")
T4_SUBTYPES = ("T4a", "T4b", "T4c", "T4d")
T5_SUBTYPES = ("T5a", "T5b", "T5c", "T5d")
ALL_TYPES = INPUT_TYPES + T4_SUBTYPES + T5_SUBTYPES
PATCH_CENTER = (19.0, 20.0)   # right-eye Mi1 median hex column (measured)
INPUT_HALF = 6                # 13x13 input window
SCORE_HALF = 4                # 9x9 scored T4/T5 window
DRIVEN_TYPES = ("L1", "L2", "L3")   # direct photoreceptor targets
INPUT_DRIVE = -1.0            # histaminergic sign (ESTABLISHED -, ASSUMED |1.0|)

DT_MS = 2.0
SETTLE_MS = 2500.0
TAIL_MS = 800.0               # >= WINDOW_AFTER_S for the last-crossed cells
EDGE_MARGIN = 1.0             # columns beyond patch extent, both sides
WINDOW_BEFORE_COL = 2.0       # v2 window opens: front 2 columns before cell
WINDOW_AFTER_S = 0.75         # v2 window closes: 0.75 s after front passes
SPEEDS = (2.5, 5.0, 10.0)     # columns / s
DIRECTIONS = ("+x", "-x", "+y", "-y")
OPPOSITE = {"+x": "-x", "-x": "+x", "+y": "-y", "-y": "+y"}
DIR_VECTORS = {"+x": (1.0, 0.0), "-x": (-1.0, 0.0),
               "+y": (0.0, 1.0), "-y": (0.0, -1.0)}
CAL_DIRECTION = (2 ** -0.5, 2 ** -0.5)   # +45 deg diagonal, held out
CAL_SPEED = 5.0
CAL_TARGET_PEAK = 0.5
GAIN_GRID = (1e-5, 3e-5, 1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1, 3e-1)
V_ABORT = 1e3
V_REST = 0.5
ALPHA_SCALE = 0.01

# Curated presynaptic signs (doc section 2 / I6). L1-L5 keep measured
# MaleCNS signs (the doc curates no lamina rows); audited at run time.
CURATED_SIGNS = {
    "Mi1": +1, "Tm1": +1, "Tm2": +1, "Tm3": +1, "Tm4": +1, "Tm9": +1,
    "T4a": +1, "T4b": +1, "T4c": +1, "T4d": +1,
    "T5a": +1, "T5b": +1, "T5c": +1, "T5d": +1,
    "Mi4": -1, "Mi9": -1,
}

# Per-type tau table (doc section 3). Class labels: ESTABLISHED; every
# millisecond value: ASSUMED (ranges in the doc; swept axes marked).
FAST_TAUS = {"L1": 15.0, "L2": 15.0, "L4": 20.0, "L5": 25.0, "Mi1": 20.0,
             "Tm3": 12.0, "Tm1": 20.0, "Tm2": 12.0, "Tm4": 20.0,
             "T4a": 20.0, "T4b": 20.0, "T4c": 20.0, "T4d": 20.0,
             "T5a": 20.0, "T5b": 20.0, "T5c": 20.0, "T5d": 20.0}
SLOW_TYPES = ("L3", "Mi4", "Mi9")   # get tau_slow; Tm9 gets (4/3)*tau_slow
TAU_SLOW_SWEEP = (100.0, 150.0, 200.0, 300.0)   # ASSUMED, swept (doc I5)
FAST_SCALE_SWEEP = (1.0, 2.0)                    # ASSUMED, swept
UNIFORM_TAU = 50.0            # trivial alternative: flyvision init for all


def log_print(handle, message: str) -> None:
    print(message, flush=True)
    handle.write(message + "\n")
    handle.flush()


def build_patch() -> dict[str, Any]:
    """Extract the right-eye subcircuit, assign columns, cut the patch."""

    import numpy as np
    import pyarrow.feather as feather
    from scipy import sparse

    from flygi.connectome.subcircuit import extract_subcircuit

    with np.load(RUNTIME_DIR / "node_metadata.npz", allow_pickle=False) as z:
        types_all = z["type"].astype("U")
        inst_all = z["instance"].astype("U")
    mask = np.isin(types_all, ALL_TYPES) & np.char.endswith(inst_all, "_R")
    dense = np.flatnonzero(mask).astype(np.int64)
    sub = extract_subcircuit(RUNTIME_DIR, dense)
    types = sub.types.astype("U")
    n = types.shape[0]

    table = feather.read_table(
        ANNOTATIONS, columns=["bodyId", "assignedOlHex1", "assignedOlHex2"]
    ).to_pandas().dropna(subset=["assignedOlHex1"])
    hexmap = {
        int(b): (float(a), float(c))
        for b, a, c in zip(
            table["bodyId"], table["assignedOlHex1"], table["assignedOlHex2"]
        )
    }
    h1 = np.full(n, np.nan)
    h2 = np.full(n, np.nan)
    for i, body in enumerate(sub.body_ids):
        got = hexmap.get(int(body))
        if got is not None:
            h1[i], h2[i] = got
    assigned = ~np.isnan(h1)

    # Column for unassigned cells (Tm3, L4, T4/T5): |W|-weighted centroid of
    # hex-assigned partners, in+out. METHOD ASSUMED; validated against
    # ground-truth assignments (median error 0.06 columns, header).
    absolute = abs(sub.matrix) + abs(sub.matrix).T
    weight_sum = absolute @ assigned.astype(np.float64)
    est1 = np.where(assigned, h1,
                    (absolute @ np.where(assigned, h1, 0.0))
                    / np.maximum(weight_sum, 1e-12))
    est2 = np.where(assigned, h2,
                    (absolute @ np.where(assigned, h2, 0.0))
                    / np.maximum(weight_sum, 1e-12))
    est1 = np.where(np.isnan(est1) | (weight_sum <= 0), np.nan, est1)
    est2 = np.where(np.isnan(est2) | (weight_sum <= 0), np.nan, est2)

    c1, c2 = PATCH_CENTER
    in_input = (
        (np.abs(est1 - c1) <= INPUT_HALF) & (np.abs(est2 - c2) <= INPUT_HALF)
        & np.isin(types, INPUT_TYPES) & ~np.isnan(est1)
    )
    in_score = (
        (np.abs(est1 - c1) <= SCORE_HALF) & (np.abs(est2 - c2) <= SCORE_HALF)
        & np.isin(types, T4_SUBTYPES + T5_SUBTYPES) & ~np.isnan(est1)
    )
    keep = np.flatnonzero(in_input | in_score)
    matrix = sparse.csr_matrix(sub.matrix[np.ix_(keep, keep)])
    patch_types = types[keep]
    patch_h1 = est1[keep]
    patch_h2 = est2[keep]

    # Sign audit (doc I6): measured builder signs vs curated table.
    coo = matrix.tocoo()
    pre_types = patch_types[coo.col]
    measured_sign = np.sign(coo.data)
    curated = np.array([CURATED_SIGNS.get(t, 0) for t in pre_types])
    have_curated = curated != 0
    flipped = int(np.sum(have_curated & (measured_sign != curated)))
    signs_forced = np.where(have_curated, curated, measured_sign)
    counts = np.abs(coo.data)

    # alpha per connected (pre-type, post-type) pair = 0.01 * mean count.
    type_names = sorted(set(patch_types.tolist()))
    code_of = {t: i for i, t in enumerate(type_names)}
    pre_code = np.array([code_of[t] for t in pre_types])
    post_code = np.array([code_of[t] for t in patch_types[coo.row]])
    pair = pre_code * len(type_names) + post_code
    pair_sum = np.zeros(len(type_names) ** 2)
    pair_n = np.zeros(len(type_names) ** 2)
    np.add.at(pair_sum, pair, counts)
    np.add.at(pair_n, pair, 1.0)
    alpha = ALPHA_SCALE * pair_sum[pair] / np.maximum(pair_n[pair], 1.0)
    weighted = sparse.csr_matrix(
        (signs_forced * alpha * counts, (coo.row, coo.col)),
        shape=matrix.shape,
    )

    # Embed hex axial coords in the plane (unit column spacing; ASSUMED
    # rotation vs the fly's visual axes -- see header).
    x = patch_h1 + 0.5 * patch_h2
    y = (3 ** 0.5 / 2.0) * patch_h2

    per_type = {t: int((patch_types == t).sum()) for t in ALL_TYPES}
    return {
        "matrix": weighted,
        "raw_counts": matrix,
        "types": patch_types,
        "x": x,
        "y": y,
        "node_count": int(keep.size),
        "nnz": int(weighted.nnz),
        "per_type": per_type,
        "sign_audit": {
            "curated_edges": int(have_curated.sum()),
            "edges_flipped_by_curation": flipped,
            "note": "0 expected: measured MaleCNS consensus NT agrees with "
                    "the curated table for every patch type",
        },
        "dropped_modulatory_edges": int(sub.dropped_modulatory_edges),
        "unsigned_edges": int(sub.unsigned_edges),
    }


class GradedFlyvisNetwork:
    """The doc section-1 graded dynamics on the patch (subclass-free
    reimplementation would hide provenance -- so this wraps the engine's
    ParameterTable for per-type resolution but overrides the update to the
    verified flyvision form: instantaneous rectified graded release,
    stimulus inside the leak, no spikes anywhere)."""

    def __init__(self, matrix, types, table, *, dt_ms: float, gain: float):
        import numpy as np
        from scipy import sparse

        self.matrix = sparse.csr_matrix(matrix, dtype=np.float64)
        self.dt = float(dt_ms)
        self.gain = float(gain)
        params = table.resolve(types)
        # tau clamped >= dt exactly as flyvision does (verified in doc).
        self.tau = np.maximum(params["tau_m_ms"].astype(np.float64), self.dt)
        self.v_rest = params["v_rest"].astype(np.float64)
        if not bool(params["graded"].all()):
            raise RuntimeError("class-2 DS model must be all-graded (doc R2)")
        self.v = self.v_rest.copy()

    def reset(self) -> None:
        self.v = self.v_rest.copy()

    def state(self):
        return self.v.copy()

    def set_state(self, v) -> None:
        self.v = v.copy()

    def output(self):
        import numpy as np
        return np.maximum(self.v, 0.0)

    def step(self, external) -> None:
        import numpy as np
        release = np.maximum(self.v, 0.0)
        drive = self.gain * (self.matrix @ release)
        self.v = self.v + (self.dt / self.tau) * (
            -(self.v - self.v_rest) + drive + external
        )


def make_table(tau_slow: float, fast_scale: float, uniform: float | None):
    """ParameterTable with per-type provenance (engine's resolver)."""

    from flygi.dynamics.spiking import ParameterTable, TypeParams

    def graded(tau: float, provenance: str) -> TypeParams:
        return TypeParams(
            tau_m_ms=tau, v_thresh=1e9, provenance=provenance,
            v_rest=V_REST, graded=True, graded_gain=1.0,
        )

    if uniform is not None:
        prov = ("TRIVIAL CONTROL: uniform tau %.0f ms for every type "
                "(flyvision init); heterogeneity ablated" % uniform)
        return ParameterTable(default=graded(uniform, prov), rules=[])

    rules = []
    for t in SLOW_TYPES:
        rules.append((t, graded(
            tau_slow,
            f"{t}: slow class ESTABLISHED (Arenz 2017; Borst 2025); "
            f"tau {tau_slow:.0f} ms ASSUMED, swept 100-300")))
    rules.append(("Tm9", graded(
        tau_slow * 4.0 / 3.0,
        "Tm9: slow class ESTABLISHED; tau = (4/3)*tau_slow ASSUMED "
        "(doc 200:150 ratio), swept")))
    for t, tau in FAST_TAUS.items():
        rules.append((t, graded(
            tau * fast_scale,
            f"{t}: fast class ESTABLISHED (Behnia 2014 anchors; Arenz "
            f"2017); tau {tau * fast_scale:.0f} ms ASSUMED, fast_scale "
            f"swept 1-2 within doc ranges")))
    return ParameterTable(
        default=graded(50.0, "unmatched type: flyvision init 50 ms (ASSUMED)"),
        rules=rules,
    )


def run_sweep(net, patch, polarity: str, direction_vec, speed: float,
              settled_state, score_idx):
    """One moving-edge sweep from a settled state.

    Returns (peak_evoked, sum_v1, sum_v2, stable) for the scored cells:
    evoked = max(output - settled_output, 0); v1 accumulates it * dt over
    the whole sweep (the recorded artifact readout), v2 only inside the
    per-cell crossing-locked window (the corrected readout, header).
    """

    import numpy as np

    x, y = patch["x"], patch["y"]
    dx, dy = direction_vec
    proj = x * dx + y * dy
    # Same traverse length for every direction at a given speed (header).
    extent = float(
        max(np.ptp(x), np.ptp(y), np.ptp(x * (2 ** -0.5) + y * (2 ** -0.5)))
    )
    lo = float(proj.min())
    front0 = lo - EDGE_MARGIN
    travel = extent + 2 * EDGE_MARGIN
    steps = int(round((travel / speed * 1000.0 + TAIL_MS) / DT_MS))

    driven = patch["driven_mask"]
    driven_proj = proj[driven]
    drive = np.zeros(net.v.shape[0])

    net.set_state(settled_state)
    base_out = net.output()[score_idx]
    crossing_s = (proj[score_idx] - front0) / speed
    window_open = crossing_s - WINDOW_BEFORE_COL / speed
    window_close = crossing_s + WINDOW_AFTER_S
    peak = np.zeros(score_idx.size)
    total_v1 = np.zeros(score_idx.size)
    total_v2 = np.zeros(score_idx.size)
    stable = True
    for k in range(steps):
        t = k * DT_MS / 1000.0
        front = front0 + speed * t
        behind = driven_proj <= front
        if polarity == "on":
            luminance = np.where(behind, 1.0, 0.0)
        else:
            luminance = np.where(behind, 0.0, 1.0)
        drive[driven] = INPUT_DRIVE * luminance
        net.step(drive)
        if k % 50 == 0 and not np.all(np.isfinite(net.v)):
            stable = False
            break
        if k % 50 == 0 and np.max(np.abs(net.v)) > V_ABORT:
            stable = False
            break
        evoked = np.maximum(net.output()[score_idx] - base_out, 0.0)
        np.maximum(peak, evoked, out=peak)
        step_mass = evoked * (DT_MS / 1000.0)
        total_v1 += step_mass
        in_window = (t >= window_open) & (t <= window_close)
        total_v2 += np.where(in_window, step_mass, 0.0)
    if not np.all(np.isfinite(net.v)) or np.max(np.abs(net.v)) > V_ABORT:
        stable = False
    return peak, total_v1, total_v2, stable


def settle(net, patch, polarity: str):
    import numpy as np
    drive = np.zeros(net.v.shape[0])
    if polarity == "off":   # bright background before an OFF edge
        drive[patch["driven_mask"]] = INPUT_DRIVE * 1.0
    net.reset()
    steps = int(round(SETTLE_MS / DT_MS))
    previous = net.v.copy()
    for k in range(steps):
        net.step(drive)
        if k % 100 == 0 and (
            not np.all(np.isfinite(net.v)) or np.max(np.abs(net.v)) > V_ABORT
        ):
            return None, float("nan")
        if k == steps - 2:
            previous = net.v.copy()
    residual = float(np.max(np.abs(net.v - previous)))
    return net.state(), residual


import numpy as np  # noqa: E402  (used by helpers above via closures)


def calibrate(patch, table, score_idx, score_types, handle) -> dict[str, Any]:
    """Declared gain calibration on the held-out diagonal sweep (both
    polarities; metric matches the scoring's population split)."""

    is_t4 = np.array([t.startswith("T4") for t in score_types])
    curve = []
    best = None
    for g in GAIN_GRID:
        net = GradedFlyvisNetwork(
            patch["matrix"], patch["types"], table, dt_ms=DT_MS, gain=g
        )
        peaks = []
        stable = True
        for pol, member_mask in (("on", is_t4), ("off", ~is_t4)):
            settled, residual = settle(net, patch, pol)
            if settled is None:
                stable = False
                break
            peak, _, _, ok = run_sweep(
                net, patch, pol, CAL_DIRECTION, CAL_SPEED,
                settled, score_idx,
            )
            stable &= ok
            peaks.append(peak[member_mask])
        if not stable or not peaks:
            curve.append({"gain": g, "stable": False})
            continue
        med = float(np.median(np.concatenate(peaks)))
        curve.append({"gain": g, "stable": True, "median_peak_evoked": med})
        if med > 1e-12:
            loss = abs(np.log10(med / CAL_TARGET_PEAK))
            if best is None or loss < best[0]:
                best = (loss, g, med)
    chosen = best[1] if best is not None else None
    log_print(handle, f"  calibration: chosen gain {chosen} "
                      f"(median peak {best[2]:.4f})" if best else
                      "  calibration: NO stable nonzero gain")
    return {"curve": curve, "chosen_gain": chosen,
            "target_median_peak": CAL_TARGET_PEAK,
            "held_out_stimulus": "edge along +45deg diagonal, 5 col/s, both "
                                 "polarities (direction not among the 4 "
                                 "scored); metric = median peak evoked over "
                                 "T4-on-ON u T5-on-OFF"}


def band_metrics(responses, per_speed, score_types, is_t4):
    """The preregistered band evaluated on one readout's responses."""

    scored = np.where(is_t4[None, :], responses["on"], responses["off"])
    pref = np.argmax(scored, axis=0)
    anti = np.array([DIRECTIONS.index(OPPOSITE[DIRECTIONS[p]]) for p in pref])
    cells = np.arange(scored.shape[1])
    r_pref, r_anti = scored[pref, cells], scored[anti, cells]
    denom = r_pref + r_anti
    defined = denom > 1e-9
    dsi = np.full(cells.size, np.nan)
    dsi[defined] = (r_pref[defined] - r_anti[defined]) / denom[defined]

    per_subtype = {}
    for name in T4_SUBTYPES + T5_SUBTYPES:
        members = score_types == name
        pol = "on" if name.startswith("T4") else "off"
        sums = responses[pol][:, members].sum(axis=1)
        p = int(np.argmax(sums))
        a = DIRECTIONS.index(OPPOSITE[DIRECTIONS[p]])
        d = float(sums[p] + sums[a])
        per_subtype[name] = {
            "cells": int(members.sum()),
            "preferred": DIRECTIONS[p],
            "subtype_dsi": float((sums[p] - sums[a]) / d) if d > 1e-9
                           else float("nan"),
            "direction_totals": {n: float(s) for n, s in zip(DIRECTIONS, sums)},
        }
    t4_distinct = len({per_subtype[n]["preferred"] for n in T4_SUBTYPES})
    t5_distinct = len({per_subtype[n]["preferred"] for n in T5_SUBTYPES})
    defined_fraction = float(defined.mean())
    median_pooled = float(np.median(dsi[defined])) if defined.any() else float("nan")

    per_speed_median = {}
    for si, speed in enumerate(SPEEDS):
        sp = np.where(is_t4[None, :], per_speed["on"][si], per_speed["off"][si])
        sp_pref, sp_anti = sp[pref, cells], sp[anti, cells]
        sp_den = sp_pref + sp_anti
        ok = sp_den > 1e-9
        per_speed_median[str(speed)] = (
            float(np.median((sp_pref[ok] - sp_anti[ok]) / sp_den[ok]))
            if ok.any() else float("nan")
        )

    passed = bool(
        defined.any()
        and median_pooled >= BAND_MEDIAN_DSI
        and t4_distinct >= BAND_DISTINCT_DIRECTIONS
        and t5_distinct >= BAND_DISTINCT_DIRECTIONS
        and defined_fraction >= BAND_DEFINED_FRACTION
    )
    t4_defined = defined & is_t4
    t5_defined = defined & ~is_t4
    return {
        "median_dsi_pooled": median_pooled,
        "median_dsi_t4_on": float(np.median(dsi[t4_defined]))
                            if t4_defined.any() else float("nan"),
        "median_dsi_t5_off": float(np.median(dsi[t5_defined]))
                             if t5_defined.any() else float("nan"),
        "defined_fraction": defined_fraction,
        "t4_distinct_preferred": t4_distinct,
        "t5_distinct_preferred": t5_distinct,
        "per_subtype": per_subtype,
        "per_speed_median_dsi": per_speed_median,
        "pass": passed,
    }


def score_config(patch, table, gain, score_idx, score_types, handle):
    """The preregistered 4-direction measurement at a fixed gain, scored
    under both readouts (v2 = corrected instrument, v1 = recorded
    artifact; header READOUT section)."""

    is_t4 = np.array([t.startswith("T4") for t in score_types])
    shape = (len(DIRECTIONS), score_idx.size)
    speed_shape = (len(SPEEDS),) + shape
    acc = {
        "v1": {pol: np.zeros(shape) for pol in ("on", "off")},
        "v2": {pol: np.zeros(shape) for pol in ("on", "off")},
    }
    acc_speed = {
        "v1": {pol: np.zeros(speed_shape) for pol in ("on", "off")},
        "v2": {pol: np.zeros(speed_shape) for pol in ("on", "off")},
    }
    baselines = {}
    all_stable = True
    for pol in ("on", "off"):
        net = GradedFlyvisNetwork(
            patch["matrix"], patch["types"], table, dt_ms=DT_MS, gain=gain
        )
        settled, residual = settle(net, patch, pol)
        if settled is None:
            return None
        base = np.maximum(settled, 0.0)
        baselines[pol] = {
            t: float(np.mean(base[patch["types"] == t]))
            for t in ALL_TYPES if (patch["types"] == t).any()
        }
        baselines[pol]["settle_residual"] = residual
        for si, speed in enumerate(SPEEDS):
            for di, dname in enumerate(DIRECTIONS):
                _, total_v1, total_v2, stable = run_sweep(
                    net, patch, pol, DIR_VECTORS[dname], speed,
                    settled, score_idx,
                )
                all_stable &= stable
                acc["v1"][pol][di] += total_v1
                acc["v2"][pol][di] += total_v2
                acc_speed["v1"][pol][si, di] = total_v1
                acc_speed["v2"][pol][si, di] = total_v2

    result: dict[str, Any] = {
        "baseline_mean_output": baselines,
        "all_sweeps_stable": bool(all_stable),
    }
    for readout, key in (("v2", "readout_v2_crossing_window"),
                         ("v1", "readout_v1_wholesweep")):
        result[key] = band_metrics(
            acc[readout], acc_speed[readout], score_types, is_t4
        )
    primary = result["readout_v2_crossing_window"]
    result["pass"] = primary["pass"]
    result["median_dsi_pooled"] = primary["median_dsi_pooled"]
    v1 = result["readout_v1_wholesweep"]
    log_print(handle,
              f"  scored v2(window): median DSI "
              f"{primary['median_dsi_pooled']:.4f} "
              f"(T4 {primary['median_dsi_t4_on']:.4f} / "
              f"T5 {primary['median_dsi_t5_off']:.4f}), defined "
              f"{primary['defined_fraction']:.2f}, distinct "
              f"T4 {primary['t4_distinct_preferred']} "
              f"T5 {primary['t5_distinct_preferred']}, stable "
              f"{all_stable} -> pass={primary['pass']} | v1(wholesweep) "
              f"median {v1['median_dsi_pooled']:.4f} pass={v1['pass']}")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="FC2 T4/T5 DS benchmark")
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "results" / "benchmarks" / "fc2_visual_ds.json",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    log_path = args.output.with_suffix(".log")
    handle = open(log_path, "w")

    started = time.time()
    patch = build_patch()
    types = patch["types"]
    patch["driven_mask"] = np.isin(types, DRIVEN_TYPES)
    score_mask = np.isin(types, T4_SUBTYPES + T5_SUBTYPES)
    score_idx = np.flatnonzero(score_mask)
    score_types = types[score_idx]
    log_print(handle,
              f"patch: {patch['node_count']} cells, {patch['nnz']} signed "
              f"edges, {int(score_idx.size)} scored T4/T5 cells, built in "
              f"{time.time() - started:.1f}s")
    log_print(handle, f"sign audit: {patch['sign_audit']}")

    report: dict[str, Any] = {
        "benchmark": "FC2 V1 rerun -- T4/T5 direction selectivity, class-2 "
                     "graded per-type temporal dynamics on a right-eye patch",
        "band": BAND_TEXT,
        "citation": CITATION,
        "class1_result": "FAILED at all 21 operating points (best pooled "
                         "median DSI 0.288 at gain 0.8/leak 0.1); "
                         "results/benchmarks/visual_motion.json",
        "model": "graded leaky integrator, flyvision form (doc section 1); "
                 "signed raw MaleCNS counts; alpha=0.01*mean pair count; "
                 "Vrest=0.5; relu at synapse; forward Euler dt=2ms",
        "ct1": "EXCLUDED (2 point cells in MaleCNS; unsplit CT1 sums the "
               "visual field, doc R1/I4). T5 therefore has no CT1(Lo1) "
               "trailing inhibition; its DS must come from slow-Tm9 "
               "leading excitation vs fast center.",
        "patch": {k: patch[k] for k in
                  ("node_count", "nnz", "per_type", "sign_audit",
                   "dropped_modulatory_edges", "unsigned_edges")},
        "patch_geometry": {
            "center_hex": PATCH_CENTER, "input_half": INPUT_HALF,
            "score_half": SCORE_HALF,
            "column_source": "assignedOlHex1/2 (raw annotations feather); "
                             "Tm3/L4/T4/T5 by connectivity centroid "
                             "(validated: median err 0.06 col)",
        },
        "stimulus": {
            "speeds_col_per_s": SPEEDS, "directions": DIRECTIONS,
            "dt_ms": DT_MS, "settle_ms": SETTLE_MS, "tail_ms": TAIL_MS,
            "drive": "luminance -> L1/L2/L3 with sign -1 (histamine)",
        },
        "calibration_declared": (
            "one global gain per configuration, chosen on a held-out edge "
            "moving along the +45deg diagonal (not among the 4 scored "
            "directions) at 5 col/s in both polarities; log-grid argmin "
            "|log(median peak evoked over T4-on-ON u T5-on-OFF / 0.5)| "
            "subject to stability; scored on the 4 cardinal directions x "
            "2 polarities x 3 speeds"
        ),
        "expected_tier_note": "repo base rate for expected-to-help changes "
                              "is 0/11; pass/fail here is open until run",
        "readout_instrument_history": {
            "v1_wholesweep": (
                "first preregistered readout: evoked integrated over the "
                "whole sweep. MEASURED artifact (run 1, 2026-09-29): all 8 "
                "heterogeneous configs 0.104-0.107 median DSI AND uniform-"
                "tau control 0.1072 -- statistic is tau-independent, not "
                "the correlator. Trace probe measured median 84.6% of the "
                "evoked integral is standing post-transient DC (edge = "
                "permanent luminance step; DC gain is 1 at every tau)."
            ),
            "v2_crossing_window": (
                "corrected instrument, adopted before any v2 number was "
                "seen: evoked integrated only in the per-cell stimulus-"
                "locked window [front 2 columns before cell, 0.75 s after "
                "front passes cell] (sizes ASSUMED); direction-symmetric "
                "by construction. Band and calibration unchanged. Both "
                "readouts scored from the same simulations."
            ),
        },
        "configs": [],
        "trivial_alternative": None,
    }

    def save() -> None:
        args.output.write_text(json.dumps(report, indent=2))

    save()

    # --- heterogeneous-tau sweep (the class-2 model) -----------------------
    for tau_slow in TAU_SLOW_SWEEP:
        for fast_scale in FAST_SCALE_SWEEP:
            t0 = time.time()
            label = f"tau_slow={tau_slow:.0f}ms fast_scale={fast_scale:.1f}"
            log_print(handle, f"[config {label}]")
            table = make_table(tau_slow, fast_scale, uniform=None)
            cal = calibrate(patch, table, score_idx, score_types, handle)
            row: dict[str, Any] = {
                "tau_slow_ms": tau_slow, "fast_scale": fast_scale,
                "tm9_tau_ms": tau_slow * 4.0 / 3.0,
                "parameter_provenance": table.provenance_report(),
                "calibration": cal,
            }
            if cal["chosen_gain"] is None:
                row["result"] = None
                row["blocker"] = "no stable nonzero gain on calibration grid"
            else:
                row["result"] = score_config(
                    patch, table, cal["chosen_gain"], score_idx,
                    score_types, handle,
                )
                if row["result"] is None:
                    row["blocker"] = ("settle diverged at the calibrated "
                                      "gain during scoring")
            row["elapsed_s"] = round(time.time() - t0, 1)
            report["configs"].append(row)
            save()

    # --- trivial alternative: uniform tau, identical everything else -------
    t0 = time.time()
    log_print(handle, f"[trivial control: uniform tau {UNIFORM_TAU:.0f}ms]")
    table = make_table(0.0, 1.0, uniform=UNIFORM_TAU)
    cal = calibrate(patch, table, score_idx, score_types, handle)
    control: dict[str, Any] = {
        "uniform_tau_ms": UNIFORM_TAU,
        "calibration": cal,
    }
    if cal["chosen_gain"] is None:
        control["result"] = None
        control["blocker"] = "no stable nonzero gain on calibration grid"
    else:
        control["result"] = score_config(
            patch, table, cal["chosen_gain"], score_idx, score_types, handle
        )
        if control["result"] is None:
            control["blocker"] = ("settle diverged at the calibrated gain "
                                  "during scoring")
    control["elapsed_s"] = round(time.time() - t0, 1)
    report["trivial_alternative"] = control
    save()

    # --- summary (per readout) ---------------------------------------------
    scored = [c for c in report["configs"] if c.get("result")]
    report["summary"] = {"total_elapsed_s": round(time.time() - started, 1)}
    for key in ("readout_v2_crossing_window", "readout_v1_wholesweep"):
        best = max(
            scored, key=lambda c: c["result"][key]["median_dsi_pooled"],
            default=None,
        )
        control_dsi = (
            control["result"][key]["median_dsi_pooled"]
            if control.get("result") else float("nan")
        )
        best_dsi = best["result"][key]["median_dsi_pooled"] if best else None
        report["summary"][key] = {
            "pass_configs": [
                {"tau_slow_ms": c["tau_slow_ms"],
                 "fast_scale": c["fast_scale"]}
                for c in scored if c["result"][key]["pass"]
            ],
            "best_config": (
                {"tau_slow_ms": best["tau_slow_ms"],
                 "fast_scale": best["fast_scale"],
                 "gain": best["calibration"]["chosen_gain"]}
                if best else None
            ),
            "best_median_dsi": best_dsi,
            "trivial_uniform_tau_median_dsi": control_dsi,
            "attribution_holds": bool(
                best is not None
                and np.isfinite(control_dsi)
                and best_dsi > 2.0 * abs(control_dsi)
                and best_dsi - abs(control_dsi) > 0.10
            ) if best else False,
        }
    save()
    log_print(handle, json.dumps(report["summary"], indent=2))
    handle.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
