"""Tests for the PURE plumbing of scripts/arenas/cx_heading_killtest.py
(H-CX-HEADING-LATENT, Task 9 Stage B). The measurement is data-gated
and local; testable here: the preregistered command sequences, the
command integral, circular stats/error, the CX-block rewire (outside
untouched, degrees preserved inside), the frozen three-bar verdict,
and the frozen constants."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location(
    "cx_heading_killtest", ROOT / "scripts/arenas/cx_heading_killtest.py")
ch = importlib.util.module_from_spec(_spec)
sys.modules["cx_heading_killtest"] = ch
_spec.loader.exec_module(ch)


def test_sequences_frozen_and_deterministic():
    a = ch.make_sequences()
    b = ch.make_sequences()
    assert a == b
    assert len(a) == ch.N_SEQUENCES
    assert all(len(s) == ch.SEGMENTS for s in a)
    assert all(c in ("L", "R", "off") for s in a for c in s)
    assert ch.make_sequences(seed=1) != a      # seed actually matters


def test_integrate_commands():
    seq = ["L", "L", "off", "R", "off", "L"]
    total = ch.integrate_commands(seq, rate_left=0.1, rate_right=-0.3,
                                  steps_per_segment=100)
    assert abs(total - (3 * 0.1 * 100 + 1 * -0.3 * 100)) < 1e-12
    assert ch.integrate_commands(["off"] * 6, 0.1, -0.3) == 0.0


def test_circular_stats_and_error():
    radians = np.deg2rad(np.array([0.0, 90.0]))
    mass, angle, cv = ch.circular_stats(np.array([1.0, 1.0]), radians)
    assert abs(angle - 45.0) < 1e-9 and 0 < cv < 1 and mass == 2.0
    m0, a0, cv0 = ch.circular_stats(np.zeros(2), radians)
    assert np.isnan(a0) and cv0 == 1.0
    assert ch.circ_err_deg(350.0, 10.0) == 20.0
    assert np.isnan(ch.circ_err_deg(float("nan"), 10.0))


def test_cx_block_rewire_touches_only_the_block():
    rng = np.random.default_rng(3)
    n = 40
    dense = (rng.random((n, n)) < 0.15) * rng.integers(1, 5, (n, n))
    np.fill_diagonal(dense, 0)
    W = sparse.csr_matrix(dense.astype(float))
    cx = np.arange(10, 26)
    out = ch.cx_block_rewire(W, cx, seed=11)
    full_o, full_w = np.asarray(out.todense()), np.asarray(W.todense())
    outside = np.ones((n, n), dtype=bool)
    outside[np.ix_(cx, cx)] = False
    assert np.array_equal(full_o[outside], full_w[outside])
    blk_o, blk_w = full_o[np.ix_(cx, cx)], full_w[np.ix_(cx, cx)]
    assert not np.array_equal(blk_o, blk_w)            # actually rewired
    assert np.array_equal((blk_o != 0).sum(0), (blk_w != 0).sum(0))  # in-deg
    assert np.array_equal((blk_o != 0).sum(1), (blk_w != 0).sum(1))  # out-deg


def _continuum(errs_cv):
    return {str(a): {"err_deg": e, "circvar": cv}
            for a, (e, cv) in zip((112.5, 202.5, 292.5), errs_cv)}


def _state(real_cont, real_track, rw_cont, rw_track):
    continuum = {"real": _continuum(real_cont)}
    tracking = {"real": real_track}
    for i in range(3):
        continuum[f"rw{i}"] = _continuum(rw_cont)
        tracking[f"rw{i}"] = rw_track
    return continuum, tracking


GOOD = [(10.0, 0.3)] * 3
BAD = [(170.0, 0.9)] * 3


def test_verdict_pass_and_kill_paths():
    out = ch.assemble_verdict(*_state(GOOD, [10, 20, 15], BAD, [120, 150, 90]))
    assert out["bars"] == {"continuum": True, "tracking": True,
                           "wiring_specific": True}
    assert out["verdict"] == "PASS"
    # kill: one held-out angle drifts out of band
    out = ch.assemble_verdict(*_state([(10, .3), (50, .3), (10, .3)],
                                      [10, 20, 15], BAD, [120, 150, 90]))
    assert not out["bars"]["continuum"] and out["verdict"] == "KILL"
    # kill: tracking error over the bar
    out = ch.assemble_verdict(*_state(GOOD, [50, 60, 70], BAD, [120, 150, 90]))
    assert not out["bars"]["tracking"]
    # kill: a rewired arm matches real (no wiring-specific separation)
    out = ch.assemble_verdict(*_state(GOOD, [10, 20, 15], GOOD, [9, 19, 14]))
    assert not out["bars"]["wiring_specific"]
    # NaN tracking (lost bump) counts as 180 in the mean
    out = ch.assemble_verdict(*_state(GOOD, [float("nan")] * 3,
                                      BAD, [120, 150, 90]))
    assert not out["bars"]["tracking"]
    # NaN continuum angle fails bar 1
    out = ch.assemble_verdict(*_state([(float("nan"), 0.3)] + [(10, .3)] * 2,
                                      [10, 20, 15], BAD, [120, 150, 90]))
    assert not out["bars"]["continuum"]


def test_frozen_constants_match_registration():
    assert (ch.GAIN, ch.LEAK, ch.INTERNAL_STEPS) == (1.5, 0.3, 4)
    assert ch.CAL_ANGLE == 22.5
    assert ch.HELDOUT_ANGLES == (112.5, 202.5, 292.5)
    assert (ch.WRITE_STEPS, ch.WRITE_SCALE, ch.SETTLE_STEPS) == (20, 1.0, 10)
    assert ch.DARK_STEPS == 200 and ch.ROTATION_STEPS == 30
    assert ch.TRACK_SEED == 20261010
    assert (ch.N_SEQUENCES, ch.SEGMENTS, ch.SEGMENT_STEPS) == (3, 6, 200)
    assert (ch.RETENTION_MIN, ch.CIRCVAR_MAX) == (0.05, 0.6)
    assert ch.ERR_MAX_DEG == 45.0 and ch.RATE_MIN_DEG_PER_STEP == 0.05
    assert ch.REWIRE_SEED_BASE == 4242 and ch.REWIRE_SEEDS == (0, 1, 2)
    assert ch.MAX_UNSTABLE_FRACTION == 0.20
    assert ch.EXPECTED_COUNTS == {"EPG": 46, "PEN_a(PEN1)": 20,
                                  "PEN_b(PEN2)": 22, "Delta7": 42, "PEG": 18}


def test_check_prerequisites_reports_cloud_blockers():
    missing = ch.check_prerequisites()
    assert any("runtime" in m for m in missing) or missing == []
