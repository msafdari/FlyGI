#!/usr/bin/env python3
"""Task 2 (DSEC-Flow) -- connectome-independent metrics and baselines.

This is the half of the kill-test instrument that needs NO fly data and NO
event data, so it is built and verified first, in the cloud container, on
synthetic flow (docs/arenas/task2_dsec_flow/killtest_design.md; HANDOFF
next-step 1). Everything here is declared plumbing in the sense of the
first principle: metric definitions, the benchmark's file encoding, and
the trivial baselines the fly arm must be compared against. If any
intelligence ends up living in this file, that is a bug.

Contents:
  * EPE, 2D angular error (direction-only; the kill-rule metric), 3D
    angular error (the classic (u,v,1) form, context), and n-pixel
    outlier rates (1PE/2PE/3PE, EPE > n px over valid cells).
  * The DSEC/KITTI submission encoding and its exact inverse:
    16-bit 3-channel PNG, R = flow_x*128 + 2^15, G = flow_y*128 + 2^15,
    B = valid flag. The PNG codec is pure numpy + stdlib zlib (no
    imageio/cv2 dependency on the user's machine); the encoder writes
    filter-0 scanlines, the decoder handles all five PNG filters.
  * Trivial baselines that need only ground truth: zero flow and the
    GT-median global translation. (The event-count centroid-shift
    comparator needs event data and lives in dsec_killtest.py.)

Dependencies: numpy + Python stdlib only, deliberately.

Verify (no data needed):  python scripts/arenas/dsec_metrics.py --selftest
Tests:                    tests/test_dsec_metrics.py
"""

from __future__ import annotations

import struct
import zlib

import numpy as np

KITTI_SCALE = 128.0
KITTI_OFFSET = 2 ** 15


# ---------------------------------------------------------------------------
# Metrics. All take flow arrays shaped (..., 2) [x, y components in pixels]
# and an optional boolean valid mask shaped (...,); invalid cells are
# excluded from every statistic.
# ---------------------------------------------------------------------------

def _masked(est: np.ndarray, gt: np.ndarray, valid: np.ndarray | None):
    est = np.asarray(est, dtype=np.float64)
    gt = np.asarray(gt, dtype=np.float64)
    if est.shape != gt.shape or est.shape[-1] != 2:
        raise ValueError(f"flow shapes must match and end in 2: "
                         f"{est.shape} vs {gt.shape}")
    if valid is None:
        valid = np.ones(gt.shape[:-1], dtype=bool)
    valid = np.asarray(valid, dtype=bool)
    if valid.shape != gt.shape[:-1]:
        raise ValueError(f"valid shape {valid.shape} != {gt.shape[:-1]}")
    return est[valid], gt[valid]


def epe(est, gt, valid=None) -> np.ndarray:
    """Per-cell endpoint error over valid cells (1-D array)."""
    e, g = _masked(est, gt, valid)
    return np.linalg.norm(e - g, axis=-1)


def angular_error_2d(est, gt, valid=None, *, min_mag: float = 1e-9):
    """Per-cell angle in DEGREES between the 2D direction of est and gt,
    over valid cells where BOTH magnitudes exceed min_mag (direction is
    undefined at zero; the kill test's own magnitude gate is applied by
    the caller). Returns (angles, defined_fraction_of_valid)."""
    e, g = _masked(est, gt, valid)
    ne = np.linalg.norm(e, axis=-1)
    ng = np.linalg.norm(g, axis=-1)
    defined = (ne > min_mag) & (ng > min_mag)
    cos = np.full(e.shape[0], np.nan)
    cos[defined] = np.sum(e[defined] * g[defined], axis=-1) / (
        ne[defined] * ng[defined]
    )
    angles = np.degrees(np.arccos(np.clip(cos[defined], -1.0, 1.0)))
    frac = float(defined.mean()) if defined.size else float("nan")
    return angles, frac


def angular_error_3d(est, gt, valid=None) -> np.ndarray:
    """Classic optical-flow angular error: angle in degrees between
    (u, v, 1) vectors (Barron convention). Defined everywhere; context
    metric only."""
    e, g = _masked(est, gt, valid)
    e3 = np.concatenate([e, np.ones((e.shape[0], 1))], axis=-1)
    g3 = np.concatenate([g, np.ones((g.shape[0], 1))], axis=-1)
    cos = np.sum(e3 * g3, axis=-1) / (
        np.linalg.norm(e3, axis=-1) * np.linalg.norm(g3, axis=-1)
    )
    return np.degrees(np.arccos(np.clip(cos, -1.0, 1.0)))


def outlier_rates(est, gt, valid=None,
                  thresholds=(1.0, 2.0, 3.0)) -> dict[str, float]:
    """DSEC-board n-pixel outlier rates: fraction of valid cells whose
    EPE exceeds n px, for n in thresholds."""
    err = epe(est, gt, valid)
    if err.size == 0:
        return {f"{int(t)}PE": float("nan") for t in thresholds}
    return {f"{int(t)}PE": float((err > t).mean()) for t in thresholds}


def summarize(est, gt, valid=None) -> dict[str, float]:
    """The full context table for one arm: EPE mean/median, outlier
    rates, AE3D mean, AE2D mean/median + defined fraction."""
    err = epe(est, gt, valid)
    ae2, frac2 = angular_error_2d(est, gt, valid)
    ae3 = angular_error_3d(est, gt, valid)
    def _m(a, f):  # noqa: E306
        return float(f(a)) if a.size else float("nan")
    out = {
        "epe_mean": _m(err, np.mean), "epe_median": _m(err, np.median),
        "ae2d_mean_deg": _m(ae2, np.mean),
        "ae2d_median_deg": _m(ae2, np.median),
        "ae2d_defined_fraction": frac2,
        "ae3d_mean_deg": _m(ae3, np.mean),
        "n_valid": int(err.size),
    }
    out.update(outlier_rates(est, gt, valid))
    return out


# ---------------------------------------------------------------------------
# DSEC/KITTI flow PNG encoding (16-bit, 3-channel, big-endian per PNG spec)
# ---------------------------------------------------------------------------

def flow_to_kitti_uint16(flow: np.ndarray,
                         valid: np.ndarray | None = None) -> np.ndarray:
    """(H, W, 2) float flow [+ optional (H, W) valid] -> (H, W, 3) uint16
    in the benchmark encoding. Values are rounded to the format's 1/128 px
    quantum and clipped to the representable range; invalid cells are
    zeroed as KITTI does."""
    flow = np.asarray(flow, dtype=np.float64)
    h, w, two = flow.shape
    if two != 2:
        raise ValueError("flow must be (H, W, 2)")
    if valid is None:
        valid = np.ones((h, w), dtype=bool)
    valid = np.asarray(valid, dtype=bool)
    img = np.zeros((h, w, 3), dtype=np.uint16)
    coded = np.clip(np.round(flow * KITTI_SCALE + KITTI_OFFSET), 0, 65535)
    img[..., 0] = np.where(valid, coded[..., 0].astype(np.uint16), 0)
    img[..., 1] = np.where(valid, coded[..., 1].astype(np.uint16), 0)
    img[..., 2] = valid.astype(np.uint16)
    return img


def kitti_uint16_to_flow(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Exact inverse of flow_to_kitti_uint16 up to the 1/128 px quantum.
    Returns (flow (H, W, 2) float64, valid (H, W) bool)."""
    img = np.asarray(img)
    if img.ndim != 3 or img.shape[-1] != 3 or img.dtype != np.uint16:
        raise ValueError("expected (H, W, 3) uint16")
    valid = img[..., 2] > 0
    flow = (img[..., :2].astype(np.float64) - KITTI_OFFSET) / KITTI_SCALE
    flow[~valid] = 0.0
    return flow, valid


def _png_chunk(tag: bytes, payload: bytes) -> bytes:
    crc = zlib.crc32(tag + payload) & 0xFFFFFFFF
    return struct.pack(">I", len(payload)) + tag + payload + struct.pack(">I", crc)


_PNG_SIG = b"\x89PNG\r\n\x1a\n"


def encode_png_16bit_rgb(img: np.ndarray, *, filter_type: int = 0) -> bytes:
    """Minimal PNG writer for (H, W, 3) uint16 (bit depth 16, color type 2).
    filter_type (0..4) applies one PNG filter to every scanline; the
    default 0 is what submissions use -- the other types exist so the
    decoder's un-filter paths are testable against our own encoder."""
    img = np.asarray(img)
    if img.ndim != 3 or img.shape[-1] != 3 or img.dtype != np.uint16:
        raise ValueError("expected (H, W, 3) uint16")
    if filter_type not in (0, 1, 2, 3, 4):
        raise ValueError("filter_type must be 0..4")
    h, w, _ = img.shape
    raw = img.astype(">u2").tobytes()
    stride = w * 6                       # 3 channels x 2 bytes
    bpp = 6
    lines = []
    prior = np.zeros(stride, dtype=np.int32)
    for r in range(h):
        row = np.frombuffer(
            raw[r * stride:(r + 1) * stride], dtype=np.uint8
        ).astype(np.int32)
        left = np.concatenate([np.zeros(bpp, np.int32), row[:-bpp]])
        up_left = np.concatenate([np.zeros(bpp, np.int32), prior[:-bpp]])
        if filter_type == 0:
            filt = row
        elif filter_type == 1:
            filt = row - left
        elif filter_type == 2:
            filt = row - prior
        elif filter_type == 3:
            filt = row - (left + prior) // 2
        else:                            # 4: Paeth
            p = left + prior - up_left
            pa, pb, pc = (np.abs(p - left), np.abs(p - prior),
                          np.abs(p - up_left))
            pred = np.where((pa <= pb) & (pa <= pc), left,
                            np.where(pb <= pc, prior, up_left))
            filt = row - pred
        lines.append(bytes([filter_type]) + (filt % 256).astype(np.uint8).tobytes())
        prior = row
    ihdr = struct.pack(">IIBBBBB", w, h, 16, 2, 0, 0, 0)
    idat = zlib.compress(b"".join(lines), 6)
    return (_PNG_SIG + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IDAT", idat)
            + _png_chunk(b"IEND", b""))


def decode_png_16bit_rgb(data: bytes) -> np.ndarray:
    """Minimal PNG reader for the files encode_png_16bit_rgb writes (and
    any non-interlaced 16-bit RGB PNG): parses IHDR, concatenates IDAT,
    reverses all five scanline filters. Returns (H, W, 3) uint16."""
    if data[:8] != _PNG_SIG:
        raise ValueError("not a PNG")
    pos, w = 8, None
    idat = b""
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        payload = data[pos + 8:pos + 8 + length]
        pos += 12 + length
        if tag == b"IHDR":
            w, h, depth, color, comp, filt, interlace = struct.unpack(
                ">IIBBBBB", payload
            )
            if (depth, color, comp, filt, interlace) != (16, 2, 0, 0, 0):
                raise ValueError(
                    f"unsupported PNG layout: depth={depth} color={color} "
                    f"interlace={interlace} (need 16-bit RGB, no interlace)"
                )
        elif tag == b"IDAT":
            idat += payload
        elif tag == b"IEND":
            break
    if w is None:
        raise ValueError("missing IHDR")
    raw = zlib.decompress(idat)
    stride = w * 6
    bpp = 6
    if len(raw) != h * (stride + 1):
        raise ValueError("PNG data length mismatch")
    out = np.zeros((h, stride), dtype=np.uint8)
    prior = np.zeros(stride, dtype=np.int32)
    for r in range(h):
        line = raw[r * (stride + 1):(r + 1) * (stride + 1)]
        ftype = line[0]
        row = np.frombuffer(line[1:], dtype=np.uint8).astype(np.int32)
        if ftype == 0:
            recon = row
        elif ftype == 2:
            recon = (row + prior) % 256
        elif ftype in (1, 3, 4):
            recon = np.zeros(stride, dtype=np.int32)
            for i in range(stride):
                left = recon[i - bpp] if i >= bpp else 0
                up = prior[i]
                up_left = prior[i - bpp] if i >= bpp else 0
                if ftype == 1:
                    pred = left
                elif ftype == 3:
                    pred = (left + up) // 2
                else:
                    p = left + up - up_left
                    pa, pb, pc = abs(p - left), abs(p - up), abs(p - up_left)
                    pred = (left if pa <= pb and pa <= pc
                            else up if pb <= pc else up_left)
                recon[i] = (row[i] + pred) % 256
        else:
            raise ValueError(f"unknown PNG filter {ftype}")
        out[r] = recon.astype(np.uint8)
        prior = recon
    return (
        np.frombuffer(out.tobytes(), dtype=">u2")
        .reshape(h, w, 3).astype(np.uint16)
    )


def write_flow_png(path, flow, valid=None) -> None:
    with open(path, "wb") as f:
        f.write(encode_png_16bit_rgb(flow_to_kitti_uint16(flow, valid)))


def read_flow_png(path) -> tuple[np.ndarray, np.ndarray]:
    with open(path, "rb") as f:
        return kitti_uint16_to_flow(decode_png_16bit_rgb(f.read()))


# ---------------------------------------------------------------------------
# Trivial baselines that need only ground truth
# ---------------------------------------------------------------------------

def zero_flow_baseline(gt, valid=None) -> dict[str, float]:
    """TRIVIAL-1: predict zero everywhere. Direction undefined, so this
    is EPE/outlier context only (killtest_design.md)."""
    return summarize(np.zeros_like(np.asarray(gt, dtype=np.float64)),
                     gt, valid)


def global_translation_baseline(gt, valid=None) -> tuple[dict, np.ndarray]:
    """TRIVIAL-2: one vector for the whole field = per-component median
    of valid GT (oracle context -- it reads GT; killtest_design.md).
    Returns (summary, the constant vector)."""
    gt_arr = np.asarray(gt, dtype=np.float64)
    _, g = _masked(gt_arr, gt_arr, valid)
    vec = (np.median(g, axis=0) if g.size
           else np.zeros(2))
    est = np.broadcast_to(vec, gt_arr.shape).copy()
    return summarize(est, gt_arr, valid), vec


# ---------------------------------------------------------------------------
# Self-test on synthetic flow (the in-cloud verification, HANDOFF step 1)
# ---------------------------------------------------------------------------

def selftest() -> int:
    rng = np.random.default_rng(0)
    checks: list[tuple[str, bool, str]] = []

    def check(name, ok, detail=""):
        checks.append((name, bool(ok), detail))
        print(f"  [{'ok' if ok else 'FAIL'}] {name} {detail}")

    # EPE: zero estimate vs constant GT field.
    gt = np.zeros((40, 60, 2))
    gt[..., 0] = 3.0
    gt[..., 1] = -4.0
    err = epe(np.zeros_like(gt), gt)
    check("epe constant field", np.allclose(err, 5.0), f"epe={err.mean():.3f}")

    # AE2D: 90-degree rotated estimate.
    est = np.zeros_like(gt)
    est[..., 0] = 4.0
    est[..., 1] = 3.0
    ang, frac = angular_error_2d(est, gt)
    check("ae2d orthogonal", np.allclose(ang, 90.0) and frac == 1.0,
          f"ae2d={ang.mean():.2f}deg defined={frac:.2f}")

    # Outlier rates with a half-field 4 px error.
    est2 = gt.copy()
    est2[:20, :, 0] += 4.0
    rates = outlier_rates(est2, gt)
    check("outlier rates", abs(rates["3PE"] - 0.5) < 1e-12
          and abs(rates["1PE"] - 0.5) < 1e-12, str(rates))

    # KITTI round trip, every filter type, negatives + invalid cells.
    flow = rng.uniform(-200, 200, size=(31, 47, 2))
    valid = rng.random((31, 47)) > 0.2
    ok_all = True
    for ftype in range(5):
        png = encode_png_16bit_rgb(flow_to_kitti_uint16(flow, valid),
                                   filter_type=ftype)
        back, vback = kitti_uint16_to_flow(decode_png_16bit_rgb(png))
        ok = (np.array_equal(valid, vback)
              and np.max(np.abs(back[valid] - flow[valid])) <= 0.5 / KITTI_SCALE
              and np.all(back[~valid] == 0.0))
        ok_all &= ok
    check("kitti png round trip (filters 0-4)", ok_all,
          f"quantum={1 / KITTI_SCALE:.5f}px")

    # Baselines on a uniform-translation field + noise: global translation
    # must beat zero flow; zero-flow EPE must equal mean |gt|.
    gt3 = np.broadcast_to(np.array([6.0, -2.0]), (50, 50, 2)).copy()
    gt3 += rng.normal(0, 0.3, size=gt3.shape)
    z = zero_flow_baseline(gt3)
    g, vec = global_translation_baseline(gt3)
    check("zero-flow epe = mean |gt|",
          abs(z["epe_mean"] - np.linalg.norm(gt3, axis=-1).mean()) < 1e-9,
          f"epe={z['epe_mean']:.3f}")
    check("global translation beats zero flow",
          g["epe_mean"] < z["epe_mean"],
          f"{g['epe_mean']:.3f} < {z['epe_mean']:.3f}, vec={vec.round(2)}")

    failed = [c for c in checks if not c[1]]
    print(f"selftest: {len(checks) - len(failed)}/{len(checks)} checks pass")
    return 1 if failed else 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--selftest", action="store_true")
    if parser.parse_args().selftest:
        raise SystemExit(selftest())
    parser.error("this module is a library; run with --selftest to verify")
