#!/usr/bin/env python3
"""Which EPG grouping does the source paper's own figure use? A
read-only check for assumption AC-B1a (the compass map amendment of
2026-11-21, docs/arenas/compass_map_amendment_20261121.md).

WHY THIS EXISTS. Biswas et al. (bioRxiv 10.1101/2024.11.01.621596v2)
never say which left and right bridge glomeruli share one of their
eight ring units. Their Fig. 1g prints the 88 x 88 EPG + Delta7
synapse-count matrix of the male CNS dataset with thin grey lines
between units. That figure is the only published record of their
grouping, and it can be read without touching any fitted value.

WHAT IT DOES, on a rendered image of the panel.
  1. Finds the matrix frame and the thin separator lines, and reports
     the unit sizes (how many neurons sit between consecutive lines).
  2. Reads the darkness of each of the 46 x 46 EPG cells (darkness is
     linear in count on the figure's colour bar).
  3. Builds, from OUR compiled MaleCNS counts, the mean count between
     every pair of the sixteen EPG labels (L1..L8, R1..R8).
  4. For every hypothesis about how the figure orders the 46 EPG
     cells -- every left-right matching whose unit sizes equal the
     figure's, units listed in right-glomerulus order or in
     left-glomerulus order, either label first inside a unit -- it
     predicts each label-pair block of the figure from our counts and
     scores the fit (root-mean-square error in grey levels after one
     least-squares scale). Cells of one label are interchangeable, so
     block means are compared, never single cells.

READING. If exactly one hypothesis fits far better than every other,
the figure identifies both the ring order of the EPG cells and which
labels share a unit. The trivial alternatives are the registered
grouping (L_k with R_k), which is not even size-compatible, and the
other neighbour pairing (L_k with R_(10-k)), which is not either.

It is not a registered instrument and carries no verdict. It reads
the compiled runtime and an image, prints, and writes a small JSON.

The image is NOT in the repository. The record of 2026-11-21 used
page 2 of the version-2 PDF rendered 7,200 pixels wide and cropped to
panel g (1,560 x 1,500 pixels, SHA-256 1a988e38...01f97; a local copy
is kept under results/arenas/compass_amendment_20261121/). Any crop
that contains the whole matrix frame, with no other long dark line
to its left or above it, will do.

Run:    python scripts/arenas/biswas_fig1g_check.py --image <panel.png>
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from flygi.compass_map import (  # noqa: E402
    RING_MAPS, parse_label, ring_index, ring_label, ring_unit)

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
OUT_JSON = ROOT / "results/arenas/biswas_fig1g_check.json"
TYPE_PATTERNS = ("EPG", "PEN_a*", "PEN_b*", "Delta7", "PEG")
N_CELLS = 88
N_EPG = 46
LABELS = [f"R{k}" for k in range(1, 9)] + [f"L{k}" for k in range(1, 9)]


def find_frame(gray: np.ndarray) -> tuple[float, float, float, float]:
    """The square matrix frame: the first long dark column and row, and
    the dark column / row that closes a square with them."""
    h, w = gray.shape
    dark = gray < 60
    cols = np.flatnonzero(dark.sum(axis=0) > 0.6 * h)
    rows = np.flatnonzero(dark.sum(axis=1) > 0.5 * w)
    if cols.size < 2 or rows.size < 2:
        raise ValueError("matrix frame not found in the image")
    x0, y0 = float(cols[0]), float(rows[0])
    y1 = float(rows[-1])
    side = y1 - y0
    x1 = float(cols[np.argmin(np.abs(cols - (x0 + side)))])
    return x0 + 0.5, x1 + 0.5, y0 + 0.5, y1


def separators(gray: np.ndarray, frame, axis: str) -> list[float]:
    """Thin grey separator lines, in cell units, along one axis."""
    x0, x1, y0, y1 = frame
    if axis == "x":
        a, lo, hi = gray[int(y0) + 2:int(y1) - 1, :], x0, x1
    else:
        a, lo, hi = gray[:, int(x0) + 2:int(x1) - 1].T, y0, y1
    cell = (hi - lo) / N_CELLS
    score = np.zeros(a.shape[1])
    for x in range(4, a.shape[1] - 4):
        side = np.minimum(a[:, x - 3], a[:, x + 3])
        score[x] = np.mean((side - a[:, x]) > 4.0)
    found = [x for x in range(int(lo) + 3, int(hi) - 3)
             if score[x] > 0.30 and score[x] >= score[x - 1]
             and score[x] >= score[x + 1]]
    return [(x - lo) / cell for x in found]


def cell_darkness(gray: np.ndarray, frame) -> np.ndarray:
    """88 x 88 darkness (255 - median grey of a 7 x 7 patch at each cell
    centre). Rows are the figure's y axis (pre), columns its x axis
    (post)."""
    x0, x1, y0, y1 = frame
    cx, cy = (x1 - x0) / N_CELLS, (y1 - y0) / N_CELLS
    out = np.zeros((N_CELLS, N_CELLS))
    for r in range(N_CELLS):
        for c in range(N_CELLS):
            xc = int(round(x0 + (c + 0.5) * cx))
            yc = int(round(y0 + (r + 0.5) * cy))
            out[r, c] = 255.0 - np.median(gray[yc - 3:yc + 4, xc - 3:xc + 4])
    return out


def unit_sizes_from(seps: list[float]) -> tuple[list[int], float]:
    """Unit sizes from separator positions, and the largest distance of
    a separator from an integer cell boundary."""
    bounds = [0] + [int(round(s)) for s in seps] + [N_CELLS]
    worst = max((abs(s - round(s)) for s in seps), default=0.0)
    return [b - a for a, b in zip(bounds, bounds[1:])], worst


def fit_rms(sequence: list[str], cells_per_label: dict[str, int],
            table: np.ndarray, figure_epg: np.ndarray) -> float:
    """RMS error (grey levels) of the figure's label-pair block means
    against our mean counts, for one ordering of the 46 EPG cells.
    table[post, pre] holds summed counts in LABELS order."""
    order: list[str] = []
    for lab in sequence:
        order += [lab] * cells_per_label[lab]
    where = {lab: [i for i, x in enumerate(order) if x == lab]
             for lab in LABELS}
    pred, obs = [], []
    for post in LABELS:
        for pre in LABELS:
            n = cells_per_label[post] * cells_per_label[pre]
            block = figure_epg[np.ix_(where[pre], where[post])]
            if post == pre:
                n -= cells_per_label[post]
                block = block[~np.eye(cells_per_label[post], dtype=bool)]
            pred.append(table[LABELS.index(post), LABELS.index(pre)] / n)
            obs.append(float(block.mean()))
    pred, obs = np.asarray(pred), np.asarray(obs)
    scale = (pred @ obs) / (pred @ pred)
    return float(np.sqrt(np.mean((obs - scale * pred) ** 2)))


def hypotheses(cells_per_label: dict[str, int], target: list[int]):
    """Every size-compatible ordering: a left-right matching, units in
    right order or in left order, either label first inside a unit."""
    for first, other in (("R", "L"), ("L", "R")):
        for sigma in itertools.permutations(range(1, 9)):
            sizes = [cells_per_label[f"{first}{k}"]
                     + cells_per_label[f"{other}{sigma[k - 1]}"]
                     for k in range(1, 9)]
            if sizes != target:
                continue
            for lead in (True, False):
                seq: list[str] = []
                for k in range(1, 9):
                    a, b = f"{first}{k}", f"{other}{sigma[k - 1]}"
                    seq += [a, b] if lead else [b, a]
                yield seq


def named_orderings() -> dict[str, list[str]]:
    """The orderings each named ring map implies, for labelling rows of
    the output: cells in ring order, cut into that map's units."""
    out = {}
    for ring_map in RING_MAPS:
        cells = [(s, k) for s in "LR" for k in range(1, 9)]
        # the ring position at which unit 0 starts (1 for the amended
        # map, whose first unit is positions 1 and 2; 0 for the
        # registered one), so a unit that straddles position 15 -> 0
        # keeps its ring order
        start = next(o for o in range(16) if all(
            ring_unit(s, k, ring_map)
            == ((ring_index(s, k, ring_map) - o) % 16) // 2
            for s, k in cells))
        ordered = sorted(cells, key=lambda c: (
            ring_index(c[0], c[1], ring_map) - start) % 16)
        out[ring_map] = [f"{s}{k}" for s, k in ordered]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--image", type=Path, required=True,
                        help="PNG crop of Biswas et al. v2 Fig. 1g")
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()
    if not RUNTIME_DIR.exists():
        print(f"BLOCKED: compiled MaleCNS runtime absent: {RUNTIME_DIR}")
        return 3
    try:
        from PIL import Image
    except ImportError:
        print("BLOCKED: python package Pillow is needed to read the image")
        return 3

    started = time.time()
    digest = hashlib.sha256(args.image.read_bytes()).hexdigest()
    rgba = Image.open(args.image).convert("RGBA")
    white = Image.new("RGBA", rgba.size, (255, 255, 255, 255))
    gray = np.asarray(Image.alpha_composite(white, rgba).convert("L"),
                      dtype=float)
    frame = find_frame(gray)
    print(f"image {args.image.name} {gray.shape[1]}x{gray.shape[0]} "
          f"sha256 {digest[:16]}...; matrix frame x {frame[0]:.1f}.."
          f"{frame[1]:.1f}, y {frame[2]:.1f}..{frame[3]:.1f}")

    seps_x = separators(gray, frame, "x")
    seps_y = separators(gray, frame, "y")
    sizes_x, worst_x = unit_sizes_from(seps_x)
    sizes_y, worst_y = unit_sizes_from(seps_y)
    print(f"separators (cells), x: {[round(s, 2) for s in seps_x]}")
    print(f"separators (cells), y: {[round(s, 2) for s in seps_y]}")
    if sizes_x != sizes_y or len(sizes_x) != 16:
        print("BLOCKED: the two axes disagree or do not show 16 units; "
              f"x {sizes_x}, y {sizes_y}")
        return 3
    epg_sizes, d7_sizes = sizes_x[:8], sizes_x[8:]
    print(f"figure unit sizes: EPG {epg_sizes} (sum {sum(epg_sizes)}), "
          f"Delta7 {d7_sizes} (sum {sum(d7_sizes)}); largest distance of "
          f"a line from a cell boundary {max(worst_x, worst_y):.2f} cells")
    if sum(epg_sizes) != N_EPG:
        print("BLOCKED: the first eight units do not hold 46 cells")
        return 3
    figure_epg = cell_darkness(gray, frame)[:N_EPG, :N_EPG]

    from flygi.connectome.subcircuit import extract_subcircuit, select_nodes
    sub = extract_subcircuit(RUNTIME_DIR,
                             select_nodes(RUNTIME_DIR,
                                          type_patterns=TYPE_PATTERNS))
    types = sub.types.astype("U")
    instances = sub.instances.astype("U")
    epg = np.flatnonzero(types == "EPG")
    parsed = [parse_label(instances[i]) for i in epg]
    labels = [f"{p[0]}{p[1]}" for p in parsed]
    if any(lab not in LABELS for lab in labels):
        print("BLOCKED: an EPG label does not parse to L1..L8 / R1..R8")
        return 3
    cells_per_label = {lab: labels.count(lab) for lab in LABELS}
    counts = np.abs(np.asarray(sub.matrix[np.ix_(epg, epg)].todense(),
                               dtype=np.float64))
    table = np.zeros((16, 16))
    for a, post in enumerate(LABELS):
        rows = [i for i, lab in enumerate(labels) if lab == post]
        for b, pre in enumerate(LABELS):
            cols = [i for i, lab in enumerate(labels) if lab == pre]
            table[a, b] = counts[np.ix_(rows, cols)].sum()

    named = named_orderings()
    regular = {}
    for ring_map, seq in named.items():
        sizes = [cells_per_label[seq[2 * u]] + cells_per_label[seq[2 * u + 1]]
                 for u in range(8)]
        regular[ring_map] = {"ordering": " ".join(seq), "unit_sizes": sizes,
                             "size_compatible": sizes == epg_sizes}
        print(f"{ring_map:10s} map: units {sizes} -> "
              f"{'matches' if sizes == epg_sizes else 'does NOT match'} "
              f"the figure's EPG unit sizes")

    scored = sorted((fit_rms(seq, cells_per_label, table, figure_epg),
                     " ".join(seq))
                    for seq in hypotheses(cells_per_label, epg_sizes))
    print(f"\nhypotheses scored: {len(scored)} (every size-compatible "
          "left-right matching, units in R order or L order, either "
          "label first)")
    for rms, seq in scored[:5]:
        tag = [f"the {name} map" for name, s in named.items()
               if " ".join(s) == seq]
        tag += [f"the {name} map read backwards" for name, s in named.items()
                if " ".join(reversed(s)) == seq]
        print(f"  rms {rms:6.2f} grey levels  {seq}"
              + (f"   <- {tag[0]}" if tag else ""))
    print(f"  ... worst rms {scored[-1][0]:.2f}")
    best, second = scored[0], scored[1]
    amended_units = sorted(
        tuple(sorted(lab for lab in LABELS
                     if ring_unit(lab[0], int(lab[1:]), "amended") == u))
        for u in range(8))
    best_seq = best[1].split()
    best_units = sorted(tuple(sorted(best_seq[2 * u:2 * u + 2]))
                        for u in range(8))
    ring_now = [("%s%d" % ring_label(i, "amended")) for i in range(16)]
    doubled = ring_now + ring_now
    reverse = list(reversed(ring_now)) * 2
    is_ring = any(doubled[i:i + 16] == best_seq or reverse[i:i + 16] == best_seq
                  for i in range(16))
    print(f"\nbest ordering's units equal the amended units: "
          f"{best_units == amended_units}; best ordering is the amended "
          f"ring order (up to rotation and direction): {is_ring}; "
          f"margin to the runner-up: {second[0] / max(best[0], 1e-9):.1f}x")

    record = {"image": args.image.name, "image_sha256": digest,
              "frame": frame, "separators_x": seps_x, "separators_y": seps_y,
              "figure_epg_unit_sizes": epg_sizes,
              "figure_delta7_unit_sizes": d7_sizes,
              "cells_per_label": cells_per_label,
              "named_maps": regular,
              "n_hypotheses": len(scored),
              "ranking_top": [{"rms_grey": r, "ordering": s}
                              for r, s in scored[:10]],
              "worst_rms_grey": scored[-1][0],
              "best_units_equal_amended_units": best_units == amended_units,
              "best_is_amended_ring_order": bool(is_ring),
              "elapsed_s": round(time.time() - started, 1)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2))
    print(f"wrote {args.output} ({record['elapsed_s']} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
