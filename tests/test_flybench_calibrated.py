"""Tests for the calibrated flybench adapter + frozen verdict machinery.

H-FLYGI-FLYBENCH-CALIBRATED (docs/arenas/task3_flybench/
calibrated_design.md). Pure parts run everywhere; the adapter-level tests
need flybench installed (skipped otherwise). The MaleCNS measurement is
the user's local run; what these tests pin down is the instrument: the
LK alpha search, the wiring-reuse policy, the mechanical check split, and
the frozen bars.
"""

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


HAVE_FLYBENCH = importlib.util.find_spec("flybench") is not None
if HAVE_FLYBENCH:
    ad = _load("flygi_flybench_adapter", ROOT / "scripts/arenas/flygi_flybench_adapter.py")
vd = _load("flybench_calibrated_verdict", ROOT / "scripts/arenas/flybench_calibrated_verdict.py")


# ---------------------------------------------------------- pure: alpha search

@pytest.mark.skipif(not HAVE_FLYBENCH, reason="flybench not installed")
def test_lk_alpha_search_hits_target():
    rng = np.random.default_rng(0)
    v_max = rng.normal(-45.0, 3.0, size=(16, 500))
    mu, sigma = v_max.mean(axis=0), np.maximum(v_max.std(axis=0), 1e-6)
    alpha, achieved = ad.lk_alpha_search(v_max, mu, sigma, target=0.075)
    assert abs(achieved - 0.075) < 0.01
    assert 0.0 < alpha < 8.0


@pytest.mark.skipif(not HAVE_FLYBENCH, reason="flybench not installed")
def test_lk_alpha_search_unreachable_band_reports_edge():
    # all-silent cells: even alpha=0 yields fraction 0 < target
    v_max = np.full((8, 50), -52.0)
    mu, sigma = v_max.mean(axis=0), np.maximum(v_max.std(axis=0), 1e-6)
    alpha, achieved = ad.lk_alpha_search(v_max, mu, sigma, target=0.075)
    assert achieved < 0.075 and alpha == 0.0   # the caller marks this blocked


# ---------------------------------------------------- pure: wiring-reuse tests

@pytest.mark.skipif(not HAVE_FLYBENCH, reason="flybench not installed")
def test_wiring_predicates():
    from scipy import sparse
    rng = np.random.default_rng(1)
    base = sparse.random(60, 60, density=0.1, random_state=2, format="csr")
    base.data[:] = rng.integers(1, 9, base.nnz)
    # jitter: same pattern, different weights
    jit = base.copy(); jit.data = jit.data * 1.3
    assert ad._same_indices(jit, base)
    # silence: zero three rows entirely
    # silencing zeroes OUTGOING synapses = columns of the engine's
    # transposed (post, pre) matrix
    sil = base.tolil(); sil[:, [3, 7, 11]] = 0
    sil = sil.tocsr(); sil.eliminate_zeros()
    assert ad._silenced_subset(sil, base)
    assert not ad._silenced_subset(base, base)         # nothing zeroed
    # rewired: same shape, different pattern
    rew = sparse.random(60, 60, density=0.1, random_state=9, format="csr")
    assert not ad._same_indices(rew, base)
    assert not ad._silenced_subset(rew, base)


# ------------------------------------------------- adapter-level (toy, cheap)

@pytest.mark.skipif(not HAVE_FLYBENCH, reason="flybench not installed")
def test_calibrated_adapter_on_toy(tmp_path, monkeypatch):
    from flybench.connectome import Connectome
    from flybench.sim import LIFParams
    monkeypatch.setattr(ad, "CAL_CACHE_DIR", tmp_path)
    toy_dir = Path.home() / ".cache" / "flybench" / "toy"
    if not toy_dir.exists():
        pytest.skip("toy connectome not built")
    c = Connectome.load(toy_dir)
    a = ad.FlyGICalibratedAdapter(c, LIFParams(seed=0))
    cal = a.calibration
    assert cal["applied"] and cal["kc_count"] > 0 and cal["graded_units"] > 0
    assert abs(cal["achieved_sparseness"] - ad.CAL_TARGET_SPARSENESS) < 0.05
    assert not cal["blocked_sparseness"]
    # graded units emit no spikes; KCs have per-cell thresholds above rest
    graded = a.net.params["graded"]
    assert graded.sum() == cal["graded_units"]
    kc = c.select(ad.KC_SELECT)
    assert (a.net.params["v_thresh"][kc] > a.p.v_rest_mv).all()
    # determinism incl. cache round trip
    r1 = a.run(200.0, [])
    b = ad.FlyGICalibratedAdapter(c, LIFParams(seed=0))
    assert b.calibration["reused"] == "identical"
    r2 = b.run(200.0, [])
    assert np.array_equal(r1.spike_times_ms, r2.spike_times_ms)
    assert np.array_equal(r1.spike_neurons, r2.spike_neurons)
    # sidecar written, carries n_neurons for verdict scoping
    sidecars = list(tmp_path.glob("*.json"))
    assert sidecars and json.loads(sidecars[0].read_text())["n_neurons"] == c.n


@pytest.mark.skipif(not HAVE_FLYBENCH, reason="flybench not installed")
def test_silenced_variant_reuses_base_thresholds(tmp_path, monkeypatch):
    from flybench.bench import silence_neurons
    from flybench.connectome import Connectome
    from flybench.sim import LIFParams
    monkeypatch.setattr(ad, "CAL_CACHE_DIR", tmp_path)
    toy_dir = Path.home() / ".cache" / "flybench" / "toy"
    if not toy_dir.exists():
        pytest.skip("toy connectome not built")
    ad.FlyGICalibratedAdapter._bases = []
    c = Connectome.load(toy_dir)
    a = ad.FlyGICalibratedAdapter(c, LIFParams(seed=0))
    apl = c.select(ad.APL_SELECT)
    sil = ad.FlyGICalibratedAdapter(silence_neurons(c, apl), LIFParams(seed=0))
    # acute manipulation: thresholds must come from the intact base
    assert sil.calibration["reused"] == "silenced-subset"
    kc = c.select(ad.KC_SELECT)
    assert np.allclose(a.net.params["v_thresh"][kc], sil.net.params["v_thresh"][kc])


# ------------------------------------------------------ verdict: split + bars

def _report(checks, graded=0.75, specificity=0.3, n_neurons=1000):
    return {"graded": graded, "specificity": specificity,
            "n_neurons": n_neurons,
            "tasks": [{"task": "t", "checks": checks}]}


def _chk(desc, op, graded):
    return {"description": desc, "op": op, "graded": graded}


def test_split_classification():
    checks = [
        _chk("rate[water] > 5.0 Hz", ">", 0.2),                  # activation
        _chk("spikes per neuron[loom] >= 1.0", ">=", 0.9),       # activation
        _chk("network rate[baseline] < 0.5 Hz", "<", 1.0),       # suppression
        _chk("rate[a] / rate[b] > 1", ">", 0.5),                 # ratio -> suppression
    ]
    uni = _report(checks)
    cal = _report(checks)
    act, sup = vd.split_scores(uni, cal)
    assert len(act) == 2 and len(sup) == 2


def test_verdict_pass_and_kill():
    uni_checks = [_chk("rate[x] > 5.0 Hz", ">", 0.40),
                  _chk("rate[y] / rate[z] < 0.5", "<", 0.90)]
    cal_pass = [_chk("rate[x] > 5.0 Hz", ">", 0.60),
                _chk("rate[y] / rate[z] < 0.5", "<", 0.90)]
    out = vd.verdict(_report(uni_checks, graded=0.711, specificity=0.282),
                     _report(cal_pass, graded=0.72, specificity=0.30))
    assert out["verdict"] == "PASS", out
    # kill: activation regresses
    cal_kill = [_chk("rate[x] > 5.0 Hz", ">", 0.35),
                _chk("rate[y] / rate[z] < 0.5", "<", 0.95)]
    out2 = vd.verdict(_report(uni_checks, graded=0.711, specificity=0.282),
                      _report(cal_kill, graded=0.72, specificity=0.30))
    assert out2["verdict"] == "KILL" and not out2["bars"]["activation_improves"]
    # kill: overall graded given back
    out3 = vd.verdict(_report(uni_checks, graded=0.711, specificity=0.282),
                      _report(cal_pass, graded=0.65, specificity=0.30))
    assert out3["verdict"] == "KILL" and not out3["bars"]["overall_holds"]
    # kill: specificity given back
    out4 = vd.verdict(_report(uni_checks, graded=0.711, specificity=0.282),
                      _report(cal_pass, graded=0.72, specificity=0.20))
    assert out4["verdict"] == "KILL" and not out4["bars"]["specificity_holds"]


def test_verdict_blocked_on_empty_activation_set():
    checks = [_chk("rate[y] / rate[z] < 0.5", "<", 0.9)]
    out = vd.verdict(_report(checks), _report(checks))
    assert out["verdict"] == "BLOCKED"
    assert any("activation" in r for r in out["blocked_reasons"])


def test_moved_checks_stay_shared_despite_annotation_drift():
    # Regression for the 2026-10-03 instrument bug: flybench appends a
    # volatile "  [N/3 seeds, sd S]" annotation to each description, so a
    # check the manipulation MOVED got a new annotation and dropped out of
    # the shared set -- bar 1 was then computed only over unmoved checks.
    uni = _report([_chk("rate[x] > 5.0 Hz  [0/3 seeds, sd 0]", ">", 0.40)])
    cal = _report([_chk("rate[x] > 5.0 Hz  [3/3 seeds, sd 0.21]", ">", 0.90)])
    act, sup = vd.split_scores(uni, cal)
    assert len(act) == 1 and act[0][1:] == (0.40, 0.90)


def test_frozen_bar_constants_match_registration():
    assert vd.BAR_ACTIVATION_DELTA == 0.02
    assert vd.BAR_OVERALL_GRADED == 0.701
    assert vd.BAR_SPECIFICITY == 0.252
