#!/usr/bin/env python3
"""BIOLOGICAL BENCHMARK SUITE -- VISUAL group (fly-module verdict, Requirement 1).

These are COMPUTATIONAL ANALOGUES of published fly results, not replications:
the compiled MaleCNS graph (166,700 nodes, 24.99M signed edges) run as a leaky
rate model ``h <- (1-a) h + a tanh(g W h + input)`` is asked whether, anywhere
in operating-point space, it reproduces the qualitative published finding. A
miss everywhere is a model-class limit (UNVALIDATABLE-AT-THIS-FIDELITY), and is
recorded as such, not hidden.

OPERATING GRID (fixed, shared across all benchmark groups): recurrent_gain in
{0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5} x leak in {0.1, 0.3, 0.6};
internal_steps=4 (the deployed convention); bias 0. 21 points, run
SEQUENTIALLY in one process with ONE graph load (memory rule).

===========================================================================
PREREGISTRATION -- BANDS FIXED BEFORE THE SWEEP RUNS. This file is committed
before any grid point executes; misses are reported as misses, and no band
is adjusted after seeing results.
===========================================================================

BENCHMARK V1 -- T4/T5 direction selectivity.
  CITATION: Maisak, M.S., Haag, J., Ammer, G., et al. "A directional tuning
  map of Drosophila elementary motion detectors." Nature 500, 212-216 (2013).
  Published finding: T4 and T5 cells are strongly direction-selective, and
  the four subtypes (a-d) of each prefer the four cardinal directions, one
  subtype per direction (tiling the four lobula-plate layers). Responses in
  the null direction are largely absent, i.e. selectivity is strong.

  PROTOCOL (computational analogue): a 4-cell-wide bar sweeps across the
  64x64 ARC grid in each of the four screen-cardinal directions (16 frames,
  4 cells per frame; one network.advance of internal_steps=4 per frame;
  state starts from zeros per sweep). Positive-lobe T4/T5 activity is
  accumulated per cell per direction from frame index 2 onward (the first
  two frames are onset transient, skipped identically in all directions).
  DSI per unit = (R_pref - R_anti) / (R_pref + R_anti), pref = argmax over
  the four directions, anti = the opposite direction.

  PASS BAND, preregistered (a grid point PASSES V1 iff ALL of):
    (a) pooled per-cell MEDIAN DSI >= 0.30, over all T4 cells measured
        under the ON bar and all T5 cells measured under the OFF bar,
        cells with R_pref + R_anti > 1e-9 only;
    (b) the population preferred directions of subtypes T4a-d cover >= 3
        distinct screen directions, and likewise T5a-d >= 3 (Maisak's
        qualitative target is 4 distinct; >= 3 is allowed because the
        hex-lattice-to-screen rotation is unknown, so two of the four
        anatomical directions could alias onto one screen cardinal);
    (c) >= 50% of T4/T5 cells have a defined DSI (guards against a nearly
        silent network passing on a handful of active cells).
  The 0.30 threshold is a deliberately permissive computational-analogue
  bound on Maisak's near-saturating selectivity; the point of the band is
  to detect DIRECTION-selective structure at all, since a frozen rate model
  has none of the explicit delay lines that build direction selectivity in
  the animal. EXPECTED-tier note, stated before running: the repo's prior
  measurement found frame-to-frame T4/T5 pattern change 3.41x larger for a
  moving than a static bar at gain 2.0 (context, recorded in the output),
  but explicitly could NOT establish direction selectivity; this benchmark
  may therefore miss everywhere, and that outcome is a primary result.

BENCHMARK V2 -- LC object-position tuning (representational similarity).
  CITATION: Wu, M., Nern, A., Williamson, W.R., et al. "Visual projection
  neurons in the Drosophila lobula link feature detection to distinct
  behavioral programs." eLife 5:e21022 (2016). Published finding: LC/LPLC
  visual projection neurons have retinotopic receptive fields that tile
  visual space, so which members of an LC population respond encodes object
  position.

  PROTOCOL (computational analogue): a single 4x4 bright object is placed
  at each of a 5x5 grid of screen positions (top-left corners at rows/cols
  {4,16,28,40,52}); from zeros, the network is advanced 3 times (3 x 4
  internal steps) holding the static frame's drive; the positive-lobe
  activity of the 4,674 LC/LPLC-family cells is the population vector for
  that position. Representational dissimilarity between two positions =
  1 - Pearson r between their LC vectors; position distance = Euclidean
  distance between object centres in cells. Spearman rho is computed
  between the two, across all 300 unordered position pairs.

  PASS BAND, preregistered (a grid point PASSES V2 iff BOTH of):
    (a) Spearman rho >= 0.50 between position distance and LC pattern
        dissimilarity (nearby objects must yield more similar LC
        population vectors than distant ones);
    (b) >= 80% of position pairs have a defined Pearson r (guards against
        a silent or constant LC population passing vacuously; pairs with a
        zero-variance vector are undefined and dropped).
  Secondary, recorded but NOT part of the band: per-LC-type Spearman rho
  for every LC/LPLC type with >= 100 cells.

===========================================================================
ASSUMPTIONS (declared; each is a convention we chose, not fly physiology):
- ASSUMPTION "bar colours": the deployed bio-eye encoder is categorical
  (ARC colour c drives medulla/lamina type index c % 15), so a "bright bar"
  has no literal analogue. The ON bar's cells cycle the colours that the
  encoder's own colour->channel map sends to L1/Mi1/Mi4 (T4's ON-pathway
  inputs); the OFF bar cycles the colours sent to L2/Tm1/Tm2/Tm9 (T5's
  OFF-pathway inputs). Background is colour 0. This hands each detector
  class input on the channels it evolved to read (input-validity
  principle); it is still an invented mapping, and if it is wrong the
  benchmark tests less than it claims. T4 is scored on the ON bar and T5
  on the OFF bar; both conditions are recorded for both.
- ASSUMPTION "screen directions": 'right/left/down/up' are ARC-grid axes.
  The compiled hex lattice's rotation relative to the fly's visual field
  axes is unknown, so the band tests distinctness and consistency of
  preferred directions, never their absolute identity (front-to-back etc.).
- ASSUMPTION "onset skip = 2 frames" and "settle = 3 advances": chosen so
  signals can propagate the >= 2 synapses from medulla input to T4/T5 and
  LC before reading; identical across directions/positions, so they cannot
  create a direction or position bias.
- ESTABLISHED (this repo, node_metadata.npz): subtype labels T4a-d/T5a-d
  (13,580 cells; 5 additional *_unclear cells excluded), LC family = type
  prefix LC|LPLC (4,674 cells).

Run:  python scripts/benchmarks/visual_motion.py
Output: results/benchmarks/visual_motion.json (saved after every grid point).
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# The shared operating grid (fixed across all benchmark groups).
GAINS = (0.8, 1.0, 1.2, 1.5, 1.8, 2.0, 2.5)
LEAKS = (0.1, 0.3, 0.6)
INTERNAL_STEPS = 4
BIAS = 0.0

# V1 protocol constants (preregistered).
BAR_WIDTH = 4
BAR_STEP = 4  # cells per frame -> 16 frames per sweep
ONSET_SKIP = 2
DIRECTIONS = ("right", "left", "up", "down")
OPPOSITE = {"right": "left", "left": "right", "up": "down", "down": "up"}
ON_PATHWAY_TYPES = ("L1", "Mi1", "Mi4")
OFF_PATHWAY_TYPES = ("L2", "Tm1", "Tm2", "Tm9")
BACKGROUND_COLOUR = 0
T4_SUBTYPES = ("T4a", "T4b", "T4c", "T4d")
T5_SUBTYPES = ("T5a", "T5b", "T5c", "T5d")
V1_MEDIAN_DSI_BAND = 0.30
V1_DISTINCT_DIRECTIONS_BAND = 3
V1_DEFINED_FRACTION_BAND = 0.50

# V2 protocol constants (preregistered).
OBJECT_SIZE = 4
POSITION_OFFSETS = (4, 16, 28, 40, 52)  # 5x5 = 25 positions
SETTLE_ADVANCES = 3
V2_RHO_BAND = 0.50
V2_VALID_PAIR_FRACTION_BAND = 0.80
LC_TYPE_MIN_CELLS = 100

# Prior repo measurement, recorded for context (given, not re-measured here):
PRIOR_CONTEXT = (
    "Prior repo measurement at gain 2.0: frame-to-frame T4/T5 pattern change "
    "3.41x larger for a moving than a static bar (2.53x for LC); direction "
    "selectivity itself was explicitly not established by that measurement."
)


def _grid_frames() -> "tuple[dict[str, list[Any]], list[Any], list[tuple[int, int]]]":
    """Build every stimulus grid: V1 bar sweeps and V2 object positions."""

    import numpy as np

    size = 64

    def bar_grid(direction: str, position: int, colours: list[int]) -> Any:
        grid = np.full((size, size), BACKGROUND_COLOUR, dtype=np.int8)
        lo, hi = max(position, 0), min(position + BAR_WIDTH, size)
        if hi <= lo:
            return grid
        rows = np.arange(size)[:, None]
        cols = np.arange(size)[None, :]
        cycle = np.asarray(colours, dtype=np.int8)
        pattern = cycle[(rows + cols) % len(cycle)]
        if direction in ("right", "left"):
            grid[:, lo:hi] = pattern[:, lo:hi]
        else:
            grid[lo:hi, :] = pattern[lo:hi, :]
        return grid

    steps = list(range(0, size - BAR_WIDTH + 1, BAR_STEP))  # 0..60, 16 frames

    def sweep(direction: str, colours: list[int]) -> list[Any]:
        positions = steps if direction in ("right", "down") else steps[::-1]
        return [bar_grid(direction, p, colours) for p in positions]

    def object_grid(r0: int, c0: int, colours: list[int]) -> Any:
        grid = np.full((size, size), BACKGROUND_COLOUR, dtype=np.int8)
        rows = np.arange(size)[:, None]
        cols = np.arange(size)[None, :]
        cycle = np.asarray(colours, dtype=np.int8)
        pattern = cycle[(rows + cols) % len(cycle)]
        grid[r0 : r0 + OBJECT_SIZE, c0 : c0 + OBJECT_SIZE] = pattern[
            r0 : r0 + OBJECT_SIZE, c0 : c0 + OBJECT_SIZE
        ]
        return grid

    return bar_grid, sweep, object_grid  # type: ignore[return-value]


def main() -> int:
    parser = argparse.ArgumentParser(description="FlyGI visual benchmark group")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results" / "benchmarks" / "visual_motion.json"
    )
    parser.add_argument(
        "--coarse",
        action="store_true",
        help="halve the per-point protocol (bar step 8 -> 8 frames, settle 2); "
        "only for keeping the grid complete if a point exceeds the time budget",
    )
    args = parser.parse_args()

    import numpy as np
    from scipy.stats import spearmanr

    from flygi.arc.factory import build_connectome_policy
    from flygi.config import load_config
    from flygi.dynamics.rate import RateParameters, ScipyRateNetwork
    from flygi.encoding.features import encode_observation

    global BAR_STEP, SETTLE_ADVANCES
    if args.coarse:
        BAR_STEP = 8
        SETTLE_ADVANCES = 2

    class _NullActions:
        RESET = 0

        @staticmethod
        def from_id(identifier: int) -> int:
            return identifier

    class _Frame:
        def __init__(self, g: Any) -> None:
            self.frame = [g]

    started = time.time()
    config = load_config(ROOT / "configs/literal_rate_bioeye_lc.yaml")
    assembled = build_connectome_policy(config, _NullActions)
    network = assembled.policy._network
    projection = assembled.projection
    connectivity = network.connectivity
    node_count = network.node_count
    description = projection.describe()
    if description.get("kind") != "retinotopic_columnar_colour":
        raise SystemExit(
            f"expected the deployed bio-eye encoder, got {description.get('kind')}"
        )
    print(f"graph + encoder loaded in {time.time() - started:.1f}s", flush=True)

    # Derive bar colours FROM the encoder's own colour->channel map so the
    # protocol cannot silently drift from the deployed plumbing.
    colour_map = description["colour_channel_map"]  # {str(colour): type_name}
    on_colours = sorted(
        int(c) for c, t in colour_map.items() if t in ON_PATHWAY_TYPES
    )
    off_colours = sorted(
        int(c) for c, t in colour_map.items() if t in OFF_PATHWAY_TYPES
    )
    # Drop the 0/15 collision partner if present: background is colour 0, so a
    # bar must never reuse a colour that shares channel 0's type.
    background_type = colour_map[str(BACKGROUND_COLOUR)]
    on_colours = [c for c in on_colours if colour_map[str(c)] != background_type]
    off_colours = [c for c in off_colours if colour_map[str(c)] != background_type]
    if not on_colours or not off_colours:
        raise SystemExit(
            f"could not derive pathway colours: on={on_colours} off={off_colours}"
        )
    print(
        f"ON bar colours {on_colours} -> {[colour_map[str(c)] for c in on_colours]}; "
        f"OFF bar colours {off_colours} -> {[colour_map[str(c)] for c in off_colours]}",
        flush=True,
    )

    with np.load(
        Path(config.graph.output_dir) / "node_metadata.npz", allow_pickle=False
    ) as archive:
        types = archive["type"].astype("U")

    subtype_indices = {name: np.flatnonzero(types == name) for name in T4_SUBTYPES + T5_SUBTYPES}
    for name, idx in subtype_indices.items():
        if idx.size == 0:
            raise SystemExit(f"subtype {name} missing from node metadata")
    t4t5_idx = np.concatenate([subtype_indices[n] for n in T4_SUBTYPES + T5_SUBTYPES])
    # Position of each subtype's cells inside the concatenated t4t5 array.
    spans: dict[str, slice] = {}
    cursor = 0
    for name in T4_SUBTYPES + T5_SUBTYPES:
        n = subtype_indices[name].size
        spans[name] = slice(cursor, cursor + n)
        cursor += n
    is_t4 = np.zeros(t4t5_idx.size, dtype=bool)
    for name in T4_SUBTYPES:
        is_t4[spans[name]] = True

    lc_mask = np.char.startswith(types, "LC") | np.char.startswith(types, "LPLC")
    lc_idx = np.flatnonzero(lc_mask)
    lc_types = types[lc_idx]
    lc_big_types = sorted(
        t for t in set(lc_types.tolist()) if int((lc_types == t).sum()) >= LC_TYPE_MIN_CELLS
    )
    print(
        f"T4/T5 cells {t4t5_idx.size}, LC family {lc_idx.size}, "
        f"LC types >= {LC_TYPE_MIN_CELLS} cells: {len(lc_big_types)}",
        flush=True,
    )

    _, sweep, object_grid = _grid_frames()

    def drive_of(grid: Any) -> Any:
        features = encode_observation(
            _Frame(grid),
            previous_grid=None,
            previous_action_id=None,
            available_action_ids=(6,),
        )
        return projection.drive_features(features)

    # Precompute every drive once: drives depend only on the stimulus, never on
    # gain/leak, and the encoder has no change channel (motion is left to the
    # network's own persistent state, which is exactly what V1 probes).
    v1_drives: dict[tuple[str, str], list[Any]] = {}
    for condition, colours in (("on", on_colours), ("off", off_colours)):
        for direction in DIRECTIONS:
            v1_drives[(condition, direction)] = [
                drive_of(g) for g in sweep(direction, colours)
            ]
    frames_per_sweep = len(next(iter(v1_drives.values())))
    positions = [(r, c) for r in POSITION_OFFSETS for c in POSITION_OFFSETS]
    v2_drives = [drive_of(object_grid(r, c, on_colours)) for r, c in positions]
    centres = np.asarray(
        [(r + OBJECT_SIZE / 2.0, c + OBJECT_SIZE / 2.0) for r, c in positions]
    )
    pair_i, pair_j = np.triu_indices(len(positions), k=1)
    position_distance = np.linalg.norm(centres[pair_i] - centres[pair_j], axis=1)
    print(
        f"precomputed {len(v1_drives) * frames_per_sweep} V1 drives "
        f"({frames_per_sweep} frames/sweep) and {len(v2_drives)} V2 drives",
        flush=True,
    )

    def run_v1(net: ScipyRateNetwork) -> dict[str, Any]:
        # R[condition][direction_index, cell] = accumulated positive activity.
        R = {
            cond: np.zeros((len(DIRECTIONS), t4t5_idx.size), dtype=np.float64)
            for cond in ("on", "off")
        }
        for cond in ("on", "off"):
            for di, direction in enumerate(DIRECTIONS):
                state = net.initial_state()
                for k, drive in enumerate(v1_drives[(cond, direction)]):
                    state = net.advance(state, drive)
                    if k >= ONSET_SKIP:
                        R[cond][di] += np.maximum(state[t4t5_idx], 0.0)

        # Per-cell DSI: T4 cells scored on the ON bar, T5 cells on the OFF bar.
        scored = np.where(is_t4[None, :], R["on"], R["off"])  # (4, cells)
        pref = np.argmax(scored, axis=0)
        anti = np.asarray([DIRECTIONS.index(OPPOSITE[DIRECTIONS[p]]) for p in pref])
        r_pref = scored[pref, np.arange(scored.shape[1])]
        r_anti = scored[anti, np.arange(scored.shape[1])]
        total = r_pref + r_anti
        defined = total > 1e-9
        dsi = np.full(scored.shape[1], np.nan)
        dsi[defined] = (r_pref[defined] - r_anti[defined]) / total[defined]

        per_subtype: dict[str, Any] = {}
        for name in T4_SUBTYPES + T5_SUBTYPES:
            cond = "on" if name.startswith("T4") else "off"
            block = R[cond][:, spans[name]]
            sums = block.sum(axis=1)
            p = int(np.argmax(sums))
            a = DIRECTIONS.index(OPPOSITE[DIRECTIONS[p]])
            denom = float(sums[p] + sums[a])
            sub_dsi = float((sums[p] - sums[a]) / denom) if denom > 1e-9 else float("nan")
            cell_pref = pref[spans[name]]
            cell_defined = defined[spans[name]]
            consistency = (
                float((cell_pref[cell_defined] == p).mean())
                if cell_defined.any()
                else float("nan")
            )
            per_subtype[name] = {
                "preferred": DIRECTIONS[p],
                "subtype_dsi": sub_dsi,
                "cell_consistency": consistency,
                "direction_totals": {d: float(s) for d, s in zip(DIRECTIONS, sums)},
            }
        t4_distinct = len({per_subtype[n]["preferred"] for n in T4_SUBTYPES})
        t5_distinct = len({per_subtype[n]["preferred"] for n in T5_SUBTYPES})
        defined_fraction = float(defined.mean())
        median_dsi = float(np.median(dsi[defined])) if defined.any() else float("nan")
        median_t4 = (
            float(np.median(dsi[is_t4 & defined])) if (is_t4 & defined).any() else float("nan")
        )
        median_t5 = (
            float(np.median(dsi[~is_t4 & defined]))
            if (~is_t4 & defined).any()
            else float("nan")
        )
        passed = bool(
            defined.any()
            and median_dsi >= V1_MEDIAN_DSI_BAND
            and t4_distinct >= V1_DISTINCT_DIRECTIONS_BAND
            and t5_distinct >= V1_DISTINCT_DIRECTIONS_BAND
            and defined_fraction >= V1_DEFINED_FRACTION_BAND
        )
        return {
            "median_dsi_pooled": median_dsi,
            "median_dsi_t4_on": median_t4,
            "median_dsi_t5_off": median_t5,
            "defined_fraction": defined_fraction,
            "t4_distinct_preferred": t4_distinct,
            "t5_distinct_preferred": t5_distinct,
            "per_subtype": per_subtype,
            "pass": passed,
        }

    def run_v2(net: ScipyRateNetwork) -> dict[str, Any]:
        vectors = np.zeros((len(positions), lc_idx.size), dtype=np.float64)
        for i, drive in enumerate(v2_drives):
            state = net.initial_state()
            for _ in range(SETTLE_ADVANCES):
                state = net.advance(state, drive)
            vectors[i] = np.maximum(state[lc_idx], 0.0)

        def rsa(matrix: Any) -> tuple[float, float, int]:
            centred = matrix - matrix.mean(axis=1, keepdims=True)
            norms = np.linalg.norm(centred, axis=1)
            ok = norms > 1e-12
            with np.errstate(invalid="ignore", divide="ignore"):
                unit = centred / np.maximum(norms[:, None], 1e-30)
                corr = unit @ unit.T
            dissimilarity = 1.0 - corr[pair_i, pair_j]
            valid = ok[pair_i] & ok[pair_j]
            n_valid = int(valid.sum())
            if n_valid < 3:
                return float("nan"), float(n_valid / pair_i.size), n_valid
            rho = spearmanr(position_distance[valid], dissimilarity[valid]).statistic
            return float(rho), float(n_valid / pair_i.size), n_valid

        rho, valid_fraction, n_valid = rsa(vectors)
        per_type: dict[str, float] = {}
        for t in lc_big_types:
            sub_rho, _, _ = rsa(vectors[:, lc_types == t])
            per_type[t] = sub_rho
        passed = bool(
            np.isfinite(rho)
            and rho >= V2_RHO_BAND
            and valid_fraction >= V2_VALID_PAIR_FRACTION_BAND
        )
        return {
            "spearman_rho": rho,
            "valid_pair_fraction": valid_fraction,
            "valid_pairs": n_valid,
            "mean_lc_positive_mass": float(vectors.sum(axis=1).mean()),
            "per_type_rho": per_type,
            "pass": passed,
        }

    report: dict[str, Any] = {
        "group": "VISUAL",
        "coarse_protocol": bool(args.coarse),
        "protocol": {
            "grid": {"gains": GAINS, "leaks": LEAKS, "internal_steps": INTERNAL_STEPS, "bias": BIAS},
            "config": "configs/literal_rate_bioeye_lc.yaml",
            "encoder": description,
            "v1": {
                "citation": "Maisak et al. 2013, Nature 500:212-216",
                "band": (
                    f"PASS iff pooled per-cell median DSI >= {V1_MEDIAN_DSI_BAND} "
                    f"(T4 on ON bar, T5 on OFF bar) AND T4a-d distinct preferred "
                    f"directions >= {V1_DISTINCT_DIRECTIONS_BAND} AND T5a-d distinct "
                    f">= {V1_DISTINCT_DIRECTIONS_BAND} AND defined-DSI fraction >= "
                    f"{V1_DEFINED_FRACTION_BAND}; preregistered before the sweep"
                ),
                "bar_width": BAR_WIDTH,
                "bar_step": BAR_STEP,
                "onset_skip": ONSET_SKIP,
                "frames_per_sweep": frames_per_sweep,
                "on_colours": on_colours,
                "off_colours": off_colours,
                "prior_context": PRIOR_CONTEXT,
            },
            "v2": {
                "citation": "Wu et al. 2016, eLife 5:e21022",
                "band": (
                    f"PASS iff Spearman rho >= {V2_RHO_BAND} between object-position "
                    f"distance and 1 - Pearson pattern correlation of LC/LPLC positive "
                    f"activity over 300 position pairs AND valid-pair fraction >= "
                    f"{V2_VALID_PAIR_FRACTION_BAND}; preregistered before the sweep"
                ),
                "object_size": OBJECT_SIZE,
                "position_offsets": POSITION_OFFSETS,
                "settle_advances": SETTLE_ADVANCES,
                "lc_cells": int(lc_idx.size),
            },
        },
        "grid_points": [],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    for gain in GAINS:
        for leak in LEAKS:
            point_start = time.time()
            net = ScipyRateNetwork(
                connectivity,
                RateParameters(
                    internal_steps=INTERNAL_STEPS,
                    leak=leak,
                    recurrent_gain=gain,
                    bias=BIAS,
                ),
                copy_connectivity=False,
            )
            v1 = run_v1(net)
            v2 = run_v2(net)
            elapsed = time.time() - point_start
            row = {
                "gain": gain,
                "leak": leak,
                "v1": v1,
                "v2": v2,
                "elapsed_s": round(elapsed, 1),
            }
            report["grid_points"].append(row)
            args.output.write_text(json.dumps(report, indent=2))
            print(
                f"gain {gain} leak {leak}: V1 median DSI "
                f"{v1['median_dsi_pooled']:.4f} (defined {v1['defined_fraction']:.2f}, "
                f"T4 distinct {v1['t4_distinct_preferred']}, T5 distinct "
                f"{v1['t5_distinct_preferred']}) pass={v1['pass']} | V2 rho "
                f"{v2['spearman_rho']:.4f} (valid {v2['valid_pair_fraction']:.2f}) "
                f"pass={v2['pass']} | {elapsed:.1f}s",
                flush=True,
            )
            del net
            if elapsed > 600 and not args.coarse:
                print(
                    "NOTE: point exceeded the 10-minute budget; rerun with "
                    "--coarse to keep the grid complete under budget",
                    flush=True,
                )

    def summarize(key: str, value_key: str) -> dict[str, Any]:
        points = report["grid_points"]
        passes = [[p["gain"], p["leak"]] for p in points if p[key]["pass"]]
        finite = [
            p for p in points if np.isfinite(p[key][value_key])
        ]
        best = max(finite, key=lambda p: p[key][value_key]) if finite else None
        return {
            "pass_points": passes,
            "best_point": [best["gain"], best["leak"]] if best else None,
            "best_value": best[key][value_key] if best else None,
        }

    report["summary"] = {
        "v1": summarize("v1", "median_dsi_pooled"),
        "v2": summarize("v2", "spearman_rho"),
        "grid_complete": len(report["grid_points"]) == len(GAINS) * len(LEAKS),
        "total_elapsed_s": round(time.time() - started, 1),
    }
    args.output.write_text(json.dumps(report, indent=2))
    print(json.dumps(report["summary"], indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
