"""Deterministic acceptance tests for the sparse leaky-rate backend."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from flygi.dynamics import DynamicsValidationError, RateParameters, ScipyRateNetwork


def _chain() -> sparse.csr_matrix:
    """Return the three-node chain 0 -> 1 -> 2 as W[post, pre]."""

    return sparse.csr_matrix(
        (
            np.ones(2, dtype=np.float32),
            (np.asarray([1, 2], dtype=np.int32), np.asarray([0, 1], dtype=np.int32)),
        ),
        shape=(3, 3),
        dtype=np.float32,
    )


def test_rate_step_matches_declared_equation() -> None:
    connectivity = sparse.csr_matrix(
        np.asarray(
            [
                [0.0, 0.5, -0.25],
                [0.75, 0.0, 0.0],
                [0.0, -0.5, 0.0],
            ],
            dtype=np.float32,
        )
    )
    parameters = RateParameters(internal_steps=4, leak=0.3, recurrent_gain=0.9, bias=0.1)
    network = ScipyRateNetwork(connectivity, parameters)
    state = np.asarray([0.2, -0.4, 0.1], dtype=np.float32)
    input_current = np.asarray([0.05, 0.2, -0.1], dtype=np.float32)

    expected = (np.float32(1.0 - parameters.leak) * state) + np.float32(parameters.leak) * np.tanh(
        np.float32(parameters.recurrent_gain) * (connectivity @ state)
        + input_current
        + np.float32(parameters.bias)
    )
    actual = network.step(state, input_current)

    assert actual.dtype == np.float32
    np.testing.assert_allclose(actual, expected, rtol=1e-6, atol=1e-7)


def test_step_and_advance_have_identical_update_semantics() -> None:
    parameters = RateParameters(internal_steps=5, leak=0.3, recurrent_gain=0.9)
    network = ScipyRateNetwork(_chain(), parameters)
    state = np.asarray([0.25, -0.1, 0.05], dtype=np.float32)
    input_current = np.asarray([0.2, 0.0, -0.05], dtype=np.float32)

    one_step = network.step(state, input_current)
    explicit_one_step = network.advance(state, input_current, internal_steps=1)
    np.testing.assert_array_equal(one_step, explicit_one_step)

    repeated = state.copy()
    for _ in range(parameters.internal_steps):
        repeated = network.step(repeated, input_current)
    configured_advance = network.advance(state, input_current)
    np.testing.assert_array_equal(repeated, configured_advance)


def test_same_seed_and_inputs_are_bitwise_deterministic() -> None:
    network = ScipyRateNetwork(
        _chain(),
        RateParameters(internal_steps=7, leak=0.6, recurrent_gain=1.1, bias=-0.02),
    )
    first_initial = network.initial_state(seed=20260920, scale=0.5)
    second_initial = network.initial_state(seed=20260920, scale=0.5)
    other_initial = network.initial_state(seed=20260921, scale=0.5)
    input_current = np.asarray([0.1, -0.2, 0.3], dtype=np.float32)

    np.testing.assert_array_equal(first_initial, second_initial)
    assert not np.array_equal(first_initial, other_initial)
    first = network.advance(first_initial, input_current)
    second = network.advance(second_initial, input_current)
    np.testing.assert_array_equal(first, second)


def test_tiny_graph_activity_stays_finite_and_bounded_for_10000_steps() -> None:
    node_count = 8
    rows = np.arange(node_count, dtype=np.int32)
    columns = np.roll(rows, 1)
    weights = np.where(rows % 2 == 0, 1.0, -1.0).astype(np.float32)
    connectivity = sparse.csr_matrix(
        (weights, (rows, columns)),
        shape=(node_count, node_count),
        dtype=np.float32,
    )
    network = ScipyRateNetwork(
        connectivity,
        RateParameters(internal_steps=1, leak=0.6, recurrent_gain=1.1, bias=0.05),
    )
    state = network.initial_state(seed=17, scale=1.0)
    input_current = np.linspace(-0.25, 0.25, node_count, dtype=np.float32)
    maximum_magnitude = float(np.max(np.abs(state)))

    for _ in range(10_000):
        state = network.step(state, input_current)
        assert state.dtype == np.float32
        assert np.isfinite(state).all()
        maximum_magnitude = max(maximum_magnitude, float(np.max(np.abs(state))))

    tolerance = 8 * np.finfo(np.float32).eps
    assert maximum_magnitude <= 1.0 + tolerance


def test_chain_input_changes_graph_state_and_descending_trace() -> None:
    network = ScipyRateNetwork(
        _chain(),
        RateParameters(internal_steps=3, leak=1.0, recurrent_gain=1.0),
    )
    initial = network.initial_state()
    positive_input = np.asarray([1.0, 0.0, 0.0], dtype=np.float32)
    negative_input = -positive_input

    positive_state = network.advance(initial, positive_input)
    negative_state = network.advance(initial, negative_input)
    descending = np.asarray([2], dtype=np.int32)
    positive_trace = network.readout(positive_state, descending)
    negative_trace = network.readout(negative_state, descending)

    sensor = np.tanh(np.float32(1.0))
    relay = np.tanh(sensor)
    expected = np.asarray([sensor, relay, np.tanh(relay)], dtype=np.float32)
    np.testing.assert_allclose(positive_state, expected, rtol=1e-6, atol=1e-7)
    np.testing.assert_allclose(negative_state, -expected, rtol=1e-6, atol=1e-7)
    np.testing.assert_allclose(positive_trace, expected[descending], rtol=1e-6, atol=1e-7)
    np.testing.assert_allclose(negative_trace, -positive_trace, rtol=1e-6, atol=1e-7)
    assert positive_trace[0] > 0.0


def test_caller_arrays_are_unchanged_and_internal_graph_is_frozen() -> None:
    caller_connectivity = _chain()
    network = ScipyRateNetwork(caller_connectivity)
    state = np.asarray([0.3, -0.2, 0.1], dtype=np.float32)
    input_current = np.asarray([-0.1, 0.2, 0.0], dtype=np.float32)
    state_before = state.copy()
    input_before = input_current.copy()
    frozen_weights = network.connectivity.data.copy()

    result = network.advance(state, input_current, internal_steps=3)

    np.testing.assert_array_equal(state, state_before)
    np.testing.assert_array_equal(input_current, input_before)
    assert not np.shares_memory(result, state)
    assert not np.shares_memory(result, input_current)
    assert network.connectivity.data.flags.writeable is False
    assert network.connectivity.indices.flags.writeable is False
    assert network.connectivity.indptr.flags.writeable is False
    with pytest.raises(ValueError):
        network.connectivity.data[0] = 9.0

    caller_connectivity.data[:] = 0.0
    np.testing.assert_array_equal(network.connectivity.data, frozen_weights)


@pytest.mark.parametrize(
    ("keyword", "value", "message"),
    [
        ("internal_steps", 0, "internal_steps"),
        ("internal_steps", True, "internal_steps"),
        ("internal_steps", 1.5, "internal_steps"),
        ("leak", 0.0, "leak"),
        ("leak", 1.01, "leak"),
        ("leak", np.nan, "leak"),
        ("leak", True, "leak"),
        ("leak", "0.3", "leak"),
        ("leak", 1e-100, "underflows"),
        ("recurrent_gain", -0.1, "recurrent_gain"),
        ("recurrent_gain", np.inf, "recurrent_gain"),
        ("recurrent_gain", 1e100, "representable"),
        ("bias", np.nan, "bias"),
        ("bias", False, "bias"),
    ],
)
def test_rate_parameters_reject_invalid_values(keyword: str, value: object, message: str) -> None:
    with pytest.raises(DynamicsValidationError, match=message):
        RateParameters(**{keyword: value})  # type: ignore[arg-type]


def test_network_rejects_invalid_connectivity() -> None:
    with pytest.raises(TypeError, match="CSR"):
        ScipyRateNetwork(np.eye(2, dtype=np.float32))  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="CSR"):
        ScipyRateNetwork(sparse.csc_matrix(np.eye(2, dtype=np.float32)))
    with pytest.raises(DynamicsValidationError, match="square"):
        ScipyRateNetwork(sparse.csr_matrix((2, 3), dtype=np.float32))
    with pytest.raises(DynamicsValidationError, match="at least one"):
        ScipyRateNetwork(sparse.csr_matrix((0, 0), dtype=np.float32))
    with pytest.raises(DynamicsValidationError, match="dtype must be float32"):
        ScipyRateNetwork(sparse.eye(2, format="csr", dtype=np.float64))

    nonfinite = sparse.csr_matrix(np.asarray([[0.0, np.inf], [0.0, 0.0]], dtype=np.float32))
    with pytest.raises(DynamicsValidationError, match="NaN or infinity"):
        ScipyRateNetwork(nonfinite)

    explicit_zero = sparse.csr_matrix(
        (
            np.asarray([0.0], dtype=np.float32),
            np.asarray([1], dtype=np.int32),
            np.asarray([0, 1, 1], dtype=np.int32),
        ),
        shape=(2, 2),
    )
    with pytest.raises(DynamicsValidationError, match="explicit zero"):
        ScipyRateNetwork(explicit_zero)


@pytest.mark.parametrize(
    ("state", "input_current", "message"),
    [
        (np.zeros(2, dtype=np.float32), None, "state must have shape"),
        (np.zeros(3, dtype=np.int32), None, "state dtype must be float32"),
        (
            np.asarray([0.0, np.nan, 0.0], dtype=np.float32),
            None,
            "state contains NaN or infinity",
        ),
        (
            np.zeros(3, dtype=np.float32),
            np.zeros(2, dtype=np.float32),
            "input_current must have shape",
        ),
        (
            np.zeros(3, dtype=np.float32),
            np.zeros(3, dtype=np.int32),
            "input_current dtype must be float32",
        ),
        (
            np.zeros(3, dtype=np.float32),
            np.asarray([0.0, 0.0, np.inf], dtype=np.float32),
            "input_current contains NaN or infinity",
        ),
    ],
)
def test_step_rejects_invalid_state_or_input(
    state: np.ndarray, input_current: np.ndarray | None, message: str
) -> None:
    network = ScipyRateNetwork(_chain())

    with pytest.raises(DynamicsValidationError, match=message):
        network.step(state, input_current)


@pytest.mark.parametrize("internal_steps", [0, -1, True, 1.5])
def test_advance_rejects_invalid_internal_steps(internal_steps: object) -> None:
    network = ScipyRateNetwork(_chain())

    with pytest.raises(DynamicsValidationError, match="internal_steps"):
        network.advance(network.initial_state(), internal_steps=internal_steps)  # type: ignore[arg-type]


def test_initial_state_and_readout_validation() -> None:
    network = ScipyRateNetwork(_chain())

    with pytest.raises(DynamicsValidationError, match="scale"):
        network.initial_state(scale=-0.1)
    with pytest.raises(DynamicsValidationError, match="scale"):
        network.initial_state(scale=np.inf)
    with pytest.raises(DynamicsValidationError, match="seed is required"):
        network.initial_state(scale=0.1)
    with pytest.raises(DynamicsValidationError, match="one-dimensional integer"):
        network.readout(network.initial_state(), np.asarray([0.0]))
    with pytest.raises(DynamicsValidationError, match="outside"):
        network.readout(network.initial_state(), np.asarray([3], dtype=np.int32))
