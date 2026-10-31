"""Tests for scripts/arenas/cx_biswas_killtest.py (H-CX-BISWAS-FITTED).

The measurement is data-gated and local; testable in-cloud: the frozen
design constants, their analytic branch identities (Appendix A), the
coarse-graining mechanics (sum-over-pre / average-over-post, the
Delta7 argmax assignment with the AC-B5 tie rule, the AC-B1 label
convention), the gamma fits in BOTH directions (the synthetic-recovery
gate and the uniform-counts can-fail control), the mirror algebra at a
known solution, the G1 rate-model bars incl. decay and runaway
failure modes, and the verdict assembly."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / f"scripts/arenas/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


bk = _load("cx_biswas_killtest")


# --- frozen design -----------------------------------------------------------

def test_frozen_constants():
    assert bk.A_DELTA_CONFIGS == (8, 6, 4)
    assert bk.PUBLISHED_RA == {8: 0.548, 6: 0.437, 4: 0.391}
    assert bk.RA_CONSISTENCY_BAND == 0.1
    # G1 bars verbatim from H-CX-CLASS3-COMPASS
    assert bk.RETENTION_MIN == 0.05
    assert bk.CIRCVAR_MAX == 0.6
    assert bk.ERR_MAX_DEG == 45.0
    assert bk.G1_MIN_PASS == 6
    assert bk.REWIRE_SEED_BASE == 4242
    assert bk.REWIRE_SEEDS == (0, 1, 2)
    # their published grid ranges and defaults
    assert bk.GRID_GAMMA_EE == (0.0, 0.05, 100)
    assert bk.GRID_GAMMA_EIE == (-0.001, 0.0, 100)
    assert bk.GRID_GAMMA_II == (-0.05, 0.0, 100)
    assert bk.GAMMA_II_DEFAULT == 0.0
    # AC-B4/AC-B5
    assert bk.Z_INACTIVE == {8: (), 6: (3, 4), 4: (2, 3, 4, 5)}
    assert bk.CANONICAL_ACTIVE == (2, 3, 4, 5)
    assert bk.TIE_MARGIN == 0.98
    assert bk.TIE_BLOCK_FRACTION == 0.25
    assert bk.EXPECTED_COUNTS["EPG"] == 46
    assert bk.EXPECTED_COUNTS["Delta7"] == 42
    # build-time operationalizations B-R1..9
    assert bk.FIT_RTOL_SYM == 1e-6
    assert bk.FIT_ATOL_MIRROR == 1e-8
    assert bk.TOL_DRIVE == 1e-9
    assert bk.RA_SCAN_XATOL == 1e-10
    assert bk.RA_SCAN_POINTS == 2001
    assert bk.SIGMA_SEED == 1.0
    assert bk.T_DARK == 100.0
    assert (bk.ODE_RTOL, bk.ODE_ATOL) == (1e-8, 1e-10)
    assert bk.RUNAWAY_MAX == 1e6
    assert bk.Z_FP_ITERS == 100
    assert bk.MIRROR_SEED_CAP == 10


# --- their analytic branch (Appendix A identities) ---------------------------

@pytest.mark.parametrize("ra", [0.0, 0.3, 0.548, 0.95])
def test_w_profile_branch_identities(ra):
    w1, w2, w3 = bk.w_profile(ra)
    assert w1 == pytest.approx((1 + ra) / 2)          # A.23
    assert w2 == pytest.approx(1 - 2 * w1 ** 2)       # A.17
    assert w3 == pytest.approx(w1 * (4 * w1 ** 2 - 3))  # A.18
    # A.10 and A.13 hold identically on the branch
    assert (1 - w3) * (1 - w1) == pytest.approx((w1 + w2) ** 2)
    assert (1 + w3) * (1 + w1) == pytest.approx((w1 - w2) ** 2)


def test_bump_profile_and_tiling():
    # A.24: r_s - r_a = 2 is built into the profile
    y = bk.bump_profile(0.0, 0.5)
    assert y == pytest.approx([1.0, 2.5, 2.5, 1.0])
    # A.25: <theta> = mu pi/8 across the mu range
    for mu in (-1.0, -0.25, 0.0, 0.6, 1.0):
        assert bk.mean_angle_a6(bk.bump_profile(mu, 0.42)) == \
            pytest.approx(mu * np.pi / 8)


def test_mirror_equations_reduce_to_symmetric():
    # their B.49 remark: primes equal -> the symmetric model; on the
    # branch the first two equations then vanish identically
    for ra in (0.2, 0.5, 0.8):
        w1, w2, w3 = bk.w_profile(ra)
        params = np.array([w1, w2, w3, w1, w1, w2])
        f = bk.mirror_equations(params)
        assert abs(f[0]) < 1e-12 and abs(f[1]) < 1e-12


# --- coarse-graining mechanics ----------------------------------------------

def test_epg_unit_from_instance_convention():
    # AC-B1: (digit - 1) mod 8, L/R merged, digit 9 wraps onto digit 1
    assert bk.epg_unit_from_instance("EPG(PB08)_L3_C1") == 2
    assert bk.epg_unit_from_instance("EPG(PB08)_R3_C2") == 2
    assert bk.epg_unit_from_instance("EPG_L1") == 0
    assert bk.epg_unit_from_instance("EPG_R9") == 0
    assert bk.epg_unit_from_instance("EPG_unlabelled") is None


def test_unit_count_matrix_sums_pre_averages_post():
    # unit 0 holds TWO post neurons with different in-sums from the
    # two pre neurons of unit 1: the entry is the mean of the sums
    n = 9 + 9
    W = np.zeros((n, n))
    post_idx = np.arange(9)                   # units [0,0,1..7]
    post_units = np.array([0, 0, 1, 2, 3, 4, 5, 6, 7])
    pre_idx = np.arange(9, 18)                # units [1,1,0,2..7]
    pre_units = np.array([1, 1, 0, 2, 3, 4, 5, 6, 7])
    W[0, 9], W[0, 10] = 3.0, 5.0     # post neuron 0 receives 8 total
    W[1, 9] = 4.0                    # post neuron 1 receives 4 total
    C = bk.unit_count_matrix(W, pre_idx, pre_units, post_idx,
                             post_units)
    assert C[0, 1] == pytest.approx((8.0 + 4.0) / 2)  # mean of sums
    assert C[0, 0] == 0.0 and C[3, 1] == 0.0


def test_unit_count_matrix_empty_post_unit_raises():
    W = np.zeros((2, 2))
    with pytest.raises(ValueError):
        bk.unit_count_matrix(W, np.array([0]), np.array([0]),
                             np.array([1]), np.array([3]))


def test_distance_average_and_circulant():
    D = bk.circular_distance_matrix()
    assert D.max() == 4 and D[0, 4] == 4 and D[0, 7] == 1
    c = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    C = bk.circulant_from_profile(c)
    assert bk.distance_average(C) == pytest.approx(c)
    assert C[2, 2] == 5.0 and C[0, 4] == 1.0 and C[1, 7] == 3.0


def test_mirror_average_axis():
    rng = np.random.default_rng(0)
    C = rng.random((8, 8))
    M = bk.mirror_average(C)
    p = bk.mirror_permutation()
    assert np.allclose(M, M[np.ix_(p, p)])
    # canonical axis between units 3 and 4: 3 <-> 4, 0 <-> 7
    assert p[3] == 4 and p[0] == 7


def test_assign_delta7_units_and_tie_rule():
    # 2 EPGs per wedge; Delta7 #0 clearly prefers wedge 2, #1 is a
    # 0.99 near-tie (counts as tie), #2 outputs nothing (tie)
    epg_idx = np.arange(16)
    epg_units = np.repeat(np.arange(8), 2)
    d7_idx = np.array([16, 17, 18])
    W = np.zeros((19, 19))
    W[4, 16] = W[5, 16] = 10.0            # wedge 2
    W[0, 17], W[2, 17] = 10.0, 9.9        # wedge 0 vs 0.99 x on wedge 1
    rec = bk.assign_delta7_units(W, epg_idx, epg_units, d7_idx)
    assert rec["units"][0] == 2
    assert rec["units"][1] == 0           # argmax; tie reported
    assert rec["tie_fraction"] == pytest.approx(2 / 3)


def test_assign_delta7_tie_breaks_to_lowest_index():
    epg_idx = np.arange(16)
    epg_units = np.repeat(np.arange(8), 2)
    d7_idx = np.array([16])
    W = np.zeros((17, 17))
    W[6, 16] = 10.0                       # wedge 3
    W[10, 16] = 10.0                      # wedge 5, exact tie
    rec = bk.assign_delta7_units(W, epg_idx, epg_units, d7_idx)
    assert rec["units"][0] == 3
    assert rec["tie_fraction"] == 1.0


# --- the amended in-cloud gate, both directions ------------------------------

def test_gate_synthetic_recovery_to_1e6():
    synth = bk.synthetic_blocks()
    result = bk.run_configuration(synth, 8)
    assert result["valid_fit"]
    chosen = result["fit"]["chosen"]
    assert chosen["r_a"] == pytest.approx(bk.SYNTH_RA, abs=1e-6)
    assert chosen["gamma_ee"] == pytest.approx(bk.SYNTH_GAMMA_EE,
                                               rel=1e-6)
    assert chosen["gamma_eie"] == pytest.approx(bk.SYNTH_GAMMA_EIE,
                                                rel=1e-6)
    assert all(chosen["checks"].values())


def test_gate_synthetic_g1_eight_of_eight():
    result = bk.run_configuration(bk.synthetic_blocks(), 8)
    assert result["g1"]["n_pass"] == 8
    for row in result["g1"]["rows"]:
        assert row["retention"] == pytest.approx(1.0, abs=1e-3)
        assert row["err_deg"] <= 1.0
    # the 8 seeds sit 45 deg apart (the mu=0 rotations, A.25)
    pvas = sorted(r["seed_pva_deg"] for r in result["g1"]["rows"])
    assert np.allclose(np.diff(pvas), 45.0)


def test_gate_can_fail_on_uniform_counts():
    uniform = {k: np.full((8, 8), 10.0)
               for k in ("C_EE", "C_EI", "C_IE", "C_II")}
    result = bk.run_configuration(uniform, 8)
    assert not result["valid_fit"]
    assert not result["pass"]


def test_validate_gate_passes_in_cloud():
    gate = bk.validate_gate()
    assert gate["pass"]
    assert gate["recovery"]["pass"]
    assert gate["g1_synthetic"]["pass"]
    assert gate["can_fail"]["pass"]
    assert gate["identities"]["pass"]


def test_fit_is_invariant_under_count_rescaling():
    # AC-B3: C -> alpha C must give the same r_a and gamma / alpha
    synth = bk.synthetic_blocks()
    scaled = {k: 3.7 * v for k, v in synth.items()
              if k.startswith("C_")}
    base = bk.run_configuration(synth, 8)["fit"]["chosen"]
    other = bk.run_configuration(scaled, 8)["fit"]["chosen"]
    assert other["r_a"] == pytest.approx(base["r_a"], abs=1e-9)
    assert other["gamma_ee"] == pytest.approx(base["gamma_ee"] / 3.7,
                                              rel=1e-9)
    # C^EIE = C^EI C^IE is QUADRATIC in the count scale
    assert other["gamma_eie"] == pytest.approx(
        base["gamma_eie"] / 3.7 ** 2, rel=1e-9)


# --- mirror machinery --------------------------------------------------------

def test_mirror_algebra_reproduces_known_solution():
    # at gamma*, with every z active, the barred matrix carries the
    # symmetric branch values and the three equalities hold
    synth = bk.synthetic_blocks()
    C_EIE = bk.effective_feedback(synth["C_EI"], synth["C_II"],
                                  synth["C_IE"], 0.0, np.arange(8))
    Wb = bk.mirror_barred(synth["C_EE"], C_EIE, synth["gamma_ee"],
                          synth["gamma_eie"])
    w1p, w2p, w3, w1pp, w1, w2pp = bk.mirror_params(Wb)
    e1, e2, e3 = bk.w_profile(synth["r_a"])
    assert w1p == pytest.approx(e1, abs=1e-9)
    assert w1pp == pytest.approx(e1, abs=1e-9)
    assert w1 == pytest.approx(e1, abs=1e-9)
    assert w2p == pytest.approx(e2, abs=1e-9)
    assert w3 == pytest.approx(e3, abs=1e-9)
    f = bk.mirror_equations(bk.mirror_params(Wb))
    assert np.abs(f).max() < 1e-9


def test_mirror_barred_rejects_nonpositive_denominator():
    C = np.eye(8) * 200.0
    assert bk.mirror_barred(C, np.zeros((8, 8)), 0.01, -1e-4) is None


def test_fit_mirror_finds_the_synthetic_a_delta_6_root():
    # pinned UNCONDITIONALLY (review finding: a conditional here would
    # hide a regression of the machinery carrying two configurations)
    synth = bk.synthetic_blocks()
    rec = bk.fit_mirror(synth["C_EE"], synth["C_EI"], synth["C_IE"],
                        synth["C_II"], 6)
    assert rec["kind"] == "mirror" and rec["a_delta"] == 6
    assert rec["valid"] is True
    assert rec["max_abs_residual"] <= bk.FIT_ATOL_MIRROR
    assert rec["r_a"] == pytest.approx(0.21607, abs=1e-4)
    assert rec["n_seeds"] >= 1 and rec["n_valid"] == 1


def test_fit_mirror_a_delta_4_filters_invalid_roots():
    # this synthetic has no A_Delta=4 realization: every refined
    # cluster root must be filtered, never crash, and the record must
    # carry the candidate list (their 'filter out invalid solutions')
    synth = bk.synthetic_blocks()
    rec = bk.fit_mirror(synth["C_EE"], synth["C_EI"], synth["C_IE"],
                        synth["C_II"], 4)
    assert rec["valid"] is False and rec["n_valid"] == 0
    assert rec["n_seeds"] >= 1
    assert all("checks" in c for c in rec["candidates"])


def test_recipe_reads_only_the_symmetrized_system():
    # the 2026-10-31 adversarial-review blocker: the fit must certify
    # the circulant system G1 simulates, for ALL configurations --
    # circulant-symmetrizing the inputs beforehand changes NOTHING
    rng = np.random.default_rng(3)
    synth = bk.synthetic_blocks()
    noisy = {k: v * (1 + 0.2 * (rng.random(v.shape) - 0.5))
             for k, v in synth.items() if k.startswith("C_")}
    pre = {k: bk.circulant_from_profile(bk.distance_average(v))
           for k, v in noisy.items()}
    for a_delta in bk.A_DELTA_CONFIGS:
        r1 = bk.run_configuration(noisy, a_delta)
        r2 = bk.run_configuration(pre, a_delta)
        assert r1["valid_fit"] == r2["valid_fit"], a_delta
        if r1["valid_fit"]:
            assert r1["r_a"] == pytest.approx(r2["r_a"], abs=1e-9)
            assert r1["pass"] == r2["pass"]


def test_recipe_is_invariant_under_unit_label_rotation():
    # review finding CODE-2's regression: with circulant inputs the
    # whole recipe is exactly invariant under a global rotation of
    # the EPG unit labels, mirror configurations included
    rng = np.random.default_rng(11)
    n_epg, n_d7 = 16, 16
    epg_idx = np.arange(n_epg)
    d7_idx = np.arange(n_epg, n_epg + n_d7)
    units = np.repeat(np.arange(8), 2)
    W = rng.random((32, 32)) * 3.0
    r0 = bk.run_graph(W, epg_idx, units, d7_idx)
    r1 = bk.run_graph(W, epg_idx, (units + 3) % 8, d7_idx)
    for a_delta in bk.A_DELTA_CONFIGS:
        a, b = r0["configs"][a_delta], r1["configs"][a_delta]
        assert a["valid_fit"] == b["valid_fit"]
        assert a["pass"] == b["pass"]
        if a["valid_fit"]:
            assert a["r_a"] == pytest.approx(b["r_a"], abs=1e-9)


def test_drive_checks_tolerate_the_identical_zero():
    # their A.31 first inequality is identically zero on the branch:
    # the transition drive must count as nonpositive, not as a fail
    ra = 0.5
    w = np.append(bk.w_profile(ra), -0.2)
    Wb = bk.circulant_from_profile(np.concatenate([[0.0], w]))
    u_z = np.full((8, 4), 0.1)           # all z driven positive
    checks = bk.drive_checks(Wb, u_z, ra, ())
    assert checks["inactive_epg_drives_nonpositive"]
    assert checks["active_z_drives_nonnegative"]
    checks2 = bk.drive_checks(Wb, u_z, ra, (0,))
    assert not checks2["inactive_z_drives_nonpositive"]


# --- G1 failure modes --------------------------------------------------------

def _synthetic_sim_matrices(scale):
    synth = bk.synthetic_blocks()
    g_ee, g_eie = synth["gamma_ee"] * scale, synth["gamma_eie"] * scale
    g_ie = float(np.sqrt(abs(g_eie)))
    return (g_ee * synth["C_EE"], -g_ie * synth["C_EI"],
            g_ie * synth["C_IE"], np.zeros((8, 8)))


def test_g1_detects_decay():
    # halving the gains breaks the eigenvalue-1 degeneracy downward:
    # the bump decays and retention falls under the bar
    W_EE, W_EI, W_IE, W_II = _synthetic_sim_matrices(0.5)
    g1 = bk.simulate_g1(W_EE, W_EI, W_IE, W_II, bk.SYNTH_RA)
    assert g1["n_pass"] == 0
    for row in g1["rows"]:
        assert row["retention"] < bk.RETENTION_MIN


def test_g1_detects_runaway():
    # doubling the excitatory gain alone blows the bump up; runaway
    # is not an attractor and must fail, never crash
    synth = bk.synthetic_blocks()
    g_ie = float(np.sqrt(abs(synth["gamma_eie"])))
    g1 = bk.simulate_g1(3.0 * synth["gamma_ee"] * synth["C_EE"],
                        -g_ie * synth["C_EI"],
                        g_ie * synth["C_IE"], np.zeros((8, 8)),
                        bk.SYNTH_RA)
    assert g1["n_pass"] == 0
    assert not g1["pass"]


def test_pva_and_circvar_degenerate_inputs():
    angle, circvar = bk.pva_deg(np.zeros(8))
    assert np.isnan(angle) and circvar == 1.0
    y = np.zeros(8)
    y[2] = 3.0
    angle, circvar = bk.pva_deg(y)
    assert angle == pytest.approx(90.0)
    assert circvar == pytest.approx(0.0)
    assert bk.circ_err_deg(350.0, 10.0) == pytest.approx(20.0)


# --- verdict assembly --------------------------------------------------------

def _config(valid, g1_pass):
    return {"valid_fit": valid, "pass": bool(valid and g1_pass),
            "g1": None}


def _graph(valid_by_config, pass_by_config, error=None):
    if error:
        return {"error": error}
    return {"configs": {a: _config(valid_by_config[a],
                                   pass_by_config[a])
                        for a in bk.A_DELTA_CONFIGS},
            "tie_fraction": 0.0}


def test_verdict_pass_requires_all_nulls_failing_everywhere():
    real = _graph({8: True, 6: True, 4: False},
                  {8: True, 6: False, 4: False})
    null_fail = _graph({8: False, 6: False, 4: False},
                       {8: False, 6: False, 4: False})
    assert bk.assemble_verdict(real, [null_fail] * 3) == "PASS"
    # a null passing at the real-passing configuration spoils it
    null_pass = _graph({8: True, 6: False, 4: False},
                       {8: True, 6: False, 4: False})
    assert bk.assemble_verdict(
        real, [null_fail, null_pass, null_fail]) == "KILL"
    # a null passing ELSEWHERE does not
    null_elsewhere = _graph({8: False, 6: True, 4: False},
                            {8: False, 6: True, 4: False})
    assert bk.assemble_verdict(
        real, [null_fail, null_elsewhere, null_fail]) == "PASS"


def test_verdict_kill_and_transfer_limit():
    # valid fit everywhere but G1 fails everywhere -> KILL
    real_kill = _graph({8: True, 6: True, 4: True},
                       {8: False, 6: False, 4: False})
    nulls = [_graph({8: False, 6: False, 4: False},
                    {8: False, 6: False, 4: False})] * 3
    assert bk.assemble_verdict(real_kill, nulls) == "KILL"
    # no valid fit anywhere -> BLOCKED (the recipe-transfer limit)
    real_blocked = _graph({8: False, 6: False, 4: False},
                          {8: False, 6: False, 4: False})
    assert bk.assemble_verdict(real_blocked, nulls) == "BLOCKED"


def test_verdict_blocked_on_errors_and_incomplete_bars():
    real = _graph({8: True, 6: False, 4: False},
                  {8: True, 6: False, 4: False})
    good = _graph({8: False, 6: False, 4: False},
                  {8: False, 6: False, 4: False})
    bad = _graph(None, None, error="RuntimeError('x')")
    assert bk.assemble_verdict(real, [good, good, bad]) == "BLOCKED"
    assert bk.assemble_verdict(real, [good, good]) == "BLOCKED"
    assert bk.assemble_verdict({"error": "boom"},
                               [good, good, good]) == "BLOCKED"


# --- recipe end-to-end on a rewired toy (structure, not outcome) -------------

def test_run_graph_structure_on_toy():
    rng = np.random.default_rng(7)
    n_epg, n_d7 = 16, 8
    epg_idx = np.arange(n_epg)
    epg_units = np.repeat(np.arange(8), 2)
    d7_idx = np.arange(n_epg, n_epg + n_d7)
    n = n_epg + n_d7
    W = rng.random((n, n)) * (rng.random((n, n)) < 0.4)
    record = bk.run_graph(W, epg_idx, epg_units, d7_idx)
    assert set(record["configs"]) == set(bk.A_DELTA_CONFIGS)
    assert 0.0 <= record["tie_fraction"] <= 1.0
    for entry in record["configs"].values():
        assert "valid_fit" in entry and "pass" in entry
        if entry["valid_fit"]:
            assert entry["g1"] is not None


def test_run_graph_empty_delta7_unit_is_fit_fail_never_a_crash():
    # a rewire can starve a Delta7 unit of members: the frozen rule
    # counts that as no-valid-fit everywhere (never an exception)
    epg_idx = np.arange(16)
    epg_units = np.repeat(np.arange(8), 2)
    d7_idx = np.arange(16, 24)
    W = np.zeros((24, 24))
    for j, d7 in enumerate(d7_idx):      # every Delta7 -> wedge 0
        W[0, d7] = 1.0 + j
    record = bk.run_graph(W, epg_idx, epg_units, d7_idx)
    assert record["empty_z_units"] == [1, 2, 3, 4, 5, 6, 7]
    for entry in record["configs"].values():
        assert not entry["valid_fit"] and not entry["pass"]


def test_check_prerequisites_blocks_in_cloud():
    missing = bk.check_prerequisites()
    if not bk.RUNTIME_DIR.exists():
        assert any("runtime" in m for m in missing)
