"""Sparse weight transforms, transmitter signs, and stable normalization."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from flygi.connectome.normalize import (
    incoming_l1_normalize,
    transform_weights,
    transmitter_signs,
)


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("raw", [0.0, 3.0, 8.0]),
        ("log1p", np.log1p([0.0, 3.0, 8.0])),
        ("sqrt", np.sqrt([0.0, 3.0, 8.0])),
        ("binary", [0.0, 1.0, 1.0]),
    ],
)
def test_weight_transforms(mode: str, expected: list[float] | np.ndarray) -> None:
    transformed = transform_weights(np.asarray([0, 3, 8], dtype=np.int64), mode)  # type: ignore[arg-type]

    assert transformed.dtype == np.float32
    np.testing.assert_allclose(transformed, expected, rtol=1e-6)


def test_incoming_l1_normalization_stays_sparse() -> None:
    matrix = sparse.csr_matrix(np.asarray([[3.0, -4.0], [0.0, 2.0]], dtype=np.float32))

    normalized = incoming_l1_normalize(matrix, epsilon=1e-8)

    assert sparse.isspmatrix_csr(normalized)
    assert normalized.nnz == 3
    np.testing.assert_allclose(normalized.toarray(), [[3 / 7, -4 / 7], [0, 1]], rtol=1e-6)


def test_transmitter_heuristic_keeps_modulators_and_unknowns_explicit() -> None:
    signs, counts = transmitter_signs(
        ["acetylcholine", "GABA", "dopamine", None],
        modulator_treatment="zero",
        unknown_treatment="negative",
    )

    np.testing.assert_array_equal(signs, [1.0, -1.0, 0.0, -1.0])
    assert counts == {
        "excitatory": 1,
        "inhibitory": 1,
        "modulatory": 1,
        "unknown": 1,
        "modulator_treatment": "zero",
        "unknown_treatment": "negative",
    }
