#!/usr/bin/env python3
"""H-T4T5-CLASS25-MOTION -- does the class-2.5-validated T4/T5 population
decode real ARC sprite displacement direction on HELD-OUT games?

PREREGISTRATION (EXPERIMENTS.yaml H-T4T5-CLASS25-MOTION, 2026-09-30,
immutable; restated, not changed):
  - Ground truth: the taxis premise machinery's measured exact movers
    (the games where action-correlated translation is recovered exactly).
  - Stimuli: real consecutive frame pairs around a measured displacement,
    presented retinotopically to the class-2.5 patch at its PASSING
    configuration (verbatim from results/benchmarks/fc25_visual_ds.json,
    no re-tuning).
  - Features: T4a-d/T5a-d population responses in the crossing-window
    readout.  Decoder: one linear probe per arm, same form and
    regularization, trained on TRAIN-game events, scored 4-way direction
    accuracy on HELD-OUT games x 3 seeds.
  - Controls, all mandatory: uniform-tau-with-trained-strengths twin
    (the class-2.5 attribution control); degree-preserving rewired patch;
    engineered equivalent = the taxis shift-matcher's direction estimate
    on the same pairs (ceiling context, NOT a required beat).
  - PASS BANDS, fixed in the registration: held-out 4-way accuracy >
    0.25 chance (binomial p < 0.05) AND real > uniform-tau twin AND
    real > degree-preserving null (paired sign tests p < 0.05 across
    game x seed cells).

===========================================================================
MECHANICAL CHOICES -- ALL DECLARED HERE, BEFORE ANY HELD-OUT SCORING.
Nothing below is tuned on held-out games; the only calibrated quantity
(probe regularization C) is chosen by leave-one-game-out CV on TRAIN
games only, with the identical grid and procedure for every arm.

GROUND-TRUTH REGENERATION (taxis-premise machinery, offline arcade):
  * Game set: the 14 measured dead games = the key set of
    results/taxis_premise.json (asserted at run time).
  * Capture: per game, one strict-offline session
    (evaluate_random_baseline plumbing: _new_offline_arcade,
    derived_run_seeds, experiment seed CAPTURE_SEED=20260930), budget
    REPLAY_BUDGET=600 steps, uniform-random choice among the frame's
    legal directional actions {1,2,3,4} (RESET when the state needs it
    or offers no directional action).  Every directional transition
    (prev_grid, action_id, new_grid) is kept.
  * Mover rediscovery: the captured transitions are fed IN ORDER to the
    repo's own SpatialTaxis.observe_transition (src/flygi/controller/
    taxis.py, unmodified); a game's movers are the final _movers table
    (modal displacement per action, >=3 obs, >=50% modal fraction --
    the taxis_premise_v2 protocol's matcher).  ASSUMPTION (declared):
    ">=1 stable mover recovered" operationalizes the preregistration's
    "exact movers" game set; the original v2 results file is truncated
    (85 bytes), so the set is rediscovered, not read.
  * Event verification: a transition is an event iff its action has a
    mover AND the timer-masked diff (final-mask, _DIFF_MIN<=n<=_DIFF_MAX)
    is matched by the taxis shift scan (verbatim constants _SHIFT_RANGE,
    _SHIFT_AGREE) with best shift EXACTLY equal to that action's modal
    mover displacement.  Label = dominant-axis direction of the shift
    (dr>0 down, dr<0 up, dc>0 right, dc<0 left); diagonal ties
    (|dr|==|dc|, both nonzero) are excluded and counted.
  * Caps and floors: at most EVENT_CAP=60 events per game (first in
    replay order); a game enters the dataset iff it yields >=
    EVENT_FLOOR=10 verified events (the preregistered aim is >=30 per
    game over >=6 games; actual counts are reported either way).

RETINOTOPIC PRESENTATION (fc25/fc2 machinery, patch and mapping reused):
  * Patch, weights, parameters: fc2.build_patch() + fc25.
    trained_weight_matrix + fc25.trained_table at the PASSING fc25
    configuration (trained_subset), gain read verbatim from
    results/benchmarks/fc25_visual_ds.json (chosen_gain; asserted
    non-None and pass=True).  No re-tuning anywhere.
  * ASSUMPTION (spatial mapping, declared): 1 ARC pixel = 1 hex-column
    plane unit.  Each driven cell (L1/L2/L3, fc2.DRIVEN_TYPES) samples
    the frame by bilinear interpolation at
      row = anchor_r + (y_cell - y_center),
      col = anchor_c + (x_cell - x_center),
    where (x_center, y_center) is fc2.PATCH_CENTER embedded by fc2's
    hex basis, and the anchor is the centroid of the event's
    timer-masked diff (erase+draw straddle; the sprite sits
    symmetrically at -d/2 (t-1) and +d/2 (t) about the crop centre for
    EVERY direction, so the anchor rule leaks no label).  Coordinates
    clamp to the 64x64 frame edge.  Timer strips are NOT masked out of
    the stimulus (masking would edit the fly's input; their changes are
    label-independent).
  * ASSUMPTION (luminance, declared): ARC colour index / 15.0 in [0,1];
    drive = fc2.INPUT_DRIVE * luminance onto driven cells (histamine
    sign, as fc2).  The palette treated as ordinal grayscale is an
    invention; what the correlator needs is spatiotemporal contrast.
  * Temporal protocol: settle SETTLE on frame t-1 from rest
    (fc2.SETTLE_MS=2500 ms), then present frame t for the response
    window.  Crossing-window analog (declared): a frame switch makes
    every cell's crossing instantaneous at t=0, so the v2 window
    [front-2col, +0.75s] degenerates to [0, fc2.WINDOW_AFTER_S=0.75 s];
    evoked = max(output - settled_output, 0) integrated over that
    window per scored T4/T5 cell (fc2 v2 form).  dt = fc2.DT_MS = 2 ms.
    Features = the 498 scored-cell evoked integrals.
  * Dynamics code: fc2.GradedFlyvisNetwork run verbatim, with
    parameter vectors reshaped to column vectors so events batch as
    matrix columns (shape adaptation only; update equation untouched).
    Stability: fc2.V_ABORT checks every 50 steps; an event unstable in
    ANY arm is dropped from EVERY arm (pairing preserved) and counted.

ARMS (same probe, same features pipeline):
  * real          : trained_subset weights + taus, fc25 chosen gain.
  * uniform_tau   : trained alphas + trained V_rest, tau 50 ms for all
                    types (fc25's own attribution twin), at ITS OWN fc25
                    calibrated gain (verbatim from the results file).
  * rewired       : degree-preserving rewired real matrix
                    (flygi.connectome.nulls.degree_preserving_rewire,
                    default NullOptions), real arm's table and gain.
                    One independent null instance per seed
                    (rewire seed = REWIRE_SEED_BASE + seed).
  * engineered    : taxis shift-matcher's own direction estimate on the
                    same frame pairs.  NOTE, stated openly: events are
                    VERIFIED with this same matcher, so its accuracy is
                    1.0 by construction here -- reported as ceiling
                    context exactly as preregistered, not a beat target.

SPLIT AND DECODER (declared):
  * Seeds 0,1,2.  Per seed: qualifying games sorted, permuted by
    default_rng(seed); HELD-OUT = first max(2, round(0.4*n)) games,
    TRAIN = rest.  Events never move between splits within a seed.
  * Probe: features z-scored with TRAIN statistics; multinomial
    logistic regression (sklearn, L2, lbfgs, max_iter 5000); C chosen
    from C_GRID=(0.01, 0.1, 1.0, 10.0) by leave-one-TRAIN-game-out
    mean accuracy, smallest C on ties.  Identical for every arm.
  * Band operationalization (declared): binomial test (one-sided,
    scipy binomtest vs 0.25) on each seed's pooled held-out events;
    the chance criterion requires p < 0.05 in ALL THREE seeds.  Paired
    sign tests (one-sided, real > control) over (held-out game x seed)
    accuracy cells, ties dropped.  PASS = all three criteria.

TIER DISCIPLINE: every number this script writes is Measured under this
protocol.  Expected tier, base rate stated in the registration: ~2 for 15.

Run:    python scripts/benchmarks/t4t5_motion_arm.py
Output: results/benchmarks/t4t5_motion_arm.json (+ .log)
"""

from __future__ import annotations

import gc
import importlib.util
import json
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

# --- declared constants (header section restates the reasoning) -------------
CAPTURE_SEED = 20260930          # experiment seed for derived_run_seeds
REPLAY_BUDGET = 600              # offline steps per game
EVENT_CAP = 60                   # max events kept per game (replay order)
EVENT_FLOOR = 10                 # min verified events for a game to qualify
RESP_WINDOW_MS = 750.0           # fc2.WINDOW_AFTER_S * 1000 (asserted)
SEEDS = (0, 1, 2)
HELDOUT_FRACTION = 0.4
C_GRID = (0.01, 0.1, 1.0, 10.0)
REWIRE_SEED_BASE = 4242
ALPHA = 0.05
LABELS = ("up", "down", "left", "right")

FC25_RESULTS = ROOT / "results/benchmarks/fc25_visual_ds.json"
TAXIS_V1_RESULTS = ROOT / "results/taxis_premise.json"
OUT_JSON = ROOT / "results/benchmarks/t4t5_motion_arm.json"
OUT_LOG = OUT_JSON.with_suffix(".log")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _free_ram_note() -> str:
    """Resource rule: measure before launch (memory 2026-09-24 OOM)."""
    try:
        raw = subprocess.run(["vm_stat"], capture_output=True, text=True,
                             timeout=10).stdout
        stats = {}
        for line in raw.splitlines():
            if ":" in line and "Pages" in line:
                key, value = line.split(":", 1)
                stats[key.strip()] = int(value.strip().rstrip("."))
        page = 16384
        free = (stats.get("Pages free", 0)
                + stats.get("Pages speculative", 0)) * page
        inactive = stats.get("Pages inactive", 0) * page
        return (f"free={free / 2**30:.2f}GiB "
                f"inactive(reclaimable)={inactive / 2**30:.2f}GiB")
    except Exception as exc:  # pragma: no cover
        return f"unavailable ({exc})"


# ---------------------------------------------------------------------------
# Ground truth: capture transitions, rediscover movers, verify events
# ---------------------------------------------------------------------------

def capture_transitions(base, runtime, game, log) -> list[tuple]:
    """One offline session of random directional play; returns
    (prev_grid, action_id, new_grid) int16 triples."""
    from flygi.arc.state import ArcTurnState
    from flygi.encoding.features import latest_grid

    arcade = base._new_offline_arcade(runtime, ROOT / "environment_files")
    scorecard_id = arcade.open_scorecard(
        tags=["diagnostic", "t4t5-motion-arm"],
        opaque={"game_id": game.game_id, "experiment_seed": CAPTURE_SEED},
    )
    env_seed, _ = base.derived_run_seeds(CAPTURE_SEED, game.game_id)
    base._seed_process_for_environment(env_seed)
    environment = arcade.make(
        game.game_id, seed=env_seed, scorecard_id=scorecard_id,
        save_recording=False, include_frame_data=False,
    )
    rng = np.random.default_rng(env_seed)

    def act(identifier: int):
        action = runtime.GameAction.from_id(identifier)
        response = environment.step(action, data={}, reasoning=None)
        if response is None:
            raise RuntimeError("environment step returned None")
        return response

    frame = environment.observation_space
    transitions: list[tuple] = []
    resets = 0
    for _ in range(REPLAY_BUDGET):
        turn = ArcTurnState.from_frame(frame)
        if turn.needs_reset or turn.is_win:
            frame = act(0)
            resets += 1
            continue
        legal = [a for a in turn.available_action_ids if a in (1, 2, 3, 4)]
        if not legal:
            # Declared: a state with no directional action gets a RESET.
            frame = act(0)
            resets += 1
            continue
        aid = int(rng.choice(legal))
        prev = np.asarray(latest_grid(frame), dtype=np.int16).copy()
        frame = act(aid)
        new = np.asarray(latest_grid(frame), dtype=np.int16).copy()
        transitions.append((prev, aid, new))
    log(f"  captured {len(transitions)} directional transitions "
        f"({resets} resets)")
    del environment, arcade
    gc.collect()
    return transitions


def match_shift(prev, new, rows, cols):
    """The taxis shift scan, verbatim semantics (changed cells only;
    constants imported from the module so they cannot drift)."""
    from flygi.controller.taxis import _GRID, _SHIFT_RANGE

    best_score, best_shift = 0.0, (0, 0)
    for dr in range(-_SHIFT_RANGE, _SHIFT_RANGE + 1):
        for dc in range(-_SHIFT_RANGE, _SHIFT_RANGE + 1):
            if dr == 0 and dc == 0:
                continue
            sr, sc = rows - dr, cols - dc
            inside = (sr >= 0) & (sr < _GRID) & (sc >= 0) & (sc < _GRID)
            if inside.sum() < max(3, 0.5 * rows.size):
                continue
            score = float(
                (prev[sr[inside], sc[inside]]
                 == new[rows[inside], cols[inside]]).mean()
            )
            better = score > best_score + 1e-9
            tie = abs(score - best_score) <= 1e-9 and (
                abs(dr) + abs(dc)
            ) < (abs(best_shift[0]) + abs(best_shift[1]))
            if better or tie:
                best_score, best_shift = score, (dr, dc)
    return best_score, best_shift


def direction_label(shift) -> str | None:
    dr, dc = shift
    if abs(dr) > abs(dc):
        return "down" if dr > 0 else "up"
    if abs(dc) > abs(dr):
        return "right" if dc > 0 else "left"
    return None  # diagonal tie, excluded (declared)


def ground_truth_for_game(base, runtime, game, log) -> dict[str, Any]:
    """Capture, rediscover movers, verify events. Returns a record with
    the kept events (prev, new, label, anchor, engineered_label)."""
    from flygi.controller.taxis import _DIFF_MAX, _DIFF_MIN, _SHIFT_AGREE, SpatialTaxis

    transitions = capture_transitions(base, runtime, game, log)
    taxis = SpatialTaxis()
    for prev, aid, new in transitions:
        taxis.observe_transition(prev.astype(np.int8), aid, new.astype(np.int8))
    movers = {int(k): tuple(int(x) for x in v) for k, v in taxis._movers.items()}
    record: dict[str, Any] = {
        "transitions": len(transitions),
        "movers": {str(k): list(v) for k, v in movers.items()},
        "events": [],
        "diagonal_excluded": 0,
        "rejected_shift_mismatch": 0,
    }
    if not movers:
        log("  no stable movers recovered -- game does not qualify")
        return record
    mask = taxis._timer_mask()
    events = []
    for prev, aid, new in transitions:
        if aid not in movers or len(events) >= EVENT_CAP:
            continue
        diff = (prev != new) & ~mask
        count = int(diff.sum())
        if count < _DIFF_MIN or count > _DIFF_MAX:
            continue
        rows, cols = np.where(diff)
        score, shift = match_shift(prev, new, rows, cols)
        if score < _SHIFT_AGREE:
            continue
        if shift != movers[aid]:
            record["rejected_shift_mismatch"] += 1
            continue
        label = direction_label(shift)
        if label is None:
            record["diagonal_excluded"] += 1
            continue
        # Engineered equivalent = the matcher's own estimate on this pair
        # (identical to the label by the verification rule; see header).
        events.append({
            "prev": prev, "new": new, "action": aid,
            "shift": shift, "label": label,
            "anchor": (float(rows.mean()), float(cols.mean())),
            "engineered_label": direction_label(shift),
        })
    record["events"] = events
    label_counts = {}
    for e in events:
        label_counts[e["label"]] = label_counts.get(e["label"], 0) + 1
    record["label_counts"] = label_counts
    log(f"  movers {record['movers']} -> {len(events)} verified events "
        f"{label_counts} (cap {EVENT_CAP})")
    return record


# ---------------------------------------------------------------------------
# Stimulus presentation and batched dynamics
# ---------------------------------------------------------------------------

def bilinear(grid01: np.ndarray, rr: np.ndarray, cc: np.ndarray) -> np.ndarray:
    rr = np.clip(rr, 0.0, 63.0)
    cc = np.clip(cc, 0.0, 63.0)
    r0 = np.floor(rr).astype(np.int64)
    c0 = np.floor(cc).astype(np.int64)
    r1 = np.minimum(r0 + 1, 63)
    c1 = np.minimum(c0 + 1, 63)
    fr = rr - r0
    fc = cc - c0
    return (grid01[r0, c0] * (1 - fr) * (1 - fc)
            + grid01[r1, c0] * fr * (1 - fc)
            + grid01[r0, c1] * (1 - fr) * fc
            + grid01[r1, c1] * fr * fc)


def build_drives(fc2, patch, events) -> tuple[np.ndarray, np.ndarray]:
    """Per-event external drive vectors for frame t-1 and frame t.
    ASSUMPTION (header): 1 px = 1 column unit; luminance = colour/15;
    drive = fc2.INPUT_DRIVE * luminance on driven cells."""
    driven_idx = np.flatnonzero(patch["driven_mask"])
    c1, c2 = fc2.PATCH_CENTER
    x_center = c1 + 0.5 * c2
    y_center = (3 ** 0.5 / 2.0) * c2
    off_r = patch["y"][driven_idx] - y_center
    off_c = patch["x"][driven_idx] - x_center
    n = patch["types"].shape[0]
    m = len(events)
    drives_prev = np.zeros((n, m))
    drives_next = np.zeros((n, m))
    for j, event in enumerate(events):
        ar, ac = event["anchor"]
        rr = ar + off_r
        cc = ac + off_c
        prev01 = event["prev"].astype(np.float64) / 15.0
        new01 = event["new"].astype(np.float64) / 15.0
        drives_prev[driven_idx, j] = fc2.INPUT_DRIVE * bilinear(prev01, rr, cc)
        drives_next[driven_idx, j] = fc2.INPUT_DRIVE * bilinear(new01, rr, cc)
    return drives_prev, drives_next


def simulate_arm(fc2, matrix, patch, table, gain, drives_prev, drives_next,
                 score_idx, log, label) -> tuple[np.ndarray, np.ndarray, float]:
    """Settle on frame t-1, switch to frame t, integrate the crossing-window
    evoked response.  fc2.GradedFlyvisNetwork verbatim; parameters reshaped
    to columns so events batch as matrix columns (shape adaptation only)."""
    t0 = time.time()
    m = drives_prev.shape[1]
    net = fc2.GradedFlyvisNetwork(
        matrix, patch["types"], table, dt_ms=fc2.DT_MS, gain=gain
    )
    net.tau = net.tau[:, None]
    net.v_rest = net.v_rest[:, None]
    net.v = np.repeat(net.v_rest, m, axis=1)
    bad = np.zeros(m, dtype=bool)

    def unstable_columns() -> np.ndarray:
        finite = np.isfinite(net.v).all(axis=0)
        with np.errstate(invalid="ignore"):
            big = np.where(
                finite, np.abs(np.where(np.isfinite(net.v), net.v, 0.0)).max(axis=0), np.inf
            ) > fc2.V_ABORT
        return ~finite | big

    settle_steps = int(round(fc2.SETTLE_MS / fc2.DT_MS))
    resp_steps = int(round(RESP_WINDOW_MS / fc2.DT_MS))
    previous = None
    with np.errstate(over="ignore", invalid="ignore"):
        for k in range(settle_steps):
            if k == settle_steps - 1:
                previous = net.v.copy()
            net.step(drives_prev)
            if k % 100 == 0:
                bad |= unstable_columns()
        delta = np.abs(net.v - previous)
        residual = float(np.nanmax(np.where(np.isfinite(delta), delta, np.nan)))
        base_out = np.maximum(net.v, 0.0)[score_idx, :]
        total = np.zeros((score_idx.size, m))
        for k in range(resp_steps):
            net.step(drives_next)
            if k % 50 == 0:
                bad |= unstable_columns()
            evoked = np.maximum(
                np.maximum(net.v, 0.0)[score_idx, :] - base_out, 0.0
            )
            total += evoked * (fc2.DT_MS / 1000.0)
        bad |= unstable_columns()
    log(f"  [{label}] simulated {m} events in {time.time() - t0:.1f}s, "
        f"unstable {int(bad.sum())}, settle residual {residual:.2e}")
    return total.T.copy(), bad, residual   # (events, cells)


# ---------------------------------------------------------------------------
# Decoding
# ---------------------------------------------------------------------------

def fit_probe(features, labels, games, train_games, held_games):
    """Declared probe: z-score on TRAIN, multinomial logistic (L2, lbfgs),
    C by leave-one-TRAIN-game-out mean accuracy, smallest C on ties."""
    from sklearn.linear_model import LogisticRegression

    train_mask = np.isin(games, train_games)
    mu = features[train_mask].mean(axis=0)
    sd = features[train_mask].std(axis=0)
    sd = np.where(sd < 1e-12, 1.0, sd)
    scaled = (features - mu) / sd

    def new_clf(c):
        return LogisticRegression(C=c, penalty="l2", solver="lbfgs",
                                  max_iter=5000)

    best_c, best_cv = None, -1.0
    for c in C_GRID:
        fold_accs = []
        for game in train_games:
            fit_mask = train_mask & (games != game)
            val_mask = games == game
            if fit_mask.sum() == 0 or val_mask.sum() == 0:
                continue
            if np.unique(labels[fit_mask]).size < 2:
                continue
            clf = new_clf(c).fit(scaled[fit_mask], labels[fit_mask])
            fold_accs.append(
                float((clf.predict(scaled[val_mask]) == labels[val_mask]).mean())
            )
        cv = float(np.mean(fold_accs)) if fold_accs else -1.0
        if cv > best_cv + 1e-12:
            best_cv, best_c = cv, c
    clf = new_clf(best_c).fit(scaled[train_mask], labels[train_mask])
    per_game = {}
    correct = total = 0
    for game in held_games:
        mask = games == game
        hits = int((clf.predict(scaled[mask]) == labels[mask]).sum())
        per_game[game] = {"n": int(mask.sum()), "correct": hits,
                          "accuracy": hits / int(mask.sum())}
        correct += hits
        total += int(mask.sum())
    return {
        "chosen_C": best_c,
        "train_cv_accuracy": round(best_cv, 4),
        "per_game": per_game,
        "pooled_correct": correct,
        "pooled_n": total,
        "pooled_accuracy": correct / total if total else float("nan"),
    }


def main() -> int:
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    handle = open(OUT_LOG, "w")

    def log(message: str) -> None:
        print(message, flush=True)
        handle.write(message + "\n")
        handle.flush()

    started = time.time()
    log(f"RAM at start: {_free_ram_note()} (single process; fc25-scale run)")

    fc25 = _load_module("fc25_visual_ds", HERE / "fc25_visual_ds.py")
    fc2 = fc25.load_fc2()
    assert abs(fc2.WINDOW_AFTER_S * 1000.0 - RESP_WINDOW_MS) < 1e-9, \
        "response window drifted from fc2.WINDOW_AFTER_S -- refuse to run"
    params = json.loads(fc25.PARAMS_JSON.read_text())
    fc25_results = json.loads(FC25_RESULTS.read_text())

    # Passing configuration, verbatim (no re-tuning; asserted).
    passing = next(c for c in fc25_results["configs"]
                   if c["label"] == "trained_subset")
    assert passing["result"]["readout_v2_crossing_window"]["pass"] is True, \
        "fc25 trained_subset no longer passes -- refuse to run"
    gain_real = passing["calibration"]["chosen_gain"]
    control_row = fc25_results["trivial_alternative"]
    gain_twin = control_row["calibration"]["chosen_gain"]
    assert gain_real is not None and gain_twin is not None
    log(f"fc25 passing configuration: trained_subset gain={gain_real}; "
        f"uniform-tau twin gain={gain_twin} (both verbatim from "
        f"{FC25_RESULTS.name})")

    # The 14-game measured dead set (taxis premise key set, asserted).
    games14 = sorted(json.loads(TAXIS_V1_RESULTS.read_text()).keys())
    assert len(games14) == 14, f"expected 14 premise games, got {len(games14)}"

    report: dict[str, Any] = {
        "benchmark": "H-T4T5-CLASS25-MOTION: class-2.5 T4/T5 population vs "
                     "real ARC sprite displacement direction, held-out games",
        "preregistration": "EXPERIMENTS.yaml H-T4T5-CLASS25-MOTION "
                           "(2026-09-30, before implementation)",
        "pass_bands": "held-out 4-way accuracy > 0.25 (binomial p<0.05, "
                      "ALL 3 seeds; declared operationalization) AND real > "
                      "uniform-tau AND real > rewired (paired sign tests "
                      "p<0.05 over game x seed cells)",
        "declared": {
            "capture_seed": CAPTURE_SEED, "replay_budget": REPLAY_BUDGET,
            "event_cap": EVENT_CAP, "event_floor": EVENT_FLOOR,
            "settle_ms": fc2.SETTLE_MS, "response_window_ms": RESP_WINDOW_MS,
            "dt_ms": fc2.DT_MS, "px_per_column": 1.0,
            "luminance": "colour_index/15 (ASSUMPTION)",
            "anchor": "timer-masked diff centroid (symmetric +/- d/2, no "
                      "label leak)",
            "seeds": list(SEEDS), "heldout_fraction": HELDOUT_FRACTION,
            "probe": "z-score(TRAIN) + multinomial logistic L2 lbfgs, C by "
                     "leave-one-TRAIN-game-out CV over " + str(C_GRID),
            "rewire": f"degree_preserving_rewire, default NullOptions, seed "
                      f"= {REWIRE_SEED_BASE}+seed, real gain/table",
            "gain_real": gain_real, "gain_twin": gain_twin,
        },
        "games": {},
    }

    def save() -> None:
        OUT_JSON.write_text(json.dumps(report, indent=1))

    # ------------------------------------------------ ground truth
    base = _load_module(
        "_t4t5_arm_base", ROOT / "scripts" / "evaluate_random_baseline.py"
    )
    runtime = base.load_arc_runtime()
    frozen = base.discover_games(
        runtime, ROOT / "environment_files", games14
    )
    all_events: list[dict[str, Any]] = []
    for game in frozen:
        base_id = game.base_game_id
        log(f"[{base_id}] ground truth ({game.game_id})")
        try:
            record = ground_truth_for_game(base, runtime, game, log)
        except Exception as exc:
            record = {"error": f"{type(exc).__name__}: {exc}", "events": []}
            log(f"  ERROR {record['error']}")
        qualified = len(record["events"]) >= EVENT_FLOOR
        for event in record["events"]:
            event["game"] = base_id
        if qualified:
            all_events.extend(record["events"])
        report["games"][base_id] = {
            k: v for k, v in record.items() if k != "events"
        } | {"n_events": len(record.get("events", ())),
             "qualified": qualified}
        save()

    qualifying = sorted({e["game"] for e in all_events})
    report["qualifying_games"] = qualifying
    report["events_total"] = len(all_events)
    log(f"qualifying games: {len(qualifying)}/{len(games14)} "
        f"({', '.join(qualifying)}); events total {len(all_events)}")
    if len(qualifying) < 3:
        report["blocker"] = ("fewer than 3 qualifying games -- split "
                            "infeasible; stopping before any scoring")
        save()
        handle.close()
        return 1
    save()

    # ------------------------------------------------ stimuli and features
    log("building fc2 patch (verbatim machinery)...")
    patch = fc2.build_patch()
    types = patch["types"]
    patch["driven_mask"] = np.isin(types, fc2.DRIVEN_TYPES)
    score_mask = np.isin(types, fc2.T4_SUBTYPES + fc2.T5_SUBTYPES)
    score_idx = np.flatnonzero(score_mask)
    log(f"patch: {patch['node_count']} cells, {int(score_idx.size)} scored "
        f"T4/T5 cells")

    drives_prev, drives_next = build_drives(fc2, patch, all_events)
    labels = np.array([e["label"] for e in all_events])
    games_arr = np.array([e["game"] for e in all_events])
    engineered = np.array([e["engineered_label"] for e in all_events])

    alphas = {p: v["subset_mean"] for p, v in params["pairs"].items()}
    real_matrix, coverage = fc25.trained_weight_matrix(fc2, patch, alphas)
    table_real = fc25.trained_table(fc2, params, "subset", None)
    table_twin = fc25.trained_table(fc2, params, "subset", fc25.UNIFORM_TAU)
    report["alpha_coverage"] = {
        k: coverage[k] for k in
        ("pairs_total", "pairs_trained", "edges_trained_fraction",
         "synapse_mass_trained_fraction")
    }

    feats: dict[str, np.ndarray] = {}
    bad_any = np.zeros(len(all_events), dtype=bool)
    residuals: dict[str, float] = {}
    feats["real"], bad, residuals["real"] = simulate_arm(
        fc2, real_matrix, patch, table_real, gain_real,
        drives_prev, drives_next, score_idx, log, "real")
    bad_any |= bad
    feats["uniform_tau"], bad, residuals["uniform_tau"] = simulate_arm(
        fc2, real_matrix, patch, table_twin, gain_twin,
        drives_prev, drives_next, score_idx, log, "uniform_tau")
    bad_any |= bad

    from flygi.connectome.nulls import degree_preserving_rewire

    rewire_stats = {}
    for seed in SEEDS:
        rewired, stats = degree_preserving_rewire(
            real_matrix, seed=REWIRE_SEED_BASE + seed
        )
        rewire_stats[str(seed)] = {
            k: stats[k] for k in stats
            if isinstance(stats[k], (int, float, str, bool))
        }
        feats[f"rewired_{seed}"], bad, residuals[f"rewired_{seed}"] = (
            simulate_arm(fc2, rewired, patch, table_real, gain_real,
                         drives_prev, drives_next, score_idx, log,
                         f"rewired_{seed}")
        )
        bad_any |= bad
    report["rewire_stats"] = rewire_stats
    report["settle_residuals"] = {k: round(v, 10) for k, v in residuals.items()}

    dropped = int(bad_any.sum())
    report["events_dropped_unstable"] = dropped
    if dropped:
        log(f"dropping {dropped} events unstable in >=1 arm (pairing kept)")
        keep = ~bad_any
        labels, games_arr, engineered = (
            labels[keep], games_arr[keep], engineered[keep])
        feats = {k: v[keep] for k, v in feats.items()}
    save()

    # ------------------------------------------------ decode and score
    from scipy.stats import binomtest

    arms = ("real", "uniform_tau", "rewired")
    per_seed_rows = []
    cell_acc: dict[str, list[float]] = {a: [] for a in arms}
    cell_names: list[str] = []
    pooled = {a: [] for a in arms}
    pooled_eng = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        perm = list(rng.permutation(qualifying))
        n_held = max(2, int(round(HELDOUT_FRACTION * len(qualifying))))
        held_games = sorted(perm[:n_held])
        train_games = sorted(perm[n_held:])
        train_label_counts = {
            lab: int((labels[np.isin(games_arr, train_games)] == lab).sum())
            for lab in LABELS
        }
        row: dict[str, Any] = {
            "seed": seed, "train_games": train_games,
            "held_games": held_games,
            "train_label_counts": train_label_counts,
            "arms": {},
        }
        for arm in arms:
            key = f"rewired_{seed}" if arm == "rewired" else arm
            result = fit_probe(
                feats[key], labels, games_arr, train_games, held_games)
            test = binomtest(result["pooled_correct"], result["pooled_n"],
                             0.25, alternative="greater")
            result["binomial_p_vs_0.25"] = float(test.pvalue)
            row["arms"][arm] = result
            pooled[arm].append(result["pooled_accuracy"])
            for game in held_games:
                cell_acc[arm].append(result["per_game"][game]["accuracy"])
        for game in held_games:
            cell_names.append(f"{game}@s{seed}")
        held_mask = np.isin(games_arr, held_games)
        eng_acc = float((engineered[held_mask] == labels[held_mask]).mean())
        row["engineered_pooled_accuracy"] = eng_acc
        pooled_eng.append(eng_acc)
        per_seed_rows.append(row)
        log(f"[seed {seed}] held {held_games} | " + " ".join(
            f"{a}={row['arms'][a]['pooled_accuracy']:.3f}"
            f"(p={row['arms'][a]['binomial_p_vs_0.25']:.4f},"
            f"C={row['arms'][a]['chosen_C']})"
            for a in arms) + f" eng={eng_acc:.3f}")
    report["per_seed"] = per_seed_rows

    def sign_test(a: list[float], b: list[float]) -> dict[str, Any]:
        diff = np.array(a) - np.array(b)
        pos = int((diff > 1e-12).sum())
        neg = int((diff < -1e-12).sum())
        ties = int(len(diff) - pos - neg)
        if pos + neg == 0:
            return {"n_cells": len(diff), "n_pos": pos, "n_neg": neg,
                    "ties": ties, "p_one_sided": 1.0}
        test = binomtest(pos, pos + neg, 0.5, alternative="greater")
        return {"n_cells": len(diff), "n_pos": pos, "n_neg": neg,
                "ties": ties, "p_one_sided": float(test.pvalue)}

    binom_rows = [
        {"seed": r["seed"],
         "k": r["arms"]["real"]["pooled_correct"],
         "n": r["arms"]["real"]["pooled_n"],
         "accuracy": round(r["arms"]["real"]["pooled_accuracy"], 4),
         "p": r["arms"]["real"]["binomial_p_vs_0.25"]}
        for r in per_seed_rows
    ]
    all_binom = all(r["p"] < ALPHA for r in binom_rows)
    vs_twin = sign_test(cell_acc["real"], cell_acc["uniform_tau"])
    vs_rewired = sign_test(cell_acc["real"], cell_acc["rewired"])
    paired_tests = {
        "binomial_vs_chance_real": {
            "per_seed": binom_rows, "all_seeds_significant": all_binom},
        "real_vs_uniform_tau": vs_twin,
        "real_vs_rewired": vs_rewired,
        "cells": cell_names,
        "cell_accuracies": {a: [round(v, 4) for v in cell_acc[a]]
                            for a in arms},
    }
    report["paired_tests"] = paired_tests

    means = {a: float(np.mean(pooled[a])) for a in arms}
    means["engineered"] = float(np.mean(pooled_eng))
    report["heldout_accuracy_mean_over_seeds"] = {
        k: round(v, 4) for k, v in means.items()}
    passed = bool(all_binom
                  and vs_twin["p_one_sided"] < ALPHA
                  and vs_rewired["p_one_sided"] < ALPHA)
    report["passed"] = passed
    report["peak_rss_gib"] = round(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**30, 2)
    report["elapsed_s"] = round(time.time() - started, 1)
    report["ram_at_end"] = _free_ram_note()
    save()
    log(f"RESULT: passed={passed} | real={means['real']:.4f} "
        f"uniform_tau={means['uniform_tau']:.4f} "
        f"rewired={means['rewired']:.4f} engineered={means['engineered']:.4f}"
        f" | binomial all-seeds={all_binom} "
        f"vs_twin p={vs_twin['p_one_sided']:.4f} "
        f"vs_rewired p={vs_rewired['p_one_sided']:.4f} | "
        f"peak RSS {report['peak_rss_gib']} GiB, "
        f"{report['elapsed_s']}s total")
    handle.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
