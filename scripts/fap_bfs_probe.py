#!/usr/bin/env python3
"""H-FAP-PROGRAMS instrument 2: breadth-first search for a level-1 program.

HYPOTHESIS (same registration as fap_program_premise.py, 2026-09-27): if the
dead games' level 1 really is a short exact program, then the reachable state
space under the legal action set is SMALL (the forensics measured 5-35 correct
actions) and a breadth-first enumeration with frame-hash deduplication will
find a scoring sequence in minutes. If BFS with a generous depth exhausts the
reachable states without scoring, level 1 is NOT a short program over the
probed action set, and the archetype-library premise is dead for that game.

This is forensic instrumentation over the strict-offline arcade: no agent, no
fly, score-ineligible. Nodes are deduplicated on timer-masked frame bytes so
the countdown strip does not explode the state space. Each node is reached by
replaying its action prefix after a RESET, which the forensics measured as
restoring the initial frame at 100% cell identity.

Click actions: ACTION6 is included only at --click-cells coordinates (if any),
because 64x64 click targets would make the branching factor 4096. The default
probes the directional/simple actions the frame declares legal.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import deque
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))


def _load_baseline() -> Any:
    path = ROOT / "scripts" / "evaluate_random_baseline.py"
    spec = importlib.util.spec_from_file_location("_flygi_fap_bfs_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True)
    parser.add_argument("--depth", type=int, default=10)
    parser.add_argument("--max-nodes", type=int, default=4000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--wake",
        type=int,
        default=1,
        help="action issued and discarded after each RESET (0 disables); "
        "the engine swallows the first post-reset action",
    )
    parser.add_argument(
        "--click-cells",
        default="",
        help="comma-separated x:y click targets to include as ACTION6 branches",
    )
    parser.add_argument(
        "--mask-rows", default="", help="comma-separated rows to zero before hashing"
    )
    parser.add_argument(
        "--mask-cols", default="", help="comma-separated cols to zero before hashing"
    )
    parser.add_argument(
        "--environments-dir", type=Path, default=ROOT / "environment_files"
    )
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    import numpy as np

    base = _load_baseline()
    runtime = base.load_arc_runtime()
    games = base.discover_games(runtime, args.environments_dir.resolve(), [args.game])
    if not games:
        raise SystemExit(f"game {args.game!r} not found")
    game = games[0]

    arcade = base._new_offline_arcade(runtime, args.environments_dir.resolve())
    scorecard_id = arcade.open_scorecard(
        tags=["diagnostic", "fap-bfs"], opaque={"game_id": game.game_id}
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

    from flygi.encoding.features import latest_grid

    mask_rows = [int(v) for v in args.mask_rows.split(",") if v != ""]
    mask_cols = [int(v) for v in args.mask_cols.split(",") if v != ""]
    clicks = [
        tuple(int(v) for v in cell.split(":"))
        for cell in args.click_cells.split(",")
        if cell
    ]

    def fingerprint(frame: Any) -> bytes:
        grid = np.asarray(latest_grid(frame), dtype=np.int16).copy()
        if mask_rows:
            grid[mask_rows, :] = 0
        if mask_cols:
            grid[:, mask_cols] = 0
        return grid.tobytes()

    def act(identifier: int, payload: dict[str, int]) -> Any:
        action = runtime.GameAction.from_id(identifier)
        if payload:
            action.set_data(payload)
        response = environment.step(action, data=payload or {}, reasoning=None)
        if response is None:
            raise SystemExit("environment step returned None")
        return response

    def replay(prefix: list[tuple[int, dict[str, int]]]) -> Any:
        frame = act(0, {})
        if args.wake:
            # MEASURED 2026-09-27 (sc25): the engine swallows the first action
            # after every RESET completely -- identical frames regardless of
            # which action wakes it -- so replays issue one throwaway action.
            frame = act(args.wake, {})
        for identifier, payload in prefix:
            frame = act(identifier, payload)
        return frame

    initial = replay([])
    base_score = int(getattr(initial, "levels_completed", 0) or 0)

    def branches(frame: Any) -> list[tuple[int, dict[str, int]]]:
        legal = {getattr(a, "value", a) for a in getattr(frame, "available_actions", [])}
        out: list[tuple[int, dict[str, int]]] = []
        for identifier in (1, 2, 3, 4, 5):
            if identifier in legal:
                out.append((identifier, {}))
        if 6 in legal:
            out.extend((6, {"x": x, "y": y}) for x, y in clicks)
        return out

    seen: set[bytes] = {fingerprint(initial)}
    queue: deque[list[tuple[int, dict[str, int]]]] = deque([[]])
    expanded = 0
    steps_executed = 0
    winner: list[tuple[int, dict[str, int]]] | None = None
    frontier_report = -1

    while queue and expanded < args.max_nodes and winner is None:
        prefix = queue.popleft()
        if len(prefix) >= args.depth:
            continue
        if len(prefix) != frontier_report:
            frontier_report = len(prefix)
            print(
                f"depth {frontier_report}: {len(seen)} states, "
                f"{expanded} nodes expanded, {steps_executed} env steps",
                flush=True,
            )
        frame = replay(prefix)
        steps_executed += len(prefix) + 1
        expanded += 1
        for identifier, payload in branches(frame):
            frame = replay(prefix)  # fresh copy of the node
            steps_executed += len(prefix) + 1
            after = act(identifier, payload)
            steps_executed += 1
            child = prefix + [(identifier, payload)]
            score = int(getattr(after, "levels_completed", 0) or 0)
            if score > base_score or str(getattr(after, "state", "")).endswith("WIN"):
                winner = child
                break
            key = fingerprint(after)
            if key not in seen:
                seen.add(key)
                queue.append(child)

    verdict = {
        "game_id": game.game_id,
        "distinct_states": len(seen),
        "nodes_expanded": expanded,
        "env_steps": steps_executed,
        "depth_limit": args.depth,
        "click_cells": clicks,
        "program_found": winner is not None,
        "program": [
            {"action": identifier, **payload} for identifier, payload in winner or []
        ],
        "program_length": len(winner) if winner else None,
    }
    print(json.dumps(verdict, indent=2))
    if args.output:
        args.output.write_text(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
