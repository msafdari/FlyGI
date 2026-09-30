#!/usr/bin/env python3
"""Run a reproducible random-policy baseline on cached ARC-AGI-3 games.

The evaluator is deliberately separate from the upstream Agent loop.  In
particular, it enforces its own action ceiling because the pinned framework's
``Agent.main`` loop uses an inclusive ``<= MAX_ACTIONS`` condition.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import logging
import math
import os
import platform
import random
import resource
import subprocess
import sys
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from statistics import fmean, median
from time import perf_counter_ns
from typing import Any

import numpy as np

from flygi.arc import RandomLegalPolicy
from flygi.arc.state import ArcTurnState, action_id, symbolic_name
from flygi.seed import derive_seed

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENVIRONMENTS_DIR = ROOT / "environment_files"
DEFAULT_RESULTS_DIR = ROOT / "results" / "random_baseline"
SCHEMA_VERSION = 1
UINT32_MODULUS = 1 << 32


@dataclass(frozen=True, slots=True)
class ArcRuntime:
    """Late-bound optional ARC dependencies."""

    Arcade: type
    OperationMode: Any
    GameAction: Any


@dataclass(frozen=True, slots=True)
class FrozenGame:
    """One exact cached game package selected before evaluation begins."""

    game_id: str
    base_game_id: str
    title: str
    metadata_path: Path
    metadata_sha256: str
    source_sha256: str
    baseline_actions: tuple[int, ...]

    def manifest(self) -> dict[str, Any]:
        """Return the portable provenance fields written to a result."""

        try:
            metadata_path = self.metadata_path.relative_to(ROOT)
        except ValueError:
            metadata_path = self.metadata_path
        return {
            "game_id": self.game_id,
            "base_game_id": self.base_game_id,
            "title": self.title,
            "metadata_path": metadata_path.as_posix(),
            "metadata_sha256": self.metadata_sha256,
            "source_sha256": self.source_sha256,
            "baseline_actions": list(self.baseline_actions),
        }


def load_arc_runtime() -> ArcRuntime:
    """Import the optional local ARC runtime with an actionable error."""

    try:
        from arc_agi import Arcade, OperationMode
        from arcengine import GameAction
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on install extras
        raise RuntimeError(
            "ARC dependencies are missing; run `uv sync --all-extras` before evaluation"
        ) from exc
    logging.getLogger("arc_agi.scorecard").setLevel(logging.WARNING)
    return ArcRuntime(Arcade=Arcade, OperationMode=OperationMode, GameAction=GameAction)


def sha256_file(path: Path) -> str:
    """Hash a file without reading it all into memory."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _source_tree_sha256(directory: Path) -> str:
    """Hash the stable Python sources in a cached game package."""

    digest = hashlib.sha256()
    sources = sorted(path for path in directory.rglob("*.py") if path.is_file())
    for path in sources:
        relative = path.relative_to(directory).as_posix().encode("utf-8")
        content_hash = bytes.fromhex(sha256_file(path))
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(content_hash)
    return digest.hexdigest()


def _new_offline_arcade(
    runtime: ArcRuntime,
    environments_dir: Path,
) -> Any:
    """Construct an arcade and verify that no online fallback is possible."""

    # The upstream constructor lets OPERATION_MODE=competition override even an
    # explicit argument.  Pinning the subprocess environment closes that hole.
    os.environ["OPERATION_MODE"] = "offline"
    logger = logging.getLogger("flygi.random_baseline.arc")
    logger.setLevel(logging.WARNING)
    arcade = runtime.Arcade(
        operation_mode=runtime.OperationMode.OFFLINE,
        environments_dir=str(environments_dir),
        logger=logger,
    )
    if arcade.operation_mode != runtime.OperationMode.OFFLINE:
        raise RuntimeError(
            f"strict-offline invariant failed: runtime selected {arcade.operation_mode!r}"
        )
    return arcade


def discover_games(
    runtime: ArcRuntime,
    environments_dir: Path,
    requested: Sequence[str],
) -> list[FrozenGame]:
    """Resolve requested cached games to sorted, exact versioned packages."""

    arcade = _new_offline_arcade(runtime, environments_dir)
    by_full: dict[str, Any] = {}
    by_base: dict[str, list[Any]] = {}
    for info in arcade.get_environments():
        game_id = str(info.game_id)
        if "-" not in game_id:
            raise RuntimeError(
                f"cached game {game_id!r} has no version suffix and cannot be frozen"
            )
        if game_id in by_full:
            raise RuntimeError(f"duplicate cached game version: {game_id}")
        by_full[game_id] = info
        by_base.setdefault(game_id.split("-", 1)[0], []).append(info)

    tokens = _normalize_game_tokens(requested)
    if tokens == ["all"]:
        selected_infos = list(by_full.values())
    else:
        selected_infos = []
        for token in tokens:
            if token in by_full:
                selected_infos.append(by_full[token])
                continue
            matches = by_base.get(token, [])
            if not matches:
                raise ValueError(f"requested game {token!r} is not cached")
            if len(matches) != 1:
                versions = sorted(str(info.game_id) for info in matches)
                raise ValueError(
                    f"requested base game {token!r} is ambiguous; choose one of {versions}"
                )
            selected_infos.append(matches[0])

    unique_infos = {str(info.game_id): info for info in selected_infos}
    games: list[FrozenGame] = []
    for game_id in sorted(unique_infos):
        info = unique_infos[game_id]
        if info.local_dir is None:
            raise RuntimeError(f"cached game {game_id} has no local directory")
        local_dir = Path(info.local_dir).resolve()
        metadata_path = local_dir / "metadata.json"
        if not metadata_path.is_file():
            raise FileNotFoundError(f"cached game metadata not found: {metadata_path}")
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        if metadata.get("game_id") != game_id:
            raise RuntimeError(
                f"metadata game_id mismatch for {game_id}: {metadata.get('game_id')!r}"
            )
        games.append(
            FrozenGame(
                game_id=game_id,
                base_game_id=game_id.split("-", 1)[0],
                title=str(getattr(info, "title", "")),
                metadata_path=metadata_path,
                metadata_sha256=sha256_file(metadata_path),
                source_sha256=_source_tree_sha256(local_dir),
                baseline_actions=tuple(int(value) for value in (info.baseline_actions or [])),
            )
        )
    if not games:
        raise RuntimeError(f"no cached games found under {environments_dir}")
    return games


def _normalize_game_tokens(requested: Sequence[str]) -> list[str]:
    tokens = [part.strip() for item in requested for part in item.split(",") if part.strip()]
    if not tokens:
        raise ValueError("at least one game or 'all' must be requested")
    lowered = [token.lower() for token in tokens]
    if "all" in lowered and len(tokens) != 1:
        raise ValueError("'all' cannot be combined with named games")
    if len(set(tokens)) != len(tokens):
        raise ValueError("duplicate games are not allowed")
    return lowered if lowered == ["all"] else tokens


def derived_run_seeds(experiment_seed: int, game_id: str) -> tuple[int, int]:
    """Return stable, domain-separated environment and policy seeds."""

    environment_seed = derive_seed(experiment_seed, f"arc-environment:{game_id}")
    policy_seed = derive_seed(experiment_seed, f"random-policy:{game_id}")
    return environment_seed, policy_seed


def _seed_process_for_environment(environment_seed: int) -> None:
    """Seed Python and NumPy's legacy global RNG before game construction."""

    normalized = environment_seed & ((1 << 64) - 1)
    os.environ["PYTHONHASHSEED"] = str(normalized)
    random.seed(normalized)
    np.random.seed(normalized % UINT32_MODULUS)


def _frame_fingerprint(frame: Any) -> str:
    digest = hashlib.sha256()
    layers = getattr(frame, "frame", ()) or ()
    digest.update(len(layers).to_bytes(8, "big"))
    for layer in layers:
        array = np.ascontiguousarray(np.asarray(layer))
        shape = json.dumps(list(array.shape), separators=(",", ":")).encode("ascii")
        dtype = array.dtype.str.encode("ascii")
        digest.update(len(shape).to_bytes(8, "big"))
        digest.update(shape)
        digest.update(len(dtype).to_bytes(8, "big"))
        digest.update(dtype)
        digest.update(array.tobytes(order="C"))
    return digest.hexdigest()


def _action_payload(action: Any) -> dict[str, Any]:
    payload = getattr(action, "action_data", None)
    if payload is None:
        return {}
    dump = getattr(payload, "model_dump", None)
    if callable(dump):
        return dict(dump())
    if isinstance(payload, dict):
        return dict(payload)
    return dict(vars(payload))


def _action_name(action: Any) -> str:
    name = getattr(action, "name", None)
    return str(name) if name is not None else f"ACTION{action_id(action)}"


def _timing_summary(values: Sequence[int]) -> dict[str, int | float | None]:
    if not values:
        return {
            "count": 0,
            "total_ns": 0,
            "mean_ns": None,
            "median_ns": None,
            "p95_ns": None,
            "min_ns": None,
            "max_ns": None,
        }
    return {
        "count": len(values),
        "total_ns": sum(values),
        "mean_ns": fmean(values),
        "median_ns": median(values),
        "p95_ns": float(np.percentile(values, 95)),
        "min_ns": min(values),
        "max_ns": max(values),
    }


def _entropy_bits(counts: Counter[str]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return -sum((count / total) * math.log2(count / total) for count in counts.values() if count)


def _replay_trace_sha256(trace: Sequence[dict[str, Any]]) -> str:
    """Hash deterministic trace fields while excluding machine timing noise."""

    replay_trace = [
        {key: value for key, value in entry.items() if not key.endswith("_ns")} for entry in trace
    ]
    payload = json.dumps(
        replay_trace,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _reasoning_payload(action: Any) -> dict[str, Any] | None:
    reasoning = getattr(action, "reasoning", None)
    if reasoning is None:
        return None
    return reasoning if isinstance(reasoning, dict) else {"text": str(reasoning)}


def _official_run(scorecard: Any, game_id: str) -> dict[str, Any]:
    environment = scorecard.find_environment(game_id)
    if environment is None:
        raise RuntimeError(f"official scorecard has no entry for {game_id}")
    if not environment.runs:
        raise RuntimeError(f"official scorecard has no runs for {game_id}")
    runs: list[dict[str, Any]] = []
    for run_index, run in enumerate(environment.runs):
        dump = getattr(run, "model_dump", None)
        raw = dump(mode="json", exclude_none=False) if callable(dump) else vars(run)
        runs.append(
            {
                "run_index": run_index,
                "score": float(raw["score"]),
                "levels_completed": int(raw["levels_completed"]),
                "actions": int(raw["actions"]),
                "resets": None if raw.get("resets") is None else int(raw["resets"]),
                "state": None if raw.get("state") is None else symbolic_name(raw["state"]),
                "completed": raw.get("completed"),
                "level_scores": raw.get("level_scores"),
                "level_actions": raw.get("level_actions"),
                "level_baseline_actions": raw.get("level_baseline_actions"),
                "message": raw.get("message"),
            }
        )
    return {
        "score": float(environment.score),
        "levels_completed": int(environment.levels_completed),
        "actions": int(environment.actions),
        "resets": int(environment.resets),
        "completed": bool(environment.completed),
        "run_count": len(runs),
        "runs": runs,
    }


def _failure(phase: str, exc: BaseException) -> dict[str, str]:
    return {
        "phase": phase,
        "type": type(exc).__name__,
        "message": str(exc),
    }


def _peak_rss_bytes() -> int:
    """Return process peak RSS in bytes on macOS and Linux."""

    raw = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    return raw if sys.platform == "darwin" else raw * 1024


def evaluate_one(
    runtime: ArcRuntime,
    game: FrozenGame,
    experiment_seed: int,
    action_budget: int,
    environments_dir: Path,
    *,
    arcade_factory: Callable[[], Any] | None = None,
    policy_factory: Callable[[int], Any] | None = None,
    extra_row_fields: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate one fresh seed/game pair and always return a result row.

    ``policy_factory`` receives the derived policy seed and returns any object
    exposing ``is_done(frame)`` and ``choose_action(frame)``. The default is the
    uniform random-legal chance control, so the Gate 0 result stays reproducible.
    """

    if action_budget <= 0:
        raise ValueError("action_budget must be positive")
    environment_seed, policy_seed = derived_run_seeds(experiment_seed, game.game_id)
    row: dict[str, Any] = {
        "seed": experiment_seed,
        "game_id": game.game_id,
        "environment_seed": environment_seed,
        "policy_seed": policy_seed,
        "action_budget": action_budget,
        "status": "failed",
        "termination_reason": None,
        "failure": None,
        "actions_attempted": 0,
        "actions_completed": 0,
        "illegal_action_count": 0,
        "game_over_frames": 0,
        "final_state": None,
        "final_levels_completed": None,
        "action_counts": {},
        "action_entropy_bits": 0.0,
        "observations": {
            "count": 0,
            "unique": 0,
            "repeats": 0,
            "repeat_rate": 0.0,
            "consecutive_repeats": 0,
        },
        "action6_coordinates": {"count": 0, "valid": 0, "invalid": 0},
        "timing": {
            "policy": _timing_summary([]),
            "environment_step": _timing_summary([]),
            "evaluation_wall_ns": 0,
        },
        "official": None,
        "trace": [],
        "replay_trace_sha256": None,
    }
    if extra_row_fields:
        row.update(dict(extra_row_fields))
    action_counts: Counter[str] = Counter()
    observation_hashes: list[str] = []
    policy_times: list[int] = []
    environment_times: list[int] = []
    coordinate_count = coordinate_valid = coordinate_invalid = 0
    illegal_action_count = 0
    trace: list[dict[str, Any]] = []
    scorecard_id: str | None = None
    arcade: Any | None = None
    latest_frame: Any | None = None
    wall_start = perf_counter_ns()

    try:
        arcade = (
            arcade_factory()
            if arcade_factory is not None
            else _new_offline_arcade(runtime, environments_dir)
        )
        if arcade.operation_mode != runtime.OperationMode.OFFLINE:
            raise RuntimeError("arcade_factory returned a non-offline runtime")
        scorecard_id = arcade.open_scorecard(
            tags=["agent", "flygi", "random-baseline"],
            opaque={
                "experiment_seed": experiment_seed,
                "environment_seed": environment_seed,
                "policy_seed": policy_seed,
                "action_budget": action_budget,
                "game_id": game.game_id,
            },
        )
        _seed_process_for_environment(environment_seed)
        environment = arcade.make(
            game.game_id,
            seed=environment_seed,
            scorecard_id=scorecard_id,
            save_recording=False,
            include_frame_data=False,
        )
        if environment is None:
            raise RuntimeError("environment creation returned None")
        latest_frame = environment.observation_space
        if latest_frame is None:
            raise RuntimeError("environment has no initial observation")
        observation_hashes.append(_frame_fingerprint(latest_frame))
        policy = (
            RandomLegalPolicy(runtime.GameAction, seed=policy_seed)
            if policy_factory is None
            else policy_factory(policy_seed)
        )
        reset_id = action_id(runtime.GameAction.RESET)

        # This range is the budget authority; unlike the upstream loop, it can
        # never execute budget + 1 actions.
        for step_index in range(action_budget):
            # Registered gate-(a) amendment: policies that budget their own
            # exploration receive the remaining row budget each turn.
            budget_setter = getattr(policy, "set_remaining_action_budget", None)
            if callable(budget_setter):
                budget_setter(action_budget - step_index)
            if policy.is_done(latest_frame):
                row["termination_reason"] = "win"
                break

            policy_start = perf_counter_ns()
            try:
                action = policy.choose_action(latest_frame)
            finally:
                policy_elapsed = perf_counter_ns() - policy_start
                policy_times.append(policy_elapsed)

            turn = ArcTurnState.from_frame(latest_frame)
            action_identifier = action_id(action)
            name = _action_name(action)
            payload = _action_payload(action)
            action_counts[name] += 1
            row["actions_attempted"] += 1

            available_action_ids = list(turn.available_action_ids)
            # GATE-0 LEGALITY AMENDMENT, declared 2026-09-30 (H-ONLINE-SEARCH
            # build): a voluntary RESET on an ACTIVE frame is protocol-legal.
            # MEASURED: the engine accepts action 0 on active frames while
            # never listing it in available_actions, and the search layer's
            # program replay depends on it. On a needs-reset frame, RESET
            # remains the only legal action, exactly as before.
            protocol_legal = (
                action_identifier == reset_id
                if turn.needs_reset
                else (
                    action_identifier == reset_id
                    or action_identifier in turn.available_action_ids
                )
            )
            if not protocol_legal:
                illegal_action_count += 1
            before_hash = observation_hashes[-1]
            trace_entry: dict[str, Any] = {
                "step": step_index,
                "action_id": action_identifier,
                "action": name,
                "payload": payload,
                "available_action_ids": available_action_ids,
                "protocol_legal": protocol_legal,
                "state_before": symbolic_name(latest_frame.state),
                "levels_completed_before": int(latest_frame.levels_completed),
                "observation_before_sha256": before_hash,
                "policy_ns": policy_elapsed,
                "environment_step_ns": None,
                "state_after": None,
                "levels_completed_after": None,
                "observation_after_sha256": None,
            }
            trace.append(trace_entry)
            if not protocol_legal:
                raise RuntimeError(
                    f"policy selected illegal action {action_identifier} in "
                    f"state {turn.game_state} with mask {available_action_ids}"
                )

            if action_identifier == 6:
                coordinate_count += 1
                x, y = payload.get("x"), payload.get("y")
                valid = (
                    isinstance(x, int)
                    and not isinstance(x, bool)
                    and isinstance(y, int)
                    and not isinstance(y, bool)
                    and 0 <= x <= 63
                    and 0 <= y <= 63
                )
                if valid:
                    coordinate_valid += 1
                else:
                    coordinate_invalid += 1
                    raise RuntimeError(f"ACTION6 emitted invalid coordinates: {payload!r}")

            environment_start = perf_counter_ns()
            try:
                response = environment.step(
                    action,
                    data=payload,
                    reasoning=_reasoning_payload(action),
                )
            finally:
                environment_elapsed = perf_counter_ns() - environment_start
                environment_times.append(environment_elapsed)
                trace_entry["environment_step_ns"] = environment_elapsed
            if response is None:
                raise RuntimeError("environment step returned None")
            row["actions_completed"] += 1
            latest_frame = response
            after_hash = _frame_fingerprint(latest_frame)
            observation_hashes.append(after_hash)
            trace_entry["state_after"] = symbolic_name(latest_frame.state)
            trace_entry["levels_completed_after"] = int(latest_frame.levels_completed)
            trace_entry["observation_after_sha256"] = after_hash
            if trace_entry["state_after"] == "GAME_OVER":
                row["game_over_frames"] += 1
        else:
            row["termination_reason"] = "budget_exhausted"

        row["status"] = "success"
    except Exception as exc:  # Preserve a failed seed/game row and continue the matrix.
        row["termination_reason"] = "failure"
        row["failure"] = _failure("evaluation", exc)
    finally:
        if arcade is not None and scorecard_id is not None:
            try:
                scorecard = arcade.close_scorecard(scorecard_id)
                if scorecard is None:
                    raise RuntimeError("closing official scorecard returned None")
                row["official"] = _official_run(scorecard, game.game_id)
                if (
                    row["status"] == "success"
                    and row["official"]["actions"] != row["actions_completed"]
                ):
                    raise RuntimeError(
                        "scorecard action count does not match evaluator count: "
                        f"{row['official']['actions']} != {row['actions_completed']}"
                    )
            except Exception as exc:
                if row["failure"] is None:
                    row["failure"] = _failure("scorecard_close", exc)
                    row["termination_reason"] = "failure"
                else:
                    row["failure"]["scorecard_close"] = _failure("scorecard_close", exc)
                row["status"] = "failed"

        if latest_frame is not None:
            row["final_state"] = symbolic_name(latest_frame.state)
            row["final_levels_completed"] = int(latest_frame.levels_completed)
        row["timing"] = {
            "policy": _timing_summary(policy_times),
            "environment_step": _timing_summary(environment_times),
            "evaluation_wall_ns": perf_counter_ns() - wall_start,
        }
        row["action_counts"] = dict(sorted(action_counts.items()))
        row["action_entropy_bits"] = _entropy_bits(action_counts)
        row["illegal_action_count"] = illegal_action_count
        row["trace"] = trace
        row["replay_trace_sha256"] = _replay_trace_sha256(trace)
        unique_observations = len(set(observation_hashes))
        repeats = len(observation_hashes) - unique_observations
        consecutive_repeats = sum(left == right for left, right in pairwise(observation_hashes))
        row["observations"] = {
            "count": len(observation_hashes),
            "unique": unique_observations,
            "repeats": repeats,
            "repeat_rate": repeats / len(observation_hashes) if observation_hashes else 0.0,
            "consecutive_repeats": consecutive_repeats,
        }
        row["action6_coordinates"] = {
            "count": coordinate_count,
            "valid": coordinate_valid,
            "invalid": coordinate_invalid,
        }
    return row


def _group_summary(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    official = [row["official"] for row in rows if row.get("official") is not None]
    scores = [item["score"] for item in official]
    levels = [item["levels_completed"] for item in official]
    policy_samples = [entry["policy_ns"] for row in rows for entry in row["trace"]]
    environment_samples = [
        entry["environment_step_ns"]
        for row in rows
        for entry in row["trace"]
        if entry["environment_step_ns"] is not None
    ]
    action_counts: Counter[str] = Counter()
    for row in rows:
        action_counts.update(row["action_counts"])
    return {
        "rows": len(rows),
        "successful_rows": sum(row["status"] == "success" for row in rows),
        "failed_rows": sum(row["status"] == "failed" for row in rows),
        "official_rows": len(official),
        "mean_score": fmean(scores) if scores else None,
        "min_score": min(scores) if scores else None,
        "max_score": max(scores) if scores else None,
        "total_levels_completed": sum(levels),
        "mean_levels_completed": fmean(levels) if levels else None,
        "rows_with_progress": sum(item["levels_completed"] > 0 for item in official),
        "completed_games": sum(bool(item["completed"]) for item in official),
        "official_actions": sum(item["actions"] for item in official),
        "official_resets": sum(item["resets"] for item in official),
        "actions_attempted": sum(row["actions_attempted"] for row in rows),
        "actions_completed": sum(row["actions_completed"] for row in rows),
        "illegal_action_count": sum(row["illegal_action_count"] for row in rows),
        "invalid_action6_coordinates": sum(row["action6_coordinates"]["invalid"] for row in rows),
        "game_over_frames": sum(row["game_over_frames"] for row in rows),
        "budget_violations": sum(
            row["actions_completed"] > row["action_budget"]
            or (
                row["termination_reason"] == "budget_exhausted"
                and row["actions_completed"] != row["action_budget"]
            )
            for row in rows
        ),
        "action_counts": dict(sorted(action_counts.items())),
        "action_entropy_bits": _entropy_bits(action_counts),
        "unique_observations": sum(row["observations"]["unique"] for row in rows),
        "observation_repeats": sum(row["observations"]["repeats"] for row in rows),
        "policy_time_ns": sum(row["timing"]["policy"]["total_ns"] for row in rows),
        "environment_step_time_ns": sum(
            row["timing"]["environment_step"]["total_ns"] for row in rows
        ),
        "policy_timing": _timing_summary(policy_samples),
        "environment_step_timing": _timing_summary(environment_samples),
        "evaluation_wall_ns": sum(row["timing"]["evaluation_wall_ns"] for row in rows),
    }


def aggregate_rows(rows: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Build overall, per-game, and per-seed summaries."""

    by_game: dict[str, list[dict[str, Any]]] = {}
    by_seed: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        by_game.setdefault(row["game_id"], []).append(row)
        by_seed.setdefault(row["seed"], []).append(row)
    return {
        "overall": _group_summary(rows),
        "by_game": {game_id: _group_summary(by_game[game_id]) for game_id in sorted(by_game)},
        "by_seed": {str(seed): _group_summary(by_seed[seed]) for seed in sorted(by_seed)},
    }


def _gate_summary(
    rows: Sequence[dict[str, Any]],
    *,
    expected_rows: int,
    replay_check: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate engineering invariants; score is intentionally not a gate."""

    summary = _group_summary(rows)
    issues: list[str] = []
    if len(rows) != expected_rows:
        issues.append(f"expected {expected_rows} rows, observed {len(rows)}")
    if summary["failed_rows"]:
        issues.append(f"{summary['failed_rows']} rows failed")
    if summary["illegal_action_count"]:
        issues.append(f"{summary['illegal_action_count']} illegal actions")
    if summary["invalid_action6_coordinates"]:
        issues.append(f"{summary['invalid_action6_coordinates']} invalid ACTION6 coordinates")
    if summary["budget_violations"]:
        issues.append(f"{summary['budget_violations']} action-budget violations")
    if not replay_check.get("matched", False):
        issues.append("deterministic replay check did not match")
    return {
        "passed": not issues,
        "issues": issues,
        "positive_score_required": False,
    }


def _deterministic_replay_check(
    runtime: ArcRuntime,
    games: Sequence[FrozenGame],
    seeds: Sequence[int],
    action_budget: int,
    environments_dir: Path,
    rows: Sequence[dict[str, Any]],
    *,
    policy_factory: Callable[[int], Any] | None = None,
) -> dict[str, Any]:
    """Repeat one seeded game and compare its deterministic trace."""

    target_game = next(
        (game for game in games if game.base_game_id.lower() == "lf52"),
        games[0],
    )
    target_seed = seeds[0]
    reference = next(
        row for row in rows if row["seed"] == target_seed and row["game_id"] == target_game.game_id
    )
    replay = evaluate_one(
        runtime,
        target_game,
        target_seed,
        action_budget,
        environments_dir,
        policy_factory=policy_factory,
    )
    matched = (
        reference["status"] == "success"
        and replay["status"] == "success"
        and reference["replay_trace_sha256"] == replay["replay_trace_sha256"]
        and reference["official"] == replay["official"]
    )
    return {
        "game_id": target_game.game_id,
        "seed": target_seed,
        "matched": matched,
        "reference_status": reference["status"],
        "replay_status": replay["status"],
        "reference_trace_sha256": reference["replay_trace_sha256"],
        "replay_trace_sha256": replay["replay_trace_sha256"],
        "reference_official": reference["official"],
        "replay_official": replay["official"],
        "replay_failure": replay["failure"],
    }


def _git_provenance() -> dict[str, Any]:
    def run(*arguments: str) -> str:
        completed = subprocess.run(
            ["git", *arguments],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        return completed.stdout.strip()

    try:
        commit = run("rev-parse", "HEAD")
        status_lines = run("status", "--porcelain=v1", "--untracked-files=all").splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        return {"commit": None, "dirty": None, "status": [], "error": str(exc)}
    return {"commit": commit, "dirty": bool(status_lines), "status": status_lines}


def _dependency_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for distribution in ("flygi", "arc-agi", "arcengine", "numpy", "pydantic"):
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = None
    return versions


def build_result(
    *,
    games: Sequence[FrozenGame],
    seeds: Sequence[int],
    action_budget: int,
    rows: Sequence[dict[str, Any]],
    replay_check: dict[str, Any],
    schema: str = "flygi.random-baseline",
    policy_label: str = "uniform-random-legal",
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the immutable result document."""

    document = {
        "schema": schema,
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "parameters": {
            "policy": policy_label,
            "strict_offline": True,
            "seeds": list(seeds),
            "action_budget": action_budget,
            "games": [game.game_id for game in games],
            "coordinate_bounds": [0, 63],
            "stop_on_win": True,
        },
        "provenance": {
            "git": _git_provenance(),
            "uv_lock_sha256": sha256_file(ROOT / "uv.lock"),
            "evaluator_sha256": sha256_file(Path(__file__).resolve()),
            "python": sys.version,
            "platform": platform.platform(),
            "dependencies": _dependency_versions(),
            "peak_rss_bytes": _peak_rss_bytes(),
            "games": [game.manifest() for game in games],
        },
        "rows": list(rows),
        "summaries": aggregate_rows(rows),
        "checks": {
            "deterministic_replay": replay_check,
            "gate": _gate_summary(
                rows,
                expected_rows=len(seeds) * len(games),
                replay_check=replay_check,
            ),
        },
    }
    if extra:
        document.update(dict(extra))
    return document


def write_json_exclusive(path: Path, result: dict[str, Any]) -> None:
    """Write one result exactly once; never replace an existing artifact."""

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    with path.open("x", encoding="utf-8") as handle:
        handle.write(payload)


def _default_output(seeds: Sequence[int], games: Sequence[FrozenGame], budget: int) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    identity = json.dumps(
        {"seeds": list(seeds), "games": [game.game_id for game in games], "budget": budget},
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    suffix = hashlib.sha256(identity).hexdigest()[:10]
    return DEFAULT_RESULTS_DIR / f"{timestamp}-{suffix}.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        required=True,
        help="explicit experiment seeds (for example: --seeds 0 1 2)",
    )
    parser.add_argument(
        "--games",
        nargs="+",
        default=["all"],
        help="'all', base ids, exact versioned ids, or comma-separated ids",
    )
    parser.add_argument("--action-budget", type=int, default=80)
    parser.add_argument("--environments-dir", type=Path, default=DEFAULT_ENVIRONMENTS_DIR)
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.action_budget <= 0:
        raise SystemExit("--action-budget must be positive")
    if len(set(args.seeds)) != len(args.seeds):
        raise SystemExit("--seeds must not contain duplicates")

    runtime = load_arc_runtime()
    try:
        games = discover_games(runtime, args.environments_dir.resolve(), args.games)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc
    output = (
        args.output.resolve()
        if args.output is not None
        else _default_output(args.seeds, games, args.action_budget)
    )
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing result: {output}")

    rows: list[dict[str, Any]] = []
    total = len(args.seeds) * len(games)
    position = 0
    for seed in args.seeds:
        for game in games:
            position += 1
            print(f"[{position}/{total}] seed={seed} game={game.game_id}", flush=True)
            row = evaluate_one(
                runtime,
                game,
                seed,
                args.action_budget,
                args.environments_dir.resolve(),
            )
            rows.append(row)
            print(
                f"  {row['status']}: actions={row['actions_completed']} "
                f"levels={None if row['official'] is None else row['official']['levels_completed']} "
                f"score={None if row['official'] is None else row['official']['score']}",
                flush=True,
            )

    replay_game = next(
        (game for game in games if game.base_game_id.lower() == "lf52"),
        games[0],
    )
    print(
        f"[replay] seed={args.seeds[0]} game={replay_game.game_id}",
        flush=True,
    )
    replay_check = _deterministic_replay_check(
        runtime,
        games,
        args.seeds,
        args.action_budget,
        args.environments_dir.resolve(),
        rows,
    )

    result = build_result(
        games=games,
        seeds=args.seeds,
        action_budget=args.action_budget,
        rows=rows,
        replay_check=replay_check,
    )
    write_json_exclusive(output, result)
    summary = result["summaries"]["overall"]
    print(
        f"Wrote {output} ({summary['successful_rows']}/{summary['rows']} successful rows, "
        f"mean score={summary['mean_score']})"
    )
    return 0 if result["checks"]["gate"]["passed"] else 1


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("evaluate_random_baseline", main))
