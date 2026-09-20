"""Lock the documented W[post, pre] convention with a three-neuron chain."""

from __future__ import annotations

import numpy as np
import pandas as pd

from flygi.connectome.build import NodeIndex, build_sparse_counts


def test_a_to_b_to_c_propagates_forward_only() -> None:
    a, b, c = 2**40 + 1, 2**40 + 2, 2**40 + 3
    edges = pd.DataFrame(
        {
            "body_pre": pd.Series([a, b], dtype="int64"),
            "body_post": pd.Series([b, c], dtype="int64"),
            "weight": pd.Series([2, 3], dtype="int64"),
        }
    )
    index = NodeIndex.from_body_ids(pd.Series([a, b, c], dtype="int64"))
    matrix = build_sparse_counts(edges, index)

    activity_a = np.asarray([1.0, 0.0, 0.0])
    after_one_step = matrix @ activity_a
    after_two_steps = matrix @ after_one_step

    np.testing.assert_array_equal(after_one_step, [0.0, 2.0, 0.0])
    np.testing.assert_array_equal(after_two_steps, [0.0, 0.0, 6.0])
    assert matrix[index.indices_for([a])[0], index.indices_for([b])[0]] == 0


def test_dense_mapping_round_trips_ids_above_32_bits() -> None:
    body_ids = np.asarray([2**48 + 2, 7, 2**40 + 1], dtype=np.uint64)
    index = NodeIndex.from_body_ids(body_ids)
    dense = index.indices_for(body_ids)

    assert index.body_ids.dtype == np.uint64
    np.testing.assert_array_equal(index.body_ids_for(dense), body_ids)
