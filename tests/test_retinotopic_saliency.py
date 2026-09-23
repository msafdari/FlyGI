"""The spatial readback must localize, and must read back the encoder's own map.

Grounding measurement (real graph, 16 trials): hex-map readback localizes a
known 6x6 change to 0.8 cells median where the deployed head sits at 23.5
(chance 37.2). These tests pin the mechanism on a synthetic map so the property
is regression-guarded without loading 24.5M edges.
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


def test_a_change_at_one_column_localizes_to_that_column(tmp_path: Path) -> None:
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
    assert RetinotopicSaliency(tmp_path, mode="surprise").mode == "surprise"
    with pytest.raises(RetinotopicSaliencyError, match="unknown saliency mode"):
        RetinotopicSaliency(tmp_path, mode="telepathy")
    with pytest.raises(RetinotopicSaliencyError, match="missing"):
        RetinotopicSaliency(tmp_path / "nowhere")
    saliency = RetinotopicSaliency(tmp_path)
    with pytest.raises(RetinotopicSaliencyError, match="shapes"):
        saliency.axis_scores(np.zeros(NODES), np.zeros(NODES - 1))
