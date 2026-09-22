"""Paired comparison of two conditions over matched ARC rows.

Every FlyGI comparison so far has been computed ad hoc in a throwaway script,
which is fine for looking and wrong for reporting. This module makes the
declared analysis reusable and tested.

Three things it refuses to do quietly, because each has already been a live risk
in this project:

**Seeds are not independent replicates when the policy is deterministic.** The
frozen agent produced byte-identical traces across all five seeds in all 25
games, so a test over 125 rows would have claimed five times the evidence it
had. Uncertainty is therefore clustered on the game, never on the row, and a
paired comparison reports how many distinct traces it actually saw.

**Action counts for uncompleted levels are right-censored, not missing.** A row
that never completed a level did not take "no actions"; it took at least the
whole budget and then stopped. Averaging completion times over completers only
is a selection-biased estimate, and it flatters whichever condition completes
the rarest, hardest games. `censored_summary` reports the completion rate and a
restricted mean with the censoring made explicit instead.

**A near-degenerate outcome cannot support a confident interval.** With one or
two nonzero rows in 25 games, the bootstrap is reported together with the number
of nonzero clusters so the reader can see the effect rests on one game.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray


class PairedAnalysisError(ValueError):
    """Raised when two conditions cannot be compared as declared."""


@dataclass(frozen=True)
class PairedResult:
    """One paired comparison, with its own limitations attached."""

    metric: str
    pairs: int
    clusters: int
    mean_difference: float
    median_difference: float
    bootstrap_low: float
    bootstrap_high: float
    permutation_p: float
    nonzero_clusters: int
    distinct_traces_a: int | None
    distinct_traces_b: int | None
    warnings: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "pairs": self.pairs,
            "clusters": self.clusters,
            "mean_difference": self.mean_difference,
            "median_difference": self.median_difference,
            "bootstrap_95_ci": [self.bootstrap_low, self.bootstrap_high],
            "permutation_p": self.permutation_p,
            "nonzero_clusters": self.nonzero_clusters,
            "distinct_traces_a": self.distinct_traces_a,
            "distinct_traces_b": self.distinct_traces_b,
            "warnings": list(self.warnings),
            "uncertainty_clustered_on": "game",
        }


def _row_key(row: Mapping[str, Any]) -> tuple[int, str]:
    if "seed" not in row or "game_id" not in row:
        raise PairedAnalysisError("rows must carry 'seed' and 'game_id'")
    return int(row["seed"]), str(row["game_id"])


def extract_metric(row: Mapping[str, Any], metric: str) -> float:
    """Read one declared metric from a result row."""

    official = row.get("official") or {}
    if metric == "score":
        return float(official.get("score") or 0.0)
    if metric == "levels_completed":
        return float(official.get("levels_completed") or 0)
    if metric == "unique_observations":
        return float((row.get("observations") or {}).get("unique") or 0)
    if metric == "action_entropy_bits":
        return float(row.get("action_entropy_bits") or 0.0)
    if metric == "actions_completed":
        return float(row.get("actions_completed") or 0)
    raise PairedAnalysisError(f"unknown metric: {metric!r}")


def match_rows(
    left: Sequence[Mapping[str, Any]],
    right: Sequence[Mapping[str, Any]],
) -> list[tuple[Mapping[str, Any], Mapping[str, Any]]]:
    """Pair rows on ``(seed, game_id)``, refusing silent partial overlap."""

    lookup = {}
    for row in right:
        key = _row_key(row)
        if key in lookup:
            raise PairedAnalysisError(f"duplicate row for {key} in the second condition")
        lookup[key] = row

    pairs = []
    missing = []
    for row in left:
        key = _row_key(row)
        partner = lookup.get(key)
        if partner is None:
            missing.append(key)
            continue
        pairs.append((row, partner))
    if missing:
        raise PairedAnalysisError(
            f"{len(missing)} rows have no match in the second condition, e.g. {missing[:3]}; "
            "a paired comparison needs identical (seed, game) coverage"
        )
    if not pairs:
        raise PairedAnalysisError("no matched rows to compare")
    return pairs


def _cluster_bootstrap(
    differences: NDArray[np.float64],
    clusters: NDArray[np.int64],
    *,
    resamples: int,
    seed: int,
) -> tuple[float, float]:
    """Resample whole games, not rows, so within-game correlation is respected."""

    unique = np.unique(clusters)
    generator = np.random.default_rng(seed)
    means = np.empty(resamples, dtype=np.float64)
    grouped = [differences[clusters == cluster] for cluster in unique]
    for index in range(resamples):
        picked = generator.integers(0, len(grouped), size=len(grouped))
        means[index] = np.concatenate([grouped[i] for i in picked]).mean()
    return float(np.percentile(means, 2.5)), float(np.percentile(means, 97.5))


def _permutation_p(
    differences: NDArray[np.float64],
    clusters: NDArray[np.int64],
    *,
    resamples: int,
    seed: int,
) -> float:
    """Exchange condition labels within each game, which is what pairing allows."""

    unique = np.unique(clusters)
    generator = np.random.default_rng(seed)
    observed = abs(float(differences.mean()))
    masks = [clusters == cluster for cluster in unique]
    at_least_as_extreme = 0
    for _ in range(resamples):
        flipped = differences.copy()
        signs = generator.integers(0, 2, size=len(masks)) * 2 - 1
        for mask, sign in zip(masks, signs, strict=True):
            flipped[mask] *= sign
        if abs(float(flipped.mean())) >= observed - 1e-15:
            at_least_as_extreme += 1
    # Add-one correction: a permutation test can never report p = 0.
    return float((at_least_as_extreme + 1) / (resamples + 1))


def compare(
    left: Sequence[Mapping[str, Any]],
    right: Sequence[Mapping[str, Any]],
    *,
    metric: str = "score",
    resamples: int = 10_000,
    seed: int = 20260922,
) -> PairedResult:
    """Compare two conditions on matched rows, clustering uncertainty on games."""

    pairs = match_rows(left, right)
    differences = np.asarray(
        [extract_metric(a, metric) - extract_metric(b, metric) for a, b in pairs],
        dtype=np.float64,
    )
    games = sorted({str(a["game_id"]) for a, _ in pairs})
    game_index = {game: i for i, game in enumerate(games)}
    clusters = np.asarray([game_index[str(a["game_id"])] for a, _ in pairs], dtype=np.int64)

    nonzero_clusters = int(
        sum(1 for cluster in np.unique(clusters) if np.any(differences[clusters == cluster] != 0.0))
    )

    def distinct_traces(rows: Sequence[Mapping[str, Any]]) -> int | None:
        hashes = [r.get("replay_trace_sha256") for r in rows]
        return len({h for h in hashes if h}) if any(hashes) else None

    warnings: list[str] = []
    if nonzero_clusters <= 2:
        warnings.append(
            f"only {nonzero_clusters} game(s) show any difference; the estimate rests on "
            "those games and the interval should not be read as a general effect"
        )
    seeds_per_game = len(pairs) / max(len(games), 1)
    left_traces = distinct_traces([a for a, _ in pairs])
    if seeds_per_game > 1 and left_traces is not None and left_traces <= len(games):
        warnings.append(
            "the first condition produced no more distinct traces than games, so its "
            "seeds are not independent replicates and the effective sample size is the "
            "number of games"
        )
    if len(games) < 10:
        warnings.append(f"only {len(games)} clusters; bootstrap intervals will be coarse")

    low, high = _cluster_bootstrap(differences, clusters, resamples=resamples, seed=seed)
    return PairedResult(
        metric=metric,
        pairs=len(pairs),
        clusters=len(games),
        mean_difference=float(differences.mean()),
        median_difference=float(np.median(differences)),
        bootstrap_low=low,
        bootstrap_high=high,
        permutation_p=_permutation_p(differences, clusters, resamples=resamples, seed=seed + 1),
        nonzero_clusters=nonzero_clusters,
        distinct_traces_a=left_traces,
        distinct_traces_b=distinct_traces([b for _, b in pairs]),
        warnings=tuple(warnings),
    )


def level_completion_actions(row: Mapping[str, Any]) -> list[int]:
    """Actions taken to reach each level completion, read from the trace.

    The evaluator stores ``actions_completed`` as the total length of the row,
    which is the action budget for anything that did not finish, so it cannot
    answer "how fast". The per-step trace does: every entry carries
    ``levels_completed_before`` and ``levels_completed_after``, so a completion
    is any step where the count rises, and the action index is the step number
    plus one.

    This works retroactively on every artifact already recorded, so no run has
    to be repeated to obtain it.
    """

    completions: list[int] = []
    for entry in row.get("trace") or []:
        before = int(entry.get("levels_completed_before") or 0)
        after = int(entry.get("levels_completed_after") or 0)
        if after > before:
            completions.extend([int(entry["step"]) + 1] * (after - before))
    return completions


def censored_summary(
    rows: Sequence[Mapping[str, Any]],
    *,
    budget: int,
) -> dict[str, Any]:
    """Summarize actions-to-completion honestly under right-censoring.

    A row that completed no level is censored at the action budget: it did not
    take zero actions, and it did not take "no time". Averaging only completers
    is selection-biased and flatters whichever condition completes the rarest,
    hardest games. The restricted mean substitutes the budget for censored rows,
    which is a declared lower bound rather than an invented value.
    """

    if budget <= 0:
        raise PairedAnalysisError("budget must be positive")
    completed, censored, untraced = [], 0, 0
    for row in rows:
        official = row.get("official") or {}
        if official.get("levels_completed"):
            actions = level_completion_actions(row)
            if actions:
                # Time to the FIRST completion; later levels are a separate question.
                completed.append(float(min(actions)))
            else:
                # The row completed but carries no trace, so its speed is unknown.
                # Counting it as the budget is a declared upper bound, not a guess.
                completed.append(float(budget))
                untraced += 1
        else:
            censored += 1
    total = len(completed) + censored
    if total == 0:
        raise PairedAnalysisError("no rows to summarize")
    restricted = (sum(completed) + censored * budget) / total
    return {
        "rows": total,
        "completed": len(completed),
        "censored": censored,
        "completion_rate": len(completed) / total,
        "completions_without_a_trace": untraced,
        "restricted_mean_actions": restricted,
        "completer_only_mean_actions": (sum(completed) / len(completed) if completed else None),
        "censoring_note": (
            "completer-only mean is selection-biased; the restricted mean substitutes "
            "the action budget for censored rows and is a lower bound"
        ),
    }
