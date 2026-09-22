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
