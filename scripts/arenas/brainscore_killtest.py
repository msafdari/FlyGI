#!/usr/bin/env python3
"""H-EARLYFILTER-BRAINSCORE-V1 -- the Task 5 (Brain-Score) kill test.

PREREGISTRATION (EXPERIMENTS.yaml H-EARLYFILTER-BRAINSCORE-V1 and
docs/arenas/task5_brainscore/killtest_design.md, both 2026-10-04,
frozen BEFORE this file existed; restated, not changed):

  - ONE public benchmark: FreemanZiemba2013public.V1-pls, loaded
    through brainscore-vision's public pool on the local host. Their
    stimuli, their PLS metric, their ceiling, their cross-validation
    -- no reimplementation.
  - Circuit under test: the fc25 class-2.5 patch's EARLY-FILTER
    population (the 13 INPUT_TYPES). Scored cells = INPUT_TYPES within
    the central 9x9 hex window (SCORE_HALF=4 around PATCH_CENTER);
    T4/T5 are excluded from features.
  - ONE declared drive convention (AB-4, no sweep): image -> grayscale
    (Rec. 601 if RGB) -> bilinear 128x128 -> per-column mean luminance
    over the DSEC identity-crop pixel assignment -> drive =
    (column mean - 0.5), constant for 250 ms, through L1/L2/L3 at
    INPUT_DRIVE (-1.0). Settle 2500 ms at zero drive once per arm;
    250 ms zero tail. Features = rectified evoked integrals of scored
    cells over stimulus + tail vs the settled baseline.
  - Arms: REAL (fc25 trained_subset, verbatim gain) / TWIN
    (uniform-tau, its own gain; attribution context, decides nothing)
    / NULL (degree-preserving rewire per seed 0,1,2, base 4242, real
    table+gain) / PASSTHROUGH (the per-column drive vector itself,
    n_cols dims -- the circuit's own input as features).
  - PASS iff (1) REAL ceiled center > 0 AND center - reported error
    > 0; (2) REAL center > NULL center for ALL THREE rewire seeds;
    (3) REAL center > PASSTHROUGH center. KILL otherwise -- no
    retries, no tuning, no second benchmark, no submission on a KILL.
  - BLOCKED (exit 3): brainscore-vision not importable / benchmark or
    its data not loadable; < 100 stimuli; > 20% unstable presentations
    in any simulated arm; an API mismatch blocking the metric call.

Data gate: runs where the compiled runtime, the fc25 passing result
and the brainscore-vision package live (the cloud container has none
of them). Exits 3 with a BLOCKED report otherwise.

Run:    python scripts/arenas/brainscore_killtest.py
Output: results/arenas/brainscore_killtest.json (+ .log)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BENCH = ROOT / "scripts/benchmarks"
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- frozen constants (killtest_design.md; do not tune) ---------------------
BENCHMARK_ID = "FreemanZiemba2013public.V1-pls"
RECORDING_TARGET = "V1"      # hard-assigned; no region search (design)
IMAGE_SIZE = 128             # reuses the DVS identity-crop machinery
STIM_MS = 250.0
TAIL_MS = 250.0
MID_GRAY = 0.5
SEEDS = (0, 1, 2)
REWIRE_SEED_BASE = 4242
MIN_STIMULI = 100
MAX_UNSTABLE_FRACTION = 0.20
LUMA = (0.299, 0.587, 0.114)  # Rec. 601

FC25_RESULTS = ROOT / "results/benchmarks/fc25_visual_ds.json"
PARAMS_JSON = ROOT / "docs/fidelity2/flyvis_trained_params.json"
RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
ANNOTATIONS = ROOT / "data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT_JSON = ROOT / "results/arenas/brainscore_killtest.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Pure plumbing (unit-tested in-cloud; no benchmark package needed)
# ---------------------------------------------------------------------------

def to_gray(img: np.ndarray) -> np.ndarray:
    """Float [0, 1] grayscale from HxW / HxWx1 / HxWx3 / HxWx4 arrays
    (alpha dropped), uint8 or float input. Rec. 601 luma for color."""
    arr = np.asarray(img, dtype=np.float64)
    if np.issubdtype(np.asarray(img).dtype, np.integer):
        arr = arr / 255.0
    if arr.ndim == 3:
        if arr.shape[2] == 1:
            arr = arr[:, :, 0]
        else:
            arr = (LUMA[0] * arr[:, :, 0] + LUMA[1] * arr[:, :, 1]
                   + LUMA[2] * arr[:, :, 2])
    return np.clip(arr, 0.0, 1.0)


def bilinear_resize(gray: np.ndarray, size: int) -> np.ndarray:
    """Pure-numpy bilinear resample to (size, size), pixel-center
    aligned. Deterministic by construction -- the declared convention
    does not depend on a library's resize semantics."""
    h, w = gray.shape
    if (h, w) == (size, size):
        return gray.astype(np.float64)
    ys = (np.arange(size) + 0.5) * (h / size) - 0.5
    xs = (np.arange(size) + 0.5) * (w / size) - 0.5
    y0 = np.clip(np.floor(ys).astype(int), 0, h - 1)
    x0 = np.clip(np.floor(xs).astype(int), 0, w - 1)
    y1 = np.minimum(y0 + 1, h - 1)
    x1 = np.minimum(x0 + 1, w - 1)
    wy = np.clip(ys - y0, 0.0, 1.0)[:, None]
    wx = np.clip(xs - x0, 0.0, 1.0)[None, :]
    g = gray.astype(np.float64)
    top = g[y0[:, None], x0[None, :]] * (1 - wx) + g[y0[:, None], x1[None, :]] * wx
    bot = g[y1[:, None], x0[None, :]] * (1 - wx) + g[y1[:, None], x1[None, :]] * wx
    return top * (1 - wy) + bot * wy


def column_drive(gray: np.ndarray, pixel_to_col: np.ndarray,
                 n_cols: int) -> np.ndarray:
    """Per-column drive = mean luminance over the column's assigned
    pixels, minus MID_GRAY (the declared contrast-about-mid-gray
    convention). ASSUMPTION: a column with no assigned pixels gets zero
    contrast drive (not -MID_GRAY); on the 13x13 lattice under the
    128-crop every column has pixels, so this branch should never carry
    signal -- it exists so an empty column cannot inject a dark edge."""
    flat_col = pixel_to_col.ravel()
    ok = flat_col >= 0
    sums = np.bincount(flat_col[ok], weights=gray.ravel()[ok],
                       minlength=n_cols)
    counts = np.bincount(flat_col[ok], minlength=n_cols).astype(np.float64)
    mean = np.where(counts > 0, sums / np.maximum(counts, 1.0), MID_GRAY)
    return mean - MID_GRAY


def early_filter_indices(types: np.ndarray, x: np.ndarray, y: np.ndarray,
                         input_types, center, half: float) -> np.ndarray:
    """Scored population: INPUT_TYPES cells within the central hex
    window. The patch stores the planar embedding x = h1 + h2/2,
    y = (sqrt(3)/2) h2; inverted here. The 1e-9 tolerance exists
    because the round trip through the embedding moves a cell at
    exactly |dh| = half to half + O(eps); build_patch selects on raw
    hex coords and never faces this, so without the tolerance the two
    selections would disagree on boundary cells (caught by unit test
    before any data contact)."""
    h2 = y / (3 ** 0.5 / 2.0)
    h1 = x - 0.5 * h2
    tol = half + 1e-9
    inside = (np.abs(h1 - center[0]) <= tol) & (np.abs(h2 - center[1]) <= tol)
    return np.flatnonzero(inside & np.isin(types, tuple(input_types)))


def score_center_error(score: Any) -> tuple[float, float]:
    """Extract (center, error) from a Brain-Score Score across the API
    shapes the package has shipped: an xarray with an `aggregation`
    dim, a scalar with an `error` attr, or a plain float. A missing
    error comes back as NaN; the verdict treats NaN error as 0.0 and
    records that it was unavailable (killtest_design.md bar 1)."""
    try:
        agg = getattr(score, "sel", None)
        if agg is not None and "aggregation" in getattr(score, "dims", ()):
            center = float(score.sel(aggregation="center").values)
            try:
                error = float(score.sel(aggregation="error").values)
            except Exception:
                error = float("nan")
            return center, error
    except Exception:
        pass
    attrs = getattr(score, "attrs", {}) or {}
    error = float("nan")
    if "error" in attrs:
        try:
            error = float(np.asarray(attrs["error"]).item())
        except Exception:
            error = float("nan")
    try:
        center = float(np.asarray(getattr(score, "values", score)).item())
    except Exception:
        center = float(score)
    return center, error


def assemble_verdict(scores: dict) -> dict:
    """The frozen three-bar rule on arm scores. `scores` maps
    "real"/"twin"/"passthrough" -> {"center", "error"} and "null" -> a
    list of three {"center", ...} (seed order). The twin decides
    nothing."""
    real_c = scores["real"]["center"]
    real_e = scores["real"].get("error", float("nan"))
    err = 0.0 if (real_e is None or math.isnan(real_e)) else real_e
    null_centers = [s["center"] for s in scores["null"]]
    bars = {
        "real_above_floor": bool(real_c > 0.0 and real_c - err > 0.0),
        "real_beats_null_all_seeds": bool(
            len(null_centers) == len(SEEDS)
            and all(real_c > n for n in null_centers)),
        "real_beats_passthrough": bool(
            real_c > scores["passthrough"]["center"]),
    }
    return {
        "bars": bars,
        "real_error_available": not (real_e is None or math.isnan(real_e)),
        "verdict": "PASS" if all(bars.values()) else "KILL",
    }


def check_prerequisites() -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not ANNOTATIONS.exists():
        missing.append(f"raw annotations feather: {ANNOTATIONS}")
    if not PARAMS_JSON.exists():
        missing.append(f"trained flyvis params: {PARAMS_JSON}")
    if not FC25_RESULTS.exists():
        missing.append(f"fc25 passing result (local-only): {FC25_RESULTS}")
    for mod in ("pyarrow", "scipy", "sklearn", "brainscore_vision"):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    return missing


# ---------------------------------------------------------------------------
# Data-gated assembly (local host only)
# ---------------------------------------------------------------------------

def resolve_visual_degrees(benchmark) -> float:
    """The declared rule (killtest_design.md): the model reports
    visual_degrees equal to the benchmark's stimulus presentation
    degrees, so each image fills the patch window exactly. Probed from
    the benchmark object; failure to find one is an API mismatch ->
    BLOCKED upstream, never a guessed number."""
    for attr in ("visual_degrees", "_visual_degrees"):
        got = getattr(benchmark, attr, None)
        if got is None:
            continue
        value = got() if callable(got) else got
        if value is not None:
            return float(value)
    raise ApiMismatch(
        "could not resolve the benchmark's stimulus presentation degrees "
        f"from {type(benchmark).__name__} (tried visual_degrees / "
        "_visual_degrees)")


class ApiMismatch(RuntimeError):
    """A brainscore-vision API shape this instrument does not know.
    BLOCKED per the registration, never a verdict."""


def load_image_gray(path: Path) -> np.ndarray:
    try:
        from PIL import Image
        with Image.open(path) as im:
            return to_gray(np.asarray(im))
    except ImportError:
        import cv2
        arr = cv2.imread(str(path), cv2.IMREAD_UNCHANGED)
        if arr is None:
            raise IOError(f"unreadable image: {path}")
        if arr.ndim == 3 and arr.shape[2] >= 3:
            arr = arr[:, :, 2::-1]       # BGR -> RGB
        return to_gray(arr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-EARLYFILTER-BRAINSCORE-V1 kill test (data-gated)")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites()
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("Run where the compiled runtime, the fc25 result and "
              "brainscore-vision live "
              "(docs/arenas/task5_brainscore/runbook.md).")
        return 3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    dk = _load_module("dsec_killtest", HERE / "dsec_killtest.py")
    fc25 = _load_module("fc25_visual_ds", BENCH / "fc25_visual_ds.py")
    fc2 = fc25.load_fc2()
    params = json.loads(PARAMS_JSON.read_text())
    fc25_results = json.loads(FC25_RESULTS.read_text())
    passing = next(c for c in fc25_results["configs"]
                   if c["label"] == "trained_subset")
    assert passing["result"]["readout_v2_crossing_window"]["pass"] is True
    gain_real = passing["calibration"]["chosen_gain"]
    gain_twin = fc25_results["trivial_alternative"]["calibration"]["chosen_gain"]

    # Patch + lattice + identity-crop pixel assignment (DSEC machinery,
    # exactly the DVS construction at crop = IMAGE_SIZE).
    patch = fc2.build_patch()
    types = patch["types"]
    driven_idx = np.flatnonzero(np.isin(types, fc2.DRIVEN_TYPES))
    lattice = dk.build_lattice(patch["x"][driven_idx], patch["y"][driven_idx])
    mapping = dk.crop_mapping(lattice["col_x"], lattice["col_y"],
                              crop=IMAGE_SIZE)
    pixel_to_col = dk.assign_crop_pixels(lattice, mapping)
    n_cols = lattice["n_cols"]
    driven_cols = lattice["cell_col"]
    n_nodes = types.shape[0]
    score_idx = early_filter_indices(
        types, patch["x"], patch["y"], fc2.INPUT_TYPES, fc2.PATCH_CENTER,
        float(fc2.SCORE_HALF))
    empty_cols = int((np.bincount(
        pixel_to_col[pixel_to_col >= 0].ravel(), minlength=n_cols) == 0).sum())
    log(f"lattice: {n_cols} columns ({empty_cols} without pixels); "
        f"{score_idx.size} scored early-filter cells of {n_nodes} nodes; "
        f"pixels assigned {float((pixel_to_col >= 0).mean()):.3f}")

    real_matrix, _cov = fc25.trained_weight_matrix(
        fc2, patch, {p_: v["subset_mean"] for p_, v in params["pairs"].items()})
    table_real = fc25.trained_table(fc2, params, "subset", None)
    table_twin = fc25.trained_table(fc2, params, "subset", fc25.UNIFORM_TAU)
    from flygi.connectome.nulls import degree_preserving_rewire

    stim_steps = int(round(STIM_MS / fc2.DT_MS))
    tail_steps = int(round(TAIL_MS / fc2.DT_MS))
    unstable: dict[str, float] = {}

    def simulate(matrix, table, gain, drives, label):
        """Batched settle-stream-tail at CONSTANT drive per stimulus
        (the fc2 dynamics verbatim; the DVS batching with one
        sub-window). drives: (m, n_cols) column contrasts."""
        t0 = time.time()
        m = drives.shape[0]
        net = fc2.GradedFlyvisNetwork(matrix, types, table,
                                      dt_ms=fc2.DT_MS, gain=gain)
        for _ in range(int(round(fc2.SETTLE_MS / fc2.DT_MS))):
            net.step(np.zeros(n_nodes))
        settled = net.v.copy()
        base_out = np.maximum(settled, 0.0)[score_idx]
        net.tau = net.tau[:, None]
        net.v_rest = net.v_rest[:, None]
        net.v = np.repeat(settled[:, None], m, axis=1)
        bad = np.zeros(m, dtype=bool)
        total = np.zeros((score_idx.size, m))
        drive = np.zeros((n_nodes, m))
        drive[driven_idx, :] = fc2.INPUT_DRIVE * drives[:, driven_cols].T
        zero = np.zeros_like(drive)
        step = 0
        with np.errstate(over="ignore", invalid="ignore"):
            for phase_steps, phase_drive in ((stim_steps, drive),
                                             (tail_steps, zero)):
                for _ in range(phase_steps):
                    net.step(phase_drive)
                    step += 1
                    if step % 50 == 0:
                        finite = np.isfinite(net.v).all(axis=0)
                        bad |= ~finite | (np.where(
                            finite, np.abs(np.where(np.isfinite(net.v),
                                                    net.v, 0.0)).max(axis=0),
                            np.inf) > fc2.V_ABORT)
                    total += np.maximum(
                        np.maximum(net.v, 0.0)[score_idx, :]
                        - base_out[:, None],
                        0.0) * (fc2.DT_MS / 1000.0)
        unstable[label] = float(bad.mean()) if m else 0.0
        log(f"  [{label}] {m} stimuli in {time.time() - t0:.1f}s, "
            f"unstable {int(bad.sum())}")
        return total.T.copy()            # (m, n_scored)

    # --- everything from here touches brainscore-vision: API mismatch
    # or data failure is BLOCKED, never a verdict ------------------------
    try:
        import brainscore_vision
        from brainio.assemblies import NeuroidAssembly

        benchmark = brainscore_vision.load_benchmark(BENCHMARK_ID)
        degrees = resolve_visual_degrees(benchmark)
        log(f"benchmark {BENCHMARK_ID} loaded; visual degrees {degrees}")

        stim_cache: dict[str, np.ndarray] = {}

        def stimulus_path(stimuli, sid: str) -> Path:
            for accessor in ("get_stimulus", "get_image"):
                got = getattr(stimuli, accessor, None)
                if got is not None:
                    return Path(got(sid))
            raise ApiMismatch(
                "stimulus set exposes neither get_stimulus nor get_image")

        def drives_for(stimuli) -> tuple[np.ndarray, list[str]]:
            id_col = ("stimulus_id" if "stimulus_id" in stimuli.columns
                      else "image_id")
            ids = [str(s) for s in stimuli[id_col].values]
            rows = []
            for sid in ids:
                if sid not in stim_cache:
                    gray = bilinear_resize(
                        load_image_gray(stimulus_path(stimuli, sid)),
                        IMAGE_SIZE)
                    stim_cache[sid] = column_drive(gray, pixel_to_col, n_cols)
                rows.append(stim_cache[sid])
            return np.stack(rows), ids

        class EvokedFeatureModel:
            """Minimal BrainModel: precomputable features behind the
            public start_recording / look_at / visual_degrees contract.
            Plumbing only -- every number comes from the simulated
            patch or the declared drive."""

            def __init__(self, identifier: str, features_fn):
                self.identifier = identifier
                self._features_fn = features_fn
                self._time_bins = None

            def visual_degrees(self) -> float:
                return degrees

            def start_task(self, *a, **k):
                raise ApiMismatch(
                    f"{BENCHMARK_ID} requested a behavioral task; this "
                    "instrument registers a neural recording model only")

            def start_recording(self, recording_target, time_bins=None,
                                **_kwargs):
                if str(recording_target) != RECORDING_TARGET:
                    raise ApiMismatch(
                        f"benchmark asked to record {recording_target!r}; "
                        f"the registration hard-assigns {RECORDING_TARGET}")
                self._time_bins = ([tuple(b) for b in time_bins]
                                   if time_bins is not None else None)

            def look_at(self, stimuli, number_of_trials=1, **_kwargs):
                feats, ids = self._features_fn(stimuli)
                n_stim, n_feat = feats.shape
                pres_coords = {
                    col: ("presentation", np.asarray(stimuli[col].values))
                    for col in stimuli.columns}
                neuroid_ids = [f"{self.identifier}-n{i}"
                               for i in range(n_feat)]
                coords = dict(pres_coords)
                coords["neuroid_id"] = ("neuroid", neuroid_ids)
                coords["region"] = ("neuroid",
                                    [RECORDING_TARGET] * n_feat)
                if self._time_bins:
                    # Declared (killtest_design.md): identical features
                    # for every requested bin -- the evoked integrals
                    # are not primate-latency-resolved.
                    nb = len(self._time_bins)
                    data = np.repeat(feats[:, :, None], nb, axis=2)
                    coords["time_bin_start"] = (
                        "time_bin", [b[0] for b in self._time_bins])
                    coords["time_bin_end"] = (
                        "time_bin", [b[1] for b in self._time_bins])
                    assembly = NeuroidAssembly(
                        data, coords=coords,
                        dims=["presentation", "neuroid", "time_bin"])
                else:
                    assembly = NeuroidAssembly(
                        data=feats, coords=coords,
                        dims=["presentation", "neuroid"])
                return assembly

        def circuit_fn(matrix, table, gain, label):
            def fn(stimuli):
                drives, ids = drives_for(stimuli)
                return simulate(matrix, table, gain, drives, label), ids
            return fn

        def passthrough_fn(stimuli):
            drives, ids = drives_for(stimuli)
            return drives, ids

        def run_arm(label, features_fn):
            model = EvokedFeatureModel(f"flygi-earlyfilter-{label}",
                                       features_fn)
            score = benchmark(model)
            center, error = score_center_error(score)
            log(f"[{label}] center {center:.4f} error {error:.4f}")
            return {"center": center, "error": error}

        scores: dict[str, Any] = {
            "real": run_arm("real", circuit_fn(real_matrix, table_real,
                                               gain_real, "real")),
            "twin": run_arm("twin", circuit_fn(real_matrix, table_twin,
                                               gain_twin, "twin")),
            "passthrough": run_arm("passthrough", passthrough_fn),
        }
        scores["null"] = []
        for seed in SEEDS:
            rewired, _ = degree_preserving_rewire(
                real_matrix, seed=REWIRE_SEED_BASE + seed)
            scores["null"].append(run_arm(
                f"null{seed}", circuit_fn(rewired, table_real, gain_real,
                                          f"null{seed}")))

        n_stimuli = len(stim_cache)
        if n_stimuli < MIN_STIMULI:
            log(f"BLOCKED: only {n_stimuli} stimuli presented "
                f"(floor {MIN_STIMULI})")
            return 3
        worst_unstable = max(unstable.values()) if unstable else 0.0
        if worst_unstable > MAX_UNSTABLE_FRACTION:
            log(f"BLOCKED: unstable fraction {worst_unstable:.3f} exceeds "
                f"{MAX_UNSTABLE_FRACTION} "
                f"({max(unstable, key=unstable.get)})")
            return 3

    except ApiMismatch as exc:
        log(f"BLOCKED (API mismatch, not a verdict): {exc}")
        return 3
    except Exception:
        log("BLOCKED (benchmark/package failure, not a verdict):")
        log(traceback.format_exc())
        return 3

    out = assemble_verdict(scores)
    record = {
        "hypothesis": "H-EARLYFILTER-BRAINSCORE-V1",
        "benchmark": BENCHMARK_ID,
        "visual_degrees": degrees,
        "n_stimuli": n_stimuli,
        "n_scored_cells": int(score_idx.size),
        "n_cols": int(n_cols),
        "scores": scores,
        "unstable": unstable,
        "bars": out["bars"],
        "real_error_available": out["real_error_available"],
        "verdict": out["verdict"],
        "elapsed_s": round(time.time() - started, 1),
    }
    args.output.write_text(json.dumps(record, indent=2))
    log(json.dumps(record, indent=2))
    log(f"VERDICT: {out['verdict']}")
    handle.close()
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
