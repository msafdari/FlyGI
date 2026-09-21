"""Milestone 3: the frame-to-action causal path must be live, not decorative."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, StrEnum

import numpy as np
import pytest
from scipy import sparse

from flygi.arc.policy import ConnectomePolicy, PolicyError, StatePolicy
from flygi.decoding.coordinate_head import CoordinateHead, novelty_centroid
from flygi.decoding.dn_trace import DescendingTrace, ReadoutError, contiguous_groups
from flygi.decoding.literal import LiteralActionMap, scale_aware_probabilities
from flygi.dynamics.rate import RateParameters, ScipyRateNetwork
from flygi.encoding.features import (
    FEATURE_DIMENSION,
    FeatureError,
    encode_observation,
    latest_grid,
)
from flygi.encoding.sparse_projection import (
    ProjectionOptions,
    build_sensory_projection,
)

NODES = 600
SENSORY = 200
READOUT = 256


class FakeGameState(StrEnum):
    NOT_PLAYED = "NOT_PLAYED"
    NOT_FINISHED = "NOT_FINISHED"
    WIN = "WIN"
    GAME_OVER = "GAME_OVER"


class FakeGameAction(Enum):
    RESET = 0
    ACTION1 = 1
    ACTION2 = 2
    ACTION3 = 3
    ACTION4 = 4
    ACTION5 = 5
    ACTION6 = 6
    ACTION7 = 7

    def __init__(self, _: int) -> None:
        self.action_data: dict[str, int] = {}
        self.reasoning: object | None = None

    def is_complex(self) -> bool:
        return self is type(self).ACTION6

    def set_data(self, data: dict[str, int]) -> dict[str, int]:
        self.action_data = dict(data)
        return self.action_data

    @classmethod
    def from_id(cls, action_id: int) -> FakeGameAction:
        return cls(action_id)


@dataclass
class FakeFrame:
    state: FakeGameState = FakeGameState.NOT_FINISHED
    available_actions: list[int] = field(default_factory=lambda: [1, 2, 3, 4, 5, 6, 7])
    frame: list = field(default_factory=list)


def _grid(seed: int) -> np.ndarray:
    generator = np.random.default_rng(seed)
    return generator.integers(0, 16, size=(64, 64), dtype=np.int8)


def _frame(seed: int, **kwargs: object) -> FakeFrame:
    return FakeFrame(frame=[_grid(seed)], **kwargs)  # type: ignore[arg-type]


def _network(gain: float = 0.9, seed: int = 0) -> ScipyRateNetwork:
    generator = np.random.default_rng(seed)
    dense = (generator.random((NODES, NODES)) < 0.05) * generator.random((NODES, NODES))
    np.fill_diagonal(dense, 0.0)
    matrix = sparse.csr_matrix(dense.astype(np.float32))
    matrix.sort_indices()
    rows = np.asarray(abs(matrix).sum(axis=1)).ravel()
    scale = 1.0 / (1e-8 + rows)
    matrix = sparse.diags(scale.astype(np.float32)) @ matrix
    matrix = matrix.tocsr()
    matrix.sort_indices()
    matrix.eliminate_zeros()
    return ScipyRateNetwork(
        matrix.astype(np.float32),
        RateParameters(internal_steps=4, leak=0.3, recurrent_gain=gain),
    )


def _policy(*, ablate_graph: bool = False, decision_seed: int = 0) -> ConnectomePolicy:
    """Mirror the factory, including the matched bypass for the ablation."""

    readout_indices = np.arange(NODES - READOUT, NODES, dtype=np.int64)
    if ablate_graph:
        # Same interface budget, readout-targeted, zero recurrence.
        target = readout_indices
        per_neuron = max(1, round(SENSORY * 32 / READOUT))
        network = _network(gain=0.0)
    else:
        target = np.arange(SENSORY, dtype=np.int64)
        per_neuron = 32
        network = _network()
    projection = build_sensory_projection(
        target,
        NODES,
        seed=0,
        options=ProjectionOptions(connections_per_neuron=per_neuron, input_scale=1.0),
    )
    readout = DescendingTrace(readout_indices, NODES)
    return ConnectomePolicy(
        FakeGameAction,
        network=network,
        projection=projection,
        readout=readout,
        action_map=LiteralActionMap(READOUT),
        coordinate_head=CoordinateHead(READOUT),
        internal_steps=4,
        decision_seed=decision_seed,
        state_policy=StatePolicy(),
        ablate_graph=ablate_graph,
    )


# --- features ---------------------------------------------------------------


def test_features_encode_the_declared_layout() -> None:
    grid = _grid(1)
    features = encode_observation(
        _frame(1), previous_grid=None, previous_action_id=3, available_action_ids=(1, 2)
    )
    assert features.vector.shape == (FEATURE_DIMENSION,)
    assert features.changed_cells == 0
    # 4,096 one-hot cells plus the previous action plus two legal-action bits.
    assert np.count_nonzero(features.vector) == 4096 + 1 + 2
    assert np.array_equal(features.grid, grid)


def test_features_report_changed_cells_against_the_previous_frame() -> None:
    first = _grid(1)
    features = encode_observation(
        _frame(2), previous_grid=first, previous_action_id=None, available_action_ids=(1,)
    )
    assert features.changed_cells > 0
    assert features.changed_cells == int(np.count_nonzero(first != _grid(2)))


def test_features_reject_malformed_grids() -> None:
    with pytest.raises(FeatureError):
        latest_grid(FakeFrame(frame=[np.zeros((8, 8), dtype=np.int8)]))
    with pytest.raises(FeatureError):
        latest_grid(FakeFrame(frame=[np.full((64, 64), 99, dtype=np.int16)]))
    with pytest.raises(FeatureError):
        latest_grid(FakeFrame(frame=[]))


# --- the causal path --------------------------------------------------------


def test_a_changed_frame_changes_the_sensory_drive() -> None:
    projection = build_sensory_projection(np.arange(SENSORY, dtype=np.int64), NODES, seed=0)
    first = encode_observation(
        _frame(1), previous_grid=None, previous_action_id=None, available_action_ids=(1,)
    )
    second = encode_observation(
        _frame(2), previous_grid=None, previous_action_id=None, available_action_ids=(1,)
    )
    assert not np.array_equal(projection.drive(first.vector), projection.drive(second.vector))


def test_sensory_drive_changes_graph_state_and_readout_and_logits() -> None:
    """One assertion chain for the whole declared causal path."""

    first, second = _policy(), _policy()
    first.choose_action(_frame(1))
    second.choose_action(_frame(2))

    assert not np.array_equal(first.state, second.state)
    assert first.records[0].readout_mean_abs != second.records[0].readout_mean_abs
    assert first.records[0].logits != second.records[0].logits


def test_ablating_the_graph_changes_the_action_sequence() -> None:
    """The preregistered bypass. No change here would mean the graph is decorative."""

    live = _adaptive_policy(ablate_graph=False)
    ablated = _adaptive_policy(ablate_graph=True)
    live_actions = [live.choose_action(_frame(step)).value for step in range(12)]
    ablated_actions = [ablated.choose_action(_frame(step)).value for step in range(12)]

    assert live_actions != ablated_actions


def test_the_bypass_still_drives_its_readout() -> None:
    """A bypass whose readout is always silent measures nothing."""

    ablated = _policy(ablate_graph=True)
    for step in range(6):
        ablated.choose_action(_frame(step))
    assert not all(record.readout_silent for record in ablated.records)
    assert float(np.abs(ablated.state).max()) > 0.0


def test_the_bypass_has_zero_recurrent_gain() -> None:
    with pytest.raises(PolicyError):
        ConnectomePolicy(
            FakeGameAction,
            network=_network(gain=0.9),
            projection=build_sensory_projection(
                np.arange(NODES - READOUT, NODES, dtype=np.int64), NODES, seed=0
            ),
            readout=DescendingTrace(np.arange(NODES - READOUT, NODES, dtype=np.int64), NODES),
            action_map=LiteralActionMap(READOUT),
            coordinate_head=CoordinateHead(READOUT),
            internal_steps=4,
            ablate_graph=True,
        )


def test_state_persists_across_actions_and_carries_history() -> None:
    policy = _policy()
    policy.choose_action(_frame(1))
    after_first = np.array(policy.state, copy=True)
    policy.choose_action(_frame(1))
    after_second = np.array(policy.state, copy=True)

    # The same observation twice must still change the state, because the graph
    # integrates it rather than recomputing from scratch.
    assert not np.array_equal(after_first, after_second)

    fresh = _policy()
    fresh.choose_action(_frame(1))
    assert np.array_equal(after_first, fresh.state)

    policy.reset_state()
    assert np.array_equal(policy.state, np.zeros(NODES, dtype=np.float32))


def test_two_histories_ending_on_the_same_frame_differ() -> None:
    """Memory, not just reflex: the state must depend on what came before."""

    first, second = _policy(), _policy()
    for step in (1, 2, 3):
        first.choose_action(_frame(step))
    for step in (3, 2, 1):
        second.choose_action(_frame(step))
    shared = _frame(9)
    first.choose_action(shared)
    second.choose_action(shared)

    assert not np.array_equal(first.state, second.state)


# --- protocol compliance ----------------------------------------------------


@pytest.mark.parametrize(
    "mask",
    [[1], [1, 2], [3, 5], [1, 2, 3, 4, 5, 6, 7], [6], [2, 6, 7]],
)
def test_the_chosen_action_is_always_inside_the_mask(mask: list[int]) -> None:
    policy = _policy()
    for step in range(6):
        action = policy.choose_action(_frame(step, available_actions=list(mask)))
        assert action.value in mask


def test_action6_always_emits_integer_coordinates_inside_the_grid() -> None:
    policy = _policy()
    for step in range(20):
        action = policy.choose_action(_frame(step, available_actions=[6]))
        assert action.value == 6
        payload = action.action_data
        assert isinstance(payload["x"], int) and not isinstance(payload["x"], bool)
        assert isinstance(payload["y"], int) and not isinstance(payload["y"], bool)
        assert 0 <= payload["x"] <= 63
        assert 0 <= payload["y"] <= 63


@pytest.mark.parametrize("state", [FakeGameState.NOT_PLAYED, FakeGameState.GAME_OVER])
def test_protocol_reset_states_always_produce_reset(state: FakeGameState) -> None:
    policy = _policy()
    action = policy.choose_action(_frame(1, state=state, available_actions=[1, 2, 3]))
    assert action is FakeGameAction.RESET
    assert policy.records[-1].forced_reset


def test_the_graph_still_sees_the_frame_on_a_forced_reset() -> None:
    """State must survive a game over so the failed attempt leaves a trace."""

    policy = _policy()
    policy.choose_action(_frame(1, state=FakeGameState.GAME_OVER))
    assert not np.array_equal(policy.state, np.zeros(NODES, dtype=np.float32))


def test_is_done_only_on_a_win() -> None:
    policy = _policy()
    assert policy.is_done(_frame(1, state=FakeGameState.WIN))
    assert not policy.is_done(_frame(1, state=FakeGameState.GAME_OVER))
    assert not policy.is_done(_frame(1, state=FakeGameState.NOT_FINISHED))


def test_an_empty_mask_in_an_active_state_is_an_error_not_a_guess() -> None:
    policy = _policy()
    with pytest.raises(PolicyError):
        policy.choose_action(_frame(1, available_actions=[]))


def test_the_same_seed_and_frames_give_the_same_actions() -> None:
    frames = [_frame(step) for step in range(8)]
    repeat_a = _policy(decision_seed=17)
    repeat_b = _policy(decision_seed=17)
    first = [repeat_a.choose_action(frame).value for frame in frames]
    second = [repeat_b.choose_action(frame).value for frame in frames]
    assert first == second


def test_same_seed_replays_click_payloads_and_different_seeds_diverge() -> None:
    """Click-only games need seeded coordinate diversity, not action diversity."""

    frame = _frame(7, available_actions=[6])

    def click_trace(seed: int) -> list[tuple[int, int]]:
        policy = _policy(decision_seed=seed)
        trace = []
        for _ in range(12):
            action = policy.choose_action(frame)
            trace.append((int(action.action_data["x"]), int(action.action_data["y"])))
        return trace

    assert click_trace(41) == click_trace(41)
    assert click_trace(41) != click_trace(42)


def test_reset_state_rewinds_the_single_policy_rng() -> None:
    policy = _policy(decision_seed=123)
    frame = _frame(7, available_actions=[6])
    first = []
    for _ in range(5):
        action = policy.choose_action(frame)
        first.append(dict(action.action_data))
    policy.reset_state()
    replay = []
    for _ in range(5):
        action = policy.choose_action(frame)
        replay.append(dict(action.action_data))
    assert replay == first


def test_policy_reports_zero_trainable_parameters() -> None:
    description = _policy().describe()
    assert description["trainable_parameters"] == 0
    assert description["encoder"]["trainable"] is False
    assert description["action_map"]["trainable"] is False
    assert description["coordinate_head"]["trainable"] is False
    assert description["decision_rng"]["seed"] == 0
    assert description["action_map"]["selection"] == "zscore_softmax_categorical"
    assert description["coordinate_head"]["selection"] == "zscore_softmax_categorical"


# --- decoder units ----------------------------------------------------------


def test_contiguous_groups_partition_exactly_once() -> None:
    blocks = contiguous_groups(1314, 8)
    assert sum(block.size for block in blocks) == 1314
    assert np.array_equal(np.concatenate(blocks), np.arange(1314))
    with pytest.raises(ReadoutError):
        contiguous_groups(4, 8)


def test_a_silent_readout_standardizes_to_zero_rather_than_amplified_noise() -> None:
    readout = DescendingTrace(np.arange(0, 16, dtype=np.int64), NODES)
    state = np.zeros(NODES, dtype=np.float32)
    trace, diagnostics = readout.standardized(state)
    assert diagnostics.silent
    assert np.array_equal(trace, np.zeros(16, dtype=np.float32))


def test_standardization_removes_the_readout_magnitude_problem() -> None:
    """Real descending activity is of order 1e-6; logits must not be."""

    readout = DescendingTrace(np.arange(0, 64, dtype=np.int64), NODES)
    state = np.zeros(NODES, dtype=np.float32)
    generator = np.random.default_rng(0)
    state[:64] = (generator.standard_normal(64) * 1e-6).astype(np.float32)
    trace, diagnostics = readout.standardized(state)

    assert diagnostics.mean_abs < 1e-5
    assert not diagnostics.silent
    assert abs(float(trace.mean())) < 1e-4
    assert 0.9 < float(trace.std()) < 1.1


def test_action_map_never_selects_a_masked_action_even_when_it_scores_highest() -> None:
    action_map = LiteralActionMap(READOUT)
    trace = np.zeros(READOUT, dtype=np.float32)
    blocks = contiguous_groups(READOUT, 8)
    trace[blocks[4]] = 10.0  # ACTION4 would win if the mask were ignored.
    decision = action_map.decide(trace, [1, 2], rng=np.random.default_rng(0))
    assert decision.action_id in (1, 2)
    assert float(decision.masked_logits[4]) == float("-inf")
    assert decision.probabilities[4] == 0.0
    assert np.isclose(decision.probabilities.sum(), 1.0)


def test_scale_aware_sampling_is_invariant_to_positive_affine_logit_scale() -> None:
    logits = np.asarray([-0.2, 0.1, 0.9, 0.4], dtype=np.float32)
    first, _ = scale_aware_probabilities(logits, 0.35)
    second, _ = scale_aware_probabilities(logits * 1000.0 + 27.0, 0.35)
    assert np.allclose(first, second, atol=1e-6)


def test_flat_logits_are_sampled_uniformly_and_singletons_are_certain() -> None:
    flat, flat_scale = scale_aware_probabilities(np.zeros(4, dtype=np.float32), 0.35)
    singleton, singleton_scale = scale_aware_probabilities(np.ones(1, dtype=np.float32), 0.35)
    assert np.array_equal(flat, np.full(4, 0.25))
    assert flat_scale == 0.0
    assert np.array_equal(singleton, np.ones(1))
    assert singleton_scale == 0.0


def test_coordinate_head_responds_to_the_trace() -> None:
    head = CoordinateHead(READOUT)
    generator = np.random.default_rng(0)
    seen = {
        head.coordinates(generator.standard_normal(READOUT).astype(np.float32)) for _ in range(32)
    }
    assert len(seen) > 1
    assert all(0 <= x <= 63 and 0 <= y <= 63 for x, y in seen)


def test_coordinate_head_requires_enough_readout_neurons() -> None:
    with pytest.raises(ReadoutError):
        CoordinateHead(64)


def test_novelty_centroid_uses_changed_cells_in_xy_order() -> None:
    before = np.zeros((64, 64), dtype=np.int8)
    after = np.array(before, copy=True)
    after[10, 20] = 1
    after[12, 24] = 1
    assert novelty_centroid(before, after) == (22, 11)
    assert novelty_centroid(after, after) is None
    assert novelty_centroid(None, after) is None


def test_unchanged_clicks_explore_distinct_seeded_coordinates() -> None:
    policy = _policy(decision_seed=5)
    frame = _frame(9, available_actions=[6])
    coordinates = []
    methods = []
    for _ in range(10):
        action = policy.choose_action(frame)
        coordinates.append((action.action_data["x"], action.action_data["y"]))
        methods.append(policy.records[-1].coordinate_method)

    assert methods[0] == "factorized_sample"
    assert methods[1:] == ["seeded_untried_uniform"] * 9
    assert len(set(coordinates)) == len(coordinates)


def test_a_changed_frame_after_a_click_uses_the_novelty_centroid() -> None:
    policy = _policy(decision_seed=5)
    first = np.zeros((64, 64), dtype=np.int8)
    second = np.array(first, copy=True)
    second[7, 13] = 1
    policy.choose_action(FakeFrame(available_actions=[6], frame=[first]))
    action = policy.choose_action(FakeFrame(available_actions=[6], frame=[second]))
    assert action.action_data == {"x": 13, "y": 7}
    assert policy.records[-1].coordinate_method == "novelty_centroid"


# --- adaptive readout -------------------------------------------------------


def _adaptive_policy(**kwargs: object) -> ConnectomePolicy:
    from flygi.decoding.dn_trace import AdaptiveStandardizer

    policy = _policy(**kwargs)  # type: ignore[arg-type]
    policy._standardizer = AdaptiveStandardizer(READOUT, adaptation_rate=0.1, clip=10.0)
    return policy


def test_adaptive_standardizer_removes_a_constant_offset() -> None:
    """Fixed per-neuron offsets must not decide the action."""

    from flygi.decoding.dn_trace import AdaptiveStandardizer

    standardizer = AdaptiveStandardizer(64, adaptation_rate=0.3)
    offset = np.linspace(0.0, 1.0, 64).astype(np.float32)
    generator = np.random.default_rng(0)

    outputs = []
    for _ in range(40):
        signal = offset + (generator.standard_normal(64) * 1e-3).astype(np.float32)
        outputs.append(standardizer.transform(signal))

    settled = np.asarray(outputs[20:])
    # If the offset survived, the same neurons would dominate every turn.
    assert abs(float(settled.mean())) < 1.0
    assert len({int(np.argmax(row)) for row in settled}) > 1


def test_adaptive_standardizer_removes_a_slow_drift() -> None:
    """The measured failure mode: a drifting state locks the argmax."""

    from flygi.decoding.dn_trace import AdaptiveStandardizer

    standardizer = AdaptiveStandardizer(32, adaptation_rate=0.3)
    generator = np.random.default_rng(1)
    picks = []
    for step in range(40):
        drift = np.full(32, step * 0.5, dtype=np.float32)
        drift[0] += 5.0  # a persistently high neuron
        signal = drift + (generator.standard_normal(32) * 0.1).astype(np.float32)
        picks.append(int(np.argmax(standardizer.transform(signal))))

    assert len(set(picks[10:])) > 1


def test_adaptive_standardizer_first_turn_has_no_expectation() -> None:
    from flygi.decoding.dn_trace import AdaptiveStandardizer

    standardizer = AdaptiveStandardizer(16)
    first = standardizer.transform(np.arange(16, dtype=np.float32))
    assert np.array_equal(first, np.zeros(16, dtype=np.float32))
    assert standardizer.turns_seen == 1


def test_adaptive_standardizer_output_is_always_bounded() -> None:
    from flygi.decoding.dn_trace import AdaptiveStandardizer

    standardizer = AdaptiveStandardizer(16, adaptation_rate=0.5, clip=10.0)
    generator = np.random.default_rng(2)
    for step in range(50):
        scale = 1e-9 if step % 2 else 1e6
        values = (generator.standard_normal(16) * scale).astype(np.float32)
        output = standardizer.transform(values)
        assert np.isfinite(output).all()
        assert float(np.abs(output).max()) <= 10.0


def test_adaptive_standardizer_resets_with_the_neural_state() -> None:
    from flygi.decoding.dn_trace import AdaptiveStandardizer

    standardizer = AdaptiveStandardizer(8)
    standardizer.transform(np.ones(8, dtype=np.float32))
    standardizer.transform(np.full(8, 2.0, dtype=np.float32))
    assert standardizer.turns_seen == 2
    standardizer.reset()
    assert standardizer.turns_seen == 0


def test_adaptive_readout_produces_varied_actions_where_population_zscore_locks() -> None:
    """Regression guard for the observed constant-argmax behavior."""

    generator = np.random.default_rng(3)
    frames = [_frame(int(seed)) for seed in generator.integers(0, 10_000, size=24)]

    plain = _policy()
    adaptive = _adaptive_policy()
    plain_actions = [plain.choose_action(frame).value for frame in frames]
    adaptive_actions = [adaptive.choose_action(frame).value for frame in frames]

    assert len(set(adaptive_actions)) >= len(set(plain_actions))
    assert len(set(adaptive_actions)) > 1


def test_adaptive_readout_still_respects_the_mask_and_coordinates() -> None:
    policy = _adaptive_policy()
    for step in range(10):
        action = policy.choose_action(_frame(step, available_actions=[2, 6]))
        assert action.value in (2, 6)
        if action.value == 6:
            assert 0 <= action.action_data["x"] <= 63
            assert 0 <= action.action_data["y"] <= 63
