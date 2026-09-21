#!/usr/bin/env python3
"""Calibrate the fixed sampler using behavior only, never public ARC score.

The candidate set, ranking metrics, directions, and tie-break rule are declared
in this file before any run starts.  Each candidate is evaluated on matched
real-connectome and no-recurrent-graph bypass rows using the same derived
decision seed.  The selected candidate is determined only from exploration,
graph-causality, and runtime measurements:

* unique observations (higher is better),
* consecutive observation repeats (lower is better),
* policy entropy as a fraction of the legal maximum (higher is better),
* matched real-versus-bypass action/payload disagreement (higher is better),
* median real-condition policy time (lower is better).

Official score and level-progress fields are removed from the immutable output
and are never passed to the ranking code.  Engineering validity, same-seed
replay, across-seed diversity, and a live graph-causal effect are eligibility
guards rather than tunable objectives.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import math
import sys
from collections import Counter
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean, median
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

DEFAULT_CONFIG = ROOT / "configs/literal_rate_signed.yaml"
DEFAULT_RESULTS_DIR = ROOT / "results" / "sampler_calibration"
DEFAULT_GAMES = ("lp85", "ft09", "ls20", "sp80")
DEFAULT_SEEDS = (0, 1)
DEFAULT_ACTION_BUDGET = 40
CLICK_ONLY_GAMES = frozenset({"ft09", "lp85", "r11l", "s5i5", "tn36", "vc33"})
SCHEMA = "flygi.sampler-calibration"
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class SamplerCandidate:
    """One preregistered, scale-aware sampler operating point."""

    name: str
    action_temperature: float
    coordinate_temperature: float

    def describe(self) -> dict[str, str | float]:
        return {
            "name": self.name,
            "action_temperature": self.action_temperature,
            "coordinate_temperature": self.coordinate_temperature,
        }


# Paired points keep the search deliberately small.  The policy standardizes
# logits before applying these temperatures, so values are comparable across
# games and graph conditions.
CANDIDATES = (
    SamplerCandidate("focused", action_temperature=0.15, coordinate_temperature=0.20),
    SamplerCandidate("balanced", action_temperature=0.35, coordinate_temperature=0.50),
    SamplerCandidate("exploratory", action_temperature=0.70, coordinate_temperature=1.00),
)
CANDIDATE_BY_NAME = {candidate.name: candidate for candidate in CANDIDATES}

RANKING_METRICS = (
    ("mean_unique_observations", "higher"),
    ("mean_consecutive_repeats", "lower"),
    ("action_entropy_fraction_of_legal_max", "higher"),
    ("causal_turn_disagreement_rate", "higher"),
    ("median_policy_ns", "lower"),
)


def _load_script_module(filename: str, module_name: str) -> ModuleType:
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BASELINE = _load_script_module("evaluate_random_baseline.py", "_flygi_calibration_baseline")


def _canonical_payload(payload: Mapping[str, Any] | None) -> str:
    return json.dumps(payload or {}, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _behavioral_trace(trace: Sequence[Mapping[str, Any]]) -> tuple[tuple[int, str], ...]:
    """Return only decisions and payloads; timing and score cannot enter."""

    return tuple(
        (int(entry["action_id"]), _canonical_payload(entry.get("payload"))) for entry in trace
    )


def sampler_diagnostics(
    records: Sequence[Any], trace: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Summarize declared sampler probabilities against each legal action set."""

    if len(records) != len(trace):
        raise RuntimeError(
            f"policy emitted {len(records)} records for {len(trace)} completed decisions"
        )

    entropy_bits = 0.0
    legal_max_bits = 0.0
    entropy_turns = 0
    probabilities: list[float] = []
    coordinates: list[tuple[int, int]] = []
    coordinate_methods: Counter[str] = Counter()

    for record, entry in zip(records, trace, strict=True):
        if not bool(getattr(record, "forced_reset", False)):
            legal_count = len(entry.get("available_action_ids", []))
            if legal_count > 1:
                value = getattr(record, "action_entropy_bits", None)
                if value is None:
                    raise RuntimeError(
                        "policy TurnRecord lacks action_entropy_bits; sampler calibration "
                        "requires the stochastic-policy diagnostics"
                    )
                value = float(value)
                maximum = math.log2(legal_count)
                if not math.isfinite(value) or value < -1e-7 or value > maximum + 1e-5:
                    raise RuntimeError(
                        f"invalid action entropy {value!r} for {legal_count} legal actions"
                    )
                entropy_bits += max(0.0, value)
                legal_max_bits += maximum
                entropy_turns += 1

            probability = getattr(record, "action_probability", None)
            if probability is not None:
                probability = float(probability)
                if not math.isfinite(probability) or not 0.0 <= probability <= 1.0:
                    raise RuntimeError(f"invalid selected-action probability {probability!r}")
                probabilities.append(probability)

        if int(entry["action_id"]) == 6:
            payload = entry.get("payload") or {}
            x = getattr(record, "coordinate_x", None)
            y = getattr(record, "coordinate_y", None)
            if x is None:
                x = payload.get("x")
            if y is None:
                y = payload.get("y")
            if isinstance(x, int) and isinstance(y, int):
                coordinates.append((x, y))
            method = getattr(record, "coordinate_method", None)
            coordinate_methods[str(method or "unreported")] += 1

    return {
        "entropy_turns": entropy_turns,
        "action_entropy_bits": entropy_bits,
        "legal_max_entropy_bits": legal_max_bits,
        "action_entropy_fraction_of_legal_max": (
            entropy_bits / legal_max_bits if legal_max_bits > 0.0 else None
        ),
        "mean_selected_action_probability": fmean(probabilities) if probabilities else None,
        "coordinate_draws": len(coordinates),
        "unique_coordinates": len(set(coordinates)),
        "coordinate_methods": dict(sorted(coordinate_methods.items())),
    }


def summarize_behavior(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Build the score-blind metric view used by candidate ranking."""

    if not rows:
        raise ValueError("cannot summarize an empty calibration condition")
    entropy_bits = sum(float(row["sampler_diagnostics"]["action_entropy_bits"]) for row in rows)
    legal_max_bits = sum(
        float(row["sampler_diagnostics"]["legal_max_entropy_bits"]) for row in rows
    )
    policy_samples = [
        int(entry["policy_ns"])
        for row in rows
        for entry in row["trace"]
        if entry.get("policy_ns") is not None
    ]
    observation_counts = [int(row["observations"]["count"]) for row in rows]
    consecutive = [int(row["observations"]["consecutive_repeats"]) for row in rows]
    coordinate_draws = sum(int(row["sampler_diagnostics"]["coordinate_draws"]) for row in rows)
    unique_coordinate_sum = sum(
        int(row["sampler_diagnostics"]["unique_coordinates"]) for row in rows
    )
    return {
        "rows": len(rows),
        "actions": sum(int(row["actions_completed"]) for row in rows),
        "mean_unique_observations": fmean(int(row["observations"]["unique"]) for row in rows),
        "mean_consecutive_repeats": fmean(consecutive),
        "consecutive_repeat_rate": (
            sum(consecutive) / sum(max(0, count - 1) for count in observation_counts)
            if sum(max(0, count - 1) for count in observation_counts)
            else 0.0
        ),
        "action_entropy_bits": entropy_bits,
        "legal_max_entropy_bits": legal_max_bits,
        "action_entropy_fraction_of_legal_max": (
            entropy_bits / legal_max_bits if legal_max_bits > 0.0 else None
        ),
        "median_policy_ns": float(median(policy_samples)) if policy_samples else None,
        "p95_policy_ns": (
            float(__import__("numpy").percentile(policy_samples, 95)) if policy_samples else None
        ),
        "coordinate_draws": coordinate_draws,
        "sum_within_row_unique_coordinates": unique_coordinate_sum,
    }


def graph_causal_diversity(
    real_rows: Sequence[Mapping[str, Any]], bypass_rows: Sequence[Mapping[str, Any]]
) -> dict[str, Any]:
    """Compare matched action/payload traces under real and bypass dynamics."""

    def indexed(rows: Sequence[Mapping[str, Any]]) -> dict[tuple[str, int], Mapping[str, Any]]:
        return {(str(row["game_id"]), int(row["seed"])): row for row in rows}

    real = indexed(real_rows)
    bypass = indexed(bypass_rows)
    if real.keys() != bypass.keys():
        missing_bypass = sorted(real.keys() - bypass.keys())
        missing_real = sorted(bypass.keys() - real.keys())
        raise ValueError(
            f"real/bypass row keys differ; missing bypass={missing_bypass}, "
            f"missing real={missing_real}"
        )

    differing_pairs = 0
    differing_turns = 0
    compared_turns = 0
    per_pair: list[dict[str, Any]] = []
    for game_id, seed in sorted(real):
        left = _behavioral_trace(real[(game_id, seed)]["trace"])
        right = _behavioral_trace(bypass[(game_id, seed)]["trace"])
        width = max(len(left), len(right))
        mismatches = sum(
            index >= len(left) or index >= len(right) or left[index] != right[index]
            for index in range(width)
        )
        differing = mismatches > 0
        differing_pairs += int(differing)
        differing_turns += mismatches
        compared_turns += width
        per_pair.append(
            {
                "game_id": game_id,
                "seed": seed,
                "real_turns": len(left),
                "bypass_turns": len(right),
                "differing_turns": mismatches,
                "different": differing,
            }
        )
    return {
        "matched_pairs": len(per_pair),
        "differing_pairs": differing_pairs,
        "differing_pair_fraction": differing_pairs / len(per_pair) if per_pair else 0.0,
        "compared_turns": compared_turns,
        "differing_turns": differing_turns,
        "causal_turn_disagreement_rate": (
            differing_turns / compared_turns if compared_turns else 0.0
        ),
        "passed": bool(differing_pairs and differing_turns),
        "per_pair": per_pair,
    }


def seed_diversity(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Require stochastic traces across seeds, including click-only coverage."""

    by_game: dict[str, list[Mapping[str, Any]]] = {}
    for row in rows:
        by_game.setdefault(str(row["game_id"]), []).append(row)

    per_game: list[dict[str, Any]] = []
    for game_id in sorted(by_game):
        game_rows = by_game[game_id]
        base_game_id = str(game_rows[0].get("base_game_id", game_id.split("-", 1)[0]))
        trace_count = len({_behavioral_trace(row["trace"]) for row in game_rows})
        per_game.append(
            {
                "game_id": game_id,
                "base_game_id": base_game_id,
                "seeds": len({int(row["seed"]) for row in game_rows}),
                "unique_action_payload_traces": trace_count,
                "diverse": trace_count > 1,
                "category": "click_only" if base_game_id in CLICK_ONLY_GAMES else "mixed",
            }
        )

    seeds = {int(row["seed"]) for row in rows}
    selected_categories = {item["category"] for item in per_game}
    diverse_categories = {item["category"] for item in per_game if item["diverse"]}
    return {
        "seed_count": len(seeds),
        "games": len(per_game),
        "diverse_games": sum(bool(item["diverse"]) for item in per_game),
        "selected_categories": sorted(selected_categories),
        "diverse_categories": sorted(diverse_categories),
        "passed": len(seeds) >= 2 and selected_categories <= diverse_categories,
        "per_game": per_game,
    }


def engineering_check(rows: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Check deployment invariants without reading official score fields."""

    failed = sum(row["status"] != "success" for row in rows)
    illegal = sum(int(row["illegal_action_count"]) for row in rows)
    invalid_coordinates = sum(int(row["action6_coordinates"]["invalid"]) for row in rows)
    budget_violations = sum(
        int(row["actions_completed"]) > int(row["action_budget"])
        or (
            row["termination_reason"] == "budget_exhausted"
            and int(row["actions_completed"]) != int(row["action_budget"])
        )
        for row in rows
    )
    issues: list[str] = []
    if failed:
        issues.append(f"{failed} rows failed")
    if illegal:
        issues.append(f"{illegal} illegal actions")
    if invalid_coordinates:
        issues.append(f"{invalid_coordinates} invalid ACTION6 coordinates")
    if budget_violations:
        issues.append(f"{budget_violations} action-budget violations")
    return {
        "passed": not issues,
        "issues": issues,
        "rows": len(rows),
        "failed_rows": failed,
        "illegal_actions": illegal,
        "invalid_action6_coordinates": invalid_coordinates,
        "budget_violations": budget_violations,
    }


def behavior_only_row(row: Mapping[str, Any]) -> dict[str, Any]:
    """Remove public-score and level-progress values from a persisted row."""

    cleaned = copy.deepcopy(dict(row))
    cleaned.pop("official", None)
    cleaned.pop("final_levels_completed", None)
    for entry in cleaned.get("trace", []):
        entry.pop("levels_completed_before", None)
        entry.pop("levels_completed_after", None)
    return cleaned


def _metric_rank(values: Mapping[str, float], direction: str) -> dict[str, int]:
    reverse = direction == "higher"
    ordered_values = sorted(set(values.values()), reverse=reverse)
    lookup = {value: index + 1 for index, value in enumerate(ordered_values)}
    return {name: lookup[value] for name, value in values.items()}


def rank_candidates(candidate_results: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Apply the preregistered equal-weight ordinal ranking."""

    if not candidate_results:
        raise ValueError("cannot rank an empty candidate set")
    names = [str(result["candidate"]["name"]) for result in candidate_results]
    if len(set(names)) != len(names):
        raise ValueError("candidate names must be unique")

    eligible_names = {
        str(result["candidate"]["name"])
        for result in candidate_results
        if bool(result["checks"]["eligible"])
    }
    metric_ranks: dict[str, dict[str, int]] = {}
    for metric, direction in RANKING_METRICS:
        values: dict[str, float] = {}
        missing: set[str] = set()
        for result in candidate_results:
            name = str(result["candidate"]["name"])
            raw = result["ranking_metrics"].get(metric)
            if raw is None or not math.isfinite(float(raw)):
                missing.add(name)
            else:
                values[name] = float(raw)
        if not values:
            metric_ranks[metric] = {name: 1 for name in names}
            continue
        if eligible_names:
            eligible_values = {
                name: value for name, value in values.items() if name in eligible_names
            }
            ineligible_values = {
                name: value for name, value in values.items() if name not in eligible_names
            }
            ranks = _metric_rank(eligible_values, direction) if eligible_values else {}
            if ineligible_values:
                offset = max(ranks.values(), default=0)
                ranks.update(
                    {
                        name: rank + offset
                        for name, rank in _metric_rank(ineligible_values, direction).items()
                    }
                )
        else:
            ranks = _metric_rank(values, direction)
        missing_rank = max(ranks.values(), default=0) + 1
        ranks.update({name: missing_rank for name in missing})
        metric_ranks[metric] = ranks

    records: list[dict[str, Any]] = []
    for declaration_index, result in enumerate(candidate_results):
        name = str(result["candidate"]["name"])
        per_metric = {metric: metric_ranks[metric][name] for metric, _ in RANKING_METRICS}
        records.append(
            {
                "candidate": name,
                "eligible": bool(result["checks"]["eligible"]),
                "metric_ranks": per_metric,
                "rank_sum": sum(per_metric.values()),
                "declaration_index": declaration_index,
            }
        )
    records.sort(
        key=lambda item: (
            not item["eligible"],
            item["rank_sum"],
            item["declaration_index"],
        )
    )
    for index, record in enumerate(records, start=1):
        record["rank"] = index
    return records


class PolicyFactory:
    """Create fresh, seeded policies while reusing immutable graph assets."""

    def __init__(
        self,
        builder: Callable[..., Any],
        config: Any,
        actions: Any,
        *,
        runtime_dir: Path | None,
        bundle: Any,
        projection: Any,
        ablate_graph: bool,
        internal_steps: int | None,
        candidate: SamplerCandidate,
    ) -> None:
        self._builder = builder
        self._config = config
        self._actions = actions
        self._runtime_dir = runtime_dir
        self._bundle = bundle
        self._projection = projection
        self._ablate_graph = ablate_graph
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
            ablate_graph=self._ablate_graph,
            internal_steps=self._internal_steps,
            decision_seed=decision_seed,
            action_temperature=self._candidate.action_temperature,
            coordinate_temperature=self._candidate.coordinate_temperature,
        )
        self.current = assembled
        if self.interface is None:
            self.interface = assembled.describe()
        return assembled.policy


def _run_condition(
    runtime: Any,
    games: Sequence[Any],
    seeds: Sequence[int],
    action_budget: int,
    environments_dir: Path,
    factory: PolicyFactory,
    *,
    candidate: SamplerCandidate,
    condition: str,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    total = len(seeds) * len(games)
    position = 0
    for seed in seeds:
        for game in games:
            position += 1
            print(
                f"[{candidate.name}/{condition} {position}/{total}] "
                f"seed={seed} game={game.game_id}",
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
                    "condition": condition,
                    "base_game_id": game.base_game_id,
                },
            )
            assembled = factory.current
            records = [] if assembled is None else list(assembled.policy.records)
            row["sampler_diagnostics"] = sampler_diagnostics(records, row["trace"])
            rows.append(row)
            print(
                f"  {row['status']}: actions={row['actions_completed']} "
                f"unique_obs={row['observations']['unique']} "
                f"consecutive_repeats={row['observations']['consecutive_repeats']}",
                flush=True,
            )
    return rows


def _behavior_replay_check(
    runtime: Any,
    games: Sequence[Any],
    seeds: Sequence[int],
    action_budget: int,
    environments_dir: Path,
    rows: Sequence[Mapping[str, Any]],
    factory: PolicyFactory,
) -> dict[str, Any]:
    target_game = games[0]
    target_seed = int(seeds[0])
    reference = next(
        row for row in rows if row["seed"] == target_seed and row["game_id"] == target_game.game_id
    )
    factory.current = None
    replay = BASELINE.evaluate_one(
        runtime,
        target_game,
        target_seed,
        action_budget,
        environments_dir,
        policy_factory=factory,
    )
    matched = (
        reference["status"] == "success"
        and replay["status"] == "success"
        and reference["replay_trace_sha256"] == replay["replay_trace_sha256"]
    )
    return {
        "game_id": target_game.game_id,
        "seed": target_seed,
        "matched": matched,
        "reference_status": reference["status"],
        "replay_status": replay["status"],
        "reference_trace_sha256": reference["replay_trace_sha256"],
        "replay_trace_sha256": replay["replay_trace_sha256"],
        "replay_failure": replay["failure"],
        "compared_fields": ["status", "action_payload_observation_trace_sha256"],
        "official_score_compared": False,
    }


def _candidate_result(
    candidate: SamplerCandidate,
    real_rows: list[dict[str, Any]],
    bypass_rows: list[dict[str, Any]],
    replay: Mapping[str, Any],
    real_interface: Mapping[str, Any] | None,
    bypass_interface: Mapping[str, Any] | None,
) -> dict[str, Any]:
    real_behavior = summarize_behavior(real_rows)
    bypass_behavior = summarize_behavior(bypass_rows)
    causal = graph_causal_diversity(real_rows, bypass_rows)
    diversity = seed_diversity(real_rows)
    real_engineering = engineering_check(real_rows)
    bypass_engineering = engineering_check(bypass_rows)
    entropy_measured = real_behavior["action_entropy_fraction_of_legal_max"] is not None
    eligible = bool(
        real_engineering["passed"]
        and bypass_engineering["passed"]
        and replay["matched"]
        and diversity["passed"]
        and causal["passed"]
        and entropy_measured
    )
    ranking_metrics = {
        "mean_unique_observations": real_behavior["mean_unique_observations"],
        "mean_consecutive_repeats": real_behavior["mean_consecutive_repeats"],
        "action_entropy_fraction_of_legal_max": real_behavior[
            "action_entropy_fraction_of_legal_max"
        ],
        "causal_turn_disagreement_rate": causal["causal_turn_disagreement_rate"],
        "median_policy_ns": real_behavior["median_policy_ns"],
    }
    return {
        "candidate": candidate.describe(),
        "ranking_metrics": ranking_metrics,
        "behavior": {"real": real_behavior, "bypass": bypass_behavior},
        "graph_causal_diversity": causal,
        "seed_diversity": diversity,
        "checks": {
            "eligible": eligible,
            "real_engineering": real_engineering,
            "bypass_engineering": bypass_engineering,
            "same_seed_replay": dict(replay),
            "entropy_measured": entropy_measured,
        },
        "conditions": {
            "real": {
                "interface": dict(real_interface or {}),
                "rows": [behavior_only_row(row) for row in real_rows],
            },
            "bypass": {
                "interface": dict(bypass_interface or {}),
                "rows": [behavior_only_row(row) for row in bypass_rows],
            },
        },
    }


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
        help="subset of the preregistered candidates; arbitrary temperatures are not accepted",
    )
    parser.add_argument("--environments-dir", type=Path, default=BASELINE.DEFAULT_ENVIRONMENTS_DIR)
    parser.add_argument("--output", type=Path, default=None)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.action_budget <= 0:
        raise SystemExit("--action-budget must be positive")
    if len(set(args.seeds)) != len(args.seeds):
        raise SystemExit("--seeds must not contain duplicates")
    if len(args.seeds) < 2:
        raise SystemExit("sampler calibration requires at least two seeds")
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
        "candidates": [candidate.describe() for candidate in candidates],
    }
    output = (
        args.output.resolve() if args.output is not None else _default_output(declared_parameters)
    )
    if output.exists():
        raise SystemExit(f"refusing to overwrite existing result: {output}")

    print(
        "Behavior-only sampler calibration: official score and level progress "
        "are excluded from ranking and output.",
        flush=True,
    )
    print(json.dumps(declared_parameters, indent=2, sort_keys=True), flush=True)

    from flygi.arc.factory import build_connectome_policy
    from flygi.config import load_config

    config = load_config(args.config)
    runtime = BASELINE.load_arc_runtime()
    try:
        games = BASELINE.discover_games(runtime, args.environments_dir.resolve(), args.games)
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(str(exc)) from exc

    # Load the graph and build each condition's immutable projection exactly
    # once.  Candidate policies reuse these objects, so only sampler settings
    # vary within a condition.
    initial_seed = BASELINE.derived_run_seeds(args.seeds[0], games[0].game_id)[1]
    first = candidates[0]
    real_template = build_connectome_policy(
        config,
        runtime.GameAction,
        runtime_dir=args.runtime_dir,
        internal_steps=args.internal_steps,
        decision_seed=initial_seed,
        action_temperature=first.action_temperature,
        coordinate_temperature=first.coordinate_temperature,
    )
    bypass_template = build_connectome_policy(
        config,
        runtime.GameAction,
        runtime_dir=args.runtime_dir,
        bundle=real_template.bundle,
        ablate_graph=True,
        internal_steps=args.internal_steps,
        decision_seed=initial_seed,
        action_temperature=first.action_temperature,
        coordinate_temperature=first.coordinate_temperature,
    )

    candidate_results: list[dict[str, Any]] = []
    for candidate in candidates:
        real_factory = PolicyFactory(
            build_connectome_policy,
            config,
            runtime.GameAction,
            runtime_dir=args.runtime_dir,
            bundle=real_template.bundle,
            projection=real_template.projection,
            ablate_graph=False,
            internal_steps=args.internal_steps,
            candidate=candidate,
        )
        bypass_factory = PolicyFactory(
            build_connectome_policy,
            config,
            runtime.GameAction,
            runtime_dir=args.runtime_dir,
            bundle=real_template.bundle,
            projection=bypass_template.projection,
            ablate_graph=True,
            internal_steps=args.internal_steps,
            candidate=candidate,
        )
        real_rows = _run_condition(
            runtime,
            games,
            args.seeds,
            args.action_budget,
            args.environments_dir.resolve(),
            real_factory,
            candidate=candidate,
            condition="real",
        )
        bypass_rows = _run_condition(
            runtime,
            games,
            args.seeds,
            args.action_budget,
            args.environments_dir.resolve(),
            bypass_factory,
            candidate=candidate,
            condition="no-recurrent-graph-bypass",
        )
        replay = _behavior_replay_check(
            runtime,
            games,
            args.seeds,
            args.action_budget,
            args.environments_dir.resolve(),
            real_rows,
            real_factory,
        )
        candidate_results.append(
            _candidate_result(
                candidate,
                real_rows,
                bypass_rows,
                replay,
                real_factory.interface,
                bypass_factory.interface,
            )
        )

    ranking = rank_candidates(candidate_results)
    selected = next((item["candidate"] for item in ranking if item["eligible"]), None)
    result = {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "created_at": datetime.now(UTC).isoformat(),
        "preregistration": {
            **declared_parameters,
            "resolved_games": [game.game_id for game in games],
            "score_blind": True,
            "excluded_from_output_and_ranking": [
                "official scorecard",
                "score",
                "levels completed",
                "per-level scores",
            ],
            "ranking": {
                "method": "equal-weight ordinal rank sum",
                "metrics": [
                    {"name": metric, "direction": direction, "weight": 1}
                    for metric, direction in RANKING_METRICS
                ],
                "eligibility_guards": [
                    "engineering validity in both conditions",
                    "same-seed real-condition replay",
                    "across-seed action/payload diversity for each selected game category",
                    "nonzero matched real-versus-bypass action/payload disagreement",
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
        "candidates": candidate_results,
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
    print(f"Wrote immutable score-blind calibration artifact: {output}", flush=True)
    return 0 if selected is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
