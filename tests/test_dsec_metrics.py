"""Tests for scripts/arenas/dsec_metrics.py (Task 2 kill-test plumbing).

Correctness tests per AGENTS.md: these establish the metrics and codec do
what their definitions say, on constructed cases with known answers. The
comparison-test obligation for the kill test itself lives in the
registered pass/kill rule (killtest_design.md), which runs where the data
is; the baseline-vs-baseline ordering checks here (global translation
beats zero flow on a translation field) are the module-level version.
"""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "dsec_metrics", ROOT / "scripts/arenas/dsec_metrics.py"
)
dm = importlib.util.module_from_spec(_spec)
sys.modules["dsec_metrics"] = dm
_spec.loader.exec_module(dm)


def test_epe_constant_field():
    gt = np.zeros((8, 9, 2))
    gt[..., 0], gt[..., 1] = 3.0, -4.0
    assert np.allclose(dm.epe(np.zeros_like(gt), gt), 5.0)


def test_epe_respects_valid_mask():
    gt = np.ones((4, 4, 2))
    est = gt.copy()
    est[0, 0] += 100.0          # huge error on an INVALID cell
    valid = np.ones((4, 4), dtype=bool)
    valid[0, 0] = False
    assert np.allclose(dm.epe(est, gt, valid), 0.0)
    assert dm.epe(est, gt, valid).shape == (15,)


def test_angular_error_2d_known_angles():
    gt = np.zeros((1, 3, 2))
    gt[..., 0] = 1.0            # GT points +x everywhere
    est = np.array([[[1.0, 0.0], [0.0, 2.0], [-3.0, 0.0]]])
    ang, frac = dm.angular_error_2d(est, gt)
    assert np.allclose(ang, [0.0, 90.0, 180.0])
    assert frac == 1.0


def test_angular_error_2d_undefined_at_zero():
    gt = np.ones((2, 2, 2))
    est = np.zeros((2, 2, 2))
    est[0, 0] = 1.0             # only one cell has a defined direction
    ang, frac = dm.angular_error_2d(est, gt)
    assert ang.shape == (1,)
    assert frac == pytest.approx(0.25)


def test_angular_error_3d_zero_for_exact():
    rng = np.random.default_rng(1)
    gt = rng.normal(size=(5, 5, 2))
    # arccos near cos=1 amplifies float round-off; 1e-3 deg is exact
    # for every purpose this metric serves.
    assert np.all(dm.angular_error_3d(gt, gt) < 1e-3)


def test_outlier_rates():
    gt = np.zeros((10, 10, 2))
    est = np.zeros_like(gt)
    est[:5, :, 0] = 2.5         # EPE 2.5 on half the field
    rates = dm.outlier_rates(est, gt)
    assert rates == {"1PE": 0.5, "2PE": 0.5, "3PE": 0.0}


def test_kitti_uint16_round_trip_values():
    flow = np.array([[[1.0, -1.0], [255.9921875, -256.0]]])
    img = dm.flow_to_kitti_uint16(flow)
    back, valid = dm.kitti_uint16_to_flow(img)
    assert valid.all()
    assert np.max(np.abs(back - flow)) <= 0.5 / dm.KITTI_SCALE
    # The canonical encoding constants, checked literally.
    assert img[0, 0, 0] == 128 + 2 ** 15
    assert img[0, 0, 1] == 2 ** 15 - 128


def test_kitti_invalid_cells_zeroed():
    flow = np.full((2, 2, 2), 7.0)
    valid = np.array([[True, False], [True, True]])
    back, vback = dm.kitti_uint16_to_flow(dm.flow_to_kitti_uint16(flow, valid))
    assert np.array_equal(vback, valid)
    assert np.all(back[~valid] == 0.0)
    assert np.allclose(back[valid], 7.0)


@pytest.mark.parametrize("filter_type", [0, 1, 2, 3, 4])
def test_png_round_trip_every_filter(filter_type):
    rng = np.random.default_rng(2 + filter_type)
    img = rng.integers(0, 65536, size=(13, 17, 3), dtype=np.uint16)
    png = dm.encode_png_16bit_rgb(img, filter_type=filter_type)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert np.array_equal(dm.decode_png_16bit_rgb(png), img)


def test_png_file_round_trip(tmp_path):
    rng = np.random.default_rng(7)
    flow = rng.uniform(-200, 200, size=(12, 20, 2))
    valid = rng.random((12, 20)) > 0.3
    path = tmp_path / "000000.png"
    dm.write_flow_png(path, flow, valid)
    back, vback = dm.read_flow_png(path)
    assert np.array_equal(valid, vback)
    assert np.max(np.abs(back[valid] - flow[valid])) <= 0.5 / dm.KITTI_SCALE


def test_decoder_rejects_non_png_and_8bit():
    with pytest.raises(ValueError):
        dm.decode_png_16bit_rgb(b"not a png at all")
    with pytest.raises(ValueError):
        dm.encode_png_16bit_rgb(np.zeros((2, 2, 3), dtype=np.uint8))


def test_zero_flow_baseline_equals_mean_magnitude():
    rng = np.random.default_rng(3)
    gt = rng.normal(size=(20, 20, 2)) * 5
    z = dm.zero_flow_baseline(gt)
    assert z["epe_mean"] == pytest.approx(
        float(np.linalg.norm(gt, axis=-1).mean())
    )


def test_global_translation_beats_zero_on_translation_field():
    rng = np.random.default_rng(4)
    gt = np.broadcast_to(np.array([6.0, -2.0]), (30, 30, 2)).copy()
    gt += rng.normal(0, 0.3, size=gt.shape)
    z = dm.zero_flow_baseline(gt)
    g, vec = dm.global_translation_baseline(gt)
    assert g["epe_mean"] < z["epe_mean"]
    assert np.allclose(vec, [6.0, -2.0], atol=0.2)


def test_summarize_shapes_and_keys():
    gt = np.ones((5, 5, 2))
    s = dm.summarize(gt, gt)
    for key in ("epe_mean", "epe_median", "ae2d_mean_deg", "1PE", "2PE",
                "3PE", "ae3d_mean_deg", "n_valid"):
        assert key in s
    assert s["n_valid"] == 25
    assert s["epe_mean"] == 0.0


def test_selftest_passes():
    assert dm.selftest() == 0
