#!/usr/bin/env python3
"""H-CONSEQUENCE-COUPLING premise-killer (preregistered in EXPERIMENTS.yaml).

Question: does the fly's driven state carry learnable action-consequence
information -- "will this action change the frame?" -- beyond what the action
identity and the raw observation already give? This is the smallest offline
test of the StochasticGoose-style fix (online consequence readout feeding
the primary ranking term). If real N_t adds nothing over raw grid features,
the reservoir-readout premise is dead before anything is built.

Protocol (identical for every arm): per game, features [X_t, onehot(a_t)],
target changed(t+1) = any(grid_{t+1} != grid_t); temporal split 60/40
within game (train early, test late -- the online-realistic direction);
logistic regression, fixed C=1, saga, class-balanced; metric = test AUC.

ASSUMPTION: the frame-change bit is the right consequence target because it
is the signal the preview's best non-LLM agent (StochasticGoose, 12.58%)
trained on; milestone distance would be stronger but is not extractable
from random-legal streams.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
STREAMS = ROOT / "results" / "jepa" / "streams"
STATES = ROOT / "results" / "jepa" / "states"
OUT = ROOT / "results" / "jepa" / "consequence_premise.json"

ARMS = ("action_only", "raw_grid", "bioeye", "real", "null", "bypass")


def _bioeye_projection():
    from flygi.config import load_config
    from flygi.encoding.retinotopic import build_columnar_colour_projection

    config = load_config(ROOT / "configs" / "literal_rate_bioeye_t4t5.yaml")
    return build_columnar_colour_projection(Path(config.graph.output_dir), 166_700)


def main() -> int:
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import roc_auc_score

    projection = _bioeye_projection()
    occupied = np.unique(projection._column_key)
    results: dict[str, dict[str, float]] = {arm: {} for arm in ARMS}

    for stream_path in sorted(STREAMS.glob("*.npz")):
        game = stream_path.stem
        with np.load(stream_path) as archive:
            grids = np.asarray(archive["grids"], dtype=np.int8)
            actions = np.asarray(archive["action_ids"])
        T = grids.shape[0] - 1  # transitions
        changed = np.array(
            [bool((grids[t + 1] != grids[t]).any()) for t in range(T)], dtype=np.int8
        )
        onehot = np.zeros((T, 8), dtype=np.float32)
        onehot[np.arange(T), np.clip(actions[:T], 0, 7)] = 1.0
        split = int(T * 0.6)
        if len(np.unique(changed[:split])) < 2 or len(np.unique(changed[split:])) < 2:
            continue  # degenerate game (always/never changes); AUC undefined

        feature_sets: dict[str, np.ndarray] = {"action_only": onehot}
        feature_sets["raw_grid"] = np.concatenate(
            [grids[:T].reshape(T, -1).astype(np.float32), onehot], axis=1
        )
        bio = np.stack(
            [projection.column_histogram(grids[t])[occupied, :].ravel() for t in range(T)]
        ).astype(np.float32)
        feature_sets["bioeye"] = np.concatenate([bio, onehot], axis=1)
        for condition in ("real", "null", "bypass"):
            path = STATES / condition / f"{game}.npz"
            if not path.exists():
                continue
            with np.load(path) as archive:
                states = np.asarray(archive["states"][:T], dtype=np.float32)
            feature_sets[condition] = np.concatenate([states, onehot], axis=1)

        for arm, X in feature_sets.items():
            mu, sd = X[:split].mean(0), np.maximum(X[:split].std(0), 1e-8)
            Xs = (X - mu) / sd
            model = LogisticRegression(
                C=1.0, solver="saga", max_iter=200, class_weight="balanced", tol=1e-3
            )
            model.fit(Xs[:split], changed[:split])
            score = model.decision_function(Xs[split:])
            results[arm][game] = float(roc_auc_score(changed[split:], score))
        print(
            f"{game}: "
            + " ".join(
                f"{a}={results[a].get(game, float('nan')):.3f}" for a in ARMS if game in results[a]
            ),
            flush=True,
        )

    summary = {}
    for arm in ARMS:
        vals = np.array(list(results[arm].values()))
        if vals.size:
            summary[arm] = {
                "median_auc": float(np.median(vals)),
                "mean_auc": float(vals.mean()),
                "games": int(vals.size),
                "games_above_0.6": int((vals > 0.6).sum()),
            }
    OUT.write_text(json.dumps({"per_game": results, "summary": summary}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
