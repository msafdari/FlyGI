#!/usr/bin/env python3
"""sc25 level-3 probe driver.

Auto-plays levels 1-2 with the FapExecutor (measured-solved), then executes
an optional JSON program with a per-step render dump. Forensic tool only.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


base = _load("b", ROOT / "scripts" / "evaluate_random_baseline.py")
premise = _load("prem", ROOT / "scripts" / "fap_program_premise.py")

import numpy as np  # noqa: E402

from flygi.controller.fap_library import FapExecutor  # noqa: E402
from flygi.encoding.features import latest_grid  # noqa: E402


def grid_of(frame):
    try:
        return np.asarray(latest_grid(frame), dtype=np.int16)
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--program", type=Path, default=None)
    ap.add_argument("--out", type=Path, default=Path("/tmp/fap_ext/sc25/run"))
    ap.add_argument("--to-level", type=int, default=2, help="auto-play until levels_completed reaches this")
    ap.add_argument("--budget", type=int, default=400)
    ap.add_argument("--dump-auto", action="store_true", help="also dump frames during auto-play")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    rt = base.load_arc_runtime()
    g = base.discover_games(rt, ROOT / "environment_files", ["sc25"])[0]
    arc = base._new_offline_arcade(rt, ROOT / "environment_files")
    sc = arc.open_scorecard(tags=["diag", "sc25-door"], opaque={})
    env_seed, _ = base.derived_run_seeds(0, g.game_id)
    base._seed_process_for_environment(env_seed)
    env = arc.make(g.game_id, seed=env_seed, scorecard_id=sc,
                   save_recording=False, include_frame_data=False)

    executor = FapExecutor()
    frame = env.observation_space
    auto_actions = 0
    prev_levels = 0
    for step_index in range(args.budget):
        levels = int(getattr(frame, "levels_completed", 0) or 0)
        state = str(getattr(frame, "state", ""))
        if levels != prev_levels:
            executor.notify_level_advance()
            prev_levels = levels
        if levels >= args.to_level and state.endswith("NOT_FINISHED"):
            break
        grid = grid_of(frame)
        if grid is not None:
            executor.observe(grid)
        legal = {getattr(a, "value", a) for a in getattr(frame, "available_actions", [])}
        step = None
        if state.endswith("NOT_FINISHED") and grid is not None:
            proposal = executor.propose(grid)
            if proposal is not None and proposal.action in legal:
                step = proposal
        if step is None:
            print(f"[auto {auto_actions}] executor abstained at levels={levels} state={state}; stopping auto-play")
            break
        action = rt.GameAction.from_id(step.action)
        payload = {}
        if step.action == 6:
            payload = {"x": int(step.x), "y": int(step.y)}
            action.set_data(payload)
        response = env.step(action, data=payload, reasoning=None)
        auto_actions += 1
        if args.dump_auto:
            gnow = grid_of(response)
            if gnow is not None:
                (args.out / f"auto_{auto_actions:03d}_a{step.action}.txt").write_text(
                    premise.render_grid(gnow))
        if response is None:
            print("env.step returned None during auto-play")
            return 1
        frame = response

    levels = int(getattr(frame, "levels_completed", 0) or 0)
    print(f"AUTO-PLAY done: {auto_actions} actions, levels_completed={levels}, "
          f"state={getattr(frame, 'state', '')}, score={getattr(frame, 'score', None)}")
    print(f"available_actions={[getattr(a,'value',a) for a in getattr(frame,'available_actions',[])]}")
    grid = grid_of(frame)
    if grid is not None:
        (args.out / "L_start.txt").write_text(premise.render_grid(grid))
        print(f"wrote {args.out}/L_start.txt")

    if args.program is None:
        return 0

    steps = json.loads(args.program.read_text())
    prev_grid = grid
    for i, spec in enumerate(steps, start=1):
        aid = int(spec["action"])
        action = rt.GameAction.from_id(aid)
        payload = {}
        if aid == 6:
            payload = {"x": int(spec["x"]), "y": int(spec["y"])}
            action.set_data(payload)
        frame = env.step(action, data=payload, reasoning=None)
        if frame is None:
            print(f"[{i}] step returned None")
            return 1
        gnow = grid_of(frame)
        changed = None
        if gnow is not None and prev_grid is not None and gnow.shape == prev_grid.shape:
            changed = int((gnow != prev_grid).sum())
        info = dict(
            i=i, action=aid, payload=payload or None,
            state=str(getattr(frame, "state", "")),
            levels=int(getattr(frame, "levels_completed", 0) or 0),
            score=getattr(frame, "score", None),
            changed_cells=changed,
            avail=[getattr(a, "value", a) for a in getattr(frame, "available_actions", [])],
        )
        print(json.dumps(info))
        if gnow is not None:
            tag = f"p{i:03d}_a{aid}" + (f"_x{payload['x']}y{payload['y']}" if payload else "")
            (args.out / (tag + ".txt")).write_text(premise.render_grid(gnow))
            prev_grid = gnow
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
