#!/usr/bin/env python3
"""H-ALMB-GASDRIFT -- the Task 6 (e-nose / gas drift) kill test.

PREREGISTRATION (EXPERIMENTS.yaml H-ALMB-GASDRIFT and
docs/arenas/task6_enose/killtest_design.md, both 2026-10-06, frozen
BEFORE this file existed; restated, not changed):

  - UCI Gas Sensor Array Drift (batch1.dat..batch10.dat, libsvm-style,
    128 features, labels 1-6). TRAIN = batch 1 (15/class, seeded);
    TEST = batches 2-10 (6/class/batch, seeded). Trainable classes =
    labels with >= 10 TRAIN samples in batch 1; chance = 1/n_trainable.
    BLOCKED below 4 trainable classes or 150 total test samples.
  - Encoder, frozen (AE-1/AE-4): per-feature rank-CDF normalization
    fit on TRAIN only, clipped [0,1]; ENCODER_SEED permutation assigns
    each feature to a distinct glomerular type (34 of 162 stay at
    background); PN rate = 5 + 95 * level Hz; Poisson paired across
    arms by per-sample drive seed.
  - Circuit: fc2_kc_sparse machinery verbatim (subcircuit, dynamics,
    dt 0.1 ms, settle 200 ms, odor 500 ms, w_scale), config tau_m 20 /
    tau_syn 5 / beta 1.0 (the recorded passing config -- asserted
    against results/benchmarks/fc2_kc_sparse.json verdict.pass_configs);
    theta and alpha recalibrated PER ARM by the fc2_kc_sparse recipe
    on a seeded CAL_N=8 TRAIN subset. Rewired arms calibrate fresh.
  - Features per sample: the 4,064-dim KC spike-count vector
    (run_trial's kc_odor_spikes), via the continuous-drive
    generalization run_sample (binary levels reduce EXACTLY to
    run_trial's member-mask form; equivalence unit-tested in-cloud on
    a toy network against run_trial itself).
  - Arms: REAL / NULL x3 (degree-preserving rewire, seeds 4242+0..2) /
    RAW (identical probe on the identical normalized 128 features) /
    SCRAM (context only: second encoder permutation on the real
    circuit; decides nothing).
  - Probe per arm: z-score(TRAIN), multinomial logistic L2 lbfgs, C
    from (0.01, 0.1, 1, 10) by 3-fold CV on TRAIN.
  - PASS iff (1) REAL pooled test accuracy above chance, exact
    binomial p < 0.05; (2) REAL mean-over-batches accuracy > NULL for
    ALL THREE seeds; (3) REAL > RAW. KILL otherwise. The established
    literature (Caron 2013; Litwin-Kumar 2017) itself predicts bar 2
    fails for this circuit -- stated in the registration.
  - BLOCKED (exit 3): data/floor failures, calibration hit_target
    false in any arm, > 5% simulation exceptions in any arm.

Data gate: runs where the compiled runtime, the fc2_kc_sparse passing
result and the dataset live (the cloud container has none of them).

Run:    python scripts/arenas/gasdrift_killtest.py --data-root <dir> [--workers N]
Output: results/arenas/gasdrift_killtest.json (+ .log)
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
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "scripts/benchmarks"
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- frozen constants (killtest_design.md; do not tune) ---------------------
N_FEATURES = 128
N_BATCHES = 10
TRAIN_PER_CLASS = 15
TEST_PER_CLASS_PER_BATCH = 6
MIN_TRAIN_PER_CLASS = 10
MIN_TRAINABLE_CLASSES = 4
MIN_TEST_TOTAL = 150
SPLIT_SEED = 20261006
ENCODER_SEED = 20261006
ENCODER_SEED_SCRAM = 20261007
DRIVE_SEED_BASE = 20261008
CAL_SEED = 20261009
CAL_N = 8
CONFIG = {"tau_m_kc": 20.0, "tau_syn_kc": 5.0, "beta": 1.0}
SEEDS = (0, 1, 2)
REWIRE_SEED_BASE = 4242
C_GRID = (0.01, 0.1, 1.0, 10.0)
ALPHA_SIG = 0.05
MAX_EXCEPTION_FRACTION = 0.05

FC2K_RESULTS = ROOT / "results/benchmarks/fc2_kc_sparse.json"
RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
ANNOTATIONS = ROOT / "data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT_JSON = ROOT / "results/arenas/gasdrift_killtest.json"


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ---------------------------------------------------------------------------
# Pure plumbing (unit-tested in-cloud)
# ---------------------------------------------------------------------------

def parse_libsvm_line(line: str) -> tuple[int, np.ndarray]:
    """One UCI drift line -> (gas label, 128-feature vector). The label
    token is "6" in some distributions and "6;concentration" in others;
    both parse. Feature ids must be 1..128, each at most once."""
    tokens = line.split()
    if not tokens:
        raise ValueError("empty line")
    label = int(float(tokens[0].split(";")[0]))
    x = np.full(N_FEATURES, np.nan)
    for tok in tokens[1:]:
        key, _, val = tok.partition(":")
        idx = int(key)
        if not 1 <= idx <= N_FEATURES:
            raise ValueError(f"feature index {idx} outside 1..{N_FEATURES}")
        if not math.isnan(x[idx - 1]):
            raise ValueError(f"feature index {idx} repeated")
        x[idx - 1] = float(val)
    if np.isnan(x).any():
        raise ValueError(f"{int(np.isnan(x).sum())} of {N_FEATURES} "
                         "features missing")
    return label, x


def load_batch(path: Path) -> tuple[np.ndarray, np.ndarray]:
    labels, rows = [], []
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line:
            continue
        label, x = parse_libsvm_line(line)
        labels.append(label)
        rows.append(x)
    return np.array(labels, dtype=np.int64), np.stack(rows)


def rank_cdf_fit(train_X: np.ndarray) -> np.ndarray:
    """Per-feature sorted TRAIN values (the frozen empirical CDF)."""
    return np.sort(train_X, axis=0)


def rank_cdf_apply(sorted_cols: np.ndarray, X: np.ndarray) -> np.ndarray:
    """value -> fraction of TRAIN values <= it, per feature, clipped to
    [0, 1]. Drift beyond the train range saturates at 0/1 by
    construction -- that is the phenomenon under test (AE-4)."""
    n = sorted_cols.shape[0]
    out = np.empty_like(X, dtype=np.float64)
    for j in range(X.shape[1]):
        out[:, j] = np.searchsorted(sorted_cols[:, j], X[:, j],
                                    side="right") / n
    return np.clip(out, 0.0, 1.0)


def encoder_map(seed: int, n_glomeruli: int) -> np.ndarray:
    """Feature i -> glomerular-type index map: one seeded permutation,
    each feature to a distinct glomerulus (AE-1: the assignment is an
    invention; declared, not tuned)."""
    rng = np.random.default_rng(seed)
    return rng.permutation(n_glomeruli)[:N_FEATURES]


def glomerulus_levels(x_norm: np.ndarray, feat_to_glom: np.ndarray,
                      n_glomeruli: int) -> np.ndarray:
    levels = np.zeros(n_glomeruli)
    levels[feat_to_glom] = x_norm
    return levels


def select_split(labels_by_batch: dict[int, np.ndarray]) -> dict[str, Any]:
    """Seeded caps on the dataset's own batch structure. Returns the
    trainable-class set, TRAIN indices into batch 1, and TEST indices
    per batch. Pure given the label arrays."""
    rng = np.random.default_rng(SPLIT_SEED)
    train_labels = labels_by_batch[1]
    classes = sorted(
        c for c in np.unique(train_labels)
        if int((train_labels == c).sum()) >= MIN_TRAIN_PER_CLASS)
    train_idx = []
    for c in classes:
        pool = np.flatnonzero(train_labels == c)
        take = min(TRAIN_PER_CLASS, pool.size)
        train_idx.extend(rng.choice(pool, size=take, replace=False).tolist())
    test_idx = {}
    for b in range(2, N_BATCHES + 1):
        lab = labels_by_batch.get(b)
        if lab is None:
            continue
        picks = []
        for c in classes:
            pool = np.flatnonzero(lab == c)
            take = min(TEST_PER_CLASS_PER_BATCH, pool.size)
            if take:
                picks.extend(rng.choice(pool, size=take,
                                        replace=False).tolist())
        if picks:
            test_idx[b] = sorted(picks)
    return {"classes": [int(c) for c in classes],
            "train_idx": sorted(train_idx),
            "test_idx": test_idx,
            "n_test_total": int(sum(len(v) for v in test_idx.values()))}


def exact_binomial_above_chance(correct: int, n: int, p0: float) -> float:
    if n == 0:
        return float("nan")
    return float(sum(math.comb(n, k) * p0 ** k * (1 - p0) ** (n - k)
                     for k in range(correct, n + 1)))


def assemble_verdict(summary: dict) -> dict:
    """The frozen three-bar rule. summary carries, per arm, the
    mean-over-batches accuracy; for REAL also pooled correct/n and the
    chance rate. SCRAM decides nothing."""
    real = summary["real"]
    chance_p = exact_binomial_above_chance(
        real["pooled_correct"], real["pooled_n"], summary["chance"])
    null_means = [a["mean_acc"] for a in summary["null"]]
    bars = {
        "real_above_chance": bool(chance_p < ALPHA_SIG),
        "real_beats_null_all_seeds": bool(
            len(null_means) == len(SEEDS)
            and all(real["mean_acc"] > m for m in null_means)),
        "real_beats_raw": bool(real["mean_acc"] > summary["raw"]["mean_acc"]),
    }
    return {"bars": bars, "real_chance_p": chance_p,
            "verdict": "PASS" if all(bars.values()) else "KILL"}


def check_prerequisites(data_root: Path | None) -> list[str]:
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not ANNOTATIONS.exists():
        missing.append(f"raw annotations feather: {ANNOTATIONS}")
    if not FC2K_RESULTS.exists():
        missing.append(f"fc2_kc_sparse passing result (local-only): "
                       f"{FC2K_RESULTS}")
    for mod in ("pyarrow", "scipy", "sklearn"):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    if data_root is None:
        missing.append("--data-root (directory with batch1.dat..batch10.dat)")
    else:
        for b in range(1, N_BATCHES + 1):
            if not (Path(data_root) / f"batch{b}.dat").exists():
                missing.append(f"batch{b}.dat not found under {data_root}")
    return missing


# ---------------------------------------------------------------------------
# Continuous-drive generalization of fc2_kc_sparse.run_trial /
# free_potential_peaks. The loops are that script's verbatim with ONE
# change: the binary member-mask probability
#     np.where(member_mask, p_active, p_bg)
# becomes the affine
#     p_bg + (p_active - p_bg) * clip(levels, 0, 1)
# which reduces EXACTLY to the original at levels in {0, 1}
# (equivalence asserted against run_trial itself by unit test on a toy
# network, before any data contact).
# ---------------------------------------------------------------------------

def pn_probability(fc2k, pn_levels: np.ndarray) -> np.ndarray:
    p_bg = fc2k.RATE_BG_HZ * fc2k.DT_MS / 1000.0
    p_active = fc2k.RATE_ACTIVE_HZ * fc2k.DT_MS / 1000.0
    return p_bg + (p_active - p_bg) * np.clip(pn_levels, 0.0, 1.0)


def run_sample(fc2k, sub, pn_idx, kc_idx, apl_idx, mbon_idx, table,
               w_scale, pn_levels, drive_seed, collect_probe=False):
    from flygi.dynamics.spiking import SpikingNetwork
    net = SpikingNetwork(sub.matrix, sub.types, table,
                         dt_ms=fc2k.DT_MS, w_scale=w_scale)
    rng = np.random.default_rng(drive_seed)
    p_bg = fc2k.RATE_BG_HZ * fc2k.DT_MS / 1000.0
    probability = np.full(pn_idx.size, p_bg, dtype=np.float64)
    odor_probability = pn_probability(fc2k, pn_levels)

    kc_odor = np.zeros(kc_idx.size, dtype=np.int64)
    apl_out_sum = 0.0
    i_exc_sum = 0.0
    apl_free_sum = np.zeros(apl_idx.size, dtype=np.float64)

    for step in range(fc2k.SETTLE_STEPS + fc2k.ODOR_STEPS):
        if step == fc2k.SETTLE_STEPS:
            probability = odor_probability
        out = net.step(None)
        if step >= fc2k.SETTLE_STEPS:
            kc_odor += out[kc_idx] > 0
            apl_out_sum += float(out[apl_idx].sum())
            if collect_probe:
                i_exc_sum += float(net.i_syn[kc_idx].mean())
                apl_free_sum += np.maximum(net.v[apl_idx], 0.0)
        net.last_output[pn_idx] = (
            rng.random(pn_idx.size) < probability).astype(np.float32)

    result = {
        "frac2": float((kc_odor >= fc2k.RESPONSIVE_MIN_SPIKES).mean()),
        "kc_odor_spikes": kc_odor,
        "apl_mean_output": apl_out_sum / (fc2k.ODOR_STEPS * apl_idx.size),
    }
    if collect_probe:
        result["i_exc_mean"] = i_exc_sum / fc2k.ODOR_STEPS
        result["apl_free_mean"] = apl_free_sum / fc2k.ODOR_STEPS
    return result


def free_peaks_sample(fc2k, sub, pn_idx, kc_idx, pn_levels,
                      tau_m_kc, tau_syn_kc, w_scale, drive_seed):
    from flygi.dynamics.spiking import SpikingNetwork
    from flygi.dynamics.spiking import ParameterTable, TypeParams
    table = ParameterTable(
        default=TypeParams(tau_m_ms=20.0, v_thresh=1e9, tau_syn_ms=5.0,
                           provenance="free run"),
        rules=[
            ("APL", TypeParams(tau_m_ms=fc2k.TAU_M_APL, v_thresh=1e9,
                               provenance="free run", graded=True,
                               graded_gain=0.0)),
            ("KC*", TypeParams(tau_m_ms=tau_m_kc, v_thresh=1e9,
                               tau_syn_ms=tau_syn_kc,
                               provenance="free run")),
        ],
    )
    net = SpikingNetwork(sub.matrix, sub.types, table,
                         dt_ms=fc2k.DT_MS, w_scale=w_scale)
    rng = np.random.default_rng(drive_seed)
    p_bg = fc2k.RATE_BG_HZ * fc2k.DT_MS / 1000.0
    probability = np.full(pn_idx.size, p_bg, dtype=np.float64)
    odor_probability = pn_probability(fc2k, pn_levels)
    peaks = np.zeros(kc_idx.size, dtype=np.float32)
    for step in range(fc2k.SETTLE_STEPS + fc2k.ODOR_STEPS):
        if step == fc2k.SETTLE_STEPS:
            probability = odor_probability
        net.step(None)
        if step >= fc2k.SETTLE_STEPS:
            np.maximum(peaks, net.v[kc_idx], out=peaks)
        net.last_output[pn_idx] = (
            rng.random(pn_idx.size) < probability).astype(np.float32)
    return peaks


# ---------------------------------------------------------------------------
# Worker-pool plumbing (decision-neutral parallelism: per-sample drive
# seeds are fixed and each trial is independent given the calibrated
# network, so results are identical at any worker count).
# ---------------------------------------------------------------------------

_W: dict[str, Any] = {}


def _worker_init(arm_spec: dict):
    import dataclasses
    fc2k = _load_module("fc2_kc_sparse_w", BENCH / "fc2_kc_sparse.py")
    sub = fc2k.build_subcircuit()
    if arm_spec["rewire_seed"] is not None:
        from flygi.connectome.nulls import degree_preserving_rewire
        rewired, _ = degree_preserving_rewire(
            sub.matrix, seed=arm_spec["rewire_seed"])
        sub = dataclasses.replace(sub, matrix=rewired)
    types = sub.types
    pn_mask = np.zeros(types.size, dtype=bool)
    for s in fc2k.PN_SUBSTRINGS:
        pn_mask |= np.char.find(types, s) >= 0
    _W.update(
        fc2k=fc2k, sub=sub,
        pn_idx=np.flatnonzero(pn_mask),
        kc_idx=np.flatnonzero(np.char.startswith(types, "KC")),
        apl_idx=np.flatnonzero(types == "APL"),
        mbon_idx=np.flatnonzero(np.char.startswith(types, "MBON")),
        table=_W_build_table(fc2k, arm_spec),
        w_scale=arm_spec["w_scale"],
        pn_types=types,
    )


def _W_build_table(fc2k, arm_spec):
    return fc2k.build_table(arm_spec["theta"], arm_spec["alpha"],
                            CONFIG["tau_m_kc"], CONFIG["tau_syn_kc"])


def _pn_levels_for(glom_levels: np.ndarray) -> np.ndarray:
    """Expand per-glomerular-type levels to per-PN levels."""
    fc2k, pn_idx = _W["fc2k"], _W["pn_idx"]
    names = _W.setdefault(
        "pn_type_names", sorted(set(_W["pn_types"][pn_idx].tolist())))
    name_to_i = _W.setdefault("name_to_i",
                              {n: i for i, n in enumerate(names)})
    per_pn = np.array([glom_levels[name_to_i[t]]
                       for t in _W["pn_types"][pn_idx]])
    return per_pn


def _worker_run(task):
    gid, glom_levels = task
    try:
        res = run_sample(_W["fc2k"], _W["sub"], _W["pn_idx"], _W["kc_idx"],
                         _W["apl_idx"], _W["mbon_idx"], _W["table"],
                         _W["w_scale"], _pn_levels_for(np.asarray(glom_levels)),
                         (DRIVE_SEED_BASE, gid))
        return gid, res["kc_odor_spikes"], None
    except Exception:
        return gid, None, traceback.format_exc()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-ALMB-GASDRIFT kill test (data-gated)")
    parser.add_argument("--data-root", type=Path, default=None)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites(args.data_root)
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("Run where the compiled runtime, the fc2_kc_sparse result "
              "and the dataset live (docs/arenas/task6_enose/runbook.md).")
        return 3

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    fc2k = _load_module("fc2_kc_sparse", BENCH / "fc2_kc_sparse.py")
    fc2k_results = json.loads(FC2K_RESULTS.read_text())
    assert CONFIG in fc2k_results["verdict"]["pass_configs"], \
        "frozen config is not among fc2_kc_sparse pass_configs"

    # Data + split + encoder (frozen).
    labels_by_batch, X_by_batch = {}, {}
    for b in range(1, N_BATCHES + 1):
        labels_by_batch[b], X_by_batch[b] = load_batch(
            args.data_root / f"batch{b}.dat")
        log(f"batch{b}: {labels_by_batch[b].size} samples, classes "
            f"{np.unique(labels_by_batch[b]).tolist()}")
    split = select_split(labels_by_batch)
    classes = split["classes"]
    log(f"trainable classes {classes}; train {len(split['train_idx'])}; "
        f"test total {split['n_test_total']}")
    if len(classes) < MIN_TRAINABLE_CLASSES or \
            split["n_test_total"] < MIN_TEST_TOTAL:
        log(f"BLOCKED: floors not met ({len(classes)} classes, "
            f"{split['n_test_total']} test samples)")
        return 3
    chance = 1.0 / len(classes)

    sorted_cols = rank_cdf_fit(X_by_batch[1][split["train_idx"]])
    norm = {b: rank_cdf_apply(sorted_cols, X_by_batch[b])
            for b in range(1, N_BATCHES + 1)}

    # Global sample list: (gid, batch, row) -- gid fixes the drive seed.
    samples = [(0, 1, i) for i in split["train_idx"]]
    for b in sorted(split["test_idx"]):
        samples += [(0, b, i) for i in split["test_idx"][b]]
    samples = [(gid, b, i) for gid, (_, b, i) in enumerate(samples)]
    train_rows = [s for s in samples if s[1] == 1]
    test_rows = [s for s in samples if s[1] != 1]
    y_of = lambda b, i: int(labels_by_batch[b][i])

    # Subcircuit facts (built once here for calibration; workers rebuild).
    sub = fc2k.build_subcircuit()
    types = sub.types
    pn_mask = np.zeros(types.size, dtype=bool)
    for s in fc2k.PN_SUBSTRINGS:
        pn_mask |= np.char.find(types, s) >= 0
    pn_idx = np.flatnonzero(pn_mask)
    kc_idx = np.flatnonzero(np.char.startswith(types, "KC"))
    apl_idx = np.flatnonzero(types == "APL")
    mbon_idx = np.flatnonzero(np.char.startswith(types, "MBON"))
    pn_type_names = sorted(set(types[pn_idx].tolist()))
    n_glom = len(pn_type_names)
    name_to_i = {n: i for i, n in enumerate(pn_type_names)}
    pn_type_of = np.array([name_to_i[t] for t in types[pn_idx]])
    pn_kc = sub.matrix[kc_idx][:, pn_idx]
    w_scale = 1.0 / float(pn_kc.data[pn_kc.data > 0].mean())
    log(f"subcircuit: {sub.node_count} nodes ({pn_idx.size} PN / "
        f"{kc_idx.size} KC / {apl_idx.size} APL / {mbon_idx.size} MBON); "
        f"{n_glom} glomerular types; w_scale {w_scale:.5f}")

    feat_maps = {"real": encoder_map(ENCODER_SEED, n_glom),
                 "scram": encoder_map(ENCODER_SEED_SCRAM, n_glom)}

    def levels_of(b, i, which):
        return glomerulus_levels(norm[b][i], feat_maps[which], n_glom)

    # Calibration subset: seeded CAL_N TRAIN samples (input statistics).
    cal_rng = np.random.default_rng(CAL_SEED)
    cal_rows = [train_rows[k] for k in
                cal_rng.choice(len(train_rows), size=CAL_N, replace=False)]

    import dataclasses
    from flygi.connectome.nulls import degree_preserving_rewire

    def calibrate(matrix, which, label):
        """The fc2_kc_sparse recipe verbatim on this input: theta0 from
        free peaks (2 cal samples) -> open-loop alpha probe -> theta
        bisection to TARGET_F on the CAL_N samples."""
        arm_sub = dataclasses.replace(sub, matrix=matrix)
        # The alpha-balance feedback must read the ARM's own APL->KC
        # weights: a rewired arm has different APL edges than the real
        # circuit (caught in review before any data contact).
        arm_apl_block = np.abs(np.asarray(
            matrix[kc_idx][:, apl_idx].todense(), dtype=np.float64))
        tau_m, tau_syn, beta = (CONFIG["tau_m_kc"], CONFIG["tau_syn_kc"],
                                CONFIG["beta"])

        def pn_levels(row):
            _, b, i = row
            return levels_of(b, i, which)[pn_type_of]

        peaks = np.concatenate([
            free_peaks_sample(fc2k, arm_sub, pn_idx, kc_idx,
                              pn_levels(cal_rows[k]), tau_m, tau_syn,
                              w_scale, (DRIVE_SEED_BASE, cal_rows[k][0]))
            for k in range(2)])
        theta0 = float(np.quantile(peaks, 1.0 - fc2k.TARGET_F))
        if theta0 <= 0:
            return {"failed": "free potentials never positive"}

        def one(theta, alpha, row, probe=False):
            return run_sample(fc2k, arm_sub, pn_idx, kc_idx, apl_idx,
                              mbon_idx,
                              fc2k.build_table(theta, alpha, tau_m, tau_syn),
                              w_scale, pn_levels(row),
                              (DRIVE_SEED_BASE, row[0]), collect_probe=probe)

        probe = one(theta0, 0.0, cal_rows[0], probe=True)
        i_exc = probe["i_exc_mean"]
        apl_free = np.asarray(probe["apl_free_mean"], dtype=np.float64)
        feedback_per_gain = float((arm_apl_block @ apl_free).mean()) * \
            w_scale * tau_syn / fc2k.DT_MS
        if i_exc <= 0 or feedback_per_gain <= 1e-12:
            return {"failed": "APL undriven or nonpositive excitation"}
        alpha = beta * (i_exc / feedback_per_gain)

        lo, hi = theta0 / 4.0, theta0 * 4.0
        theta, best, history = theta0, None, []
        for _ in range(fc2k.MAX_BISECT):
            fracs = [one(theta, alpha, r)["frac2"] for r in cal_rows]
            med = float(np.median(fracs))
            history.append({"theta": theta, "median": med})
            if best is None or abs(med - fc2k.TARGET_F) < \
                    abs(best[1] - fc2k.TARGET_F):
                best = (theta, med)
            if abs(med - fc2k.TARGET_F) <= fc2k.CAL_TOL:
                break
            lo, hi = (theta, hi) if med > fc2k.TARGET_F else (lo, theta)
            theta = float(np.sqrt(lo * hi))
        theta, cal_median = best
        hit = bool(abs(cal_median - fc2k.TARGET_F) <= fc2k.CAL_TOL)
        log(f"  [{label}] calibrated theta {theta:.3f} alpha {alpha:.4f} "
            f"cal_median {cal_median:.4f} hit_target={hit}")
        return {"theta": theta, "alpha": alpha, "cal_median": cal_median,
                "hit_target": hit, "history": history}

    def simulate_arm(matrix, cal, which, label, rewire_seed):
        """All samples through the calibrated arm; returns the feature
        matrix aligned with `samples` plus the exception fraction."""
        arm_spec = {"theta": cal["theta"], "alpha": cal["alpha"],
                    "w_scale": w_scale, "rewire_seed": rewire_seed}
        tasks = [(gid, levels_of(b, i, which)) for gid, b, i in samples]
        t0 = time.time()
        results: dict[int, np.ndarray] = {}
        errors = []
        if args.workers > 1:
            import multiprocessing as mp
            ctx = mp.get_context("spawn")
            with ctx.Pool(args.workers, initializer=_worker_init,
                          initargs=(arm_spec,)) as pool:
                for gid, feats, err in pool.imap_unordered(
                        _worker_run, tasks, chunksize=4):
                    (errors.append((gid, err)) if err is not None
                     else results.__setitem__(gid, feats))
        else:
            _worker_init(arm_spec)
            for task in tasks:
                gid, feats, err = _worker_run(task)
                (errors.append((gid, err)) if err is not None
                 else results.__setitem__(gid, feats))
        frac_err = len(errors) / len(tasks)
        for gid, err in errors[:3]:
            log(f"  [{label}] sample {gid} failed:\n{err}")
        log(f"  [{label}] {len(tasks)} samples in {time.time() - t0:.1f}s, "
            f"exceptions {len(errors)} ({frac_err:.3f})")
        X = np.stack([results.get(gid, np.zeros(kc_idx.size))
                      for gid, _, _ in samples]).astype(np.float64)
        return X, frac_err

    def fit_probe(Xtr, ytr, cv_seed):
        from sklearn.linear_model import LogisticRegression
        from sklearn.model_selection import StratifiedKFold, cross_val_score
        mu, sd = Xtr.mean(0), Xtr.std(0)
        sd = np.where(sd < 1e-12, 1.0, sd)
        Z = (Xtr - mu) / sd
        best_c, best_cv = C_GRID[0], -1.0
        skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=cv_seed)
        for c in C_GRID:
            clf = LogisticRegression(C=c, max_iter=2000)
            cv = float(np.mean(cross_val_score(clf, Z, ytr, cv=skf)))
            if cv > best_cv:
                best_c, best_cv = c, cv
        clf = LogisticRegression(C=best_c, max_iter=2000).fit(Z, ytr)
        return lambda X: clf.predict((X - mu) / sd), best_c

    def score_arm(X, label, cv_seed):
        tr = [k for k, (_, b, _) in enumerate(samples) if b == 1]
        ytr = np.array([y_of(b, i) for _, b, i in train_rows])
        predict, c = fit_probe(X[tr], ytr, cv_seed)
        per_batch, pooled_correct, pooled_n = {}, 0, 0
        for b in sorted(split["test_idx"]):
            ks = [k for k, (_, bb, _) in enumerate(samples) if bb == b]
            y = np.array([y_of(bb, i) for _, bb, i in
                          (samples[k] for k in ks)])
            pred = predict(X[ks])
            acc = float((pred == y).mean())
            per_batch[b] = acc
            pooled_correct += int((pred == y).sum())
            pooled_n += y.size
        mean_acc = float(np.mean(list(per_batch.values())))
        log(f"[{label}] mean-over-batches {mean_acc:.4f} "
            f"pooled {pooled_correct}/{pooled_n} C={c} "
            f"curve {['%.3f' % per_batch[b] for b in sorted(per_batch)]}")
        return {"mean_acc": mean_acc, "per_batch": per_batch,
                "pooled_correct": pooled_correct, "pooled_n": pooled_n,
                "probe_C": c}

    # --- arms ---------------------------------------------------------------
    summary: dict[str, Any] = {"chance": chance}
    calibrations: dict[str, Any] = {}
    exception_fracs: dict[str, float] = {}

    cal_real = calibrate(sub.matrix, "real", "real")
    calibrations["real"] = cal_real
    if cal_real.get("failed") or not cal_real["hit_target"]:
        log("BLOCKED: real-arm calibration failed or missed target")
        return 3
    X_real, exception_fracs["real"] = simulate_arm(
        sub.matrix, cal_real, "real", "real", None)
    summary["real"] = score_arm(X_real, "real", cv_seed=0)

    cal_scram = calibrate(sub.matrix, "scram", "scram")
    calibrations["scram"] = cal_scram
    if cal_scram.get("failed") or not cal_scram["hit_target"]:
        log("BLOCKED: scram-arm calibration failed or missed target")
        return 3
    X_scram, exception_fracs["scram"] = simulate_arm(
        sub.matrix, cal_scram, "scram", "scram", None)
    summary["scram"] = score_arm(X_scram, "scram", cv_seed=0)

    summary["null"] = []
    for seed in SEEDS:
        rw_seed = REWIRE_SEED_BASE + seed
        rewired, _ = degree_preserving_rewire(sub.matrix, seed=rw_seed)
        cal = calibrate(rewired, "real", f"null{seed}")
        calibrations[f"null{seed}"] = cal
        if cal.get("failed") or not cal["hit_target"]:
            log(f"BLOCKED: null{seed} calibration failed or missed target")
            return 3
        Xn, exception_fracs[f"null{seed}"] = simulate_arm(
            rewired, cal, "real", f"null{seed}", rw_seed)
        summary["null"].append(score_arm(Xn, f"null{seed}", cv_seed=seed))

    X_raw = np.stack([norm[b][i] for _, b, i in samples])
    summary["raw"] = score_arm(X_raw, "raw", cv_seed=0)

    worst = max(exception_fracs.values())
    if worst > MAX_EXCEPTION_FRACTION:
        log(f"BLOCKED: exception fraction {worst:.3f} exceeds "
            f"{MAX_EXCEPTION_FRACTION}")
        return 3

    out = assemble_verdict(summary)
    record = {
        "hypothesis": "H-ALMB-GASDRIFT",
        "classes": classes, "chance": chance,
        "n_train": len(train_rows), "n_test": len(test_rows),
        "split": {str(b): len(v) for b, v in split["test_idx"].items()},
        "calibrations": {k: {kk: vv for kk, vv in v.items()
                             if kk != "history"}
                         for k, v in calibrations.items()},
        "scores": summary,
        "exception_fracs": exception_fracs,
        "bars": out["bars"],
        "real_chance_p": out["real_chance_p"],
        "verdict": out["verdict"],
        "elapsed_s": round(time.time() - started, 1),
        "workers": args.workers,
    }
    args.output.write_text(json.dumps(record, indent=2, default=float))
    log(json.dumps(record, indent=2, default=float))
    log(f"VERDICT: {out['verdict']}")
    handle.close()
    return 0 if out["verdict"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
