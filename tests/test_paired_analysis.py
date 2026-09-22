"""Paired comparison, with the failure modes this project has actually hit."""

from __future__ import annotations

import pytest

from flygi.evaluation import (
    PairedAnalysisError,
    censored_summary,
    compare,
    extract_metric,
    match_rows,
)


def _row(seed, game, score=0.0, levels=0, unique=100, actions=600, trace=None):
    return {
        "seed": seed,
        "game_id": game,
        "official": {"score": score, "levels_completed": levels},
        "observations": {"unique": unique},
        "action_entropy_bits": 1.5,
        "actions_completed": actions,
        "replay_trace_sha256": trace or f"{game}-{seed}",
    }


def _matrix(scores, seeds=(0, 1, 2), games=("g1", "g2", "g3", "g4", "g5")):
    return [_row(seed, game, score=scores(seed, game)) for game in games for seed in seeds]


def test_identical_conditions_show_no_difference() -> None:
    rows = _matrix(lambda s, g: 1.0)
    result = compare(rows, list(rows), metric="score")
    assert result.mean_difference == 0.0
    assert result.permutation_p > 0.5
    assert result.nonzero_clusters == 0


def test_a_broad_consistent_difference_is_detected() -> None:
    left = _matrix(lambda s, g: 2.0)
    right = _matrix(lambda s, g: 1.0)
    result = compare(left, right, metric="score", resamples=2000)

    assert result.mean_difference == pytest.approx(1.0)
    assert result.bootstrap_low > 0.0
    assert result.permutation_p < 0.1
    assert result.nonzero_clusters == 5


def test_an_effect_resting_on_one_game_is_flagged() -> None:
    """The project's actual situation: all signal from a single game."""

    left = _matrix(lambda s, g: 4.76 if g == "g1" else 0.0)
    right = _matrix(lambda s, g: 0.0)
    result = compare(left, right, metric="score", resamples=2000)

    assert result.mean_difference > 0
    assert result.nonzero_clusters == 1
    assert any("rests on" in w for w in result.warnings)
    # A single cluster cannot be resolved from zero by a cluster bootstrap.
    assert result.bootstrap_low == 0.0


def test_deterministic_seeds_are_flagged_as_fake_replicates() -> None:
    """The frozen agent gave byte-identical traces across all five seeds."""

    games = ("g1", "g2", "g3")
    left = [
        _row(seed, game, score=1.0, trace=f"{game}-same") for game in games for seed in (0, 1, 2)
    ]
    right = [_row(seed, game, score=0.0) for game in games for seed in (0, 1, 2)]
    result = compare(left, right, metric="score", resamples=1000)

    assert result.distinct_traces_a == 3
    assert result.pairs == 9
    assert any("not independent replicates" in w for w in result.warnings)


def test_uncertainty_is_clustered_on_games_not_rows() -> None:
    """Adding seeds of the same game must not shrink the interval like new games."""

    few = compare(
        _matrix(lambda s, g: 1.0 if g == "g1" else 0.0, seeds=(0,)),
        _matrix(lambda s, g: 0.0, seeds=(0,)),
        metric="score",
        resamples=2000,
    )
    many = compare(
        _matrix(lambda s, g: 1.0 if g == "g1" else 0.0, seeds=tuple(range(8))),
        _matrix(lambda s, g: 0.0, seeds=tuple(range(8))),
        metric="score",
        resamples=2000,
    )
    assert few.clusters == many.clusters == 5
    assert many.pairs == 40
    # Eight times the rows, same five games: the interval must not collapse.
    assert many.bootstrap_high == pytest.approx(few.bootstrap_high, rel=0.25)


def test_matching_refuses_partial_overlap() -> None:
    left = _matrix(lambda s, g: 1.0)
    right = [r for r in _matrix(lambda s, g: 1.0) if r["game_id"] != "g3"]
    with pytest.raises(PairedAnalysisError, match="no match"):
        compare(left, right)


def test_matching_refuses_duplicate_rows() -> None:
    rows = _matrix(lambda s, g: 1.0)
    with pytest.raises(PairedAnalysisError, match="duplicate"):
        match_rows(rows, [*rows, rows[0]])


def test_permutation_p_is_never_zero() -> None:
    left = _matrix(lambda s, g: 100.0)
    right = _matrix(lambda s, g: 0.0)
    result = compare(left, right, metric="score", resamples=500)
    assert result.permutation_p > 0.0


def test_metrics_read_the_declared_fields() -> None:
    row = _row(0, "g1", score=3.0, levels=2, unique=42, actions=17)
    assert extract_metric(row, "score") == 3.0
    assert extract_metric(row, "levels_completed") == 2.0
    assert extract_metric(row, "unique_observations") == 42.0
    assert extract_metric(row, "actions_completed") == 17.0
    with pytest.raises(PairedAnalysisError):
        extract_metric(row, "nonsense")


# --- right-censoring --------------------------------------------------------


def test_censored_summary_does_not_average_completers_only() -> None:
    """A row that never completed did not take zero actions."""

    rows = [
        _traced_row(0, "g1", completion_steps={49}),
        _traced_row(0, "g2", completion_steps=set()),
        _traced_row(0, "g3", completion_steps=set()),
        _traced_row(0, "g4", completion_steps=set()),
    ]
    summary = censored_summary(rows, budget=600)

    assert summary["completed"] == 1
    assert summary["censored"] == 3
    assert summary["completion_rate"] == 0.25
    assert summary["completer_only_mean_actions"] == 50.0
    # The restricted mean must reflect the three runs that never finished.
    assert summary["restricted_mean_actions"] == pytest.approx((50 + 3 * 600) / 4)
    assert summary["restricted_mean_actions"] > summary["completer_only_mean_actions"]


def test_censoring_bias_favours_the_rarest_completer() -> None:
    """The exact trap: completing one easy game fast looks better than completing many."""

    lucky = [_traced_row(0, "g1", completion_steps={9})] + [
        _traced_row(0, f"g{i}", completion_steps=set()) for i in range(2, 6)
    ]
    steady = [_traced_row(0, f"g{i}", completion_steps={299}) for i in range(1, 5)] + [
        _traced_row(0, "g5", completion_steps=set())
    ]

    lucky_summary = censored_summary(lucky, budget=600)
    steady_summary = censored_summary(steady, budget=600)

    # Completer-only mean makes the worse agent look five times faster.
    assert (
        lucky_summary["completer_only_mean_actions"] < steady_summary["completer_only_mean_actions"]
    )
    # The restricted mean and the completion rate both prefer the better agent.
    assert steady_summary["restricted_mean_actions"] < lucky_summary["restricted_mean_actions"]
    assert steady_summary["completion_rate"] > lucky_summary["completion_rate"]


def test_censored_summary_validates_its_inputs() -> None:
    with pytest.raises(PairedAnalysisError):
        censored_summary([_row(0, "g1")], budget=0)
    with pytest.raises(PairedAnalysisError):
        censored_summary([], budget=600)


# --- actions to completion, recovered from the trace ------------------------


def _traced_row(seed, game, completion_steps, total=600):
    trace, levels = [], 0
    for step in range(total):
        before = levels
        if step in completion_steps:
            levels += 1
        trace.append(
            {"step": step, "levels_completed_before": before, "levels_completed_after": levels}
        )
    row = _row(seed, game, levels=levels, actions=total)
    row["trace"] = trace
    return row


def test_completion_actions_are_recovered_from_the_trace() -> None:
    from flygi.evaluation import level_completion_actions

    row = _traced_row(0, "g1", completion_steps={8, 120})
    assert level_completion_actions(row) == [9, 121]
    assert level_completion_actions(_traced_row(0, "g2", completion_steps=set())) == []


def test_censored_summary_uses_real_completion_speed() -> None:
    """Previously this reported the budget for every row and meant nothing."""

    rows = [
        _traced_row(0, "g1", completion_steps={8}),
        _traced_row(0, "g2", completion_steps={299}),
        _traced_row(0, "g3", completion_steps=set()),
        _traced_row(0, "g4", completion_steps=set()),
    ]
    summary = censored_summary(rows, budget=600)

    assert summary["completed"] == 2
    assert summary["completions_without_a_trace"] == 0
    assert summary["completer_only_mean_actions"] == pytest.approx((9 + 300) / 2)
    assert summary["restricted_mean_actions"] == pytest.approx((9 + 300 + 600 + 600) / 4)


def test_a_completion_without_a_trace_is_bounded_not_guessed() -> None:
    row = _row(0, "g1", levels=1, actions=600)  # no trace attached
    summary = censored_summary([row], budget=600)
    assert summary["completions_without_a_trace"] == 1
    assert summary["completer_only_mean_actions"] == 600.0
