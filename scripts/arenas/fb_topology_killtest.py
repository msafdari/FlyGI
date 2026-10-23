#!/usr/bin/env python3
"""H-FB-COLUMNAR-TOPOLOGY -- the Task 10 fan-shaped-body structural probe
(Stage-A analog).

PREREGISTRATION (docs/arenas/task10_menu/killtest_design.md section 4,
frozen 2026-10-23 BEFORE this file existed; restated, not changed):

  - PREMISE (structure only, the Stage-A scope rule -- no computation
    claim at any outcome): the MaleCNS v1.0 FB columnar wiring
    structurally encodes the published vector-computation geometry:
    (i) coupling routed through hDelta concentrates at half-width
    (~180 deg) FB-column offsets, and (ii) left-PB vs right-PB PFN
    populations project into FB columns at OPPOSITE-signed angular
    offsets -- and degree-preserving rewires destroy both.
  - COMPOSITION (frozen table, MEASURED in-cloud from the raw release
    annotations, due_diligence.md): PFNa 58, PFNd 40, PFNm_a 21,
    PFNm_b 26, PFNp_a 64, PFNp_b 136, PFNp_c 40, PFNp_d 28, PFNp_e 23,
    PFNv 20, hDelta 189, vDelta 430, FC 274, PFL1 14, PFL2 12, PFL3 24.
    BLOCKED on any deviation. (The registration's noduli context row
    4/2/2/4/2/2 names no types, so the noduli are not extracted here;
    recorded as a resolved ambiguity in the build report.)
  - COORDINATES (AC-FB1..4): _C column labels on a common azimuthal
    frame, angle = 2*pi*(c-0.5)/N_type with N_type the type row's own
    observed column count (in-cloud baselines: FC 9, hDelta 12, vDelta
    10 incl. C0); PFN instance glomerulus digits 2-9 + L/R in the
    Stage-A PB frame (each side's 8 glomeruli span 360 deg, mirrored);
    hDelta a/b sub-column suffixes collapse to the numeric column;
    _irreg cells kept and flagged.
  - BAR 1 (hDelta antipode): W2 = relu(W[FC<-hDelta]) @
    relu(W[hDelta<-labelled-PFN]), aggregated by (FC column angle, PFN
    column angle) as mean cell-pair coupling (Stage-A aggregation);
    statistic A = mass fraction at circular angular distance within ONE
    40-deg sector of 180 deg, i.e. distance in [160, 180] deg. IN = the
    five labelled PFN types (163 column-labelled cells in the frozen
    baseline), OUT = FC (274).
  - BAR 2 (PFN mirror): per hemisphere, one-hop W[FC<-PFN_side]
    aggregated into (FC column angle - PB glomerulus angle) offset
    profiles q_L, q_R; S = max_d max(q_L(d) q_R(-d), q_L(-d) q_R(d)),
    computed by mirror_peak imported VERBATIM from
    cx_topology_killtest.py (never re-implemented) on the Stage-A
    16-bin (22.5 deg) offset frame; d scans 1..7 bins, offset 0 and the
    antipode bin excluded per the Stage-A verbatim semantics. The
    registered motif (one-sector = 40-deg offsets ~ bins +/-2) lies
    inside the scanned domain.
  - NULLS: 200 degree-preserving rewires of the full extracted FB
    subcircuit (flygi.connectome.nulls.degree_preserving_rewire, seeds
    4242+0..199), identical pipeline; one-sided empirical
    p = (1 + k)/201 (floor 0.00498), alpha 0.05.
  - PASS iff BOTH bars beat the nulls at p < 0.05; KILL otherwise.
    CONTEXT, non-decisional: PFL and vDelta offset profiles, reported.
  - COVERAGE floor 0.90 on every bar-coordinate population (in-cloud
    raw baselines: FC 100%, hDelta 98.9%, labelled-PFN 98.8%; context
    baselines vDelta 100%, PFL 100% reported, non-blocking -- PFL and
    vDelta are declared non-decisional context populations).
  - BLOCKED (exit 3): (1) runtime absent (cloud always blocks);
    (2) compiled per-type counts deviate from the frozen composition
    table; (3) column/glomerulus coverage < 0.90 on any bar population
    (AC-FB6); (4) degenerate zero-mass two-hop/one-hop for any bar
    statistic; (5) synthetic gate failing either direction.
  - VALIDATION GATE (in-cloud, pre-data; the AC-4 pattern): idealized
    Hulse-motif FB circuit (9-column FC frame; per side 8 PFN glomeruli
    projecting at opposite-signed one-sector offsets; hDelta half-width
    connectivity): both bars must PASS on the ideal at the empirical
    floor AND its own degree-preserving rewire must KILL both. Asserted
    by unit test before any data contact, and evaluated at run time
    before the extraction touches data (floor 5).

Data gate: runs where the compiled runtime lives (the cloud container
lacks it). The PIPELINE itself is pure and is validated in-cloud on the
idealized circuit, including against the real rewire machinery, before
any data contact.

Run:    python scripts/arenas/fb_topology_killtest.py
Output: results/arenas/fb_topology_killtest.json (+ .log)
"""

from __future__ import annotations

import argparse
import fnmatch
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

# --- Stage-A machinery, imported from the Stage-A module (VERBATIM reuse;
#     the registration forbids re-implementation of mirror_peak) ----------
_CX_PATH = Path(__file__).resolve().parent / "cx_topology_killtest.py"
if "cx_topology_killtest" in sys.modules:
    _cx = sys.modules["cx_topology_killtest"]
else:
    _spec = importlib.util.spec_from_file_location("cx_topology_killtest", _CX_PATH)
    _cx = importlib.util.module_from_spec(_spec)
    sys.modules["cx_topology_killtest"] = _cx
    _spec.loader.exec_module(_cx)

mirror_peak = _cx.mirror_peak    # Bar 2 statistic -- Stage-A VERBATIM
relu_dense = _cx.relu_dense
empirical_p = _cx.empirical_p

# --- frozen constants (killtest_design.md section 4; do not tune) ----------
N_NULLS = 200
REWIRE_SEED_BASE = 4242
ALPHA = 0.05
MIN_COVERAGE = 0.90
SECTOR_DEG = 40.0            # one FC sector: 360/9 from the frozen FC frame
ANTIPODE_DEG = 180.0
# Stage-A offset frame reused, not retuned: 16 bins of 22.5 deg, so the
# verbatim mirror_peak scans the same d = 1..7 domain it was validated on.
N_OFFSET_BINS = int(_cx.N_WEDGES)
GLOM_MIN, GLOM_MAX, N_GLOMS = 2, 9, 8
GATE_BREAK_SEED = 7          # the Stage-A destroyed-arm precedent seed
GATE_BUILD_SEED = 0
GATE_NOISE = 0.01

# Frozen composition table (MEASURED in-cloud, due_diligence.md; row grain
# is the registration's own table grain: per-type for PFN and PFL, family
# totals for hDelta / vDelta / FC).
COMPOSITION = {
    "PFNa": 58, "PFNd": 40, "PFNm_a": 21, "PFNm_b": 26,
    "PFNp_a": 64, "PFNp_b": 136, "PFNp_c": 40, "PFNp_d": 28, "PFNp_e": 23,
    "PFNv": 20,
    "hDelta": 189, "vDelta": 430, "FC": 274,
    "PFL1": 14, "PFL2": 12, "PFL3": 24,
}
ROW_PATTERNS = {
    "PFNa": "PFNa*", "PFNd": "PFNd*", "PFNm_a": "PFNm_a*",
    "PFNm_b": "PFNm_b*", "PFNp_a": "PFNp_a*", "PFNp_b": "PFNp_b*",
    "PFNp_c": "PFNp_c*", "PFNp_d": "PFNp_d*", "PFNp_e": "PFNp_e*",
    "PFNv": "PFNv*",
    "hDelta": "hDelta*", "vDelta": "vDelta*", "FC": "FC[123]*",
    "PFL1": "PFL1*", "PFL2": "PFL2*", "PFL3": "PFL3*",
}
# IN populations of both bars: the five labelled PFN types (163
# column-labelled cells of 165 in the frozen in-cloud baseline).
LABELLED_PFN_ROWS = ("PFNa", "PFNd", "PFNm_a", "PFNm_b", "PFNv")
PFL_ROWS = ("PFL1", "PFL2", "PFL3")
TYPE_PATTERNS = tuple(ROW_PATTERNS.values())

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
RAW_WEIGHTS = ROOT / "data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather"
OUT_JSON = ROOT / "results/arenas/fb_topology_killtest.json"

# AC-FB3 (ASSUMED, registered): hDelta a/b sub-column suffixes collapse to
# the numeric column -- the regex takes the digits and drops any trailing
# letter. Check: list distinct suffixes in the annotations; breaks if a/b
# sub-columns are anatomically distinct half-columns rather than split
# bodies of one column (Bar 1 would blur by at most half a column).
COLUMN_RE = re.compile(r"_C(\d+)")
GLOM_RE = re.compile(r"_([LR])(\d)")
IRREG_MARK = "_irreg"


# ---------------------------------------------------------------------------
# Pure plumbing (unit-tested in-cloud on the idealized Hulse-motif circuit)
# ---------------------------------------------------------------------------

def fb_column(instance: str):
    """_C<digits>[a|b] -> numeric column, else None (AC-FB3 collapse)."""
    match = COLUMN_RE.search(instance)
    if not match:
        return None
    return int(match.group(1))


def pb_glomerulus(instance: str):
    """_L<g>/_R<g> with g in 2..9 -> (side, g), else None.

    The registration pins PFN glomerulus digits to 2-9 (8 per side);
    anything else does not parse, mirroring the Stage-A wedge parser.
    """
    match = GLOM_RE.search(instance)
    if not match:
        return None
    side, glom = match.group(1), int(match.group(2))
    if not GLOM_MIN <= glom <= GLOM_MAX:
        return None
    return side, glom


def column_angle_deg(column: int, n_columns: int) -> float:
    """AC-FB1 (ASSUMED, registered): _C column labels live on a common
    azimuthal frame, angle = 360*(c-0.5)/N_type with N_type the type
    row's own observed distinct-column count (Stage-A AC-1 analog). The
    frame assumes near-contiguous column indexing; angles are wrapped so
    a gap in the indexing cannot push an angle off the circle. Check:
    compare against an independent FB column-to-azimuth map if one is
    published for MaleCNS. Breaks: both bars lose their geometric
    meaning if MaleCNS _C labels are not an azimuthal column order.
    """
    return ((column - 0.5) * 360.0 / n_columns) % 360.0


def glom_angle_deg(side: str, glom: int) -> float:
    """AC-FB2 (ASSUMED, registered): PB-glomerulus/EPG-wedge frame
    concordance. Each side's 8 glomeruli (digits 2-9) span 360 deg at
    45-deg spacing, and the two sides are MIRRORED (here: R increases
    with the digit, L decreases). Which side is reversed is inert --
    mirror_peak's two-term max is invariant under swapping the reversed
    side -- and the shared anchor (digit 2 at 0 deg) rotates the two
    frames oppositely, which preserves the mirror pairing. The binding
    assumption is the mirrored-pair structure itself plus the glomerulus
    numbering tracking the heading frame. Check: derive the PB map from
    EPG/Delta7 innervation in the annotations. Breaks: Bar 2 loses the
    mirror signal (false KILL direction), never gains one.
    """
    base = (glom - GLOM_MIN) * 360.0 / N_GLOMS
    return base if side == "R" else (360.0 - base) % 360.0


def wrap_deg(delta) -> np.ndarray:
    """Wrap signed degree differences into (-180, 180]."""
    d = np.asarray(delta, dtype=np.float64) % 360.0
    return np.where(d > 180.0, d - 360.0, d)


def circ_dist_deg(a, b) -> np.ndarray:
    return np.abs(wrap_deg(np.asarray(a) - np.asarray(b)))


def two_hop_rect(W, out_idx: np.ndarray, mid_idx: np.ndarray,
                 in_idx: np.ndarray) -> np.ndarray:
    """relu(W[out<-mid]) @ relu(W[mid<-in]) with W[post, pre] throughout.

    AC-FB5 (MEASURED, registered): the bar populations (PFN, hDelta; FC
    inputs scored downstream of them) are consensus-acetylcholine, so
    relu keeps their outputs -- relu is the Stage-A mechanical choice,
    not a new invention. Check: the run-time consensus_nt audit of the
    extracted subcircuit (reported in the record). Breaks: if a bar
    population were measured inhibitory, relu would silently delete its
    coupling and Bar 1/2 would read zero mass (a BLOCKED, not a verdict).
    """
    a = relu_dense(W[out_idx][:, mid_idx])
    b = relu_dense(W[mid_idx][:, in_idx])
    return a @ b


def aggregate_mean(values: np.ndarray, out_angles: np.ndarray,
                   in_angles: np.ndarray):
    """Mean cell-pair coupling per (out angle, in angle) bin -- the
    Stage-A wedge_aggregate semantic on an angle-keyed frame. Returns
    (mean matrix, unique out angles, unique in angles)."""
    out_u, out_inv = np.unique(np.round(out_angles, 6), return_inverse=True)
    in_u, in_inv = np.unique(np.round(in_angles, 6), return_inverse=True)
    P = np.zeros((out_u.size, out_inv.size))
    P[out_inv, np.arange(out_inv.size)] = 1.0
    Q = np.zeros((in_u.size, in_inv.size))
    Q[in_inv, np.arange(in_inv.size)] = 1.0
    sums = P @ values @ Q.T
    counts = np.outer(np.bincount(out_inv, minlength=out_u.size),
                      np.bincount(in_inv, minlength=in_u.size)).astype(float)
    return sums / counts, out_u, in_u


def antipodal_mass(mean: np.ndarray, out_angles: np.ndarray,
                   in_angles: np.ndarray) -> float:
    """BAR 1 statistic A: mass fraction of the aggregated matrix at
    circular angular distance within ONE 40-deg sector of 180 deg
    (distance in [160, 180]). NaN if the matrix is all zero
    (degenerate -> BLOCKED upstream)."""
    total = float(mean.sum())
    if total <= 0:
        return float("nan")
    dist = circ_dist_deg(out_angles[:, None], in_angles[None, :])
    inside = dist >= (ANTIPODE_DEG - SECTOR_DEG / 2.0 - 1e-9)
    return float(mean[inside].sum() / total)


def offset_histogram(mean: np.ndarray, out_angles: np.ndarray,
                     in_angles: np.ndarray) -> np.ndarray:
    """Aggregate an (out angle, in angle) mean matrix into the Stage-A
    16-bin signed offset profile h, h[k] = mean over (out, in) angle
    pairs whose wrapped (out - in) difference rounds to bin k (22.5-deg
    bins, index k = signed bin mod 16) -- the offset_profile semantic
    (mean per offset, over all grid pairs) on the angle-keyed frame."""
    delta = wrap_deg(out_angles[:, None] - in_angles[None, :])
    bins = (np.round(delta / (360.0 / N_OFFSET_BINS)).astype(int)
            % N_OFFSET_BINS)
    h = np.zeros(N_OFFSET_BINS)
    count = np.zeros(N_OFFSET_BINS)
    np.add.at(h, bins.ravel(), mean.ravel())
    np.add.at(count, bins.ravel(), 1.0)
    nonzero = count > 0
    h[nonzero] /= count[nonzero]
    return h


def circulant(h: np.ndarray) -> np.ndarray:
    """Embed a 16-bin offset profile as the circulant matrix whose
    Stage-A offset_profile is exactly h, so the VERBATIM mirror_peak
    (never re-implemented) evaluates the registered
    S = max_d max(q_L(d) q_R(-d), q_L(-d) q_R(d)) on it."""
    n = h.size
    idx = (np.arange(n)[:, None] - np.arange(n)[None, :]) % n
    return h[idx]


def one_hop_hist(W, out_idx: np.ndarray, out_angles: np.ndarray,
                 in_idx: np.ndarray, in_angles: np.ndarray):
    """One-hop relu coupling aggregated into a 16-bin offset profile.
    Returns (h, aggregated mass)."""
    if out_idx.size == 0 or in_idx.size == 0:
        return np.zeros(N_OFFSET_BINS), 0.0
    # AC-FB5 again: relu keeps the consensus-ACh bar populations.
    block = relu_dense(W[out_idx][:, in_idx])
    mean, out_u, in_u = aggregate_mean(block, out_angles, in_angles)
    return offset_histogram(mean, out_u, in_u), float(mean.sum())


# ---------------------------------------------------------------------------
# Group parsing and coverage (AC-FB6 lives here)
# ---------------------------------------------------------------------------

def _row_mask(types: np.ndarray, row: str) -> np.ndarray:
    pattern = ROW_PATTERNS[row]
    return np.array([fnmatch.fnmatchcase(t, pattern) for t in types])


def _columns_and_angles(indices: np.ndarray, instances: np.ndarray):
    """Labelled subset of `indices` with per-row angles. N_type = the
    row's own observed distinct-column count (AC-FB1)."""
    cols = np.array([c if (c := fb_column(instances[i])) is not None else -1
                     for i in indices])
    keep = cols >= 0
    labelled = indices[keep]
    kept_cols = cols[keep]
    if labelled.size == 0:
        return labelled, np.zeros(0), 0
    n_columns = int(np.unique(kept_cols).size)
    angles = np.array([column_angle_deg(int(c), n_columns) for c in kept_cols])
    return labelled, angles, n_columns


def parse_groups(types: np.ndarray, instances: np.ndarray) -> dict[str, Any]:
    """Parse every bar and context population, with coverage accounting."""
    g: dict[str, Any] = {}

    def family(rows):
        mask = np.zeros(types.size, dtype=bool)
        for row in rows:
            mask |= _row_mask(types, row)
        return np.flatnonzero(mask)

    # AC-FB4 (ASSUMED, registered): _irreg cells are KEPT (they stay in
    # the subcircuit and in every type population) and FLAGGED here; if
    # such a cell also carries a parseable _C label it keeps it. Check:
    # inspect the _irreg instances in the annotations. Breaks: if _irreg
    # marks a different column convention, coverage and the frames blur
    # by those cells only.
    def irregular_count(indices):
        return int(sum(IRREG_MARK in instances[i] for i in indices))

    fc_all = family(("FC",))
    fc_idx, fc_angles, fc_n = _columns_and_angles(fc_all, instances)
    g.update(fc_idx_all=fc_all, fc_idx=fc_idx, fc_angles=fc_angles,
             fc_n_columns=fc_n,
             fc_coverage=(fc_idx.size / fc_all.size) if fc_all.size else 0.0,
             fc_irregular=irregular_count(fc_all))

    hd_all = family(("hDelta",))
    hd_idx, _hd_angles, hd_n = _columns_and_angles(hd_all, instances)
    g.update(hdelta_idx_all=hd_all, hdelta_n_columns=hd_n,
             hdelta_coverage=(hd_idx.size / hd_all.size) if hd_all.size else 0.0,
             hdelta_irregular=irregular_count(hd_all))

    vd_all = family(("vDelta",))
    vd_idx, _vd_angles, vd_n = _columns_and_angles(vd_all, instances)
    g.update(vdelta_idx_all=vd_all, vdelta_n_columns=vd_n,
             vdelta_coverage=(vd_idx.size / vd_all.size) if vd_all.size
             else float("nan"),
             vdelta_irregular=irregular_count(vd_all))

    # Labelled-PFN column frame (Bar 1 IN): per-row observed column count.
    pfn_col_idx, pfn_col_angles = [], []
    pfn_total = 0
    pfn_n_columns = {}
    for row in LABELLED_PFN_ROWS:
        cells = family((row,))
        pfn_total += int(cells.size)
        idx, angles, n_cols = _columns_and_angles(cells, instances)
        pfn_n_columns[row] = n_cols
        if idx.size:
            pfn_col_idx.append(idx)
            pfn_col_angles.append(angles)
    g["pfn_col_idx"] = (np.concatenate(pfn_col_idx) if pfn_col_idx
                        else np.zeros(0, dtype=np.int64))
    g["pfn_col_angles"] = (np.concatenate(pfn_col_angles) if pfn_col_angles
                           else np.zeros(0))
    g["pfn_total"] = pfn_total
    g["pfn_n_columns"] = pfn_n_columns
    g["pfn_col_coverage"] = (g["pfn_col_idx"].size / pfn_total
                             if pfn_total else 0.0)
    labelled_cells = family(LABELLED_PFN_ROWS)
    g["pfn_irregular"] = irregular_count(labelled_cells)

    # Labelled-PFN glomerulus frame (Bar 2 IN), split by hemisphere.
    glom_side: dict[str, list[int]] = {"L": [], "R": []}
    glom_angle: dict[str, list[float]] = {"L": [], "R": []}
    glom_labelled = 0
    for i in labelled_cells:
        parsed = pb_glomerulus(str(instances[i]))
        if parsed is None:
            continue
        glom_labelled += 1
        side, glom = parsed
        glom_side[side].append(int(i))
        glom_angle[side].append(glom_angle_deg(side, glom))
    for side in ("L", "R"):
        g[f"pfn_glom_idx_{side}"] = np.asarray(glom_side[side], dtype=np.int64)
        g[f"pfn_glom_angles_{side}"] = np.asarray(glom_angle[side])
    g["pfn_glom_coverage"] = (glom_labelled / pfn_total) if pfn_total else 0.0

    # PFL context frame (non-decisional): per-row observed column count.
    pfl_idx, pfl_angles = [], []
    pfl_total = 0
    pfl_labelled = 0
    for row in PFL_ROWS:
        cells = family((row,))
        pfl_total += int(cells.size)
        idx, angles, _n = _columns_and_angles(cells, instances)
        pfl_labelled += int(idx.size)
        if idx.size:
            pfl_idx.append(idx)
            pfl_angles.append(angles)
    g["pfl_idx"] = (np.concatenate(pfl_idx) if pfl_idx
                    else np.zeros(0, dtype=np.int64))
    g["pfl_angles"] = (np.concatenate(pfl_angles) if pfl_angles
                       else np.zeros(0))
    g["pfl_coverage"] = (pfl_labelled / pfl_total) if pfl_total \
        else float("nan")
    return g


# ---------------------------------------------------------------------------
# Metrics for one wiring
# ---------------------------------------------------------------------------

def analyze(matrix, g: dict[str, Any], with_context: bool = False) -> dict[str, Any]:
    """One wiring's full bar-metric set (and, for the real arm only, the
    non-decisional context profiles)."""
    result: dict[str, Any] = {}

    # BAR 1: two-hop labelled-PFN -> hDelta -> FC antipodal concentration.
    W2 = two_hop_rect(matrix, g["fc_idx"], g["hdelta_idx_all"], g["pfn_col_idx"])
    mean, out_u, in_u = aggregate_mean(W2, g["fc_angles"], g["pfn_col_angles"])
    result["bar1_antipodal"] = antipodal_mass(mean, out_u, in_u)

    # BAR 2: per-hemisphere one-hop FC<-PFN offset profiles -> mirror_peak.
    hists: dict[str, np.ndarray] = {}
    masses: dict[str, float] = {}
    for side in ("L", "R"):
        hists[side], masses[side] = one_hop_hist(
            matrix, g["fc_idx"], g["fc_angles"],
            g[f"pfn_glom_idx_{side}"], g[f"pfn_glom_angles_{side}"])
    result["bar2_mirror"] = mirror_peak(circulant(hists["L"]),
                                        circulant(hists["R"]))
    result["bar2_onehop_mass"] = {s: masses[s] for s in ("L", "R")}

    if with_context:
        result["bar1_offset_hist"] = offset_histogram(mean, out_u, in_u).tolist()
        result["bar2_offset_hist"] = {s: hists[s].tolist() for s in ("L", "R")}
        context: dict[str, Any] = {"non_decisional": True}
        # vDelta analog of Bar 1 (reported, decides nothing).
        if g["vdelta_idx_all"].size and g["fc_idx"].size and g["pfn_col_idx"].size:
            W2v = two_hop_rect(matrix, g["fc_idx"], g["vdelta_idx_all"],
                               g["pfn_col_idx"])
            mv, ov, iv = aggregate_mean(W2v, g["fc_angles"], g["pfn_col_angles"])
            context["vdelta_antipodal"] = antipodal_mass(mv, ov, iv)
            context["vdelta_offset_hist"] = offset_histogram(mv, ov, iv).tolist()
        else:
            context["vdelta_antipodal"] = None
        # PFL analog of Bar 2 (reported, decides nothing).
        if g["pfl_idx"].size:
            pfl_hists = {}
            for side in ("L", "R"):
                pfl_hists[side], _ = one_hop_hist(
                    matrix, g["pfl_idx"], g["pfl_angles"],
                    g[f"pfn_glom_idx_{side}"], g[f"pfn_glom_angles_{side}"])
            context["pfl_mirror"] = mirror_peak(circulant(pfl_hists["L"]),
                                                circulant(pfl_hists["R"]))
            context["pfl_offset_hist"] = {s: pfl_hists[s].tolist()
                                          for s in ("L", "R")}
        else:
            context["pfl_mirror"] = None
        result["context"] = context
    return result


# ---------------------------------------------------------------------------
# The frozen decision pipeline (pure given its inputs)
# ---------------------------------------------------------------------------

def run_pipeline(matrix, types, instances, n_nulls: int, log,
                 rewire_fn=None) -> dict[str, Any]:
    """Coverage floors, real metrics, null distribution, bars. Returns
    the record dict with 'verdict' of PASS / KILL, or 'blocked' set.
    Cost-honest order: floors first, real arm next, nulls only after the
    real arm is valid."""
    types = np.asarray(types).astype("U")
    instances = np.asarray(instances).astype("U")
    g = parse_groups(types, instances)

    record: dict[str, Any] = {
        "hypothesis": "H-FB-COLUMNAR-TOPOLOGY",
        "coverage": {
            "fc_column": g["fc_coverage"],
            "hdelta_column": g["hdelta_coverage"],
            "labelled_pfn_column": g["pfn_col_coverage"],
            "labelled_pfn_glomerulus": g["pfn_glom_coverage"],
            "vdelta_column_context": g["vdelta_coverage"],
            "pfl_column_context": g["pfl_coverage"],
        },
        "column_counts": {
            "FC": g["fc_n_columns"], "hDelta": g["hdelta_n_columns"],
            "vDelta": g["vdelta_n_columns"], **g["pfn_n_columns"],
        },
        "group_sizes": {
            "FC_labelled": int(g["fc_idx"].size),
            "hDelta_all": int(g["hdelta_idx_all"].size),
            "labelled_PFN_column": int(g["pfn_col_idx"].size),
            "labelled_PFN_glom_L": int(g["pfn_glom_idx_L"].size),
            "labelled_PFN_glom_R": int(g["pfn_glom_idx_R"].size),
            "vDelta_all": int(g["vdelta_idx_all"].size),
            "PFL_labelled": int(g["pfl_idx"].size),
        },
        "irregular_flagged": {
            "FC": g["fc_irregular"], "hDelta": g["hdelta_irregular"],
            "vDelta": g["vdelta_irregular"], "labelled_PFN": g["pfn_irregular"],
        },
    }

    # AC-FB6 (ASSUMED, registered): instance labels survive the compile --
    # this coverage floor IS its check. The 0.90 floor binds on every
    # bar-coordinate population (FC and labelled-PFN columns, labelled-PFN
    # glomeruli, and hDelta, whose baseline the registration cites among
    # the floors); vDelta and PFL are declared non-decisional context, so
    # their coverage is reported but never blocks.
    floors = {
        "fc_column": g["fc_coverage"],
        "hdelta_column": g["hdelta_coverage"],
        "labelled_pfn_column": g["pfn_col_coverage"],
        "labelled_pfn_glomerulus": g["pfn_glom_coverage"],
    }
    failing = {k: v for k, v in floors.items() if not v >= MIN_COVERAGE}
    if failing:
        record["blocked"] = ("coverage below "
                             f"{MIN_COVERAGE}: "
                             + ", ".join(f"{k} {v:.3f}"
                                         for k, v in failing.items()))
        return record

    real = analyze(matrix, g, with_context=True)
    if not np.isfinite(real["bar1_antipodal"]):
        record["blocked"] = "degenerate two-hop (zero mass) for Bar 1"
        return record
    if min(real["bar2_onehop_mass"].values()) <= 0:
        record["blocked"] = ("degenerate one-hop (zero mass) for Bar 2: "
                             f"{real['bar2_onehop_mass']}")
        return record
    record["real"] = real
    log(f"real: bar1 antipodal {real['bar1_antipodal']:.4f}, "
        f"bar2 mirror {real['bar2_mirror']:.4f}, context vdelta "
        f"{real['context']['vdelta_antipodal']}, pfl mirror "
        f"{real['context']['pfl_mirror']}")

    if rewire_fn is None:
        from flygi.connectome.nulls import degree_preserving_rewire

        def rewire_fn(m, seed):
            rewired, _ = degree_preserving_rewire(m, seed=seed)
            return rewired

    null_antipodal, null_mirror = [], []
    t0 = time.time()
    for k in range(n_nulls):
        null = analyze(rewire_fn(matrix, REWIRE_SEED_BASE + k), g)
        a = null["bar1_antipodal"]
        null_antipodal.append(a if np.isfinite(a) else 0.0)
        null_mirror.append(null["bar2_mirror"])
        if (k + 1) % 50 == 0:
            log(f"  nulls {k + 1}/{n_nulls} ({time.time() - t0:.1f}s)")

    p_antipodal = empirical_p(real["bar1_antipodal"], null_antipodal)
    p_mirror = empirical_p(real["bar2_mirror"], null_mirror)
    bars = {
        "antipode": bool(p_antipodal < ALPHA),
        "mirror": bool(p_mirror < ALPHA),
    }
    record.update({
        "null_antipodal_max": float(max(null_antipodal)),
        "null_mirror_max": float(max(null_mirror)),
        "p_antipodal": p_antipodal,
        "p_mirror": p_mirror,
        "n_nulls": n_nulls,
        "bars": bars,
        "verdict": "PASS" if all(bars.values()) else "KILL",
    })
    return record


# ---------------------------------------------------------------------------
# The in-cloud synthetic gate (BLOCKED floor 5; the AC-4 pattern)
# ---------------------------------------------------------------------------

def build_ideal_circuit(n_fc_per_col: int = 3, n_pfn_per_glom: int = 2,
                        n_hd_per_path: int = 2, noise: float = GATE_NOISE,
                        seed: int = GATE_BUILD_SEED):
    """Idealized Hulse-motif FB circuit, the registered gate substrate:
    9-column FC frame; per side 8 PFN glomeruli (digits 2-9) projecting
    one-hop into FC at opposite-signed one-sector (40-deg) offsets, the
    right side the exact reflection of the left; hDelta half-width
    connectivity (PFN column -> hDelta -> the FC columns straddling the
    180-deg antipode). The two motifs are the ESTABLISHED Hulse anatomy;
    the circuit itself is ASSUMED/idealized -- it validates only that
    the pipeline detects the motifs expressed in its own frozen
    coordinate convention, never anything about the fly.

    Jitter multiplies EXISTING edges only (the Stage-A _ring precedent:
    dense noise would make the graph complete and leave the
    degree-preserving rewire zero legal swaps).
    """
    from scipy import sparse

    rng = np.random.default_rng(seed)
    types: list[str] = []
    instances: list[str] = []
    fc_cells: dict[int, list[int]] = {c: [] for c in range(1, 10)}
    for c in range(1, 10):
        for k in range(n_fc_per_col):
            fc_cells[c].append(len(types))
            types.append("FC1A")
            instances.append(f"FC1A_C{c}.{k}")
    hd_cells: dict[int, list[int]] = {a: [] for a in range(1, 10)}
    for a in range(1, 10):
        for k in range(n_hd_per_path):
            hd_cells[a].append(len(types))
            types.append("hDeltaA")
            # exercise the AC-FB3 sub-column collapse on half the cells
            suffix = "a" if k % 2 == 0 else ""
            instances.append(f"hDeltaA_C{a}{suffix}.{k}")

    centers = {c: column_angle_deg(c, 9) for c in range(1, 10)}

    def nearest_col(angle: float) -> int:
        return min(centers, key=lambda c: (circ_dist_deg(centers[c], angle), c))

    pfn: list[tuple[int, int, int]] = []  # (cell, home column, one-hop target)
    for g in range(GLOM_MIN, GLOM_MAX + 1):
        theta_l = glom_angle_deg("L", g)
        target_l = nearest_col((theta_l + SECTOR_DEG) % 360.0)
        for side in ("L", "R"):
            theta = glom_angle_deg(side, g)
            # Alternate each glomerulus's cells between the two FC-frame
            # columns straddling its angle, so the ideal occupies all 9
            # columns and the per-type observed column count (AC-FB1)
            # reproduces the builder's 9-column frame exactly.
            containing = int(theta // SECTOR_DEG) + 1
            relative = (theta % SECTOR_DEG) - SECTOR_DEG / 2.0
            step = 1 if relative >= 0 else -1
            other = ((containing - 1 + step) % 9) + 1
            # R is the exact reflection of L: column c reflects to 10 - c,
            # so the R offset profile is the L profile negated bin-for-bin.
            target = target_l if side == "L" else 10 - target_l
            for k in range(n_pfn_per_glom):
                home = containing if k % 2 == 0 else other
                cell = len(types)
                types.append("PFNd")
                instances.append(f"PFNd_{side}{g}_C{home}.{k}")
                pfn.append((cell, home, target))

    n = len(types)
    W = np.zeros((n, n))
    for cell, home, target in pfn:
        for hd in hd_cells[home]:
            W[hd, cell] = 2.0                      # hDelta <- PFN
        for fc in fc_cells[target]:
            W[fc, cell] = 2.0                      # FC <- PFN (one-sector)
    for a in range(1, 10):
        antipodes = (((a - 1 + 4) % 9) + 1, ((a - 1 + 5) % 9) + 1)
        for hd in hd_cells[a]:
            for c in antipodes:
                for fc in fc_cells[c]:
                    W[fc, hd] = 2.0                # FC(antipode) <- hDelta
    if noise:
        mask = W != 0
        W[mask] *= 1.0 + noise * rng.standard_normal(int(mask.sum()))
    return sparse.csr_matrix(W), np.array(types), np.array(instances)


def synthetic_gate(n_nulls: int = N_NULLS, log=lambda m: None) -> dict[str, Any]:
    """The registered two-direction gate: both bars PASS on the ideal at
    the empirical floor through the REAL degree_preserving_rewire
    machinery, AND the ideal's own rewire KILLs both bars."""
    from flygi.connectome.nulls import degree_preserving_rewire

    W, types, instances = build_ideal_circuit()
    ideal = run_pipeline(W, types, instances, n_nulls, log)
    floor = 1.0 / (n_nulls + 1.0)
    ideal_ok = (
        "blocked" not in ideal
        and ideal["verdict"] == "PASS"
        and ideal["p_antipodal"] <= floor + 1e-12
        and ideal["p_mirror"] <= floor + 1e-12
    )
    broken_W, _ = degree_preserving_rewire(W, seed=GATE_BREAK_SEED)
    broken = run_pipeline(broken_W, types, instances, n_nulls, log)
    broken_ok = (
        "blocked" not in broken
        and broken["bars"] == {"antipode": False, "mirror": False}
    )
    return {
        "n_nulls": n_nulls,
        "empirical_floor": floor,
        "ideal": ideal,
        "rewired_ideal": broken,
        "ideal_passes_at_floor": bool(ideal_ok),
        "rewire_kills_both": bool(broken_ok),
        "passed": bool(ideal_ok and broken_ok),
    }


# ---------------------------------------------------------------------------
# Data-gated assembly (local host only)
# ---------------------------------------------------------------------------

def composition_check(types) -> list[str]:
    """BLOCKED floor (2): compiled per-type counts must equal the frozen
    composition table, at the table's own row grain."""
    types = np.asarray(types).astype("U")
    mismatches = []
    for row, expected in COMPOSITION.items():
        observed = int(_row_mask(types, row).sum())
        if observed != expected:
            mismatches.append(f"{row}: expected {expected}, observed {observed}")
    return mismatches


def check_prerequisites() -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not RAW_WEIGHTS.is_file():
        missing.append(f"raw pair table: {RAW_WEIGHTS}")
    for mod in ("scipy", "pyarrow"):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-FB-COLUMNAR-TOPOLOGY kill test (data-gated)")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites()
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("Run where the compiled runtime lives "
              "(docs/arenas/task10_menu/).")
        return 3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()

    # Floor (5): the synthetic gate runs BEFORE any data contact.
    log("synthetic gate (pre-data, both directions)...")
    gate = synthetic_gate(N_NULLS, log)
    gate_summary = {
        "n_nulls": gate["n_nulls"],
        "empirical_floor": gate["empirical_floor"],
        "ideal_passes_at_floor": gate["ideal_passes_at_floor"],
        "rewire_kills_both": gate["rewire_kills_both"],
        "passed": gate["passed"],
        "ideal_p": {"antipodal": gate["ideal"].get("p_antipodal"),
                    "mirror": gate["ideal"].get("p_mirror")},
        "rewired_p": {"antipodal": gate["rewired_ideal"].get("p_antipodal"),
                      "mirror": gate["rewired_ideal"].get("p_mirror")},
    }
    log(f"synthetic gate: {json.dumps(gate_summary, default=float)}")
    if not gate["passed"]:
        record = {"hypothesis": "H-FB-COLUMNAR-TOPOLOGY",
                  "blocked": "synthetic gate failed", "gate": gate_summary}
        args.output.write_text(json.dumps(record, indent=2, default=float))
        log("BLOCKED: synthetic gate failed (floor 5)")
        return 3

    from flygi.connectome.subcircuit import extract_subcircuit, select_nodes
    indices = select_nodes(RUNTIME_DIR, type_patterns=TYPE_PATTERNS)
    sub = extract_subcircuit(RUNTIME_DIR, indices)
    log(f"subcircuit: {sub.node_count} nodes, {sub.matrix.nnz} signed edges, "
        f"dropped modulatory {sub.dropped_modulatory_edges}, unsigned "
        f"{sub.unsigned_edges}")
    mismatches = composition_check(sub.types)
    if mismatches:
        record = {"hypothesis": "H-FB-COLUMNAR-TOPOLOGY",
                  "blocked": "composition deviates from the frozen table",
                  "gate": gate_summary, "mismatches": mismatches}
        args.output.write_text(json.dumps(record, indent=2, default=float))
        log("BLOCKED: composition deviates from the frozen table:")
        for item in mismatches:
            log(f"  - {item}")
        return 3

    record = run_pipeline(sub.matrix, sub.types, sub.instances, N_NULLS, log)
    record["gate"] = gate_summary
    # AC-FB5's run-time audit: report the bar populations' consensus NT.
    types_arr = np.asarray(sub.types).astype("U")
    nt_report = {}
    for row in ("FC", "hDelta") + LABELLED_PFN_ROWS:
        mask = _row_mask(types_arr, row)
        values, counts = np.unique(np.asarray(sub.consensus_nt)[mask],
                                   return_counts=True)
        nt_report[row] = {str(v): int(c) for v, c in zip(values, counts)}
    record["consensus_nt_audit"] = nt_report
    record["elapsed_s"] = round(time.time() - started, 1)
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(json.dumps(record, indent=2, default=float))
    if "blocked" in record:
        log(f"BLOCKED: {record['blocked']}")
        return 3
    log(f"VERDICT: {record['verdict']}")
    handle.close()
    return 0 if record["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
