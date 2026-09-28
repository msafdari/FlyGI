#!/usr/bin/env python3
"""H-FAP-PROGRAMS premise-killer: can a hand-written exact program fall level 1?

HYPOTHESIS (registered under H-DEAD-GAMES-TAXONOMY's follow-up, 2026-09-27):
the forensics concluded level 1 of every dead game is a SHORT EXACT PROGRAM
whose goal is displayed on screen. The fixed-action-pattern library plan
(recognize the archetype, release the matching program) rests entirely on
that premise, so before ANY library is built, the cheapest killer runs:
a human/Claude reads the rendered frames and writes the exact program by
hand. If even a hand-authored program cannot complete level 1, the "short
exact program" claim is wrong (or the games require information not on the
screen) and the library premise is DEAD before a line of it exists.

TRIVIAL ALTERNATIVE (named per the operating directive): random legal play,
already measured at 0 levels on these games across every 600-action battery
row. Any hand program that falls a level beats it; failing to beat "random
never wins here" kills the premise.

This tool has two modes and NO agent code in the loop -- it is forensic
instrumentation, deliberately fly-free and score-ineligible:

  --dump             reset the game and write frame renders after each step
                     of an optional --program prefix, for reading.
  --program FILE     execute a JSON action list and report level transitions.

Program JSON: a list of steps, each {"action": 0-6, "x": int, "y": int}
(x/y only for action 6; action 0 is RESET). Frames render as 64x64 text
using one hex digit per colour, plus a colour census, to the --out dir.
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
    spec = importlib.util.spec_from_file_location("_flygi_fap_premise_base", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def render_grid(grid: Any) -> str:
    import numpy as np

    array = np.asarray(grid, dtype=np.int16)
    rows = ["".join(format(int(v) % 16, "x") for v in row) for row in array]
    header = "    " + "".join(str(c % 10) for c in range(array.shape[1]))
    body = "\n".join(f"{r:>3d} {line}" for r, line in enumerate(rows))
    counts = np.bincount(array.ravel(), minlength=16)
    census = " ".join(f"{format(c, 'x')}:{int(n)}" for c, n in enumerate(counts) if n)
    return f"{header}\n{body}\ncolours {census}"


def frame_summary(frame: Any) -> dict[str, Any]:
    return {
        "state": str(getattr(frame, "state", None)),
        "score": getattr(frame, "levels_completed", None),
        "win_levels": getattr(frame, "win_levels", None),
        "available_actions": [
            getattr(a, "value", a) for a in getattr(frame, "available_actions", [])
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game", required=True)
    parser.add_argument("--program", type=Path, default=None)
    parser.add_argument("--dump", action="store_true", help="write frame renders")
    parser.add_argument("--out", type=Path, default=Path("/tmp/fap_premise"))
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument(
        "--environments-dir", type=Path, default=ROOT / "environment_files"
    )
    args = parser.parse_args()

    base = _load_baseline()
    runtime = base.load_arc_runtime()
    games = base.discover_games(runtime, args.environments_dir.resolve(), [args.game])
    if not games:
        raise SystemExit(f"game {args.game!r} not found")
    game = games[0]

    steps: list[dict[str, Any]] = []
    if args.program is not None:
        steps = json.loads(args.program.read_text())
        if not isinstance(steps, list):
            raise SystemExit("program must be a JSON list of steps")

    arcade = base._new_offline_arcade(runtime, args.environments_dir.resolve())
    scorecard_id = arcade.open_scorecard(
        tags=["diagnostic", "fap-premise"],
        opaque={"game_id": game.game_id, "seed": args.seed, "steps": len(steps)},
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
    frame = environment.observation_space

    out_dir = args.out / game.game_id
    if args.dump:
        out_dir.mkdir(parents=True, exist_ok=True)

    from flygi.encoding.features import latest_grid

    def emit(tag: str, frame: Any) -> None:
        info = frame_summary(frame)
        print(f"[{tag}] {info}")
        if args.dump:
            path = out_dir / f"{tag}.txt"
            path.write_text(render_grid(latest_grid(frame)) + "\n" + json.dumps(info))

    emit("000-initial", frame)
    transitions: list[dict[str, Any]] = []
    score_before = frame_summary(frame)["score"]

    for index, step in enumerate(steps, start=1):
        identifier = int(step["action"])
        action = runtime.GameAction.from_id(identifier)
        payload: dict[str, int] = {}
        if identifier == 6:
            payload = {"x": int(step["x"]), "y": int(step["y"])}
            action.set_data(payload)
        response = environment.step(action, data=payload, reasoning=None)
        if response is None:
            raise SystemExit(f"step {index}: environment returned None")
        frame = response
        info = frame_summary(frame)
        transitions.append({"step": index, "action": step, **info})
        tag = f"{index:03d}-a{identifier}" + (
            f"-x{step['x']}y{step['y']}" if identifier == 6 else ""
        )
        emit(tag, frame)
        if info["state"] in {"WIN", "GameState.WIN"}:
            break

    score_after = frame_summary(frame)["score"]
    verdict = {
        "game_id": game.game_id,
        "steps_executed": len(transitions),
        "score_before": score_before,
        "score_after": score_after,
        "level_fell": (score_after or 0) > (score_before or 0),
        "final_state": frame_summary(frame)["state"],
    }
    print(json.dumps(verdict, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
