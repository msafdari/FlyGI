"""Regression tests for the explicitly legacy-transposed spatial readback.

Historical measurement (real graph, 16 trials): this mapping localized a known
6x6 change to 0.8 cells under its own transposed coordinates. The 2026-09-26
audit invalidated that as ARC-coordinate evidence. These tests preserve the
legacy contract without loading 24.5M edges; a corrected convention needs
separate off-diagonal goldens.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from flygi.decoding.retinotopic_saliency import (
    GRID,
    RetinotopicSaliency,
    RetinotopicSaliencyError,
)

SPAN1, SPAN2 = 9, 11
NODES = 4000


def _write_map(directory: Path) -> Path:
    """A synthetic lattice: one neuron per column, node index = column order."""

    hex1, hex2, nodes = [], [], []
    node = 100  # offset so node index != position anywhere
    for a in range(1, SPAN1 + 1):
        for b in range(1, SPAN2 + 1):
            hex1.append(a)
            hex2.append(b)
            nodes.append(node)
            node += 1
    np.savez(
        directory / "retinotopy.npz",
        node_indices=np.asarray(nodes, dtype=np.int64),
        hex1=np.asarray(hex1, dtype=np.int64),
        hex2=np.asarray(hex2, dtype=np.int64),
        type=np.asarray(["L1"] * len(nodes)),
        superclass=np.asarray(["ol_intrinsic"] * len(nodes)),
    )
    return directory


def _column_node(a: int, b: int) -> int:
    return 100 + (a - 1) * SPAN2 + (b - 1)


def test_legacy_axis_ownership_is_regression_guarded(tmp_path: Path) -> None:
    saliency = RetinotopicSaliency(_write_map(tmp_path))
    before = np.zeros(NODES, dtype=np.float32)
    after = before.copy()
    a, b = 3, 8  # a known column
    after[_column_node(a, b)] = 1.0
    x, y = saliency.axis_scores(after, before)
    expected_row = round((a - 1) / (SPAN1 - 1) * (GRID - 1))
    expected_col = round((b - 1) / (SPAN2 - 1) * (GRID - 1))
    assert int(np.argmax(x)) == expected_row
    assert int(np.argmax(y)) == expected_col


def test_no_change_means_no_preference(tmp_path: Path) -> None:
    saliency = RetinotopicSaliency(_write_map(tmp_path))
    state = np.random.default_rng(0).standard_normal(NODES).astype(np.float32)
    x, y = saliency.axis_scores(state, state)
    assert float(x.sum()) == 0.0 and float(y.sum()) == 0.0


def test_magnitude_weights_the_estimate(tmp_path: Path) -> None:
    """A big change must outvote a small one, not merely tie with it."""

    saliency = RetinotopicSaliency(_write_map(tmp_path))
    before = np.zeros(NODES, dtype=np.float32)
    after = before.copy()
    after[_column_node(2, 2)] = 0.1
    after[_column_node(8, 10)] = 1.0
    x, _ = saliency.axis_scores(after, before)
    big_row = round((8 - 1) / (SPAN1 - 1) * (GRID - 1))
    assert int(np.argmax(x)) == big_row


def test_modes_and_errors(tmp_path: Path) -> None:
    _write_map(tmp_path)
    surprise = RetinotopicSaliency(tmp_path, mode="surprise")
    assert surprise.mode == "surprise"
    description = surprise.describe()
    assert description["measurement_coordinate_convention"] == "legacy_hex1_x_transposed"
    assert description["measurement_valid_for_arc_coordinates"] is False
    with pytest.raises(RetinotopicSaliencyError, match="unknown saliency mode"):
        RetinotopicSaliency(tmp_path, mode="telepathy")
    with pytest.raises(RetinotopicSaliencyError, match="missing"):
        RetinotopicSaliency(tmp_path / "nowhere")
    saliency = RetinotopicSaliency(tmp_path)
    with pytest.raises(RetinotopicSaliencyError, match="shapes"):
        saliency.axis_scores(np.zeros(NODES), np.zeros(NODES - 1))
