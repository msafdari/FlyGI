#!/usr/bin/env python3
"""Run FlyGI's adapter against public ARC-AGI-3 environments locally.

Follows the official ARC-AGI-3 Kaggle Starter interface at revision
eeb1535404f321d280a8f9194bbc1d7aca5f05fc. See THIRD_PARTY_NOTICES.md.
"""

from __future__ import annotations

import argparse
import importlib.util
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
VENDOR = ROOT / "vendor" / "ARC-AGI-3-Agents"
ADAPTER = ROOT / "kaggle" / "agent" / "my_agent.py"

sys.path.insert(0, str(SOURCE))
if not VENDOR.exists():
    raise SystemExit(f"Framework not found at {VENDOR}. Run `make setup` first.")
sys.path.insert(0, str(VENDOR))

import arc_agi  # noqa: E402
from arc_agi import OperationMode  # noqa: E402


def load_my_agent_class():
    """Import the adapter exactly as the official harness will."""

    spec = importlib.util.spec_from_file_location("flygi_user_agent", ADAPTER)
    if spec is None or spec.loader is None:
        raise SystemExit(f"Could not load {ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "MyAgent"):
        raise SystemExit(f"{ADAPTER} must define a class named MyAgent")
    return module.MyAgent


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--game",
        default=None,
        help="Short game id or comma-separated ids; omit to run all public games",
    )
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--list", action="store_true", help="list games and exit")
    parser.add_argument("--render", choices=["terminal"], default=None)
    return parser


def main() -> None:
    args = _parser().parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    arcade = arc_agi.Arcade(operation_mode=OperationMode.NORMAL)
    environments = arcade.get_environments()
    if args.list:
        print(f"{len(environments)} environments:")
        for environment in environments:
            print(f"  {environment.game_id}: {getattr(environment, 'title', '?')}")
        return

    available = {environment.game_id.split("-")[0]: environment for environment in environments}
    if args.game:
        requested = [item.strip().split("-")[0] for item in args.game.split(",")]
        missing = sorted(set(requested) - set(available))
        if missing:
            raise SystemExit(f"Unknown game id(s): {missing}. Run --list.")
        game_ids = requested
    else:
        game_ids = list(available)

    agent_class = load_my_agent_class()
    agent_class.MAX_ACTIONS = min(agent_class.MAX_ACTIONS, args.max_steps)
    failures: list[str] = []
    for position, game_id in enumerate(game_ids, start=1):
        print(f"=== [{position}/{len(game_ids)}] {game_id} ===")
        environment = arcade.make(game_id, render_mode=args.render)
        if environment is None:
            failures.append(f"{game_id}: environment creation returned None")
            continue
        agent = agent_class(
            card_id="flygi-local",
            game_id=game_id,
            agent_name=f"FlyGI.random.{game_id}",
            ROOT_URL="http://localhost",
            record=False,
            arc_env=environment,
            tags=["flygi", "milestone-0", "random-legal"],
        )
        try:
            agent.main()
        except Exception as exc:  # Surface all failures after a multi-game run.
            failures.append(f"{game_id}: {type(exc).__name__}: {exc}")

    if failures:
        raise SystemExit("ARC local run failed:\n  " + "\n  ".join(failures))


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("play_local", main))
