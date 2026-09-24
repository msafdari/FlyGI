#!/usr/bin/env python3
"""Capture (grid, action) streams from cached ARC games for the JEPA probe.

H-JEPA-SPONTANEOUS, registered assumption (a): streams come from a uniform
random-legal policy so the captured statistics describe the world and the
encoder, not any controller's habits. Grids are stored raw (int8, 64x64) so
every downstream design decision -- encoder, horizons, masking -- can change
without re-capturing.

Alignment convention: grids[i] is the observation BEFORE actions[i] is taken,
grids[i+1] the observation after, so a stream of T grids carries T-1
transitions. action_ids, click coordinates, game state, and levels_completed
are stored per transition for change-masking and action-conditioned baselines.
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "jepa" / "streams"


def _load_baseline() -> Any:
    spec = importlib.util.spec_from_file_location(
        "flygi_random_baseline", ROOT / "scripts" / "evaluate_random_baseline.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def capture_game(baseline: Any, runtime: Any, game: Any, steps: int, seed: int) -> dict[str, Any]:
    from flygi.arc.state import ArcTurnState, action_id, symbolic_name
    from flygi.encoding.features import latest_grid

    environment_seed, policy_seed = baseline.derived_run_seeds(seed, game.game_id)
    arcade = baseline._new_offline_arcade(runtime, baseline.DEFAULT_ENVIRONMENTS_DIR.resolve())
    scorecard_id = arcade.open_scorecard(
        tags=["flygi", "jepa-capture"],
        opaque={"experiment_seed": seed, "game_id": game.game_id, "purpose": "jepa-probe"},
    )
    baseline._seed_process_for_environment(environment_seed)
    environment = arcade.make(
        game.game_id,
        seed=environment_seed,
        scorecard_id=scorecard_id,
        save_recording=False,
        include_frame_data=False,
    )
    if environment is None:
        raise RuntimeError(f"environment creation returned None for {game.game_id}")
    policy = baseline.RandomLegalPolicy(runtime.GameAction, seed=policy_seed)

    frame = environment.observation_space
    grids: list[np.ndarray] = [np.asarray(latest_grid(frame), dtype=np.int8)]
    action_ids: list[int] = []
    click_xy: list[tuple[int, int]] = []
    states: list[str] = [symbolic_name(frame.state)]
    levels: list[int] = [int(frame.levels_completed)]
    try:
        for _ in range(steps):
            if policy.is_done(frame):
                break
            action = policy.choose_action(frame)
            payload = baseline._action_payload(action)
            turn = ArcTurnState.from_frame(frame)
            identifier = action_id(action)
            legal = (
                identifier == action_id(runtime.GameAction.RESET)
                if turn.needs_reset
                else identifier in turn.available_action_ids
            )
            if not legal:
                raise RuntimeError(f"policy chose illegal action {identifier} in {game.game_id}")
            response = environment.step(action, data=payload, reasoning=None)
            if response is None:
                raise RuntimeError(f"environment step returned None for {game.game_id}")
            frame = response
            grids.append(np.asarray(latest_grid(frame), dtype=np.int8))
            action_ids.append(identifier)
            click_xy.append((int(payload.get("x", -1)), int(payload.get("y", -1))))
            states.append(symbolic_name(frame.state))
            levels.append(int(frame.levels_completed))
    finally:
        with contextlib.suppress(Exception):
            arcade.close_scorecard(scorecard_id)

    return {
        "grids": np.stack(grids),
        "action_ids": np.asarray(action_ids, dtype=np.int16),
        "click_xy": np.asarray(click_xy, dtype=np.int16).reshape(-1, 2),
        "states": np.asarray(states),
        "levels": np.asarray(levels, dtype=np.int16),
        "environment_seed": environment_seed,
        "policy_seed": policy_seed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=400)
    parser.add_argument("--seed", type=int, default=20260924)
    parser.add_argument("--games", nargs="+", default=["all"])
    args = parser.parse_args(argv)

    from flygi.telemetry import run_or_null

    telemetry = run_or_null()
    baseline = _load_baseline()
    runtime = baseline.load_arc_runtime()
    games = baseline.discover_games(
        runtime, baseline.DEFAULT_ENVIRONMENTS_DIR.resolve(), args.games
    )
    OUT.mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    for game in games:
        path = OUT / f"{game.game_id}.npz"
        if path.exists():
            existing = np.load(path)
            manifest.append(
                {"game": game.game_id, "steps": int(existing["grids"].shape[0]), "file": path.name}
            )
            print(f"{game.game_id}: already captured, skipping", flush=True)
            continue
        stream = capture_game(baseline, runtime, game, args.steps, args.seed)
        np.savez_compressed(
            path,
            grids=stream["grids"],
            action_ids=stream["action_ids"],
            click_xy=stream["click_xy"],
            states=stream["states"],
            levels=stream["levels"],
        )
        manifest.append(
            {
                "game": game.game_id,
                "steps": int(stream["grids"].shape[0]),
                "environment_seed": stream["environment_seed"],
                "policy_seed": stream["policy_seed"],
                "file": path.name,
            }
        )
        telemetry.info("jepa.capture.game", game=game.game_id, steps=int(stream["grids"].shape[0]))
        print(f"{game.game_id}: {stream['grids'].shape[0]} frames", flush=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"captured {len(manifest)} games -> {OUT}")
    return 0


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("jepa_capture", main))
