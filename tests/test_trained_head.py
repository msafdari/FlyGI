"""The Track B trainable readout over a frozen connectome."""

from __future__ import annotations

import numpy as np
import pytest

from flygi.decoding.dn_trace import ReadoutError
from flygi.decoding.trained_head import TrainedActionHead, TrainedHeadSpec

READOUT = 1314


def _head(**kwargs: object) -> TrainedActionHead:
    return TrainedActionHead(TrainedHeadSpec(readout_size=READOUT, **kwargs))  # type: ignore[arg-type]


def test_parameter_budget_is_small_and_declared() -> None:
    """A head big enough to solve the task alone would prove nothing."""

    spec = TrainedHeadSpec(readout_size=READOUT)
    assert spec.input_dim == spec.feature_dim + 16
    assert spec.parameter_count == spec.input_dim * 8 + 8
    assert spec.parameter_count < 1000


def test_zero_parameters_give_zero_logits() -> None:
    head = _head()
    trace = np.random.default_rng(0).standard_normal(READOUT).astype(np.float32)
    assert np.allclose(head.logits(trace, None, (1, 2)), 0.0)


def test_logits_depend_on_the_readout() -> None:
    """If the trace did not reach the logits the graph would be decorative."""

    head = _head()
    generator = np.random.default_rng(1)
    head.set_parameters(generator.standard_normal(head.parameter_count))
    a = generator.standard_normal(READOUT).astype(np.float32)
    b = generator.standard_normal(READOUT).astype(np.float32)
    assert not np.allclose(head.logits(a, None, (1, 2)), head.logits(b, None, (1, 2)))


def test_logits_depend_on_protocol_context() -> None:
    head = _head()
    generator = np.random.default_rng(2)
    head.set_parameters(generator.standard_normal(head.parameter_count))
    trace = generator.standard_normal(READOUT).astype(np.float32)

    assert not np.allclose(head.logits(trace, 1, (1, 2)), head.logits(trace, 3, (1, 2)))
    assert not np.allclose(head.logits(trace, 1, (1, 2)), head.logits(trace, 1, (1, 2, 5)))


def test_the_fixed_projection_is_not_trainable_and_is_seed_stable() -> None:
    """The compression is part of the frozen interface, shared across conditions."""

    first, second = _head(), _head()
    generator = np.random.default_rng(3)
    trace = generator.standard_normal(READOUT).astype(np.float32)
    assert np.array_equal(first.features(trace, None, ()), second.features(trace, None, ()))
    assert first.describe()["projection_trainable"] is False

    other = _head(projection_seed=999)
    assert not np.allclose(other.features(trace, None, ()), first.features(trace, None, ()))


def test_parameters_round_trip_and_validate() -> None:
    head = _head()
    values = np.random.default_rng(4).standard_normal(head.parameter_count)
    head.set_parameters(values)
    assert np.allclose(head.get_parameters(), values.astype(np.float32))

    with pytest.raises(ReadoutError):
        head.set_parameters(np.zeros(3))
    with pytest.raises(ReadoutError):
        head.set_parameters(np.full(head.parameter_count, np.nan))


def test_head_rejects_malformed_inputs() -> None:
    head = _head()
    with pytest.raises(ReadoutError):
        head.logits(np.zeros(7, dtype=np.float32), None, (1,))
    with pytest.raises(ReadoutError):
        head.logits(np.zeros(READOUT, dtype=np.float32), 99, (1,))
    with pytest.raises(ReadoutError):
        head.logits(np.zeros(READOUT, dtype=np.float32), None, (99,))
    with pytest.raises(ReadoutError):
        head.logits(np.full(READOUT, np.inf, dtype=np.float32), None, (1,))


def test_spec_rejects_unusable_shapes() -> None:
    for kwargs in (
        {"readout_size": 0},
        {"readout_size": 10, "feature_dim": 0},
        {"readout_size": 10, "feature_dim": 11},
        {"readout_size": 10, "action_slots": 4},
    ):
        with pytest.raises(ReadoutError):
            TrainedHeadSpec(**kwargs)  # type: ignore[arg-type]


def test_trained_head_changes_the_policy_action_sequence() -> None:
    """If the head did not reach the action, Track B would be decorative."""

    import test_closed_loop as loop

    frames = [loop._frame(step) for step in range(14)]
    baseline = loop._adaptive_policy()
    base_actions = [baseline.choose_action(f).value for f in frames]

    head = TrainedActionHead(TrainedHeadSpec(readout_size=loop.READOUT))
    head.set_parameters(np.random.default_rng(7).standard_normal(head.parameter_count) * 3.0)
    trained = loop._adaptive_policy()
    trained._trained_head = head
    trained_actions = [trained.choose_action(f).value for f in frames]

    assert base_actions != trained_actions


def test_trained_head_still_respects_the_legal_mask() -> None:
    import test_closed_loop as loop

    head = TrainedActionHead(TrainedHeadSpec(readout_size=loop.READOUT))
    head.set_parameters(np.random.default_rng(8).standard_normal(head.parameter_count) * 5.0)
    policy = loop._adaptive_policy()
    policy._trained_head = head
    for step in range(12):
        action = policy.choose_action(loop._frame(step, available_actions=[2, 5]))
        assert action.value in (2, 5)


def test_trace_ablation_blinds_the_head_to_the_connectome() -> None:
    """The diagnostic that decides whether a trained result is a graph result."""

    import test_closed_loop as loop

    head = TrainedActionHead(TrainedHeadSpec(readout_size=loop.READOUT))
    head.set_parameters(np.random.default_rng(11).standard_normal(head.parameter_count) * 3.0)

    live = loop._adaptive_policy()
    live._trained_head = head
    blind = loop._adaptive_policy()
    blind._trained_head = head
    blind._ablate_trace = True

    frames = [loop._frame(step) for step in range(14)]
    assert [live.choose_action(f).value for f in frames] != [
        blind.choose_action(f).value for f in frames
    ]
    assert blind.describe()["trace_ablated"] is True
    assert live.describe()["trace_ablated"] is False
