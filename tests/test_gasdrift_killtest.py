"""Tests for the PURE plumbing of scripts/arenas/gasdrift_killtest.py
(H-ALMB-GASDRIFT). The measurement is data-gated and local; what is
testable here: the libsvm parser (both label dialects), the frozen
rank-CDF convention, the seeded encoder map, the split selector on
synthetic label sets, the frozen three-bar verdict assembly, and — the
load-bearing one — the EXACT equivalence of the continuous-drive
run_sample to fc2_kc_sparse.run_trial at binary drive levels, on a toy
spiking network, before any data contact."""

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location(
    "gasdrift_killtest", ROOT / "scripts/arenas/gasdrift_killtest.py")
gd = importlib.util.module_from_spec(_spec)
sys.modules["gasdrift_killtest"] = gd
_spec.loader.exec_module(gd)

_spec2 = importlib.util.spec_from_file_location(
    "fc2_kc_sparse", ROOT / "scripts/benchmarks/fc2_kc_sparse.py")
fc2k = importlib.util.module_from_spec(_spec2)
sys.modules["fc2_kc_sparse"] = fc2k
_spec2.loader.exec_module(fc2k)


def test_parse_libsvm_line_both_label_dialects():
    feats = " ".join(f"{i}:{i / 10.0}" for i in range(1, 129))
    lab, x = gd.parse_libsvm_line(f"6 {feats}")
    assert lab == 6 and x.shape == (128,) and x[0] == 0.1 and x[127] == 12.8
    lab2, _ = gd.parse_libsvm_line(f"3;50.0 {feats}")
    assert lab2 == 3
    with pytest.raises(ValueError):
        gd.parse_libsvm_line("1 " + " ".join(
            f"{i}:0.0" for i in range(1, 128)))      # one feature missing
    with pytest.raises(ValueError):
        gd.parse_libsvm_line(f"1 129:0.5 {feats}")   # out-of-range index


def test_rank_cdf_fit_apply_and_saturation():
    train = np.array([[0.0], [1.0], [2.0], [3.0]])
    cols = gd.rank_cdf_fit(train)
    vals = gd.rank_cdf_apply(cols, np.array([[-5.0], [0.0], [1.5], [3.0],
                                             [99.0]]))
    assert vals[0, 0] == 0.0          # below train range -> saturates at 0
    assert vals[1, 0] == 0.25         # fraction <= 0.0
    assert vals[2, 0] == 0.5
    assert vals[3, 0] == 1.0
    assert vals[4, 0] == 1.0          # drift beyond range -> saturates at 1


def test_encoder_map_seeded_distinct_and_scram_differs():
    m = gd.encoder_map(gd.ENCODER_SEED, 162)
    assert m.shape == (128,) and len(set(m.tolist())) == 128
    assert np.array_equal(m, gd.encoder_map(gd.ENCODER_SEED, 162))
    assert not np.array_equal(m, gd.encoder_map(gd.ENCODER_SEED_SCRAM, 162))
    levels = gd.glomerulus_levels(np.linspace(0, 1, 128), m, 162)
    assert levels.shape == (162,)
    assert np.count_nonzero(levels) == 127   # the 0.0 feature lands as 0


def test_select_split_floors_and_caps():
    rng = np.random.default_rng(0)
    labels = {1: np.repeat([1, 2, 3, 4, 5, 6], [40, 40, 40, 40, 9, 0])}
    for b in range(2, 11):
        labels[b] = rng.integers(1, 7, size=100)
    split = gd.select_split(labels)
    assert split["classes"] == [1, 2, 3, 4]        # 5 below floor, 6 absent
    assert len(split["train_idx"]) == 4 * gd.TRAIN_PER_CLASS
    for b, idx in split["test_idx"].items():
        per = {c: sum(labels[b][i] == c for i in idx)
               for c in split["classes"]}
        assert all(v <= gd.TEST_PER_CLASS_PER_BATCH for v in per.values())
        assert all(labels[b][i] in split["classes"] for i in idx)


def _summary(real_mean, nulls, raw, correct=100, n=200, chance=0.25):
    return {
        "chance": chance,
        "real": {"mean_acc": real_mean, "pooled_correct": correct,
                 "pooled_n": n},
        "null": [{"mean_acc": m} for m in nulls],
        "raw": {"mean_acc": raw},
    }


def test_verdict_pass_and_kill_paths():
    out = gd.assemble_verdict(_summary(0.6, [0.4, 0.45, 0.5], 0.55))
    assert out["verdict"] == "PASS", out
    # kill: not above chance
    out = gd.assemble_verdict(_summary(0.6, [0.4] * 3, 0.5,
                                       correct=55, n=200))
    assert not out["bars"]["real_above_chance"]
    assert out["verdict"] == "KILL"
    # kill: one rewire seed at or above real (ties lose)
    out = gd.assemble_verdict(_summary(0.6, [0.4, 0.6, 0.4], 0.5))
    assert not out["bars"]["real_beats_null_all_seeds"]
    # kill: raw wins
    out = gd.assemble_verdict(_summary(0.6, [0.4] * 3, 0.65))
    assert not out["bars"]["real_beats_raw"]
    # missing null seed blocks the bar rather than passing silently
    out = gd.assemble_verdict(_summary(0.6, [0.4, 0.4], 0.5))
    assert not out["bars"]["real_beats_null_all_seeds"]


def test_frozen_constants_match_registration():
    assert gd.TRAIN_PER_CLASS == 15
    assert gd.TEST_PER_CLASS_PER_BATCH == 6
    assert gd.MIN_TRAIN_PER_CLASS == 10
    assert gd.MIN_TRAINABLE_CLASSES == 4 and gd.MIN_TEST_TOTAL == 150
    assert gd.SPLIT_SEED == 20261006 and gd.ENCODER_SEED == 20261006
    assert gd.ENCODER_SEED_SCRAM == 20261007
    assert gd.DRIVE_SEED_BASE == 20261008 and gd.CAL_SEED == 20261009
    assert gd.CAL_N == 8
    assert gd.CONFIG == {"tau_m_kc": 20.0, "tau_syn_kc": 5.0, "beta": 1.0}
    assert gd.SEEDS == (0, 1, 2) and gd.REWIRE_SEED_BASE == 4242
    assert gd.MAX_EXCEPTION_FRACTION == 0.05


def test_check_prerequisites_reports_cloud_blockers():
    missing = gd.check_prerequisites(None)
    assert any("--data-root" in m for m in missing)


# ---------------------------------------------------------------------------
# The load-bearing equivalence: run_sample at binary levels must
# reproduce fc2_kc_sparse.run_trial exactly (same Poisson stream, same
# spike counts) on a toy network.
# ---------------------------------------------------------------------------

def _toy_subcircuit():
    from dataclasses import dataclass
    from scipy import sparse

    types = np.array(["adPN-x", "adPN-y", "lPN-z",
                      "KCa", "KCb", "KCc", "KCd",
                      "APL", "MBON1"])
    n = types.size
    W = np.zeros((n, n))
    rng = np.random.default_rng(7)
    for kc in (3, 4, 5, 6):                 # PN -> KC claws
        for pn in (0, 1, 2):
            W[kc, pn] = rng.integers(1, 5)
    for kc in (3, 4, 5, 6):                 # KC -> APL, APL -> KC (inh)
        W[7, kc] = 2.0
        W[kc, 7] = -3.0
        W[8, kc] = 1.0                      # KC -> MBON

    @dataclass(frozen=True)
    class Toy:
        matrix: object
        types: object

    return Toy(matrix=sparse.csr_matrix(W), types=types)


def test_run_sample_equals_run_trial_at_binary_levels():
    sub = _toy_subcircuit()
    types = sub.types
    pn_idx = np.array([0, 1, 2])
    kc_idx = np.array([3, 4, 5, 6])
    apl_idx = np.array([7])
    mbon_idx = np.array([8])
    member_mask = np.array([True, False, True])     # odor members
    table = fc2k.build_table(theta_kc=2.0, alpha=0.5,
                             tau_m_kc=20.0, tau_syn_kc=5.0)
    seed = (123, 4)

    ref = fc2k.run_trial(sub, pn_idx, kc_idx, apl_idx, mbon_idx,
                         member_mask, table, 1.0, seed)
    got = gd.run_sample(fc2k, sub, pn_idx, kc_idx, apl_idx, mbon_idx,
                        table, 1.0, member_mask.astype(np.float64), seed)
    assert np.array_equal(ref["kc_odor_spikes"], got["kc_odor_spikes"])
    assert ref["frac2"] == got["frac2"]
    assert abs(ref["apl_mean_output"] - got["apl_mean_output"]) < 1e-12

    # and the probability construction is the exact affine reduction
    p = gd.pn_probability(fc2k, member_mask.astype(np.float64))
    p_bg = fc2k.RATE_BG_HZ * fc2k.DT_MS / 1000.0
    p_active = fc2k.RATE_ACTIVE_HZ * fc2k.DT_MS / 1000.0
    assert np.allclose(p, np.where(member_mask, p_active, p_bg))


def test_free_peaks_sample_runs_and_is_deterministic():
    sub = _toy_subcircuit()
    pn_idx = np.array([0, 1, 2])
    kc_idx = np.array([3, 4, 5, 6])
    levels = np.array([1.0, 0.3, 0.0])
    a = gd.free_peaks_sample(fc2k, sub, pn_idx, kc_idx, levels,
                             20.0, 5.0, 1.0, (9, 9))
    b = gd.free_peaks_sample(fc2k, sub, pn_idx, kc_idx, levels,
                             20.0, 5.0, 1.0, (9, 9))
    assert a.shape == (4,) and np.array_equal(a, b)
    assert np.isfinite(a).all()
