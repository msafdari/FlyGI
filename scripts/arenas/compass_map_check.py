#!/usr/bin/env python3
"""Does a compass label map agree with the wiring? A read-only check.

WHY THIS EXISTS (2026-11-21, the compass map amendment,
docs/arenas/compass_map_amendment_20261121.md). Nine compass
instruments placed EPG cells on the ellipsoid-body ring from their
bridge labels, and none of them ever compared that placement with the
connectome. Their validation gates could not: each gate built its
synthetic ring with the inverse of the instrument's own map, so it
passed under any map. This script is the comparison that was missing,
and it is the amended map's test against its trivial alternatives:

  the REGISTERED map (AC-1 as frozen 2026-10-10), and
  RANDOM maps (the sixteen half-wedge labels dealt onto the sixteen
  ring positions at random, seeded).

STATISTIC (declared here, before the amended instruments ran). Take
the direct EPG -> EPG synapse counts between different half-wedges
(the same-half-wedge mass is the same under every map and is left
out). Under a map, each ordered pair of half-wedges sits at a circular
ring distance 1..8. The statistic is the share of that count at
distance 1 (nearest neighbours), also reported cumulatively to
distance 2. A map that follows the ring concentrates count at short
distance.

WHAT THE CHECK ASSUMES, and what carries it. ESTABLISHED for the
ellipsoid body: EPG cells contact their neighbours there (Turner-Evans
et al. 2020, Neuron 108:145, Results; Hulse et al. 2021, eLife
10:e66039, Fig. 17Ci). The counts used here are WHOLE-NEURON counts,
bridge and gall included. That does not weaken the check, for a reason
worth stating: two cells of the SAME bridge half sit at the same ring
distance under both maps (the amendment reflects the left half as a
whole), so same-side count cannot tell the maps apart. Everything
that distinguishes them is CROSS-SIDE count, and left and right EPG
arbors meet only in the ellipsoid body. The cross-side share is
therefore reported on its own as well.

WHAT IT IS NOT. It is not a registered instrument and carries no
verdict. The amended map was NOT chosen by maximising this statistic:
it is the published anatomical order (module docstring of
flygi.compass_map). This check asks whether the MaleCNS
labels follow that published order, which is the one ASSUMPTION the
amended map still carries.

Read-only: reads the compiled runtime, prints, and writes a small JSON
only where --output says (default results/arenas/compass_map_check.json,
git-ignored).

Run:    python scripts/arenas/compass_map_check.py
"""

from __future__ import annotations

import argparse
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
    N_RING, RING_MAP_DESCRIPTION, RING_MAPS, parse_label, ring_index)

RUNTIME_DIR = ROOT / "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
OUT_JSON = ROOT / "results/arenas/compass_map_check.json"
TYPE_PATTERNS = ("EPG", "PEN_a*", "PEN_b*", "Delta7", "PEG")
N_RANDOM_MAPS = 10000
RANDOM_SEED = 20261121
LABELS = [(side, k) for side in ("L", "R") for k in range(1, 9)]


def label_count_matrix(counts: np.ndarray, labels: list) -> np.ndarray:
    """16x16 summed |count| between half-wedge labels, [post, pre],
    rows and columns in LABELS order."""
    out = np.zeros((len(LABELS), len(LABELS)))
    where = {lab: [i for i, l in enumerate(labels) if l == lab]
             for lab in LABELS}
    for a, post in enumerate(LABELS):
        for b, pre in enumerate(LABELS):
            if where[post] and where[pre]:
                out[a, b] = counts[np.ix_(where[post], where[pre])].sum()
    return out


def distance_shares(G: np.ndarray, position: np.ndarray,
                    cross_side_only: bool = False) -> np.ndarray:
    """Share of the off-diagonal label-to-label count at each circular
    ring distance 1..8, given each label's ring position. With
    cross_side_only, only pairs of one left and one right label."""
    shares = np.zeros(N_RING // 2 + 1)
    n = len(position)
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            if cross_side_only and LABELS[a][0] == LABELS[b][0]:
                continue
            d = min((position[a] - position[b]) % N_RING,
                    (position[b] - position[a]) % N_RING)
            shares[d] += G[a, b]
    total = shares.sum()
    return shares / total if total > 0 else shares


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--output", type=Path, default=OUT_JSON)
    args = parser.parse_args()
    if not RUNTIME_DIR.exists():
        print(f"BLOCKED: compiled MaleCNS runtime absent: {RUNTIME_DIR}")
        return 3

    started = time.time()
    from flygi.connectome.subcircuit import extract_subcircuit, select_nodes
    sub = extract_subcircuit(RUNTIME_DIR,
                             select_nodes(RUNTIME_DIR,
                                          type_patterns=TYPE_PATTERNS))
    types = sub.types.astype("U")
    instances = sub.instances.astype("U")
    epg = np.flatnonzero(types == "EPG")
    labels = [parse_label(instances[i]) for i in epg]
    if any(lab is None or lab not in LABELS for lab in labels):
        print("BLOCKED: an EPG label does not parse to L1..L8 / R1..R8")
        return 3
    counts = np.abs(np.asarray(sub.matrix[np.ix_(epg, epg)].todense(),
                               dtype=np.float64))
    G = label_count_matrix(counts, labels)
    per_label = {f"{s}{k}": sum(1 for l in labels if l == (s, k))
                 for s, k in LABELS}
    print(f"EPG cells {epg.size}; cells per half-wedge {per_label}")
    print(f"direct EPG->EPG count {counts.sum():.0f}, of which between "
          f"different half-wedges {G.sum() - np.trace(G):.0f}")

    print("\nWhere each LEFT half-wedge's cross-side synapses go "
          "(pre L_k -> post R_j, summed counts), and which two right "
          "half-wedges each map puts beside it:")
    left_table = {}
    for k in range(1, 9):
        col = LABELS.index(("L", k))
        to_right = {j: float(G[LABELS.index(("R", j)), col])
                    for j in range(1, 9)}
        top = sorted(to_right, key=to_right.get, reverse=True)[:2]
        beside = {}
        for ring_map in RING_MAPS:
            here = ring_index("L", k, ring_map)
            beside[ring_map] = sorted(
                j for j in range(1, 9)
                if min((ring_index("R", j, ring_map) - here) % N_RING,
                       (here - ring_index("R", j, ring_map)) % N_RING) == 1)
        left_table[f"L{k}"] = {
            "to_right_counts": to_right, "top_two": top, "beside": beside}
        print(f"  L{k}: most to R{top[0]} ({to_right[top[0]]:.0f}) and "
              f"R{top[1]} ({to_right[top[1]]:.0f}); to R{k} "
              f"{to_right[k]:.0f} | amended map puts it beside "
              f"R{beside['amended']}, registered beside "
              f"R{beside['registered']}")

    rng = np.random.default_rng(RANDOM_SEED)
    random_d1 = np.empty(N_RANDOM_MAPS)
    random_d2 = np.empty(N_RANDOM_MAPS)
    for r in range(N_RANDOM_MAPS):
        shares = distance_shares(G, rng.permutation(N_RING))
        random_d1[r] = shares[1]
        random_d2[r] = shares[1] + shares[2]

    record = {"n_random_maps": N_RANDOM_MAPS, "random_seed": RANDOM_SEED,
              "cells_per_half_wedge": per_label,
              "left_to_right": left_table,
              "random": {
                  "distance_1_share": {
                      "mean": float(random_d1.mean()),
                      "p95": float(np.quantile(random_d1, 0.95)),
                      "max": float(random_d1.max())},
                  "distance_le_2_share": {
                      "mean": float(random_d2.mean()),
                      "p95": float(np.quantile(random_d2, 0.95)),
                      "max": float(random_d2.max())}},
              "maps": {}}
    print(f"\nShare of the between-half-wedge EPG->EPG count by ring "
          f"distance; {N_RANDOM_MAPS} random maps (seed {RANDOM_SEED}): "
          f"distance-1 share mean {random_d1.mean():.4f}, 95th pct "
          f"{np.quantile(random_d1, 0.95):.4f}, max {random_d1.max():.4f}")
    off_total = float(G.sum() - np.trace(G))
    cross_total = float(sum(G[a, b] for a in range(len(LABELS))
                            for b in range(len(LABELS))
                            if LABELS[a][0] != LABELS[b][0]))
    record["between_half_wedge_count"] = off_total
    record["cross_side_count"] = cross_total
    for ring_map in RING_MAPS:
        position = np.array([ring_index(s, k, ring_map) for s, k in LABELS])
        shares = distance_shares(G, position)
        d1 = float(shares[1])
        d2 = float(shares[1] + shares[2])
        p1 = float((1 + (random_d1 >= d1).sum()) / (N_RANDOM_MAPS + 1))
        p2 = float((1 + (random_d2 >= d2).sum()) / (N_RANDOM_MAPS + 1))
        cross = distance_shares(G, position, cross_side_only=True)
        same_side = {str(d): float(shares[d] - cross[d] * cross_total / off_total)
                     for d in range(1, N_RING // 2 + 1)}
        record["maps"][ring_map] = {
            "description": RING_MAP_DESCRIPTION[ring_map],
            "cross_side_distance_1_share": float(cross[1]),
            "same_side_share_of_all_by_distance": same_side,
            "share_by_distance": {str(d): float(shares[d])
                                  for d in range(1, N_RING // 2 + 1)},
            "distance_1_share": d1, "distance_le_2_share": d2,
            "p_distance_1_vs_random": p1,
            "p_distance_le_2_vs_random": p2}
        print(f"  {ring_map:10s}: distance 1 {d1:.4f} (p vs random "
              f"{p1:.5f}); distance <= 2 {d2:.4f} (p {p2:.5f}); by "
              f"distance 1..8 "
              + " ".join(f"{shares[d]:.3f}"
                         for d in range(1, N_RING // 2 + 1)))
        print(f"  {'':10s}  cross-side count only ({cross_total:.0f} "
              f"synapses): share between ring neighbours {cross[1]:.4f}")
    record["elapsed_s"] = round(time.time() - started, 1)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, indent=2))
    print(f"\nwrote {args.output} ({record['elapsed_s']} s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
