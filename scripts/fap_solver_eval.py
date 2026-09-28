#!/usr/bin/env python3
"""Offline milestone gate for the FAP library (H-FAP-PROGRAMS follow-up).

The milestone, per the operating directive, is not "it runs": it is "it
beats the trivial alternative". The trivial alternative here is random
legal play, which has scored 0 levels on the template games in every
600-action battery row ever run. This harness plays each requested game
with the FapExecutor driving whenever it matches and random-legal play
when it abstains, and reports levels completed. It also runs the full
25-game sweep as an ABSTENTION AUDIT: on games the library was not built
for, it must match rarely and never crash, so seating it in the deployed
policy cannot cost the champion anything.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))


def _load_baseline() -> Any:
    path = ROOT / "scripts" / "evaluate_random_baseline.py"
    spec = importlib.util.spec_from_file_location("_flygi_fap_eval_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--games", nargs="+", default=["all"])
    parser.add_argument("--budget", type=int, default=300)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--environments-dir", type=Path, default=ROOT / "environment_files"
    )
    parser.add_argument(
        "--output", type=Path, default=ROOT / "results" / "fap_solver_eval.json"
    )
    args = parser.parse_args()

    import numpy as np

    from flygi.controller.fap_library import FapExecutor
    from flygi.encoding.features import latest_grid

    base = _load_baseline()
    runtime = base.load_arc_runtime()
    games = base.discover_games(runtime, args.environments_dir.resolve(), args.games)
    arcade = base._new_offline_arcade(runtime, args.environments_dir.resolve())
    scorecard_id = arcade.open_scorecard(
        tags=["diagnostic", "fap-solver-eval"], opaque={}
    )

    report: dict[str, Any] = {"budget": args.budget, "games": {}}
    for game in games:
        environment_seed, policy_seed = base.derived_run_seeds(args.seed, game.game_id)
        base._seed_process_for_environment(environment_seed)
        environment = arcade.make(
            game.game_id,
            seed=environment_seed,
            scorecard_id=scorecard_id,
            save_recording=False,
            include_frame_data=False,
        )
        random_policy = base.RandomLegalPolicy(runtime.GameAction, seed=policy_seed)
        executor = FapExecutor()
        frame = environment.observation_space
        fap_actions = 0
        random_actions = 0
        levels = 0
        for _ in range(args.budget):
            state = str(getattr(frame, "state", ""))
            if state.endswith("WIN"):
                break
            try:
                grid = np.asarray(latest_grid(frame), dtype=np.int16)
            except Exception:
                grid = None  # transition frames can arrive empty
            if grid is not None:
                executor.observe(grid)
            legal = {
                getattr(a, "value", a)
                for a in getattr(frame, "available_actions", [])
            }
            step = None
            if state.endswith("NOT_FINISHED") and grid is not None:
                proposal = executor.propose(grid)
                if proposal is not None and proposal.action in legal:
                    step = proposal
            if step is not None:
                action = runtime.GameAction.from_id(step.action)
                payload: dict[str, int] = {}
                if step.action == 6:
                    payload = {"x": int(step.x), "y": int(step.y)}
                    action.set_data(payload)
                fap_actions += 1
            else:
                action = random_policy.choose_action(frame)
                payload = base._action_payload(action)
                random_actions += 1
            response = environment.step(action, data=payload, reasoning=None)
            if response is None:
                break
            frame = response
            levels = int(getattr(frame, "levels_completed", 0) or 0)
        gid = game.game_id.split("-")[0]
        report["games"][gid] = {
            "levels": levels,
            "win_levels": getattr(frame, "win_levels", None),
            "fap_actions": fap_actions,
            "random_actions": random_actions,
            "matched": executor.describe()["matched"],
            "final_state": str(getattr(frame, "state", None)),
        }
        print(f"{gid}: {report['games'][gid]}", flush=True)
    args.output.write_text(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
