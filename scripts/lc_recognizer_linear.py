#!/usr/bin/env python3
"""H-LC-RECOGNIZER escalation 2: game-held-out LINEAR probe.

AMENDMENT REGISTERED 2026-09-27, after the nearest-centroid endpoint and
before this run: the centroid test bottomed out with EVERY reader at or
below chance (real LC 0.367, real LH 0.320, scrambled control LC 0.546,
raw histogram 0.520) -- a test all arms fail equally cannot separate the
fly from its control, so one escalation is preregistered: an L2 logistic
probe (C=1, balanced classes, features z-scored on the training folds),
leave-one-GAME-out over the same cached feature matrices, identical
pipeline for every arm. This is the last escalation: if the real bio-eye
LC probe does not beat BOTH the scrambled-encoder control and the raw-grid
baseline here, H-LC-RECOGNIZER is recorded dead as tested and no further
decoder shopping is allowed on this question.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from lc_recognizer_premise import DEAD_GAMES, _grid_baseline_features  # noqa: E402


def holdout_linear(features: np.ndarray, game_names: list[str], labels: np.ndarray) -> dict:
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    is_dead = np.array([game_names[i] in DEAD_GAMES for i in labels])
    per_game: dict[str, float] = {}
    for i, held_out in enumerate(game_names):
        test = labels == i
        scaler = StandardScaler().fit(features[~test])
        model = LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000)
        model.fit(scaler.transform(features[~test]), is_dead[~test])
        predicted = model.predict(scaler.transform(features[test]))
        per_game[held_out] = float((predicted == is_dead[test]).mean())
    return {
        "mean_accuracy": float(np.mean(list(per_game.values()))),
        "per_game": per_game,
    }


def main() -> int:
    with np.load(ROOT / "results" / "diagnostics" / "recognizer_frames.npz") as archive:
        grids = {k: archive[k] for k in archive.files}
    game_names = list(grids.keys())
    labels = np.concatenate([np.full(len(v), i) for i, v in enumerate(grids.values())])
    stacked = np.concatenate(list(grids.values()), axis=0)

    report: dict = {"holdout_chance": 0.5, "arms": {}}
    report["baseline_grid_histogram"] = holdout_linear(
        _grid_baseline_features(stacked), game_names, labels
    )
    print("baseline:", report["baseline_grid_histogram"]["mean_accuracy"], flush=True)
    for arm in ("real_bioeye", "control_scrambled"):
        cache = ROOT / "results" / "diagnostics" / f"recognizer_features_{arm}.npz"
        with np.load(cache) as archive:
            report["arms"][arm] = {
                group: holdout_linear(archive[group], game_names, labels)
                for group in archive.files
            }
        for group, result in report["arms"][arm].items():
            print(f"{arm} {group}: {result['mean_accuracy']:.4f}", flush=True)

    real = report["arms"]["real_bioeye"]
    control = report["arms"]["control_scrambled"]
    baseline = report["baseline_grid_histogram"]["mean_accuracy"]
    report["kill_condition_met"] = bool(
        real["lc_family"]["mean_accuracy"]
        <= max(control["lc_family"]["mean_accuracy"], baseline)
    )
    out = ROOT / "results" / "recognizer_premise_linear.json"
    out.write_text(json.dumps(report, indent=2))
    print(json.dumps({k: v for k, v in report.items() if k != "arms"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
