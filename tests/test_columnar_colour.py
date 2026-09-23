"""The bio-eye encoder: retinotopy preserved, colours categorical, control valid.

These encode the three live checks that gated the encoder's first run, plus the
properties of its falsification control, against a small synthetic column map so
they run in milliseconds rather than loading 24.5M edges.
"""

from __future__ import annotations

import numpy as np
import pytest

from flygi.encoding.retinotopic import (
    GRID_SIZE,
    ColumnarColourProjection,
    RetinotopicOptions,
    RetinotopyError,
)

TYPES = ["C2", "L1", "L2", "Mi1", "Tm4"]  # 5 channels; 16 colours -> collisions


def _columns(span1: int = 8, span2: int = 9, node_count: int = 4000) -> dict:
    """A synthetic lattice: every column carries one neuron of every type."""

    hex1, hex2, types, nodes = [], [], [], []
    node = 0
    for a in range(1, span1 + 1):
        for b in range(1, span2 + 1):
            for name in TYPES:
                hex1.append(a)
                hex2.append(b)
                types.append(name)
                nodes.append(node)
                node += 1
    return {
        "node_indices": np.asarray(nodes, dtype=np.int64),
        "hex1": np.asarray(hex1, dtype=np.int64),
        "hex2": np.asarray(hex2, dtype=np.int64),
        "type": np.asarray(types),
    }


class _Frame:
    def __init__(self, grid: np.ndarray) -> None:
        self.grid = grid


NODES = 4000


def _drive(projection: ColumnarColourProjection, grid: np.ndarray) -> np.ndarray:
    return projection.drive_features(_Frame(grid))


def test_neighbouring_cells_drive_nearer_columns_than_distant_cells() -> None:
    projection = ColumnarColourProjection(_columns(), NODES)

    def column_of(row: int, col: int) -> int:
        grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int8)
        grid[row, col] = 1
        histogram = projection.column_histogram(grid)
        return int(np.argmax(histogram[:, 1 % len(TYPES)]))

    near = abs(column_of(30, 30) - column_of(30, 33))
    far = abs(column_of(30, 30) - column_of(30, 62))
    assert near < far, "retinotopy is not preserved; the encoder has no reason to exist"


def test_distinct_colours_drive_distinct_channels() -> None:
    projection = ColumnarColourProjection(_columns(), NODES)
    a = _drive(projection, np.full((GRID_SIZE, GRID_SIZE), 1, dtype=np.int8))
    b = _drive(projection, np.full((GRID_SIZE, GRID_SIZE), 2, dtype=np.int8))
    assert not np.array_equal(a, b), "colours collapsed; this is the old encoder's defect"


def test_colours_are_histograms_never_averages() -> None:
    """The mean of colour 1 and colour 3 must NOT look like colour 2."""

    projection = ColumnarColourProjection(_columns(), NODES)
    mixed = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int8)
    mixed[:, ::2] = 1
    mixed[:, 1::2] = 3
    solid2 = np.full((GRID_SIZE, GRID_SIZE), 2, dtype=np.int8)
    assert not np.allclose(_drive(projection, mixed), _drive(projection, solid2)), (
        "a half-and-half mixture of colours 1 and 3 produced colour 2's drive; "
        "categorical colour is being averaged"
    )


def test_colliding_colours_share_a_channel_by_the_declared_rule() -> None:
    projection = ColumnarColourProjection(_columns(), NODES)
    channels = len(TYPES)
    described = projection.describe()
    assert described["channels"] == channels
    a = _drive(projection, np.full((GRID_SIZE, GRID_SIZE), 0, dtype=np.int8))
    b = _drive(projection, np.full((GRID_SIZE, GRID_SIZE), channels, dtype=np.int8))
    assert np.array_equal(a, b), "colours c and c+channels must collide, by declaration"


def test_out_of_range_colour_is_rejected() -> None:
    projection = ColumnarColourProjection(_columns(), NODES)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int16)
    grid[0, 0] = 16
    with pytest.raises(RetinotopyError):
        projection.column_histogram(grid)


# --- the permutation control -------------------------------------------------


def test_the_permutation_control_differs_and_is_deterministic() -> None:
    plain = ColumnarColourProjection(_columns(), NODES)
    seeded = RetinotopicOptions(colour_permutation_seed=7)
    perm_a = ColumnarColourProjection(_columns(), NODES, options=seeded)
    perm_b = ColumnarColourProjection(_columns(), NODES, options=seeded)
    grid = np.arange(GRID_SIZE * GRID_SIZE, dtype=np.int64).reshape(GRID_SIZE, GRID_SIZE) % 16
    grid = grid.astype(np.int8)
    assert not np.array_equal(_drive(plain, grid), _drive(perm_a, grid)), (
        "the control equals the declared rule; it can falsify nothing"
    )
    assert np.array_equal(_drive(perm_a, grid), _drive(perm_b, grid)), (
        "the control is not reproducible across builds"
    )


def test_the_permutation_control_keeps_the_collision_structure() -> None:
    projection = ColumnarColourProjection(
        _columns(), NODES, options=RetinotopicOptions(colour_permutation_seed=7)
    )
    channels = len(TYPES)
    a = _drive(projection, np.full((GRID_SIZE, GRID_SIZE), 0, dtype=np.int8))
    b = _drive(projection, np.full((GRID_SIZE, GRID_SIZE), channels, dtype=np.int8))
    assert np.array_equal(a, b), "the permutation broke the matched collision structure"


def test_an_identity_permutation_is_refused() -> None:
    """A control that changes nothing must fail loudly, not run quietly."""

    identity_seed = None
    for seed in range(3000):
        candidate = np.random.default_rng(seed).permutation(len(TYPES))
        if np.array_equal(candidate, np.arange(len(TYPES))):
            identity_seed = seed
            break
    if identity_seed is None:
        pytest.skip("no identity-producing seed found in the search range")
    with pytest.raises(RetinotopyError, match="controls nothing"):
        ColumnarColourProjection(
            _columns(), NODES, options=RetinotopicOptions(colour_permutation_seed=identity_seed)
        )


def test_describe_records_the_full_colour_map() -> None:
    projection = ColumnarColourProjection(
        _columns(), NODES, options=RetinotopicOptions(colour_permutation_seed=7)
    )
    described = projection.describe()
    assert described["colour_permutation_seed"] == 7
    assert "PERMUTED" in described["colour_to_channel"]
    assert set(described["colour_channel_map"]) == {str(c) for c in range(16)}
