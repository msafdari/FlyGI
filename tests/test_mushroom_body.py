"""Reward-modulated plasticity at the site where Drosophila actually learns."""

from __future__ import annotations

import numpy as np
import pytest
from scipy import sparse

from flygi.plasticity import (
    MushroomBody,
    MushroomBodyError,
    MushroomBodyParameters,
    resolve_mushroom_body,
)

KC = np.arange(0, 40, dtype=np.int64)
MBON = np.arange(40, 48, dtype=np.int64)
DAN = np.arange(48, 54, dtype=np.int64)
OTHER = np.arange(54, 60, dtype=np.int64)
NODES = 60


def _graph(seed: int = 0) -> sparse.csr_matrix:
    """A toy brain with a wired mushroom body and unrelated circuitry."""

    generator = np.random.default_rng(seed)
    dense = np.zeros((NODES, NODES), dtype=np.float32)
    dense[np.ix_(MBON, KC)] = generator.random((len(MBON), len(KC))) * 0.5 + 0.1
    dense[np.ix_(MBON, DAN)] = generator.random((len(MBON), len(DAN))) * 0.3 + 0.05
    dense[np.ix_(OTHER, KC)] = generator.random((len(OTHER), len(KC))) * 0.4 + 0.1
    matrix = sparse.csr_matrix(dense)
    matrix.sort_indices()
    return matrix


def _anatomy(matrix: sparse.csr_matrix):
    return resolve_mushroom_body(matrix, kenyon_cells=KC, mbons=MBON, dopaminergic=DAN)


def _state(seed: int = 1, kc_scale: float = 1.0, dan_scale: float = 1.0) -> np.ndarray:
    generator = np.random.default_rng(seed)
    state = np.zeros(NODES, dtype=np.float32)
    state[KC] = (generator.random(len(KC)) * kc_scale).astype(np.float32)
    state[DAN] = (generator.random(len(DAN)) * dan_scale).astype(np.float32)
    return state


def test_the_plastic_block_is_exactly_the_kenyon_to_mbon_edges() -> None:
    matrix = _graph()
    body = MushroomBody(matrix, _anatomy(matrix))
    assert body.plastic_edge_count == len(KC) * len(MBON)
    assert body.describe()["site"] == "Kenyon cell -> MBON"


def test_plasticity_never_touches_the_rest_of_the_graph() -> None:
    """Everything outside the mushroom body must stay exactly frozen."""

    matrix = _graph()
    body = MushroomBody(matrix, _anatomy(matrix))
    before = matrix[np.ix_(OTHER, KC)].toarray().copy()
    dan_before = matrix[np.ix_(MBON, DAN)].toarray().copy()

    for _ in range(5):
        body.update(matrix, _state(), reward=1.0)

    assert np.array_equal(matrix[np.ix_(OTHER, KC)].toarray(), before)
    assert np.array_equal(matrix[np.ix_(MBON, DAN)].toarray(), dan_before)


def test_reward_and_coincident_activity_are_both_required() -> None:
    """The rule is three-factor: no reward, no dopamine, or no Kenyon cells means no learning."""

    for label, reward, kc_scale, dan_scale in (
        ("no reward", 0.0, 1.0, 1.0),
        ("no kenyon activity", 1.0, 0.0, 1.0),
        ("no dopamine", 1.0, 1.0, 0.0),
    ):
        matrix = _graph()
        body = MushroomBody(
            matrix, _anatomy(matrix), MushroomBodyParameters(learning_rate=0.5, decay=0.0)
        )
        before = matrix.data.copy()
        body.update(matrix, _state(kc_scale=kc_scale, dan_scale=dan_scale), reward=reward)
        assert np.array_equal(matrix.data, before), label


def test_dopamine_depresses_the_active_synapses() -> None:
    """The established direction of the effect, not a convenience choice."""

    matrix = _graph()
    body = MushroomBody(
        matrix, _anatomy(matrix), MushroomBodyParameters(learning_rate=0.2, decay=0.0)
    )
    before = matrix[np.ix_(MBON, KC)].toarray().copy()
    body.update(matrix, _state(), reward=1.0)
    after = matrix[np.ix_(MBON, KC)].toarray()

    assert (after <= before + 1e-6).all()
    assert (after < before - 1e-9).any()


def test_negative_reward_potentiates_back_toward_baseline() -> None:
    matrix = _graph()
    body = MushroomBody(
        matrix, _anatomy(matrix), MushroomBodyParameters(learning_rate=0.2, decay=0.0)
    )
    before = matrix[np.ix_(MBON, KC)].toarray().copy()
    body.update(matrix, _state(), reward=-1.0)
    after = matrix[np.ix_(MBON, KC)].toarray()
    assert (after >= before - 1e-6).all()


def test_weights_stay_bounded_and_keep_their_sign_under_extreme_reward() -> None:
    """Plasticity must modulate the connectome, never invert or erase it."""

    matrix = _graph()
    body = MushroomBody(
        matrix, _anatomy(matrix), MushroomBodyParameters(learning_rate=5.0, decay=0.0)
    )
    for _ in range(50):
        body.update(matrix, _state(), reward=1000.0)
    block = matrix[np.ix_(MBON, KC)].toarray()
    assert np.isfinite(block).all()
    assert (block >= 0.0).all()
    assert block.max() <= 1.0


def test_decay_relaxes_toward_the_frozen_baseline() -> None:
    matrix = _graph()
    body = MushroomBody(
        matrix, _anatomy(matrix), MushroomBodyParameters(learning_rate=0.3, decay=0.0)
    )
    baseline = matrix[np.ix_(MBON, KC)].toarray().copy()
    for _ in range(5):
        body.update(matrix, _state(), reward=1.0)
    depressed = matrix[np.ix_(MBON, KC)].toarray().copy()
    assert (depressed < baseline - 1e-9).any()

    body._parameters = MushroomBodyParameters(learning_rate=0.0, decay=0.5)
    for _ in range(30):
        body.update(matrix, _state(), reward=0.0)
    relaxed = matrix[np.ix_(MBON, KC)].toarray()
    assert np.abs(relaxed - baseline).mean() < np.abs(depressed - baseline).mean()


def test_reset_restores_the_frozen_baseline_exactly() -> None:
    matrix = _graph()
    body = MushroomBody(matrix, _anatomy(matrix))
    baseline = matrix.data.copy()
    for _ in range(5):
        body.update(matrix, _state(), reward=1.0)
    assert not np.array_equal(matrix.data, baseline)
    body.reset(matrix)
    assert np.array_equal(matrix.data, baseline)
    assert body.updates_applied == 0


def test_the_compartment_map_comes_from_real_anatomy() -> None:
    """Which MBON a teaching signal reaches is decided by the connectome."""

    matrix = _graph()
    anatomy = _anatomy(matrix)
    assert anatomy.dan_to_mbon.shape == (len(MBON), len(DAN))
    assert anatomy.dan_to_mbon.nnz == len(MBON) * len(DAN)

    isolated = _graph()
    dense = isolated.toarray()
    dense[np.ix_(MBON[:4], DAN)] = 0.0  # half the MBONs lose dopaminergic input
    isolated = sparse.csr_matrix(dense)
    isolated.sort_indices()
    body = MushroomBody(
        isolated,
        resolve_mushroom_body(isolated, kenyon_cells=KC, mbons=MBON, dopaminergic=DAN),
        MushroomBodyParameters(learning_rate=0.3, decay=0.0),
    )
    before = isolated[np.ix_(MBON, KC)].toarray().copy()
    body.update(isolated, _state(), reward=1.0)
    after = isolated[np.ix_(MBON, KC)].toarray()

    assert np.array_equal(after[:4], before[:4])
    assert (after[4:] < before[4:] - 1e-9).any()


def test_refuses_an_unwired_mushroom_body() -> None:
    dense = np.zeros((NODES, NODES), dtype=np.float32)
    dense[np.ix_(OTHER, KC)] = 0.5
    matrix = sparse.csr_matrix(dense)
    matrix.sort_indices()
    with pytest.raises(MushroomBodyError):
        MushroomBody(
            matrix,
            resolve_mushroom_body(matrix, kenyon_cells=KC, mbons=MBON, dopaminergic=DAN),
        )


def test_parameters_and_populations_are_validated() -> None:
    for kwargs in (
        {"learning_rate": -1.0},
        {"decay": 1.5},
        {"weight_ceiling_scale": 0.5},
        {"reward_scale": float("nan")},
        {"gate_floor": 0.0},
    ):
        with pytest.raises(MushroomBodyError):
            MushroomBodyParameters(**kwargs)  # type: ignore[arg-type]

    matrix = _graph()
    with pytest.raises(MushroomBodyError):
        resolve_mushroom_body(matrix, kenyon_cells=KC, mbons=KC, dopaminergic=DAN)
    with pytest.raises(MushroomBodyError):
        resolve_mushroom_body(
            matrix, kenyon_cells=np.array([NODES + 5]), mbons=MBON, dopaminergic=DAN
        )


# --- closed-loop integration ------------------------------------------------


def _plastic_policy(reward_source: str = "observation_change", learning_rate: float = 0.5):
    """A toy closed-loop policy whose mushroom body is wired and plastic."""

    import test_closed_loop as loop

    from flygi.arc.policy import ConnectomePolicy, StatePolicy
    from flygi.decoding.coordinate_head import CoordinateHead
    from flygi.decoding.dn_trace import AdaptiveStandardizer, DescendingTrace
    from flygi.decoding.literal import LiteralActionMap
    from flygi.dynamics.rate import RateParameters, ScipyRateNetwork
    from flygi.encoding.sparse_projection import ProjectionOptions, build_sensory_projection

    nodes = loop.NODES
    generator = np.random.default_rng(3)
    dense = (generator.random((nodes, nodes)) < 0.05) * generator.random((nodes, nodes))
    np.fill_diagonal(dense, 0.0)
    kc = np.arange(100, 260, dtype=np.int64)
    mbon = np.arange(260, 300, dtype=np.int64)
    dan = np.arange(300, 340, dtype=np.int64)
    readout = np.arange(nodes - loop.READOUT, nodes, dtype=np.int64)
    dense[np.ix_(mbon, kc)] = generator.random((len(mbon), len(kc))) * 0.5 + 0.2
    dense[np.ix_(mbon, dan)] = generator.random((len(mbon), len(dan))) * 0.3 + 0.1
    dense[np.ix_(readout, mbon)] = generator.random((len(readout), len(mbon))) * 0.4 + 0.1

    matrix = sparse.csr_matrix(dense.astype(np.float32))
    matrix.sort_indices()
    rows = np.asarray(abs(matrix).sum(axis=1)).ravel()
    matrix = (sparse.diags((1.0 / (1e-8 + rows)).astype(np.float32)) @ matrix).tocsr()
    matrix.sort_indices()
    matrix.eliminate_zeros()
    matrix.data = np.array(matrix.data, dtype=np.float32, copy=True)

    network = ScipyRateNetwork(
        matrix,
        RateParameters(internal_steps=4, leak=0.3, recurrent_gain=0.9),
        copy_connectivity=False,
        allow_plasticity=True,
    )
    body = MushroomBody(
        network.connectivity,
        resolve_mushroom_body(network.connectivity, kenyon_cells=kc, mbons=mbon, dopaminergic=dan),
        MushroomBodyParameters(learning_rate=learning_rate, decay=0.0),
    )
    return ConnectomePolicy(
        loop.FakeGameAction,
        network=network,
        projection=build_sensory_projection(
            np.arange(loop.SENSORY, dtype=np.int64),
            nodes,
            seed=0,
            options=ProjectionOptions(connections_per_neuron=32),
        ),
        readout=DescendingTrace(readout, nodes),
        action_map=LiteralActionMap(loop.READOUT),
        coordinate_head=CoordinateHead(loop.READOUT),
        internal_steps=4,
        standardizer=AdaptiveStandardizer(loop.READOUT),
        state_policy=StatePolicy(),
        mushroom_body=body,
        reward_source=reward_source,
    ), loop


def test_plasticity_changes_the_action_sequence() -> None:
    """If learning never reaches behaviour, the circuit is decorative."""

    plastic, loop = _plastic_policy(learning_rate=5.0)
    frozen, _ = _plastic_policy(learning_rate=0.0)
    frames = [loop._frame(step) for step in range(16)]

    assert [plastic.choose_action(f).value for f in frames] != [
        frozen.choose_action(f).value for f in frames
    ]
    assert plastic.plasticity_records
    assert any(r["absolute_change"] > 0 for r in plastic.plasticity_records)


def test_zero_reward_means_no_weight_change_in_the_closed_loop() -> None:
    """The dense reward is observation change; identical frames earn nothing."""

    policy, loop = _plastic_policy(learning_rate=5.0)
    same = loop._frame(4)
    for _ in range(6):
        policy.choose_action(same)
    # After the first turn the frame stops changing, so reward falls to zero.
    assert policy.plasticity_records[-1]["reward"] == 0.0
    assert policy.plasticity_records[-1]["absolute_change"] == 0.0


def test_reset_restores_the_baseline_graph_in_the_closed_loop() -> None:
    policy, loop = _plastic_policy(learning_rate=5.0)
    baseline = policy._network.connectivity.data.copy()
    for step in range(8):
        policy.choose_action(loop._frame(step))
    assert not np.array_equal(policy._network.connectivity.data, baseline)
    policy.reset_state()
    assert np.array_equal(policy._network.connectivity.data, baseline)


def test_plasticity_is_reported_in_the_interface_description() -> None:
    policy, _ = _plastic_policy()
    described = policy.describe()["plasticity"]
    assert described["site"] == "Kenyon cell -> MBON"
    assert described["rest_of_graph_frozen"] is True
    assert described["reward_source"] == "observation_change"


def test_the_rule_works_at_connectome_activity_scale() -> None:
    """Regression: real activity is ~1e-6 and real weights ~1e-3.

    Written in raw units the update lands near 1e-18, rounds to zero in float32,
    and a full episode moves no weight at all. That is exactly what happened on
    the real graph before the rule was made scale-free.
    """

    matrix = _graph()
    body = MushroomBody(
        matrix, _anatomy(matrix), MushroomBodyParameters(learning_rate=0.05, decay=0.0)
    )
    tiny = np.zeros(NODES, dtype=np.float32)
    generator = np.random.default_rng(5)
    tiny[KC] = (generator.random(len(KC)) * 1e-6).astype(np.float32)
    tiny[DAN] = (generator.random(len(DAN)) * 1e-6).astype(np.float32)

    report = body.update(matrix, tiny, reward=0.02)
    assert report["absolute_change"] > 0.0


def test_learning_is_invariant_to_the_activity_scale() -> None:
    """A thousandfold change in activity must not change what is learned."""

    generator = np.random.default_rng(6)
    base = np.zeros(NODES, dtype=np.float32)
    base[KC] = generator.random(len(KC)).astype(np.float32)
    base[DAN] = generator.random(len(DAN)).astype(np.float32)

    changes = []
    for scale in (1.0, 1e-3, 1e-6):
        matrix = _graph()
        body = MushroomBody(
            matrix, _anatomy(matrix), MushroomBodyParameters(learning_rate=0.1, decay=0.0)
        )
        body.update(matrix, (base * scale).astype(np.float32), reward=1.0)
        changes.append(matrix[np.ix_(MBON, KC)].toarray())

    assert np.allclose(changes[0], changes[1], rtol=1e-4, atol=1e-9)
    assert np.allclose(changes[0], changes[2], rtol=1e-4, atol=1e-9)


def test_reward_magnitude_still_matters_after_normalization() -> None:
    """Normalizing the spatial pattern must not normalize away the reward."""

    deltas = []
    for reward in (0.1, 1.0):
        matrix = _graph()
        body = MushroomBody(
            matrix, _anatomy(matrix), MushroomBodyParameters(learning_rate=0.1, decay=0.0)
        )
        before = matrix[np.ix_(MBON, KC)].toarray().copy()
        body.update(matrix, _state(), reward=reward)
        deltas.append(float(np.abs(matrix[np.ix_(MBON, KC)].toarray() - before).sum()))

    assert deltas[1] > deltas[0] * 5
