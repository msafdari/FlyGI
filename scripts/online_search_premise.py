#!/usr/bin/env python3
"""H-ONLINE-SEARCH premise-killer: budgeted online BFS over all 25 public games.

PREREGISTRATION (EXPERIMENTS.yaml, H-ONLINE-SEARCH, updated 2026-09-30): the
budget is FIXED at 4,000 expanded nodes and depth 16 per game; the endpoint is
the number of games where the search finds a level-1-completing program within
budget; the decision bar is >= 5 of 25 games. This script is the instrument;
it does not move the bar. Secondary endpoints reported alongside: distinct
state counts and depth-to-first-score (program length) per game.

This is forensic instrumentation over the strict-offline arcade: no agent, no
fly, score-ineligible. It EXTENDS scripts/fap_bfs_probe.py (BFS with
frame-byte dedup, RESET + action-prefix replay, throwaway wake action for the
measured post-reset swallow) with three automated upgrades:

1. SCENE-DERIVED CLICK BRANCHING. ACTION6 branches come from the champion's
   own scene machinery (src/flygi/controller/scene.py): conservative
   background inference, per-color four-connected components capped by
   components_for_coverage(limit=64), then component_click_candidates with
   the champion's config values (max_tier=2, max_clicks_per_tier=64, from
   src/flygi/config.py ControllerConfig defaults). DECLARED CAP: the top
   CLICK_CAP=12 candidates per node, stable-sorted by (tier ascending,
   component area descending, emission order). A click-legal frame with zero
   component candidates (fully uniform scene) falls back to one click at the
   grid centre (32, 32), mirroring the policy's last-resort fallback. Simple
   actions 1-5 are included whenever the frame declares them legal, so the
   branching factor is at most 5 + 12 = 17.

2. AUTO WAKE DETECTION (per game, before the search). Fresh RESET, one legal
   probe action, masked-grid diff: if the first probe leaves the masked grid
   identical AND repeating the same probe then changes it, the engine
   swallowed the first post-reset action (the quirk MEASURED on sc25
   2026-09-27) and every replay issues that probe once as a discarded wake
   action. Probes that change nothing twice are treated as no-ops and the
   next legal probe is tried (up to 3 probes, each from its own fresh
   RESET). All-probes-no-op => wake disabled, recorded as undetermined.

3. AUTO TIMER-LINE MASKING (per game, before wake detection). DECLARED RULE:
   sample TIMER_SAMPLE_STEPS=24 random legal actions from a fresh RESET
   (seeded random walk; clicks drawn from unmasked scene candidates); a
   border line (row or col with index < 4 or >= 60, matching the champion's
   VolatileMaskConfig.border_width=4) is masked before hashing AND before
   component extraction when it changed in >= 60% of the effective sampled
   transitions (those where anything on the grid changed) and in at least 4
   of them. Interior lines are never masked: moving objects must stay part
   of state identity.

State identity refines fap_bfs_probe: BLAKE2b-128 over the timer-masked grid
bytes plus the legal-action mask (same ingredients as the champion's
canonical_state_key). Adding the legal-action mask can only split states,
never merge them, so BFS completeness is preserved.

DECLARED LIMITATION (unchanged from fap_bfs_probe): replay assumes RESET
restores the initial frame exactly, as the forensics measured at 100% cell
identity on the probed games; a stochastic game would drift and its record
here would understate reachability. Replay drift is not separately verified.

Operational stop, distinct from the preregistered budget: a game exceeding
--wall-seconds (default 1500 s ~ 25 min) is stopped where it stands and
recorded with partial=true.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.util
import json
import os
import random
import subprocess
import sys
import time
from collections import deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

import numpy as np  # noqa: E402

from flygi.controller.scene import (  # noqa: E402
    component_click_candidates,
    components_for_coverage,
    extract_components,
    infer_background,
)
from flygi.encoding.features import GRID_SIZE, latest_grid  # noqa: E402

# --- Preregistered budget (EXPERIMENTS.yaml H-ONLINE-SEARCH; immutable) -----
PREREGISTERED_MAX_NODES = 4000
PREREGISTERED_DEPTH = 16
DECISION_BAR = ">= 5 of 25 games with a level-1-completing program found within budget"

# --- Declared instrument constants (plumbing, not the budget) ---------------
CLICK_CAP = 12  # top candidates per node by (tier asc, component area desc)
CHAMPION_COMPONENT_LIMIT = 64  # src/flygi/config.py ControllerConfig.component_limit
CHAMPION_MAX_TIER = 2  # ControllerConfig.max_candidate_tier
CHAMPION_MAX_CLICKS_PER_TIER = 64  # ControllerConfig.max_clicks_per_tier
TIMER_SAMPLE_STEPS = 24
TIMER_BORDER_WIDTH = 4  # matches champion VolatileMaskConfig.border_width
TIMER_CHANGE_FRACTION = 0.60
TIMER_MIN_CHANGES = 4
WAKE_MAX_PROBES = 3
FALLBACK_CLICK = (32, 32)

_SIMPLE_ACTIONS = (1, 2, 3, 4, 5)
_CLICK_ACTION = 6


def _load_baseline() -> Any:
    path = ROOT / "scripts" / "evaluate_random_baseline.py"
    spec = importlib.util.spec_from_file_location("_flygi_online_search_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _free_ram_note() -> str:
    """Best-effort free-RAM measurement (memory rule: measure before launch)."""

    try:
        raw = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=10).stdout
        stats = {}
        for line in raw.splitlines():
            if ":" in line and "Pages" in line:
                key, value = line.split(":", 1)
                stats[key.strip()] = int(value.strip().rstrip("."))
        page = 16384
        free = (stats.get("Pages free", 0) + stats.get("Pages speculative", 0)) * page
        inactive = stats.get("Pages inactive", 0) * page
        return f"free={free / 2**30:.2f}GiB inactive(reclaimable)={inactive / 2**30:.2f}GiB"
    except Exception as exc:  # pragma: no cover - measurement is best-effort
        return f"unavailable ({exc})"


class GameProbe:
    """One game's masked-BFS program search on the strict-offline arcade."""

    def __init__(
        self,
        runtime: Any,
        environment: Any,
        game_id: str,
        *,
        max_nodes: int,
        depth: int,
        click_cap: int,
        wall_seconds: float,
        walk_seed: int,
        log: Any,
    ) -> None:
        self.runtime = runtime
        self.environment = environment
        self.game_id = game_id
        self.max_nodes = max_nodes
        self.depth = depth
        self.click_cap = click_cap
        self.wall_seconds = wall_seconds
        self.walk_seed = walk_seed
        self.log = log
        self.started = time.monotonic()
        self.env_steps_total = 0
        self.mask_rows: list[int] = []
        self.mask_cols: list[int] = []
        self.wake: tuple[int, dict[str, int]] | None = None
        self.wake_evidence = "not probed"

    # -- environment primitives ----------------------------------------------

    def act(self, identifier: int, payload: dict[str, int]) -> Any:
        action = self.runtime.GameAction.from_id(identifier)
        if payload:
            action.set_data(payload)
        response = self.environment.step(action, data=payload or {}, reasoning=None)
        if response is None:
            raise SystemExit("environment step returned None")
        self.env_steps_total += 1
        return response

    def replay(self, prefix: list[tuple[int, dict[str, int]]]) -> Any:
        frame = self.act(0, {})
        if self.wake is not None:
            # MEASURED 2026-09-27 (sc25): the engine swallows the first action
            # after every RESET completely; the auto-detected probe is issued
            # once and discarded. Games without the quirk skip this entirely.
            frame = self.act(*self.wake)
        for identifier, payload in prefix:
            frame = self.act(identifier, payload)
        return frame

    @staticmethod
    def legal_ids(frame: Any) -> set[int]:
        return {
            int(getattr(action, "value", action))
            for action in getattr(frame, "available_actions", [])
        }

    def timed_out(self) -> bool:
        return time.monotonic() - self.started > self.wall_seconds

    # -- masked grids and state identity --------------------------------------

    def masked_grid(self, frame: Any) -> np.ndarray:
        grid = np.asarray(latest_grid(frame), dtype=np.int16).copy()
        if self.mask_rows:
            grid[self.mask_rows, :] = -1
        if self.mask_cols:
            grid[:, self.mask_cols] = -1
        return grid

    def ignored_mask(self) -> np.ndarray:
        mask = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.bool_)
        if self.mask_rows:
            mask[self.mask_rows, :] = True
        if self.mask_cols:
            mask[:, self.mask_cols] = True
        return mask

    def fingerprint(self, frame: Any) -> bytes:
        legal = bytes(1 if i in self.legal_ids(frame) else 0 for i in range(7))
        return hashlib.blake2b(
            self.masked_grid(frame).tobytes() + legal, digest_size=16
        ).digest()

    # -- scene-derived click branching ----------------------------------------

    def derive_clicks(self, frame: Any, *, use_mask: bool = True) -> list[tuple[int, dict[str, int]]]:
        grid = latest_grid(frame)
        ignored = self.ignored_mask() if use_mask else None
        background = infer_background(grid, ignored_mask=ignored)
        components = components_for_coverage(
            extract_components(
                grid,
                background_color=background,
                ignored_mask=ignored,
                minimum_area=1,
            ),
            limit=CHAMPION_COMPONENT_LIMIT,
        )
        candidates = component_click_candidates(
            components,
            max_tier=CHAMPION_MAX_TIER,
            max_clicks_per_tier=CHAMPION_MAX_CLICKS_PER_TIER,
        )
        if not candidates:
            # Last-resort centre click on a uniform scene, as the policy does.
            return [(_CLICK_ACTION, {"x": FALLBACK_CLICK[0], "y": FALLBACK_CLICK[1]})]
        area = {component.index: component.area for component in components}
        ranked = sorted(
            candidates, key=lambda c: (c.tier, -area[c.component_index])
        )  # stable: emission order breaks ties
        return [
            (_CLICK_ACTION, {"x": candidate.x, "y": candidate.y})
            for candidate in ranked[: self.click_cap]
        ]

    def branches(self, frame: Any) -> list[tuple[int, dict[str, int]]]:
        legal = self.legal_ids(frame)
        out: list[tuple[int, dict[str, int]]] = [
            (identifier, {}) for identifier in _SIMPLE_ACTIONS if identifier in legal
        ]
        if _CLICK_ACTION in legal:
            out.extend(self.derive_clicks(frame))
        return out

    # -- automated setup: timer mask, then wake detection ---------------------

    def detect_timer_mask(self) -> None:
        """DECLARED RULE (see module docstring): random walk, then mask border
        lines changing in >= 60% of effective transitions (min 4)."""

        rng = random.Random(self.walk_seed)
        frame = self.act(0, {})
        grids: list[list[np.ndarray]] = [[np.asarray(latest_grid(frame), dtype=np.int16)]]
        for _ in range(TIMER_SAMPLE_STEPS):
            legal = self.legal_ids(frame)
            options: list[tuple[int, dict[str, int]]] = [
                (identifier, {}) for identifier in _SIMPLE_ACTIONS if identifier in legal
            ]
            if _CLICK_ACTION in legal:
                options.extend(self.derive_clicks(frame, use_mask=False))
            if not options:
                # GAME_OVER / needs-reset mid-walk: start a new segment so no
                # comparison spans a reset.
                frame = self.act(0, {})
                grids.append([np.asarray(latest_grid(frame), dtype=np.int16)])
                continue
            frame = self.act(*rng.choice(options))
            grids[-1].append(np.asarray(latest_grid(frame), dtype=np.int16))

        border = [
            index
            for index in range(GRID_SIZE)
            if index < TIMER_BORDER_WIDTH or index >= GRID_SIZE - TIMER_BORDER_WIDTH
        ]
        row_changes = {index: 0 for index in border}
        col_changes = {index: 0 for index in border}
        effective = 0
        for segment in grids:
            for before, after in zip(segment, segment[1:], strict=False):
                if not (before != after).any():
                    continue  # swallowed or no-op transition: not informative
                effective += 1
                for index in border:
                    if (before[index, :] != after[index, :]).any():
                        row_changes[index] += 1
                    if (before[:, index] != after[:, index]).any():
                        col_changes[index] += 1
        threshold = max(TIMER_MIN_CHANGES, int(np.ceil(TIMER_CHANGE_FRACTION * effective)))
        if effective >= TIMER_MIN_CHANGES:
            self.mask_rows = [index for index in border if row_changes[index] >= threshold]
            self.mask_cols = [index for index in border if col_changes[index] >= threshold]
        self.timer_effective_transitions = effective
        self.log(
            f"[{self.game_id}] timer mask: rows={self.mask_rows} cols={self.mask_cols} "
            f"({effective} effective transitions)"
        )

    def detect_wake(self) -> None:
        """Masked-grid swallow test; see module docstring for the protocol."""

        frame = self.act(0, {})
        legal = self.legal_ids(frame)
        probes: list[tuple[int, dict[str, int]]] = [
            (identifier, {}) for identifier in _SIMPLE_ACTIONS if identifier in legal
        ]
        if _CLICK_ACTION in legal:
            probes.extend(self.derive_clicks(frame))
        probes = probes[:WAKE_MAX_PROBES]
        if not probes:
            self.wake = None
            self.wake_evidence = "no legal probe action on the initial frame"
            return

        for attempt, probe in enumerate(probes):
            if attempt > 0:
                frame = self.act(0, {})
            reference = self.masked_grid(frame)
            first = self.masked_grid(self.act(*probe))
            if (first != reference).any():
                self.wake = None
                self.wake_evidence = f"probe {probe} changed the masked grid on step 1"
                return
            second = self.masked_grid(self.act(*probe))
            if (second != reference).any():
                self.wake = probe
                self.wake_evidence = (
                    f"probe {probe}: step 1 left the masked grid identical, the "
                    "identical step 2 changed it -- post-reset swallow detected"
                )
                return
        self.wake = None
        self.wake_evidence = (
            f"undetermined: {len(probes)} probe(s) were no-ops twice from fresh "
            "resets; wake disabled"
        )

    # -- the budgeted search ---------------------------------------------------

    def search(self) -> dict[str, Any]:
        self.detect_timer_mask()
        self.detect_wake()
        self.log(f"[{self.game_id}] wake={'ON ' + str(self.wake) if self.wake else 'off'}: "
                 f"{self.wake_evidence}")
        setup_steps = self.env_steps_total

        initial = self.replay([])
        base_score = int(getattr(initial, "levels_completed", 0) or 0)

        seen: set[bytes] = {self.fingerprint(initial)}
        queue: deque[tuple[list[tuple[int, dict[str, int]]], list[tuple[int, dict[str, int]]]]]
        queue = deque([([], self.branches(initial))])
        expanded = 0
        depth_expanded = 0
        depth_generated = 0
        winner: list[tuple[int, dict[str, int]]] | None = None
        frontier_report = -1
        partial = False

        while queue and expanded < self.max_nodes and winner is None:
            if self.timed_out():
                partial = True
                break
            prefix, node_branches = queue.popleft()
            expanded += 1
            depth_expanded = max(depth_expanded, len(prefix))
            if len(prefix) != frontier_report:
                frontier_report = len(prefix)
                self.log(
                    f"[{self.game_id}] depth {frontier_report}: {len(seen)} states, "
                    f"{expanded} nodes, {self.env_steps_total} env steps, "
                    f"{time.monotonic() - self.started:.0f}s"
                )
            for identifier, payload in node_branches:
                if self.timed_out():
                    partial = True
                    break
                self.replay(prefix)
                after = self.act(identifier, payload)
                child = prefix + [(identifier, payload)]
                depth_generated = max(depth_generated, len(child))
                score = int(getattr(after, "levels_completed", 0) or 0)
                if score > base_score or str(getattr(after, "state", "")).endswith("WIN"):
                    winner = child
                    break
                key = self.fingerprint(after)
                if key in seen:
                    continue
                seen.add(key)
                if len(child) < self.depth:
                    child_branches = self.branches(after)
                    if child_branches:
                        queue.append((child, child_branches))
            if partial:
                break

        if winner is None and expanded >= self.max_nodes:
            outcome = "node-budget-exhausted"
        elif winner is not None:
            outcome = "program-found"
        elif partial:
            outcome = "wall-clock-partial"
        else:
            outcome = "state-space-exhausted"

        return {
            "game_id": self.game_id,
            "distinct_states": len(seen),
            "nodes_expanded": expanded,
            "env_steps": self.env_steps_total - setup_steps,
            "env_steps_total": self.env_steps_total,
            "depth_limit": self.depth,
            "max_depth_expanded": depth_expanded,
            "max_depth_generated": depth_generated,
            "click_cap": self.click_cap,
            "timer_mask_rows": self.mask_rows,
            "timer_mask_cols": self.mask_cols,
            "timer_effective_transitions": self.timer_effective_transitions,
            "wake_swallow_detected": self.wake is not None,
            "wake_action": None
            if self.wake is None
            else {"action": self.wake[0], **self.wake[1]},
            "wake_evidence": self.wake_evidence,
            "base_score": base_score,
            "program_found": winner is not None,
            "program": [
                {"action": identifier, **payload} for identifier, payload in winner or []
            ],
            "program_length": len(winner) if winner else None,
            "partial": partial,
            "outcome": outcome,
            "wall_seconds": round(time.monotonic() - self.started, 1),
        }


def _atomic_write(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2))
    temporary.replace(path)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", default="all", help="comma-separated games or 'all'")
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--max-nodes",
        type=int,
        default=PREREGISTERED_MAX_NODES,
        help="preregistered: 4000; override only for mechanical smoke tests",
    )
    parser.add_argument(
        "--depth",
        type=int,
        default=PREREGISTERED_DEPTH,
        help="preregistered: 16; override only for mechanical smoke tests",
    )
    parser.add_argument("--click-cap", type=int, default=CLICK_CAP)
    parser.add_argument("--wall-seconds", type=float, default=1500.0)
    parser.add_argument(
        "--environments-dir", type=Path, default=ROOT / "environment_files"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results" / "online_search_premise.json"
    )
    parser.add_argument(
        "--log", type=Path, default=ROOT / "results" / "online_search_premise.log"
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    log_handle = args.log.open("a")

    def log(message: str) -> None:
        stamped = f"{time.strftime('%H:%M:%S')} {message}"
        print(stamped, flush=True)
        log_handle.write(stamped + "\n")
        log_handle.flush()

    base = _load_baseline()
    runtime = base.load_arc_runtime()
    requested = ["all"] if args.games.strip().lower() == "all" else args.games.split(",")
    games = base.discover_games(runtime, args.environments_dir.resolve(), requested)

    ram_note = _free_ram_note()
    log(
        f"H-ONLINE-SEARCH sweep: {len(games)} games, budget {args.max_nodes} nodes x "
        f"depth {args.depth} (preregistered {PREREGISTERED_MAX_NODES} x "
        f"{PREREGISTERED_DEPTH}), click cap {args.click_cap}, wall "
        f"{args.wall_seconds:.0f}s/game, seed {args.seed}; RAM {ram_note}"
    )

    payload: dict[str, Any] = {
        "experiment": "H-ONLINE-SEARCH",
        "preregistered_budget": {
            "max_nodes": PREREGISTERED_MAX_NODES,
            "depth": PREREGISTERED_DEPTH,
            "decision_bar": DECISION_BAR,
        },
        "run_budget": {"max_nodes": args.max_nodes, "depth": args.depth},
        "instrument": {
            "click_cap": args.click_cap,
            "click_ranking": "tier asc, component area desc, emission order (stable)",
            "champion_scene_caps": {
                "component_limit": CHAMPION_COMPONENT_LIMIT,
                "max_candidate_tier": CHAMPION_MAX_TIER,
                "max_clicks_per_tier": CHAMPION_MAX_CLICKS_PER_TIER,
            },
            "timer_rule": (
                f"border lines (outer {TIMER_BORDER_WIDTH}) changing in >= "
                f"{TIMER_CHANGE_FRACTION:.0%} of effective random-walk transitions "
                f"(min {TIMER_MIN_CHANGES}) over {TIMER_SAMPLE_STEPS} sampled steps"
            ),
            "state_identity": "blake2b-128(masked grid bytes + legal-action mask)",
            "wall_seconds_per_game": args.wall_seconds,
        },
        "seed": args.seed,
        "ram_at_start": ram_note,
        "games": {},
        "summary": {},
    }

    for position, game in enumerate(games, start=1):
        log(f"[{game.game_id}] starting ({position}/{len(games)})")
        arcade = base._new_offline_arcade(runtime, args.environments_dir.resolve())
        scorecard_id = arcade.open_scorecard(
            tags=["diagnostic", "online-search-premise"],
            opaque={"game_id": game.game_id},
        )
        environment_seed, _ = base.derived_run_seeds(args.seed, game.game_id)
        base._seed_process_for_environment(environment_seed)
        environment = arcade.make(
            game.game_id,
            seed=environment_seed,
            scorecard_id=scorecard_id,
            save_recording=False,
            include_frame_data=False,
        )
        probe = GameProbe(
            runtime,
            environment,
            game.game_id,
            max_nodes=args.max_nodes,
            depth=args.depth,
            click_cap=args.click_cap,
            wall_seconds=args.wall_seconds,
            walk_seed=environment_seed,
            log=log,
        )
        try:
            record = probe.search()
        except Exception as exc:  # record the failure, keep sweeping
            record = {
                "game_id": game.game_id,
                "error": f"{type(exc).__name__}: {exc}",
                "program_found": False,
                "partial": True,
                "outcome": "error",
                "wall_seconds": round(time.monotonic() - probe.started, 1),
            }
            log(f"[{game.game_id}] ERROR {record['error']}")
        payload["games"][game.game_id] = record
        found = [
            key for key, row in payload["games"].items() if row.get("program_found")
        ]
        payload["summary"] = {
            "games_completed": len(payload["games"]),
            "games_with_level1_program": len(found),
            "games_found": found,
            "decision_bar": DECISION_BAR,
            "bar_met_so_far": len(found) >= 5,
        }
        _atomic_write(args.output, payload)
        log(
            f"[{game.game_id}] done: outcome={record.get('outcome')} "
            f"states={record.get('distinct_states')} nodes={record.get('nodes_expanded')} "
            f"found={record.get('program_found')} len={record.get('program_length')} "
            f"partial={record.get('partial')} wall={record.get('wall_seconds')}s "
            f"| running tally {len(found)}/{len(payload['games'])} found"
        )
        del environment, arcade, probe
        gc.collect()

    summary = payload["summary"]
    log(
        f"SWEEP COMPLETE: {summary['games_with_level1_program']} of "
        f"{summary['games_completed']} games with a level-1 program; bar "
        f"'{DECISION_BAR}' -> {'MET' if summary['bar_met_so_far'] else 'NOT MET'}"
    )
    log_handle.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
