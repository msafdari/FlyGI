#!/usr/bin/env python3
"""H-T4T5-NATSTAT-DIRECTION -- the Task 10 item 5 kill test.

PREREGISTRATION (EXPERIMENTS.yaml H-T4T5-NATSTAT-DIRECTION and
docs/arenas/task10_menu/killtest_design.md section 5, both frozen
2026-10-23 in one commit BEFORE any instrument code; restated here, not
changed):

  - PREMISE: the T4/T5 rewire-parity measured three times (ARC, DSEC,
    DVS) is caused by non-ecological input statistics: on translating
    NATURAL scenes at validated class-2.5 physiology the real wiring
    beats its rewires at direction estimation, and the advantage
    disappears when the natural statistics are destroyed
    (phase-scrambled) with the power spectrum preserved.
  - 2x2: {REAL, 3x REWIRE (seeds 4242+0..2)} x {NATURAL,
    PHASE-SCRAMBLED}; identical fc25 class-2.5 machinery (13x13 hex
    patch, dt 2 ms, settle 2500 ms, trained params from
    docs/fidelity2/flyvis_trained_params.json); identical AB-4 encoder,
    ONE instance across all arms and conditions (the AE-1 dodge: the
    manipulated variable lives in stimulus space, upstream of any map).
  - STIMULI: rigid constant-velocity translation of static natural
    images; 8 directions (4 cardinals + 4 diagonals); speeds
    {2.5, 5, 10} col/s (the fc25 passing band). Scrambled condition:
    per-image phase randomization with one declared seed per image,
    amplitude spectrum preserved (rel 1e-6, asserted at run time),
    identical translation applied.
  - CORPUS: van Hateren natural-image subset, FROZEN ID list +
    checksums in the instrument (user-fetched locally; SOURCED caveat
    carried -- the mirror is unverifiable from the cloud); declared
    calibration/evaluation split by index list (calibration touches a
    contrast scalar only); Sintel-via-local-flyvis is the declared
    fallback corpus. Corpus stays outside the repo tree.
  - READOUT (AD-8, no fitted parameters): vector vote -- per-subtype
    preferred directions read verbatim from the fc25 results JSON,
    DIR_VECTORS unit vectors; per-item estimate vs imposed direction =
    2D angular error. Item = (image, direction, speed).
  - BARS: B1 -- REAL beats the per-item mean of the 3 rewires on
    NATURAL items (one-sided paired sign test p < 0.05 AND median
    per-item error strictly lower; the Task-2 bar verbatim). B2 -- the
    gap is statistics-dependent: d_i = err_NULL - err_REAL per item;
    one-sided paired sign test d_natural > d_scrambled on matched
    items, p < 0.05, AND median(d_nat - d_scr) > 0. PASS iff B1 AND
    B2; KILL otherwise -- B2 failing refutes explanation 3 in its
    sharpest available form.
  - FLOOR CONTEXT (reported, non-decisional): circuit-free
    frame-difference-centroid estimator on the identical lattice
    input; uniform-tau TWIN attribution arm.
  - GATES (in-cloud, numpy-only, pre-data; asserted by unit tests in
    tests/test_natstat_killtest.py): (i) scramble integrity;
    (ii) translation exactness recovered by lattice cross-correlation
    to sub-column precision; (iii) AD-8 vote recovers direction
    exactly on a synthetic ideal-correlator table; (iv) verdict-logic
    tests covering PASS, both KILL paths, every BLOCKED floor. On the
    verdict machine before eval (data-gated hooks): G0 -- fc25's own
    moving-edge stimulus pushed through the NEW stimulus code path
    reproduces the recorded per-subtype preferred-direction tiling
    (argmax exact) and DSI within +/-0.02 of the measured 0.3216.
    G1 -- usable-input gate: REAL-natural median per-item error below
    the 90-deg chance floor, one-sided sign test p < 0.05; failure =
    BLOCKED (a measured convention limit of the AB-4-class drive),
    never a statistics verdict.
  - BLOCKED floors (exit 3; an instrument statement, never a
    verdict): (1) < 30 evaluable eval items in any arm-condition;
    (2) G0 fail; (3) G1 fail; (4) scramble-integrity selftest fail at
    run time; (5) > 20% unstable-item drop (an unstable item is
    dropped from EVERY arm and counted); (6) corpus absent -- exit
    BLOCKED listing exactly the missing corpus (the dsec precondition
    pattern).
  - Exit codes: 0 PASS / 1 KILL / 3 BLOCKED.

OPERATIONALIZATIONS declared here, BEFORE any data contact (the
registration's terms made exact; each is also marked ASSUMPTION at its
code site):

  OP-1  Frozen corpus list: imk00001..imk00060 -- the first 60 IDs of
        the published van Hateren IML set in lexicographic order (the
        deterministic sampling rule). Calibration split = every 5th
        index starting at 0 (12 images); evaluation = the other 48.
  OP-2  Checksums: sha256 values are unknowable from the cloud (the
        registration's own SOURCED caveat), so the instrument pins
        them at FIRST LOCAL CONTACT into
        results/arenas/natstat_corpus_checksums_<source>.json and
        verifies every later run against the pin; any mismatch is
        BLOCKED (corpus integrity), never a verdict.
  OP-3  .iml format: 1024 rows x 1536 cols of big-endian uint16
        (SOURCED: the database's published MATLAB reader uses
        'ieee-be'; unverifiable from the cloud); per-image division by
        its own max -> [0, 1] (deterministic, parameter-free). File
        size is asserted before reading.
  OP-4  The one calibrated contrast scalar gamma: shown image =
        clip(0.5 + gamma * (gray - mean(gray)), 0, 1) on the central
        square (mean -> AB-4 mid-gray); gamma is chosen on the CAL
        images only, from the fixed grid CONTRAST_GRID, as argmin
        |log10(p95(|column drive|) / 0.5)| over the centered static
        views -- 0.5 is the AB-4 full-edge drive magnitude, the regime
        G0 certifies. Drive-level only: calibration runs NO network
        and scoring never feeds back.
  OP-5  Working substrate: central square crop -> AB-4 bilinear resize
        to work_size = 128 + 2*(ceil(travel_px/2) + 2); the 128x128
        view window translates across it at integer-pixel offsets
        updated every STIM_FRAME_MS = 20 ms (quantization <= 0.5 px
        ~= 0.075 col, below the sub-column gate-ii bar; 20 ms = 10
        engine steps at fc2 dt 2 ms).
  OP-6  Scramble site: the NATURAL working substrate (post-contrast,
        post-clip) is what gets phase-scrambled, so natural and
        scrambled items share the identical translation + encoder
        path downstream and the run-time amplitude assert holds on
        exactly the translated substrate. The scramble output is NOT
        clipped (clipping would silently break the preserved-amplitude
        claim); the out-of-range fraction is recorded. The DC phase is
        pinned to 0, so mean luminance is preserved.
  OP-7  Travel: fc2's sweep geometry reused unchanged -- travel =
        patch extent + 2 * EDGE_MARGIN columns, identical for every
        direction at a given speed.
  OP-8  Settle: per item, 2500 ms at the item's FIRST-FRAME drive (the
        fc2 settle-on-background analog; removes the full-field onset
        transient -- the fc2 v1 readout artifact lesson); evoked =
        rectified output minus the per-item settled baseline,
        integrated over the translation plus a 750 ms tail at the HELD
        FINAL FRAME (TAIL_MS == fc2.WINDOW_AFTER_S * 1000, asserted;
        motion stops, late responses play out). A zero-drive tail
        would inject a direction-independent offset transient into
        every item (the same v1 lesson); holding the frame gives the
        testable invariant that a static item evokes exactly zero,
        asserted by unit test.
  OP-9  G1 scope: REAL-natural EVAL items under REAL's own stability
        mask, evaluated BEFORE the remaining arms run (the
        registration's "before eval"); later drops do not reopen it.
  OP-10 Floor-1 scope: the decisional arm-conditions only (REAL and
        each of the 3 rewires, both conditions). The TWIN is context,
        decides nothing, and therefore cannot block.
  OP-11 Trivial floor estimator: displacement of the
        |frame-difference|-mass centroid from the first third to the
        last third of frames (the dsec TRIVIAL-3 analog on frames),
        on the identical per-column drive input. Context only.
  OP-12 Sintel fallback rule: used ONLY when --image-root is absent
        (a partially present van Hateren corpus is BLOCKED, named
        exactly, never silently swapped). Frames = lexicographic
        (scene, frame) listing under <root>/training/final (or <root>
        itself), stride = floor(total/60), first 60; fewer than 60 is
        BLOCKED.
  OP-13 G0 geometry: fc2's edge sweep verbatim (front0 = min patch
        projection - EDGE_MARGIN, same travel, per-cell v2
        crossing-locked windows, fc2.TAIL_MS at the held final frame,
        settle on the pre-edge screen) with the edge RENDERED AT PIXEL
        RESOLUTION and pushed through the AB-4 column encoder -- the
        new stimulus code path end to end. Decision on the v2 band
        (fc2.band_metrics, the verdict machine); v1 recorded as
        context.
  OP-14 Amplitude metric for "rel 1e-6": max |A_scr - A_nat| / max
        A_nat over the full 2-D spectrum. The run-time selftest also
        checks determinism (same seed -> identical array) and
        decorrelation (|pearson| < 0.5, skipped for a constant image).
  OP-15 Scramble seeds: seed = SCRAMBLE_SEED_BASE + corpus index (one
        declared seed per image, frozen here).

INSTRUMENT AMENDMENT (2026-10-29; G0 blocked the first local run BEFORE
any decision data, exactly as designed -- recorded at the
post-data-contact standard regardless): the drive -> external boundary
as first committed applied INPUT_DRIVE to the mid-gray-centered column
contrast, handing the network fc2's native drive + 0.5 at every sample
of every sweep and settle (measured exactly on the registered lattice;
OFF items spent their whole scored window at POSITIVE lamina drive,
outside fc2's native [-1, 0] envelope, and the local G0 measured T5/OFF
collapsed at 0.11562 while T4/ON held in band at 0.31583). Fixed by
restoring absolute luminance at the single shared external_from_drive
site (external = INPUT_DRIVE * (drive + MID_GRAY)); the frozen
constants, bars, floors, the AB-4 encoder functions and the sweep
geometry are untouched. Full finding + before/after numbers at
external_from_drive; the registration's required full re-run happens on
the local host.

TIER DISCIPLINE: every number this script prints or saves is Measured
under this protocol. Expected-tier content, with its base rate: none
offered beyond the program's 0-for-16 score-adjacent record
(docs/arenas/SYNTHESIS.md). Priors both ways are recorded in the
registration.

Run (where the compiled runtime, the fc25 result and the corpus live):
    python scripts/arenas/natstat_killtest.py --image-root <dir with
        imk00001.iml .. imk00060.iml>
    python scripts/arenas/natstat_killtest.py --sintel-root <MPI-Sintel
        root>            (declared fallback corpus)
Output: results/arenas/natstat_killtest.json (+ .log)
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BENCH = ROOT / "scripts/benchmarks"
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# ASSUMPTION (ANS-1, register row): the encoder is the Task-5 AB-4
# convention VERBATIM -- grayscale (Rec. 601) -> bilinear 128x128 ->
# per-column mean luminance over the DSEC identity-crop pixel assignment
# -> drive = column mean - 0.5. AMENDED 2026-10-29 (instrument bug,
# caught by G0): applying INPUT_DRIVE to that mid-gray-centered drive
# directly handed the network fc2's drive + 0.5 everywhere; the network
# boundary now restores absolute luminance first (external =
# INPUT_DRIVE * (drive + MID_GRAY); finding + measured divergence at
# external_from_drive). The encoder itself is unchanged. ONE
# instance across all arms and conditions (the AE-1 dodge): these are
# the brainscore_killtest/dsec_killtest functions themselves, imported,
# not reimplemented, so no arm can see a different map. What breaks if
# wrong: AE-1 measured ~4.4 points of map noise; a per-arm encoder would
# let that noise masquerade as a wiring effect.
bk = _load_module("brainscore_killtest", HERE / "brainscore_killtest.py")
dk = _load_module("dsec_killtest", HERE / "dsec_killtest.py")
to_gray = bk.to_gray
bilinear_resize = bk.bilinear_resize
column_drive = bk.column_drive

# --- frozen constants (killtest_design.md section 5; do not tune) -----------
HYPOTHESIS = "H-T4T5-NATSTAT-DIRECTION"
REGISTRATION = ("docs/arenas/task10_menu/killtest_design.md section 5 "
                "(frozen 2026-10-23, before any instrument code)")

IMAGE_SIZE = 128              # AB-4 view size (asserted == bk.IMAGE_SIZE)
# ASSUMPTION (ANS-2, register row): "naturalistic motion" here MEANS
# rigid constant-velocity translation at the fc25 passing band speeds;
# saccades and 3D flow are out of scope. A KILL leaves richer ecology
# untested and the close sentence must say so.
SPEEDS = (2.5, 5.0, 10.0)     # col/s, the fc25 passing band
_SQ = 2.0 ** -0.5
DIRECTIONS_8 = ("+x", "+x+y", "+y", "-x+y", "-x", "-x-y", "-y", "+x-y")
DIR_VECTORS_8 = {
    "+x": (1.0, 0.0), "+x+y": (_SQ, _SQ), "+y": (0.0, 1.0),
    "-x+y": (-_SQ, _SQ), "-x": (-1.0, 0.0), "-x-y": (-_SQ, -_SQ),
    "-y": (0.0, -1.0), "+x-y": (_SQ, -_SQ),
}

REWIRE_SEED_BASE = 4242
REWIRE_SEEDS = (0, 1, 2)
ALPHA = 0.05
MIN_EVAL_ITEMS = 30           # floor 1 (Task-2 rule)
MAX_UNSTABLE_FRACTION = 0.20  # floor 5
AMPLITUDE_RTOL = 1e-6         # scramble integrity, asserted at run time
SCRAMBLE_SEED_BASE = 20261023  # OP-15: seed = base + corpus index
G0_DSI_REF = 0.3216           # the measured fc25 class-2.5 DSI
G0_DSI_TOL = 0.02             # declared in the registration
CHANCE_FLOOR_DEG = 90.0       # G1 chance floor for 2D angular error
STIM_FRAME_MS = 20.0          # OP-5 (10 engine steps at fc2 dt 2 ms)
TAIL_MS = 750.0               # asserted == fc2.WINDOW_AFTER_S * 1000
TRAVEL_MARGIN_COL = 1.0       # asserted == fc2.EDGE_MARGIN (OP-7)
CONTRAST_GRID = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0, 16.0)   # OP-4, fixed
CONTRAST_TARGET = 0.5         # AB-4 full-edge drive magnitude
CONTRAST_PERCENTILE = 95.0
N_COLUMNS_EXPECTED = 169      # the registration's 13x13 hex patch
EXIT_CODES = {"PASS": 0, "KILL": 1, "BLOCKED": 3}

# ASSUMPTION (ANS-4, register row): the frozen van Hateren subset below
# is ASSUMED representative of natural-image statistics. The list is the
# deterministic rule OP-1 (first 60 published IDs, lexicographic),
# frozen before any run; checksums pin per OP-2 because the mirror is
# unverifiable from the cloud. What breaks if wrong: a KILL could be
# about these 60 scenes, not natural statistics; the Sintel fallback and
# the recorded rule make that auditable.
N_IMAGES = 60
VAN_HATEREN_IDS = tuple(f"imk{i:05d}" for i in range(1, N_IMAGES + 1))
CAL_INDICES = tuple(range(0, N_IMAGES, 5))           # 12 images (OP-1)
EVAL_INDICES = tuple(i for i in range(N_IMAGES) if i % 5 != 0)  # 48
# sha256 constants: {} = none hardcodable from the cloud (OP-2); the
# first local contact pins them to CHECKSUM_LOCK_TEMPLATE and every
# later run verifies against the pin. A user-promoted hex here is
# verified with highest precedence.
VAN_HATEREN_SHA256: dict[str, str] = {}
CHECKSUM_LOCK_TEMPLATE = "results/arenas/natstat_corpus_checksums_{source}.json"
VH_HEIGHT, VH_WIDTH = 1024, 1536                      # OP-3

FC25_RESULTS = ROOT / "results/benchmarks/fc25_visual_ds.json"
PARAMS_JSON = ROOT / "docs/fidelity2/flyvis_trained_params.json"
RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
ANNOTATIONS = ROOT / "data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather"
OUT_JSON = ROOT / "results/arenas/natstat_killtest.json"

assert set(CAL_INDICES).isdisjoint(EVAL_INDICES)
assert sorted(CAL_INDICES + EVAL_INDICES) == list(range(N_IMAGES))


# ---------------------------------------------------------------------------
# Numpy-only stimulus module (unit-tested in-cloud; no fly runtime, no
# data files). Everything the 2x2 sees flows through these functions.
# ---------------------------------------------------------------------------

def central_square(gray: np.ndarray) -> np.ndarray:
    """Centered side x side crop, side = min(h, w)."""
    h, w = gray.shape
    side = min(h, w)
    r0 = (h - side) // 2
    c0 = (w - side) // 2
    return gray[r0:r0 + side, c0:c0 + side]


def central_window(img: np.ndarray, size: int) -> np.ndarray:
    """Centered size x size window of a square array."""
    n = img.shape[0]
    if n < size:
        raise ValueError(f"array side {n} < window {size}")
    b = (n - size) // 2
    return img[b:b + size, b:b + size]


def apply_contrast(gray: np.ndarray, scalar: float) -> np.ndarray:
    """OP-4: shown = clip(0.5 + scalar * (gray - mean), 0, 1).

    ASSUMPTION (OP-4, declared in header): mean luminance maps to the
    AB-4 mid-gray and ONE global scalar sets contrast. The scalar is
    the registration's "contrast scalar only" calibration freedom;
    everything else here is parameter-free. What breaks if wrong: a
    mis-set contrast moves every arm and condition identically (the
    encoder is shared), so it can cause a BLOCKED G1, never a false
    arm separation."""
    g = np.asarray(gray, dtype=np.float64)
    return np.clip(0.5 + float(scalar) * (g - g.mean()), 0.0, 1.0)


def required_work_size(travel_col: float, units_per_px: float) -> int:
    """OP-5: substrate side so the 128-window stays inside at max shift."""
    margin_px = int(math.ceil((travel_col / 2.0) / units_per_px)) + 2
    return IMAGE_SIZE + 2 * margin_px


def make_substrate(gray: np.ndarray, scalar: float, work_size: int) -> np.ndarray:
    """OP-5: central square -> contrast (OP-4) -> AB-4 bilinear resize
    to the working resolution. The same bilinear_resize instance as the
    Task-5 encoder (ANS-1)."""
    sq = apply_contrast(central_square(gray), scalar)
    return bilinear_resize(sq, work_size)


def amplitude_rel_err(a: np.ndarray, b: np.ndarray) -> float:
    """OP-14 metric: max |A_b - A_a| / max A_a over the 2-D spectrum."""
    fa = np.abs(np.fft.fft2(np.asarray(a, np.float64)))
    fb = np.abs(np.fft.fft2(np.asarray(b, np.float64)))
    peak = float(fa.max())
    if peak <= 0.0:
        return float("inf")
    return float(np.abs(fb - fa).max() / peak)


def phase_scramble(image: np.ndarray, seed: int) -> tuple[np.ndarray, dict]:
    """Per-image phase randomization, amplitude spectrum preserved.

    ASSUMPTION (ANS-3, register row): "natural statistics" MEANS exactly
    what this destroys -- the phase structure -- with the power spectrum
    explicitly outside the claim. The added phase field is the angle of
    the FFT of a seeded real white-noise field, which is Hermitian-odd
    by construction, so the inverse transform is real to machine
    precision; the DC phase is pinned to 0 (mean preserved, OP-6). The
    output is NOT clipped (OP-6): clipping would silently break the
    preserved-amplitude claim that the run-time assert certifies. What
    breaks if wrong: B2 would compare conditions that differ in more
    than phase structure, and the integrity record would not show it."""
    a = np.asarray(image, dtype=np.float64)
    spectrum = np.fft.fft2(a)
    rng = np.random.default_rng(seed)
    noise = rng.standard_normal(a.shape)
    phi = np.angle(np.fft.fft2(noise))
    phi[0, 0] = 0.0
    scrambled = np.real(
        np.fft.ifft2(np.abs(spectrum) * np.exp(1j * (np.angle(spectrum) + phi)))
    )
    rel = amplitude_rel_err(a, scrambled)
    integrity = {
        "seed": int(seed),
        "amplitude_rel_err": rel,
        "ok": bool(rel <= AMPLITUDE_RTOL),
        "out_of_range_fraction": float(
            np.mean((scrambled < 0.0) | (scrambled > 1.0))
        ),
    }
    return scrambled, integrity


def scramble_selftest(substrate: np.ndarray, seed: int) -> dict:
    """Run-time scramble-integrity selftest (floor 4 + OP-14): amplitude
    preserved to AMPLITUDE_RTOL, deterministic per seed, decorrelated."""
    s1, integ = phase_scramble(substrate, seed)
    s2, _ = phase_scramble(substrate, seed)
    deterministic = bool(np.array_equal(s1, s2))
    a = np.asarray(substrate, np.float64).ravel()
    b = s1.ravel()
    if a.std() > 1e-12 and b.std() > 1e-12:
        corr = float(np.corrcoef(a, b)[0, 1])
        decorrelated = bool(abs(corr) < 0.5)
    else:
        corr = float("nan")
        decorrelated = True
    return {
        "amplitude_rel_err": integ["amplitude_rel_err"],
        "amplitude_ok": integ["ok"],
        "deterministic": deterministic,
        "pixel_correlation": corr,
        "decorrelated": decorrelated,
        "ok": bool(integ["ok"] and deterministic and decorrelated),
    }


def travel_extent(x: np.ndarray, y: np.ndarray) -> float:
    """fc2.run_sweep's extent rule verbatim (OP-7): identical traverse
    length for every direction at a given speed."""
    return float(max(
        np.ptp(x), np.ptp(y), np.ptp(x * (2 ** -0.5) + y * (2 ** -0.5))
    ))


def frame_offsets(direction_vec, speed: float, travel: float,
                  units_per_px: float,
                  frame_ms: float = STIM_FRAME_MS) -> tuple[np.ndarray, np.ndarray]:
    """OP-5 window offsets: image content moves along +direction_vec
    (plane coords, y up) at `speed` col/s, so the sampling window moves
    (-dx, +dy) in pixel coords (image y points down -- the dsec
    declared mapping). Offsets are quantized to integer pixels per
    frame (<= 0.5 px error ~= 0.075 col, below the gate-ii bar)."""
    n_frames = max(int(math.ceil(travel / speed * 1000.0 / frame_ms)), 2)
    t = np.arange(n_frames) * frame_ms / 1000.0
    s = speed * t - travel / 2.0        # signed content displacement, col
    dx, dy = float(direction_vec[0]), float(direction_vec[1])
    ox = np.rint(-dx * s / units_per_px).astype(np.int64)
    oy = np.rint(+dy * s / units_per_px).astype(np.int64)
    return ox, oy


def translated_drives(substrate: np.ndarray, pixel_to_col: np.ndarray,
                      n_cols: int, direction_vec, speed: float,
                      travel: float, units_per_px: float,
                      frame_ms: float = STIM_FRAME_MS) -> np.ndarray:
    """Rigid constant-velocity translation through the AB-4 encoder:
    per frame, cut the 128x128 view at the quantized offset and take
    the column drive. Returns (n_frames, n_cols)."""
    work = substrate.shape[0]
    if substrate.shape[0] != substrate.shape[1]:
        raise ValueError("substrate must be square")
    ox, oy = frame_offsets(direction_vec, speed, travel, units_per_px,
                           frame_ms)
    base = (work - IMAGE_SIZE) // 2
    out = np.zeros((ox.size, n_cols))
    for k in range(ox.size):
        r0 = base + int(oy[k])
        c0 = base + int(ox[k])
        if r0 < 0 or c0 < 0 or r0 + IMAGE_SIZE > work or c0 + IMAGE_SIZE > work:
            raise ValueError(
                "substrate too small for the requested travel "
                "(instrument bug: required_work_size violated)")
        window = substrate[r0:r0 + IMAGE_SIZE, c0:c0 + IMAGE_SIZE]
        out[k] = column_drive(window, pixel_to_col, n_cols)
    return out


def edge_frame_drives(pixel_proj: np.ndarray, fronts: np.ndarray,
                      polarity: str, pixel_to_col: np.ndarray,
                      n_cols: int) -> np.ndarray:
    """OP-13: the fc2 moving edge RENDERED AT PIXEL RESOLUTION through
    the AB-4 encoder (G0's new stimulus code path). pixel_proj: plane
    projection of each view pixel onto the sweep direction (flattened
    crop x crop); fronts: (n_frames,) front positions. ON: luminance 1
    where proj <= front (behind the front, fc2.run_sweep's rule)."""
    crop = int(round(math.sqrt(pixel_proj.size)))
    out = np.zeros((fronts.size, n_cols))
    for k in range(fronts.size):
        behind = pixel_proj <= fronts[k]
        if polarity == "on":
            lum = np.where(behind, 1.0, 0.0)
        else:
            lum = np.where(behind, 0.0, 1.0)
        out[k] = column_drive(lum.reshape(crop, crop), pixel_to_col, n_cols)
    return out


def external_from_drive(col_drive: np.ndarray, input_drive: float) -> np.ndarray:
    """The ONE drive -> network-external-input convention. Every network
    input in this instrument (G0 settle, G0 sweep, simulate_items) goes
    through this function, so no arm or gate can see a different map.

    BUG FIX (2026-10-29, instrument; caught by G0 BEFORE any decision
    data, exactly as the gate was designed to): as first committed this
    boundary was `input_drive * col_drive` -- fc2's histaminergic sign
    applied to the MID-GRAY-CENTERED AB-4 contrast instead of to
    absolute luminance. MEASURED divergence vs fc2's native edge drive
    (engine-step grid, registered 169-column lattice, both polarities x
    4 directions x 3 speeds): external = fc2's + 0.5 EXACTLY at every
    plateau sample and both settle screens (ON settle +0.5 vs fc2 0.0;
    OFF settle -0.5 vs -1.0; OFF post-edge +0.5 vs 0.0 -- POSITIVE
    drive into the histaminergic lamina, outside fc2's native [-1, 0]
    envelope, so every OFF item spent its scored v2 window in a regime
    fc2's convention cannot produce; the ON post-edge level -0.5 stays
    inside the envelope). Local G0 consequence (run record, WORKLOG
    "Task 10 item 5", 2026-10-29): pooled v2 median DSI 0.17634 vs the
    required 0.3216 +/- 0.02 -- T4/ON in band (0.31583), T5/OFF
    collapsed (0.11562), while the same fc25 reference reproduced at
    0.32157 the same day through fc2's native drive (t4t5 gate B).
    FIX: reconstruct absolute column luminance before the sign,
    external = input_drive * (col_drive + MID_GRAY) = input_drive *
    column_mean_luminance. Measured after: plateau + settle divergence
    0.0 exactly; residual confined to each column's crossing (the
    declared OP-5 pixel-sampling ramp + <= 20 ms frame hold): mean
    |diff| <= 0.0100, worst-column time-integral 0.132 a.u. s (was
    4.887). Frozen constants/bars/floors and the shared AB-4 encoder
    (ANS-1) untouched; asserted per direction/speed/polarity by
    tests/test_natstat_killtest.py::
    test_g0_edge_external_drive_matches_fc2_native."""
    return float(input_drive) * (np.asarray(col_drive, np.float64)
                                 + bk.MID_GRAY)


def lattice_xcorr_shift(drive_a: np.ndarray, drive_b: np.ndarray,
                        lattice: dict, max_shift: int = 4) -> np.ndarray:
    """Gate-ii machinery: the content shift of b relative to a, in
    plane units, recovered on the dense axial grid by mean-normalized
    cross-correlation with 1-D quadratic peak refinement per axial axis
    (sub-column precision, asserted by unit test)."""
    ax = lattice["axial"]
    h1_min, h2_min = ax.min(axis=0)
    h1_max, h2_max = ax.max(axis=0)
    g1 = int(h1_max - h1_min + 1)
    g2 = int(h2_max - h2_min + 1)
    a = np.zeros((g1, g2))
    b = np.zeros((g1, g2))
    a[ax[:, 0] - h1_min, ax[:, 1] - h2_min] = drive_a - np.mean(drive_a)
    b[ax[:, 0] - h1_min, ax[:, 1] - h2_min] = drive_b - np.mean(drive_b)
    shifts = list(range(-max_shift, max_shift + 1))
    corr = np.full((len(shifts), len(shifts)), -np.inf)
    for i, d1 in enumerate(shifts):
        for j, d2 in enumerate(shifts):
            lo1, hi1 = max(0, -d1), min(g1, g1 - d1)
            lo2, hi2 = max(0, -d2), min(g2, g2 - d2)
            if hi1 <= lo1 or hi2 <= lo2:
                continue
            block = (a[lo1:hi1, lo2:hi2]
                     * b[lo1 + d1:hi1 + d1, lo2 + d2:hi2 + d2])
            corr[i, j] = float(block.sum() / block.size)

    i_star, j_star = np.unravel_index(int(np.argmax(corr)), corr.shape)

    def refine(cm: float, c0: float, cp: float) -> float:
        denom = cm - 2.0 * c0 + cp
        if not np.isfinite(denom) or abs(denom) < 1e-15:
            return 0.0
        return float(np.clip(0.5 * (cm - cp) / denom, -0.5, 0.5))

    d1 = float(shifts[i_star])
    d2 = float(shifts[j_star])
    if 0 < i_star < len(shifts) - 1 and np.isfinite(
            corr[i_star - 1, j_star]) and np.isfinite(corr[i_star + 1, j_star]):
        d1 += refine(corr[i_star - 1, j_star], corr[i_star, j_star],
                     corr[i_star + 1, j_star])
    if 0 < j_star < len(shifts) - 1 and np.isfinite(
            corr[i_star, j_star - 1]) and np.isfinite(corr[i_star, j_star + 1]):
        d2 += refine(corr[i_star, j_star - 1], corr[i_star, j_star],
                     corr[i_star, j_star + 1])
    return d1 * dk.HEX_E1 + d2 * dk.HEX_E2


# ---------------------------------------------------------------------------
# Readout + statistics (pure; unit-tested in-cloud)
# ---------------------------------------------------------------------------

def ad8_vote(evoked: np.ndarray, pref_vec: np.ndarray) -> np.ndarray:
    """AD-8: per-item global estimate = sum over scored cells of
    evoked * subtype preferred unit vector. No fitted parameters: the
    preferred vectors are read verbatim from the fc25 results JSON."""
    return (np.asarray(evoked, np.float64)[:, None]
            * np.asarray(pref_vec, np.float64)).sum(axis=0)


def angular_error_deg(est, imposed) -> float:
    """2D angular error in degrees; NaN when the estimate is undefined
    (non-finite or ~zero vector)."""
    e = np.asarray(est, dtype=np.float64)
    g = np.asarray(imposed, dtype=np.float64)
    ne = float(np.linalg.norm(e))
    ng = float(np.linalg.norm(g))
    if not np.isfinite(e).all() or ne <= 1e-12 or ng <= 1e-12:
        return float("nan")
    cos = float(np.dot(e, g) / (ne * ng))
    return float(np.degrees(np.arccos(np.clip(cos, -1.0, 1.0))))


def sign_test_less(a: np.ndarray, b: np.ndarray) -> dict[str, Any]:
    """One-sided exact paired sign test, H1: a < b. METHOD PINNED (no
    scipy dependency drift): pairs with NaN on either side or ties are
    dropped; p = exact binomial tail via math.comb at theta = 1/2."""
    a = np.asarray(a, dtype=np.float64)
    b = np.asarray(b, dtype=np.float64)
    ok = np.isfinite(a) & np.isfinite(b)
    less = int(np.sum(a[ok] < b[ok]))
    greater = int(np.sum(a[ok] > b[ok]))
    n = less + greater
    if n == 0:
        return {"n": 0, "less": 0, "p": float("nan")}
    p = sum(math.comb(n, k) for k in range(less, n + 1)) / 2.0 ** n
    return {"n": n, "less": less, "p": float(min(p, 1.0))}


def frame_difference_centroid(drives: np.ndarray, lattice: dict) -> np.ndarray:
    """OP-11 trivial floor (context, non-decisional): displacement of
    the |frame-difference|-mass centroid from the first third to the
    last third of frames, on the identical per-column drive input.
    NaN when either third carries no change mass."""
    d = np.diff(np.asarray(drives, np.float64), axis=0)
    if d.shape[0] < 2:
        return np.full(2, np.nan)
    third = max(d.shape[0] // 3, 1)
    mass_first = np.abs(d[:third]).sum(axis=0)
    mass_last = np.abs(d[-third:]).sum(axis=0)
    sf, sl = float(mass_first.sum()), float(mass_last.sum())
    if sf <= 0.0 or sl <= 0.0:
        return np.full(2, np.nan)
    cx, cy = lattice["col_x"], lattice["col_y"]
    c0 = np.array([(cx * mass_first).sum() / sf, (cy * mass_first).sum() / sf])
    c1 = np.array([(cx * mass_last).sum() / sl, (cy * mass_last).sum() / sl])
    return c1 - c0


# ---------------------------------------------------------------------------
# Gates + verdict (pure; unit-tested in-cloud)
# ---------------------------------------------------------------------------

def calibrate_contrast(cal_grays: list[np.ndarray], pixel_to_col: np.ndarray,
                       n_cols: int, work_size: int) -> dict[str, Any]:
    """OP-4: the one contrast scalar, chosen on CAL images only, at the
    drive level (no network runs). Grid argmin |log10(p95 / 0.5)|."""
    curve = []
    best = None
    for gamma in CONTRAST_GRID:
        mags = []
        for gray in cal_grays:
            view = central_window(make_substrate(gray, gamma, work_size),
                                  IMAGE_SIZE)
            mags.append(np.abs(column_drive(view, pixel_to_col, n_cols)))
        p95 = float(np.percentile(np.concatenate(mags), CONTRAST_PERCENTILE))
        curve.append({"gamma": gamma, "p95_abs_drive": p95})
        if p95 > 1e-12:
            loss = abs(math.log10(p95 / CONTRAST_TARGET))
            if best is None or loss < best[0]:
                best = (loss, gamma, p95)
    return {
        "curve": curve,
        "chosen_gamma": best[1] if best else None,
        "chosen_p95_abs_drive": best[2] if best else None,
        "target_p95": CONTRAST_TARGET,
        "rule": "argmin |log10(p95(|column drive|)/0.5)| over CAL centered "
                "static views; fixed grid; drive-level only (OP-4)",
    }


def g0_check(band_v2: dict, recorded_per_subtype: dict) -> dict[str, Any]:
    """G0 decision: per-subtype preferred tiling argmax EXACT vs the
    fc25 JSON, and pooled median DSI within G0_DSI_TOL of G0_DSI_REF."""
    tiling = {}
    for name, rec in recorded_per_subtype.items():
        got = band_v2["per_subtype"].get(name, {}).get("preferred")
        tiling[name] = {"recorded": rec["preferred"], "reproduced": got}
    tiling_exact = all(v["recorded"] == v["reproduced"]
                       for v in tiling.values()) and len(tiling) > 0
    dsi = float(band_v2["median_dsi_pooled"])
    dsi_ok = bool(np.isfinite(dsi) and abs(dsi - G0_DSI_REF) <= G0_DSI_TOL)
    return {
        "tiling": tiling,
        "tiling_exact": bool(tiling_exact),
        "median_dsi_pooled": dsi,
        "dsi_ref": G0_DSI_REF,
        "dsi_tol": G0_DSI_TOL,
        "dsi_ok": dsi_ok,
        "pass": bool(tiling_exact and dsi_ok),
    }


def g1_check(real_natural_errors: np.ndarray) -> dict[str, Any]:
    """G1 usable-input gate (OP-9): REAL-natural per-item errors must
    beat the 90-deg chance floor -- median strictly below AND one-sided
    sign test p < ALPHA. Failure is BLOCKED (a measured convention
    limit of the AB-4-class drive), never a statistics verdict."""
    e = np.asarray(real_natural_errors, dtype=np.float64)
    test = sign_test_less(e, np.full(e.shape, CHANCE_FLOOR_DEG))
    finite = np.isfinite(e)
    median = float(np.median(e[finite])) if finite.any() else float("nan")
    passed = bool(np.isfinite(test["p"]) and test["p"] < ALPHA
                  and np.isfinite(median) and median < CHANCE_FLOOR_DEG)
    return {
        "n_evaluable": int(finite.sum()),
        "median_ae_deg": median,
        "chance_floor_deg": CHANCE_FLOOR_DEG,
        "sign_test_vs_chance": test,
        "pass": passed,
    }


DECISIONAL_ARMS = ("real",) + tuple(f"rewired_{s}" for s in REWIRE_SEEDS)


def assemble_verdict(errs: dict[str, dict[str, np.ndarray]] | None,
                     gates: dict[str, bool],
                     unstable_fraction: float) -> dict[str, Any]:
    """The frozen verdict rule on per-item angular errors.

    errs: None (evaluation not reached), or {"natural": {...},
    "scrambled": {...}} mapping arm -> aligned per-eval-item error
    arrays (NaN = not evaluable). Decisional arms: real + rewired_0..2
    (the twin is context and decides nothing, OP-10). gates:
    {"scramble_integrity", "g0", "g1"} booleans. Returns the verdict
    record with the frozen exit code."""
    floors: list[str] = []
    if not gates.get("scramble_integrity", False):
        floors.append("floor 4 (scramble): run-time scramble-integrity "
                      "selftest failed")
    if not gates.get("g0", False):
        floors.append("floor 2 (G0): fc25 moving-edge reproduction through "
                      "the new stimulus path failed")
    if not gates.get("g1", False):
        floors.append("floor 3 (G1): REAL-natural did not beat the 90-deg "
                      "chance floor (usable-input gate)")
    if unstable_fraction > MAX_UNSTABLE_FRACTION:
        floors.append(f"floor 5 (unstable): {unstable_fraction:.3f} of eval "
                      f"items dropped for instability "
                      f"(> {MAX_UNSTABLE_FRACTION})")
    if errs is not None:
        for cond in ("natural", "scrambled"):
            for arm in DECISIONAL_ARMS:
                n_ok = int(np.isfinite(
                    np.asarray(errs[cond][arm], np.float64)).sum())
                if n_ok < MIN_EVAL_ITEMS:
                    floors.append(
                        f"floor 1 (items): only {n_ok} evaluable eval items "
                        f"in {arm}/{cond} (need >= {MIN_EVAL_ITEMS})")
    elif not floors:
        floors.append("floor 0 (instrument): no evaluation data and no "
                      "recorded gate failure")

    out: dict[str, Any] = {
        "floors": floors,
        "unstable_fraction": float(unstable_fraction),
    }
    if floors:
        out.update({"verdict": "BLOCKED", "bars": None, "tests": None,
                    "exit_code": EXIT_CODES["BLOCKED"]})
        return out

    nat, scr = errs["natural"], errs["scrambled"]
    real_nat = np.asarray(nat["real"], np.float64)
    real_scr = np.asarray(scr["real"], np.float64)
    null_nat = np.mean(np.stack(
        [np.asarray(nat[f"rewired_{s}"], np.float64) for s in REWIRE_SEEDS]
    ), axis=0)
    null_scr = np.mean(np.stack(
        [np.asarray(scr[f"rewired_{s}"], np.float64) for s in REWIRE_SEEDS]
    ), axis=0)

    # B1 (Task-2 bar verbatim): REAL beats the rewire mean on NATURAL.
    b1_test = sign_test_less(real_nat, null_nat)
    med_real_nat = float(np.nanmedian(real_nat))
    med_null_nat = float(np.nanmedian(null_nat))
    b1 = bool(np.isfinite(b1_test["p"]) and b1_test["p"] < ALPHA
              and med_real_nat < med_null_nat)

    # B2: the gap is statistics-dependent. d = err_NULL - err_REAL.
    d_nat = null_nat - real_nat
    d_scr = null_scr - real_scr
    b2_test = sign_test_less(d_scr, d_nat)      # H1: d_scr < d_nat
    gap = d_nat - d_scr
    med_gap = float(np.nanmedian(gap)) if np.isfinite(gap).any() else float("nan")
    b2 = bool(np.isfinite(b2_test["p"]) and b2_test["p"] < ALPHA
              and np.isfinite(med_gap) and med_gap > 0.0)

    verdict = "PASS" if (b1 and b2) else "KILL"
    out.update({
        "bars": {"B1_real_beats_null_on_natural": b1,
                 "B2_gap_is_statistics_dependent": b2},
        "tests": {
            "b1_sign_test_real_lt_nullmean_natural": b1_test,
            "b1_median_real_natural": med_real_nat,
            "b1_median_nullmean_natural": med_null_nat,
            "b2_sign_test_dscr_lt_dnat": b2_test,
            "b2_median_dnat_minus_dscr": med_gap,
            "median_d_natural": float(np.nanmedian(d_nat))
            if np.isfinite(d_nat).any() else float("nan"),
            "median_d_scrambled": float(np.nanmedian(d_scr))
            if np.isfinite(d_scr).any() else float("nan"),
        },
        "verdict": verdict,
        "exit_code": EXIT_CODES[verdict],
    })
    return out


# ---------------------------------------------------------------------------
# Corpus (frozen list, OP-1..3, OP-12; checksum pin OP-2)
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def resolve_corpus(image_root: Path | None,
                   sintel_root: Path | None) -> tuple[list[dict], list[str], str | None]:
    """Frozen corpus resolution. Returns (entries, missing, source);
    entries are {"id", "path"} in frozen order. Any missing item is one
    line of the BLOCKED report (the dsec precondition pattern)."""
    if image_root is not None:
        root = Path(image_root)
        entries, missing = [], []
        if not root.is_dir():
            return [], [f"van Hateren corpus directory not found: {root}"], \
                "van_hateren"
        for vid in VAN_HATEREN_IDS:
            p = root / f"{vid}.iml"
            entries.append({"id": vid, "path": p})
            if not p.exists():
                missing.append(f"van Hateren image: {p}")
        return entries, missing, "van_hateren"
    if sintel_root is not None:
        root = Path(sintel_root)
        base = root / "training" / "final"
        if not base.is_dir():
            base = root
        frames = sorted(base.glob("*/frame_*.png"))
        if len(frames) < N_IMAGES:
            return [], [f"Sintel fallback: only {len(frames)} frames under "
                        f"{base} (need >= {N_IMAGES}; rule OP-12)"], "sintel"
        stride = max(len(frames) // N_IMAGES, 1)
        picked = frames[::stride][:N_IMAGES]
        entries = [{"id": f"{p.parent.name}/{p.name}", "path": p}
                   for p in picked]
        return entries, [], "sintel"
    return [], ["corpus: pass --image-root (van Hateren imk00001..imk00060 "
                ".iml files) or --sintel-root (declared fallback, OP-12)"], None


def verify_checksums(entries: list[dict], source: str,
                     lock_path: Path | None = None) -> dict[str, Any]:
    """OP-2 corpus-integrity pin. Precedence: a hardcoded module
    constant (none hardcodable from the cloud; a user may promote the
    pinned values later) > the lock file > pin-on-first-contact.

    ASSUMPTION (OP-2, declared in header): sha256 values for the
    user-fetched corpus are unknowable in-cloud, so first LOCAL contact
    pins them and every later run verifies the pin. What breaks if
    wrong: a corpus swapped between runs would silently change the
    frozen stimulus set; the pin makes that BLOCKED instead."""
    if lock_path is None:
        lock_path = ROOT / CHECKSUM_LOCK_TEMPLATE.format(source=source)
    sums = {e["id"]: sha256_file(e["path"]) for e in entries}
    expected: dict[str, str] = {}
    if source == "van_hateren":
        expected.update(VAN_HATEREN_SHA256)
    pinned = None
    if lock_path.exists():
        pinned = json.loads(lock_path.read_text())
        for k, v in pinned.get("sha256", {}).items():
            expected.setdefault(k, v)
    mismatches = [
        f"checksum mismatch for {k}: expected {expected[k][:16]}..., "
        f"measured {sums[k][:16]}..."
        for k in sums if k in expected and expected[k] != sums[k]
    ]
    status = "verified" if expected and not mismatches else "pinned_first_contact"
    if not expected:
        lock_path.parent.mkdir(parents=True, exist_ok=True)
        lock_path.write_text(json.dumps({
            "source": source,
            "pinned_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "note": "first-local-contact sha256 pin (OP-2); verified on "
                    "every later run",
            "sha256": sums,
        }, indent=1))
    return {"status": status, "lock_path": str(lock_path),
            "mismatches": mismatches, "sha256": sums}


def read_van_hateren_iml(path: Path) -> np.ndarray:
    """OP-3: 1024x1536 big-endian uint16, normalized by the image max.

    ASSUMPTION (OP-3, SOURCED): the .iml layout follows the database's
    published MATLAB reader ('ieee-be', [1536 1024] fread) --
    unverifiable from the cloud; the size assert and the non-blank
    check catch a wrong-format file at first local contact."""
    data = np.fromfile(str(path), dtype=">u2")
    if data.size != VH_HEIGHT * VH_WIDTH:
        raise ValueError(
            f"{path}: expected {VH_HEIGHT * VH_WIDTH} uint16 samples "
            f"({VH_HEIGHT}x{VH_WIDTH}), got {data.size} -- not a van "
            f"Hateren .iml (OP-3)")
    img = data.reshape(VH_HEIGHT, VH_WIDTH).astype(np.float64)
    peak = float(img.max())
    if peak <= 0.0:
        raise ValueError(f"{path}: blank image")
    return img / peak


def load_corpus_gray(path: Path) -> np.ndarray:
    if path.suffix.lower() == ".iml":
        return read_van_hateren_iml(path)
    return bk.load_image_gray(path)       # PIL/cv2-gated (Sintel PNGs)


def check_prerequisites(image_root: Path | None,
                        sintel_root: Path | None) -> list[str]:
    """Everything the run needs; each missing item is one line of the
    BLOCKED report (dsec pattern). Pure checks only."""
    missing = []
    if not RUNTIME_DIR.exists():
        missing.append(f"compiled MaleCNS runtime: {RUNTIME_DIR}")
    if not ANNOTATIONS.exists():
        missing.append(f"raw annotations feather: {ANNOTATIONS}")
    if not PARAMS_JSON.exists():
        missing.append(f"trained flyvis params: {PARAMS_JSON}")
    if not FC25_RESULTS.exists():
        missing.append(f"fc25 passing result (local-only): {FC25_RESULTS}")
    for mod in ("pyarrow", "scipy"):
        if importlib.util.find_spec(mod) is None:
            missing.append(f"python package: {mod}")
    if image_root is None and sintel_root is None:
        missing.append("--image-root (van Hateren corpus directory with "
                       "imk00001.iml..imk00060.iml) or --sintel-root "
                       "(declared fallback corpus)")
    elif image_root is not None and not Path(image_root).exists():
        missing.append(f"corpus root not found: {image_root}")
    elif image_root is None and sintel_root is not None \
            and not Path(sintel_root).exists():
        missing.append(f"Sintel root not found: {sintel_root}")
    if sintel_root is not None and image_root is None \
            and importlib.util.find_spec("PIL") is None \
            and importlib.util.find_spec("cv2") is None:
        missing.append("python package: PIL or cv2 (Sintel fallback PNGs)")
    return missing


# ---------------------------------------------------------------------------
# Data-gated simulation (local host only)
# ---------------------------------------------------------------------------

def simulate_items(fc2mod, matrix, types, table, gain: float,
                   drives: np.ndarray, driven_idx: np.ndarray,
                   driven_cols: np.ndarray, score_idx: np.ndarray,
                   log=None, label: str = "") -> tuple[np.ndarray, np.ndarray]:
    """Batched per-item run of the fc2 graded dynamics on frame drives.

    drives: (m, n_frames, n_cols) per-column AB-4 contrasts per frame.
    ASSUMPTION (OP-8, declared in header): each item settles 2500 ms at
    its FIRST-FRAME drive (the fc2 settle-on-background analog; removes
    the direction-unrelated full-field onset transient -- the fc2 v1
    artifact lesson), then streams frames (each held STIM_FRAME_MS =
    10 engine steps), then a TAIL_MS tail at the HELD FINAL FRAME;
    evoked = rectified output minus the per-item settled baseline,
    integrated throughout. The held-frame tail makes a static item
    evoke exactly zero (unit-tested invariant); a zero-drive tail
    would inject a direction-independent offset transient into every
    item. What breaks if wrong: a settle/tail convention that leaves a
    shared transient inflates every arm identically (shared path) --
    it can cost G1, never fake an arm separation.
    Returns (evoked (m, n_scored), unstable (m,))."""
    m, n_frames, _ = drives.shape
    t0 = time.time()
    net = fc2mod.GradedFlyvisNetwork(matrix, types, table,
                                     dt_ms=fc2mod.DT_MS, gain=gain)
    n_nodes = net.v.shape[0]
    v0 = net.v_rest.copy()
    net.tau = net.tau[:, None]
    net.v_rest = net.v_rest[:, None]
    net.v = np.repeat(v0[:, None], m, axis=1)
    bad = np.zeros(m, dtype=bool)

    def unstable() -> np.ndarray:
        finite = np.isfinite(net.v).all(axis=0)
        with np.errstate(invalid="ignore"):
            big = np.where(
                finite,
                np.abs(np.where(np.isfinite(net.v), net.v, 0.0)).max(axis=0),
                np.inf,
            ) > fc2mod.V_ABORT
        return ~finite | big

    def ext(frame_cols: np.ndarray) -> np.ndarray:
        d = np.zeros((n_nodes, m))
        # 2026-10-29 bug-fix site: absolute luminance restored at the one
        # shared boundary (see external_from_drive).
        d[driven_idx, :] = external_from_drive(
            frame_cols[:, driven_cols].T, fc2mod.INPUT_DRIVE)
        return d

    settle_steps = int(round(fc2mod.SETTLE_MS / fc2mod.DT_MS))
    sub_steps = int(round(STIM_FRAME_MS / fc2mod.DT_MS))
    tail_steps = int(round(TAIL_MS / fc2mod.DT_MS))
    step = 0
    with np.errstate(over="ignore", invalid="ignore"):
        first = ext(drives[:, 0, :])
        for _ in range(settle_steps):
            net.step(first)
            step += 1
            if step % 100 == 0:
                bad |= unstable()
        base_out = np.maximum(net.v, 0.0)[score_idx, :]
        total = np.zeros((score_idx.size, m))
        for f in range(n_frames):
            drive = ext(drives[:, f, :])
            for _ in range(sub_steps):
                net.step(drive)
                step += 1
                if step % 50 == 0:
                    bad |= unstable()
                evoked = np.maximum(
                    np.maximum(net.v, 0.0)[score_idx, :] - base_out, 0.0)
                total += evoked * (fc2mod.DT_MS / 1000.0)
        last = ext(drives[:, -1, :])        # held final frame (OP-8)
        for _ in range(tail_steps):
            net.step(last)
            step += 1
            if step % 50 == 0:
                bad |= unstable()
            evoked = np.maximum(
                np.maximum(net.v, 0.0)[score_idx, :] - base_out, 0.0)
            total += evoked * (fc2mod.DT_MS / 1000.0)
        bad |= unstable()
    if log is not None:
        log(f"  [{label}] {m} items x {n_frames} frames in "
            f"{time.time() - t0:.1f}s, unstable {int(bad.sum())}")
    return total.T.copy(), bad


def g0_edge_reproduction(fc2mod, patch, pixel_to_col, n_cols, lattice,
                         mapping, table, gain: float, score_idx, score_types,
                         recorded_per_subtype: dict, log) -> dict[str, Any]:
    """G0 (OP-13): fc2's moving-edge protocol with the edge rendered at
    pixel resolution through the AB-4 encoder (the new stimulus path),
    scored on the v2 crossing-window verdict machine (fc2.band_metrics
    verbatim). Data-gated hook; decision logic in g0_check (unit-
    tested in-cloud)."""
    t0 = time.time()
    types = patch["types"]
    x, y = patch["x"], patch["y"]
    extent = travel_extent(x, y)
    driven_idx = np.flatnonzero(patch["driven_mask"])
    driven_cols = lattice["cell_col"]
    n_nodes = types.shape[0]
    is_t4 = np.array([t.startswith("T4") for t in score_types])

    crop = IMAGE_SIZE
    py, px = np.mgrid[0:crop, 0:crop]
    pxx, pyy = dk.pixels_to_plane(px.ravel(), py.ravel(), mapping)

    settle_steps = int(round(fc2mod.SETTLE_MS / fc2mod.DT_MS))
    sub_steps = int(round(STIM_FRAME_MS / fc2mod.DT_MS))
    tail_steps = int(round(fc2mod.TAIL_MS / fc2mod.DT_MS))

    shape = (len(fc2mod.DIRECTIONS), score_idx.size)
    acc_v2 = {pol: np.zeros(shape) for pol in ("on", "off")}
    acc_v1 = {pol: np.zeros(shape) for pol in ("on", "off")}
    speed_shape = (len(fc2mod.SPEEDS),) + shape
    acc_speed_v2 = {pol: np.zeros(speed_shape) for pol in ("on", "off")}
    acc_speed_v1 = {pol: np.zeros(speed_shape) for pol in ("on", "off")}
    all_stable = True

    for pol in ("on", "off"):
        screen0 = np.zeros((crop, crop)) if pol == "on" else np.ones((crop, crop))
        d0 = column_drive(screen0, pixel_to_col, n_cols)
        ext0 = np.zeros(n_nodes)
        # 2026-10-29 bug-fix site (see external_from_drive): settle on the
        # pre-edge screen at fc2's absolute-luminance drive (ON 0.0 / OFF
        # -1.0), not at its mid-gray-centered +0.5-shifted image.
        ext0[driven_idx] = external_from_drive(d0[driven_cols],
                                               fc2mod.INPUT_DRIVE)
        net = fc2mod.GradedFlyvisNetwork(patch["matrix"], types, table,
                                         dt_ms=fc2mod.DT_MS, gain=gain)
        for k in range(settle_steps):
            net.step(ext0)
            if k % 100 == 0 and (
                not np.all(np.isfinite(net.v))
                or np.max(np.abs(net.v)) > fc2mod.V_ABORT
            ):
                all_stable = False
                break
        if not all_stable:
            break
        settled = net.state()
        base_out = np.maximum(settled, 0.0)[score_idx]

        for si, speed in enumerate(fc2mod.SPEEDS):
            for di, dname in enumerate(fc2mod.DIRECTIONS):
                dx, dy = fc2mod.DIR_VECTORS[dname]
                proj = x * dx + y * dy
                front0 = float(proj.min()) - fc2mod.EDGE_MARGIN
                travel = extent + 2.0 * fc2mod.EDGE_MARGIN
                n_frames = max(int(math.ceil(
                    travel / speed * 1000.0 / STIM_FRAME_MS)), 2)
                frame_t = np.arange(n_frames) * STIM_FRAME_MS / 1000.0
                fronts = front0 + speed * frame_t
                pixel_proj = pxx * dx + pyy * dy
                col_frames = edge_frame_drives(pixel_proj, fronts, pol,
                                               pixel_to_col, n_cols)
                crossing = (proj[score_idx] - front0) / speed
                w_open = crossing - fc2mod.WINDOW_BEFORE_COL / speed
                w_close = crossing + fc2mod.WINDOW_AFTER_S
                net.set_state(settled)
                total_v1 = np.zeros(score_idx.size)
                total_v2 = np.zeros(score_idx.size)
                ext = np.zeros(n_nodes)
                step = 0
                stable = True
                for f in range(n_frames + 1):
                    # last frame held for fc2.TAIL_MS (OP-13)
                    frame = col_frames[min(f, n_frames - 1)]
                    # 2026-10-29 bug-fix site (see external_from_drive)
                    ext[driven_idx] = external_from_drive(
                        frame[driven_cols], fc2mod.INPUT_DRIVE)
                    reps = sub_steps if f < n_frames else tail_steps
                    for _ in range(reps):
                        t = step * fc2mod.DT_MS / 1000.0
                        net.step(ext)
                        step += 1
                        if step % 50 == 0 and (
                            not np.all(np.isfinite(net.v))
                            or np.max(np.abs(net.v)) > fc2mod.V_ABORT
                        ):
                            stable = False
                            break
                        evoked = np.maximum(
                            net.output()[score_idx] - base_out, 0.0)
                        mass = evoked * (fc2mod.DT_MS / 1000.0)
                        total_v1 += mass
                        in_window = (t >= w_open) & (t <= w_close)
                        total_v2 += np.where(in_window, mass, 0.0)
                    if not stable:
                        break
                all_stable &= stable
                acc_v1[pol][di] += total_v1
                acc_v2[pol][di] += total_v2
                acc_speed_v1[pol][si, di] = total_v1
                acc_speed_v2[pol][si, di] = total_v2

    if not all_stable:
        record = {"stable": False, "elapsed_s": round(time.time() - t0, 1),
                  "check": {"pass": False,
                            "reason": "instability during the G0 edge "
                                      "reproduction (instrument statement)"}}
        log(f"G0: UNSTABLE -> fail ({record['elapsed_s']}s)")
        return record

    band_v2 = fc2mod.band_metrics(acc_v2, acc_speed_v2, score_types, is_t4)
    band_v1 = fc2mod.band_metrics(acc_v1, acc_speed_v1, score_types, is_t4)
    check = g0_check(band_v2, recorded_per_subtype)
    log(f"G0: v2 median DSI {band_v2['median_dsi_pooled']:.4f} (ref "
        f"{G0_DSI_REF} +/- {G0_DSI_TOL}), tiling exact "
        f"{check['tiling_exact']} -> pass={check['pass']} "
        f"({time.time() - t0:.1f}s)")
    return {"stable": True, "band_v2": band_v2, "band_v1_context": band_v1,
            "check": check, "elapsed_s": round(time.time() - t0, 1)}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="H-T4T5-NATSTAT-DIRECTION kill test (data-gated)")
    parser.add_argument("--image-root", type=Path, default=None,
                        help="directory with the frozen van Hateren subset "
                             "(imk00001.iml .. imk00060.iml)")
    parser.add_argument("--sintel-root", type=Path, default=None,
                        help="MPI-Sintel root (declared fallback corpus, "
                             "used only when --image-root is absent)")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()

    missing = check_prerequisites(args.image_root, args.sintel_root)
    if missing:
        print("BLOCKED -- the kill test cannot run here. Missing:")
        for item in missing:
            print(f"  - {item}")
        print("This is the measured cloud-container state; run on the "
              "machine that has the compiled runtime, the fc25 result and "
              "the corpus (docs/arenas/task10_menu/).")
        return EXIT_CODES["BLOCKED"]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    handle = open(args.output.with_suffix(".log"), "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    fc25 = _load_module("fc25_visual_ds", BENCH / "fc25_visual_ds.py")
    fc2 = fc25.load_fc2()
    # Frozen-machinery asserts (killtest_design.md section 5 preamble).
    assert fc2.DT_MS == 2.0 and fc2.SETTLE_MS == 2500.0
    assert abs(fc2.WINDOW_AFTER_S * 1000.0 - TAIL_MS) < 1e-9
    assert fc2.EDGE_MARGIN == TRAVEL_MARGIN_COL
    assert STIM_FRAME_MS % fc2.DT_MS == 0.0
    assert bk.IMAGE_SIZE == IMAGE_SIZE and bk.MID_GRAY == 0.5

    params = json.loads(PARAMS_JSON.read_text())
    fc25_results = json.loads(FC25_RESULTS.read_text())
    passing = next(c for c in fc25_results["configs"]
                   if c["label"] == "trained_subset")
    assert passing["result"]["readout_v2_crossing_window"]["pass"] is True, \
        "fc25 trained_subset no longer passes -- refuse to run"
    # ASSUMPTION (ANS-5, register row): the fc25 operating point
    # (chosen_gain, read verbatim here) is ASSUMED to transfer from
    # moving edges to translating natural movies. Checked by gate G1,
    # not assumed silently: if the drive convention cannot carry
    # direction at this gain, G1 fails and the run is BLOCKED as a
    # measured convention limit, never a statistics verdict.
    gain_real = passing["calibration"]["chosen_gain"]
    gain_twin = fc25_results["trivial_alternative"]["calibration"]["chosen_gain"]
    # AD-8 readout inputs, read VERBATIM from the fc25 results JSON (no
    # fitted parameters anywhere in the readout).
    recorded_per_subtype = \
        passing["result"]["readout_v2_crossing_window"]["per_subtype"]
    pref_of_subtype = {
        name: np.array(fc2.DIR_VECTORS[info["preferred"]])
        for name, info in recorded_per_subtype.items()
    }
    log(f"fc25 passing config: trained_subset gain={gain_real}; twin gain="
        f"{gain_twin}; preferred "
        f"{ {k: v['preferred'] for k, v in recorded_per_subtype.items()} }")

    # Patch + the ONE encoder instance (ANS-1): the identical AB-4
    # lattice/crop/assignment machinery for every arm and condition.
    patch = fc2.build_patch()
    types = patch["types"]
    patch["driven_mask"] = np.isin(types, fc2.DRIVEN_TYPES)
    driven_idx = np.flatnonzero(patch["driven_mask"])
    score_idx = np.flatnonzero(
        np.isin(types, fc2.T4_SUBTYPES + fc2.T5_SUBTYPES))
    score_types = types[score_idx]
    lattice = dk.build_lattice(patch["x"][driven_idx], patch["y"][driven_idx])
    mapping = dk.crop_mapping(lattice["col_x"], lattice["col_y"],
                              crop=IMAGE_SIZE)
    pixel_to_col = dk.assign_crop_pixels(lattice, mapping)
    n_cols = lattice["n_cols"]
    driven_cols = lattice["cell_col"]
    if n_cols != N_COLUMNS_EXPECTED:
        log(f"BLOCKED -- lattice has {n_cols} columns, the registration's "
            f"13x13 patch has {N_COLUMNS_EXPECTED}; instrument "
            f"precondition, not a verdict")
        return EXIT_CODES["BLOCKED"]
    pref_vec = np.stack([pref_of_subtype[t] for t in score_types])
    units_per_px = mapping["units_per_px"]
    extent = travel_extent(patch["x"], patch["y"])
    travel = extent + 2.0 * fc2.EDGE_MARGIN     # OP-7
    work_size = required_work_size(travel, units_per_px)
    log(f"patch: {patch['node_count']} cells; lattice {n_cols} columns; "
        f"{score_idx.size} scored T4/T5; travel {travel:.2f} col; "
        f"work size {work_size}px (units/px {units_per_px:.4f})")

    # Corpus (floor 6 + OP-2 integrity).
    entries, corpus_missing, source = resolve_corpus(args.image_root,
                                                     args.sintel_root)
    if corpus_missing:
        log("BLOCKED -- corpus incomplete. Missing:")
        for item in corpus_missing:
            log(f"  - {item}")
        return EXIT_CODES["BLOCKED"]
    checks = verify_checksums(entries, source)
    if checks["mismatches"]:
        log("BLOCKED -- corpus integrity (OP-2 pin violated):")
        for item in checks["mismatches"]:
            log(f"  - {item}")
        return EXIT_CODES["BLOCKED"]
    log(f"corpus: {source}, {len(entries)} images, checksums "
        f"{checks['status']} ({checks['lock_path']})")
    try:
        grays = [load_corpus_gray(e["path"]) for e in entries]
    except (ValueError, OSError) as exc:
        log(f"BLOCKED -- corpus unreadable (instrument statement): {exc}")
        return EXIT_CODES["BLOCKED"]

    # Contrast calibration (OP-4; CAL images only, drive level only).
    cal = calibrate_contrast([grays[i] for i in CAL_INDICES], pixel_to_col,
                             n_cols, work_size)
    if cal["chosen_gamma"] is None:
        log("BLOCKED -- degenerate CAL drive (no gamma yields nonzero "
            "p95 |drive|); corpus or encoder fault, not a verdict")
        return EXIT_CODES["BLOCKED"]
    gamma = cal["chosen_gamma"]
    log(f"contrast calibration: gamma={gamma} "
        f"(p95 |drive| {cal['chosen_p95_abs_drive']:.4f}, target "
        f"{CONTRAST_TARGET})")

    # Substrates + scramble (OP-5, OP-6, OP-15; floor 4 selftest).
    substrates = {"natural": [], "scrambled": []}
    integrity_rows = []
    for idx, gray in enumerate(grays):
        nat = make_substrate(gray, gamma, work_size)
        scr, integ = phase_scramble(nat, SCRAMBLE_SEED_BASE + idx)
        substrates["natural"].append(nat)
        substrates["scrambled"].append(scr)
        integrity_rows.append(integ)
    selftest = scramble_selftest(substrates["natural"][CAL_INDICES[0]],
                                 SCRAMBLE_SEED_BASE + CAL_INDICES[0])
    scramble_ok = bool(selftest["ok"]
                       and all(r["ok"] for r in integrity_rows))
    worst_rel = max(r["amplitude_rel_err"] for r in integrity_rows)
    log(f"scramble selftest: ok={scramble_ok} (worst amplitude rel err "
        f"{worst_rel:.2e}, selftest {selftest})")

    gates = {"scramble_integrity": scramble_ok, "g0": False, "g1": False}
    report: dict[str, Any] = {
        "hypothesis": HYPOTHESIS,
        "registration": REGISTRATION,
        "expected_tier_note": "base rate for score-adjacent expectations "
                              "0 for 16 (docs/arenas/SYNTHESIS.md); none "
                              "offered beyond it",
        "literature_anchor_nondecisional": (
            "correlator velocity estimation on translating van Hateren "
            "scenes: Dror, O'Carroll & Laughlin ~2001 (SOURCED, "
            "unverifiable from the cloud; registration section 5 names it "
            "as context only -- it decides nothing here)"),
        "corpus": {"source": source,
                   "ids": [e["id"] for e in entries],
                   "checksums": checks,
                   "cal_indices": list(CAL_INDICES),
                   "eval_indices": list(EVAL_INDICES),
                   "sourced_caveat": "corpus provenance is user-fetched and "
                                     "unverifiable from the cloud (SOURCED)"},
        "calibration": cal,
        "stimulus": {"speeds_col_per_s": SPEEDS,
                     "directions": DIRECTIONS_8,
                     "travel_col": travel,
                     "stim_frame_ms": STIM_FRAME_MS,
                     "tail_ms": TAIL_MS,
                     "work_size_px": work_size,
                     "units_per_px": units_per_px,
                     "scramble_seed_base": SCRAMBLE_SEED_BASE},
        "scramble": {"selftest": selftest,
                     "worst_amplitude_rel_err": worst_rel,
                     "out_of_range_fraction_max": max(
                         r["out_of_range_fraction"] for r in integrity_rows)},
        "gates": gates,
        "elapsed_s": None,
    }

    def finish(verdict_record: dict[str, Any]) -> int:
        report["verdict_record"] = verdict_record
        report["verdict"] = verdict_record["verdict"]
        report["elapsed_s"] = round(time.time() - started, 1)
        args.output.write_text(json.dumps(report, indent=2))
        log(f"VERDICT: {verdict_record['verdict']} "
            f"(floors: {verdict_record['floors']})")
        handle.close()
        return int(verdict_record["exit_code"])

    if not scramble_ok:
        return finish(assemble_verdict(None, gates, 0.0))

    # G0 (floor 2; cost-honest: before any natural-scene arm runs).
    table_real = fc25.trained_table(fc2, params, "subset", None)
    table_twin = fc25.trained_table(fc2, params, "subset", fc25.UNIFORM_TAU)
    real_matrix, coverage = fc25.trained_weight_matrix(
        fc2, patch, {p_: v["subset_mean"]
                     for p_, v in params["pairs"].items()})
    patch["matrix"] = real_matrix
    report["alpha_coverage"] = coverage
    g0 = g0_edge_reproduction(fc2, patch, pixel_to_col, n_cols, lattice,
                              mapping, table_real, gain_real, score_idx,
                              score_types, recorded_per_subtype, log)
    report["g0"] = g0
    gates["g0"] = bool(g0["check"]["pass"])
    if not gates["g0"]:
        return finish(assemble_verdict(None, gates, 0.0))

    # Eval items (frozen order: image major, then direction, then speed).
    items = [(img, di, si)
             for img in EVAL_INDICES
             for di in range(len(DIRECTIONS_8))
             for si in range(len(SPEEDS))]
    n_items = len(items)
    by_speed: dict[int, list[int]] = {si: [] for si in range(len(SPEEDS))}
    for pos, (_, _, si) in enumerate(items):
        by_speed[si].append(pos)
    log(f"eval items: {n_items} ({len(EVAL_INDICES)} images x "
        f"{len(DIRECTIONS_8)} directions x {len(SPEEDS)} speeds)")

    def build_drives(cond: str, si: int) -> np.ndarray:
        rows = []
        for pos in by_speed[si]:
            img, di, _ = items[pos]
            rows.append(translated_drives(
                substrates[cond][img], pixel_to_col, n_cols,
                DIR_VECTORS_8[DIRECTIONS_8[di]], SPEEDS[si], travel,
                units_per_px))
        return np.stack(rows)

    from flygi.connectome.nulls import degree_preserving_rewire
    arms: list[tuple[str, Any, Any, float]] = [
        ("real", real_matrix, table_real, gain_real),
        ("uniform_tau", real_matrix, table_twin, gain_twin),
    ]
    for s in REWIRE_SEEDS:
        rewired, _stats = degree_preserving_rewire(
            real_matrix, seed=REWIRE_SEED_BASE + s)
        arms.append((f"rewired_{s}", rewired, table_real, gain_real))
    arm_of = {a[0]: a for a in arms}

    errs: dict[str, dict[str, np.ndarray]] = {
        c: {a[0]: np.full(n_items, np.nan) for a in arms}
        for c in ("natural", "scrambled")}
    errs["natural"]["floor_frame_diff"] = np.full(n_items, np.nan)
    errs["scrambled"]["floor_frame_diff"] = np.full(n_items, np.nan)
    bads: dict[str, dict[str, np.ndarray]] = {
        c: {a[0]: np.zeros(n_items, dtype=bool) for a in arms}
        for c in ("natural", "scrambled")}
    drive_cache: dict[tuple[str, int], np.ndarray] = {}

    def run_arm(label: str, cond: str) -> None:
        _, matrix, table, gain = arm_of[label]
        for si in range(len(SPEEDS)):
            key = (cond, si)
            if key not in drive_cache:
                drive_cache[key] = build_drives(cond, si)
                # Trivial floor (OP-11): from the drives alone.
                for row, pos in enumerate(by_speed[si]):
                    img, di, _ = items[pos]
                    est = frame_difference_centroid(drive_cache[key][row],
                                                    lattice)
                    errs[cond]["floor_frame_diff"][pos] = angular_error_deg(
                        est, DIR_VECTORS_8[DIRECTIONS_8[di]])
            evoked, bad = simulate_items(
                fc2, matrix, types, table, gain, drive_cache[key],
                driven_idx, driven_cols, score_idx, log,
                f"{label}/{cond}/{SPEEDS[si]}colps")
            for row, pos in enumerate(by_speed[si]):
                img, di, _ = items[pos]
                bads[cond][label][pos] = bool(bad[row])
                if not bad[row]:
                    est = ad8_vote(evoked[row], pref_vec)
                    errs[cond][label][pos] = angular_error_deg(
                        est, DIR_VECTORS_8[DIRECTIONS_8[di]])

    # Cost-honest order: REAL natural first (feeds G1 and B1), G1 gate,
    # then rewires, then the scrambled condition, twin last (context).
    run_arm("real", "natural")
    g1 = g1_check(errs["natural"]["real"])
    report["g1"] = g1
    gates["g1"] = bool(g1["pass"])
    log(f"G1: median {g1['median_ae_deg']:.2f} deg vs {CHANCE_FLOOR_DEG} "
        f"(p {g1['sign_test_vs_chance']['p']:.2e}, n "
        f"{g1['n_evaluable']}) -> pass={g1['pass']}")
    if not gates["g1"]:
        frac = float(np.mean(bads["natural"]["real"]))
        return finish(assemble_verdict(None, gates, frac))

    for label in [f"rewired_{s}" for s in REWIRE_SEEDS]:
        run_arm(label, "natural")
    for label in ["real"] + [f"rewired_{s}" for s in REWIRE_SEEDS]:
        run_arm(label, "scrambled")
    run_arm("uniform_tau", "natural")
    run_arm("uniform_tau", "scrambled")

    # Floor 5: an unstable item drops from EVERY arm and is counted.
    # Decisional arms only define the drop set (OP-10).
    dropped = np.zeros(n_items, dtype=bool)
    for cond in ("natural", "scrambled"):
        for arm in DECISIONAL_ARMS:
            dropped |= bads[cond][arm]
    for cond in ("natural", "scrambled"):
        for arm in list(errs[cond]):
            errs[cond][arm][dropped] = np.nan
    unstable_fraction = float(dropped.mean())
    log(f"unstable items dropped from every arm: {int(dropped.sum())}/"
        f"{n_items} ({unstable_fraction:.3f})")

    def arm_summary(cond: str, arm: str) -> dict[str, Any]:
        e = errs[cond][arm]
        finite = np.isfinite(e)
        per_speed = {}
        for si, speed in enumerate(SPEEDS):
            idx = np.array(by_speed[si])
            sel = e[idx]
            per_speed[str(speed)] = (float(np.nanmedian(sel))
                                     if np.isfinite(sel).any()
                                     else float("nan"))
        return {"n_evaluable": int(finite.sum()),
                "median_ae_deg": (float(np.median(e[finite]))
                                  if finite.any() else float("nan")),
                "per_speed_median_ae_deg": per_speed}

    report["arms"] = {
        cond: {arm: arm_summary(cond, arm) for arm in errs[cond]}
        for cond in ("natural", "scrambled")}
    report["items"] = {"total_eval": n_items,
                       "unstable_dropped": int(dropped.sum()),
                       "unstable_fraction": unstable_fraction}

    decisional_errs = {
        cond: {arm: errs[cond][arm] for arm in DECISIONAL_ARMS}
        for cond in ("natural", "scrambled")}
    verdict_record = assemble_verdict(decisional_errs, gates,
                                      unstable_fraction)
    # Context, non-decisional: the twin and the trivial floor.
    verdict_record["context_nondecisional"] = {
        "uniform_tau_median_ae_natural":
            report["arms"]["natural"]["uniform_tau"]["median_ae_deg"],
        "uniform_tau_median_ae_scrambled":
            report["arms"]["scrambled"]["uniform_tau"]["median_ae_deg"],
        "floor_frame_diff_median_ae_natural":
            report["arms"]["natural"]["floor_frame_diff"]["median_ae_deg"],
        "floor_frame_diff_median_ae_scrambled":
            report["arms"]["scrambled"]["floor_frame_diff"]["median_ae_deg"],
    }
    return finish(verdict_record)


if __name__ == "__main__":
    sys.exit(main())
