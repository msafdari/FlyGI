#!/usr/bin/env python3
"""H-T4T5-DVS-GESTURE -- the Task 4 (NeuroBench) kill test.

PREREGISTRATION (EXPERIMENTS.yaml H-T4T5-DVS-GESTURE and
docs/arenas/task4_neurobench/killtest_design.md, both 2026-10-03, frozen
BEFORE this file existed; restated, not changed):

  - IBM DVS128 Gesture, the dataset's OWN subject split
    (trials_to_train.txt / trials_to_test.txt -- held-out subjects by
    construction). TRAIN subsampled to 40 trials/class per seed
    (seeded); full TEST. BLOCKED below 600 train / 150 test parsed
    trials, or instability in >20% of any arm's windows.
  - 6 windows of 250 ms per trial, evenly spaced; events binned by the
    DSEC instrument's own functions on the 13x13 lattice (DVS128 is
    128x128: the central-crop map at crop=128 is the identity frame);
    pseudo-luminance = cumulative signed sums at a FIXED 10 ms
    sub-window; ONE drive-normalization scalar (95th pct |end-of-window
    column sum| over a seeded 50-trial TRAIN calibration subset),
    shared by every simulated arm.
  - fc2 settle-stream-tail, batched: settle 2500 ms at zero drive once
    per arm, stream 250 ms, 250 ms zero tail. Features per trial = the
    scored T4/T5 cells' evoked integrals averaged over windows.
  - Arms: REAL (fc25 trained_subset, verbatim gain) / TWIN
    (uniform-tau, its own gain; attribution context) / NULL
    (degree-preserving rewire per seed, real table+gain) / EVENT-COUNT
    (per column |count| total and net signed sum, 2 x n_cols dims --
    same binning, no circuit).
  - One probe for every arm: z-score(TRAIN), multinomial logistic L2
    lbfgs, C from (0.01, 0.1, 1.0, 10.0) by 3-fold CV on TRAIN.
  - PASS iff (1) REAL > 1/11 chance, binomial p<0.05, ALL 3 seeds;
    (2) REAL beats NULL; (3) REAL beats EVENT-COUNT -- (2)/(3) as
    one-sided paired sign tests over subject x seed accuracy cells,
    p<0.05, AND pooled accuracy higher in >=2 of 3 seeds. KILL
    otherwise; the neurobench package is never used for this decision.

Data gate: runs where the data and the compiled runtime live (the
cloud container has neither). Exits 3 with a BLOCKED report otherwise.

Run:    python scripts/arenas/dvs_killtest.py --data-root <DvsGesture dir>
Output: results/arenas/dvs_killtest.json (+ .log)
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import math
import struct
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BENCH = ROOT / "scripts/benchmarks"
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- frozen constants (killtest_design.md; do not tune) --------------------
SENSOR = 128                 # DVS128; square, so crop == full frame
WINDOWS_PER_TRIAL = 6
WINDOW_MS = 250.0
TAIL_MS = 250.0
DT_SUB_MS = 10.0             # fixed; the DSEC grid's finest, no sweep
TRAIN_PER_CLASS = 40
CAL_TRIALS = 50
NORM_PERCENTILE = 95.0
SEEDS = (0, 1, 2)
REWIRE_SEED_BASE = 4242
C_GRID = (0.01, 0.1, 1.0, 10.0)
ALPHA = 0.05
N_CLASSES = 11
MIN_TRAIN_TRIALS = 600
MIN_TEST_TRIALS = 150
MAX_UNSTABLE_FRACTION = 0.20

FC25_RESULTS = ROOT / "results/benchmarks/fc25_visual_ds.json"
PARAMS_JSON = ROOT / "docs/fidelity2/flyvis_trained_params.json"
RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
ANNOTATIONS = ROOT / "data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT_JSON = ROOT / "results/arenas/dvs_killtest.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# AEDAT 3.1 polarity reader (pure; unit-tested on synthetic packed bytes)
# ---------------------------------------------------------------------------

def read_aedat31_polarity(path_or_bytes):
    """Return (x, y, p, t_us) int64/float arrays for every valid polarity
    event in an AEDAT 3.1 file. Layout per the jAER/libcaer spec:
    '#'-prefixed header lines, then packets with a 28-byte little-endian
    header (type u16, source u16, eventSize u32, tsOffset u32,
    tsOverflow u32, capacity u32, number u32, valid u32); polarity
    packets are type 1, each event two u32 words: data (bit0 validity,
    bit1 polarity, bits 2-16 y, bits 17-31 x) and timestamp (us, plus
    tsOverflow << 31)."""
    data = (path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray))
            else Path(path_or_bytes).read_bytes())
    pos = 0
    while pos < len(data) and data[pos:pos + 1] == b"#":
        nl = data.find(b"\n", pos)
        if nl < 0:
            return (np.empty(0, np.int64),) * 2 + (np.empty(0, np.int64),
                                                   np.empty(0, np.float64))
        pos = nl + 1
    xs, ys, ps, ts = [], [], [], []
    while pos + 28 <= len(data):
        (etype, _src, esize, _tsoff, tsovf, _cap, enum, _evalid) = \
            struct.unpack_from("<HHIIIIII", data, pos)
        pos += 28
        payload = esize * enum
        if pos + payload > len(data):
            break
        if etype == 1 and esize == 8 and enum:
            arr = np.frombuffer(data, dtype="<u4",
                                count=2 * enum, offset=pos).reshape(enum, 2)
            d = arr[:, 0]
            valid = (d & 1) == 1
            xs.append(((d >> 17) & 0x7FFF)[valid].astype(np.int64))
            ys.append(((d >> 2) & 0x7FFF)[valid].astype(np.int64))
            ps.append(((d >> 1) & 0x1)[valid].astype(np.int64))
            ts.append((arr[:, 1].astype(np.int64)
                       + (np.int64(tsovf) << 31))[valid].astype(np.float64))
        pos += payload
    if not xs:
        return (np.empty(0, np.int64), np.empty(0, np.int64),
                np.empty(0, np.int64), np.empty(0, np.float64))
    return (np.concatenate(xs), np.concatenate(ys),
            np.concatenate(ps), np.concatenate(ts))


def window_starts(t0_us: float, t1_us: float,
                  n: int = WINDOWS_PER_TRIAL,
                  window_us: float = WINDOW_MS * 1000.0) -> np.ndarray:
    """Evenly spaced window starts inside a trial; trials shorter than
    1.5 s use as many full windows as fit (>=1 if one fits)."""
    duration = t1_us - t0_us
    fit = int(duration // window_us)
    k = min(n, max(fit, 0))
    if k <= 0:
        return np.empty(0, np.float64)
    if k == 1:
        return np.array([t0_us])
    return np.linspace(t0_us, t1_us - window_us, k)


def event_count_features(signed: np.ndarray, counts: np.ndarray) -> np.ndarray:
    """EVENT-COUNT arm: per column, total |events| and net signed sum
    over the window's sub-windows -> (2 * n_cols,)."""
    return np.concatenate([counts.sum(axis=0), signed.sum(axis=0)])


def exact_binomial_above_chance(correct: int, n: int,
                                p0: float = 1.0 / N_CLASSES) -> float:
    """One-sided exact binomial P[X >= correct | n, p0]."""
    if n == 0:
        return float("nan")
    return float(sum(math.comb(n, k) * p0 ** k * (1 - p0) ** (n - k)
                     for k in range(correct, n + 1)))


def assemble_verdict(per_seed: list[dict], cells: dict[str, np.ndarray],
                     paired_sign_test_less) -> dict:
    """The frozen three-bar rule on per-seed records + subject x seed
    accuracy cells. per_seed rows carry pooled accuracies and the chance
    p-value for REAL; cells map arm -> flat array over subject x seed."""
    chance_all = all(s["real_chance_p"] < ALPHA for s in per_seed)
    real_vs_null = paired_sign_test_less(cells["null"], cells["real"])
    real_vs_ec = paired_sign_test_less(cells["event_count"], cells["real"])
    null_maj = sum(s["real_acc"] > s["null_acc"] for s in per_seed) >= 2
    ec_maj = sum(s["real_acc"] > s["event_count_acc"] for s in per_seed) >= 2
    bars = {
        "real_above_chance_all_seeds": bool(chance_all),
        "real_beats_null": bool(real_vs_null["p"] < ALPHA and null_maj),
        "real_beats_event_count": bool(real_vs_ec["p"] < ALPHA and ec_maj),
    }
    return {
        "bars": bars,
        "sign_tests": {"real_vs_null": real_vs_null,
                       "real_vs_event_count": real_vs_ec},
        "verdict": "PASS" if all(bars.values()) else "KILL",
    }


# ---------------------------------------------------------------------------
# Data-gated assembly
# ---------------------------------------------------------------------------

def check_prerequisites(data_root: Path | None) -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not ANNOTATIONS.exists():
        missing.append(f"raw annotations feather: {ANNOTATIONS}")
    if not PARAMS_JSON.exists():
        missing.append(f"trained flyvis params: {PARAMS_JSON}")
    if not FC25_RESULTS.exists():
        missing.append(f"fc25 passing result (local-only): {FC25_RESULTS}")
    for mod in ("pyarrow", "scipy", "sklearn"):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    if data_root is None:
        missing.append("--data-root (extracted DvsGesture directory)")
    elif not (Path(data_root) / "trials_to_train.txt").exists():
        missing.append(f"trials_to_train.txt not found under {data_root}")
    return missing


def load_split(data_root: Path, listing: str, log) -> list[dict]:
    """Parse every listed AEDAT file + its _labels.csv into trials."""
    trials = []
    names = [ln.strip() for ln in (data_root / listing).read_text().splitlines()
             if ln.strip()]
    for name in names:
        aedat = data_root / name
        labels = data_root / name.replace(".aedat", "_labels.csv")
        if not aedat.exists() or not labels.exists():
            log(f"  missing pair for {name}; skipped")
            continue
        x, y, p, t = read_aedat31_polarity(aedat)
        ok = (x < SENSOR) & (y < SENSOR)
        bad_frac = 1.0 - (float(ok.mean()) if x.size else 1.0)
        if bad_frac > 0.01:
            log(f"  {name}: {bad_frac:.1%} out-of-frame events (parser "
                f"sanity flag)")
        x, y, p, t = x[ok], y[ok], p[ok], t[ok]
        rows = np.loadtxt(labels, delimiter=",", skiprows=1, ndmin=2)
        for cls, t0, t1 in rows:
            trials.append({"file": name, "class": int(cls),
                           "t0": float(t0), "t1": float(t1),
                           "events": (x, y, p, t)})
    return trials


def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-T4T5-DVS-GESTURE kill test (data-gated)")
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites(args.data_root)
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("Run where the data and the compiled runtime live "
              "(docs/arenas/task4_neurobench/runbook.md).")
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

    # Patch + lattice + identity-crop pixel assignment (DSEC machinery).
    patch = fc2.build_patch()
    types = patch["types"]
    patch["driven_mask"] = np.isin(types, fc2.DRIVEN_TYPES)
    driven_idx = np.flatnonzero(patch["driven_mask"])
    score_idx = np.flatnonzero(np.isin(types, fc2.T4_SUBTYPES + fc2.T5_SUBTYPES))
    lattice = dk.build_lattice(patch["x"][driven_idx], patch["y"][driven_idx])
    mapping = dk.crop_mapping(lattice["col_x"], lattice["col_y"], crop=SENSOR)
    pixel_to_col = dk.assign_crop_pixels(lattice, mapping)
    n_cols = lattice["n_cols"]
    col_npix = np.maximum(np.bincount(
        pixel_to_col[pixel_to_col >= 0].ravel(), minlength=n_cols
    ).astype(np.float64), 1.0)
    driven_cols = lattice["cell_col"]
    n_nodes = types.shape[0]
    log(f"lattice: {n_cols} columns; {score_idx.size} scored cells; "
        f"pixels assigned {float((pixel_to_col >= 0).mean()):.3f}")

    # Trials.
    train_all = load_split(args.data_root, "trials_to_train.txt", log)
    test_all = load_split(args.data_root, "trials_to_test.txt", log)
    log(f"parsed trials: train {len(train_all)}, test {len(test_all)}")
    if len(train_all) < MIN_TRAIN_TRIALS or len(test_all) < MIN_TEST_TRIALS:
        log(f"BLOCKED: parse floors not met "
            f"({len(train_all)}/{MIN_TRAIN_TRIALS} train, "
            f"{len(test_all)}/{MIN_TEST_TRIALS} test)")
        return 3

    n_sub = int(round(WINDOW_MS / DT_SUB_MS))

    def trial_windows(trial):
        """(k, n_sub, n_cols) signed and counts tensors for one trial."""
        x, y, p, t = trial["events"]
        starts = window_starts(trial["t0"], trial["t1"])
        signed = np.zeros((starts.size, n_sub, n_cols))
        counts = np.zeros_like(signed)
        for w, s0 in enumerate(starts):
            sg, ct = dk.bin_window_events(
                x, y, p, t, s0, s0 + WINDOW_MS * 1000.0, n_sub,
                pixel_to_col, n_cols, 0, 0)
            signed[w], counts[w] = sg, ct
        return signed, counts

    # One normalization scalar (seed-0 calibration subset; frozen).
    rng0 = np.random.default_rng(SEEDS[0])
    cal_ids = rng0.choice(len(train_all), size=min(CAL_TRIALS, len(train_all)),
                          replace=False)
    end_sums = []
    for i in cal_ids:
        sg, _ = trial_windows(train_all[i])
        if sg.size:
            end_sums.append(sg.sum(axis=1) / col_npix[None, :])
    norm = float(np.percentile(np.abs(np.concatenate(end_sums)),
                               NORM_PERCENTILE))
    norm = norm if norm > 1e-12 else 1.0
    log(f"drive norm (seed-0 cal subset, {len(cal_ids)} trials): {norm:.4f}")

    def drives_and_ec(trials):
        """Per trial: drive tensor list [(k, n_sub, n_nodes)] and
        event-count feature matrix (len(trials), 2*n_cols)."""
        drv, ec = [], []
        for trial in trials:
            sg, ct = trial_windows(trial)
            cum = np.cumsum(sg, axis=1) / col_npix[None, None, :] / norm
            d = np.zeros((sg.shape[0], n_sub, n_nodes))
            d[:, :, driven_idx] = fc2.INPUT_DRIVE * cum[:, :, driven_cols]
            drv.append(d)
            k = max(sg.shape[0], 1)
            ec.append(np.concatenate([ct.sum(axis=(0, 1)),
                                      sg.sum(axis=(0, 1))]) / k)
        return drv, np.stack(ec)

    def simulate(matrix, table, gain, drive_list, label):
        """Batched settle-stream-tail; features = per-trial window-mean
        evoked integrals of scored cells. (fc2 dynamics verbatim; the
        batching is the dsec/motion-arm shape adaptation.)"""
        t0 = time.time()
        flat = [d for trial_d in drive_list for d in trial_d]
        m = len(flat)
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
        sub_steps = int(round(DT_SUB_MS / fc2.DT_MS))
        tail_steps = int(round(TAIL_MS / fc2.DT_MS))
        stacked = np.stack(flat)                       # (m, n_sub, n_nodes)
        step = 0
        with np.errstate(over="ignore", invalid="ignore"):
            for k in range(n_sub):
                drive = stacked[:, k, :].T
                for _ in range(sub_steps):
                    net.step(drive)
                    step += 1
                    if step % 50 == 0:
                        finite = np.isfinite(net.v).all(axis=0)
                        bad |= ~finite | (np.where(
                            finite, np.abs(np.where(np.isfinite(net.v),
                                                    net.v, 0.0)).max(axis=0),
                            np.inf) > fc2.V_ABORT)
                    total += np.maximum(
                        np.maximum(net.v, 0.0)[score_idx, :] - base_out[:, None],
                        0.0) * (fc2.DT_MS / 1000.0)
            zero = np.zeros_like(net.v)
            for _ in range(tail_steps):
                net.step(zero)
                total += np.maximum(
                    np.maximum(net.v, 0.0)[score_idx, :] - base_out[:, None],
                    0.0) * (fc2.DT_MS / 1000.0)
        # collapse windows back to trials (mean over each trial's windows)
        feats, wbad, j = [], [], 0
        for trial_d in drive_list:
            k = len(trial_d)
            feats.append(total[:, j:j + k].mean(axis=1) if k else
                         np.zeros(score_idx.size))
            wbad.append(bool(bad[j:j + k].any()))
            j += k
        log(f"  [{label}] {m} windows / {len(drive_list)} trials in "
            f"{time.time() - t0:.1f}s, unstable windows {int(bad.sum())}")
        return np.stack(feats), np.array(wbad), float(bad.mean()) if m else 0.0

    def fit_probe(train_X, train_y, test_X, test_y, seed):
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold
        mu, sd = train_X.mean(0), train_X.std(0)
        sd = np.where(sd < 1e-12, 1.0, sd)
        Xtr, Xte = (train_X - mu) / sd, (test_X - mu) / sd
        best_c, best_cv = C_GRID[0], -1.0
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=seed)
        for c in C_GRID:
            accs = []
            for tr_i, va_i in skf.split(Xtr, train_y):
                clf = LogisticRegression(C=c, penalty="l2", solver="lbfgs",
                                         max_iter=5000).fit(Xtr[tr_i],
                                                            train_y[tr_i])
                accs.append((clf.predict(Xtr[va_i]) == train_y[va_i]).mean())
            cv = float(np.mean(accs))
            if cv > best_cv + 1e-12:
                best_cv, best_c = cv, c
        clf = LogisticRegression(C=best_c, penalty="l2", solver="lbfgs",
                                 max_iter=5000).fit(Xtr, train_y)
        pred = clf.predict(Xte)
        return pred, float((pred == test_y).mean()), best_c

    # Assemble parameter sets.
    real_matrix, _cov = fc25.trained_weight_matrix(
        fc2, patch, {p_: v["subset_mean"] for p_, v in params["pairs"].items()})
    table_real = fc25.trained_table(fc2, params, "subset", None)
    table_twin = fc25.trained_table(fc2, params, "subset", fc25.UNIFORM_TAU)
    from flygi.connectome.nulls import degree_preserving_rewire

    # Union of all seeds' train subsets + full test -> compute REAL/TWIN once.
    by_class: dict[int, list[int]] = {}
    for i, tr in enumerate(train_all):
        by_class.setdefault(tr["class"], []).append(i)
    seed_train_ids = {}
    union = set()
    for seed in SEEDS:
        rng = np.random.default_rng(1000 + seed)
        ids = []
        for cls, members in sorted(by_class.items()):
            take = min(TRAIN_PER_CLASS, len(members))
            ids.extend(rng.choice(members, size=take, replace=False).tolist())
        seed_train_ids[seed] = ids
        union.update(ids)
    union = sorted(union)
    union_pos = {i: k for k, i in enumerate(union)}
    log(f"train union {len(union)} trials; test {len(test_all)}")

    drv_union, ec_union = drives_and_ec([train_all[i] for i in union])
    drv_test, ec_test = drives_and_ec(test_all)
    test_y = np.array([t["class"] for t in test_all])
    test_subj = np.array([t["file"].split("_")[0] for t in test_all])

    feats, unstable = {}, {}
    for label, matrix, table, gain in (
            ("real", real_matrix, table_real, gain_real),
            ("twin", real_matrix, table_twin, gain_twin)):
        ftr, btr, u1 = simulate(matrix, table, gain, drv_union, label + "/train")
        fte, bte, u2 = simulate(matrix, table, gain, drv_test, label + "/test")
        feats[label] = (ftr, fte)
        unstable[label] = max(u1, u2)

    per_seed, cells = [], {"real": [], "null": [], "event_count": [], "twin": []}
    subjects = sorted(set(test_subj))
    for seed in SEEDS:
        ids = seed_train_ids[seed]
        rows = [union_pos[i] for i in ids]
        y = np.array([train_all[i]["class"] for i in ids])
        rewired, _ = degree_preserving_rewire(real_matrix,
                                              seed=REWIRE_SEED_BASE + seed)
        ntr, _, u3 = simulate(rewired, table_real, gain_real,
                              [drv_union[r] for r in rows], f"null{seed}/train")
        nte, _, u4 = simulate(rewired, table_real, gain_real, drv_test,
                              f"null{seed}/test")
        unstable[f"null{seed}"] = max(u3, u4)
        record: dict[str, Any] = {"seed": seed}
        for arm, (Xtr, Xte) in (
                ("real", (feats["real"][0][rows], feats["real"][1])),
                ("twin", (feats["twin"][0][rows], feats["twin"][1])),
                ("null", (ntr, nte)),
                ("event_count", (ec_union[rows], ec_test))):
            pred, acc, c = fit_probe(Xtr, y, Xte, test_y, seed)
            record[f"{arm}_acc"] = acc
            record[f"{arm}_C"] = c
            if arm == "real":
                record["real_chance_p"] = exact_binomial_above_chance(
                    int((pred == test_y).sum()), len(test_y))
            for subj in subjects:
                mask = test_subj == subj
                cells[arm].append(float((pred[mask] == test_y[mask]).mean()))
        per_seed.append(record)
        log(f"[seed {seed}] " + " ".join(
            f"{a}={record[a + '_acc']:.4f}" for a in
            ("real", "twin", "null", "event_count"))
            + f" chance_p={record['real_chance_p']:.2e}")

    worst_unstable = max(unstable.values())
    cells_np = {k: np.array(v) for k, v in cells.items()}
    out = assemble_verdict(per_seed, cells_np, dk.paired_sign_test_less)
    if worst_unstable > MAX_UNSTABLE_FRACTION:
        out["verdict"] = "BLOCKED"
        out["blocked_reason"] = f"unstable fraction {worst_unstable:.2f}"
    report = {
        "hypothesis": "H-T4T5-DVS-GESTURE",
        "registration": "docs/arenas/task4_neurobench/killtest_design.md "
                        "(frozen 2026-10-03, before data)",
        "trials": {"train_parsed": len(train_all), "test": len(test_all),
                   "train_union": len(union),
                   "per_seed_train": {str(s): len(seed_train_ids[s])
                                      for s in SEEDS}},
        "subjects_test": subjects,
        "drive_norm": norm, "unstable": unstable,
        "per_seed": per_seed,
        "cells_mean": {k: float(v.mean()) for k, v in cells_np.items()},
        **out,
        "elapsed_s": round(time.time() - started, 1),
    }
    args.output.write_text(json.dumps(report, indent=2))
    log(json.dumps({k: report[k] for k in
                    ("cells_mean", "bars", "sign_tests", "verdict")}, indent=2))
    log(f"VERDICT: {report['verdict']}")
    handle.close()
    return 0 if report["verdict"] == "PASS" else (
        3 if report["verdict"] == "BLOCKED" else 1)


if __name__ == "__main__":
    raise SystemExit(main())
