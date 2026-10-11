"""Tests for scripts/arenas/cx_class3_killtest.py
(H-CX-CLASS3-COMPASS, Task 9 reopening). The MaleCNS measurement is
data-gated and local; what is testable in-cloud is the instrument:
the frozen physiology constants, the AP/PSC templates, the engine
mechanics, the published width estimator (measureBump1) and column
geometry, the AC-6 class-scale mapping, the verdict bars, the
fixture's provenance integrity, and -- the load-bearing one, required
by the frozen registration -- the VALIDATION GATE: the engine must
reproduce the published Pisokas 60-neuron fly bump before anything
about MaleCNS is claimed."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location(
    "cx_class3_killtest", ROOT / "scripts/arenas/cx_class3_killtest.py")
c3 = importlib.util.module_from_spec(_spec)
sys.modules["cx_class3_killtest"] = c3
_spec.loader.exec_module(c3)


# --- frozen constants (registration killtest_design_reopening.md) ----------

def test_frozen_physiology_constants():
    assert c3.DT_S == 1e-4
    assert c3.CM_F == 2e-8          # CODE value (paper text: 2 nF)
    assert c3.RM_OHM == 1e6         # CODE value (paper text: 10 MOhm)
    assert c3.V_REST == -52e-3
    assert c3.V_THRESH == -45e-3
    assert c3.AP_END == -72e-3
    assert c3.PSC_PEAK_A == 5e-9
    assert c3.PSC_RISE_MS == 2.0
    assert c3.PSC_HALF_MS == 5.0
    assert c3.PSC_HALFLIVES == 7
    assert c3.BG_HZ == 5.0
    assert c3.DRIVE_PEAK_HZ == 190.0
    assert c3.VM_KAPPA == pytest.approx(3 * np.pi / 4)


def test_frozen_protocol_constants():
    assert c3.WRITE_S == 1.0 and c3.DARK_S == 2.0 and c3.READ_S == 0.25
    assert c3.G1_ANGLES == tuple(22.5 + 45.0 * k for k in range(8))
    assert c3.G1_MIN_PASS == 6
    assert c3.RETENTION_MIN == 0.05
    assert c3.CIRCVAR_MAX == 0.6
    assert c3.ERR_MAX_DEG == 45.0
    assert c3.STEER_RATE_MIN_DEG_S == 9.0
    assert c3.GRID == tuple((g, i) for g in (0.5, 1.0, 2.0)
                            for i in (1.0, 2.0))
    assert c3.REWIRE_SEED_BASE == 4242 and c3.REWIRE_SEEDS == (0, 1, 2)
    assert c3.VALIDATION_SEEDS == (7, 8, 9, 10, 11)


def test_pisokas_class_weights_pinned():
    w = c3.PISOKAS_WEIGHTS
    assert w[("E-PG", "P-EN")] == w[("E-PG", "P-EG")] == \
        pytest.approx(99.9680554605268)
    assert w[("E-PG", "Delta7")] == pytest.approx(47.9173822984772)
    assert w[("P-EN", "E-PG")] == w[("P-EG", "E-PG")] == \
        pytest.approx(6.07203896674184)
    assert w[("Delta7", "P-EN")] == w[("Delta7", "P-EG")] == \
        pytest.approx(-35.6772759590409)
    assert w[("Delta7", "Delta7")] == pytest.approx(-19.3358579258735)
    assert c3.FALLBACK_MAGNITUDE == pytest.approx(6.07203896674184)


# --- templates --------------------------------------------------------------

def test_ap_template_endpoints_and_duration():
    ap = c3.ap_template()
    assert ap.size == 22                      # 2.2 ms at dt 1e-4
    assert ap[0] == pytest.approx(c3.V_THRESH)
    assert ap[-1] == pytest.approx(c3.AP_END)
    assert ap.max() == pytest.approx(c3.AP_PEAK)


def test_psc_template_peak_and_halflife():
    psc = c3.psc_template()
    rise_n = int(round(c3.PSC_RISE_MS * 1e-3 / c3.DT_S))
    fall_n = int(round(c3.PSC_HALFLIVES * c3.PSC_HALF_MS * 1e-3 / c3.DT_S))
    assert psc.size == rise_n + fall_n
    assert psc.max() == pytest.approx(c3.PSC_PEAK_A)
    assert (psc >= 0).all()
    half_n = int(round(c3.PSC_HALF_MS * 1e-3 / c3.DT_S))
    assert psc[rise_n + half_n] == pytest.approx(psc[rise_n] / 2.0)


# --- engine mechanics -------------------------------------------------------

def test_engine_silent_without_input():
    eng = c3.TemplateLIF(np.zeros((3, 3)), seed=0)
    for _ in range(200):
        spikes = eng.step(np.zeros(3))
        assert not spikes.any()
    assert np.allclose(eng.v, c3.V_REST)
    assert not eng.unstable


def test_engine_spikes_under_strong_drive_and_resets():
    eng = c3.TemplateLIF(np.zeros((1, 1)), seed=1)
    spiked = False
    for _ in range(5000):
        if eng.step(np.array([2000.0]))[0]:
            spiked = True
            break
    assert spiked
    # AP playback runs the template then lands at the undershoot
    for _ in range(eng.ap.size):
        eng.step(np.array([0.0]))
    assert eng.v[0] == pytest.approx(c3.AP_END)
    assert eng.phase[0] == -1


def test_engine_synaptic_propagation_and_sign():
    # excitatory: pre 0 -> post 1 at strong weight fires post
    W = np.zeros((2, 2))
    W[1, 0] = 200.0                 # [post, pre]
    eng = c3.TemplateLIF(W, seed=2)
    drive = np.array([2000.0, 0.0])
    post_spiked = False
    for _ in range(20000):
        s = eng.step(drive)
        if s[1]:
            post_spiked = True
            break
    assert post_spiked
    # inhibitory: same drive, negative weight keeps post below rest
    Wn = np.zeros((2, 2))
    Wn[1, 0] = -200.0
    eng2 = c3.TemplateLIF(Wn, seed=2)
    vmin = 0.0
    for _ in range(5000):
        eng2.step(drive)
        vmin = min(vmin, eng2.v[1] - c3.V_REST)
    assert vmin < -1e-3             # driven below rest, never fires
    assert eng2.v[1] < c3.V_THRESH


def test_engine_deterministic_per_seed():
    W = np.zeros((4, 4))
    W[1, 0] = W[2, 1] = 50.0
    drive = np.full(4, 300.0)
    a = c3.TemplateLIF(W, seed=11)
    b = c3.TemplateLIF(W, seed=11)
    for _ in range(2000):
        assert (a.step(drive) == b.step(drive)).all()
    assert np.allclose(a.v, b.v)


# --- published geometry and width estimator ---------------------------------

def test_pisokas_block_angles():
    nine = c3.pisokas_block_angles(9)
    assert nine.tolist() == [0, 45, 90, 135, 180, 225, 270, 315, 0]
    eight = c3.pisokas_block_angles(8)
    assert eight.tolist() == [0, 45, 90, 135, 180, 225, 270, 315]


def test_measure_bump1_matches_published_formula():
    # 3-column run: their optimization target, (3-1)/8*360 = 90
    act = np.array([0, 0, 10, 12, 11, 0, 0, 0], dtype=float)
    assert c3.measure_bump1_deg(act, circular=True) == 90.0
    assert c3.measure_bump1_deg(act, circular=False) == 90.0
    # 4-column run = 135
    act4 = np.array([0, 9, 10, 12, 11, 0, 0, 0], dtype=float)
    assert c3.measure_bump1_deg(act4, circular=True) == 135.0
    # single column = 0 width under their formula (k-1 = 0)
    act1 = np.array([0, 0, 10, 0, 0, 0, 0, 0], dtype=float)
    assert c3.measure_bump1_deg(act1, circular=True) == 0.0


def test_measure_bump1_wrap_behaviour():
    wrapped = np.array([10, 11, 0, 0, 0, 0, 9, 12], dtype=float)
    # circular variant sees one 4-column run
    assert c3.measure_bump1_deg(wrapped, circular=True) == 135.0
    # verbatim (their code) takes the FIRST run only: 2 columns -> 45
    assert c3.measure_bump1_deg(wrapped, circular=False) == 45.0


def test_measure_bump1_degenerate_profiles():
    assert c3.measure_bump1_deg(np.zeros(8)) == 0.0
    assert c3.measure_bump1_deg(np.full(8, 7.0)) == 360.0


def test_von_mises_rates_range_and_peak():
    angles = c3.pisokas_block_angles(8)
    rates = c3.von_mises_rates(angles, 90.0)
    assert rates.min() == pytest.approx(c3.BG_HZ)
    assert rates.max() == pytest.approx(c3.DRIVE_PEAK_HZ)
    assert rates[np.argmin(np.abs(angles - 90.0))] == rates.max()


# --- circular statistics and verdict bars -----------------------------------

def test_circular_stats_and_err():
    radians = np.deg2rad([0.0, 90.0, 180.0, 270.0])
    act = np.array([0.0, 10.0, 0.0, 0.0])
    mass, ang, cv = c3.circular_stats(act, radians)
    assert mass == 10.0 and ang == pytest.approx(90.0)
    assert cv == pytest.approx(0.0)
    assert c3.circ_err_deg(350.0, 10.0) == pytest.approx(20.0)
    assert np.isnan(c3.circ_err_deg(float("nan"), 10.0))


def _row(retention=0.5, circvar=0.2, err=10.0):
    return {"retention": retention, "final_circvar": circvar,
            "err_deg": err}


def test_g1_angle_pass_bars():
    assert c3.g1_angle_pass(_row())
    assert not c3.g1_angle_pass(_row(retention=0.04))
    assert not c3.g1_angle_pass(_row(circvar=0.61))
    assert not c3.g1_angle_pass(_row(err=46.0))
    assert not c3.g1_angle_pass(_row(err=float("nan")))


def test_assemble_point_verdict():
    rows = [_row() for _ in range(6)] + [_row(retention=0.0)] * 2
    good_steer = {"rate_left": 20.0, "rate_right": -15.0}
    v = c3.assemble_point_verdict(rows, good_steer)
    assert v["g1"] and v["g1_n_pass"] == 6 and v["g2"]
    # same-signed steering fails G2
    v2 = c3.assemble_point_verdict(rows, {"rate_left": 20.0,
                                          "rate_right": 15.0})
    assert not v2["g2"]
    # sub-floor magnitude fails G2
    v3 = c3.assemble_point_verdict(rows, {"rate_left": 20.0,
                                          "rate_right": -5.0})
    assert not v3["g2"]
    # 5/8 angles fails G1
    v4 = c3.assemble_point_verdict(rows[:5] + [_row(retention=0.0)] * 3,
                                   good_steer)
    assert not v4["g1"]


# --- AC-6 class-scale mapping ------------------------------------------------

def _toy_counts():
    # [post, pre]; types: 0,1 EPG; 2 PEN_a; 3 Delta7
    types = np.array(["EPG", "EPG", "PEN_a(PEN1)", "Delta7"])
    S = np.zeros((4, 4))
    S[2, 0] = 10.0          # EPG -> PEN_a, counts 10
    S[2, 1] = 30.0          # EPG -> PEN_a, counts 30
    S[0, 2] = 8.0           # PEN_a -> EPG
    S[3, 0] = 5.0           # EPG -> Delta7
    S[2, 3] = -20.0         # Delta7 -> PEN_a (compiled sign negative)
    S[1, 0] = -4.0          # EPG -> EPG: NOT a Pisokas class (fallback)
    return S, types


def test_class_scales_mean_drive_rule():
    S, types = _toy_counts()
    scales = c3.class_scales(S, types)
    # one PEN_a cell receives 10+30 = 40 counts from E-PG:
    # scale = 99.968... / 40
    assert scales[("E-PG", "P-EN")] == pytest.approx(
        c3.PISOKAS_WEIGHTS[("E-PG", "P-EN")] / 40.0)
    assert scales[("P-EN", "E-PG")] == pytest.approx(
        c3.PISOKAS_WEIGHTS[("P-EN", "E-PG")] / 8.0)
    assert scales[("E-PG", "Delta7")] == pytest.approx(
        c3.PISOKAS_WEIGHTS[("E-PG", "Delta7")] / 5.0)
    # inhibitory class scale carries the Pisokas sign
    assert scales[("Delta7", "P-EN")] == pytest.approx(
        c3.PISOKAS_WEIGHTS[("Delta7", "P-EN")] / 20.0)


def test_expand_weights_signs_and_heterogeneity():
    S, types = _toy_counts()
    W = c3.expand_weights(S, types)
    # count heterogeneity preserved within a class: 30 vs 10 -> 3x
    assert W[2, 1] == pytest.approx(3.0 * W[2, 0])
    # class mean drive equals the Pisokas weight
    assert W[2, 0] + W[2, 1] == pytest.approx(
        c3.PISOKAS_WEIGHTS[("E-PG", "P-EN")])
    # inhibition negative, excitation positive
    assert W[2, 3] < 0 and W[2, 0] > 0
    # fallback pair (EPG->EPG): compiled sign, fallback unit magnitude
    assert W[1, 0] == pytest.approx(-c3.FALLBACK_MAGNITUDE)


# --- fixture integrity -------------------------------------------------------

def test_fixture_structure_and_weight_table():
    z = np.load(c3.FIXTURE, allow_pickle=False)
    labels = z["labels_post_pre"]
    assert labels.shape == (60, 60)
    assert z["epg_idx"].size == 18
    assert z["penpeg_idx"].size == 34
    assert z["delta7_idx"].size == 8
    # ESTABLISHED layout [P-EN 16, P-EG 18, E-PG 18, Delta7 8]
    assert (z["penpeg_idx"][:16] == np.arange(16)).all()
    assert (z["delta7_idx"] == np.arange(52, 60)).all()
    table = dict(zip(np.round(z["weight_labels"], 3).tolist(),
                     z["weight_values"].tolist()))
    assert table[1.0] == pytest.approx(6.07203896674184)
    assert table[1.1] == pytest.approx(47.9173822984772)
    assert table[-1.0] == pytest.approx(-35.6772759590409)
    assert table[-1.1] == pytest.approx(-19.3358579258735)
    assert table[3.0] == pytest.approx(99.9680554605268)
    # orientation check: label 1.1 (E-PG -> Delta7) rows must all lie
    # in the Delta7 block if the matrix is [post, pre]
    rows = np.unique(np.nonzero(np.isclose(labels, 1.1))[0])
    assert set(rows.tolist()) <= set(z["delta7_idx"].tolist())


def test_prerequisites_do_not_flag_fixture():
    missing = c3.check_prerequisites()
    assert not any("validation fixture" in m for m in missing)
    assert not any("scipy" in m for m in missing)


# --- THE VALIDATION GATE (required by the frozen registration) ---------------

def test_validation_gate_reproduces_published_fly_bump():
    """The frozen registration: 'If the engine cannot reproduce the
    literature circuit, there is no instrument.' Runs the published
    60-neuron fly circuit through the engine (~17 s)."""
    gate = c3.validate_engine_on_pisokas()
    assert gate["pass"], gate
    assert not gate["unstable"]
    assert 60.0 <= gate["mean_width_deg"] <= 120.0
    for t in gate["trials"]:
        assert t["retention"] >= c3.RETENTION_MIN
        assert t["circvar"] <= c3.CIRCVAR_MAX
        assert t["err_deg"] <= c3.ERR_MAX_DEG
        # per-trial width is the 45-deg-quantized published statistic
        assert t["width_deg"] % 45.0 == 0.0
