#!/usr/bin/env python3
"""H-T4T5-DSEC-DIRECTION -- the Task 2 (DSEC-Flow) kill test.

PREREGISTRATION (EXPERIMENTS.yaml H-T4T5-DSEC-DIRECTION and
docs/arenas/task2_dsec_flow/killtest_design.md, both 2026-10-01, frozen
BEFORE any event or ground-truth data was seen; restated here, not
changed):

  - One sequence only (DSEC train with forward-flow GT; declared
    selection rule in the design doc). First 250 GT flow windows;
    temporal 20% CALIBRATION prefix / 80% EVALUATION. BLOCKED (not a
    verdict) below 30 evaluable EVAL windows.
  - Pipeline: signed event-polarity running sums per column (AD-6),
    central 480x480 crop mapped isotropically onto the patch's input
    lattice with nearest-column assignment (AD-7), fc2 drive path
    (INPUT_DRIVE on L1/L2/L3), settle-stream-tail protocol, evoked
    integrals on scored T4/T5 cells, fixed population-vector readout
    using fc25's own measured subtype preferred directions (AD-8).
    dt_sub swept over {10, 20, 50, 100} ms on CAL only, each arm
    choosing by its own CAL mean angular error (matched freedom).
  - Arms: REAL (fc25 trained_subset passing config, verbatim gain),
    TWIN (uniform-tau, its own fc25 gain), NULL (3x degree-preserving
    rewire of REAL, real table/gain), TRIVIAL-1 zero flow (EPE context
    only), TRIVIAL-2 GT-median global direction (oracle context),
    TRIVIAL-3 event-centroid-shift (KILL COMPARATOR), ENGINEERED
    lattice cross-correlation (ceiling context).
  - PASS iff REAL beats TRIVIAL-3 AND the NULL (per-window mean 2D
    angular error over evaluable columns; one-sided paired sign tests
    across EVAL windows, p < 0.05, plus strictly lower medians).
    Otherwise KILL: recorded class-2.5 limit, task complete, no dense
    pipeline, no benchmark entry.

DATA GATE, measured 2026-10-01: the cloud container has no compiled
MaleCNS runtime (data/processed absent), no flyvis results, and HTTP 000
to every data host. This script therefore checks its prerequisites first
and exits 3 with a BLOCKED report when they are missing. It runs where
the data and runtime live -- the user's local machine
(docs/arenas/task2_dsec_flow/runbook.md).

OPERATIONALIZATIONS declared here (the design doc's terms made exact,
still before data):
  - "95th-percentile per-column value" for drive normalization = the
    95th percentile of |end-of-window cumulative per-column
    pseudo-luminance| over CALIBRATION windows (end-of-window sums are
    dt-independent, so the one scalar is shared by every dt and arm).
  - Scored-cell column = nearest integer hex-axial column of the cell's
    (possibly fractional, connectivity-centroid) plane coordinate.
  - Image y points down; the lattice plane y points up. GT flow (u, v)
    enters the plane as (u, -v); estimates are compared in plane
    coordinates. One declared mapping shared by stimulus, readout and
    ground truth -- direction claims are mapping-consistent.
  - Null-instance dt: each of the three rewired instances picks its own
    CAL dt (same freedom as every arm); the EVAL kill comparison uses
    the per-window MEAN angular error across the three instances.

Expected tier, base rate stated: 0 for 12; the nearest precedent
(H-T4T5-CLASS25-MOTION) measured the rewire ABOVE real on ARC frames.

Run (where data + runtime live):
    python scripts/arenas/dsec_killtest.py --data-root <DSEC root> \
        [--sequence thun_00_a]
Output: results/arenas/dsec_killtest.json (+ .log)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "scripts/benchmarks"
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- frozen constants (killtest_design.md; do not tune) --------------------
WINDOW_CAP = 250
CAL_FRACTION = 0.2
MIN_EVAL_WINDOWS = 30
DT_SUB_GRID_MS = (10.0, 20.0, 50.0, 100.0)
CROP = 480
ASSIGN_RADIUS = 0.75        # plane units; hex Voronoi radius ~0.577
MIN_VALID_FRACTION = 0.5
MIN_GT_MAG_PX = 2.0
MIN_EVAL_COLUMNS = 10
REWIRE_SEED_BASE = 4242
REWIRE_SEEDS = (0, 1, 2)
ALPHA = 0.05
TAIL_MS = 750.0             # asserted == fc2.WINDOW_AFTER_S * 1000
NORM_PERCENTILE = 95.0
XCORR_MAX_SHIFT = 3
PRIMARY_SEQUENCE = "thun_00_a"

FC25_RESULTS = ROOT / "results/benchmarks/fc25_visual_ds.json"
PARAMS_JSON = ROOT / "docs/fidelity2/flyvis_trained_params.json"
RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
ANNOTATIONS = ROOT / "data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT_JSON = ROOT / "results/arenas/dsec_killtest.json"

HEX_E1 = np.array([1.0, 0.0])
HEX_E2 = np.array([0.5, math.sqrt(3.0) / 2.0])


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Pure geometry/binning/readout plumbing -- unit-tested with synthetic
# inputs (tests/test_dsec_killtest.py); no fly runtime, no data files.
# ---------------------------------------------------------------------------

def plane_to_axial(x: np.ndarray, y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Invert the fc2 hex embedding x = h1 + h2/2, y = (sqrt3/2) h2."""
    h2 = np.asarray(y, dtype=np.float64) / (math.sqrt(3.0) / 2.0)
    h1 = np.asarray(x, dtype=np.float64) - 0.5 * h2
    return h1, h2


def axial_to_plane(h1: np.ndarray, h2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    h1 = np.asarray(h1, dtype=np.float64)
    h2 = np.asarray(h2, dtype=np.float64)
    return h1 + 0.5 * h2, (math.sqrt(3.0) / 2.0) * h2


def build_lattice(driven_x: np.ndarray, driven_y: np.ndarray) -> dict[str, Any]:
    """Unique integer-axial columns of the driven cells, their plane
    centers, and each driven cell's column index."""
    h1f, h2f = plane_to_axial(driven_x, driven_y)
    h1 = np.round(h1f).astype(np.int64)
    h2 = np.round(h2f).astype(np.int64)
    pairs = np.stack([h1, h2], axis=1)
    uniq, cell_col = np.unique(pairs, axis=0, return_inverse=True)
    cx, cy = axial_to_plane(uniq[:, 0], uniq[:, 1])
    return {
        "axial": uniq,                       # (n_cols, 2) int
        "col_x": cx, "col_y": cy,            # plane centers
        "cell_col": cell_col,                # per driven cell
        "n_cols": int(uniq.shape[0]),
    }


def crop_mapping(col_x: np.ndarray, col_y: np.ndarray,
                 crop: int = CROP) -> dict[str, float]:
    """Isotropic, centered map between the central square crop (pixels)
    and the lattice plane (AD-7). One scale for both axes; image y down
    -> plane y up."""
    x_ext = float(col_x.max() - col_x.min())
    y_ext = float(col_y.max() - col_y.min())
    units_per_px = (max(x_ext, y_ext) + 1.0) / crop   # half-col margin
    return {
        "units_per_px": units_per_px,
        "cx": float((col_x.max() + col_x.min()) / 2.0),
        "cy": float((col_y.max() + col_y.min()) / 2.0),
        "crop": crop,
    }


def pixels_to_plane(px: np.ndarray, py: np.ndarray, mapping: dict):
    """Crop-pixel centers -> plane coordinates (y flipped)."""
    s, half = mapping["units_per_px"], mapping["crop"] / 2.0
    x = mapping["cx"] + (np.asarray(px, np.float64) + 0.5 - half) * s
    y = mapping["cy"] - (np.asarray(py, np.float64) + 0.5 - half) * s
    return x, y


def assign_crop_pixels(lattice: dict, mapping: dict) -> np.ndarray:
    """(crop, crop) int32 array of nearest column index, -1 where the
    nearest center is farther than ASSIGN_RADIUS plane units."""
    crop = mapping["crop"]
    py, px = np.mgrid[0:crop, 0:crop]
    x, y = pixels_to_plane(px.ravel(), py.ravel(), mapping)
    # brute force is fine: crop^2 x n_cols fits comfortably in RAM
    d2 = ((x[:, None] - lattice["col_x"][None, :]) ** 2
          + (y[:, None] - lattice["col_y"][None, :]) ** 2)
    nearest = np.argmin(d2, axis=1)
    ok = d2[np.arange(nearest.size), nearest] <= ASSIGN_RADIUS ** 2
    out = np.where(ok, nearest, -1).astype(np.int32)
    return out.reshape(crop, crop)


def bin_window_events(ev_x, ev_y, ev_p, ev_t, t0, t1, n_sub,
                      pixel_to_col, n_cols, crop_x0, crop_y0):
    """One flow window's events -> per-sub-window per-column signed
    polarity sums and absolute counts.

    ev_x/ev_y are FULL-FRAME pixel coords (rectified); the crop offset
    is subtracted here. Returns (signed (n_sub, n_cols),
    counts (n_sub, n_cols)); callers build the running sum (AD-6) with
    np.cumsum over axis 0."""
    ev_t = np.asarray(ev_t, dtype=np.float64)
    keep = (ev_t >= t0) & (ev_t < t1)
    x = np.asarray(ev_x, dtype=np.int64)[keep] - int(crop_x0)
    y = np.asarray(ev_y, dtype=np.int64)[keep] - int(crop_y0)
    p = np.asarray(ev_p, dtype=np.float64)[keep]
    t = ev_t[keep]
    crop = pixel_to_col.shape[0]
    inside = (x >= 0) & (x < crop) & (y >= 0) & (y < crop)
    x, y, p, t = x[inside], y[inside], p[inside], t[inside]
    col = pixel_to_col[y, x]
    good = col >= 0
    x, p, t, col = x[good], p[good], t[good], col[good]
    sign = np.where(p > 0, 1.0, -1.0)
    sub = np.minimum(
        ((t - t0) / max(t1 - t0, 1e-12) * n_sub).astype(np.int64), n_sub - 1
    )
    flat = sub * n_cols + col
    signed = np.bincount(flat, weights=sign, minlength=n_sub * n_cols)
    counts = np.bincount(flat, minlength=n_sub * n_cols).astype(np.float64)
    return (signed.reshape(n_sub, n_cols), counts.reshape(n_sub, n_cols))


def axial_neighbors(lattice: dict, radius: int = 1) -> list[np.ndarray]:
    """Per column: indices of columns within the axial box |dh|<=radius
    (the declared 3x3 neighborhood for radius 1)."""
    ax = lattice["axial"]
    out = []
    for k in range(ax.shape[0]):
        d = np.abs(ax - ax[k])
        out.append(np.flatnonzero((d[:, 0] <= radius) & (d[:, 1] <= radius)))
    return out


def centroid_shift_directions(counts_first, counts_last, lattice,
                              neighbors) -> np.ndarray:
    """TRIVIAL-3 (kill comparator): per column, displacement of the
    |count|-weighted centroid over the 3x3 axial neighborhood from the
    first third to the last third of the window. NaN where either third
    has no events in the neighborhood."""
    cx, cy = lattice["col_x"], lattice["col_y"]
    est = np.full((lattice["n_cols"], 2), np.nan)
    for k, nb in enumerate(neighbors):
        wf = counts_first[nb]
        wl = counts_last[nb]
        sf, sl = wf.sum(), wl.sum()
        if sf <= 0 or sl <= 0:
            continue
        c0 = np.array([(cx[nb] * wf).sum() / sf, (cy[nb] * wf).sum() / sf])
        c1 = np.array([(cx[nb] * wl).sum() / sl, (cy[nb] * wl).sum() / sl])
        est[k] = c1 - c0
    return est


def cross_correlation_shift(frame_first, frame_last, lattice,
                            max_shift: int = XCORR_MAX_SHIFT) -> np.ndarray:
    """ENGINEERED (ceiling context): one global axial shift per window =
    argmax cross-correlation of the two third-window count frames on the
    dense axial grid; returned as a plane vector."""
    ax = lattice["axial"]
    h1_min, h2_min = ax.min(axis=0)
    h1_max, h2_max = ax.max(axis=0)
    g1, g2 = h1_max - h1_min + 1, h2_max - h2_min + 1
    a = np.zeros((g1, g2))
    b = np.zeros((g1, g2))
    a[ax[:, 0] - h1_min, ax[:, 1] - h2_min] = frame_first
    b[ax[:, 0] - h1_min, ax[:, 1] - h2_min] = frame_last
    best, best_shift = -np.inf, (0, 0)
    for d1 in range(-max_shift, max_shift + 1):
        for d2 in range(-max_shift, max_shift + 1):
            lo1, hi1 = max(0, -d1), min(g1, g1 - d1)
            lo2, hi2 = max(0, -d2), min(g2, g2 - d2)
            if hi1 <= lo1 or hi2 <= lo2:
                continue
            score = float(
                (a[lo1:hi1, lo2:hi2] * b[lo1 + d1:hi1 + d1, lo2 + d2:hi2 + d2]).sum()
            )
            if score > best:
                best, best_shift = score, (d1, d2)
    return best_shift[0] * HEX_E1 + best_shift[1] * HEX_E2


def population_vote(evoked, cell_col, pref_vec, n_cols):
    """AD-8 readout: per column, vote = sum over that column's scored
    cells of evoked * subtype preferred unit vector. Also returns per-
    column count of DISTINCT preferred vectors present (coverage).
    evoked: (n_cells,); cell_col: (n_cells,) int; pref_vec: (n_cells, 2)."""
    votes = np.zeros((n_cols, 2))
    np.add.at(votes, cell_col, evoked[:, None] * pref_vec)
    coverage = np.zeros(n_cols, dtype=np.int64)
    for k in range(n_cols):
        members = cell_col == k
        if members.any():
            coverage[k] = np.unique(
                np.round(pref_vec[members], 6), axis=0
            ).shape[0]
    return votes, coverage


def bin_gt_to_columns(flow, valid, pixel_to_col, n_cols, crop_x0, crop_y0):
    """GT flow (full frame, image coords) -> per-column mean plane
    direction + the evaluability gate (killtest_design.md): >= 50% valid
    pixels AND median |flow| >= 2 px in the column's block.
    Returns (gt_vec_plane (n_cols, 2), evaluable (n_cols,), median_mag)."""
    crop = pixel_to_col.shape[0]
    f = np.asarray(flow, dtype=np.float64)[
        crop_y0:crop_y0 + crop, crop_x0:crop_x0 + crop
    ]
    v = np.asarray(valid, dtype=bool)[
        crop_y0:crop_y0 + crop, crop_x0:crop_x0 + crop
    ]
    col = pixel_to_col.ravel()
    val = v.ravel()
    fx = f[..., 0].ravel()
    fy = f[..., 1].ravel()
    mag = np.hypot(fx, fy)
    assigned = col >= 0
    gt = np.full((n_cols, 2), np.nan)
    evaluable = np.zeros(n_cols, dtype=bool)
    mags = []
    for k in range(n_cols):
        members = assigned & (col == k)
        n_tot = int(members.sum())
        if n_tot == 0:
            continue
        ok = members & val
        frac = ok.sum() / n_tot
        if frac < MIN_VALID_FRACTION:
            continue
        med = float(np.median(mag[ok]))
        # plane direction: image y down -> plane y up (declared mapping)
        gt[k] = [float(fx[ok].mean()), -float(fy[ok].mean())]
        if med >= MIN_GT_MAG_PX:
            evaluable[k] = True
            mags.append(med)
    median_mag = float(np.median(mags)) if mags else float("nan")
    return gt, evaluable, median_mag


def window_mean_ae(est_vec, gt_vec, evaluable) -> float:
    """Per-window mean 2D angular error (degrees) over evaluable columns
    where the estimate is defined; NaN if none."""
    ok = evaluable & np.isfinite(est_vec).all(axis=1) \
        & (np.linalg.norm(est_vec, axis=1) > 1e-12)
    if not ok.any():
        return float("nan")
    e = est_vec[ok]
    g = gt_vec[ok]
    cos = np.sum(e * g, axis=1) / (
        np.linalg.norm(e, axis=1) * np.linalg.norm(g, axis=1)
    )
    return float(np.mean(np.degrees(np.arccos(np.clip(cos, -1, 1)))))


def paired_sign_test_less(a: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    """One-sided exact sign test, H1: a < b. Pairs with NaN on either
    side or ties are dropped. Exact binomial via math.comb."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ok = np.isfinite(a) & np.isfinite(b)
    less = int(np.sum(a[ok] < b[ok]))
    greater = int(np.sum(a[ok] > b[ok]))
    n = less + greater
    if n == 0:
        return {"n": 0, "less": 0, "p": float("nan")}
    p = sum(math.comb(n, k) for k in range(less, n + 1)) / 2.0 ** n
    return {"n": n, "less": less, "p": float(min(p, 1.0))}


# ---------------------------------------------------------------------------
# Data-gated parts: prerequisites, DSEC loading, simulation, main
# ---------------------------------------------------------------------------

def check_prerequisites(data_root: Path | None) -> list[str]:
    """Everything the run needs; each missing item is one line of the
    BLOCKED report. Pure checks only -- importable and testable."""
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not ANNOTATIONS.exists():
        missing.append(f"raw annotations feather: {ANNOTATIONS}")
    if not PARAMS_JSON.exists():
        missing.append(f"trained flyvis params: {PARAMS_JSON}")
    if not FC25_RESULTS.exists():
        missing.append(f"fc25 passing result (local-only artifact): "
                       f"{FC25_RESULTS}")
    for mod in ("h5py", "hdf5plugin", "pyarrow", "scipy"):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    if data_root is None:
        missing.append("--data-root (DSEC directory; see runbook.md)")
    elif not Path(data_root).exists():
        missing.append(f"data root not found: {data_root}")
    return missing


def find_sequence(data_root: Path, requested: str | None):
    """Declared selection rule: the requested sequence if complete, else
    PRIMARY_SEQUENCE if complete, else the alphabetically first sequence
    with forward-flow GT + timestamps + left events."""
    def complete(seq_dir: Path) -> dict | None:
        flow_dir = seq_dir / "flow" / "forward"
        ts = seq_dir / "flow" / "forward_timestamps.txt"
        events = list(seq_dir.glob("events/left/events.h5"))
        if flow_dir.is_dir() and ts.exists() and events:
            rect = list(seq_dir.glob("events/left/rectify_map.h5"))
            return {"name": seq_dir.name, "flow_dir": flow_dir,
                    "timestamps": ts, "events": events[0],
                    "rectify": rect[0] if rect else None}
        return None

    candidates = ([requested] if requested else []) + [PRIMARY_SEQUENCE]
    for name in candidates:
        got = complete(data_root / name)
        if got:
            return got
    for seq_dir in sorted(p for p in data_root.iterdir() if p.is_dir()):
        got = complete(seq_dir)
        if got:
            return got
    return None


def load_windows(seq: dict, cap: int) -> list[dict]:
    """GT flow windows in timestamp order, capped. PNG order follows the
    benchmark's own alphabetical-filename rule; timestamps pair by row."""
    rows = np.loadtxt(seq["timestamps"], delimiter=",", comments="#",
                      ndmin=2)
    pngs = sorted(seq["flow_dir"].glob("*.png"))
    n = min(len(pngs), rows.shape[0], cap)
    return [{"png": pngs[i], "t0_us": float(rows[i, 0]),
             "t1_us": float(rows[i, 1])} for i in range(n)]


def event_slice(h5, t0_us: float, t1_us: float):
    """Events in [t0, t1) absolute microseconds, using ms_to_idx to
    bound the read, refined by searchsorted."""
    t_offset = float(h5["t_offset"][()]) if "t_offset" in h5 else 0.0
    rel0, rel1 = t0_us - t_offset, t1_us - t_offset
    ev = h5["events"]
    n_total = ev["t"].shape[0]
    if "ms_to_idx" in h5:
        ms = h5["ms_to_idx"]
        lo_ms = max(int(rel0 // 1000), 0)
        hi_ms = min(int(rel1 // 1000) + 2, ms.shape[0] - 1)
        lo, hi = int(ms[lo_ms]), int(ms[hi_ms])
    else:
        lo, hi = 0, n_total
    t = np.asarray(ev["t"][lo:hi], dtype=np.float64)
    i0 = int(np.searchsorted(t, rel0, "left"))
    i1 = int(np.searchsorted(t, rel1, "left"))
    sl = slice(lo + i0, lo + i1)
    return (np.asarray(ev["x"][sl]), np.asarray(ev["y"][sl]),
            np.asarray(ev["p"][sl]),
            np.asarray(ev["t"][sl], dtype=np.float64) + t_offset)


def rectify_events(x, y, rect_map, width: int, height: int):
    """DSEC's own per-pixel rectification map, then rounding to the
    rectified integer pixel; out-of-frame rectified events are dropped
    by the caller's crop test."""
    rx = rect_map[y, x, 0]
    ry = rect_map[y, x, 1]
    return (np.round(rx).astype(np.int64), np.round(ry).astype(np.int64))


def simulate_arm_windows(fc2, matrix, types, table, gain, drives, score_idx,
                         dt_sub_ms: float, log, label: str):
    """Batched settle-stream-tail run (killtest_design.md step 4).
    drives: (n_windows, n_sub, n_nodes) external drive per sub-window.
    Returns (evoked (n_windows, n_scored), unstable (n_windows,))."""
    m, n_sub, _ = drives.shape
    t0 = time.time()
    net = fc2.GradedFlyvisNetwork(matrix, types, table,
                                  dt_ms=fc2.DT_MS, gain=gain)
    # settle once at zero drive (window-independent), then batch windows
    settle_steps = int(round(fc2.SETTLE_MS / fc2.DT_MS))
    zero = np.zeros(net.v.shape[0])
    for _ in range(settle_steps):
        net.step(zero)
    settled = net.v.copy()
    base_out = np.maximum(settled, 0.0)[score_idx]

    net.tau = net.tau[:, None]
    net.v_rest = net.v_rest[:, None]
    net.v = np.repeat(settled[:, None], m, axis=1)
    bad = np.zeros(m, dtype=bool)

    def unstable():
        finite = np.isfinite(net.v).all(axis=0)
        with np.errstate(invalid="ignore"):
            big = np.where(
                finite,
                np.abs(np.where(np.isfinite(net.v), net.v, 0.0)).max(axis=0),
                np.inf,
            ) > fc2.V_ABORT
        return ~finite | big

    sub_steps = max(int(round(dt_sub_ms / fc2.DT_MS)), 1)
    tail_steps = int(round(TAIL_MS / fc2.DT_MS))
    total = np.zeros((score_idx.size, m))
    step_count = 0
    with np.errstate(over="ignore", invalid="ignore"):
        for k in range(n_sub):
            drive = drives[:, k, :].T          # (n_nodes, m)
            for _ in range(sub_steps):
                net.step(drive)
                step_count += 1
                if step_count % 50 == 0:
                    bad |= unstable()
                evoked = np.maximum(
                    np.maximum(net.v, 0.0)[score_idx, :] - base_out[:, None],
                    0.0,
                )
                total += evoked * (fc2.DT_MS / 1000.0)
        tail_drive = np.zeros_like(net.v)
        for _ in range(tail_steps):
            net.step(tail_drive)
            step_count += 1
            if step_count % 50 == 0:
                bad |= unstable()
            evoked = np.maximum(
                np.maximum(net.v, 0.0)[score_idx, :] - base_out[:, None], 0.0
            )
            total += evoked * (fc2.DT_MS / 1000.0)
        bad |= unstable()
    log(f"  [{label}] dt_sub={dt_sub_ms:.0f}ms: {m} windows in "
        f"{time.time() - t0:.1f}s, unstable {int(bad.sum())}")
    return total.T.copy(), bad


def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-T4T5-DSEC-DIRECTION kill test (data-gated)"
    )
    parser.add_argument("--data-root", type=Path, default=None,
                        help="DSEC root containing <sequence>/flow + events")
    parser.add_argument("--sequence", default=None,
                        help=f"sequence name (default rule: "
                             f"{PRIMARY_SEQUENCE}, else alphabetical first "
                             f"complete)")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites(args.data_root)
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("This is the measured cloud-container state (WORKLOG "
              "2026-10-01); run on the machine that has the data and the "
              "compiled runtime (docs/arenas/task2_dsec_flow/runbook.md).")
        return 3

    import h5py  # noqa: PLC0415  (gated import)
    # MEASURED 2026-10-02 (local run): DSEC event arrays use HDF5 filter
    # 32001 (Blosc); h5py can read them only after hdf5plugin registers
    # the filter, else the read dies with an opaque plugin-path OSError.
    import hdf5plugin  # noqa: F401, PLC0415

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    dm = _load_module("dsec_metrics", Path(__file__).parent / "dsec_metrics.py")
    fc25 = _load_module("fc25_visual_ds", BENCH / "fc25_visual_ds.py")
    fc2 = fc25.load_fc2()
    assert abs(fc2.WINDOW_AFTER_S * 1000.0 - TAIL_MS) < 1e-9
    assert fc2.SETTLE_MS == 2500.0
    params = json.loads(PARAMS_JSON.read_text())
    fc25_results = json.loads(FC25_RESULTS.read_text())

    # fc25 passing configuration, verbatim (asserted; no re-tuning).
    passing = next(c for c in fc25_results["configs"]
                   if c["label"] == "trained_subset")
    assert passing["result"]["readout_v2_crossing_window"]["pass"] is True, \
        "fc25 trained_subset no longer passes -- refuse to run"
    gain_real = passing["calibration"]["chosen_gain"]
    gain_twin = fc25_results["trivial_alternative"]["calibration"]["chosen_gain"]
    per_subtype = passing["result"]["readout_v2_crossing_window"]["per_subtype"]
    pref_of_subtype = {
        name: np.array(fc2.DIR_VECTORS[info["preferred"]])
        for name, info in per_subtype.items()
    }
    log(f"fc25 passing config: trained_subset gain={gain_real}; twin gain="
        f"{gain_twin}; preferred directions "
        f"{ {k: v['preferred'] for k, v in per_subtype.items()} }")

    # Patch, lattice, pixel assignment.
    patch = fc2.build_patch()
    types = patch["types"]
    patch["driven_mask"] = np.isin(types, fc2.DRIVEN_TYPES)
    driven_idx = np.flatnonzero(patch["driven_mask"])
    score_idx = np.flatnonzero(np.isin(types, fc2.T4_SUBTYPES + fc2.T5_SUBTYPES))
    score_types = types[score_idx]
    lattice = build_lattice(patch["x"][driven_idx], patch["y"][driven_idx])
    mapping = crop_mapping(lattice["col_x"], lattice["col_y"])
    pixel_to_col = assign_crop_pixels(lattice, mapping)
    neighbors = axial_neighbors(lattice)
    sh1, sh2 = plane_to_axial(patch["x"][score_idx], patch["y"][score_idx])
    scored_pairs = np.stack(
        [np.round(sh1).astype(np.int64), np.round(sh2).astype(np.int64)],
        axis=1,
    )
    axial_of = {tuple(a): k for k, a in enumerate(lattice["axial"])}
    cell_col = np.array(
        [axial_of.get(tuple(p), -1) for p in scored_pairs], dtype=np.int64
    )
    in_lattice = cell_col >= 0
    cell_col = cell_col[in_lattice]
    scored_in = score_idx[in_lattice]
    pref_vec = np.stack(
        [pref_of_subtype[t] for t in score_types[in_lattice]]
    )
    log(f"lattice: {lattice['n_cols']} columns; pixels assigned "
        f"{float((pixel_to_col >= 0).mean()):.3f} of crop; scored cells "
        f"in-lattice {int(in_lattice.sum())}/{score_idx.size}")

    # Sequence, windows, split.
    seq = find_sequence(args.data_root, args.sequence)
    if seq is None:
        log("BLOCKED -- no complete sequence (flow/forward + "
            "forward_timestamps.txt + events/left/events.h5) under "
            f"{args.data_root}")
        return 3
    windows = load_windows(seq, WINDOW_CAP)
    n_cal = max(int(round(CAL_FRACTION * len(windows))), 1)
    cal_ids = list(range(n_cal))
    eval_ids = list(range(n_cal, len(windows)))
    log(f"sequence {seq['name']}: {len(windows)} windows "
        f"(cal {len(cal_ids)} / eval {len(eval_ids)}); rectify map: "
        f"{'yes' if seq['rectify'] else 'MISSING (raw coords, recorded)'}")

    rect_map = None
    if seq["rectify"]:
        with h5py.File(seq["rectify"], "r") as f:
            rect_map = np.asarray(f["rectify_map"])

    # Pass 1: GT binning + event binning per window (finest grid for
    # re-aggregation; sub-window sums re-bin exactly for coarser dts
    # because every dt in the grid divides the window).
    n_sub_max = None
    per_window: list[dict] = []
    h5 = h5py.File(seq["events"], "r")
    crop_x0 = (640 - CROP) // 2
    crop_y0 = (480 - CROP) // 2
    for i, win in enumerate(windows):
        flow, valid = dm.read_flow_png(win["png"])
        gt_vec, evaluable, med_mag = bin_gt_to_columns(
            flow, valid, pixel_to_col, lattice["n_cols"], crop_x0, crop_y0
        )
        x, y, p, t = event_slice(h5, win["t0_us"], win["t1_us"])
        if rect_map is not None and x.size:
            x, y = rectify_events(x, y, rect_map, 640, 480)
        duration_ms = (win["t1_us"] - win["t0_us"]) / 1000.0
        if n_sub_max is None:
            n_sub_max = max(int(round(duration_ms / DT_SUB_GRID_MS[0])), 1)
        signed, counts = bin_window_events(
            x, y, p, t, win["t0_us"], win["t1_us"], n_sub_max,
            pixel_to_col, lattice["n_cols"], crop_x0, crop_y0,
        )
        per_window.append({
            "gt_vec": gt_vec, "evaluable": evaluable,
            "gt_median_mag": med_mag, "signed": signed, "counts": counts,
            "duration_ms": duration_ms, "n_events": int(counts.sum()),
            "window_evaluable": bool(evaluable.sum() >= MIN_EVAL_COLUMNS),
        })
        if i % 50 == 0:
            log(f"  window {i}: {int(counts.sum())} events, "
                f"{int(evaluable.sum())} evaluable cols, med |gt| "
                f"{med_mag:.2f}px")
    h5.close()

    n_eval_ok = sum(per_window[i]["window_evaluable"] for i in eval_ids)
    log(f"evaluable EVAL windows: {n_eval_ok} (need >= {MIN_EVAL_WINDOWS})")

    # Drive normalization scalar (declared operationalization, header).
    col_npix = np.bincount(
        pixel_to_col[pixel_to_col >= 0].ravel(), minlength=lattice["n_cols"]
    ).astype(np.float64)
    col_npix = np.maximum(col_npix, 1.0)
    end_sums = np.stack([
        per_window[i]["signed"].sum(axis=0) / col_npix for i in cal_ids
    ])
    norm = float(np.percentile(np.abs(end_sums), NORM_PERCENTILE))
    norm = norm if norm > 1e-12 else 1.0
    log(f"drive normalization: p{NORM_PERCENTILE:.0f} |end-of-window "
        f"column mean| on CAL = {norm:.4f}")

    n_nodes = types.shape[0]
    driven_cols = lattice["cell_col"]

    def drives_for(ids, dt_sub):
        """(len(ids), n_sub, n_nodes) cumulative normalized drive."""
        out = []
        # dt grid members are integer multiples of the finest dt, so the
        # finest binning re-aggregates exactly (10 -> 10/5/2/1 sub-windows
        # for a 100 ms window); a remainder that does not divide evenly is
        # dropped from the last sub-window and the same rule applies to
        # every arm.
        factor = max(int(round(dt_sub / DT_SUB_GRID_MS[0])), 1)
        for i in ids:
            w = per_window[i]
            n_sub = max(w["signed"].shape[0] // factor, 1)
            s = w["signed"][:n_sub * factor].reshape(n_sub, factor, -1).sum(1)
            cum = np.cumsum(s, axis=0) / col_npix[None, :] / norm
            d = np.zeros((n_sub, n_nodes))
            d[:, driven_idx] = fc2.INPUT_DRIVE * cum[:, driven_cols]
            out.append(d)
        n_sub = max(dd.shape[0] for dd in out)
        padded = np.zeros((len(out), n_sub, n_nodes))
        for j, dd in enumerate(out):
            padded[j, :dd.shape[0]] = dd
            if dd.shape[0] < n_sub:          # hold the last drive
                padded[j, dd.shape[0]:] = dd[-1]
        return padded

    # Simulated arms: (label, matrix, table, gain).
    real_matrix, coverage = fc25.trained_weight_matrix(
        fc2, patch, {p_: v["subset_mean"] for p_, v in params["pairs"].items()}
    )
    table_real = fc25.trained_table(fc2, params, "subset", None)
    table_twin = fc25.trained_table(fc2, params, "subset", fc25.UNIFORM_TAU)
    from flygi.connectome.nulls import degree_preserving_rewire
    arms: list[tuple[str, Any, Any, float]] = [
        ("real", real_matrix, table_real, gain_real),
        ("uniform_tau", real_matrix, table_twin, gain_twin),
    ]
    for s in REWIRE_SEEDS:
        rewired, _stats = degree_preserving_rewire(
            real_matrix, seed=REWIRE_SEED_BASE + s
        )
        arms.append((f"rewired_{s}", rewired, table_real, gain_real))
    log(f"alpha coverage: {coverage['pairs_trained']}/"
        f"{coverage['pairs_total']} pairs trained")

    def arm_window_errors(arm, ids, dt_sub, keep_votes: bool = False):
        label, matrix, table, gain = arm
        drives = drives_for(ids, dt_sub)
        evoked, bad = simulate_arm_windows(
            fc2, matrix, types, table, gain, drives, scored_in,
            dt_sub, log, label,
        )
        errs = np.full(len(ids), np.nan)
        votes_kept: list = [None] * len(ids)
        for j, i in enumerate(ids):
            w = per_window[i]
            if bad[j] or not w["window_evaluable"]:
                continue
            votes, _cov = population_vote(
                evoked[j], cell_col, pref_vec, lattice["n_cols"]
            )
            errs[j] = window_mean_ae(votes, w["gt_vec"], w["evaluable"])
            if keep_votes:
                votes_kept[j] = votes
        return (errs, bad, votes_kept) if keep_votes else (errs, bad)

    # CAL: each simulated arm picks its own dt (matched freedom, frozen).
    chosen_dt: dict[str, float] = {}
    cal_record: dict[str, Any] = {}
    for arm in arms:
        label = arm[0]
        best_dt, best_err = None, np.inf
        row = {}
        for dt_sub in DT_SUB_GRID_MS:
            errs, _bad = arm_window_errors(arm, cal_ids, dt_sub)
            mean_err = float(np.nanmean(errs)) if np.isfinite(errs).any() \
                else float("inf")
            row[str(dt_sub)] = mean_err
            if mean_err < best_err:
                best_err, best_dt = mean_err, dt_sub
        if best_dt is None:      # no finite CAL error anywhere: recorded,
            best_dt = DT_SUB_GRID_MS[0]  # not a crash; EVAL will show it
        chosen_dt[label] = best_dt
        cal_record[label] = {"per_dt_mean_ae": row, "chosen_dt_ms": best_dt}
        log(f"[cal] {label}: chosen dt {best_dt} ms (mean AE {best_err:.2f})")

    # EVAL: simulated arms at their chosen dts; unstable windows drop
    # from every arm (pairing preserved).
    eval_errs: dict[str, np.ndarray] = {}
    real_votes: list = []
    bad_any = np.zeros(len(eval_ids), dtype=bool)
    for arm in arms:
        if arm[0] == "real":
            errs, bad, real_votes = arm_window_errors(
                arm, eval_ids, chosen_dt[arm[0]], keep_votes=True
            )
        else:
            errs, bad = arm_window_errors(arm, eval_ids, chosen_dt[arm[0]])
        eval_errs[arm[0]] = errs
        bad_any |= bad
    for label in eval_errs:
        eval_errs[label][bad_any] = np.nan
    null_mean = np.nanmean(
        np.stack([eval_errs[f"rewired_{s}"] for s in REWIRE_SEEDS]), axis=0
    )

    # Non-simulated arms on EVAL (dt-free by construction).
    trivial3 = np.full(len(eval_ids), np.nan)
    engineered = np.full(len(eval_ids), np.nan)
    gt_median_dir = np.full(len(eval_ids), np.nan)
    epe_rows: dict[str, list] = {"zero_flow": [], "real_scaled": [],
                                 "trivial3_scaled": []}

    def scaled_epe(est_vec, w):
        """EPE context (killtest_design.md): direction-only arms scaled
        by the window's median GT magnitude; mean over evaluable columns
        with a defined estimate."""
        ok = w["evaluable"] & np.isfinite(est_vec).all(axis=1) \
            & (np.linalg.norm(est_vec, axis=1) > 1e-12)
        if not ok.any() or not np.isfinite(w["gt_median_mag"]):
            return float("nan")
        unit = est_vec[ok] / np.linalg.norm(est_vec[ok], axis=1)[:, None]
        est = unit * w["gt_median_mag"]
        return float(np.mean(np.linalg.norm(est - w["gt_vec"][ok], axis=1)))

    for j, i in enumerate(eval_ids):
        w = per_window[i]
        if bad_any[j] or not w["window_evaluable"]:
            continue
        third = max(w["counts"].shape[0] // 3, 1)
        first = w["counts"][:third].sum(axis=0)
        last = w["counts"][-third:].sum(axis=0)
        est3 = centroid_shift_directions(first, last, lattice, neighbors)
        trivial3[j] = window_mean_ae(est3, w["gt_vec"], w["evaluable"])
        shift = cross_correlation_shift(first, last, lattice)
        est_e = np.broadcast_to(shift, (lattice["n_cols"], 2))
        engineered[j] = window_mean_ae(est_e, w["gt_vec"], w["evaluable"])
        med = np.nanmedian(w["gt_vec"][w["evaluable"]], axis=0)
        est_m = np.broadcast_to(med, (lattice["n_cols"], 2))
        gt_median_dir[j] = window_mean_ae(est_m, w["gt_vec"], w["evaluable"])
        epe_rows["zero_flow"].append(float(np.mean(
            np.linalg.norm(w["gt_vec"][w["evaluable"]], axis=1)
        )))
        if real_votes[j] is not None:
            epe_rows["real_scaled"].append(scaled_epe(real_votes[j], w))
        epe_rows["trivial3_scaled"].append(scaled_epe(est3, w))

    # Verdict (frozen rule).
    n_eval_usable = int(np.isfinite(eval_errs["real"]).sum())
    blocked = n_eval_usable < MIN_EVAL_WINDOWS
    test_vs_trivial3 = paired_sign_test_less(eval_errs["real"], trivial3)
    test_vs_null = paired_sign_test_less(eval_errs["real"], null_mean)
    med_real = float(np.nanmedian(eval_errs["real"]))
    med_t3 = float(np.nanmedian(trivial3))
    med_null = float(np.nanmedian(null_mean))
    bar1 = test_vs_trivial3["p"] < ALPHA and med_real < med_t3
    bar2 = test_vs_null["p"] < ALPHA and med_real < med_null
    verdict = ("BLOCKED" if blocked
               else "PASS" if (bar1 and bar2) else "KILL")

    report = {
        "hypothesis": "H-T4T5-DSEC-DIRECTION",
        "registration": "docs/arenas/task2_dsec_flow/killtest_design.md "
                        "(frozen 2026-10-01, before data)",
        "sequence": seq["name"],
        "windows": {"total": len(windows), "cal": len(cal_ids),
                    "eval": len(eval_ids),
                    "eval_usable": n_eval_usable,
                    "unstable_dropped": int(bad_any.sum())},
        "lattice": {"n_cols": lattice["n_cols"],
                    "crop": CROP,
                    "units_per_px": mapping["units_per_px"],
                    "pixels_assigned_fraction":
                        float((pixel_to_col >= 0).mean())},
        "drive_norm": norm,
        "alpha_coverage": coverage,
        "calibration": cal_record,
        "eval_median_mean_ae_deg": {
            "real": med_real,
            "uniform_tau": float(np.nanmedian(eval_errs["uniform_tau"])),
            "rewired_mean": med_null,
            "trivial3_event_centroid": med_t3,
            "engineered_xcorr": float(np.nanmedian(engineered)),
            "gt_median_direction": float(np.nanmedian(gt_median_dir)),
        },
        "epe_context_px_mean": {
            k: (float(np.nanmean(v)) if v else float("nan"))
            for k, v in epe_rows.items()
        },
        "sign_tests": {"real_vs_trivial3": test_vs_trivial3,
                       "real_vs_rewired_mean": test_vs_null},
        "bars": {"beats_trivial3": bool(bar1), "beats_null": bool(bar2)},
        "verdict": verdict,
        "elapsed_s": round(time.time() - started, 1),
    }
    args.output.write_text(json.dumps(report, indent=2))
    log(json.dumps(report["eval_median_mean_ae_deg"], indent=2))
    log(f"VERDICT: {verdict} (bars: trivial3={bar1}, null={bar2}; "
        f"usable EVAL windows {n_eval_usable})")
    handle.close()
    return 0 if verdict != "BLOCKED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
