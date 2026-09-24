"""H-CONSEQUENCE-COUPLING: the online click head and its trivial alternatives.

Per AGENTS.md, correctness tests are not comparison tests: the planted-rule
world below is the comparison. In that world clicks on colour-7 cells change
the frame and everything else is a no-op; the generalization test scores
predictions at coordinates the head has NEVER seen, where rote memory knows
nothing by construction.
"""

from __future__ import annotations

import numpy as np
import pytest

from flygi.controller.click_head import OnlineClickHead

GRID = 64


def _planted_world(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    grid = rng.integers(0, 4, size=(GRID, GRID), dtype=np.int8)
    targets = rng.integers(0, GRID, size=(40, 2))
    for x, y in targets:
        grid[x, y] = 7  # clickable marker colour
    return grid


def _identity_columns() -> tuple[np.ndarray, int]:
    """A synthetic one-cell-per-column map for tests without the runtime dir."""

    return np.arange(GRID * GRID, dtype=np.int64), GRID * GRID


def _train(head: OnlineClickHead, grid: np.ndarray, rng: np.random.Generator, n: int = 300):
    # Realistic click distribution: the controller's candidates are
    # component-grounded, so targets are hit far more often than uniform
    # cell sampling would (~15% here vs 1% uniform; ft09 measured 5.8%).
    targets = np.argwhere(grid == 7)
    for _ in range(n):
        if rng.random() < 0.15:
            x, y = (int(v) for v in targets[rng.integers(0, len(targets))])
        else:
            x, y = int(rng.integers(0, GRID)), int(rng.integers(0, GRID))
        head.update(grid, x, y, changed=bool(grid[x, y] == 7))


def _auc_fresh_coordinates(head: OnlineClickHead, grid: np.ndarray, seed: int) -> float:
    rng = np.random.default_rng(seed)
    scores, labels = [], []
    for _ in range(400):
        x, y = int(rng.integers(0, GRID)), int(rng.integers(0, GRID))
        scores.append(head.probability(grid, x, y))
        labels.append(bool(grid[x, y] == 7))
    scores = np.asarray(scores)
    labels = np.asarray(labels)
    if labels.all() or not labels.any():
        pytest.skip("degenerate sample")
    positives = scores[labels]
    negatives = scores[~labels]
    return float((positives[:, None] > negatives[None, :]).mean())


@pytest.mark.parametrize("mode", ["pixel_patch", "retinotopic"])
def test_head_learns_planted_rule_on_fresh_coordinates(mode: str) -> None:
    grid = _planted_world(1)
    columns, count = _identity_columns()
    head = OnlineClickHead(mode, cell_columns=columns, column_count=count)
    _train(head, grid, np.random.default_rng(2))
    auc = _auc_fresh_coordinates(head, grid, seed=3)
    assert auc > 0.9, f"{mode} failed to learn the planted rule: AUC {auc:.3f}"


def test_head_beats_rote_on_fresh_coordinates() -> None:
    """The comparison test: rote memory cannot generalize to unseen cells."""

    grid = _planted_world(1)
    columns, count = _identity_columns()
    learned = OnlineClickHead("retinotopic", cell_columns=columns, column_count=count)
    rote = OnlineClickHead("rote")
    rng_a, rng_b = np.random.default_rng(2), np.random.default_rng(2)
    _train(learned, grid, rng_a)
    _train(rote, grid, rng_b)
    auc_learned = _auc_fresh_coordinates(learned, grid, seed=3)
    auc_rote = _auc_fresh_coordinates(rote, grid, seed=3)
    assert auc_learned > auc_rote + 0.2, (
        f"learned head ({auc_learned:.3f}) must clearly beat rote memory "
        f"({auc_rote:.3f}) at coordinates neither has clicked"
    )


def test_permuted_map_destroys_locality_signal() -> None:
    """The load-bearing control behaves as designed: with a scrambled
    cell->column map each patch feature aggregates arbitrary far-away cells,
    so the planted LOCAL rule becomes much harder to learn."""

    grid = _planted_world(1)
    columns, count = _identity_columns()
    real = OnlineClickHead("retinotopic", cell_columns=columns, column_count=count)
    # Coarser, fly-realistic granularity for the permuted control: group
    # cells 4-per-column so permutation actually mixes content.
    coarse = (np.arange(GRID * GRID, dtype=np.int64) // 4, GRID * GRID // 4)
    permuted = OnlineClickHead(
        "retinotopic_permuted", cell_columns=coarse[0], column_count=coarse[1]
    )
    _train(real, grid, np.random.default_rng(2))
    _train(permuted, grid, np.random.default_rng(2))
    auc_real = _auc_fresh_coordinates(real, grid, seed=3)
    auc_permuted = _auc_fresh_coordinates(permuted, grid, seed=3)
    assert auc_real > auc_permuted + 0.1


def test_untrained_head_is_inert() -> None:
    grid = _planted_world(1)
    columns, count = _identity_columns()
    head = OnlineClickHead("retinotopic", cell_columns=columns, column_count=count)
    assert head.probability(grid, 5, 5) == pytest.approx(0.5)
    assert head.bonus(grid, 5, 5) == pytest.approx(0.0)


def test_head_is_deterministic() -> None:
    grid = _planted_world(1)
    columns, count = _identity_columns()
    runs = []
    for _ in range(2):
        head = OnlineClickHead("retinotopic", cell_columns=columns, column_count=count)
        _train(head, grid, np.random.default_rng(9))
        runs.append([head.probability(grid, x, y) for x, y in [(1, 1), (30, 40), (63, 63)]])
    assert runs[0] == runs[1]


def test_boundary_coordinates_do_not_crash() -> None:
    grid = _planted_world(1)
    columns, count = _identity_columns()
    for mode in ("retinotopic", "pixel_patch"):
        head = OnlineClickHead(mode, cell_columns=columns, column_count=count)
        for x, y in [(0, 0), (0, 63), (63, 0), (63, 63)]:
            head.update(grid, x, y, changed=True)
            assert 0.0 <= head.probability(grid, x, y) <= 1.0


def test_boost_only_never_demotes() -> None:
    """negative_scale=0: the head can promote predicted-changers but its
    bonus is never negative, so an untried click keeps its exploration rank."""

    grid = _planted_world(1)
    columns, count = _identity_columns()
    head = OnlineClickHead(
        "retinotopic", cell_columns=columns, column_count=count, negative_scale=0.0
    )
    _train(head, grid, np.random.default_rng(2))
    rng = np.random.default_rng(4)
    bonuses = [
        head.bonus(grid, int(rng.integers(0, GRID)), int(rng.integers(0, GRID))) for _ in range(200)
    ]
    assert min(bonuses) >= 0.0
    assert max(bonuses) > 0.1  # still promotes confident positives
