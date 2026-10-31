"""In-cloud validation gates for scripts/arenas/natstat_killtest.py
(H-T4T5-NATSTAT-DIRECTION, killtest_design.md section 5).

The measurement is data-gated and local; these tests assert the
registered IN-CLOUD gates before any data contact:
  (i)   scramble integrity -- amplitude spectrum preserved to rel 1e-6,
        phases decorrelated, deterministic per declared seed;
  (ii)  translation exactness -- the imposed shift of the numpy-only
        stimulus path is recovered by lattice cross-correlation to
        sub-column precision, for all 8 registered directions;
  (iii) AD-8 vote exactness on a synthetic ideal-correlator table;
  (iv)  verdict logic -- PASS, both KILL paths (B1 and B2), and every
        BLOCKED floor.
Plus the helpers the verdict machine leans on: the pinned pure sign
test, the G0/G1 gate deciders, the frozen constants, the corpus
resolution + checksum pin, the .iml reader, the trivial floor
estimator, the single-encoder-instance guarantee (ANS-1), and a
synthetic smoke test of the batched item simulator (the OP-8 static-
item zero-evoked invariant). Synthetic inputs with known answers
throughout; no fly runtime, no data files.

2026-10-29 regression gate (instrument bug caught by G0, finding at
natstat_killtest.external_from_drive): the composite stimulus path
(pixel-rendered edge -> AB-4 encoder -> external input) must deliver
fc2's NATIVE per-column drive -- exactly at plateaus and settle, within
the declared OP-5 residuals at crossings -- per polarity, direction and
speed. The original edge test only checked the encoder output in
isolation and asserted the mid-gray-centered plateau values (-0.5/+0.5)
that already contained the +0.5 offset; it could not see the external
boundary at all.
"""

import importlib.util
import math
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "natstat_killtest", ROOT / "scripts/arenas/natstat_killtest.py")
nk = importlib.util.module_from_spec(_spec)
sys.modules["natstat_killtest"] = nk
_spec.loader.exec_module(nk)


# ---------------------------------------------------------------------------
# shared synthetic fixtures
# ---------------------------------------------------------------------------

def hex_lattice(radius: int):
    """Synthetic driven lattice: the full axial box, one cell per
    column (radius 6 reproduces the registered 13x13 = 169 columns)."""
    h1, h2 = np.meshgrid(np.arange(-radius, radius + 1),
                         np.arange(-radius, radius + 1))
    x, y = nk.dk.axial_to_plane(h1.ravel(), h2.ravel())
    return nk.dk.build_lattice(x, y)


def smooth_field(side: int, seed: int, cutoff: float = 0.05) -> np.ndarray:
    """[0, 1] low-pass random texture (natural-image stand-in)."""
    rng = np.random.default_rng(seed)
    white = rng.standard_normal((side, side))
    fy = np.fft.fftfreq(side)[:, None]
    fx = np.fft.fftfreq(side)[None, :]
    mask = np.exp(-(fx ** 2 + fy ** 2) / (2.0 * cutoff ** 2))
    smooth = np.real(np.fft.ifft2(np.fft.fft2(white) * mask))
    lo, hi = smooth.min(), smooth.max()
    return (smooth - lo) / max(hi - lo, 1e-12)


def good_gates():
    return {"scramble_integrity": True, "g0": True, "g1": True}


def constant_errs(real_nat, null_nat, real_scr, null_scr, n=48):
    """Per-item error tables with constant values per arm (all three
    rewires identical, so the per-item rewire mean equals null_*)."""
    def cond(real, null):
        d = {"real": np.full(n, float(real))}
        for s in nk.REWIRE_SEEDS:
            d[f"rewired_{s}"] = np.full(n, float(null))
        return d
    return {"natural": cond(real_nat, null_nat),
            "scrambled": cond(real_scr, null_scr)}


# ---------------------------------------------------------------------------
# frozen constants + the single-encoder guarantee (ANS-1)
# ---------------------------------------------------------------------------

def test_frozen_constants_match_registration():
    assert nk.SPEEDS == (2.5, 5.0, 10.0)
    assert len(nk.DIRECTIONS_8) == 8
    for name, vec in nk.DIR_VECTORS_8.items():
        assert np.linalg.norm(vec) == pytest.approx(1.0)
    # 4 cardinals + 4 diagonals, 45 deg apart
    angles = sorted(math.degrees(math.atan2(v[1], v[0])) % 360.0
                    for v in nk.DIR_VECTORS_8.values())
    assert np.allclose(np.diff(angles), 45.0)
    assert nk.REWIRE_SEED_BASE == 4242 and nk.REWIRE_SEEDS == (0, 1, 2)
    assert nk.ALPHA == 0.05
    assert nk.MIN_EVAL_ITEMS == 30
    assert nk.MAX_UNSTABLE_FRACTION == 0.20
    assert nk.AMPLITUDE_RTOL == 1e-6
    assert nk.G0_DSI_REF == 0.3216 and nk.G0_DSI_TOL == 0.02
    assert nk.CHANCE_FLOOR_DEG == 90.0
    assert nk.TAIL_MS == 750.0
    assert nk.IMAGE_SIZE == 128
    assert nk.EXIT_CODES == {"PASS": 0, "KILL": 1, "BLOCKED": 3}
    # frozen corpus list + split (OP-1)
    assert len(nk.VAN_HATEREN_IDS) == 60
    assert nk.VAN_HATEREN_IDS[0] == "imk00001"
    assert nk.VAN_HATEREN_IDS[-1] == "imk00060"
    assert nk.CAL_INDICES == tuple(range(0, 60, 5))
    assert len(nk.CAL_INDICES) == 12 and len(nk.EVAL_INDICES) == 48
    assert set(nk.CAL_INDICES).isdisjoint(nk.EVAL_INDICES)
    assert sorted(nk.CAL_INDICES + nk.EVAL_INDICES) == list(range(60))


def test_encoder_is_the_task5_instance():
    """ANS-1: the AB-4 encoder functions ARE brainscore_killtest's own
    objects (one instance for every arm and condition), not copies."""
    assert nk.column_drive is nk.bk.column_drive
    assert nk.bilinear_resize is nk.bk.bilinear_resize
    assert nk.to_gray is nk.bk.to_gray
    assert nk.IMAGE_SIZE == nk.bk.IMAGE_SIZE
    assert nk.bk.MID_GRAY == 0.5


# ---------------------------------------------------------------------------
# gate (i): scramble integrity
# ---------------------------------------------------------------------------

def test_scramble_preserves_amplitude_and_decorrelates():
    sub = smooth_field(64, seed=3)
    scr, integ = nk.phase_scramble(sub, seed=nk.SCRAMBLE_SEED_BASE)
    assert integ["ok"] and integ["amplitude_rel_err"] <= nk.AMPLITUDE_RTOL
    assert nk.amplitude_rel_err(sub, scr) <= nk.AMPLITUDE_RTOL
    # the image itself changed, its mean (DC, pinned phase) did not
    assert not np.allclose(scr, sub, atol=1e-3)
    assert scr.mean() == pytest.approx(sub.mean(), abs=1e-9)
    corr = np.corrcoef(sub.ravel(), scr.ravel())[0, 1]
    assert abs(corr) < 0.3
    # deterministic per declared seed; different seed differs
    scr2, _ = nk.phase_scramble(sub, seed=nk.SCRAMBLE_SEED_BASE)
    assert np.array_equal(scr, scr2)
    scr3, _ = nk.phase_scramble(sub, seed=nk.SCRAMBLE_SEED_BASE + 1)
    assert not np.array_equal(scr, scr3)


def test_scramble_selftest_and_tamper_detection():
    sub = smooth_field(64, seed=4)
    st = nk.scramble_selftest(sub, seed=11)
    assert st["ok"] and st["amplitude_ok"] and st["deterministic"] \
        and st["decorrelated"]
    # the integrity metric flags a tampered (rescaled) scramble
    scr, _ = nk.phase_scramble(sub, seed=11)
    assert nk.amplitude_rel_err(sub, 1.001 * scr) > nk.AMPLITUDE_RTOL
    # and a clipped scramble whose values actually went out of range
    forced = scr - scr.min() + 0.9          # push mass above 1
    clipped = np.clip(forced, 0.0, 1.0)
    if not np.array_equal(forced, clipped):
        assert nk.amplitude_rel_err(forced, clipped) > nk.AMPLITUDE_RTOL


# ---------------------------------------------------------------------------
# gate (ii): translation exactness via lattice cross-correlation
# ---------------------------------------------------------------------------

def test_translation_recovered_to_sub_column_precision():
    lat = hex_lattice(radius=6)              # the registered 13x13
    assert lat["n_cols"] == 169
    mapping = nk.dk.crop_mapping(lat["col_x"], lat["col_y"],
                                 crop=nk.IMAGE_SIZE)
    pixel_to_col = nk.dk.assign_crop_pixels(lat, mapping)
    units = mapping["units_per_px"]
    travel = 6.0
    work = nk.required_work_size(travel, units)
    sub = smooth_field(work, seed=9)
    speed = 5.0
    for name in nk.DIRECTIONS_8:
        d = np.asarray(nk.DIR_VECTORS_8[name])
        drives = nk.translated_drives(sub, pixel_to_col, lat["n_cols"],
                                      d, speed, travel, units)
        # imposed content shift between frames 0 and k, inside [1, 2] col
        k = 15                               # 5 col/s * 0.3 s = 1.5 col
        imposed = d * speed * (k * nk.STIM_FRAME_MS / 1000.0)
        recovered = nk.lattice_xcorr_shift(drives[0], drives[k], lat,
                                           max_shift=4)
        err = float(np.linalg.norm(recovered - imposed))
        assert err < 0.5, (name, imposed.tolist(), recovered.tolist())


def test_translation_zero_shift_matches_static_ab4_view():
    """At zero offset the translated frame IS the AB-4 column drive of
    the centered static view -- the encoder is untouched by motion."""
    lat = hex_lattice(radius=6)
    mapping = nk.dk.crop_mapping(lat["col_x"], lat["col_y"],
                                 crop=nk.IMAGE_SIZE)
    pixel_to_col = nk.dk.assign_crop_pixels(lat, mapping)
    units = mapping["units_per_px"]
    travel, speed = 4.0, 2.0                 # s = 0 exactly at frame 50
    work = nk.required_work_size(travel, units)
    sub = smooth_field(work, seed=12)
    drives = nk.translated_drives(sub, pixel_to_col, lat["n_cols"],
                                  (1.0, 0.0), speed, travel, units)
    static = nk.column_drive(nk.central_window(sub, nk.IMAGE_SIZE),
                             pixel_to_col, lat["n_cols"])
    assert np.allclose(drives[50], static)


def test_frame_offsets_signs_and_span():
    units = 0.15
    ox, oy = nk.frame_offsets((1.0, 0.0), speed=5.0, travel=6.0,
                              units_per_px=units)
    # +x motion: window slides toward -x in pixels; starts at +, ends -
    assert ox[0] > 0 and ox[-1] < 0 and np.all(oy == 0)
    span_col = (ox[0] - ox[-1]) * units
    assert span_col == pytest.approx(6.0, abs=3 * units)
    ox2, oy2 = nk.frame_offsets((0.0, 1.0), speed=5.0, travel=6.0,
                                units_per_px=units)
    # +y motion (plane up): window slides toward +y in image rows
    assert np.all(ox2 == 0) and oy2[0] < 0 and oy2[-1] > 0


def test_edge_frame_drives_renders_the_fc2_edge_through_ab4():
    lat = hex_lattice(radius=2)
    mapping = nk.dk.crop_mapping(lat["col_x"], lat["col_y"], crop=60)
    pixel_to_col = nk.dk.assign_crop_pixels(lat, mapping)
    py, px = np.mgrid[0:60, 0:60]
    pxx, pyy = nk.dk.pixels_to_plane(px.ravel(), py.ravel(), mapping)
    proj = pxx * 1.0 + pyy * 0.0             # +x sweep
    fronts = np.array([-100.0, 0.0, 100.0])
    on = nk.edge_frame_drives(proj, fronts, "on", pixel_to_col,
                              lat["n_cols"])
    # fully ahead: all-dark screen -> drive -0.5; fully behind: +0.5
    assert np.allclose(on[0], -0.5)
    assert np.allclose(on[2], +0.5)
    # mid-sweep: columns left of the front bright, right dark
    left = lat["col_x"] < -1.0
    right = lat["col_x"] > 1.0
    assert np.all(on[1][left] > 0.3) and np.all(on[1][right] < -0.3)
    off = nk.edge_frame_drives(proj, fronts, "off", pixel_to_col,
                               lat["n_cols"])
    assert np.allclose(off[0], +0.5) and np.allclose(off[2], -0.5)


# ---------------------------------------------------------------------------
# 2026-10-29 instrument-bug regression gate: the EXTERNAL drive the
# network receives (not just the encoder output) must match fc2's native
# edge drive, per polarity x direction x speed. The bug this pins down:
# external = INPUT_DRIVE * (column mean - MID_GRAY) sat exactly +0.5 off
# fc2's INPUT_DRIVE * luminance at every plateau/settle sample; the OFF
# channel's scored window ran at positive lamina drive (outside fc2's
# [-1, 0] envelope) and the local G0 measured T5/OFF DSI collapsed to
# 0.11562 (T4/ON in band, 0.31583). Finding + before/after numbers:
# natstat_killtest.external_from_drive.
# ---------------------------------------------------------------------------

def test_external_from_drive_restores_absolute_luminance():
    fc2 = _load_fc2()
    assert fc2.INPUT_DRIVE == -1.0
    # full-bright AB-4 drive (+0.5) -> fc2's bright external (-1.0);
    # mid-gray (0.0) -> -0.5; full-dark (-0.5) -> fc2's dark external 0.0
    got = nk.external_from_drive(np.array([+0.5, 0.0, -0.5]),
                                 fc2.INPUT_DRIVE)
    assert np.allclose(got, [-1.0, -0.5, 0.0], atol=1e-15)
    # the composite is the identity INPUT_DRIVE * luminance: fc2's whole
    # envelope [-1, 0] is the image of luminance [0, 1], and no in-range
    # luminance can produce POSITIVE lamina drive (the T5-collapse regime)
    lum = np.linspace(0.0, 1.0, 11)
    ext = nk.external_from_drive(lum - nk.bk.MID_GRAY, fc2.INPUT_DRIVE)
    assert np.allclose(ext, -lum, atol=1e-15)
    assert (ext <= 0.0).all()


@pytest.mark.parametrize("pol", ["on", "off"])
def test_g0_edge_external_drive_matches_fc2_native(pol):
    """The G0 composite path (pixel edge -> AB-4 -> external_from_drive)
    vs fc2.run_sweep's native drive, on the engine-step grid, for every
    registered direction and speed, on the registered 169-column
    lattice. Declared tolerances (measured 2026-10-29 at the fix):
    settle + plateau samples EXACT (0.0); residuals confined to each
    column's crossing (OP-5 pixel ramp <= ASSIGN_RADIUS + pixel pitch,
    frame hold <= 20 ms): mean |diff| <= 0.011 (measured max 0.0100),
    worst-column time-integrated |diff| <= 0.15 a.u. s (measured
    0.132). Also documents the defect this gate exists for: the
    pre-fix composite (INPUT_DRIVE * drive, no +MID_GRAY) sits at
    EXACTLY +0.5 divergence on those same plateau samples."""
    fc2 = _load_fc2()
    lat = hex_lattice(radius=6)              # the registered 13x13
    assert lat["n_cols"] == 169
    mapping = nk.dk.crop_mapping(lat["col_x"], lat["col_y"],
                                 crop=nk.IMAGE_SIZE)
    pixel_to_col = nk.dk.assign_crop_pixels(lat, mapping)
    n_cols = lat["n_cols"]
    crop = nk.IMAGE_SIZE
    pyg, pxg = np.mgrid[0:crop, 0:crop]
    pxx, pyy = nk.dk.pixels_to_plane(pxg.ravel(), pyg.ravel(), mapping)
    extent = nk.travel_extent(lat["col_x"], lat["col_y"])
    travel = extent + 2.0 * fc2.EDGE_MARGIN
    sub = int(round(nk.STIM_FRAME_MS / fc2.DT_MS))
    tail_steps = int(round(fc2.TAIL_MS / fc2.DT_MS))

    # the settle screen's external == fc2's settle drive, exactly
    screen0 = (np.zeros((crop, crop)) if pol == "on"
               else np.ones((crop, crop)))
    d0 = nk.column_drive(screen0, pixel_to_col, n_cols)
    want0 = 0.0 if pol == "on" else fc2.INPUT_DRIVE * 1.0
    assert np.allclose(nk.external_from_drive(d0, fc2.INPUT_DRIVE),
                       want0, atol=1e-12)

    for dname in fc2.DIRECTIONS:
        dx, dy = fc2.DIR_VECTORS[dname]
        proj = lat["col_x"] * dx + lat["col_y"] * dy
        front0 = float(proj.min()) - fc2.EDGE_MARGIN
        pixel_proj = pxx * dx + pyy * dy
        for speed in fc2.SPEEDS:
            n_frames = max(int(math.ceil(
                travel / speed * 1000.0 / nk.STIM_FRAME_MS)), 2)
            fronts = front0 + speed * (np.arange(n_frames)
                                       * nk.STIM_FRAME_MS / 1000.0)
            drives = nk.edge_frame_drives(pixel_proj, fronts, pol,
                                          pixel_to_col, n_cols)
            k = np.arange(n_frames * sub + tail_steps)
            f_idx = np.minimum(k // sub, n_frames - 1)
            ext_new = nk.external_from_drive(drives[f_idx],
                                             fc2.INPUT_DRIVE)
            # fc2.run_sweep's native drive on the same engine grid
            t = k * fc2.DT_MS / 1000.0
            front_f = front0 + speed * t
            behind = proj[None, :] <= front_f[:, None]
            lum = (np.where(behind, 1.0, 0.0) if pol == "on"
                   else np.where(behind, 0.0, 1.0))
            ext_fc2 = fc2.INPUT_DRIVE * lum
            diff = np.abs(ext_new - ext_fc2)
            # plateau = both fronts > 1.5 col away from the column:
            # outside the pixel ramp (<= ASSIGN_RADIUS 0.75 + pitch)
            # and the <= 20 ms hold (<= 0.2 col at 10 col/s)
            plateau = ((np.abs(proj[None, :] - front_f[:, None]) > 1.5)
                       & (np.abs(proj[None, :]
                                 - fronts[f_idx][:, None]) > 1.5))
            assert plateau.mean() > 0.5, (dname, speed)
            assert diff[plateau].max() == 0.0, (dname, speed)
            assert diff.mean() <= 0.011, (dname, speed)
            worst_integral = (diff.sum(axis=0) * fc2.DT_MS / 1000.0).max()
            assert worst_integral <= 0.15, (dname, speed)
            # the recorded defect: the pre-fix composite is +0.5 off on
            # exactly these samples (regression documentation)
            buggy = np.abs(fc2.INPUT_DRIVE * drives[f_idx] - ext_fc2)
            assert buggy[plateau].min() == pytest.approx(0.5)
            assert buggy[plateau].max() == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# gate (iii): AD-8 vote exactness on an ideal-correlator table
# ---------------------------------------------------------------------------

def test_ad8_vote_exact_on_ideal_correlator_table():
    """Cells tiled over the 4 cardinal preferred directions (the fc25
    tiling) with ideal cosine-rectified responses: the vector vote must
    recover every one of the 8 imposed directions exactly."""
    prefs = np.array([[1.0, 0.0], [-1.0, 0.0], [0.0, 1.0], [0.0, -1.0]]
                     * 2)                     # T4a-d + T5a-d tiling
    pref_angles = np.arctan2(prefs[:, 1], prefs[:, 0])
    for name in nk.DIRECTIONS_8:
        d = np.asarray(nk.DIR_VECTORS_8[name])
        theta = math.atan2(d[1], d[0])
        evoked = np.maximum(np.cos(theta - pref_angles), 0.0)
        vote = nk.ad8_vote(evoked, prefs)
        assert nk.angular_error_deg(vote, d) < 1e-9, name
    # zero response -> undefined estimate, not a fake direction
    assert math.isnan(nk.angular_error_deg(
        nk.ad8_vote(np.zeros(8), prefs), (1.0, 0.0)))


def test_angular_error_known_values():
    assert nk.angular_error_deg((1, 0), (0, 1)) == pytest.approx(90.0)
    assert nk.angular_error_deg((2, 0), (1, 0)) == pytest.approx(0.0)
    assert nk.angular_error_deg((-1, 0), (1, 0)) == pytest.approx(180.0)
    assert math.isnan(nk.angular_error_deg((np.nan, 0.0), (1, 0)))


# ---------------------------------------------------------------------------
# the pinned sign test + the trivial floor estimator
# ---------------------------------------------------------------------------

def test_sign_test_exact_values():
    a = np.array([1.0, 1, 1, 1, 1])
    b = np.array([2.0, 2, 2, 2, 2])
    r = nk.sign_test_less(a, b)
    assert r["n"] == 5 and r["less"] == 5
    assert r["p"] == pytest.approx(1 / 32)
    r2 = nk.sign_test_less(np.array([1.0, np.nan]), np.array([1.0, 2.0]))
    assert r2["n"] == 0 and math.isnan(r2["p"])
    assert nk.sign_test_less(b, a)["p"] == pytest.approx(1.0)


def test_sign_test_survives_large_n():
    # Regression for the 2026-10-31 run-3 crash: float 2.0**n overflows
    # past n ~ 1023; this instrument's G1 runs at n = 1,152 eval items.
    n = 1152
    a = np.concatenate([np.zeros(700), np.full(452, 2.0)])
    b = np.ones(n)
    r = nk.sign_test_less(a, b)
    assert r["n"] == n and r["less"] == 700
    assert 0.0 <= r["p"] <= 1.0 and math.isfinite(r["p"])
    # one-sided tail with 700/1152 below: vanishingly small but nonzero
    assert r["p"] < 1e-12


def test_frame_difference_centroid_recovers_direction():
    lat = hex_lattice(radius=4)
    cx, cy = lat["col_x"], lat["col_y"]
    n_frames = 13
    drives = np.zeros((n_frames, lat["n_cols"]))
    for k in range(n_frames):
        blob_x = -2.0 + 4.0 * k / (n_frames - 1)   # moving +x
        drives[k] = np.exp(-((cx - blob_x) ** 2 + cy ** 2))
    est = nk.frame_difference_centroid(drives, lat)
    assert np.isfinite(est).all()
    assert nk.angular_error_deg(est, (1.0, 0.0)) < 30.0
    # static input: no change mass -> undefined, never a fake vector
    static = np.repeat(drives[:1], n_frames, axis=0)
    assert not np.isfinite(nk.frame_difference_centroid(static, lat)).any()


# ---------------------------------------------------------------------------
# G0 / G1 gate deciders (pure logic; the runs themselves are data-gated)
# ---------------------------------------------------------------------------

def _band(prefs: dict, dsi: float) -> dict:
    return {"per_subtype": {k: {"preferred": v} for k, v in prefs.items()},
            "median_dsi_pooled": dsi}


def test_g0_check_tiling_and_dsi_tolerance():
    recorded = {n: {"preferred": p} for n, p in
                [("T4a", "+x"), ("T4b", "-x"), ("T4c", "+y"), ("T4d", "-y"),
                 ("T5a", "+x"), ("T5b", "-x"), ("T5c", "+y"), ("T5d", "-y")]}
    good = _band({k: v["preferred"] for k, v in recorded.items()}, 0.33)
    out = nk.g0_check(good, recorded)
    assert out["pass"] and out["tiling_exact"] and out["dsi_ok"]
    # a flipped subtype WITHOUT totals fails conservatively (no tie
    # evidence -> no tie pass; 2026-10-31 amendment)
    flipped = {k: v["preferred"] for k, v in recorded.items()}
    flipped["T4a"] = "-x"
    assert not nk.g0_check(_band(flipped, 0.33), recorded)["pass"]
    # tie-aware clause (2026-10-31 amendment, the measured T5a case):
    # mismatched argmax with the reference total within G0_TIE_MARGIN
    # of the top counts as reproduced; tiling_exact stays False in the
    # record while tiling_ok and the gate pass
    tie = _band(flipped, 0.33)
    tie["per_subtype"]["T4a"]["direction_totals"] = {
        "+x": 1.3361, "-x": 1.3388, "+y": 0.8915, "-y": 0.8844}
    out_tie = nk.g0_check(tie, recorded)
    assert out_tie["pass"] and out_tie["tiling_ok"]
    assert not out_tie["tiling_exact"]
    assert abs(out_tie["tiling"]["T4a"]["tie_ratio"] - 1.3361 / 1.3388) < 1e-9
    # a genuinely flipped subtype (ratio well below the margin) still fails
    real_flip = _band(flipped, 0.33)
    real_flip["per_subtype"]["T4a"]["direction_totals"] = {
        "+x": 0.9, "-x": 1.339, "+y": 0.89, "-y": 0.88}
    assert not nk.g0_check(real_flip, recorded)["pass"]
    # the margin itself is the declared constant
    assert nk.G0_TIE_MARGIN == 0.98
    # DSI outside +/-0.02 of 0.3216 fails even with exact tiling
    assert not nk.g0_check(
        _band({k: v["preferred"] for k, v in recorded.items()}, 0.345),
        recorded)["pass"]
    assert not nk.g0_check(
        _band({k: v["preferred"] for k, v in recorded.items()},
              float("nan")), recorded)["pass"]


def test_g1_check_chance_floor():
    assert nk.g1_check(np.full(40, 30.0))["pass"]
    assert not nk.g1_check(np.full(40, 170.0))["pass"]
    # too few items for significance: fails, BLOCKED upstream
    assert not nk.g1_check(np.array([30.0, 30.0]))["pass"]
    assert not nk.g1_check(np.full(40, np.nan))["pass"]
    # median below 90 but not significant: fails
    mixed = np.array([80.0] * 11 + [100.0] * 9)
    out = nk.g1_check(mixed)
    assert out["median_ae_deg"] < 90.0 and not out["pass"]


# ---------------------------------------------------------------------------
# gate (iv): verdict logic -- PASS, both KILL paths, every BLOCKED floor
# ---------------------------------------------------------------------------

def test_verdict_pass():
    errs = constant_errs(real_nat=20, null_nat=60, real_scr=50, null_scr=50)
    out = nk.assemble_verdict(errs, good_gates(), unstable_fraction=0.0)
    assert out["verdict"] == "PASS" and out["exit_code"] == 0
    assert out["bars"]["B1_real_beats_null_on_natural"]
    assert out["bars"]["B2_gap_is_statistics_dependent"]
    assert out["tests"]["b1_sign_test_real_lt_nullmean_natural"]["p"] < 0.05


def test_verdict_kill_via_b1():
    # real does NOT beat the rewire mean on natural; B2 would hold
    errs = constant_errs(real_nat=60, null_nat=20, real_scr=60, null_scr=10)
    out = nk.assemble_verdict(errs, good_gates(), 0.0)
    assert out["verdict"] == "KILL" and out["exit_code"] == 1
    assert not out["bars"]["B1_real_beats_null_on_natural"]
    assert out["bars"]["B2_gap_is_statistics_dependent"]


def test_verdict_kill_via_b2():
    # real beats the rewires on natural AND equally on scrambled: the
    # gap is not statistics-dependent -- explanation 3 refuted
    errs = constant_errs(real_nat=20, null_nat=60, real_scr=20, null_scr=60)
    out = nk.assemble_verdict(errs, good_gates(), 0.0)
    assert out["verdict"] == "KILL" and out["exit_code"] == 1
    assert out["bars"]["B1_real_beats_null_on_natural"]
    assert not out["bars"]["B2_gap_is_statistics_dependent"]


def test_blocked_floor_1_too_few_items():
    errs = constant_errs(20, 60, 50, 50)
    errs["natural"]["rewired_1"][25:] = np.nan     # 25 < 30 evaluable
    out = nk.assemble_verdict(errs, good_gates(), 0.0)
    assert out["verdict"] == "BLOCKED" and out["exit_code"] == 3
    assert any("floor 1" in f and "rewired_1/natural" in f
               for f in out["floors"])
    # exactly 30 evaluable is NOT blocked (the floor is "< 30")
    errs2 = constant_errs(20, 60, 50, 50)
    errs2["natural"]["rewired_1"][30:] = np.nan
    assert nk.assemble_verdict(errs2, good_gates(), 0.0)["verdict"] != "BLOCKED"


def test_blocked_floor_2_g0():
    gates = good_gates()
    gates["g0"] = False
    out = nk.assemble_verdict(None, gates, 0.0)
    assert out["verdict"] == "BLOCKED" and out["exit_code"] == 3
    assert any("floor 2" in f for f in out["floors"])


def test_blocked_floor_3_g1():
    gates = good_gates()
    gates["g1"] = False
    out = nk.assemble_verdict(None, gates, 0.0)
    assert out["verdict"] == "BLOCKED"
    assert any("floor 3" in f for f in out["floors"])


def test_blocked_floor_4_scramble():
    gates = good_gates()
    gates["scramble_integrity"] = False
    out = nk.assemble_verdict(constant_errs(20, 60, 50, 50), gates, 0.0)
    assert out["verdict"] == "BLOCKED"
    assert any("floor 4" in f for f in out["floors"])


def test_blocked_floor_5_unstable():
    out = nk.assemble_verdict(constant_errs(20, 60, 50, 50), good_gates(),
                              unstable_fraction=0.25)
    assert out["verdict"] == "BLOCKED"
    assert any("floor 5" in f for f in out["floors"])
    # exactly at the threshold is NOT blocked (the floor is "> 20%")
    ok = nk.assemble_verdict(constant_errs(20, 60, 50, 50), good_gates(),
                             unstable_fraction=0.20)
    assert ok["verdict"] != "BLOCKED"


def test_blocked_without_data_and_without_gate_reason():
    out = nk.assemble_verdict(None, good_gates(), 0.0)
    assert out["verdict"] == "BLOCKED"
    assert any("floor 0" in f for f in out["floors"])


def test_check_prerequisites_reports_cloud_blockers():
    missing = nk.check_prerequisites(None, None)
    assert any("--image-root" in m for m in missing)
    if not (ROOT / "data/processed").exists():
        assert any("runtime" in m for m in missing)


def test_main_blocks_without_corpus_exit_3():
    """Floor 6 end to end (the dsec precondition pattern): invoked with
    no corpus flag, main exits BLOCKED (3) and names the missing corpus.
    Holds in-cloud (runtime also absent) AND on the local host (corpus
    flag still absent), so the assertion is environment-independent."""
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/arenas/natstat_killtest.py")],
        capture_output=True, text=True, cwd=str(ROOT),
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
    )
    assert proc.returncode == nk.EXIT_CODES["BLOCKED"] == 3
    assert "BLOCKED" in proc.stdout
    assert "--image-root" in proc.stdout


# ---------------------------------------------------------------------------
# corpus: frozen resolution, checksum pin (OP-1, OP-2), .iml reader (OP-3)
# ---------------------------------------------------------------------------

def test_resolve_corpus_names_exactly_whats_missing(tmp_path):
    root = tmp_path / "vh"
    root.mkdir()
    for vid in nk.VAN_HATEREN_IDS:
        if vid not in ("imk00007", "imk00042"):
            (root / f"{vid}.iml").write_bytes(b"x")
    entries, missing, source = nk.resolve_corpus(root, None)
    assert source == "van_hateren" and len(entries) == 60
    assert len(missing) == 2
    assert any("imk00007.iml" in m for m in missing)
    assert any("imk00042.iml" in m for m in missing)
    # complete corpus: nothing missing, frozen order kept
    for vid in ("imk00007", "imk00042"):
        (root / f"{vid}.iml").write_bytes(b"x")
    entries, missing, _ = nk.resolve_corpus(root, None)
    assert not missing
    assert [e["id"] for e in entries] == list(nk.VAN_HATEREN_IDS)
    # no corpus flag at all: the dsec precondition message
    _, missing_none, src = nk.resolve_corpus(None, None)
    assert src is None and any("--image-root" in m for m in missing_none)


def test_resolve_corpus_sintel_fallback_rule(tmp_path):
    root = tmp_path / "sintel"
    base = root / "training" / "final"
    for scene in ("alley_1", "bamboo_2", "cave_4"):
        d = base / scene
        d.mkdir(parents=True)
        for k in range(1, 26):
            (d / f"frame_{k:04d}.png").write_bytes(b"p")
    entries, missing, source = nk.resolve_corpus(None, root)
    assert source == "sintel" and not missing and len(entries) == 60
    assert entries[0]["id"].startswith("alley_1/")
    # fewer than 60 frames is BLOCKED, named with the count
    small = tmp_path / "small"
    (small / "training" / "final" / "alley_1").mkdir(parents=True)
    (small / "training" / "final" / "alley_1" / "frame_0001.png"
     ).write_bytes(b"p")
    _, missing2, _ = nk.resolve_corpus(None, small)
    assert missing2 and "only 1 frames" in missing2[0]


def test_checksum_pin_then_verify_then_tamper(tmp_path):
    files = []
    for k in range(3):
        p = tmp_path / f"im{k}.iml"
        p.write_bytes(bytes([k]) * 16)
        files.append({"id": f"im{k}", "path": p})
    lock = tmp_path / "lock.json"
    first = nk.verify_checksums(files, "van_hateren", lock_path=lock)
    assert first["status"] == "pinned_first_contact" and lock.exists()
    assert not first["mismatches"]
    second = nk.verify_checksums(files, "van_hateren", lock_path=lock)
    assert second["status"] == "verified" and not second["mismatches"]
    files[1]["path"].write_bytes(b"tampered")
    third = nk.verify_checksums(files, "van_hateren", lock_path=lock)
    assert third["mismatches"] and "im1" in third["mismatches"][0]


def test_read_van_hateren_iml_roundtrip(tmp_path):
    n = nk.VH_HEIGHT * nk.VH_WIDTH
    raw = (np.arange(n) % 60000).astype(">u2")
    p = tmp_path / "imk00001.iml"
    raw.tofile(p)
    img = nk.read_van_hateren_iml(p)
    assert img.shape == (nk.VH_HEIGHT, nk.VH_WIDTH)
    assert img.max() == pytest.approx(1.0)
    # row-major orientation: flat index 1 lands at [0, 1]
    assert img[0, 1] * 59999.0 == pytest.approx(1.0)
    bad = tmp_path / "short.iml"
    bad.write_bytes(b"\x00" * 100)
    with pytest.raises(ValueError, match="not a van Hateren"):
        nk.read_van_hateren_iml(bad)


def test_calibrate_contrast_targets_the_ab4_edge_scale():
    lat = hex_lattice(radius=6)
    mapping = nk.dk.crop_mapping(lat["col_x"], lat["col_y"],
                                 crop=nk.IMAGE_SIZE)
    pixel_to_col = nk.dk.assign_crop_pixels(lat, mapping)
    work = nk.required_work_size(4.0, mapping["units_per_px"])
    grays = [smooth_field(300, seed=s) * 0.2 + 0.4 for s in range(3)]
    cal = nk.calibrate_contrast(grays, pixel_to_col, lat["n_cols"], work)
    assert cal["chosen_gamma"] in nk.CONTRAST_GRID
    assert cal["chosen_p95_abs_drive"] > 0
    # low-contrast input picks a larger gamma than high-contrast input
    strong = [smooth_field(300, seed=s) for s in range(3)]
    cal2 = nk.calibrate_contrast(strong, pixel_to_col, lat["n_cols"], work)
    assert cal["chosen_gamma"] >= cal2["chosen_gamma"]


# ---------------------------------------------------------------------------
# the batched item simulator (OP-8 invariants; synthetic 2-node circuit)
# ---------------------------------------------------------------------------

def _load_fc2():
    spec = importlib.util.spec_from_file_location(
        "fc2_visual_ds", ROOT / "scripts/benchmarks/fc2_visual_ds.py")
    fc2 = importlib.util.module_from_spec(spec)
    sys.modules["fc2_visual_ds"] = fc2
    spec.loader.exec_module(fc2)
    return fc2


def _toy_table(tau_ms=20.0, v_rest=0.5):
    from flygi.dynamics.spiking import ParameterTable, TypeParams
    return ParameterTable(default=TypeParams(
        tau_m_ms=tau_ms, v_thresh=1e9, provenance="toy (test only)",
        v_rest=v_rest, graded=True, graded_gain=1.0), rules=[])


def test_simulate_items_static_item_evokes_zero():
    from scipy import sparse
    fc2 = _load_fc2()
    types = np.array(["L1", "T4a"])
    matrix = sparse.csr_matrix(np.array([[0.0, 0.0], [1.0, 0.0]]))
    drives = np.zeros((2, 10, 1))
    drives[1, 5:, 0] = -0.4                 # item 1: a mid-stream step
    evoked, bad = nk.simulate_items(
        fc2, matrix, types, _toy_table(), 1.0, drives,
        driven_idx=np.array([0]), driven_cols=np.array([0]),
        score_idx=np.array([1]))
    assert evoked.shape == (2, 1) and not bad.any()
    # OP-8 invariant: a stimulus identical to its settle frame (held
    # through the tail) evokes exactly ~nothing
    assert evoked[0, 0] < 1e-6
    # a changing stimulus evokes a response through the circuit
    assert evoked[1, 0] > 1e-3


def test_simulate_items_luminance_only_suppresses_lamina():
    """simulate_items uses the same fixed drive convention as G0
    (external_from_drive): under fc2's absolute-luminance histamine
    drive, NO in-range luminance can push a lamina cell above its dark
    rest. A bright -> mid-gray decrement must evoke exactly nothing
    from L1 (V rises from -0.5 toward 0, release stays clipped), while
    bright -> full dark releases it to the tonic rest (the real OFF
    response). The pre-2026-10-29 mid-gray-centered convention gave
    darker-than-mean POSITIVE lamina drive -- the regime in which the
    local G0 measured the T5/OFF collapse -- and fails this test."""
    from scipy import sparse
    fc2 = _load_fc2()
    types = np.array(["L1", "T4a"])
    matrix = sparse.csr_matrix(np.array([[0.0, 0.0], [1.0, 0.0]]))
    drives = np.zeros((3, 10, 1))
    drives[0, :, 0] = +0.5                  # static full bright
    drives[1, 0, 0] = +0.5                  # bright settle frame...
    drives[1, 1:, 0] = 0.0                  # ...then mid-gray
    drives[2, 0, 0] = +0.5                  # bright settle frame...
    drives[2, 1:, 0] = -0.5                 # ...then full dark
    evoked, bad = nk.simulate_items(
        fc2, matrix, types, _toy_table(), 1.0, drives,
        driven_idx=np.array([0]), driven_cols=np.array([0]),
        score_idx=np.array([0]))            # score L1 itself
    assert not bad.any()
    assert evoked[0, 0] < 1e-9              # OP-8 static invariant
    assert evoked[1, 0] < 1e-9              # mid-gray cannot excite L1
    assert evoked[2, 0] > 1e-3              # dark releases to tonic rest


def test_simulate_items_flags_instability():
    from scipy import sparse
    fc2 = _load_fc2()
    types = np.array(["L1", "T4a"])
    runaway = sparse.csr_matrix(np.array([[0.0, 0.0], [1.0, 10.0]]))
    drives = np.zeros((1, 5, 1))
    drives[0, :, 0] = -0.4
    _, bad = nk.simulate_items(
        fc2, runaway, types, _toy_table(), 100.0, drives,
        driven_idx=np.array([0]), driven_cols=np.array([0]),
        score_idx=np.array([1]))
    assert bad.all()
