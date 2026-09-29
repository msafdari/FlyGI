#!/usr/bin/env python3
"""H-MB-CLASS2-ASSOCIATION, stage A -- one-shot visual association on the real MB.

The decisive experiment of the fly-module verdict program: does the class-2-
validated mushroom body (real MaleCNS PN/KC/APL/MBON subcircuit, LIF KCs at the
KC-sparseness-passing configuration, graded APL, biological DAN-gated KC->MBON
depression) perform one-shot visual association on real ARC game states well
enough to beat all three controls on HELD-OUT games?

================================ PREREGISTRATION ==============================
Verbatim from EXPERIMENTS.yaml, H-MB-CLASS2-ASSOCIATION evidence (registered
2026-09-29 before any stage-A code existed). Nothing below this line is tuned.

    PREREGISTERED 2026-09-29 BEFORE IMPLEMENTATION, including one
    declared AMENDMENT to H-MODULE-VERDICT's requirement-3
    endpoint: the full agent-battery endpoint is infeasible for a
    spiking MB in the action loop (milliseconds-of-simulation per
    frame times 45,000 battery actions), so the test is STAGED --
    stage A, component-level: one-shot conditioning on real game
    frames, scored as held-out discrimination; stage B, agent
    seating with the battery endpoint, runs ONLY if stage A
    passes, with a rate-model or cached-readout port whose
    equivalence to the spiking component must itself be measured.
    This amendment is declared before any stage-A code exists.
    STAGE-A PROTOCOL, fixed now: input = bio-eye column features
    through a seeded sparse projection onto the 627 PNs
    (ENGINEERED retinotopy-preserving plumbing, labelled; the
    anatomical colour-histogram bus is measured layout-blind and
    would confound the motif); per trial, present state A with
    punishment-DAN coincidence and state B with reward-DAN
    coincidence (one shot each, biological depression rule on the
    REAL KC->MBON mask only); test = valence readout
    discrimination on near-variants of A and B (the game's own
    subsequent frames within the same level) and on unrelated
    states; pairs drawn from 5 train games, EVALUATED on 5
    disjoint held-out games x 3 seeds. CONTROLS, all three
    mandatory: degree-preserving rewired PN->KC and KC->MBON;
    shuffled-credit (eligibility permuted before each update); and
    an engineered equivalent (one-shot perceptron on the same PN
    input vector, matched update count). PASS BANDS, fixed now:
    held-out discrimination accuracy > 0.5 (binomial p < 0.05)
    AND real > each control by a paired margin > 0 across the 15
    game x seed cells (sign test p < 0.05). The MB configuration
    is one of fc2_kc_sparse.json's pass_configs (tau_m_kc 20 ms,
    tau_syn 5 ms, beta 1.0 -- the centre of the pass region),
    fixed here, not tuned during the arm. Expected tier, base
    rate stated: expected-tier predictions are ~1 for 13; the
    prior MB-learning nulls at class 1 do not predict this arm
    (they were run on a code that never validated).

BIOLOGY (Established; cited at the update rule below):
  Aso et al. 2014 eLife 3:e04577 (MB output architecture; DAN compartments
    gate KC->MBON plasticity; MBON valence channels);
  Hige et al. 2015 Neuron 88:985-998 (dopamine-gated synaptic depression of
    KC->MBON synapses of the conditioned odor's KCs; strong, ~60-80%
    suppression after pairing).

FIXED MB CONFIGURATION (from the preregistration; loaded, not retuned):
  fc2_kc_sparse pass config tau_m_kc=20 ms, tau_syn_kc=5 ms, beta=1.0, with
  ITS calibrated theta and alpha read from results/benchmarks/
  fc2_kc_sparse.json; circuit construction, w_scale, dt=0.1 ms, 200 ms settle
  + 500 ms stimulus, Poisson PN drive at 5/100 Hz -- all verbatim from
  scripts/benchmarks/fc2_kc_sparse.py (the validated benchmark).

ASSUMED MECHANICAL CHOICES -- declared here, before any held-out valence or
accuracy number was computed. Calibration (choice 7 only) uses TRAIN games
exclusively. Everything else is a fixed rule, not fitted to anything.
  1. GAME SPLIT (ASSUMED, seeded): seeded shuffle (numpy default_rng seed
     20260929) of the 25 sorted game ids in recognizer_frames.npz; first 5 =
     TRAIN (dc22 ka59 re86 sk48 su15), next 5 = HELD-OUT (bp35 lf52 r11l
     sc25 tr87). Rationale: deterministic, declared before any run.
  2. A/B FRAME RULE (ASSUMED): (A, B) = the frame pair (i, j), 1 <= i,
     i+3 <= j <= 38, maximizing raw-pixel Hamming distance (ties: first by
     scan order). Near-variants = frames {A-1, A+1, B-1, B+1} (temporal
     neighbours, per the preregistration). Rationale: operationalizes
     "well-separated" on raw pixels only -- no circuit output involved.
  3. INPUT PLUMBING (ENGINEERED, per the preregistration's own label):
     bio-eye column features = ColumnarColourProjection.column_histogram
     (occupied 892 columns x 15 colour channels = 13,380 dims, the exact
     state_tags/click-head feature recipe), then a seeded sparse signed
     projection (density 2% = 267 features per PN, signs +-1, map seeded per
     experiment seed) onto the 627 PNs. Rationale for 2%: within the task's
     declared 1-5% band; ~267 summed features per PN gives near-Gaussian
     drive for ranking. The projection carries NO learned parameters and is
     used for RANKING only (choice 4): plumbing, not intelligence.
  4. PN RATE RULE (ASSUMED): the top 93 PNs by projected drive fire at
     100 Hz, the rest at 5 Hz -- exactly fc2_kc_sparse's odor drive
     statistics (24/162 glomerular types ~ 93/627 PN cells at 100 Hz over a
     5 Hz background), so the KC threshold operates in the regime it was
     calibrated for. This collapses the "rate scale" choice to inheritance;
     no scale is tuned in this arm. Measured in a train-game probe before
     any held-out run: KC active fraction 0.052 (inside the validated
     [0.03, 0.15] band).
  5. ELIGIBILITY (ASSUMED): a KC is eligible iff it fires >= 2 spikes in the
     500 ms stimulus window -- fc2_kc_sparse's responsive criterion, reused.
  6. VALENCE READOUT (ASSUMED): primary = time-mean synaptic current i_syn
     onto each MBON over the stimulus window, mean(approach group) -
     mean(avoid group), from a fresh presentation. Rationale: the registered
     rule reads "mean approach-MBON drive minus mean avoid-MBON drive"; and
     spike counts quantize a one-shot depression. Spike-rate valence is
     recorded alongside, unscored. Comparisons are STRICT (prereg: "correct
     iff valence(B-variant) > valence(A-variant)"); ties score incorrect.
  7. DEPRESSION FACTOR d (ASSUMED, calibrated on TRAIN only): candidates
     {0.3, 0.6, 0.9} bracketing Hige 2015's measured ~60-80% suppression;
     chosen by mean TRAIN cross-pair accuracy (5 train cells, seed 0, real
     arm), ties broken toward 0.6, then toward the larger d. Frozen before
     the first held-out presentation.
  8. MBON VALENCE SPLIT (ASSUMED, seeded per experiment seed): the MaleCNS
     MBON type names are numeric (MBON01..MBON35) and do not carry valence
     labels, so the split is the preregistration-sanctioned seeded random
     halving (48 approach / 49 avoid), re-drawn per experiment seed. The
     discrimination endpoint is INVARIANT to which half is called
     "approach": punishing A depresses A-KCs' synapses onto one half,
     rewarding B depresses B-KCs' synapses onto the other, and
     valence(B) - valence(A) has the same sign under label exchange.
  9. SEEDS (ASSUMED scheme): experiment seeds {0, 1, 2}; the projection map,
     MBON split, rewiring, and credit permutations derive from the
     experiment seed; Poisson drive streams derive from (phase, game,
     experiment seed, frame) and are SHARED across arms (paired design,
     fc2's convention) and DISTINCT between conditioning and probes
     (probes are fresh presentations).
 10. UNRELATED-STATE PROBES (secondary, unscored): the preregistration's
     "and on unrelated states" is reported for the real arm only -- frame 20
     of the next two games in the held-out rotation -- and carries no pass
     band (the registered band names only cross-pair discrimination).
 11. STATISTICS (fixed form): primary accuracy pools the 15 held-out cells'
     4 cross pairs each (n = 60 Bernoulli trials), one-sided exact binomial
     vs 0.5. Per-control comparison: paired sign test across the 15 cells'
     per-cell accuracies (ties dropped), one-sided exact binomial.

CONTROLS (all three, per the preregistration):
  C1 REWIRED: degree-preserving rewiring of the PN->KC block and the
     KC->MBON block (src/flygi/connectome/nulls.degree_preserving_rewire,
     10 swaps/edge, weights travel with edges, in/out degree sequences
     preserved exactly), everything else identical, full protocol re-run.
  C2 SHUFFLED-CREDIT: identical circuit; the 4064-dim KC eligibility vector
     is permuted (seeded) before each of the two updates.
  C3 ENGINEERED: one-shot perceptron on the same 627-dim PN rate vector,
     matched update count (2) and readout form (difference of two linear
     valence channels, zero-initialized): w_app <- -x_A (punish),
     w_avoid <- -x_B (reward), valence(x) = w_app.x - w_avoid.x
     = x.x_B - x.x_A; the learning rate cancels in every sign comparison.
     Deterministic (noise-free) inputs -- conservative in the control's
     favour.

RESOURCES (rule: measure first, one process, <= 3 GB): free RAM is measured
at launch and recorded; fc2 measured peak RSS 1237 MB for the same circuit
and engine; per-presentation cost is measured and reported (prototype:
~5.8 s per 700 ms presentation at dt 0.1 ms). ~360 presentations expected
(~40 min).
===============================================================================
"""

from __future__ import annotations

import argparse
import json
import os
import resource
import subprocess
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
from scipy.stats import binomtest  # noqa: E402

from flygi.connectome.nulls import NullOptions, degree_preserving_rewire  # noqa: E402
from flygi.connectome.subcircuit import Subcircuit, extract_subcircuit, select_nodes  # noqa: E402
from flygi.dynamics.spiking import ParameterTable, SpikingNetwork, TypeParams  # noqa: E402
from flygi.encoding.retinotopic import build_columnar_colour_projection  # noqa: E402

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
FRAMES_NPZ = ROOT / "results/diagnostics/recognizer_frames.npz"
FC2_JSON = ROOT / "results/benchmarks/fc2_kc_sparse.json"

# --- Fixed constants (see header; do not tune) --------------------------------
PN_SUBSTRINGS = ("adPN", "lPN", "vPN", "ilPN", "lvPN", "l2PN")  # fc2 verbatim
PN_FNMATCH = tuple(f"*{s}*" for s in PN_SUBSTRINGS)
FC2_CONFIG = {"tau_m_kc": 20.0, "tau_syn_kc": 5.0, "beta": 1.0}  # preregistered
DT_MS = 0.1
SETTLE_MS = 200.0
STIM_MS = 500.0
RATE_BG_HZ = 5.0
RATE_ACTIVE_HZ = 100.0
ELIGIBLE_MIN_SPIKES = 2          # fc2 responsive criterion (choice 5)
N_ACTIVE_PN = 93                 # fc2 drive statistics (choice 4)
PROJ_DENSITY = 0.02              # choice 3
SPLIT_SEED = 20260929            # choice 1
EXP_SEEDS = (0, 1, 2)            # choice 9
D_CANDIDATES = (0.3, 0.6, 0.9)  # choice 7
SEED_COND, SEED_PROBE, SEED_CREDIT = 777, 888, 555   # phase bases (choice 9)
REWIRE_SEED_BASE = 4440000
TAU_M_APL = 20.0                 # fc2 verbatim
SHIU_GAP = 7.0                   # fc2 verbatim

SETTLE_STEPS = int(round(SETTLE_MS / DT_MS))
STIM_STEPS = int(round(STIM_MS / DT_MS))

LOG_PATH = ROOT / "results" / "benchmarks" / "mb_association.log"

ASSUMED_CHOICES = [
    "game split: seeded shuffle (20260929) -> train dc22/ka59/re86/sk48/su15, heldout bp35/lf52/r11l/sc25/tr87",
    "A/B frames: max raw-pixel Hamming pair with j-i>=3 in [1,38]; variants = temporal neighbours +-1",
    "input plumbing ENGINEERED: 892x15 bio-eye column histogram -> seeded signed sparse projection (density 2%) -> PN ranking",
    "PN rates: WTA top-93 PNs at 100 Hz over 5 Hz background (fc2 odor drive statistics, inherited not tuned)",
    "eligibility: >=2 KC spikes in the 500 ms stimulus window (fc2 responsive criterion)",
    "valence readout: time-mean MBON i_syn drive, approach-mean minus avoid-mean; strict comparison, ties incorrect",
    "depression factor d: candidates {0.3,0.6,0.9}, chosen on TRAIN cells only (Hige 2015 bracket)",
    "MBON split: seeded random halving 48/49 per experiment seed (numeric type names uninformative); endpoint label-invariant",
    "seeds: experiment seeds {0,1,2}; Poisson streams shared across arms, fresh for probes",
    "unrelated-state probes: unscored, real arm only (registered band covers cross pairs only)",
    "statistics: pooled binomial n=60 one-sided; per-control paired sign test over 15 cells, ties dropped",
    "diagnostics: seed-paired PRE-conditioning baseline valences recorded (real arm), UNSCORED; scored endpoint is the raw preregistered comparison",
]


def log(message: str) -> None:
    stamp = time.strftime("%H:%M:%S")
    line = f"[{stamp}] {message}"
    print(line, flush=True)
    with LOG_PATH.open("a") as handle:
        handle.write(line + "\n")


def measure_free_ram_gb() -> float:
    """Free + inactive + speculative pages, per the resource rule."""
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True, check=True).stdout
        pages = {}
        for line in out.splitlines():
            if ":" in line:
                key, _, value = line.partition(":")
                value = value.strip().rstrip(".")
                if value.isdigit():
                    pages[key.strip()] = int(value)
        page_size = 16384
        free = pages.get("Pages free", 0) + pages.get("Pages inactive", 0) + pages.get("Pages speculative", 0)
        return free * page_size / 2**30
    except Exception:  # noqa: BLE001 -- resource probe must never kill the run
        return float("nan")


def build_subcircuit() -> Subcircuit:
    indices = select_nodes(RUNTIME_DIR, type_patterns=PN_FNMATCH + ("KC*", "APL", "MBON*"))
    return extract_subcircuit(RUNTIME_DIR, indices)


def load_fc2_pass_config() -> dict[str, float]:
    """The preregistered fixed MB configuration, from the validated benchmark."""
    fc2 = json.loads(FC2_JSON.read_text())
    for cfg in fc2["configs"]:
        if (cfg.get("tau_m_kc") == FC2_CONFIG["tau_m_kc"]
                and cfg.get("tau_syn_kc") == FC2_CONFIG["tau_syn_kc"]
                and cfg.get("beta") == FC2_CONFIG["beta"]):
            if not cfg.get("pass"):
                raise RuntimeError("preregistered fc2 config did not pass; arm invalid")
            return {
                "theta": float(cfg["calibration"]["theta"]),
                "alpha": float(cfg["alpha"]),
                "heldout_median": float(cfg["heldout"]["intact_median"]),
            }
    raise RuntimeError("preregistered fc2 config not found in fc2_kc_sparse.json")


def build_table(theta: float, alpha: float) -> ParameterTable:
    """fc2_kc_sparse's table at the preregistered config, verbatim."""
    return ParameterTable(
        default=TypeParams(
            tau_m_ms=20.0, v_thresh=SHIU_GAP, tau_syn_ms=5.0,
            provenance="ESTABLISHED (Shiu 2024 canonical: tau_m 20 ms, gap 7 mV, tau_syn 5 ms, refractory 2.2 ms)",
        ),
        rules=[
            ("APL", TypeParams(
                tau_m_ms=TAU_M_APL, v_thresh=1e9, graded=True, graded_gain=alpha,
                provenance="graded ESTABLISHED (Amin 2020); alpha = fc2 calibrated (beta=1.0)",
            )),
            ("KC*", TypeParams(
                tau_m_ms=FC2_CONFIG["tau_m_kc"], v_thresh=theta,
                tau_syn_ms=FC2_CONFIG["tau_syn_kc"],
                provenance="theta CALIBRATED by fc2_kc_sparse (Litwin-Kumar procedure); fixed here per preregistration",
            )),
        ],
    )


def frame_plan(frames: np.ndarray) -> dict[str, Any]:
    """Choice 2: the max-Hamming (A, B) pair and its temporal-neighbour variants."""
    best = (1, 4, -1)
    for i in range(1, 36):
        diff = (frames[i + 3:39] != frames[i]).sum(axis=(1, 2))
        j = int(diff.argmax())
        if int(diff[j]) > best[2]:
            best = (i, i + 3 + j, int(diff[j]))
    i, j, dist = best
    return {
        "A": i, "B": j, "hamming_ab": dist,
        "variants_a": [i - 1, i + 1], "variants_b": [j - 1, j + 1],
        "variant_hamming": {
            str(v): int((frames[v] != frames[a]).sum())
            for a, vs in ((i, (i - 1, i + 1)), (j, (j - 1, j + 1))) for v in vs
        },
    }


class Plumbing:
    """ENGINEERED input plumbing (choice 3/4): frames -> PN Poisson rates.

    Bio-eye column features (fly anatomy's retinotopic lattice) through a
    seeded signed sparse projection used only to RANK PNs; the top 93 fire at
    100 Hz, the rest at 5 Hz. No learned parameters anywhere.
    """

    def __init__(self, pn_count: int) -> None:
        self._projection = build_columnar_colour_projection(RUNTIME_DIR, 166_700)
        self._occupied = np.unique(self._projection._column_key)
        self.feature_dim = int(self._occupied.size) * 15
        self._pn_count = pn_count
        self._maps: dict[int, tuple[np.ndarray, np.ndarray]] = {}

    def features(self, grid: np.ndarray) -> np.ndarray:
        histogram = self._projection.column_histogram(np.asarray(grid, dtype=np.int8))
        return histogram[self._occupied, :].astype(np.float32).ravel()

    def map_for_seed(self, exp_seed: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Seeded projection map + MBON halving for one experiment seed."""
        if exp_seed not in self._maps:
            rng = np.random.default_rng((SPLIT_SEED, exp_seed))
            nnz = max(1, int(PROJ_DENSITY * self.feature_dim))
            cols = rng.integers(0, self.feature_dim, size=(self._pn_count, nnz))
            signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=cols.shape)
            split = rng.permutation(97)
            self._maps[exp_seed] = (cols, signs, split)
        return self._maps[exp_seed]

    def pn_rates(self, grid: np.ndarray, exp_seed: int) -> np.ndarray:
        cols, signs, _ = self.map_for_seed(exp_seed)
        drive = (self.features(grid)[cols] * signs).sum(axis=1)
        top = np.argpartition(-drive, N_ACTIVE_PN - 1)[:N_ACTIVE_PN]
        rates = np.full(self._pn_count, RATE_BG_HZ, dtype=np.float64)
        rates[top] = RATE_ACTIVE_HZ
        return rates


def kc_mbon_edge_index(matrix: sparse.csr_matrix, kc_idx: np.ndarray,
                       mbon_idx: np.ndarray) -> dict[str, np.ndarray]:
    """Flat positions into matrix.data of every positive KC->MBON edge.

    Depression only rescales existing values (never restructures), so these
    positions stay valid for every .copy() of the same structure -- the REAL
    synaptic mask, per the preregistration.
    """
    kc_local = np.full(matrix.shape[0], -1, dtype=np.int64)
    kc_local[kc_idx] = np.arange(kc_idx.size)
    mbon_flag = np.zeros(matrix.shape[0], dtype=bool)
    mbon_flag[mbon_idx] = True
    pos_list, kc_list, mbon_list = [], [], []
    for local, row in enumerate(mbon_idx):
        start, end = matrix.indptr[row], matrix.indptr[row + 1]
        cols = matrix.indices[start:end]
        data = matrix.data[start:end]
        hit = (kc_local[cols] >= 0) & (data > 0)
        pos_list.append(np.arange(start, end)[hit])
        kc_list.append(kc_local[cols[hit]])
        mbon_list.append(np.full(int(hit.sum()), local, dtype=np.int64))
    return {
        "data_pos": np.concatenate(pos_list),
        "kc_local": np.concatenate(kc_list),
        "mbon_local": np.concatenate(mbon_list),
    }


def depress(working: sparse.csr_matrix, index: dict[str, np.ndarray],
            eligibility: np.ndarray, mbon_group_flag: np.ndarray, factor: float) -> int:
    """One-shot DAN-gated depression (Aso et al. 2014 eLife 3:e04577; Hige et
    al. 2015 Neuron 88:985-998): multiplicative depression of EXISTING
    KC->MBON synapses of eligible KCs onto the gated valence channel. Never
    creates a synapse; operates on the real mask only."""
    hit = eligibility[index["kc_local"]] & mbon_group_flag[index["mbon_local"]]
    working.data[index["data_pos"][hit]] *= np.float32(1.0 - factor)
    return int(hit.sum())


class Circuit:
    """One arm's circuit: base matrix + populations + fixed dynamics params."""

    def __init__(self, matrix: sparse.csr_matrix, types: np.ndarray,
                 pn_idx: np.ndarray, kc_idx: np.ndarray, apl_idx: np.ndarray,
                 mbon_idx: np.ndarray, table: ParameterTable, w_scale: float) -> None:
        self.matrix = matrix
        self.types = types
        self.pn_idx, self.kc_idx = pn_idx, kc_idx
        self.apl_idx, self.mbon_idx = apl_idx, mbon_idx
        self.table = table
        self.w_scale = w_scale
        self.edge_index = kc_mbon_edge_index(matrix, kc_idx, mbon_idx)


def present(circuit: Circuit, matrix: sparse.csr_matrix, rates: np.ndarray,
            drive_seed: tuple[int, ...], gate: bool = False) -> dict[str, Any]:
    """One 200 ms settle + 500 ms stimulus presentation (fc2 protocol verbatim:
    PNs are clamped Poisson spike sources; overwrite after each step)."""
    net = SpikingNetwork(matrix, circuit.types, circuit.table, dt_ms=DT_MS,
                         w_scale=circuit.w_scale)
    rng = np.random.default_rng(drive_seed)
    pn_idx, kc_idx, mbon_idx = circuit.pn_idx, circuit.kc_idx, circuit.mbon_idx
    p_bg = np.full(pn_idx.size, RATE_BG_HZ * DT_MS / 1000.0)
    p_stim = rates * DT_MS / 1000.0
    probability = p_bg
    kc_spikes = np.zeros(kc_idx.size, dtype=np.int64)
    mbon_spikes = np.zeros(mbon_idx.size, dtype=np.int64)
    mbon_isyn = np.zeros(mbon_idx.size, dtype=np.float64)
    if gate:
        kc_rows = matrix[kc_idx]
        w_pos_all = kc_rows.maximum(0).tocsr()
        w_pos_pn = w_pos_all[:, pn_idx].tocsr()
        pn_drive_sum, total_drive_sum = 0.0, 0.0
    for step in range(SETTLE_STEPS + STIM_STEPS):
        if step == SETTLE_STEPS:
            probability = p_stim
        net.step(None)
        if step >= SETTLE_STEPS:
            kc_spikes += net.last_output[kc_idx] > 0
            mbon_spikes += net.last_output[mbon_idx] > 0
            mbon_isyn += net.i_syn[mbon_idx]
        net.last_output[pn_idx] = (rng.random(pn_idx.size) < probability).astype(np.float32)
        if gate and step >= SETTLE_STEPS:
            vec = net.last_output
            pn_drive_sum += float((w_pos_pn @ vec[pn_idx]).sum())
            total_drive_sum += float((w_pos_all @ vec).sum())
    result: dict[str, Any] = {
        "kc_spikes": kc_spikes,
        "kc_active_fraction": float((kc_spikes >= ELIGIBLE_MIN_SPIKES).mean()),
        "mbon_isyn_mean": mbon_isyn / STIM_STEPS,
        "mbon_rate_hz": mbon_spikes / (STIM_MS / 1000.0),
    }
    if gate:
        result["pn_share_of_kc_drive"] = (
            pn_drive_sum / total_drive_sum if total_drive_sum > 0 else float("nan")
        )
    return result


def valence(mbon_isyn_mean: np.ndarray, split: np.ndarray) -> float:
    approach, avoid = split[:48], split[48:]
    return float(mbon_isyn_mean[approach].mean() - mbon_isyn_mean[avoid].mean())


def valence_rate(mbon_rate: np.ndarray, split: np.ndarray) -> float:
    approach, avoid = split[:48], split[48:]
    return float(mbon_rate[approach].mean() - mbon_rate[avoid].mean())


def run_cell(circuit: Circuit, plumbing: Plumbing, frames: np.ndarray,
             plan: dict[str, Any], game_index: int, exp_seed: int, factor: float,
             shuffle_credit: bool, gate: bool, timings: list[float],
             unrelated: list[tuple[str, np.ndarray, tuple[int, ...]]] | None = None,
             baseline: bool = False) -> dict[str, Any]:
    """One (game, seed) cell for one spiking arm: sequential one-shot
    conditioning (A-punish then B-reward) and four fresh cross-pair probes."""
    _, _, split = plumbing.map_for_seed(exp_seed)
    approach_flag = np.zeros(97, dtype=bool)
    approach_flag[split[:48]] = True
    avoid_flag = ~approach_flag
    credit_rng = np.random.default_rng((SEED_CREDIT, game_index, exp_seed))
    working = circuit.matrix.copy()
    record: dict[str, Any] = {"depressed_edges": [], "eligible_counts": [],
                              "kc_active_fractions": {}}

    def timed_present(matrix: sparse.csr_matrix, frame_i: int,
                      seed: tuple[int, ...], want_gate: bool = False) -> dict[str, Any]:
        t0 = time.time()
        out = present(circuit, matrix, plumbing.pn_rates(frames[frame_i], exp_seed),
                      seed, gate=want_gate)
        timings.append(time.time() - t0)
        record["kc_active_fractions"][str(frame_i)] = out["kc_active_fraction"]
        return out

    if baseline:
        # UNSCORED diagnostic (fc2's report-alongside convention): the same
        # probe presentations, same Poisson seeds, on the PRE-conditioning
        # matrix -- separates the learning-induced valence shift from the
        # stimulus-identity baseline. The scored endpoint below stays the
        # preregistered raw comparison; nothing here feeds a choice.
        base_valence = {}
        for v in plan["variants_a"] + plan["variants_b"]:
            out = timed_present(working, v, (SEED_PROBE, game_index, exp_seed, v))
            base_valence[str(v)] = valence(out["mbon_isyn_mean"], split)
        record["probe_valence_baseline_unscored"] = base_valence

    for anchor, channel_flag, phase in ((plan["A"], approach_flag, 0),
                                        (plan["B"], avoid_flag, 1)):
        out = timed_present(working, anchor, (SEED_COND, game_index, exp_seed, phase),
                            want_gate=gate and phase == 0)
        if gate and phase == 0:
            record["pn_share_of_kc_drive"] = out["pn_share_of_kc_drive"]
        eligibility = out["kc_spikes"] >= ELIGIBLE_MIN_SPIKES
        if shuffle_credit:
            # CONTROL C2: permute the eligibility vector before the update.
            eligibility = eligibility[credit_rng.permutation(eligibility.size)]
        record["eligible_counts"].append(int(eligibility.sum()))
        record["depressed_edges"].append(
            depress(working, circuit.edge_index, eligibility, channel_flag, factor)
        )

    probe_valence: dict[str, float] = {}
    probe_valence_rate: dict[str, float] = {}
    for v in plan["variants_a"] + plan["variants_b"]:
        out = timed_present(working, v, (SEED_PROBE, game_index, exp_seed, v))
        probe_valence[str(v)] = valence(out["mbon_isyn_mean"], split)
        probe_valence_rate[str(v)] = valence_rate(out["mbon_rate_hz"], split)
    correct = [
        bool(probe_valence[str(bv)] > probe_valence[str(av)])
        for av in plan["variants_a"] for bv in plan["variants_b"]
    ]
    record.update({
        "probe_valence": probe_valence,
        "probe_valence_rate_unscored": probe_valence_rate,
        "pairs_correct": correct,
        "accuracy": float(np.mean(correct)),
    })
    if unrelated:
        # Choice 10: unrelated states on the conditioned matrix, unscored.
        unscored = {}
        for label, grid, probe_seed in unrelated:
            t0 = time.time()
            out = present(circuit, working, plumbing.pn_rates(grid, exp_seed), probe_seed)
            timings.append(time.time() - t0)
            unscored[label] = valence(out["mbon_isyn_mean"], split)
        record["unrelated_valence_unscored"] = unscored
    return record


def engineered_cell(plumbing: Plumbing, frames: np.ndarray, plan: dict[str, Any],
                    exp_seed: int) -> dict[str, Any]:
    """CONTROL C3: one-shot perceptron, same 627-dim PN input, matched update
    count and readout form (see header)."""
    x = {i: plumbing.pn_rates(frames[i], exp_seed)
         for i in [plan["A"], plan["B"]] + plan["variants_a"] + plan["variants_b"]}
    x_a, x_b = x[plan["A"]], x[plan["B"]]
    val = {str(i): float(x[i] @ x_b - x[i] @ x_a)
           for i in plan["variants_a"] + plan["variants_b"]}
    correct = [
        bool(val[str(bv)] > val[str(av)])
        for av in plan["variants_a"] for bv in plan["variants_b"]
    ]
    return {"probe_valence": val, "pairs_correct": correct,
            "accuracy": float(np.mean(correct))}


def rewired_circuit(base: Circuit, exp_seed: int) -> tuple[Circuit, dict[str, Any]]:
    """CONTROL C1: degree-preserving rewiring of PN->KC and KC->MBON blocks."""
    matrix = base.matrix.tocoo()
    n = matrix.shape[0]
    pn_flag = np.zeros(n, dtype=bool); pn_flag[base.pn_idx] = True
    kc_flag = np.zeros(n, dtype=bool); kc_flag[base.kc_idx] = True
    mbon_flag = np.zeros(n, dtype=bool); mbon_flag[base.mbon_idx] = True
    stats: dict[str, Any] = {}
    keep = np.ones(matrix.nnz, dtype=bool)
    blocks = []
    for name, pre_flag, post_flag in (("pn_kc", pn_flag, kc_flag),
                                      ("kc_mbon", kc_flag, mbon_flag)):
        in_block = pre_flag[matrix.col] & post_flag[matrix.row]
        keep &= ~in_block
        block = sparse.csr_matrix(
            (matrix.data[in_block], (matrix.row[in_block], matrix.col[in_block])),
            shape=(n, n), dtype=np.float32)
        rewired, st = degree_preserving_rewire(
            block, seed=REWIRE_SEED_BASE + 10 * exp_seed + (0 if name == "pn_kc" else 1),
            options=NullOptions(kind="degree_preserving"))
        rw = rewired.tocoo()
        if not (pre_flag[rw.col].all() and post_flag[rw.row].all()):
            raise RuntimeError(f"rewired {name} block escaped its bipartite frame")
        for axis, flag in ((0, post_flag), (1, pre_flag)):
            before = np.asarray((block != 0).sum(axis=1 - axis)).ravel()
            after = np.asarray((rewired != 0).sum(axis=1 - axis)).ravel()
            if not np.array_equal(before, after):
                raise RuntimeError(f"rewiring {name} changed a degree sequence")
        stats[name] = {k: st[k] for k in ("edges", "accepted_swaps", "swaps_per_edge_achieved", "acceptance_rate")}
        blocks.append(rewired)
    kept = sparse.csr_matrix(
        (matrix.data[keep], (matrix.row[keep], matrix.col[keep])), shape=(n, n),
        dtype=np.float32)
    combined = (kept + blocks[0] + blocks[1]).tocsr()
    combined.sort_indices()
    if combined.nnz != base.matrix.nnz:
        raise RuntimeError("rewired reassembly changed the total edge count")
    return Circuit(combined, base.types, base.pn_idx, base.kc_idx, base.apl_idx,
                   base.mbon_idx, base.table, base.w_scale), stats


def sign_test(real: list[float], control: list[float]) -> dict[str, Any]:
    wins = sum(1 for r, c in zip(real, control) if r > c)
    losses = sum(1 for r, c in zip(real, control) if r < c)
    ties = len(real) - wins - losses
    n = wins + losses
    p = float(binomtest(wins, n, 0.5, alternative="greater").pvalue) if n else 1.0
    return {"wins": wins, "losses": losses, "ties": ties, "p": p}


def main() -> int:
    parser = argparse.ArgumentParser(description="H-MB-CLASS2-ASSOCIATION stage A")
    parser.add_argument("--output", type=Path,
                        default=ROOT / "results" / "benchmarks" / "mb_association.json")
    parser.add_argument("--quick", action="store_true",
                        help="mechanics smoke test on TRAIN games only; never a verdict")
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not args.quick:
        LOG_PATH.write_text("")

    t_start = time.time()
    free_gb = measure_free_ram_gb()
    log(f"free RAM {free_gb:.1f} GB (rule: single process <= 3 GB)")
    if free_gb == free_gb and free_gb < 3.5:
        log("ABORT: less than 3.5 GB reclaimable RAM measured")
        return 1

    fc2 = load_fc2_pass_config()
    theta, alpha = fc2["theta"], fc2["alpha"]
    log(f"preregistered MB config: tau_m 20 / tau_syn 5 / beta 1.0 -> theta {theta:.4f}, alpha {alpha:.4e}")

    sub = build_subcircuit()
    types = sub.types
    pn_mask = np.zeros(types.size, dtype=bool)
    for substring in PN_SUBSTRINGS:
        pn_mask |= np.char.find(types, substring) >= 0
    pn_idx = np.flatnonzero(pn_mask)
    kc_idx = np.flatnonzero(np.char.startswith(types, "KC"))
    apl_idx = np.flatnonzero(types == "APL")
    mbon_idx = np.flatnonzero(np.char.startswith(types, "MBON"))
    if pn_idx.size != 627 or kc_idx.size != 4064 or apl_idx.size != 2 or mbon_idx.size != 97:
        raise RuntimeError(
            f"population counts changed: PN {pn_idx.size}/627, KC {kc_idx.size}/4064, "
            f"APL {apl_idx.size}/2, MBON {mbon_idx.size}/97")
    pn_kc = sub.matrix[kc_idx][:, pn_idx]
    w_scale = 1.0 / float(pn_kc.data[pn_kc.data > 0].mean())
    matrix = sub.matrix.tocsr().copy()
    matrix.sort_indices()
    table = build_table(theta, alpha)
    real = Circuit(matrix, types, pn_idx, kc_idx, apl_idx, mbon_idx, table, w_scale)
    kc_mbon_edges = real.edge_index["data_pos"].size
    log(f"subcircuit {sub.node_count} nodes / {matrix.nnz} edges; "
        f"w_scale {w_scale:.5f}; positive KC->MBON edges {kc_mbon_edges}")

    with np.load(FRAMES_NPZ) as archive:
        all_games = sorted(archive.files)
        frames_by_game = {g: archive[g].copy() for g in all_games}
    split_rng = np.random.default_rng(SPLIT_SEED)
    order = split_rng.permutation(len(all_games))
    train_games = sorted(all_games[i] for i in order[:5])
    heldout_games = sorted(all_games[i] for i in order[5:10])
    game_index = {g: i for i, g in enumerate(all_games)}
    plans = {g: frame_plan(frames_by_game[g]) for g in train_games + heldout_games}
    log(f"train games {train_games}; held-out games {heldout_games}")

    plumbing = Plumbing(pn_idx.size)
    timings: list[float] = []

    results: dict[str, Any] = {
        "script": "scripts/benchmarks/mb_association.py",
        "arm": "H-MB-CLASS2-ASSOCIATION.stageA",
        "preregistration": "EXPERIMENTS.yaml H-MB-CLASS2-ASSOCIATION (2026-09-29); restated verbatim in the script header",
        "pass_bands": "held-out accuracy > 0.5 binomial p < 0.05 AND real > each control, paired sign test p < 0.05 over 15 cells",
        "fixed_mb_config": {**FC2_CONFIG, "theta": theta, "alpha": alpha,
                            "fc2_heldout_median": fc2["heldout_median"],
                            "w_scale": w_scale, "dt_ms": DT_MS,
                            "settle_ms": SETTLE_MS, "stim_ms": STIM_MS},
        "assumed_choices": ASSUMED_CHOICES,
        "quick_mode": bool(args.quick),
        "free_ram_gb_at_launch": free_gb,
        "subcircuit": {"nodes": int(sub.node_count), "edges": int(matrix.nnz),
                       "pn": 627, "kc": 4064, "apl": 2, "mbon": 97,
                       "positive_kc_mbon_edges": int(kc_mbon_edges)},
        "games": {"train": train_games, "heldout": heldout_games},
        "frame_plans": plans,
        "train_calibration": {},
        "cells": [],
    }

    def save() -> None:
        tmp = args.output.with_suffix(".tmp")
        tmp.write_text(json.dumps(results, indent=2, default=float))
        os.replace(tmp, args.output)

    save()

    # --- TRAIN calibration of d (choice 7; train games only, real arm) --------
    cal_games = train_games[:1] if args.quick else train_games
    cal_candidates = D_CANDIDATES[:1] if args.quick else D_CANDIDATES
    cal_table: dict[str, Any] = {}
    for d in cal_candidates:
        accs = []
        for g in cal_games:
            cell = run_cell(real, plumbing, frames_by_game[g], plans[g],
                            game_index[g], 0, d, shuffle_credit=False, gate=False,
                            timings=timings)
            accs.append(cell["accuracy"])
            log(f"train d={d} {g}: accuracy {cell['accuracy']:.2f} "
                f"(elig {cell['eligible_counts']}, depressed {cell['depressed_edges']})")
        cal_table[str(d)] = {"accuracies": accs, "mean": float(np.mean(accs))}
        results["train_calibration"] = {"table": cal_table}
        save()
    best_mean = max(v["mean"] for v in cal_table.values())
    tied = [float(k) for k, v in cal_table.items() if v["mean"] == best_mean]
    d_star = min(tied, key=lambda d: (abs(d - 0.6), -d))
    results["train_calibration"] = {
        "table": cal_table, "d_star": d_star,
        "rule": "max mean train accuracy; ties -> closest to 0.6, then larger",
    }
    log(f"TRAIN calibration: d* = {d_star} (means "
        f"{ {k: round(v['mean'], 3) for k, v in cal_table.items()} }); frozen before held-out")
    save()

    # --- HELD-OUT cells: real + all three controls ----------------------------
    eval_games = train_games[:1] if args.quick else heldout_games
    eval_seeds = (0,) if args.quick else EXP_SEEDS
    rewired_cache: dict[int, tuple[Circuit, dict[str, Any]]] = {}
    for exp_seed in eval_seeds:
        rewired_cache[exp_seed] = rewired_circuit(real, exp_seed)
        log(f"seed {exp_seed}: rewired control built "
            f"{ {k: v['accepted_swaps'] for k, v in rewired_cache[exp_seed][1].items()} } swaps")
    results["rewiring_stats"] = {str(s): st for s, (_, st) in rewired_cache.items()}

    for exp_seed in eval_seeds:
        for g in eval_games:
            t_cell = time.time()
            gi, plan, frames = game_index[g], plans[g], frames_by_game[g]
            cell: dict[str, Any] = {"game": g, "seed": exp_seed, "heldout": not args.quick}
            unrelated = None
            if not args.quick:
                pos = heldout_games.index(g)
                unrelated = [
                    (f"{other}:20", frames_by_game[other][20],
                     (SEED_PROBE, gi, exp_seed, 1000 + game_index[other]))
                    for other in (heldout_games[(pos + 1) % 5], heldout_games[(pos + 2) % 5])
                ]
            cell["real"] = run_cell(real, plumbing, frames, plan, gi, exp_seed,
                                    d_star, shuffle_credit=False, gate=True,
                                    timings=timings, unrelated=unrelated,
                                    baseline=not args.quick)
            rw_circuit, _ = rewired_cache[exp_seed]
            cell["control_rewired"] = run_cell(rw_circuit, plumbing, frames, plan,
                                               gi, exp_seed, d_star,
                                               shuffle_credit=False, gate=False,
                                               timings=timings)
            cell["control_shuffled_credit"] = run_cell(real, plumbing, frames, plan,
                                                       gi, exp_seed, d_star,
                                                       shuffle_credit=True, gate=False,
                                                       timings=timings)
            cell["control_engineered"] = engineered_cell(plumbing, frames, plan, exp_seed)
            cell["seconds"] = round(time.time() - t_cell, 1)
            results["cells"].append(cell)
            save()
            log(f"cell {g}/seed{exp_seed}: real {cell['real']['accuracy']:.2f} "
                f"rewired {cell['control_rewired']['accuracy']:.2f} "
                f"shuffled {cell['control_shuffled_credit']['accuracy']:.2f} "
                f"engineered {cell['control_engineered']['accuracy']:.2f} "
                f"({cell['seconds']}s)")

    # --- Verdict against the preregistered bands ------------------------------
    cells = results["cells"]
    arms = ("real", "control_rewired", "control_shuffled_credit", "control_engineered")
    pooled = {}
    for arm in arms:
        flat = [p for c in cells for p in c[arm]["pairs_correct"]]
        pooled[arm] = {"correct": int(np.sum(flat)), "n": len(flat),
                       "accuracy": float(np.mean(flat))}
    k, n = pooled["real"]["correct"], pooled["real"]["n"]
    binom_p = float(binomtest(k, n, 0.5, alternative="greater").pvalue)
    per_cell = {arm: [c[arm]["accuracy"] for c in cells] for arm in arms}
    tests = {
        "binomial_real_vs_chance": {"correct": k, "n": n, "p": binom_p},
        "sign_real_vs_rewired": sign_test(per_cell["real"], per_cell["control_rewired"]),
        "sign_real_vs_shuffled_credit": sign_test(per_cell["real"], per_cell["control_shuffled_credit"]),
        "sign_real_vs_engineered": sign_test(per_cell["real"], per_cell["control_engineered"]),
    }
    passed = bool(
        pooled["real"]["accuracy"] > 0.5 and binom_p < 0.05
        and all(tests[f"sign_real_vs_{c}"]["p"] < 0.05
                for c in ("rewired", "shuffled_credit", "engineered"))
    )
    results["pooled_accuracy"] = pooled
    results["paired_tests"] = tests
    results["verdict"] = {
        "passed": passed and not args.quick,
        "band_1_accuracy": {"value": pooled["real"]["accuracy"],
                            "required": "> 0.5 with binomial p < 0.05",
                            "p": binom_p,
                            "holds": bool(pooled["real"]["accuracy"] > 0.5 and binom_p < 0.05)},
        "band_2_controls": {c: {"p": tests[f"sign_real_vs_{c}"]["p"],
                                "holds": bool(tests[f"sign_real_vs_{c}"]["p"] < 0.05)}
                            for c in ("rewired", "shuffled_credit", "engineered")},
    }
    per_presentation_ms = float(np.mean(timings) * 1000.0) if timings else float("nan")
    results["per_presentation_cost_ms"] = per_presentation_ms
    results["presentations"] = len(timings)
    results["peak_rss_mb"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20)
    results["total_seconds"] = round(time.time() - t_start, 1)
    save()
    log(json.dumps(results["verdict"], indent=2))
    log(f"pooled: " + ", ".join(f"{a} {pooled[a]['accuracy']:.3f}" for a in arms))
    log(f"done in {results['total_seconds']}s, {len(timings)} presentations at "
        f"{per_presentation_ms:.0f} ms each, peak RSS {results['peak_rss_mb']} MB -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
