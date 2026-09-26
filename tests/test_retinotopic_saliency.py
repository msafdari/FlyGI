"""Regression tests for declared legacy and ARC-correct spatial readback.

Historical measurement (real graph, 16 trials): this mapping localized a known
6x6 change to 0.8 cells under its own transposed coordinates. The 2026-09-26
audit invalidated that as ARC-coordinate evidence. These tests preserve the
legacy contract and prove that the corrected convention only swaps the two
already-computed score vectors, without loading 24.5M edges.
"""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

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


def _write_exact_golden_map(directory: Path) -> Path:
    """Use MaleCNS spans; occupied pair 12/31 maps to row 20, column 50."""

    np.savez(
        directory / "retinotopy.npz",
        node_indices=np.asarray([100, 101, 102, 103], dtype=np.int64),
        # Established from the runtime asset: hex1 spans 1..36 (35), while
        # hex2 spans 1..39 (38). Pair (12,31) is occupied by 26 mapped neurons.
        hex1=np.asarray([1, 12, 12, 36], dtype=np.int64),
        hex2=np.asarray([1, 31, 31, 39], dtype=np.int64),
        type=np.asarray(["L1"] * 4),
        superclass=np.asarray(["ol_intrinsic"] * 4),
    )
    return directory


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


def test_conventions_have_exact_occupied_off_diagonal_20_50_golden(tmp_path: Path) -> None:
    """ARC x owns hex2/column and y owns hex1/row; 20/50 must expose a swap."""

    runtime = _write_exact_golden_map(tmp_path)
    legacy = RetinotopicSaliency(runtime, coordinate_convention="legacy_hex1_x")
    corrected = RetinotopicSaliency(runtime, coordinate_convention="arc_x_hex2")
    before = np.zeros(NODES, dtype=np.float32)
    after = before.copy()
    after[101] = 1.0
    legacy_x, legacy_y = legacy.axis_scores(after, before)
    corrected_x, corrected_y = corrected.axis_scores(after, before)
    assert (int(np.argmax(legacy_x)), int(np.argmax(legacy_y))) == (20, 50)
    assert (int(np.argmax(corrected_x)), int(np.argmax(corrected_y))) == (50, 20)


def test_pooling_is_historical_unnormalized_sum_not_mean(tmp_path: Path) -> None:
    saliency = RetinotopicSaliency(_write_exact_golden_map(tmp_path))
    before = np.zeros(NODES, dtype=np.float32)
    after = before.copy()
    after[101] = 1.0
    after[102] = 2.0

    x, y = saliency.axis_scores(after, before)

    assert x[20] == np.float32(3.0)
    assert y[50] == np.float32(3.0)


def test_corrected_convention_only_swaps_byte_identical_score_arrays(tmp_path: Path) -> None:
    runtime = _write_map(tmp_path)
    legacy = RetinotopicSaliency(runtime, coordinate_convention="legacy_hex1_x")
    corrected = RetinotopicSaliency(runtime, coordinate_convention="arc_x_hex2")
    before = np.zeros(NODES, dtype=np.float32)
    after = np.random.default_rng(19).standard_normal(NODES).astype(np.float32)

    legacy_x, legacy_y = legacy.axis_scores(after, before)
    corrected_x, corrected_y = corrected.axis_scores(after, before)

    assert corrected_x.dtype == legacy_y.dtype == np.float32
    assert corrected_y.dtype == legacy_x.dtype == np.float32
    assert corrected_x.tobytes() == legacy_y.tobytes()
    assert corrected_y.tobytes() == legacy_x.tobytes()


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
    assert surprise.coordinate_convention == "legacy_hex1_x"
    description = surprise.describe()
    assert description["coordinate_convention"] == "legacy_hex1_x"
    assert description["historical_measurement"] == {
        "localization_cells": 0.8,
        "coordinate_convention": "legacy_hex1_x",
        "valid_for_arc_coordinates": False,
    }
    assert description["aggregation"].startswith("external_unnormalized")
    corrected = RetinotopicSaliency(tmp_path, coordinate_convention="arc_x_hex2")
    assert corrected.describe()["coordinate_convention"] == "arc_x_hex2"
    assert corrected.describe()["historical_measurement"]["coordinate_convention"] == (
        "legacy_hex1_x"
    )
    with pytest.raises(RetinotopicSaliencyError, match="unknown saliency mode"):
        RetinotopicSaliency(tmp_path, mode="telepathy")
    with pytest.raises(RetinotopicSaliencyError, match="unknown coordinate convention"):
        RetinotopicSaliency(tmp_path, coordinate_convention="hex3_everywhere")
    with pytest.raises(RetinotopicSaliencyError, match="missing"):
        RetinotopicSaliency(tmp_path / "nowhere")
    saliency = RetinotopicSaliency(tmp_path)
    with pytest.raises(RetinotopicSaliencyError, match="shapes"):
        saliency.axis_scores(np.zeros(NODES), np.zeros(NODES - 1))


@pytest.mark.parametrize(
    ("coordinate_source", "reclick_memory"),
    [
        ("retinotopic_surprise", "none"),
        ("readout_blocks", "surprise"),
    ],
)
def test_fly_tiebreaker_wires_convention_to_both_saliency_paths(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    coordinate_source: str,
    reclick_memory: str,
) -> None:
    """Deployment and re-click construction must agree with the standalone decoder."""

    from flygi.arc import factory
    from flygi.controller.fly_tiebreak import FlyTiebreaker
    from flygi.decoding import retinotopic_saliency as saliency_module

    calls: list[dict[str, str]] = []

    class _SaliencyStub:
        def __init__(self, runtime_dir: Path, **kwargs: str) -> None:
            assert runtime_dir == tmp_path
            calls.append(kwargs)

    class _NetworkStub:
        @staticmethod
        def initial_state() -> np.ndarray:
            return np.zeros(4, dtype=np.float32)

    policy = SimpleNamespace(
        _network=_NetworkStub(),
        _readout=SimpleNamespace(size=2),
        _action_map=object(),
        _coordinates=object(),
        _standardizer=None,
        internal_steps=4,
    )
    assembled = SimpleNamespace(
        policy=policy,
        bundle=SimpleNamespace(node_count=4, edge_count=3),
        projection=object(),
    )
    monkeypatch.setattr(factory, "build_connectome_policy", lambda *args, **kwargs: assembled)
    monkeypatch.setattr(saliency_module, "RetinotopicSaliency", _SaliencyStub)

    config = SimpleNamespace(
        graph=SimpleNamespace(output_dir=tmp_path),
        encoder=SimpleNamespace(efference_copy=None),
        decoder=SimpleNamespace(
            coordinate_source=coordinate_source,
            reclick_memory=reclick_memory,
            retinotopic_coordinate_convention="arc_x_hex2",
        ),
    )
    FlyTiebreaker(config, runtime_dir=tmp_path)

    assert calls == [
        {
            "mode": "surprise",
            "coordinate_convention": "arc_x_hex2",
        }
    ]
