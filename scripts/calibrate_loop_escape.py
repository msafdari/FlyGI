#!/usr/bin/env python3
"""Select one preregistered loop-escape strength using behavior, never score.

The signed connectome, focused action/coordinate temperatures, games, seeds,
budget, candidate strengths, eligibility guards, and lexicographic selection
order are fixed before execution.  Official ARC score and level progress are
removed before rows enter the immutable output.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

DEFAULT_CONFIG = ROOT / "configs/literal_rate_signed.yaml"
DEFAULT_RESULTS_DIR = ROOT / "results" / "loop_escape_calibration"
DEFAULT_GAMES = ("ft09", "lp85", "ls20", "sp80")
DEFAULT_SEEDS = (0, 1)
DEFAULT_ACTION_BUDGET = 40
ACTION_TEMPERATURE = 0.15
COORDINATE_TEMPERATURE = 0.20
SCHEMA = "flygi.loop-escape-calibration"
SCHEMA_VERSION = 1


def _load_script_module(filename: str, module_name: str) -> ModuleType:
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SAMPLER = _load_script_module("calibrate_sampler.py", "_flygi_loop_sampler_helpers")
BASELINE = SAMPLER.BASELINE


@dataclass(frozen=True, slots=True)
class LoopEscapeCandidate:
    """One preregistered strength pair at the frozen focused temperatures."""

    name: str
    exploration_bonus: float
    unchanged_failure_penalty: float
    action_temperature: float = ACTION_TEMPERATURE
    coordinate_temperature: float = COORDINATE_TEMPERATURE

    def describe(self) -> dict[str, str | float | bool]:
        return {
            "name": self.name,
            "loop_escape_enabled": True,
            "exploration_bonus": self.exploration_bonus,
            "unchanged_failure_penalty": self.unchanged_failure_penalty,
            "action_temperature": self.action_temperature,
            "coordinate_temperature": self.coordinate_temperature,
        }


CANDIDATES = (
    LoopEscapeCandidate("mild", exploration_bonus=0.25, unchanged_failure_penalty=0.50),
    LoopEscapeCandidate("balanced", exploration_bonus=0.50, unchanged_failure_penalty=1.00),
    LoopEscapeCandidate("strong", exploration_bonus=1.00, unchanged_failure_penalty=2.00),
)
CANDIDATE_BY_NAME = {candidate.name: candidate for candidate in CANDIDATES}
SELECTION_ORDER = (
    ("mean_unique_observations", "higher"),
    ("mean_consecutive_repeats", "lower"),
    ("action_entropy_fraction_of_legal_max", "higher"),
    ("median_policy_ns", "lower"),
)


class PolicyFactory:
    """Build fresh policies while reusing the immutable graph and projection."""

    def __init__(
        self,
        builder: Callable[..., Any],
        config: Any,
        actions: Any,
        *,
        runtime_dir: Path | None,
        bundle: Any,
        projection: Any,
        internal_steps: int | None,
        candidate: LoopEscapeCandidate,
    ) -> None:
        self._builder = builder
        self._config = config
        self._actions = actions
        self._runtime_dir = runtime_dir
        self._bundle = bundle
        self._projection = projection
        self._internal_steps = internal_steps
        self._candidate = candidate
        self.current: Any | None = None
        self.interface: dict[str, Any] | None = None

    def __call__(self, decision_seed: int) -> Any:
        assembled = self._builder(
            self._config,
            self._actions,
            runtime_dir=self._runtime_dir,
            bundle=self._bundle,
            projection=self._projection,
            internal_steps=self._internal_steps,
            decision_seed=decision_seed,
            action_temperature=self._candidate.action_temperature,
            coordinate_temperature=self._candidate.coordinate_temperature,
            loop_escape_enabled=True,
            loop_escape_exploration_bonus=self._candidate.exploration_bonus,
            loop_escape_unchanged_failure_penalty=(self._candidate.unchanged_failure_penalty),
        )
        self.current = assembled
        if self.interface is None:
            self.interface = assembled.describe()
        return assembled.policy


def _attach_loop_escape_trace(records: Sequence[Any], trace: list[dict[str, Any]]) -> None:
    if len(records) != len(trace):
        raise RuntimeError(
            f"policy emitted {len(records)} records for {len(trace)} completed decisions"
        )
    for record, entry in zip(records, trace, strict=True):
        state_key = getattr(record, "loop_escape_state_key", None)
        if state_key is None:
            raise RuntimeError("enabled loop-escape policy omitted turn provenance")
        entry["loop_escape"] = {
            "state_key": state_key,
            "standardized_bias": list(record.loop_escape_standardized_bias),
            "selected_bias": record.loop_escape_selected_bias,
            "attempts_before": record.loop_escape_attempts_before,
            "unchanged_failures_before": record.loop_escape_unchanged_failures_before,
            "attempt_counts": list(record.loop_escape_attempt_counts),
            "unchanged_failure_counts": list(record.loop_escape_unchanged_failure_counts),
            "prior_choice_failed": record.loop_escape_prior_choice_failed,
            "bias_changed_argmax": record.loop_escape_bias_changed_argmax,
        }


def _run_candidate(
    runtime: Any,
    games: Sequence[Any],
    seeds: Sequence[int],
    action_budget: int,
    environments_dir: Path,
    factory: PolicyFactory,
    candidate: LoopEscapeCandidate,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total = len(seeds) * len(games)
    position = 0
    for seed in seeds:
        for game in games:
            position += 1
            print(
                f"[{candidate.name} {position}/{total}] seed={seed} game={game.game_id}",
                flush=True,
            )
            factory.current = None
            row = BASELINE.evaluate_one(
                runtime,
                game,
                seed,
                action_budget,
                environments_dir,
                policy_factory=factory,
                extra_row_fields={
                    "candidate": candidate.name,
                    "condition": "real-signed-loop-escape",
                    "base_game_id": game.base_game_id,
                },
            )
            assembled = factory.current
            records = [] if assembled is None else list(assembled.policy.records)
            _attach_loop_escape_trace(records, row["trace"])
            row["sampler_diagnostics"] = SAMPLER.sampler_diagnostics(records, row["trace"])
            rows.append(row)
            print(
                f"  {row['status']}: actions={row['actions_completed']} "
                f"unique_obs={row['observations']['unique']} "
                f"consecutive_repeats={row['observations']['consecutive_repeats']}",
                flush=True,
            )
    return rows


def candidate_result(
    candidate: LoopEscapeCandidate,
    rows: list[dict[str, Any]],
    replay: Mapping[str, Any],
    interface: Mapping[str, Any] | None,
) -> dict[str, Any]:
    behavior = SAMPLER.summarize_behavior(rows)
    engineering = SAMPLER.engineering_check(rows)
    diversity = SAMPLER.seed_diversity(rows)
    entropy_measured = behavior["action_entropy_fraction_of_legal_max"] is not None
    eligible = bool(
        engineering["passed"] and replay["matched"] and diversity["passed"] and entropy_measured
    )
    metrics = {name: behavior[name] for name, _direction in SELECTION_ORDER}
    return {
        "candidate": candidate.describe(),
        "selection_metrics": metrics,
        "behavior": behavior,
        "seed_diversity": diversity,
        "checks": {
            "eligible": eligible,
            "engineering": engineering,
            "same_seed_replay": dict(replay),
            "entropy_measured": entropy_measured,
        },
        "condition": {
            "interface": dict(interface or {}),
            "rows": [SAMPLER.behavior_only_row(row) for row in rows],
        },
    }


def rank_candidates(results: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Apply the preregistered lexicographic behavior-only selection."""

    if not results:
        raise ValueError("cannot rank an empty candidate set")
    records: list[dict[str, Any]] = []
    for declaration_index, result in enumerate(results):
        metrics = result["selection_metrics"]
        values: list[float] = []
        for name, direction in SELECTION_ORDER:
            raw = metrics.get(name)
            if raw is None:
                value = float("inf")
            else:
                value = float(raw)
                if direction == "higher":
                    value = -value
            values.append(value)
        records.append(
            {
                "candidate": str(result["candidate"]["name"]),
                "eligible": bool(result["checks"]["eligible"]),
                "selection_key": values,
                "declaration_index": declaration_index,
            }
        )
    records.sort(
        key=lambda item: (
            not item["eligible"],
            *item["selection_key"],
            item["declaration_index"],
        )
    )
    for rank, record in enumerate(records, start=1):
        record["rank"] = rank
    return records


def _default_output(parameters: Mapping[str, Any]) -> Path:
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
    identity = json.dumps(parameters, sort_keys=True, separators=(",", ":")).encode()
    suffix = hashlib.sha256(identity).hexdigest()[:10]
    return DEFAULT_RESULTS_DIR / f"{timestamp}-{suffix}.json"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--runtime-dir", type=Path, default=None)
    parser.add_argument("--seeds", type=int, nargs="+", default=list(DEFAULT_SEEDS))
    parser.add_argument("--games", nargs="+", default=list(DEFAULT_GAMES))
    parser.add_argument("--action-budget", type=int, default=DEFAULT_ACTION_BUDGET)
    parser.add_argument("--internal-steps", type=int, default=None)
    parser.add_argument(
        "--candidates",
        nargs="+",
        choices=tuple(CANDIDATE_BY_NAME),
        default=list(CANDIDATE_BY_NAME),
    )
    parser.add_argument("--environments-dir", type=Path, default=BASELINE.DEFAULT_ENVIRONMENTS_DIR)
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.action_budget <= 0:
        raise SystemExit("--action-budget must be positive")
    if len(set(args.seeds)) != len(args.seeds) or len(args.seeds) < 2:
        raise SystemExit("loop-escape calibration requires at least two distinct seeds")
    if len(set(args.candidates)) != len(args.candidates):
        raise SystemExit("--candidates must not contain duplicates")

    candidates = [CANDIDATE_BY_NAME[name] for name in args.candidates]
    declared_parameters = {
        "config": str(args.config),
        "runtime_dir": None if args.runtime_dir is None else str(args.runtime_dir),
        "seeds": list(args.seeds),
        "requested_games": list(args.games),
        "action_budget": args.action_budget,
        "internal_steps": args.internal_steps,
        "fixed_action_temperature": ACTION_TEMPERATURE,
        "fixed_coordinate_temperature": COORDINATE_TEMPERATURE,
        "candidates": [candidate.describe() for candidate in candidates],
    }
    output = (
        args.output.resolve() if args.output is not None else _default_output(declared_parameters)
    )
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing result: {output}")

    print(
        "Behavior-only loop-escape calibration: score and level progress are excluded.",
        flush=True,
    )
    print(json.dumps(declared_parameters, indent=2, sort_keys=True), flush=True)

    from flygi.arc.factory import build_connectome_policy
    from flygi.config import load_config

    config = load_config(args.config)
    if (
        config.decoder.action_temperature != ACTION_TEMPERATURE
        or config.decoder.coordinate_temperature != COORDINATE_TEMPERATURE
    ):
        raise SystemExit("config does not contain the frozen focused temperatures")
    runtime = BASELINE.load_arc_runtime()
    try:
        games = BASELINE.discover_games(runtime, args.environments_dir.resolve(), args.games)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    first_seed = BASELINE.derived_run_seeds(args.seeds[0], games[0].game_id)[1]
    first = candidates[0]
    template = build_connectome_policy(
        config,
        runtime.GameAction,
        runtime_dir=args.runtime_dir,
        internal_steps=args.internal_steps,
        decision_seed=first_seed,
        action_temperature=ACTION_TEMPERATURE,
        coordinate_temperature=COORDINATE_TEMPERATURE,
        loop_escape_enabled=True,
        loop_escape_exploration_bonus=first.exploration_bonus,
        loop_escape_unchanged_failure_penalty=first.unchanged_failure_penalty,
    )

    results: list[dict[str, Any]] = []
    for candidate in candidates:
        factory = PolicyFactory(
            build_connectome_policy,
            config,
            runtime.GameAction,
            runtime_dir=args.runtime_dir,
            bundle=template.bundle,
            projection=template.projection,
            internal_steps=args.internal_steps,
            candidate=candidate,
        )
        rows = _run_candidate(
            runtime,
            games,
            args.seeds,
            args.action_budget,
            args.environments_dir.resolve(),
            factory,
            candidate,
        )
        replay = SAMPLER._behavior_replay_check(
            runtime,
            games,
            args.seeds,
            args.action_budget,
            args.environments_dir.resolve(),
            rows,
            factory,
        )
        results.append(candidate_result(candidate, rows, replay, factory.interface))

    ranking = rank_candidates(results)
    selected = next((item["candidate"] for item in ranking if item["eligible"]), None)
    result = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "preregistration": {
            **declared_parameters,
            "resolved_games": [game.game_id for game in games],
            "score_blind": True,
            "excluded_from_output_and_selection": [
                "official scorecard",
                "score",
                "levels completed",
                "per-level scores",
            ],
            "selection": {
                "method": "lexicographic",
                "metrics": [
                    {"name": name, "direction": direction} for name, direction in SELECTION_ORDER
                ],
                "eligibility_guards": [
                    "engineering validity",
                    "same-seed replay",
                    "across-seed action/payload diversity for each selected game category",
                    "measured legal-normalized action entropy",
                ],
                "tie_breaker": "candidate declaration order",
            },
        },
        "selection": {
            "selected_candidate": selected,
            "ranking": ranking,
            "selection_succeeded": selected is not None,
        },
        "candidates": results,
        "provenance": {
            "git": BASELINE._git_provenance(),
            "python": sys.version,
            "platform": __import__("platform").platform(),
            "dependencies": BASELINE._dependency_versions(),
            "uv_lock_sha256": BASELINE.sha256_file(ROOT / "uv.lock"),
            "calibration_runner_sha256": BASELINE.sha256_file(Path(__file__).resolve()),
            "evaluation_harness_sha256": BASELINE.sha256_file(
                ROOT / "scripts" / "evaluate_random_baseline.py"
            ),
            "config_sha256": BASELINE.sha256_file(args.config),
            "peak_rss_bytes": BASELINE._peak_rss_bytes(),
            "games": [game.manifest() for game in games],
        },
    }
    BASELINE.write_json_exclusive(output, result)
    print(json.dumps(result["selection"], indent=2, sort_keys=True), flush=True)
    print(f"Wrote immutable score-blind loop-escape artifact: {output}", flush=True)
    return 0 if selected is not None else 1


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("calibrate_loop_escape", main))
