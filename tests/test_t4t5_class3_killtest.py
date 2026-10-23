"""Tests for scripts/arenas/t4t5_class3_killtest.py (H-T4T5-CLASS3-DS,
Task 10 item 2). The MaleCNS measurement is data-gated and local; what
is testable in-cloud is the instrument: the frozen constants (pinned
physiology carried from the cx class-3 engine, the fc2/fc25 protocol
constants, the band text identity), the extended engine's three
declared mechanisms (per-type membrane tau via Cm at fixed Rm,
two-state exponential synapses with the unitary-PSC-equivalent area
normalization asserted numerically against the original psc_template,
signed external drive), the AT-2 weight mapping, the statistic and
window machinery, the BLOCKED-floor logic -- and, the load-bearing one
required by the frozen registration, GATE A: the idealized delay-line
correlator at the pinned spiking physiology must reach DSI >= 0.30
with its temporal-frequency optimum strictly inside 0.5-2 Hz AND
collapse below 0.05 with arm taus equalized, in-cloud, before anything
about MaleCNS is claimed."""

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location(
    "t4t5_class3_killtest", ROOT / "scripts/arenas/t4t5_class3_killtest.py")
t4 = importlib.util.module_from_spec(_spec)
sys.modules["t4t5_class3_killtest"] = t4
_spec.loader.exec_module(t4)

cx = t4.cx
fc2 = t4.fc2
fc25 = t4.fc25


# --- frozen constants (registration killtest_design.md section 2) -----------

def test_band_text_equals_fc2():
    assert t4.BAND_TEXT == fc2.BAND_TEXT
    assert "median DSI >= 0.3" in t4.BAND_TEXT
    assert t4.fc2.CITATION == "Maisak et al. 2013, Nature 500:212-216"


def test_pinned_physiology_carried_from_cx():
    assert t4.DT_S == cx.DT_S == 1e-4
    assert t4.RM_OHM == cx.RM_OHM == 1e6
    assert t4.V_REST == cx.V_REST == -52e-3
    assert t4.V_THRESH == cx.V_THRESH == -45e-3
    assert t4.AP_END == cx.AP_END == -72e-3
    assert t4.BG_HZ == cx.BG_HZ == 5.0
    assert t4.DRIVE_PEAK_HZ == cx.DRIVE_PEAK_HZ == 190.0
    assert t4.PISOKAS_TAU_M_MS == 20.0
    # pinned Pisokas kernel: 2 ms rise, 5 ms half-life (tau = 5/ln2)
    assert t4.PSC_RISE_TAU_MS == 2.0
    assert t4.PSC_DECAY_TAU_MS == pytest.approx(5.0 / math.log(2.0))


def test_frozen_protocol_constants():
    assert t4.SPEEDS == (2.5, 5.0, 10.0)
    assert t4.DIRECTIONS == ("+x", "-x", "+y", "-y")
    assert t4.WINDOW_BEFORE_COL == 2.0
    assert t4.WINDOW_AFTER_S == 0.75
    assert t4.SETTLE_S == 2.5 and t4.TAIL_S == 0.8
    assert t4.INPUT_DRIVE_SIGN == -1.0          # histaminergic injection
    assert t4.GRID_SCALES == (0.5, 1.0, 2.0)
    assert t4.REWIRE_SEED_BASE == 4242 and t4.REWIRE_SEEDS == (0, 1, 2)
    assert t4.MAX_UNSTABLE_FRACTION == 0.20
    assert t4.EXPECTED_DIMS == {"nodes": 2701, "driven": 507,
                                "scored": 498, "columns": 169}
    assert t4.GAIN_GRID == fc25.EXTENDED_GAIN_GRID
    assert t4.CAL_DIRECTION == fc2.CAL_DIRECTION
    assert t4.CAL_SPEED == 5.0
    # R1: declared spiking calibration target (geometric midpoint of
    # the pinned input-rate band), never retuned
    assert t4.CAL_TARGET_HZ == pytest.approx(math.sqrt(5.0 * 190.0))


def test_frozen_gate_bars_and_tf_mapping():
    assert t4.GATE_DSI_MIN == 0.30
    assert t4.GATE_COLLAPSE_MAX == 0.05
    assert t4.GATE_TF_BAND_HZ == (0.5, 2.0)
    assert t4.SPEED_TO_TF_HZ == {2.5: 0.5, 5.0: 1.0, 10.0: 2.0}
    assert t4.FC25_REFERENCE_DSI == 0.3216
    assert t4.FC25_REFERENCE_TOL == 0.02
    # gate arm kernels sit inside the registered bands
    assert 10.0 <= t4.GATE_FAST_KERNEL.decay_tau_ms <= 40.0
    assert 100.0 <= t4.GATE_SLOW_KERNEL.rise_tau_ms <= 300.0
    assert 100.0 <= t4.GATE_SLOW_KERNEL.decay_tau_ms <= 300.0


def test_curated_i6_table_contents():
    # BLOCKED floor (3) audits against exactly these rows
    signs = fc2.CURATED_SIGNS
    assert signs["Mi9"] == -1 and signs["Mi4"] == -1
    for t in ("Mi1", "Tm1", "Tm2", "Tm3", "Tm4", "Tm9",
              "T4a", "T4b", "T4c", "T4d", "T5a", "T5b", "T5c", "T5d"):
        assert signs[t] == +1


# --- two-state synapse: the required normalization equality ------------------

def _discrete_area(kernel, weight):
    n = int(25 * kernel.decay_tau_ms * 1e-3 / t4.DT_S)
    return float(t4.two_state_unit_response(kernel, weight, n).sum()
                 * t4.DT_S)


def test_unitary_psc_area_matches_template_numerically():
    """THE REQUIRED UNIT TEST: each synapse's time-integrated current
    for one spike equals the Pisokas unitary PSC area scaled by |W|,
    numerically against the original psc_template."""
    template_area = float(np.sum(cx.psc_template()) * t4.DT_S)
    assert t4.PISOKAS_UNIT_AREA == pytest.approx(template_area, rel=1e-12)
    for kernel in (t4.PISOKAS_KERNEL,
                   t4.SynKernel(2.0, 133.18),      # Tm2-class long kernel
                   t4.GATE_SLOW_KERNEL):           # 150/300 ms gate arm
        for weight in (1.0, 3.5, 0.2):
            assert _discrete_area(kernel, weight) == pytest.approx(
                template_area * weight, rel=1e-6)


def test_unitary_area_holds_through_the_engine():
    """Same equality through the full engine path: one forced
    presynaptic spike, the postsynaptic current integrated."""
    from scipy import sparse
    W = sparse.csc_matrix(np.array([[0.0, 0.0], [2.0, 0.0]]))
    for kernel in (t4.PISOKAS_KERNEL, t4.SynKernel(2.0, 300.0)):
        eng = t4.TwoStateLIF([(kernel, W)], np.full(2, 20.0), seed=0)
        zeros = np.zeros(2)
        eng.v[0] = 0.0                     # force a spike this step
        area = 0.0
        steps = int(25 * kernel.decay_tau_ms * 1e-3 / t4.DT_S)
        for _ in range(steps):
            eng.step(zeros, zeros)
            area += float((eng.P - eng.R).sum(axis=0)[1]) * t4.DT_S
        assert area == pytest.approx(2.0 * t4.PISOKAS_UNIT_AREA, rel=1e-5)


def test_synkernel_rejects_degenerate_taus():
    with pytest.raises(ValueError):
        t4.SynKernel(5.0, 5.0)
    with pytest.raises(ValueError):
        t4.SynKernel(10.0, 2.0)


# --- engine mechanics ---------------------------------------------------------

def test_engine_silent_without_input():
    eng = t4.TwoStateLIF([], np.full(3, 20.0), seed=0)
    zeros = np.zeros(3)
    for _ in range(200):
        assert not eng.step(zeros, zeros).any()
    assert np.allclose(eng.v, t4.V_REST)
    assert not eng.unstable


def test_per_type_membrane_tau_via_cm():
    """Extension 1: tau = Rm*Cm with Rm fixed. Relaxation from a
    displaced membrane must follow each neuron's own tau."""
    taus_ms = np.array([20.0, 133.18])
    eng = t4.TwoStateLIF([], taus_ms, seed=0)
    assert eng.cm[0] == pytest.approx(2e-8)       # the cx pinned 20 nF
    assert eng.cm[1] == pytest.approx(133.18e-3 / t4.RM_OHM)
    eng.v = t4.V_REST + np.full(2, 5e-3)
    zeros = np.zeros(2)
    steps = int(round(0.02 / t4.DT_S))            # one 20 ms tau
    for _ in range(steps):
        eng.step(zeros, zeros)
    d = eng.v - t4.V_REST
    assert d[0] / 5e-3 == pytest.approx(math.exp(-1.0), rel=0.02)
    assert d[1] / 5e-3 == pytest.approx(math.exp(-0.02 / 0.13318),
                                        rel=0.02)


def test_signed_external_drive():
    """Extension 3: the inhibitory Poisson stream hyperpolarizes and
    never fires; the excitatory stream fires."""
    eng = t4.TwoStateLIF([], np.full(1, 20.0), seed=3)
    exc, inh = np.zeros(1), np.full(1, 2000.0)
    vmin = 0.0
    for _ in range(5000):
        assert not eng.step(exc, inh).any()
        vmin = min(vmin, float(eng.v[0] - t4.V_REST))
    assert vmin < -1e-3
    eng2 = t4.TwoStateLIF([], np.full(1, 20.0), seed=3)
    spiked = False
    for _ in range(20000):
        if eng2.step(np.full(1, 2000.0), np.zeros(1))[0]:
            spiked = True
            break
    assert spiked


def test_engine_synaptic_sign_and_propagation():
    from scipy import sparse
    Wp = sparse.csc_matrix(np.array([[0.0, 0.0], [200.0, 0.0]]))
    eng = t4.TwoStateLIF([(t4.PISOKAS_KERNEL, Wp)], np.full(2, 20.0),
                         seed=2)
    drive = np.array([2000.0, 0.0])
    zeros = np.zeros(2)
    post_spiked = False
    for _ in range(20000):
        if eng.step(drive, zeros)[1]:
            post_spiked = True
            break
    assert post_spiked
    Wn = sparse.csc_matrix(np.array([[0.0, 0.0], [-200.0, 0.0]]))
    eng2 = t4.TwoStateLIF([(t4.PISOKAS_KERNEL, Wn)], np.full(2, 20.0),
                          seed=2)
    vmin = 0.0
    for _ in range(5000):
        eng2.step(drive, zeros)
        vmin = min(vmin, float(eng2.v[1] - t4.V_REST))
    assert vmin < -1e-3 and eng2.v[1] < t4.V_THRESH


def test_engine_deterministic_and_snapshot_restore():
    from scipy import sparse
    W = sparse.csc_matrix(
        np.array([[0.0, 0.0, 0.0], [50.0, 0.0, 0.0], [0.0, 50.0, 0.0]]))
    drive = np.full(3, 300.0)
    zeros = np.zeros(3)
    a = t4.TwoStateLIF([(t4.PISOKAS_KERNEL, W)], np.full(3, 20.0), seed=11)
    b = t4.TwoStateLIF([(t4.PISOKAS_KERNEL, W)], np.full(3, 20.0), seed=11)
    for _ in range(1500):
        assert (a.step(drive, zeros) == b.step(drive, zeros)).all()
    snap = a.snapshot()
    trace_a = [a.step(drive, zeros).copy() for _ in range(500)]
    va = a.v.copy()
    a.restore(snap)
    trace_b = [a.step(drive, zeros).copy() for _ in range(500)]
    assert all((x == y).all() for x, y in zip(trace_a, trace_b))
    assert np.allclose(a.v, va)                # bit-identical continuation


# --- parameter mapping --------------------------------------------------------

def _params():
    return t4.load_trained_params()


def test_membrane_tau_vector_trained_and_uniform():
    params = _params()
    types = np.array(["Mi1", "Tm2", "Tm9"])
    tau = t4.membrane_tau_vector(types, params)
    assert tau[0] == pytest.approx(
        params["types"]["Mi1"]["tau_ms"]["subset_mean"])
    assert tau[0] == pytest.approx(19.8, abs=0.1)     # registration's example
    assert tau[1] == pytest.approx(133.2, abs=0.1)    # Tm2, the long kernel
    assert tau[1] == pytest.approx(
        params["types"]["Tm2"]["tau_ms"]["subset_mean"])
    assert tau[2] == pytest.approx(46.7, abs=0.1)     # Tm9
    uni = t4.membrane_tau_vector(types, params, uniform_ms=50.0)
    assert (uni == 50.0).all()
    with pytest.raises(KeyError):
        t4.membrane_tau_vector(np.array(["NotAType"]), params)


def test_synapse_projections_kernel_classes():
    """R2: kernel class = presynaptic type, decay tau = its trained
    tau, rise = the pinned 2 ms; the class matrices partition W."""
    from scipy import sparse
    params = _params()
    types = np.array(["Mi1", "Tm2", "T4a"])
    W = sparse.csr_matrix(np.array([[0.0, 2.0, 0.0],
                                    [1.0, 0.0, 3.0],
                                    [4.0, -5.0, 0.0]]))
    proj = t4.synapse_projections(W, types, params)
    decays = {round(k.decay_tau_ms, 2) for k, _ in proj}
    expected = {round(params["types"][t]["tau_ms"]["subset_mean"], 2)
                for t in types}
    assert decays == expected
    assert all(k.rise_tau_ms == 2.0 for k, _ in proj)
    total = sum((M for _, M in proj)).toarray()
    assert np.allclose(total, W.toarray())
    # each class holds exactly its presynaptic type's columns
    for kern, M in proj:
        cols = np.unique(sparse.coo_matrix(M).col)
        owner = {round(params["types"][t]["tau_ms"]["subset_mean"], 6)
                 for t in types[cols]}
        assert owner == {round(kern.decay_tau_ms, 6)}
    uni = t4.synapse_projections(W, types, params, uniform_ms=50.0)
    assert len(uni) == 1 and uni[0][0].decay_tau_ms == 50.0


def test_at2_weight_mapping_on_toy_patch():
    """AT-2: W_ij = curated_sign(pre) x alpha_trained(pair) x N_ij;
    untrained pairs get flyvis's init rho/<N> (via
    fc25.trained_weight_matrix, the single source of truth)."""
    from scipy import sparse
    params = _params()
    # types chosen so Mi9 tests the curated sign flip
    types = np.array(["L1", "Mi1", "Mi9"])
    counts = sparse.csr_matrix(np.array([[0.0, 0.0, 0.0],
                                         [10.0, 0.0, 6.0],
                                         [4.0, 0.0, 0.0]]))
    W, coverage = t4.at2_weight_matrix(
        {"raw_counts": counts, "types": types}, params)
    dense = W.toarray()
    a = params["pairs"]
    if "L1->Mi1" in a:
        assert dense[1, 0] == pytest.approx(
            10.0 * a["L1->Mi1"]["subset_mean"])
    # Mi9 -> Mi1 must come out NEGATIVE whatever the raw sign
    assert dense[1, 2] < 0
    assert coverage["pairs_total"] >= 2


def test_shiu_weight_matrix_bridge():
    from scipy import sparse
    psp = t4.unitary_psp_mv()
    assert 0.3 < psp < 5.0           # sane single-PSC PSP on the pinned cell
    types = np.array(["Mi1", "Mi9"])
    counts = sparse.csr_matrix(np.array([[0.0, 8.0], [3.0, 0.0]]))
    W = t4.shiu_weight_matrix({"raw_counts": counts, "types": types})
    dense = W.toarray()
    assert dense[1, 0] == pytest.approx(3.0 * 0.275 / psp)
    assert dense[0, 1] == pytest.approx(-8.0 * 0.275 / psp)   # Mi9 is -


# --- statistic machinery ------------------------------------------------------

def test_dsi_from_responses_exact():
    # 2 cells, 4 directions: cell 0 prefers +x with DSI 0.5; cell 1 flat
    resp = np.array([[3.0, 1.0],
                     [1.0, 1.0],
                     [2.0, 1.0],
                     [2.0, 1.0]])
    per_speed = np.tile(resp[None, :, :] / 3.0, (3, 1, 1))
    dsi, defined, pref, speed_pref = t4.dsi_from_responses(resp, per_speed)
    assert defined.all()
    assert t4.DIRECTIONS[pref[0]] == "+x"
    assert dsi[0] == pytest.approx((3 - 1) / (3 + 1))
    assert dsi[1] == pytest.approx(0.0)
    assert speed_pref.shape == (3, 2)
    assert speed_pref[0, 0] == pytest.approx(1.0)
    # zero responses -> undefined, not a number
    dsi0, defined0, _, _ = t4.dsi_from_responses(
        np.zeros((4, 1)), np.zeros((3, 4, 1)))
    assert not defined0.any() and np.isnan(dsi0[0])


def test_band_metrics_delegation_pass_and_fail():
    """The verdict machine is fc2.band_metrics, fed with the spiking
    accumulators' shapes: a strongly DS table passes, isotropic fails."""
    m = 8
    score_types = np.array(["T4a", "T4b", "T4c", "T4d",
                            "T5a", "T5b", "T5c", "T5d"])
    is_t4 = np.array([t.startswith("T4") for t in score_types])
    resp_ds = {p: np.zeros((4, m)) for p in ("on", "off")}
    for i in range(m):
        resp_ds["on" if i < 4 else "off"][i % 4, i] = 10.0
        resp_ds["on" if i < 4 else "off"][
            t4.DIRECTIONS.index(t4.OPPOSITE[t4.DIRECTIONS[i % 4]]), i] = 1.0
    speed_ds = {p: np.tile(resp_ds[p][None] / 3.0, (3, 1, 1))
                for p in ("on", "off")}
    band = fc2.band_metrics(resp_ds, speed_ds, score_types, is_t4)
    assert band["pass"] and band["median_dsi_pooled"] > 0.3
    flat = {p: np.ones((4, m)) for p in ("on", "off")}
    speed_flat = {p: np.ones((3, 4, m)) / 3.0 for p in ("on", "off")}
    band2 = fc2.band_metrics(flat, speed_flat, score_types, is_t4)
    assert not band2["pass"]
    assert band2["median_dsi_pooled"] == pytest.approx(0.0)


def test_traverse_geometry_direction_invariant():
    x = np.array([0.0, 1.0, 2.0, 3.0])
    y = np.array([0.0, 0.5, 1.0, 1.5])
    step_counts = set()
    for d in t4.DIRECTIONS:
        _, _, steps = t4.traverse_geometry(x, y, t4.DIR_VECTORS[d], 5.0)
        step_counts.add(steps)
    assert len(step_counts) == 1     # same traverse length, every direction


def test_run_edge_sweep_window_bookkeeping():
    """The v2 window: for an interior cell the effective window must be
    2 columns-of-travel + 0.75 s; evoked is clamped at zero."""
    x = np.array([0.0, 1.0, 2.0])
    y = np.zeros(3)
    eng = t4.TwoStateLIF([], np.full(3, 20.0), seed=0)
    snap = eng.snapshot()
    for speed in t4.SPEEDS:
        evoked, window_s, stable = t4.run_edge_sweep(
            eng, snap, x, y, np.array([0]), np.array([1]),
            np.zeros(3), (1.0, 0.0), speed, "on", +1.0)
        assert stable
        expected = t4.WINDOW_BEFORE_COL / speed + t4.WINDOW_AFTER_S
        assert window_s[0] == pytest.approx(expected, abs=3 * t4.DT_S)
        assert evoked[0] >= 0.0


# --- gates and floors ---------------------------------------------------------

def test_patch_column_count_full_grid():
    h1, h2 = np.meshgrid(np.arange(13, 26), np.arange(14, 27))
    h1, h2 = h1.ravel().astype(float), h2.ravel().astype(float)
    x = h1 + 0.5 * h2
    y = (3 ** 0.5 / 2.0) * h2
    assert t4.patch_column_count(x, y) == 169


def test_gate_b_dims_logic():
    h1, h2 = np.meshgrid(np.arange(13.0, 26.0), np.arange(14.0, 27.0))
    patch = {"node_count": 2701,
             "x": (h1 + 0.5 * h2).ravel(),
             "y": ((3 ** 0.5 / 2.0) * h2).ravel()}
    good = t4.gate_b_dims(patch, 507, 498)
    assert good["pass"]
    bad = t4.gate_b_dims(patch, 506, 498)
    assert not bad["pass"]


def test_prerequisites_do_not_flag_repo_files():
    missing = t4.check_prerequisites()
    assert not any("trained params" in m for m in missing)
    assert not any("scipy" in m for m in missing)


@pytest.mark.skipif((ROOT / "data/processed/male-cns-v1.0/"
                     "literal-rate-signed-modulators").exists(),
                    reason="runtime present: main would run the real "
                           "measurement, which is not a unit test")
def test_main_blocks_without_runtime(monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv",
                        ["t4t5_class3_killtest.py", "--output",
                         str(tmp_path / "out.json")])
    assert t4.main() == 3            # BLOCKED, the registered exit code


# --- gate A circuit structure -------------------------------------------------

def test_ideal_correlator_structure():
    c = t4.build_ideal_correlator(equalized=False)
    assert (c["tau_m_ms"] == t4.PISOKAS_TAU_M_MS).all()   # pinned membrane
    assert c["score_idx"].size == 4 * t4.GATE_N_DETECTORS_PER_DIR
    assert len(c["detector_dirs"]) == c["score_idx"].size
    # ~1-column offset arms: every detector's lead column sits exactly
    # one column opposite its preferred direction
    x, y = c["x"], c["y"]
    slow_W = c["projections"][2][1].tocoo()
    for di, dname in enumerate(c["detector_dirs"]):
        det = c["score_idx"][di]
        dx, dy = t4.DIR_VECTORS[dname]
        rows = slow_W.row == det
        assert rows.any()
        for pre in slow_W.col[rows]:
            assert x[pre] == pytest.approx(x[det] - dx)
            assert y[pre] == pytest.approx(y[det] - dy)
    # the equalized twin changes ONLY the slow arm's kernel
    e = t4.build_ideal_correlator(equalized=True)
    assert e["projections"][2][0] == t4.GATE_FAST_KERNEL
    assert c["projections"][2][0] == t4.GATE_SLOW_KERNEL
    for k in (0, 1, 3):
        assert c["projections"][k][0] == e["projections"][k][0]
    for k in range(4):
        assert np.allclose(c["projections"][k][1].toarray(),
                           e["projections"][k][1].toarray())
    # push-pull transient stage: equal-magnitude is NOT required (the
    # inhibitory half dominates so the steady state is suppressive)
    assert t4.GATE_W_XT_INH > t4.GATE_W_XT


# --- THE VALIDATION GATE A (required by the frozen registration) --------------

def test_gate_a_delay_line_capacity_and_collapse():
    """The decisive in-cloud gate: the pinned spiking physiology must
    express delay-line direction selectivity (median DSI >= 0.30, TF
    optimum strictly inside 0.5-2 Hz) and lose it when the arm taus
    are equalized (median DSI < 0.05). ~90 s of simulation."""
    gate = t4.run_gate_a()
    dl, eq = gate["delay_line"], gate["equalized"]
    assert gate["pass"], gate
    assert dl["median_dsi"] >= t4.GATE_DSI_MIN
    assert dl["defined_fraction"] >= 0.5
    assert t4.GATE_TF_BAND_HZ[0] < dl["tf_optimum_hz"] \
        < t4.GATE_TF_BAND_HZ[1]
    assert np.isfinite(eq["median_dsi"])
    assert eq["median_dsi"] < t4.GATE_COLLAPSE_MAX
    assert dl["unstable_runs"] == 0 and eq["unstable_runs"] == 0
    # the delay line's detectors point where they were built to point
    agree = sum(p == d for p, d in zip(dl["preferred"], dl["designed"]))
    assert agree >= int(0.75 * len(dl["designed"]))
