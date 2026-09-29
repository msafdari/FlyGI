#!/usr/bin/env python3
"""FIDELITY-CLASS-2 BENCHMARK -- EB RING MOVABLE PERSISTENT BUMP (fc2_eb_ring).

Class 1 (frozen uniform tanh rate model, scripts/benchmarks/cx_ring.py,
results/benchmarks/cx_ring.json, measured 2026-09-29) failed this benchmark at
all 21 operating points: the ring held a FIXED-POINT attractor near 222 deg
everywhere it was alive -- activity persisted but position never followed the
seed. Class 2 re-runs the SAME published-biology band on the same anatomy with
per-type temporal dynamics (current-based LIF, flygi.dynamics.spiking).
THE BAND DOES NOT CHANGE; only the model class does.

=========================== PREREGISTRATION ===========================
Registered in this header BEFORE any sweep ran. Misses are reported as
misses.

BAND (verbatim, unchanged from class-1 C1+C2, restated for spiking):
  (C1) after a transient wedge seed, a LOCALIZED bump (circular variance
  <= 0.6 over EPG positive activity) PERSISTS >= 2 simulated seconds in
  darkness with retention >= 0.05 of post-seed activity, AND the settled
  bump POSITION follows the seed (>= 4 distinguishable positions across
  seeds at 4 preregistered angles -- this is the anti-fixed-point
  criterion class 1 failed); (C2) asymmetric PEN drive rotates the bump
  with OPPOSITE signs for left vs right drive, |rate| >= 0.05
  deg/step-equivalent.
  Citations (class 1, unchanged): Seelig & Jayaraman 2015 Nature 521:186
  (bump persists in darkness); Turner-Evans 2017 eLife 6:e23496 and
  Green 2017 Nature 546:101 (opposite-signed PEN rotation). Kim et al.
  2017 Science 356:849: WINNER-TAKE-ALL ACROSS THE RING IS CORRECT
  PHYSIOLOGY -- not penalized; the failure mode under test is
  position-INDEPENDENCE (one fixed attractor).

OPERATIONALIZATION OF THE BAND FOR SPIKING (declared, fixed):
  * EPG positive activity = per-EPG leaky spike trace r (tau_r = 50 ms,
    ASSUMED readout-only plumbing; all criteria are ratios/normalized so
    the trace scale cancels). mass = sum(r); PVA angle and circular
    variance cv = 1 - |sum(r e^{i theta})| / mass as in class 1.
  * retention = mass at end of 2000 ms darkness / mass at seed release.
  * "POSITION follows the seed": each of the 4 settled PVAs is nearest
    (circular) to ITS OWN seed angle among the 4 preregistered angles,
    AND the 4 settled PVAs form >= 4 clusters at 45-deg resolution
    (pairwise circular distance < 45 deg merges). A dead settle (mass <=
    1e-9) fails. This is the nearest-assignment reading of ">= 4
    distinguishable positions"; class 1 failed it with every live seed
    settling near 222 deg.
  * "deg/step-equivalent": ASSUMED conversion -- one class-1 step maps
    to one 10-ms readout bin (class-1 macro-steps carry no physical
    duration). 0.05 deg/bin = 5 deg/s, well below the 30-60 deg/s
    physiological rotation floor (Turner-Evans 2017; doc B23 guidance),
    i.e. lenient in the same way the class-1 band was. The
    sign-opposition core of C2 is conversion-independent.
  * C2 rate = mean of unwrapped per-bin PVA deltas over 100 bins
    (1000 ms) of sustained one-sided PEN_a drive from the settled state;
    NaN if < 50 valid bins (both endpoints alive). RAW rates, no drift
    subtraction (matching class 1); darkness-drift arm recorded as a
    preregistered DIAGNOSTIC only.

MODEL (fidelity class 2):
  * Subcircuit: EPG/PEN_a(PEN1)/PEN_b(PEN2)/Delta7/PEG induced subgraph
    of the MaleCNS compiled graph, signed raw synapse counts
    (flygi.connectome.subcircuit; measured-NT signs: ACh +, glutamate -
    => Delta7 inhibitory per Turner-Evans 2020, GluCl). MEASURED at
    registration: 148 neurons (46 EPG + 20 PEN_a + 22 PEN_b + 42 Delta7
    + 18 PEG), 8910 edges, E-sum 96306, I-sum -41998, median nonzero
    excitatory count 10. NOTE, recorded plainly: the task sheet and
    tests/test_subcircuit.py say "106 neurons", but their exact patterns
    ("PEN_a", "PEN_b") match ZERO nodes -- the types are "PEN_a(PEN1)" /
    "PEN_b(PEN2)" -- so 106 = EPG+Delta7+PEG only, a ring with NO PEN
    cells, on which C2 is unrunnable. This script uses the corrected
    patterns; the discrepancy is reported upward, not hidden.
  * EPGt (4 cells) excluded: not in the registered member list.
  * LIF params, ESTABLISHED (Shiu et al. 2024 Nature canonical set,
    verified against paper AND code in docs/fidelity2/; consistent with
    Kakaria & de Bivort 2017 B2-B9): tau_m = 20 ms, v_rest = v_reset =
    -52 mV, v_thresh = -45 mV, tau_syn = 5 ms, refractory = 2.2 ms,
    dt = 0.1 ms (K&dB B12). K&dB's -72 mV undershoot variant NOT used
    (Shiu reset taken as canonical); declared, not swept.
  * Weights: count * one global scalar per sign class (MANDATORY
    calibration, doc B24 + consistency caution): W_eff = e_scale * count
    on excitatory entries, e_scale * i_ratio * count on inhibitory.
    ASSUMED sweep: e_scale in {0.0025, 0.005, 0.01, 0.02, 0.04, 0.08,
    0.16} (log2 grid; 0.08 reproduces Shiu's refit w_syn = 0.275 mV
    per-contact peak PSP under this engine's integration -- 0.275 mV /
    (~0.7 * tau_syn) -- and the grid spans 32x below to 2x above because
    the whole-brain refit need not transfer to a 148-cell subcircuit);
    i_ratio in {0.5, 0.75, 1.0, 1.5, 2.0} (center 0.75 = K&dB
    inhibition/excitation ratio, doc B10/B24).
  * Background: 5 Hz Poisson events on every cell (ESTABLISHED B14),
    event amplitude = 1 median-count excitatory PSC (= e_scale * 10;
    ASSUMED anchor, declared). Implemented as an external exponential
    trace with the same tau_syn = 5 ms. K&dB's printed Gaussian noise sd
    3e-10 V is physically negligible as printed (doc consistency
    caution); the Poisson background carries the noise intent.
  * Seed / PEN stimulus: Poisson 120 Hz events (ESTABLISHED B14 stimulus
    peak) at amplitude 3x background event (STIM_AMP_FACTOR = 3.0,
    ASSUMED, fixed not swept: chosen for reliable ignition; C1/C2 score
    post-release dynamics, not the seed, and L/R C2 arms share it so the
    sign test is invariant to it). Seed: 500 ms on EPG cells within
    45 deg of the seed angle (90-deg wedge, class-1 protocol). C2: 1000
    ms on left-side (_L#) or right-side (_R#) PEN_a(PEN1) cells
    (class-1 C2 drove PEN_a only; kept).
  * TONIC DRIVE KNOB (ASSUMED, doc zero-baseline-silence risk): stage 1
    sweeps tonic = 0 only. IFF no config passes calibration at stage 1,
    stage 2 re-sweeps the grid at tonic in {0.25, 0.5, 0.75} x rheobase
    (rheobase = (v_thresh - v_rest)/tau_m = 0.35 mV/ms), constant
    current to all cells. Labelled ASSUMED wherever it appears.
  * EPG ring angles, same as class 1 (ESTABLISHED annotation + ASSUMED
    mapping): instance wedge ids _L1-_L8/_R1-_R8, index = (wedge-1)*2 +
    (0 if L else 1), angle = index * 22.5 deg -- wrong only up to a fixed
    rotation/reflection, which cancels in every within-run comparison.

CALIBRATION (declared; performed on calibration stimuli, scored on
held-out stimuli, never on the scored measurement):
  * Calibrated: the two sign-class scalars (e_scale, i_ratio) and, stage
    2 only, the tonic knob -- exactly the one-scalar-per-sign-class gain
    calibration the literature allows (K&dB; Shiu w_syn refit).
  * Calibration stimulus: seed angle 22.5 deg ONLY. Criterion: that
    angle's C1-like persistence (retention >= 0.05 AND cv <= 0.6 AND
    alive at 2000 ms darkness). Selection among passers: max score =
    min(retention, 1.0) - cv; ties -> first in grid order. Position-
    following and C2 are NEVER consulted during selection.
  * Scored (held out): C1 persistence on the OTHER THREE angles (112.5,
    202.5, 292.5 -- ALL three must pass retention >= 0.05 AND cv <= 0.6),
    position-following across all 4 settled positions (selection never
    saw any position), and C2 on the three held-out angles (ALL three
    must pass; per-angle band as above). Scoring runs use fresh RNG
    streams, including a fresh re-run of the calibration angle.
  * If NO config passes calibration in either stage: the benchmark FAILS
    at C1-formation; the best-approach config (max score) is still
    scored and recorded, labelled as such.
  * Diagnostics recorded, not gated: spontaneous EPG rate in a 500-ms
    background-only pre-seed window (doc target ~1-10 Hz), mean EPG rate
    over the last 500 ms of darkness, drift arm, calibration-angle C2.

TRIVIAL ALTERNATIVE (mandatory, named): degree-preserving shuffled ring
-- the COO post-endpoint column is permuted with a seeded RNG; each
node's out-degree AND out-strength are preserved exactly ((pre, weight)
pairs untouched, so Dale/NT signs stay consistent), each node's in-edge
count is preserved exactly (post multiset unchanged), in-strength
approximately; self-loops/duplicates from the permutation are kept and
summed. The shuffled net gets the IDENTICAL calibration sweep and
scoring. Expectation stated before the run: the bump must NOT
form/persist there. ATTRIBUTION requires the real anatomy to pass what
the shuffle cannot: attribution_holds iff the real net passes C1 on the
scored angles AND the shuffled net's scored angles include NO persisting
localized bump at its own best config.

RESOURCE RULE (measured before launch): free RAM 4.4 GB (vm_stat
free+inactive); extraction scan peak RSS 1.17 GB measured, done ONCE and
released before the sweep; the 148-node simulation is < 10 MB. Sweeps
run sequentially in ONE process. Lane stays far under 3 GB.

EXPECTED-tier note (repo base rate for expected-tier score/outcome
predictions: 0 for 11): the K&dB working regime is known-narrow (B16:
~1.5% of random weight perturbations keep function); a miss everywhere
on this grid is a live outcome and will be recorded as the measurement
it is.

AMENDMENT (registered 2026-09-29 after calibration stages 1-2 ran on
the REAL network and BEFORE stage 3 ran anywhere; the BAND and the
calibration/scoring split are UNCHANGED -- this extends only the
ASSUMED calibration grid, on the calibration stimulus). Stage 1
measured 0/35 calibration passes: silence at e_scale <= 0.005,
refractory-limited seizure (retention ~1.0, cv ~0.93, EPG ~355-420 Hz,
settled PVA ~237 deg = the all-cells-firing readout skew) at e_scale >=
0.01, with i_ratio 0.5-2.0 changing nothing at seizure points; stage 2
(tonic knob) showed the same bimodality with a knife edge between
i_ratio 0.75 and 1.0 at e=0.005/tonic=0.175. Diagnosis from the
MEASURED block sums (this header, subcircuit section): total E onto EPG
is 36549 counts vs Delta7 inhibition 4294, so the doc-B24 anchor --
EFFECTIVE inhibition/excitation ~= 0.75, i.e. the block-sum ratio, not
the scalar -- requires scalar i_ratio ~= 6.4 on EPG input (per-
population implied scalars: Delta7-in 0.56, PEG-in 1.37, PEN_b-in 2.2,
EPG-in 6.4, PEN_a-in 9.4). Stages 1-2's I_RATIOS grid (0.5-2.0) was
therefore mis-centered against the doc's intent. STAGE 3 (runs only if
stages 1-2 produce no calibration pass; identical for the shuffled
null): e_scale in {0.004, 0.0055, 0.007, 0.0085, 0.01, 0.014, 0.02}
(refining the measured silence/seizure edge), i_ratio in {2, 4, 6, 8,
12} (centered on the effective-0.75 anchor), tonic in {0, 0.5 x
rheobase}. Selection rule, held-out scoring, and every band threshold
are byte-identical to stages 1-2.
======================================================================

Writes results/benchmarks/fc2_eb_ring.json, saving partial results after
every calibration config and every scored angle. Creates nothing else.
"""

from __future__ import annotations

import argparse
import json
import re
import resource
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

RUNTIME_DIR = "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
TYPE_PATTERNS = ("EPG", "PEN_a*", "PEN_b*", "Delta7", "PEG")  # corrected; see header

# --- ESTABLISHED LIF parameters (Shiu 2024 canonical; K&dB 2017 B2-B9) ---
DT_MS = 0.1
TAU_M_MS = 20.0
TAU_SYN_MS = 5.0
V_REST = -52.0
V_THRESH = -45.0
V_RESET = -52.0
REFRACTORY_MS = 2.2

# --- ASSUMED sweep grids (declared in header) ---
E_SCALES = (0.0025, 0.005, 0.01, 0.02, 0.04, 0.08, 0.16)
I_RATIOS = (0.5, 0.75, 1.0, 1.5, 2.0)
TONIC_FRACTIONS_STAGE2 = (0.25, 0.5, 0.75)  # x rheobase, only if stage 1 empty
RHEOBASE = (V_THRESH - V_REST) / TAU_M_MS  # 0.35 mV/ms
# Stage 3 (AMENDMENT in header; only if stages 1-2 produce no cal pass):
E_SCALES_3 = (0.004, 0.0055, 0.007, 0.0085, 0.01, 0.014, 0.02)
I_RATIOS_3 = (2.0, 4.0, 6.0, 8.0, 12.0)
TONIC_FRACTIONS_3 = (0.0, 0.5)

# --- protocol constants ---
PRE_SEED_MS = 500.0
SEED_MS = 500.0
DARK_MS = 2000.0  # band: >= 2 simulated seconds
ROT_MS = 1000.0
BIN_MS = 10.0  # 1 class-1 "step-equivalent" (ASSUMED conversion, header)
SEED_ANGLES = (22.5, 112.5, 202.5, 292.5)
CAL_ANGLE = 22.5
WEDGE_SPAN_DEG = 90.0
BG_RATE_HZ = 5.0  # ESTABLISHED B14
STIM_RATE_HZ = 120.0  # ESTABLISHED B14
STIM_AMP_FACTOR = 3.0  # ASSUMED (header)
READOUT_TAU_MS = 50.0  # ASSUMED readout-only plumbing (header)

# --- band thresholds (FIXED, class 1) ---
RETENTION_MIN = 0.05
CIRCVAR_MAX = 0.6
C2_RATE_MIN = 0.05  # deg per 10-ms bin ("step-equivalent")
MIN_VALID_BINS = 50
POSITION_CLUSTER_DEG = 45.0
DEAD_MASS = 1e-9

RNG_BASE = 20260929

BAND_VERBATIM = (
    "(C1) after a transient wedge seed, a LOCALIZED bump (circular variance "
    "<= 0.6 over EPG positive activity) PERSISTS >= 2 simulated seconds in "
    "darkness with retention >= 0.05 of post-seed activity, AND the settled "
    "bump POSITION follows the seed (>= 4 distinguishable positions across "
    "seeds at 4 preregistered angles -- this is the anti-fixed-point "
    "criterion class 1 failed); (C2) asymmetric PEN drive rotates the bump "
    "with OPPOSITE signs for left vs right drive, |rate| >= 0.05 "
    "deg/step-equivalent."
)


def circ_dist(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def circular_stats(activity, radians):
    """Positive mass, PVA angle (deg), circular variance -- class-1 formulas."""
    import numpy as np

    mass = float(activity.sum())
    if mass <= DEAD_MASS:
        return mass, float("nan"), 1.0
    vector = complex(np.sum(activity * np.exp(1j * radians)))
    return mass, float(np.rad2deg(np.angle(vector)) % 360.0), float(
        1.0 - abs(vector) / mass
    )


class RingSim:
    """One network (real or shuffled) at one (e_scale, i_ratio, tonic) config.

    Owns the SpikingNetwork plus the external Poisson-background trace and
    the leaky EPG readout trace; matrix pre-transformations only, src/
    untouched.
    """

    def __init__(self, base_matrix, types, epg_idx, epg_radians, e_scale, i_ratio, tonic):
        import numpy as np

        from flygi.dynamics.spiking import ParameterTable, SpikingNetwork, TypeParams

        self.np = np
        eff = base_matrix.copy().astype(np.float32)
        eff.data = np.where(
            eff.data > 0, eff.data * e_scale, eff.data * e_scale * i_ratio
        ).astype(np.float32)
        table = ParameterTable(
            default=TypeParams(
                tau_m_ms=TAU_M_MS,
                v_thresh=V_THRESH,
                v_rest=V_REST,
                v_reset=V_RESET,
                tau_syn_ms=TAU_SYN_MS,
                refractory_ms=REFRACTORY_MS,
                provenance=(
                    "ESTABLISHED: Shiu 2024 canonical LIF "
                    "(tau_m 20ms, v_rest=v_reset=-52mV, v_th=-45mV, tau_syn 5ms, "
                    "refractory 2.2ms); consistent with Kakaria & de Bivort 2017"
                ),
            )
        )
        self.net = SpikingNetwork(eff, types, table, dt_ms=DT_MS, w_scale=1.0)
        self.n = self.net.node_count
        self.epg = epg_idx
        self.radians = epg_radians
        # ASSUMED anchor (header): background event = 1 median-count E PSC.
        self.bg_amp = np.float32(e_scale * 10.0)
        self.stim_amp = np.float32(STIM_AMP_FACTOR * self.bg_amp)
        self.tonic = np.full(self.n, tonic, dtype=np.float32)
        self.p_bg = BG_RATE_HZ * DT_MS / 1000.0
        self.p_stim = STIM_RATE_HZ * DT_MS / 1000.0
        self.decay_syn = np.float32(1.0 - DT_MS / TAU_SYN_MS)
        self.decay_r = np.float32(1.0 - DT_MS / READOUT_TAU_MS)
        self.ext = np.zeros(self.n, dtype=np.float32)
        self.r = np.zeros(len(epg_idx), dtype=np.float32)

    def snapshot(self):
        n = self.net
        return (
            n.v.copy(),
            n.i_syn.copy(),
            n._refractory_left.copy(),
            n.last_output.copy(),
            self.ext.copy(),
            self.r.copy(),
        )

    def restore(self, snap):
        n = self.net
        n.v, n.i_syn, n._refractory_left, n.last_output = (
            snap[0].copy(),
            snap[1].copy(),
            snap[2].copy(),
            snap[3].copy(),
        )
        self.ext, self.r = snap[4].copy(), snap[5].copy()

    def advance(self, ms, rng, stim_idx=None, bins=False):
        """Advance ms of simulated time; returns EPG spike count and optional
        per-10ms-bin PVA angles from the readout trace."""
        np = self.np
        steps = int(round(ms / DT_MS))
        bin_steps = int(round(BIN_MS / DT_MS))
        epg_spikes = 0
        angles = []
        for k in range(steps):
            self.ext *= self.decay_syn
            bg = rng.random(self.n) < self.p_bg
            if bg.any():
                self.ext[bg] += self.bg_amp
            if stim_idx is not None and stim_idx.size:
                ev = rng.random(stim_idx.size) < self.p_stim
                if ev.any():
                    self.ext[stim_idx[ev]] += self.stim_amp
            out = self.net.step(self.ext + self.tonic)
            spikes = out[self.epg]
            epg_spikes += int(spikes.sum())
            self.r = self.r * self.decay_r + spikes
            if bins and (k + 1) % bin_steps == 0:
                _, ang, _ = circular_stats(self.r, self.radians)
                angles.append(ang)
        return epg_spikes, angles

    def read(self):
        return circular_stats(self.r, self.radians)


def rotation_rate(bin_angles):
    """Mean unwrapped per-bin PVA delta (deg/bin); NaN if < MIN_VALID_BINS."""
    import numpy as np

    deltas = []
    prev = float("nan")
    for ang in bin_angles:
        if not (np.isnan(ang) or np.isnan(prev)):
            deltas.append((ang - prev + 180.0) % 360.0 - 180.0)
        prev = ang
    if len(deltas) < MIN_VALID_BINS:
        return float("nan"), len(deltas)
    return float(np.mean(deltas)), len(deltas)


def rng_for(*ids):
    import numpy as np

    return np.random.default_rng([RNG_BASE, *ids])


def run_trial(sim, angle, epg_angles, epg_idx, rng):
    """Pre-seed, seed, darkness. Returns C1 stats + settled snapshot."""
    import numpy as np

    sim.net.reset()
    sim.ext[:] = 0.0
    sim.r[:] = 0.0
    spont_spikes, _ = sim.advance(PRE_SEED_MS, rng)
    spont_hz = spont_spikes / len(epg_idx) / (PRE_SEED_MS / 1000.0)
    wedge = epg_idx[
        np.array([circ_dist(a, angle) <= WEDGE_SPAN_DEG / 2.0 for a in epg_angles])
    ]
    sim.advance(SEED_MS, rng, stim_idx=wedge)
    release_mass, release_angle, release_cv = sim.read()
    dark_first_spikes, _ = sim.advance(DARK_MS - 500.0, rng)
    dark_last_spikes, _ = sim.advance(500.0, rng)
    dark_hz_last = dark_last_spikes / len(epg_idx) / 0.5
    final_mass, final_angle, final_cv = sim.read()
    retention = final_mass / release_mass if release_mass > DEAD_MASS else 0.0
    return {
        "spont_epg_hz": round(spont_hz, 3),
        "release_mass": release_mass,
        "release_angle": release_angle,
        "release_circvar": release_cv,
        "final_mass": final_mass,
        "settled_angle": final_angle,
        "final_circvar": final_cv,
        "retention": retention,
        "dark_epg_hz_last500ms": round(dark_hz_last, 3),
        "persist_pass": bool(
            retention >= RETENTION_MIN
            and final_cv <= CIRCVAR_MAX
            and final_mass > DEAD_MASS
        ),
    }, sim.snapshot()


def score_config(sim_factory, cfg, net_id, cfg_idx, epg_angles, epg_idx, pen_left, pen_right, save):
    """Held-out scoring: all 4 angles' C1 + C2 arms. Fresh RNG streams."""
    import numpy as np

    per_angle: dict[str, Any] = {}
    settled: dict[str, Any] = {}
    sim = sim_factory(cfg)
    for a_i, angle in enumerate(SEED_ANGLES):
        stats, snap = run_trial(
            sim, angle, epg_angles, epg_idx, rng_for(net_id, 1, cfg_idx, a_i, 0)
        )
        per_angle[str(angle)] = stats
        settled[str(angle)] = snap
        save()
    # --- C1 position criterion over all 4 settled positions ---
    settled_angles = {a: per_angle[str(a)]["settled_angle"] for a in SEED_ANGLES}
    alive = all(
        per_angle[str(a)]["final_mass"] > DEAD_MASS
        and not np.isnan(settled_angles[a])
        for a in SEED_ANGLES
    )
    follows = alive and all(
        min(SEED_ANGLES, key=lambda s: circ_dist(settled_angles[a], s)) == a
        for a in SEED_ANGLES
    )
    n_positions = 0
    if alive:
        clusters: list[list[float]] = []
        for a in SEED_ANGLES:
            placed = False
            for c in clusters:
                if any(circ_dist(settled_angles[a], x) < POSITION_CLUSTER_DEG for x in c):
                    c.append(settled_angles[a])
                    placed = True
                    break
            if not placed:
                clusters.append([settled_angles[a]])
        n_positions = len(clusters)
    heldout = [a for a in SEED_ANGLES if a != CAL_ANGLE]
    heldout_persist = all(per_angle[str(a)]["persist_pass"] for a in heldout)
    c1_pass = bool(heldout_persist and follows and n_positions >= 4)

    # --- C2: drift/left/right arms from each settled state ---
    c2: dict[str, Any] = {}
    for a_i, angle in enumerate(SEED_ANGLES):
        arms = {}
        for arm_id, (name, idx) in enumerate(
            (("drift", None), ("left", pen_left), ("right", pen_right)), start=1
        ):
            sim.restore(settled[str(angle)])
            _, bin_angles = sim.advance(
                ROT_MS, rng_for(net_id, 1, cfg_idx, a_i, arm_id), stim_idx=idx, bins=True
            )
            rate, valid = rotation_rate(bin_angles)
            arms[name] = {"rate_deg_per_bin": rate, "rate_deg_per_s": (
                rate * 1000.0 / BIN_MS if not np.isnan(rate) else float("nan")
            ), "valid_bins": valid}
        left, right = arms["left"]["rate_deg_per_bin"], arms["right"]["rate_deg_per_bin"]
        both = not (np.isnan(left) or np.isnan(right))
        arms["angle_pass"] = bool(
            both
            and left * right < 0.0
            and abs(left) >= C2_RATE_MIN
            and abs(right) >= C2_RATE_MIN
        )
        c2[str(angle)] = arms
        save()
    c2_heldout_pass = bool(all(c2[str(a)]["angle_pass"] for a in heldout))

    return {
        "per_angle_c1": per_angle,
        "position": {
            "settled_angles": {str(a): settled_angles[a] for a in SEED_ANGLES},
            "all_alive": bool(alive),
            "follows_seed_all4": bool(follows),
            "n_distinguishable_positions": int(n_positions),
        },
        "heldout_angles": [str(a) for a in heldout],
        "c1_heldout_persist_pass": bool(heldout_persist),
        "c1_pass": c1_pass,
        "c2_per_angle": c2,
        "c2_heldout_pass": c2_heldout_pass,
        "c2_cal_angle_diagnostic": c2[str(CAL_ANGLE)]["angle_pass"],
        "pass": bool(c1_pass and c2_heldout_pass),
    }


def calibrate(sim_factory, net_id, grid, epg_angles, epg_idx, save, log):
    """Sweep the grid on the calibration angle only. Returns rows + selection."""
    rows = []
    for cfg_idx, cfg in enumerate(grid):
        t0 = time.time()
        sim = sim_factory(cfg)
        stats, _ = run_trial(
            sim, CAL_ANGLE, epg_angles, epg_idx, rng_for(net_id, 0, cfg_idx, 0, 0)
        )
        score = min(stats["retention"], 1.0) - stats["final_circvar"]
        row = {
            "cfg_index": cfg_idx,
            "e_scale": cfg[0],
            "i_ratio": cfg[1],
            "tonic": cfg[2],
            **stats,
            "cal_pass": stats["persist_pass"],
            "score": round(score, 4),
            "elapsed_s": round(time.time() - t0, 1),
        }
        rows.append(row)
        log(
            f"  cal cfg{cfg_idx} e={cfg[0]} r={cfg[1]} tonic={cfg[2]:.4f}: "
            f"spont {stats['spont_epg_hz']}Hz ret {stats['retention']:.3f} "
            f"cv {stats['final_circvar']:.3f} settled {stats['settled_angle']:.1f} "
            f"dark {stats['dark_epg_hz_last500ms']}Hz "
            f"{'CAL-PASS' if row['cal_pass'] else 'miss'} [{row['elapsed_s']}s]"
        )
        save(rows)
    passers = [r for r in rows if r["cal_pass"]]
    pool = passers if passers else rows
    best = max(pool, key=lambda r: (r["score"], -r["cfg_index"]))
    return rows, best, bool(passers)


def main() -> int:
    parser = argparse.ArgumentParser(description="fc2 EB ring benchmark")
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "results" / "benchmarks" / "fc2_eb_ring.json",
    )
    parser.add_argument("--smoke", action="store_true", help="2 configs, real net only")
    args = parser.parse_args()

    import numpy as np
    from scipy import sparse

    from flygi.connectome.subcircuit import extract_subcircuit, select_nodes

    t_start = time.time()
    idx = select_nodes(ROOT / RUNTIME_DIR, type_patterns=TYPE_PATTERNS)
    sub = extract_subcircuit(ROOT / RUNTIME_DIR, idx)
    print(
        f"subcircuit: {sub.node_count} nodes, {sub.matrix.nnz} edges "
        f"({time.time() - t_start:.1f}s)",
        flush=True,
    )
    types = sub.types.astype("U")
    instances = sub.instances.astype("U")

    # EPG ring angles (class-1 mapping; header).
    epg_all = sub.indices_where("EPG")
    epg_idx, epg_angles = [], []
    for i in epg_all:
        m = re.search(r"_([LR])(\d)", instances[i])
        if m:
            side, wedge = m.group(1), int(m.group(2))
            epg_idx.append(int(i))
            epg_angles.append(((wedge - 1) * 2 + (0 if side == "L" else 1)) * 22.5)
    epg_idx = np.asarray(epg_idx, dtype=np.int64)
    epg_angles = np.asarray(epg_angles)
    epg_radians = np.deg2rad(epg_angles)

    pen_a = sub.indices_where("PEN_a*")
    pen_left, pen_right = [], []
    for i in pen_a:
        m = re.search(r"_([LR])(\d)", instances[i])
        if m:
            (pen_left if m.group(1) == "L" else pen_right).append(int(i))
    pen_left = np.asarray(pen_left, dtype=np.int64)
    pen_right = np.asarray(pen_right, dtype=np.int64)
    print(
        f"EPG with wedge labels: {epg_idx.size}; PEN_a left {pen_left.size} "
        f"right {pen_right.size}",
        flush=True,
    )

    base_real = sparse.csr_matrix(sub.matrix, dtype=np.float32)

    # Trivial alternative: degree-preserving shuffle (header).
    coo = base_real.tocoo()
    perm = np.random.default_rng([RNG_BASE, 777]).permutation(coo.data.size)
    base_shuf = sparse.csr_matrix(
        (coo.data.copy(), (coo.row[perm], coo.col.copy())),
        shape=base_real.shape,
        dtype=np.float32,
    )
    base_shuf.sum_duplicates()

    med_pos = float(np.median(base_real.data[base_real.data > 0]))
    results: dict[str, Any] = {
        "benchmark": "fc2_eb_ring (fidelity class 2: EB ring movable persistent bump)",
        "band_verbatim": BAND_VERBATIM,
        "class1_reference": {
            "script": "scripts/benchmarks/cx_ring.py",
            "result": (
                "C1 position-following 0/21 (fixed-point attractor near 222 deg "
                "everywhere alive); measured 2026-09-29, "
                "results/benchmarks/cx_ring.json"
            ),
            "citations": [
                "Seelig & Jayaraman 2015 Nature 521:186",
                "Turner-Evans et al. 2017 eLife 6:e23496",
                "Green et al. 2017 Nature 546:101",
                "Kim et al. 2017 Science 356:849 (WTA is correct physiology)",
            ],
        },
        "model": {
            "subcircuit": {
                "type_patterns": list(TYPE_PATTERNS),
                "nodes": int(sub.node_count),
                "edges": int(sub.matrix.nnz),
                "note_106_discrepancy": (
                    "task sheet / test said 106 neurons, but exact patterns "
                    "PEN_a/PEN_b match zero nodes (types are PEN_a(PEN1)/"
                    "PEN_b(PEN2)); 106 = EPG+Delta7+PEG only, no PENs, C2 "
                    "unrunnable. Corrected selection = 148 neurons."
                ),
                "median_positive_count": med_pos,
            },
            "lif_established": {
                "tau_m_ms": TAU_M_MS,
                "tau_syn_ms": TAU_SYN_MS,
                "v_rest": V_REST,
                "v_thresh": V_THRESH,
                "v_reset": V_RESET,
                "refractory_ms": REFRACTORY_MS,
                "dt_ms": DT_MS,
                "source": "Shiu 2024 canonical (docs/fidelity2/); K&dB 2017 B2-B9/B12",
            },
            "assumed_swept": {
                "e_scale": list(E_SCALES),
                "i_ratio": list(I_RATIOS),
                "tonic_stage2_x_rheobase": list(TONIC_FRACTIONS_STAGE2),
                "stage3_amendment": {
                    "e_scale": list(E_SCALES_3),
                    "i_ratio": list(I_RATIOS_3),
                    "tonic_x_rheobase": list(TONIC_FRACTIONS_3),
                    "registered": (
                        "2026-09-29 after stages 1-2 measured 0 calibration "
                        "passes (silence-or-seizure) on the real network and "
                        "before stage 3 ran; band unchanged; rationale in "
                        "script header AMENDMENT block"
                    ),
                },
            },
            "assumed_fixed": {
                "stim_amp_factor": STIM_AMP_FACTOR,
                "bg_event_amp": "e_scale * median positive count (10)",
                "readout_tau_ms": READOUT_TAU_MS,
                "deg_per_step_equivalent": "1 step = 1 bin of 10 ms",
            },
        },
        "calibration_declared": (
            "one global scalar per sign class (e_scale x i_ratio; tonic knob "
            "stage 2 only if stage 1 empty), calibrated on seed angle 22.5 deg "
            "persistence only; scored on held-out angles 112.5/202.5/292.5 "
            "(C1 persistence + C2) and on position-following across all 4 "
            "settled positions (never consulted during selection)"
        ),
        "resource_note": (
            "free RAM 4.4 GB measured pre-launch; extraction peak RSS 1.17 GB "
            "(once); simulation < 10 MB; single process, sequential sweep"
        ),
        "status": "running",
        "networks": {},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def save_all():
        results["elapsed_s"] = round(time.time() - t_start, 1)
        results["peak_rss_gb"] = round(
            resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e9, 3
        )
        args.output.write_text(json.dumps(results, indent=2))

    def log(msg):
        print(msg, flush=True)

    stage1_grid = [(e, r, 0.0) for e in E_SCALES for r in I_RATIOS]
    if args.smoke:
        stage1_grid = stage1_grid[:2]

    for net_id, (net_name, base) in enumerate(
        (("real", base_real), ("shuffled_degree_preserving", base_shuf))
    ):
        if args.smoke and net_id == 1:
            break
        log(f"== network: {net_name} ==")

        def sim_factory(cfg, _base=base):
            return RingSim(
                _base, types, epg_idx, epg_radians, cfg[0], cfg[1], cfg[2]
            )

        entry: dict[str, Any] = {}
        results["networks"][net_name] = entry

        def save_cal(rows, _entry=entry):
            _entry["calibration"] = {"stage": _entry.get("calibration", {}).get("stage", 1), "rows": rows}
            save_all()

        rows, best, any_pass = calibrate(
            sim_factory, net_id, stage1_grid, epg_angles, epg_idx, save_cal, log
        )
        entry["calibration"] = {"stage": 1, "rows": rows, "any_cal_pass": any_pass}
        stage = 1
        if not any_pass and not args.smoke:
            log(
                "  stage 1: zero calibration passes -- zero-baseline-silence "
                "blocker bit; sweeping ASSUMED tonic knob (stage 2)"
            )
            stage2_grid = [
                (e, r, f * RHEOBASE)
                for f in TONIC_FRACTIONS_STAGE2
                for e in E_SCALES
                for r in I_RATIOS
            ]

            def save_cal2(rows2, _entry=entry):
                _entry["calibration_stage2"] = {"rows": rows2}
                save_all()

            rows2, best2, any_pass2 = calibrate(
                sim_factory, net_id + 10, stage2_grid, epg_angles, epg_idx, save_cal2, log
            )
            entry["calibration_stage2"] = {"rows": rows2, "any_cal_pass": any_pass2}
            if any_pass2 or best2["score"] > best["score"]:
                best, any_pass, rows, stage = best2, any_pass2, rows2, 2
        if not any_pass and not args.smoke:
            log(
                "  stages 1-2: zero calibration passes -- running stage 3 "
                "(AMENDMENT grid: i_ratio recentered on the effective-0.75 "
                "anchor, e_scale refined at the silence/seizure edge)"
            )
            stage3_grid = [
                (e, r, f * RHEOBASE)
                for f in TONIC_FRACTIONS_3
                for e in E_SCALES_3
                for r in I_RATIOS_3
            ]

            def save_cal3(rows3, _entry=entry):
                _entry["calibration_stage3"] = {"rows": rows3}
                save_all()

            rows3, best3, any_pass3 = calibrate(
                sim_factory, net_id + 20, stage3_grid, epg_angles, epg_idx, save_cal3, log
            )
            entry["calibration_stage3"] = {"rows": rows3, "any_cal_pass": any_pass3}
            if any_pass3 or best3["score"] > best["score"]:
                best, any_pass, rows, stage = best3, any_pass3, rows3, 3
        entry["selected_config"] = {
            "stage": stage,
            "e_scale": best["e_scale"],
            "i_ratio": best["i_ratio"],
            "tonic": best["tonic"],
            "cal_pass": best["cal_pass"],
            "cal_score": best["score"],
            "label": "calibration pass" if any_pass else "best-approach (NO cal pass)",
        }
        save_all()
        log(
            f"  selected ({entry['selected_config']['label']}): "
            f"e={best['e_scale']} r={best['i_ratio']} tonic={best['tonic']:.4f}"
        )
        cfg = (best["e_scale"], best["i_ratio"], best["tonic"])
        entry["scored"] = score_config(
            sim_factory,
            cfg,
            net_id,
            int(best["cfg_index"]) + 1000 * (stage - 1),
            epg_angles,
            epg_idx,
            pen_left,
            pen_right,
            save_all,
        )
        save_all()
        s = entry["scored"]
        log(
            f"  scored: C1 heldout-persist {s['c1_heldout_persist_pass']} "
            f"follows {s['position']['follows_seed_all4']} "
            f"n_pos {s['position']['n_distinguishable_positions']} -> C1 {s['c1_pass']} | "
            f"C2 heldout {s['c2_heldout_pass']} | PASS {s['pass']}"
        )

    real = results["networks"].get("real", {})
    shuf = results["networks"].get("shuffled_degree_preserving", {})
    if real and shuf:
        shuf_persist_any = any(
            v["persist_pass"] for v in shuf["scored"]["per_angle_c1"].values()
        )
        results["verdict"] = {
            "passed": bool(real["scored"]["pass"]),
            "c1_pass": bool(real["scored"]["c1_pass"]),
            "c2_pass": bool(real["scored"]["c2_heldout_pass"]),
            "shuffled_persist_any_angle": bool(shuf_persist_any),
            "shuffled_pass": bool(shuf["scored"]["pass"]),
            "attribution_holds": bool(
                real["scored"]["c1_pass"] and not shuf_persist_any
            ),
        }
    results["status"] = "complete"
    save_all()
    log(f"done in {results['elapsed_s']}s -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
