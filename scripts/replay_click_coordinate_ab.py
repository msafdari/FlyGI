#!/usr/bin/env python3
"""Locked replay gate for H-COORDINATE-CONVENTION.

This script does not let either head choose actions. It reconstructs the exact
cached frames behind already-recorded ``sg-combo`` traces, verifies every frame
hash, and presents the same executed ACTION6 examples in the same order to:

* A: ``legacy_xy_flat`` (the historical x*64+y implementation); and
* B: ``arc_row_major`` (ARC x=column, y=row; flat=y*64+x).

Predictions are recorded before each online update. The experiment and its
promotion/kill rules are preregistered under H-COORDINATE-CONVENTION in
``EXPERIMENTS.yaml``.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import sys
from collections import defaultdict
from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean, median
from types import ModuleType
from typing import Any

import numpy as np
from sklearn.metrics import average_precision_score

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

SCHEMA = "flygi.click-coordinate-replay.v1"
HYPOTHESIS = "H-COORDINATE-CONVENTION"
DEFAULT_ROWS = ROOT / "results" / "connectome_agent" / "sg-combo.rows.jsonl"
DEFAULT_CONFIG = ROOT / "configs" / "combo_light.yaml"
DEFAULT_ENVIRONMENTS = ROOT / "environment_files"
DEFAULT_OUTPUT = ROOT / "results" / "connectome_agent" / "coordinate_convention_replay.json"
DEFAULT_GAMES = ("ft09", "lp85", "r11l", "tn36", "vc33", "sp80")
DEFAULT_SEEDS = (0, 1, 2)
EPSILON = 1e-7


def _load_baseline_module() -> ModuleType:
    path = ROOT / "scripts" / "evaluate_random_baseline.py"
    spec = importlib.util.spec_from_file_location("_flygi_coordinate_replay", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load evaluator helpers from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _base_game(game_id: str) -> str:
    return game_id.split("-", 1)[0]


def _read_rows(
    path: Path,
    *,
    games: Sequence[str],
    seeds: Sequence[int],
) -> list[dict[str, Any]]:
    wanted_games = set(games)
    wanted_seeds = set(seeds)
    selected: list[dict[str, Any]] = []
    seen: set[tuple[int, str]] = set()
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        row = json.loads(line)
        game = _base_game(str(row["game_id"]))
        seed = int(row["seed"])
        if game not in wanted_games or seed not in wanted_seeds:
            continue
        identity = (seed, game)
        if identity in seen:
            raise RuntimeError(f"duplicate selected row {identity} at line {line_number}")
        if row.get("status") != "success":
            raise RuntimeError(f"selected row {identity} is not successful")
        if not row.get("trace"):
            raise RuntimeError(f"selected row {identity} has no trace")
        seen.add(identity)
        selected.append(row)

    expected = {(seed, game) for seed in seeds for game in games}
    missing = sorted(expected - seen)
    unexpected = sorted(seen - expected)
    if missing or unexpected:
        raise RuntimeError(
            f"selected rows do not match preregistration: missing={missing}, "
            f"unexpected={unexpected}"
        )
    return sorted(selected, key=lambda row: (int(row["seed"]), str(row["game_id"])))


def _binary_log_loss(labels: Sequence[bool], probabilities: Sequence[float]) -> float:
    if not labels:
        raise ValueError("binary log loss needs at least one observation")
    y = np.asarray(labels, dtype=np.float64)
    p = np.clip(np.asarray(probabilities, dtype=np.float64), EPSILON, 1.0 - EPSILON)
    return float(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p)).mean())


def _average_precision_or_none(
    labels: Sequence[bool], probabilities: Sequence[float]
) -> float | None:
    y = np.asarray(labels, dtype=np.bool_)
    if not y.any() or y.all():
        return None
    return float(average_precision_score(y, np.asarray(probabilities, dtype=np.float64)))


def _make_action(runtime: Any, action_identifier: int) -> Any:
    factory = getattr(runtime.GameAction, "from_id", None)
    return (
        factory(action_identifier) if callable(factory) else runtime.GameAction(action_identifier)
    )


def _replay_row(
    *,
    baseline: ModuleType,
    runtime: Any,
    frozen_game: Any,
    row: Mapping[str, Any],
    environments_dir: Path,
    cell_columns: np.ndarray,
    column_count: int,
    head_kwargs: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    from flygi.controller.click_head import OnlineClickHead
    from flygi.encoding.features import latest_grid

    seed = int(row["seed"])
    game_id = str(row["game_id"])
    environment_seed = int(row["environment_seed"])
    legacy = OnlineClickHead(
        "retinotopic",
        cell_columns=cell_columns,
        column_count=column_count,
        coordinate_convention="legacy_xy_flat",
        **head_kwargs,
    )
    corrected = OnlineClickHead(
        "retinotopic",
        cell_columns=cell_columns,
        column_count=column_count,
        coordinate_convention="arc_row_major",
        **head_kwargs,
    )

    # ASSUMPTION: cached games plus the stored environment seed reconstruct the
    # exact policy frames. Every before/after hash below checks this assumption;
    # no metric is emitted after even one mismatch.
    arcade = baseline._new_offline_arcade(runtime, environments_dir)
    baseline._seed_process_for_environment(environment_seed)
    environment = arcade.make(
        frozen_game.game_id,
        seed=environment_seed,
        save_recording=False,
        include_frame_data=False,
    )
    if environment is None or environment.observation_space is None:
        raise RuntimeError(f"could not construct replay environment for {(seed, game_id)}")
    frame = environment.observation_space

    examples: list[dict[str, Any]] = []
    verified_steps = 0
    for entry in row["trace"]:
        step = int(entry["step"])
        before_hash = baseline._frame_fingerprint(frame)
        if before_hash != entry["observation_before_sha256"]:
            raise RuntimeError(
                f"before-frame mismatch for {(seed, game_id)} step {step}: "
                f"{before_hash} != {entry['observation_before_sha256']}"
            )

        action_identifier = int(entry["action_id"])
        payload = dict(entry.get("payload") or {})
        source_grid: np.ndarray | None = None
        probability_legacy: float | None = None
        probability_corrected: float | None = None
        if action_identifier == 6:
            x, y = payload.get("x"), payload.get("y")
            if not isinstance(x, int) or isinstance(x, bool):
                raise RuntimeError(f"invalid replay x at {(seed, game_id, step)}: {x!r}")
            if not isinstance(y, int) or isinstance(y, bool):
                raise RuntimeError(f"invalid replay y at {(seed, game_id, step)}: {y!r}")
            source_grid = np.asarray(latest_grid(frame), dtype=np.int8).copy()
            probability_legacy = legacy.probability(source_grid, x, y)
            probability_corrected = corrected.probability(source_grid, x, y)

        response = environment.step(_make_action(runtime, action_identifier), data=payload)
        if response is None:
            raise RuntimeError(f"environment returned no frame at {(seed, game_id, step)}")
        after_hash = baseline._frame_fingerprint(response)
        if after_hash != entry["observation_after_sha256"]:
            raise RuntimeError(
                f"after-frame mismatch for {(seed, game_id)} step {step}: "
                f"{after_hash} != {entry['observation_after_sha256']}"
            )
        verified_steps += 1

        if source_grid is not None:
            destination_grid = np.asarray(latest_grid(response), dtype=np.int8)
            changed = bool(np.any(source_grid != destination_grid))
            x, y = int(payload["x"]), int(payload["y"])
            assert probability_legacy is not None and probability_corrected is not None
            examples.append(
                {
                    "step": step,
                    "x": x,
                    "y": y,
                    "changed": changed,
                    "legacy_probability": probability_legacy,
                    "corrected_probability": probability_corrected,
                }
            )
            legacy.update(source_grid, x, y, changed)
            corrected.update(source_grid, x, y, changed)
        frame = response

    labels = [bool(example["changed"]) for example in examples]
    legacy_probabilities = [float(example["legacy_probability"]) for example in examples]
    corrected_probabilities = [float(example["corrected_probability"]) for example in examples]
    if not labels:
        raise RuntimeError(f"selected row {(seed, game_id)} has no ACTION6 examples")
    legacy_loss = _binary_log_loss(labels, legacy_probabilities)
    corrected_loss = _binary_log_loss(labels, corrected_probabilities)
    summary = {
        "seed": seed,
        "game_id": game_id,
        "verified_steps": verified_steps,
        "clicks": len(labels),
        "changed_clicks": sum(labels),
        "legacy_log_loss": legacy_loss,
        "corrected_log_loss": corrected_loss,
        "corrected_minus_legacy_log_loss": corrected_loss - legacy_loss,
        "legacy_average_precision": _average_precision_or_none(labels, legacy_probabilities),
        "corrected_average_precision": _average_precision_or_none(labels, corrected_probabilities),
    }
    return summary, examples


def _summarize(
    row_summaries: Sequence[Mapping[str, Any]],
    examples: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    deltas = [float(row["corrected_minus_legacy_log_loss"]) for row in row_summaries]
    legacy_losses = [float(row["legacy_log_loss"]) for row in row_summaries]
    corrected_losses = [float(row["corrected_log_loss"]) for row in row_summaries]
    by_game: dict[str, list[float]] = defaultdict(list)
    for row in row_summaries:
        by_game[_base_game(str(row["game_id"]))].append(
            float(row["corrected_minus_legacy_log_loss"])
        )
    game_deltas = {game: fmean(values) for game, values in sorted(by_game.items())}
    labels = [bool(example["changed"]) for example in examples]

    # PREREGISTERED CONTRACT: single-class rows remain in log loss but are
    # excluded from average precision. Pooling every example first would make
    # an all-positive row look informative merely because some other row has a
    # negative label. Group before pooling so the exclusion is real.
    examples_by_row: dict[tuple[int, str], list[Mapping[str, Any]]] = defaultdict(list)
    for example in examples:
        identity = (int(example["seed"]), str(example["game_id"]))
        examples_by_row[identity].append(example)
    ap_examples: list[Mapping[str, Any]] = []
    for row_examples in examples_by_row.values():
        row_labels = [bool(example["changed"]) for example in row_examples]
        if any(row_labels) and not all(row_labels):
            ap_examples.extend(row_examples)
    ap_labels = [bool(example["changed"]) for example in ap_examples]
    legacy_ap_probabilities = [float(example["legacy_probability"]) for example in ap_examples]
    corrected_ap_probabilities = [
        float(example["corrected_probability"]) for example in ap_examples
    ]
    legacy_ap = _average_precision_or_none(ap_labels, legacy_ap_probabilities)
    corrected_ap = _average_precision_or_none(ap_labels, corrected_ap_probabilities)

    checks = {
        "mean_row_log_loss_lower": fmean(corrected_losses) < fmean(legacy_losses),
        "median_row_delta_below_zero": median(deltas) < 0.0,
        "at_least_four_games_nonworse": sum(delta <= 0.0 for delta in game_deltas.values()) >= 4,
        "aggregate_average_precision_nonworse": (
            legacy_ap is not None and corrected_ap is not None and corrected_ap >= legacy_ap
        ),
    }
    return {
        "rows": len(row_summaries),
        "games": len(game_deltas),
        "clicks": len(examples),
        "changed_clicks": sum(labels),
        "average_precision_rows": sum(
            any(bool(example["changed"]) for example in row_examples)
            and not all(bool(example["changed"]) for example in row_examples)
            for row_examples in examples_by_row.values()
        ),
        "average_precision_clicks": len(ap_examples),
        "legacy_mean_row_log_loss": fmean(legacy_losses),
        "corrected_mean_row_log_loss": fmean(corrected_losses),
        "mean_row_log_loss_delta": fmean(deltas),
        "median_row_log_loss_delta": median(deltas),
        "legacy_aggregate_average_precision": legacy_ap,
        "corrected_aggregate_average_precision": corrected_ap,
        "game_mean_log_loss_deltas": game_deltas,
        "promotion_checks": checks,
        "replay_gate_passed": all(checks.values()),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path, default=DEFAULT_ROWS)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--environments-dir", type=Path, default=DEFAULT_ENVIRONMENTS)
    parser.add_argument("--games", nargs="+", default=list(DEFAULT_GAMES))
    parser.add_argument("--seeds", nargs="+", type=int, default=list(DEFAULT_SEEDS))
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    rows_path = args.rows.resolve()
    config_path = args.config.resolve()
    environments_dir = args.environments_dir.resolve()
    output_path = args.output.resolve()
    if output_path.exists():
        raise SystemExit(f"refusing to overwrite immutable result: {output_path}")
    if len(set(args.games)) != len(args.games) or len(set(args.seeds)) != len(args.seeds):
        raise SystemExit("games and seeds must be unique")

    from flygi.config import load_config
    from flygi.controller.click_head import load_cell_columns

    baseline = _load_baseline_module()
    runtime = baseline.load_arc_runtime()
    selected_rows = _read_rows(rows_path, games=args.games, seeds=args.seeds)
    frozen_games = {
        _base_game(game.game_id): game
        for game in baseline.discover_games(runtime, environments_dir, args.games)
    }
    config = load_config(config_path)
    cell_columns, column_count = load_cell_columns(config.graph.output_dir)
    head_kwargs = {
        "weight": config.controller.click_head_weight,
        "learning_rate": config.controller.click_head_learning_rate,
        "permutation_seed": config.controller.click_head_seed,
        "negative_scale": config.controller.click_head_negative_scale,
    }

    row_summaries: list[dict[str, Any]] = []
    examples: list[dict[str, Any]] = []
    for index, row in enumerate(selected_rows, 1):
        game = _base_game(str(row["game_id"]))
        print(
            f"[{index}/{len(selected_rows)}] seed={row['seed']} game={row['game_id']}",
            flush=True,
        )
        summary, row_examples = _replay_row(
            baseline=baseline,
            runtime=runtime,
            frozen_game=frozen_games[game],
            row=row,
            environments_dir=environments_dir,
            cell_columns=cell_columns,
            column_count=column_count,
            head_kwargs=head_kwargs,
        )
        row_summaries.append(summary)
        examples.extend(
            {"seed": int(row["seed"]), "game_id": str(row["game_id"]), **example}
            for example in row_examples
        )
        print(
            f"  clicks={summary['clicks']} positives={summary['changed_clicks']} "
            f"delta_log_loss={summary['corrected_minus_legacy_log_loss']:+.6f}",
            flush=True,
        )

    aggregate = _summarize(row_summaries, examples)
    artifact = {
        "schema": SCHEMA,
        "created_at": datetime.now(UTC).isoformat(),
        "hypothesis": HYPOTHESIS,
        "claim_tier": "measured under exact cached-trace replay",
        "source": {
            "analyzer_path": str(Path(__file__).resolve()),
            "analyzer_sha256": _sha256_file(Path(__file__).resolve()),
            "registry_path": str((ROOT / "EXPERIMENTS.yaml").resolve()),
            "registry_sha256": _sha256_file(ROOT / "EXPERIMENTS.yaml"),
            "rows_path": str(rows_path),
            "rows_sha256": _sha256_file(rows_path),
            "config_path": str(config_path),
            "config_sha256": _sha256_file(config_path),
            "environments_dir": str(environments_dir),
            "games": list(args.games),
            "seeds": list(args.seeds),
        },
        "frozen_delta": {
            "control_a": "legacy_xy_flat",
            "intervention_b": "arc_row_major",
            "only_change": "5x5 click-patch coordinate flattening/order",
        },
        "assumptions": [
            "stored before/after hashes make cached replay fidelity falsifiable",
            "prequential executed-click prediction is only a bridge to ranking and score",
            "public score-bearing games are development endpoints, not held-out transfer",
        ],
        "aggregate": aggregate,
        "per_row": row_summaries,
        "examples": examples,
    }
    if not all(math.isfinite(float(row["legacy_log_loss"])) for row in row_summaries):
        raise RuntimeError("legacy result contains non-finite log loss")
    if not all(math.isfinite(float(row["corrected_log_loss"])) for row in row_summaries):
        raise RuntimeError("corrected result contains non-finite log loss")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(aggregate, indent=2, sort_keys=True), flush=True)
    print(f"wrote {output_path}", flush=True)
    return 0 if aggregate["replay_gate_passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
