"""Tests for the PURE plumbing of scripts/arenas/dsec_killtest.py.

The kill test itself is data-gated (no runtime, no event data in the
cloud container -- measured, WORKLOG 2026-10-01) and runs on the user's
machine; what is testable here is every connectome-independent piece:
geometry, event binning, the trivial-comparator estimators, the readout
vote, GT binning gates, and the sign test. Synthetic inputs with known
answers throughout.
"""

import importlib.util
import math
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "dsec_killtest", ROOT / "scripts/arenas/dsec_killtest.py"
)
dk = importlib.util.module_from_spec(_spec)
sys.modules["dsec_killtest"] = dk
_spec.loader.exec_module(dk)


def hex_lattice(radius=2):
    """Synthetic lattice: axial square [(h1, h2)] with 3 driven cells
    per column (L1/L2/L3 share a column, as in the real patch)."""
    h1, h2 = np.meshgrid(np.arange(-radius, radius + 1),
                         np.arange(-radius, radius + 1))
    h1, h2 = h1.ravel(), h2.ravel()
    x, y = dk.axial_to_plane(h1, h2)
    x3 = np.repeat(x, 3)
    y3 = np.repeat(y, 3)
    return dk.build_lattice(x3, y3)


def test_plane_axial_round_trip():
    h1 = np.array([-3, 0, 2, 7])
    h2 = np.array([1, 0, -4, 2])
    x, y = dk.axial_to_plane(h1, h2)
    b1, b2 = dk.plane_to_axial(x, y)
    assert np.allclose(b1, h1) and np.allclose(b2, h2)


def test_build_lattice_dedupes_columns():
    lat = hex_lattice(radius=2)
    assert lat["n_cols"] == 25
    # all three cells of a column share its index
    assert np.array_equal(lat["cell_col"][0::3], lat["cell_col"][1::3])


def test_crop_mapping_is_isotropic_and_flips_y():
    lat = hex_lattice(radius=2)
    mapping = dk.crop_mapping(lat["col_x"], lat["col_y"], crop=60)
    x0, y0 = dk.pixels_to_plane(np.array([10]), np.array([10]), mapping)
    x1, _ = dk.pixels_to_plane(np.array([11]), np.array([10]), mapping)
    _, y1 = dk.pixels_to_plane(np.array([10]), np.array([11]), mapping)
    dx = float((x1 - x0)[0])
    dy = float((y1 - y0)[0])
    assert dx == pytest.approx(mapping["units_per_px"])
    assert dy == pytest.approx(-mapping["units_per_px"])  # image y down


def test_assign_crop_pixels_center_and_radius():
    lat = hex_lattice(radius=2)
    mapping = dk.crop_mapping(lat["col_x"], lat["col_y"], crop=60)
    assignment = dk.assign_crop_pixels(lat, mapping)
    assert assignment.shape == (60, 60)
    # the crop center pixel sits nearest the lattice center column
    k = assignment[30, 30]
    assert k >= 0
    center = np.argmin(lat["col_x"] ** 2 + lat["col_y"] ** 2)
    assert k == center
    # interior pixels are assigned; the far corners (outside the hex
    # footprint's smaller extent) may be dropped but never mis-assigned
    assert (assignment >= -1).all()
    interior_fraction = float((assignment >= 0).mean())
    assert interior_fraction > 0.5


def test_bin_window_events_known_counts():
    lat = hex_lattice(radius=2)
    mapping = dk.crop_mapping(lat["col_x"], lat["col_y"], crop=60)
    assignment = dk.assign_crop_pixels(lat, mapping)
    # two events on the center pixel: one ON early, one OFF late;
    # full-frame coords with crop offset (20, 20)
    x = np.array([50, 50])
    y = np.array([50, 50])
    p = np.array([1, 0])
    t = np.array([100.0, 900.0])
    signed, counts = dk.bin_window_events(
        x, y, p, t, 0.0, 1000.0, 4, assignment, lat["n_cols"], 20, 20
    )
    col = assignment[30, 30]
    assert signed.shape == (4, lat["n_cols"])
    assert signed[0, col] == 1.0          # ON in sub-window 0
    assert signed[3, col] == -1.0         # OFF in sub-window 3
    assert counts.sum() == 2.0
    # events outside the window or crop are dropped
    signed2, counts2 = dk.bin_window_events(
        np.array([50, 5]), np.array([50, 5]), np.array([1, 1]),
        np.array([2000.0, 100.0]), 0.0, 1000.0, 4,
        assignment, lat["n_cols"], 20, 20,
    )
    assert counts2.sum() <= 1.0


def test_centroid_shift_recovers_direction():
    lat = hex_lattice(radius=2)
    neighbors = dk.axial_neighbors(lat)
    # a blob of counts moving one column in +x (plane): first third on
    # column (0,0), last third on column (1,0)
    first = np.zeros(lat["n_cols"])
    last = np.zeros(lat["n_cols"])
    a = {tuple(p): k for k, p in enumerate(lat["axial"])}
    first[a[(0, 0)]] = 10.0
    last[a[(1, 0)]] = 10.0
    est = dk.centroid_shift_directions(first, last, lat, neighbors)
    k = a[(0, 0)]
    assert np.isfinite(est[k]).all()
    assert est[k][0] > 0 and abs(est[k][1]) < 1e-9
    # a column whose neighborhood saw no events stays undefined
    far = a[(-2, -2)]
    assert not np.isfinite(est[far]).any()


def test_cross_correlation_recovers_axial_shift():
    lat = hex_lattice(radius=2)
    a = {tuple(p): k for k, p in enumerate(lat["axial"])}
    rng = np.random.default_rng(5)
    first = np.zeros(lat["n_cols"])
    last = np.zeros(lat["n_cols"])
    # random pattern on the interior, copied one step in +h1
    for (h1, h2), k in a.items():
        if -2 <= h1 <= 1:
            v = rng.uniform(1, 5)
            first[k] = v
            last[a[(h1 + 1, h2)]] = v
    shift = dk.cross_correlation_shift(first, last, lat, max_shift=2)
    assert np.allclose(shift, dk.HEX_E1)


def test_population_vote_dc_cancellation():
    # two cells, same column, equal evoked, OPPOSED preferred vectors:
    # direction-independent (DC) response cancels in the vote.
    evoked = np.array([3.0, 3.0])
    cell_col = np.array([0, 0])
    pref = np.array([[1.0, 0.0], [-1.0, 0.0]])
    votes, coverage = dk.population_vote(evoked, cell_col, pref, 1)
    assert np.allclose(votes[0], 0.0)
    assert coverage[0] == 2
    # unequal evoked leaves the differential signal
    votes2, _ = dk.population_vote(np.array([5.0, 3.0]), cell_col, pref, 1)
    assert votes2[0][0] == pytest.approx(2.0)


def test_bin_gt_to_columns_direction_and_gates():
    lat = hex_lattice(radius=2)
    mapping = dk.crop_mapping(lat["col_x"], lat["col_y"], crop=60)
    assignment = dk.assign_crop_pixels(lat, mapping)
    frame = np.zeros((100, 100, 2))
    frame[..., 0] = 5.0           # u = +5 px (image right)
    frame[..., 1] = 5.0           # v = +5 px (image DOWN)
    valid = np.ones((100, 100), dtype=bool)
    gt, evaluable, med = dk.bin_gt_to_columns(
        frame, valid, assignment, lat["n_cols"], 20, 20
    )
    k = assignment[30, 30]
    assert evaluable[k]
    # plane mapping: (u, v) -> (u, -v)
    assert gt[k][0] == pytest.approx(5.0)
    assert gt[k][1] == pytest.approx(-5.0)
    assert med == pytest.approx(math.hypot(5, 5))
    # magnitude gate: below MIN_GT_MAG_PX nothing is evaluable
    _, ev2, _ = dk.bin_gt_to_columns(
        frame * 0.1, valid, assignment, lat["n_cols"], 20, 20
    )
    assert not ev2.any()
    # validity gate: < 50% valid pixels -> not evaluable
    _, ev3, _ = dk.bin_gt_to_columns(
        frame, np.zeros_like(valid), assignment, lat["n_cols"], 20, 20
    )
    assert not ev3.any()


def test_window_mean_ae_known_angles():
    gt = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 0.0]])
    est = np.array([[0.0, 1.0], [0.0, 2.0], [np.nan, np.nan]])
    evaluable = np.array([True, True, True])
    # defined estimates: 90 deg and 0 deg -> mean 45
    assert dk.window_mean_ae(est, gt, evaluable) == pytest.approx(45.0)
    assert math.isnan(
        dk.window_mean_ae(np.full((3, 2), np.nan), gt, evaluable)
    )


def test_paired_sign_test_exact_values():
    a = np.array([1.0, 1, 1, 1, 1])
    b = np.array([2.0, 2, 2, 2, 2])
    r = dk.paired_sign_test_less(a, b)
    assert r["n"] == 5 and r["less"] == 5
    assert r["p"] == pytest.approx(1 / 32)
    # ties and NaNs drop
    r2 = dk.paired_sign_test_less(np.array([1.0, np.nan]),
                                  np.array([1.0, 2.0]))
    assert r2["n"] == 0 and math.isnan(r2["p"])
    # reversed ordering is not significant
    r3 = dk.paired_sign_test_less(b, a)
    assert r3["p"] == pytest.approx(1.0)


def test_check_prerequisites_reports_cloud_blockers():
    missing = dk.check_prerequisites(None)
    assert any("--data-root" in m for m in missing)
    # the measured container state: no compiled runtime
    if not (ROOT / "data/processed").exists():
        assert any("runtime" in m for m in missing)


def test_frozen_constants_match_registration():
    """The design doc's frozen numbers, asserted against the code so a
    silent edit to either is loud."""
    assert dk.WINDOW_CAP == 250
    assert dk.CAL_FRACTION == 0.2
    assert dk.MIN_EVAL_WINDOWS == 30
    assert dk.DT_SUB_GRID_MS == (10.0, 20.0, 50.0, 100.0)
    assert dk.CROP == 480
    assert dk.MIN_GT_MAG_PX == 2.0
    assert dk.MIN_EVAL_COLUMNS == 10
    assert dk.REWIRE_SEEDS == (0, 1, 2)
    assert dk.TAIL_MS == 750.0
