"""In-cloud gates for H-FLYGI-FLYBENCH-SFA and H-FLYGI-FLYBENCH-TERMINAL.

Registration: docs/arenas/task10_menu/killtest_design.md section 6 (FROZEN
2026-10-23, before any of the code under test existed). These are the
registered IN-CLOUD GATES, asserted as unit tests:

  (1) SFA off-switch bit-identity (sfa_b = 0 byte-identical to the
      pre-extension engine, asserted against a frozen copy of the
      pre-extension step), plus the terminal adapter's off-convention
      (no terminal source -> byte-identical to the uniform adapter).
  (2) Single-neuron constant-drive adaptation vs the Benda & Herz 2003
      closed form (steady-state rate reduction and ISI lengthening;
      tolerances declared below at the assertion sites).
  (3) SFA toy equivalence: FlyBench's own AdaptiveLIFSimulator vs our
      engine+SFA behind the adapter on the full flybench toy suite --
      deltas must move the SAME DIRECTION as their adaptive-vs-reference
      delta. (Measured at build time 2026-10-23: on the toy BOTH engines
      move DOWN -- theirs graded -0.158 / hard_graded -0.172, ours
      -0.159 / -0.148. Their flywire783 row moves UP; the toy is a
      synthetic network and the gate is about direction AGREEMENT, not
      about reproducing flywire783.)
  (4) Terminal toy equivalence with a SYNTHETIC injected terminal matrix
      vs their TerminalLIFSimulator, within the declared dt (0.5 vs 0.1
      ms) / no-delay-line differences.
  (5) Verdict-script logic on synthetic JSONs: every bar and floor of
      scripts/arenas/flybench_mechanisms_verdict.py.

The MaleCNS measurement itself is the user's local run (data-gated; the
runtime and the flybench MaleCNS build exist only there).

NOTE (environment, reported in the build record): flybench 0.2.1 is NOT
pip-installed in the in-cloud test venv; it is imported from the clone at
/home/user/brandoncho369/flybench (same version the due diligence read).
On the user's machine the editable install resolves first and the clone
path is never consulted.
"""

import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# flybench: installed package first; else the in-container clone (0.2.1).
FLYBENCH_CLONE = Path("/home/user/brandoncho369/flybench")
if importlib.util.find_spec("flybench") is None and \
        (FLYBENCH_CLONE / "flybench" / "__init__.py").exists():
    sys.path.insert(0, str(FLYBENCH_CLONE))
HAVE_FLYBENCH = importlib.util.find_spec("flybench") is not None


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


if HAVE_FLYBENCH:
    ad = _load("flygi_flybench_adapter",
               ROOT / "scripts/arenas/flygi_flybench_adapter.py")
vd = _load("flybench_mechanisms_verdict",
           ROOT / "scripts/arenas/flybench_mechanisms_verdict.py")

from flygi.dynamics.spiking import (  # noqa: E402
    ParameterTable,
    SpikingError,
    SpikingNetwork,
    TypeParams,
)
from scipy import sparse  # noqa: E402

needs_flybench = pytest.mark.skipif(not HAVE_FLYBENCH,
                                    reason="flybench not importable")


# ===========================================================================
# GATE 1 -- off-switch bit-identity
# ===========================================================================

def _frozen_reference_step(net, external):
    """The PRE-EXTENSION SpikingNetwork.step body, copied VERBATIM from git
    08fac61 (src/flygi/dynamics/spiking.py) with `self` -> `net`. This is
    the frozen comparator for the registered bit-identity gate; it must
    never be edited to track the engine."""
    p = net.params
    drive = net.w_scale * (net.matrix @ net.last_output)
    net.i_syn += (net.dt / p["tau_syn_ms"]) * (-net.i_syn) + drive
    total_input = net.i_syn if external is None else net.i_syn + external
    refractory = net._refractory_left > 0
    dv = (net.dt / p["tau_m_ms"]) * (-(net.v - p["v_rest"])) + net.dt * total_input
    net.v = np.where(refractory, net.v, net.v + dv).astype(np.float32)
    net._refractory_left = np.maximum(net._refractory_left - 1, 0)

    graded = p["graded"]
    spiking = ~graded
    fired = spiking & (net.v >= p["v_thresh"]) & ~refractory
    output = np.zeros(net.node_count, dtype=np.float32)
    output[fired] = 1.0
    output[graded] = (
        np.maximum(net.v[graded] - p["v_rest"][graded], 0.0)
        * p["graded_gain"][graded]
    )
    net.v[fired] = p["v_reset"][fired]
    net._refractory_left[fired] = net._refractory_steps[fired]
    net.last_output = output
    return output


def _random_engine(**kw):
    """A small signed network with a graded node, so every engine code path
    (drive, refractory, graded output) is exercised by the identity gate."""
    rng = np.random.default_rng(7)
    n = 80
    m = sparse.random(n, n, density=0.06, random_state=11, format="csr")
    m.data = rng.integers(1, 12, m.nnz).astype(np.float32)
    m.data[rng.random(m.nnz) < 0.3] *= -1.0
    types = np.array(["neuron"] * (n - 2) + ["APL", "APL"], dtype="U16")
    table = ParameterTable(
        default=TypeParams(tau_m_ms=20.0, v_thresh=-45.0, provenance="test",
                           tau_syn_ms=5.0, v_rest=-52.0, v_reset=-52.0,
                           refractory_ms=2.2),
        rules=[("APL", TypeParams(tau_m_ms=20.0, v_thresh=1e9,
                                  provenance="test graded", graded=True,
                                  graded_gain=0.01, v_rest=-52.0))],
    )
    return SpikingNetwork(m, types, table, dt_ms=0.5, w_scale=0.275 / 20.0,
                          seed=0, **kw)


def test_sfa_off_is_bit_identical_to_frozen_pre_extension_step():
    # GATE 1 (registered): sfa_b = 0 must be BYTE-identical to the engine as
    # it stood before the extension. Three-way: the frozen reference body,
    # the default constructor, and an explicit sfa_b=0.0 (with a non-default
    # tau, which must be inert when off).
    ref = _random_engine()
    new_default = _random_engine()
    new_off = _random_engine(sfa_b=0.0, sfa_tau_ms=123.0)
    rng = np.random.default_rng(3)
    for k in range(400):
        ext = None
        if k % 3 == 0:
            ext = np.zeros(ref.node_count)
            drv = rng.integers(0, ref.node_count, size=5)
            ext[drv] = 15.0
        out_ref = _frozen_reference_step(ref, ext)
        out_a = new_default.step(ext)
        out_b = new_off.step(ext)
        for net, out in ((new_default, out_a), (new_off, out_b)):
            assert out.tobytes() == out_ref.tobytes()
            assert net.v.tobytes() == ref.v.tobytes()
            assert net.i_syn.tobytes() == ref.i_syn.tobytes()
    assert new_off.sfa_a.tobytes() == np.zeros(
        ref.node_count, dtype=np.float32).tobytes()


def test_sfa_on_changes_dynamics_and_validates_tau():
    # the switch actually switches (otherwise the identity above is vacuous)
    off = _random_engine()
    on = _random_engine(sfa_b=0.1, sfa_tau_ms=200.0)
    ext = np.zeros(off.node_count)
    ext[:10] = 15.0
    same = True
    for _ in range(400):
        same = same and (off.step(ext).tobytes() == on.step(ext).tobytes())
    assert not same
    assert on.sfa_a.max() > 0.0
    with pytest.raises(SpikingError):
        _random_engine(sfa_b=0.1, sfa_tau_ms=0.0)


@needs_flybench
def test_terminal_adapter_off_is_bit_identical_to_uniform_adapter(tmp_path, monkeypatch):
    # GATE 1, terminal side: with no terminal source resolved the terminal
    # adapter is the uniform adapter exactly (their own off-convention).
    from flybench.connectome import load_connectome
    from flybench.sim import LIFParams, Stimulus
    monkeypatch.setattr(ad, "MECH_SIDECAR_DIR", tmp_path)
    monkeypatch.delenv(ad.TERMINAL_TABLE_ENV, raising=False)
    c = load_connectome("toy")
    grn = c.select("GRN_sugar")
    stim = [Stimulus(neurons=grn, rate_hz=100.0, t_start_ms=50.0,
                     t_end_ms=450.0)]
    r_u = ad.FlyGIAdapter(c, LIFParams(seed=3)).run(600.0, stim)
    r_t = ad.FlyGITerminalAdapter(c, LIFParams(seed=3)).run(600.0, stim)
    assert np.array_equal(r_u.spike_times_ms, r_t.spike_times_ms)
    assert np.array_equal(r_u.spike_neurons, r_t.spike_neurons)


# ===========================================================================
# GATE 2 -- single-neuron constant drive vs the Benda-Herz closed form
# ===========================================================================

# Shiu constants (the adapter's operating point)
_TAU_M, _V_TH_DIST, _T_REF, _DT = 20.0, 7.0, 2.2, 0.5
_SFA_B, _SFA_TAU = 2.0 / _TAU_M, 200.0      # derived bridge, pinned tau_a


def _one_neuron_spikes(sfa_b, current, steps=6000):
    table = ParameterTable(default=TypeParams(
        tau_m_ms=_TAU_M, v_thresh=-45.0, provenance="gate 2",
        tau_syn_ms=5.0, v_rest=-52.0, v_reset=-52.0, refractory_ms=_T_REF))
    net = SpikingNetwork(sparse.csr_matrix((1, 1), dtype=np.float32),
                         np.array(["n"]), table, dt_ms=_DT, w_scale=1.0,
                         seed=0, sfa_b=sfa_b, sfa_tau_ms=_SFA_TAU)
    ext = np.array([current])
    spikes = []
    for k in range(steps):
        if net.step(ext)[0] > 0:
            spikes.append((k + 1) * _DT)
    return np.asarray(spikes)


def _f0(current):
    """Continuous-time LIF rate (spikes/ms) at constant current, reset = rest."""
    v_inf = _TAU_M * current
    if v_inf <= _V_TH_DIST:
        return 0.0
    return 1.0 / (_T_REF + _TAU_M * math.log(v_inf / (v_inf - _V_TH_DIST)))


def _benda_herz_rate(current):
    """Benda & Herz 2003 universal-model fixed point for adaptation
    subtracted from the drive: f = f0(I - sfa_b * tau_a * f), using the
    mean-adaptation approximation (valid for tau_a >> ISI; here 200 ms vs
    ~12 ms). Bisection: the RHS is decreasing in f."""
    lo, hi = 0.0, _f0(current)
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if _f0(current - _SFA_B * _SFA_TAU * mid) > mid:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def test_sfa_single_neuron_matches_benda_herz_closed_form():
    current = 50.0 / _TAU_M          # a 50 mV-equivalent constant drive
    rate = lambda s, t0, t1: ((s >= t0) & (s < t1)).sum() / ((t1 - t0) / 1e3)  # noqa: E731
    s_off = _one_neuron_spikes(0.0, current)
    s_on = _one_neuron_spikes(_SFA_B, current)
    f_off = rate(s_off, 2000.0, 3000.0)           # Hz, steady window
    f_on = rate(s_on, 2000.0, 3000.0)
    # DECLARED TOLERANCES (instrument, not science): 10% relative on each
    # rate -- covers Euler-vs-exact integration at dt 0.5 ms and the
    # refractory rounding to 2.0 ms (measured at build time: unadapted
    # 200.0 Hz vs analytic 191.7; adapted 81.0 Hz vs fixed point 81.01).
    assert f_off == pytest.approx(_f0(current) * 1e3, rel=0.10)
    assert f_on == pytest.approx(_benda_herz_rate(current) * 1e3, rel=0.10)
    # steady-state rate reduction (the closed form predicts 81 vs 192 Hz
    # at these constants; require at least a 40% reduction)
    assert f_on < 0.6 * f_off
    # ISI lengthening: adaptation accumulates, so late ISIs are longer
    # (measured 5.5 ms -> 12.0 ms; require >= 1.5x)
    isi = np.diff(s_on)
    assert isi.size > 10 and isi[-1] > 1.5 * isi[0]
    # and the unadapted train does not lengthen (the control direction)
    isi0 = np.diff(s_off)
    assert isi0[-1] == pytest.approx(isi0[0], abs=_DT)


@needs_flybench
def test_sfa_adapter_derives_unit_bridge_from_pinned_constants(tmp_path, monkeypatch):
    # AF-10: sfa_b = b_mv / tau_m = 2.0 / 20.0 = 0.1, DERIVED in the adapter
    # from the pinned constants, never hardcoded.
    from flybench.connectome import load_connectome
    from flybench.sim import LIFParams
    monkeypatch.setattr(ad, "MECH_SIDECAR_DIR", tmp_path)
    c = load_connectome("toy")
    a = ad.FlyGISFAAdapter(c, LIFParams(seed=0))
    assert a.net.sfa_b == pytest.approx(ad.SFA_B_MV / a.p.tau_m_ms)
    assert a.net.sfa_b == pytest.approx(0.1)
    assert a.net.sfa_tau_ms == ad.SFA_TAU_A_MS == 200.0
    # the sidecar carries the derived value for the verdict's off-guard
    side = [json.loads(p.read_text()) for p in tmp_path.glob("sfa-*.json")]
    assert side and side[0]["sfa_b"] == pytest.approx(0.1)
    assert side[0]["n_neurons"] == c.n


# ===========================================================================
# GATE 3 -- SFA toy-suite equivalence (full flybench toy suite; ~2.5 min)
# ===========================================================================

@needs_flybench
def test_sfa_toy_suite_deltas_move_same_direction_as_theirs(tmp_path, monkeypatch):
    from flybench.bench import load_tasks, run_suite
    from flybench.connectome import load_connectome
    from flybench.models.adaptive_lif import AdaptiveLIFSimulator
    from flybench.sim import LIFParams, LIFSimulator
    monkeypatch.setattr(ad, "MECH_SIDECAR_DIR", tmp_path)
    c = load_connectome("toy")
    tasks = load_tasks()
    reports = {}
    for name, cls in (("their_ref", LIFSimulator),
                      ("their_adaptive", AdaptiveLIFSimulator),
                      ("our_uniform", ad.FlyGIAdapter),
                      ("our_sfa", ad.FlyGISFAAdapter)):
        reports[name] = run_suite(c, LIFParams(seed=0), tasks=tasks,
                                  simulator=cls, seeds=1)
    their = {m: reports["their_adaptive"][m] - reports["their_ref"][m]
             for m in ("graded", "hard_graded")}
    ours = {m: reports["our_sfa"][m] - reports["our_uniform"][m]
            for m in ("graded", "hard_graded")}
    # DECLARED instrument floor: their delta must be large enough for its
    # direction to be defined (0.01; measured at build time: graded -0.158,
    # hard_graded -0.172 -- on the toy adaptation HURTS in BOTH engines).
    for metric in ("graded", "hard_graded"):
        assert abs(their[metric]) >= 0.01, \
            f"their adaptive-vs-reference {metric} delta ~0; gate undefined"
        assert math.copysign(1, ours[metric]) == math.copysign(1, their[metric]), (
            f"{metric}: ours {ours[metric]:+.4f} vs theirs {their[metric]:+.4f}"
            " move in opposite directions")


# ===========================================================================
# GATE 4 -- terminal equivalence on a synthetic injected terminal matrix
# ===========================================================================

def _synthetic_terminal_connectomes():
    """A(0) drives B(1) somatically; B drives D(2) somatically; C(3) contacts
    B's axon TERMINALS (inhibitory); E(4) bystander. Returns (with-terminal,
    without-terminal) flybench Connectomes over the same W."""
    import pandas as pd
    import scipy.sparse as sp
    from flybench.connectome import Connectome
    n = 5
    W = sp.csr_matrix(
        (np.array([60.0, 150.0, -40.0], dtype=np.float32),
         (np.array([0, 1, 3]), np.array([1, 2, 1]))), shape=(n, n))
    T = sp.csr_matrix(
        (np.array([40.0], dtype=np.float32),
         (np.array([3]), np.array([1]))), shape=(n, n))
    ann = pd.DataFrame({"root_id": np.arange(n, dtype=np.int64),
                        "cell_type": ["A", "B", "D", "C", "E"]})
    pos = np.full((n, 3), np.nan, dtype=np.float32)
    with_t = Connectome(root_ids=np.arange(n, dtype=np.int64), W=W,
                        positions=pos, annotations=ann,
                        name="synthetic-terminal", terminal=T)
    without = Connectome(root_ids=with_t.root_ids, W=W, positions=pos,
                         annotations=ann, name="synthetic-noterm")
    return with_t, without


@needs_flybench
def test_terminal_toy_equivalence_vs_their_simulator(tmp_path, monkeypatch):
    from flybench.models.terminal_lif import TerminalLIFSimulator
    from flybench.sim import LIFParams, LIFSimulator, Stimulus
    monkeypatch.setattr(ad, "MECH_SIDECAR_DIR", tmp_path)
    monkeypatch.delenv(ad.TERMINAL_TABLE_ENV, raising=False)
    c_term, c_ref = _synthetic_terminal_connectomes()
    DUR = 1500.0

    def run(cls, conn, drive_c):
        stims = [Stimulus(neurons=np.array([0]), rate_hz=150.0,
                          t_start_ms=100.0, t_end_ms=DUR)]
        if drive_c:
            stims.append(Stimulus(neurons=np.array([3]), rate_hz=150.0,
                                  t_start_ms=100.0, t_end_ms=DUR))
        res = cls(conn, LIFParams(seed=0)).run(DUR, stims)
        return {i: res.rate_hz([i], 100.0, DUR) for i in range(5)}

    theirs = {q: run(TerminalLIFSimulator, c_term, q) for q in (False, True)}
    ours = {q: run(ad.FlyGITerminalAdapter, c_term, q) for q in (False, True)}
    their_ref = {q: run(LIFSimulator, c_ref, q) for q in (False, True)}
    our_ref = {q: run(ad.FlyGIAdapter, c_ref, q) for q in (False, True)}

    # Signature 1 -- somatic shielding: a terminal input must NOT fire (or
    # silence) the soma. Driving C leaves B nearly unchanged under the
    # terminal model in BOTH engines, while the point-neuron reference
    # collapses B in both. (Measured at build time: terminal B 37.1->35.7
    # theirs / 33.6->30.0 ours; reference B 37.1->9.3 / 33.6->5.7.)
    for eng in (theirs, ours):
        assert eng[True][1] >= 0.8 * eng[False][1], f"soma not shielded: {eng}"
    for eng in (their_ref, our_ref):
        assert eng[True][1] <= 0.5 * eng[False][1], "reference control lost"
    # Signature 2 -- release modulation: C's terminal drive scales B's
    # release down, so D drops strongly while B stays up, in BOTH engines
    # (measured: D 34.3->9.3 theirs, 26.4->5.0 ours).
    for eng in (theirs, ours):
        assert eng[True][2] <= 0.5 * eng[False][2], f"release not modulated: {eng}"
        assert eng[False][2] > 5.0                     # D alive without C
    # Cross-engine rate agreement within the DECLARED differences (our dt
    # 0.5 vs their 0.1 ms, our one-step delay vs their 1.8 ms line, and
    # independent Poisson event sampling): 35% relative on the driven-path
    # rates (measured worst case at build time: 26% on D without C).
    for q in (False, True):
        for i in (0, 1):
            assert ours[q][i] == pytest.approx(theirs[q][i], rel=0.35)
    assert ours[False][2] == pytest.approx(theirs[False][2], rel=0.35)
    # the engine actually received a terminal matrix (not the off path)
    a = ad.FlyGITerminalAdapter(c_term, LIFParams(seed=0))
    assert a.net._terminal_mv is not None and a.net._terminal_mv.nnz == 1


@needs_flybench
def test_both_mechanism_adapters_pass_verify_adapter(tmp_path, monkeypatch):
    # shared BLOCKED floor (v): `flybench verify-adapter` must be clean on
    # both new classes; asserted here through the same library call.
    from flybench.adapter import verify_adapter
    from flybench.connectome import load_connectome
    monkeypatch.setattr(ad, "MECH_SIDECAR_DIR", tmp_path)
    monkeypatch.delenv(ad.TERMINAL_TABLE_ENV, raising=False)
    c = load_connectome("toy")
    for cls in (ad.FlyGISFAAdapter, ad.FlyGITerminalAdapter):
        rep = verify_adapter(cls, c)
        assert rep.ok, (cls.__name__,
                        [(d.name, d.detail) for d in rep.defects])


# ===========================================================================
# terminal loader gates (table sum, coverage, survival, conventions)
# ===========================================================================

@needs_flybench
def test_shipped_malecns_terminal_table_sums_to_frozen_magnitude():
    table_path = FLYBENCH_CLONE / "data/terminal/malecns_terminal.csv.gz"
    if not table_path.exists():
        import flybench
        table_path = (Path(flybench.__file__).parents[1]
                      / "data/terminal/malecns_terminal.csv.gz")
    if not table_path.exists():
        pytest.skip("shipped terminal table not present in this checkout")
    df = ad._load_terminal_table(str(table_path))
    assert float(df["terminal"].sum()) == ad.TERMINAL_TABLE_SUM == 3_782_429


@needs_flybench
def test_terminal_loader_gates_on_synthetic_tables(tmp_path, monkeypatch):
    import pandas as pd
    monkeypatch.setattr(ad, "MECH_SIDECAR_DIR", tmp_path)
    c_term, c_ref = _synthetic_terminal_connectomes()

    def write_table(name, rows):
        p = tmp_path / name
        pd.DataFrame(rows, columns=["pre", "post", "terminal"]).to_csv(
            p, index=False)
        return str(p)

    # wrong magnitude -> the frozen sum gate raises
    bad_sum = write_table("bad_sum.csv", [(0, 1, 40.0), (3, 1, 1.0)])
    monkeypatch.setenv(ad.TERMINAL_TABLE_ENV, bad_sum)
    with pytest.raises(ad.TerminalGateError, match="sums to"):
        ad.resolve_terminal(c_ref)
    # right magnitude, alien body IDs -> the coverage gate raises
    alien = write_table("alien.csv", [(900001, 900002, ad.TERMINAL_TABLE_SUM)])
    monkeypatch.setenv(ad.TERMINAL_TABLE_ENV, alien)
    with pytest.raises(ad.TerminalGateError, match="coverage"):
        ad.resolve_terminal(c_ref)
    # right magnitude, aligned IDs -> attaches; survival = clipped/published
    # (the 3->1 edge clips 3,782,429 - 40 published synapses to |W| = 40)
    good = write_table("good.csv", [(3, 1, float(ad.TERMINAL_TABLE_SUM))])
    monkeypatch.setenv(ad.TERMINAL_TABLE_ENV, good)
    T, gates = ad.resolve_terminal(c_ref)
    assert T is not None and T.nnz == 1
    assert T[3, 1] == -40.0                      # clipped to |W|, signed by W
    assert gates["source"] == "table"
    assert gates["table_sum"] == ad.TERMINAL_TABLE_SUM
    assert gates["coverage"] == 1.0
    assert gates["survival"] == pytest.approx(40.0 / ad.TERMINAL_TABLE_SUM)
    # the table takes precedence over connectome.terminal when both exist
    T2, gates2 = ad.resolve_terminal(c_term)
    assert gates2["source"] == "table"


@needs_flybench
def test_terminal_control_convention_runs_terminal_none(tmp_path, monkeypatch):
    # rewired/shuffled controls run terminal=None per FlyBench's own
    # convention (registration, declared) -- even with the table env set
    import pandas as pd
    from flybench.controls import rewire_degree_preserving
    monkeypatch.setattr(ad, "MECH_SIDECAR_DIR", tmp_path)
    c_term, _ = _synthetic_terminal_connectomes()
    good = tmp_path / "good.csv"
    pd.DataFrame([(3, 1, float(ad.TERMINAL_TABLE_SUM))],
                 columns=["pre", "post", "terminal"]).to_csv(good, index=False)
    monkeypatch.setenv(ad.TERMINAL_TABLE_ENV, str(good))
    ctl = rewire_degree_preserving(c_term, seed=0)
    T, gates = ad.resolve_terminal(ctl)
    assert T is None and gates["attached"] is False
    assert gates["source"].startswith("control:")


@needs_flybench
def test_nonfinite_membrane_is_recorded_stickily(tmp_path, monkeypatch):
    from flybench.sim import LIFParams
    monkeypatch.setattr(ad, "MECH_SIDECAR_DIR", tmp_path)
    monkeypatch.delenv(ad.TERMINAL_TABLE_ENV, raising=False)
    c_term, _ = _synthetic_terminal_connectomes()
    a = ad.FlyGITerminalAdapter(c_term, LIFParams(seed=0))
    a.net.v[0] = np.nan
    ad._mech_note_nonfinite(a)
    path = a._sidecar_path
    assert json.loads(path.read_text())["nonfinite_v"] is True
    # a later clean construction of the SAME wiring must not erase it
    ad.FlyGITerminalAdapter(c_term, LIFParams(seed=0))
    assert json.loads(path.read_text())["nonfinite_v"] is True


# ===========================================================================
# GATE 5 -- verdict-script logic on synthetic JSONs (every bar and floor)
# ===========================================================================

N = vd.UNIFORM_BASELINE_N_NEURONS


def _chk(desc, op, graded):
    return {"description": desc, "op": op, "graded": graded}


def _report(hard_graded=0.60, graded=0.7113, specificity=0.282,
            core_score=1.0, act=0.50, sup=0.90, n_neurons=N):
    return {"hard_graded": hard_graded, "graded": graded,
            "specificity": specificity, "core_score": core_score,
            "n_neurons": n_neurons,
            "tasks": [{"task": "t", "checks": [
                _chk("rate[x] > 5.0 Hz", ">", act),
                _chk("rate[y] / rate[z] < 0.5", "<", sup)]}]}


def _sidecar(dirpath, mechanism, n_neurons=N, **kw):
    rec = {"mechanism": mechanism, "n_neurons": n_neurons, "control": None,
           "weight_jitter": 0.0, "silenced": 0, "nonfinite_v": False}
    if mechanism == "sfa":
        rec.update(b_mv=2.0, tau_a_ms=200.0, sfa_b=0.1)
    else:
        rec.update(attached=True, source="table",
                   table_sum=vd.TERMINAL_TABLE_SUM,
                   coverage=0.9998, survival=0.98)
    rec.update(kw)
    dirpath.mkdir(parents=True, exist_ok=True)
    name = f"{mechanism}-{abs(hash(frozenset(kw.items()))) % 10**8:08d}.json"
    (dirpath / name).write_text(json.dumps(rec))
    return rec


def test_frozen_verdict_constants_match_registration():
    assert vd.BAR_HARD_DELTA == 0.02
    assert vd.BAR_OVERALL_GRADED == 0.701          # = 0.7113 - 0.01
    assert vd.BAR_SPECIFICITY == 0.252             # = 0.282 - 0.03
    assert vd.BAR_ACTIVATION_GUARD == 0.01
    assert vd.BAR_CORE == 1.0
    assert vd.UNIFORM_BASELINE_N_NEURONS == 176_422
    assert vd.TERMINAL_TABLE_SUM == 3_782_429
    assert vd.TERMINAL_COVERAGE_FLOOR == 0.95
    assert vd.TERMINAL_SURVIVAL_FLOOR == 0.90


def test_verdict_sfa_pass_and_each_kill_bar(tmp_path):
    _sidecar(tmp_path, "sfa")
    uni = _report()
    good = dict(hard_graded=0.63, graded=0.72, specificity=0.30, act=0.55)
    out = vd.verdict("sfa", uni, _report(**good), tmp_path)
    assert out["verdict"] == "PASS", out
    # bar 1: hard tier must improve by >= +0.02
    out = vd.verdict("sfa", uni, _report(**{**good, "hard_graded": 0.615}), tmp_path)
    assert out["verdict"] == "KILL" and not out["bars"]["hard_improves"]
    # bar 2: overall graded floor
    out = vd.verdict("sfa", uni, _report(**{**good, "graded": 0.70}), tmp_path)
    assert out["verdict"] == "KILL" and not out["bars"]["overall_holds"]
    # bar 3: specificity floor
    out = vd.verdict("sfa", uni, _report(**{**good, "specificity": 0.25}), tmp_path)
    assert out["verdict"] == "KILL" and not out["bars"]["specificity_holds"]
    # bar 4: SFA must not sell activation (uniform 0.50 - 0.01 = 0.49 floor)
    out = vd.verdict("sfa", uni, _report(**{**good, "act": 0.47}), tmp_path)
    assert out["verdict"] == "KILL" and not out["bars"]["activation_holds"]
    # exactly on the activation guard is a pass of that bar
    out = vd.verdict("sfa", uni, _report(**{**good, "act": 0.49}), tmp_path)
    assert out["bars"]["activation_holds"]


def test_verdict_terminal_pass_and_each_kill_bar(tmp_path):
    _sidecar(tmp_path, "terminal")
    uni = _report()
    good = dict(hard_graded=0.63, graded=0.72, specificity=0.30)
    out = vd.verdict("terminal", uni, _report(**good), tmp_path)
    assert out["verdict"] == "PASS", out
    assert "activation_holds" not in out["bars"]       # SFA-only guard
    out = vd.verdict("terminal", uni, _report(**{**good, "hard_graded": 0.61}), tmp_path)
    assert out["verdict"] == "KILL" and not out["bars"]["hard_improves"]
    # bar 2: core regression guard (their headline headroom does not exist
    # on our engine; core must STAY 1.000)
    out = vd.verdict("terminal", uni, _report(**{**good, "core_score": 0.97}), tmp_path)
    assert out["verdict"] == "KILL" and not out["bars"]["core_holds"]
    out = vd.verdict("terminal", uni, _report(**{**good, "graded": 0.69}), tmp_path)
    assert out["verdict"] == "KILL" and not out["bars"]["overall_holds"]
    out = vd.verdict("terminal", uni, _report(**{**good, "specificity": 0.20}), tmp_path)
    assert out["verdict"] == "KILL" and not out["bars"]["specificity_holds"]


def test_verdict_blocked_floors(tmp_path):
    good = dict(hard_graded=0.63, graded=0.72, specificity=0.30)
    # floor (iii): baseline is not the registered 176,422-neuron build
    _sidecar(tmp_path, "sfa")
    out = vd.verdict("sfa", _report(n_neurons=123), _report(**good), tmp_path)
    assert out["verdict"] == "BLOCKED" and any("176422" in r or "176,422" in r
                                               or "floor iii" in r
                                               for r in out["blocked_reasons"])
    # floor (iii): composition changed between baseline and mechanism run
    out = vd.verdict("sfa", _report(), _report(**good, n_neurons=N - 1), tmp_path)
    assert out["verdict"] == "BLOCKED"
    # instrument guard: no sidecar at all for this build
    empty = tmp_path / "empty"
    empty.mkdir()
    out = vd.verdict("sfa", _report(), _report(**good), empty)
    assert out["verdict"] == "BLOCKED" and any("sidecar" in r
                                               for r in out["blocked_reasons"])
    # floor (v): non-finite membrane recorded in any arm
    d = tmp_path / "nf"
    _sidecar(d, "sfa")
    _sidecar(d, "sfa", nonfinite_v=True, control="rewired")
    out = vd.verdict("sfa", _report(), _report(**good), d)
    assert out["verdict"] == "BLOCKED" and any("non-finite" in r
                                               for r in out["blocked_reasons"])
    # instrument guard: mechanism never on (off-switch left at 0)
    d = tmp_path / "off"
    _sidecar(d, "sfa", sfa_b=0.0)
    out = vd.verdict("sfa", _report(), _report(**good), d)
    assert out["verdict"] == "BLOCKED" and any("never on" in r
                                               for r in out["blocked_reasons"])
    # instrument guard (precedent): empty shared activation set, SFA only
    d = tmp_path / "noact"
    _sidecar(d, "sfa")
    uni = _report()
    mech = _report(**good)
    for rep in (uni, mech):
        rep["tasks"][0]["checks"] = [_chk("rate[y] / rate[z] < 0.5", "<", 0.9)]
    out = vd.verdict("sfa", uni, mech, d)
    assert out["verdict"] == "BLOCKED" and any("activation" in r
                                               for r in out["blocked_reasons"])
    # instrument guard: hard tier / specificity missing -> bars undefined
    d = tmp_path / "miss"
    _sidecar(d, "sfa")
    out = vd.verdict("sfa", _report(hard_graded=None), _report(**good), d)
    assert out["verdict"] == "BLOCKED"
    out = vd.verdict("sfa", _report(), _report(**{**good, "specificity": None}), d)
    assert out["verdict"] == "BLOCKED"


def test_verdict_blocked_terminal_floors(tmp_path):
    good = dict(hard_graded=0.63, graded=0.72, specificity=0.30)
    # floor (iv): coverage below 0.95 on a base arm
    d = tmp_path / "cov"
    _sidecar(d, "terminal", coverage=0.90)
    out = vd.verdict("terminal", _report(), _report(**good), d)
    assert out["verdict"] == "BLOCKED" and any("coverage" in r
                                               for r in out["blocked_reasons"])
    # floor (iv): synapse survival below 0.90 on a base arm
    d = tmp_path / "surv"
    _sidecar(d, "terminal", survival=0.85)
    out = vd.verdict("terminal", _report(), _report(**good), d)
    assert out["verdict"] == "BLOCKED" and any("survival" in r
                                               for r in out["blocked_reasons"])
    # loader gate echoed: wrong table magnitude
    d = tmp_path / "sum"
    _sidecar(d, "terminal", table_sum=3_000_000)
    out = vd.verdict("terminal", _report(), _report(**good), d)
    assert out["verdict"] == "BLOCKED" and any("table sum" in r
                                               for r in out["blocked_reasons"])
    # instrument guard: terminal never attached on a base arm
    d = tmp_path / "noatt"
    _sidecar(d, "terminal", attached=False, source="none")
    out = vd.verdict("terminal", _report(), _report(**good), d)
    assert out["verdict"] == "BLOCKED" and any("never attached" in r
                                               for r in out["blocked_reasons"])
    # instrument guard: attached from a non-registered source
    d = tmp_path / "src"
    _sidecar(d, "terminal", source="connectome.terminal")
    out = vd.verdict("terminal", _report(), _report(**good), d)
    assert out["verdict"] == "BLOCKED" and any("not the registered" in r
                                               for r in out["blocked_reasons"])
    # a jittered/silenced arm with low survival must NOT block (floor iv is
    # evaluated on base arms only; declared in resolve_terminal)
    d = tmp_path / "jit"
    _sidecar(d, "terminal")
    _sidecar(d, "terminal", survival=0.70, weight_jitter=0.5)
    _sidecar(d, "terminal", survival=0.70, silenced=12)
    out = vd.verdict("terminal", _report(), _report(**good), d)
    assert out["verdict"] == "PASS", out
    # control arms (terminal=None) never block the attach guard
    d = tmp_path / "ctl"
    _sidecar(d, "terminal")
    _sidecar(d, "terminal", attached=False, source="control:rewired",
             control="rewired")
    out = vd.verdict("terminal", _report(), _report(**good), d)
    assert out["verdict"] == "PASS", out


def test_verdict_keys_checks_by_identity_not_annotation(tmp_path):
    # the 2026-10-03 lesson, inherited from the calibrated verdict: the
    # volatile "  [N/3 seeds, sd S]" suffix must not drop moved checks
    uni = _report()
    mech = _report(hard_graded=0.63, graded=0.72, specificity=0.30, act=0.55)
    uni["tasks"][0]["checks"][0]["description"] = \
        "rate[x] > 5.0 Hz  [0/3 seeds, sd 0]"
    mech["tasks"][0]["checks"][0]["description"] = \
        "rate[x] > 5.0 Hz  [3/3 seeds, sd 0.21]"
    act, sup = vd.split_scores(uni, mech)
    assert len(act) == 1 and act[0][1:] == (0.50, 0.55)


def test_verdict_main_exit_codes(tmp_path, monkeypatch):
    # exit 0 PASS / 1 KILL / 3 BLOCKED, incl. floor (iii) absent baseline
    side = tmp_path / "side"
    _sidecar(side, "sfa")
    uni_p = tmp_path / "uniform.json"
    uni_p.write_text(json.dumps(_report()))
    mech_p = tmp_path / "mech.json"

    def run_main(mech_report_path):
        monkeypatch.setattr(sys, "argv", [
            "flybench_mechanisms_verdict.py", "--mechanism", "sfa",
            str(uni_p), str(mech_report_path), "--sidecar-dir", str(side)])
        return vd.main()

    mech_p.write_text(json.dumps(_report(
        hard_graded=0.63, graded=0.72, specificity=0.30, act=0.55)))
    assert run_main(mech_p) == 0
    mech_p.write_text(json.dumps(_report(
        hard_graded=0.60, graded=0.72, specificity=0.30, act=0.55)))
    assert run_main(mech_p) == 1
    assert run_main(tmp_path / "missing.json") == 3
