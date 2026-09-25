"""Defragmentation state tags: similarity math and near-duplicate behavior."""

from __future__ import annotations

import numpy as np

from flygi.controller.state_tags import RetinoTagRegistry

RUNTIME = "data/processed/male-cns-v1.0/literal-rate-signed-modulators"


def _grid(seed: int) -> np.ndarray:
    return np.random.default_rng(seed).integers(0, 8, size=(64, 64), dtype=np.int8)


def test_near_duplicates_merge_distinct_states_do_not() -> None:
    registry = RetinoTagRegistry(RUNTIME, threshold=0.9)
    base = _grid(1)
    near = base.copy()
    near[10, 10] = (near[10, 10] + 1) % 8  # one-cell flicker
    far = _grid(2)
    registry.observe(registry.tag(base))
    assert registry.seen_similar(registry.tag(near)), "one-cell variant must read familiar"
    assert not registry.seen_similar(registry.tag(far)), "distinct grid must read novel"


def test_permuted_control_differs_from_real() -> None:
    real = RetinoTagRegistry(RUNTIME, threshold=0.9)
    permuted = RetinoTagRegistry(RUNTIME, threshold=0.9, permute_retinotopy=True)
    grid = _grid(3)
    assert (real.tag(grid) != permuted.tag(grid)).any()
    assert "permuted" in permuted.describe()["kind"]


def test_registry_is_deterministic() -> None:
    a = RetinoTagRegistry(RUNTIME, threshold=0.9)
    b = RetinoTagRegistry(RUNTIME, threshold=0.9)
    grid = _grid(4)
    assert (a.tag(grid) == b.tag(grid)).all()
