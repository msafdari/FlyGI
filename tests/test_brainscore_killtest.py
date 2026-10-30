"""Tests for the PURE plumbing of scripts/arenas/brainscore_killtest.py
(H-EARLYFILTER-BRAINSCORE-V1). The measurement is data-gated and local;
what is testable here: grayscale conversion, the deterministic bilinear
resize, the declared column-drive convention, the hex-window inversion
that selects the scored early-filter population, the tolerant Score
extractor, and the frozen three-bar verdict assembly."""

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "brainscore_killtest", ROOT / "scripts/arenas/brainscore_killtest.py")
bk = importlib.util.module_from_spec(_spec)
sys.modules["brainscore_killtest"] = bk
_spec.loader.exec_module(bk)


def test_to_gray_variants():
    rgb = np.zeros((2, 2, 3), dtype=np.uint8)
    rgb[0, 0] = (255, 0, 0)
    g = bk.to_gray(rgb)
    assert g.shape == (2, 2)
    assert abs(g[0, 0] - 0.299) < 1e-9 and g[1, 1] == 0.0
    mono = bk.to_gray(np.full((3, 3), 128, dtype=np.uint8))
    assert abs(mono[0, 0] - 128 / 255) < 1e-9
    already = bk.to_gray(np.full((2, 2), 0.25))
    assert already[0, 0] == 0.25
    with_alpha = np.dstack([np.full((2, 2), 255, dtype=np.uint8)] * 3
                           + [np.zeros((2, 2), dtype=np.uint8)])
    assert abs(bk.to_gray(with_alpha)[0, 0] - 1.0) < 1e-9


def test_bilinear_resize_identity_and_constant():
    g = np.random.default_rng(0).random((17, 23))
    same = bk.bilinear_resize(np.asarray(g[:8, :8]), 8)
    assert np.allclose(same, g[:8, :8])
    const = bk.bilinear_resize(np.full((7, 11), 0.4), 128)
    assert const.shape == (128, 128)
    assert np.allclose(const, 0.4)
    # a horizontal gradient stays monotone along x after resampling
    grad = np.tile(np.linspace(0, 1, 50)[None, :], (50, 1))
    r = bk.bilinear_resize(grad, 16)
    assert np.all(np.diff(r[8]) >= -1e-12)
    assert r[8, 0] < 0.2 and r[8, -1] > 0.8


def test_column_drive_convention_and_empty_column():
    # 2x2 "image", 3 columns; column 2 gets no pixels (the ASSUMPTION
    # branch: zero contrast, not -MID_GRAY)
    gray = np.array([[1.0, 0.5], [0.0, 0.5]])
    pixel_to_col = np.array([[0, 1], [0, -1]])
    d = bk.column_drive(gray, pixel_to_col, 3)
    assert abs(d[0] - 0.0) < 1e-12          # mean(1.0, 0.0) - 0.5
    assert abs(d[1] - 0.0) < 1e-12          # 0.5 - 0.5
    assert d[2] == 0.0                       # empty column
    bright = bk.column_drive(np.ones((2, 2)), pixel_to_col, 3)
    assert abs(bright[0] - 0.5) < 1e-12


def test_early_filter_indices_inverts_embedding():
    # place cells at known hex coords, embed exactly as build_patch does
    h1 = np.array([19.0, 23.0, 24.0, 19.0, 15.0])
    h2 = np.array([20.0, 24.0, 20.0, 25.0, 16.0])
    x = h1 + 0.5 * h2
    y = (3 ** 0.5 / 2.0) * h2
    types = np.array(["Mi1", "Tm1", "L1", "Mi1", "T4a"])
    idx = bk.early_filter_indices(types, x, y, ("L1", "Mi1", "Tm1"),
                                  (19.0, 20.0), 4.0)
    # cell 0 center: in; cell 1 at (+4, +4): in; cell 2 at (+5, 0): out;
    # cell 3 at (0, +5): out; cell 4 is T4a: excluded by type
    assert idx.tolist() == [0, 1]


class _AggScore:
    dims = ("aggregation",)

    def __init__(self, center, error):
        self._v = {"center": np.array(center), "error": np.array(error)}

    def sel(self, aggregation):
        class _R:
            def __init__(self, v): self.values = v
        return _R(self._v[aggregation])


class _AttrScore:
    def __init__(self, center, error=None):
        self.values = np.array(center)
        self.attrs = {} if error is None else {"error": error}


def test_score_center_error_shapes():
    assert bk.score_center_error(_AggScore(0.3, 0.05)) == (0.3, 0.05)
    c, e = bk.score_center_error(_AttrScore(0.25, 0.01))
    assert c == 0.25 and e == 0.01
    c, e = bk.score_center_error(_AttrScore(0.25))
    assert c == 0.25 and math.isnan(e)
    c, e = bk.score_center_error(0.125)
    assert c == 0.125 and math.isnan(e)


def _scores(real, nulls, passthrough, error=0.01):
    return {
        "real": {"center": real, "error": error},
        "twin": {"center": 0.0, "error": 0.0},
        "passthrough": {"center": passthrough, "error": 0.0},
        "null": [{"center": n} for n in nulls],
    }


def test_verdict_pass_and_kill_paths():
    out = bk.assemble_verdict(_scores(0.3, [0.1, 0.12, 0.11], 0.2))
    assert out["verdict"] == "PASS", out
    # kill: floor (error swallows the center)
    out = bk.assemble_verdict(_scores(0.05, [0.01, 0.01, 0.01], 0.0,
                                      error=0.06))
    assert out["verdict"] == "KILL" and not out["bars"]["real_above_floor"]
    # kill: one rewire seed wins
    out = bk.assemble_verdict(_scores(0.3, [0.1, 0.31, 0.1], 0.2))
    assert not out["bars"]["real_beats_null_all_seeds"]
    assert out["verdict"] == "KILL"
    # kill: passthrough wins (ties lose too)
    out = bk.assemble_verdict(_scores(0.3, [0.1, 0.1, 0.1], 0.3))
    assert not out["bars"]["real_beats_passthrough"]
    # missing error: NaN treated as 0.0 and recorded unavailable
    out = bk.assemble_verdict(_scores(0.3, [0.1, 0.1, 0.1], 0.2,
                                      error=float("nan")))
    assert out["verdict"] == "PASS" and not out["real_error_available"]
    # missing null seed blocks the null bar rather than passing silently
    short = _scores(0.3, [0.1, 0.1], 0.2)
    assert not bk.assemble_verdict(short)["bars"]["real_beats_null_all_seeds"]


def test_frozen_constants_match_registration():
    assert bk.BENCHMARK_ID == "FreemanZiemba2013public.V1-pls"
    assert bk.RECORDING_TARGET == "V1"
    assert bk.IMAGE_SIZE == 128
    assert bk.STIM_MS == 250.0 and bk.TAIL_MS == 250.0
    assert bk.MID_GRAY == 0.5
    assert bk.SEEDS == (0, 1, 2) and bk.REWIRE_SEED_BASE == 4242
    assert bk.MIN_STIMULI == 100
    assert bk.MAX_UNSTABLE_FRACTION == 0.20
    assert bk.LUMA == (0.299, 0.587, 0.114)


def test_check_prerequisites_reports_cloud_blockers():
    missing = bk.check_prerequisites()
    assert any("brainscore_vision" in m for m in missing)
