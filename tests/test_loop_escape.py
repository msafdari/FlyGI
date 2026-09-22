"""Unit contracts for state-conditioned loop-escape memory."""

from __future__ import annotations

import numpy as np
import pytest

from flygi.decoding.loop_escape import (
    LoopEscapeError,
    LoopEscapeMemory,
    LoopEscapeParameters,
)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"enabled": "yes"}, "enabled must be a boolean"),
        ({"exploration_bonus": True}, "exploration_bonus must be numeric"),
        ({"exploration_bonus": -0.1}, "finite and non-negative"),
        ({"unchanged_failure_penalty": float("nan")}, "finite and non-negative"),
        ({"enabled": True, "exploration_bonus": 0.0}, "positive exploration_bonus"),
        ({"state_hash": "python_hash"}, "unsupported state_hash"),
        ({"coordinate_memory": "global"}, "unsupported coordinate_memory"),
    ],
)
def test_parameters_fail_closed(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(LoopEscapeError, match=message):
        LoopEscapeParameters(**kwargs)  # type: ignore[arg-type]


def test_observation_key_is_stable_and_state_sensitive() -> None:
    first = np.zeros((64, 64), dtype=np.int8)
    second = np.array(first, copy=True)
    second[2, 3] = 1

    assert LoopEscapeMemory.observation_key(first) == LoopEscapeMemory.observation_key(
        first.astype(np.int16)
    )
    assert LoopEscapeMemory.observation_key(first) != LoopEscapeMemory.observation_key(second)
    assert len(LoopEscapeMemory.observation_key(first)) == 16


def test_only_an_unchanged_observation_records_a_failure() -> None:
    memory = LoopEscapeMemory(
        LoopEscapeParameters(
            enabled=True,
            exploration_bonus=0.5,
            unchanged_failure_penalty=1.0,
        )
    )
    first = np.zeros((64, 64), dtype=np.int8)
    changed = np.ones((64, 64), dtype=np.int8)
    key = memory.observe(first)

    initial = memory.standardized_bias(key, [1, 2], action_slots=8)
    assert initial[1] == initial[2] == 0.5
    memory.record_choice(key, 1)
    assert memory.observe(first) == key
    assert memory.counts(key, 1) == (1, 1)
    after_failure = memory.standardized_bias(key, [1, 2], action_slots=8)
    assert after_failure[1] == pytest.approx(0.5 / np.sqrt(2.0) - 1.0)
    assert after_failure[2] == 0.5

    memory.record_choice(key, 2)
    memory.observe(changed)
    assert memory.counts(key, 2) == (1, 0)


def test_failed_clicks_are_scoped_to_the_observation_and_reset() -> None:
    memory = LoopEscapeMemory(LoopEscapeParameters(enabled=True, exploration_bonus=0.5))
    first = np.zeros((64, 64), dtype=np.int8)
    second = np.ones((64, 64), dtype=np.int8)
    first_key = memory.observe(first)
    memory.record_choice(first_key, 6, coordinate=(3, 4))
    memory.observe(first)
    assert memory.failed_click_coordinates(first_key) == {(3, 4)}

    memory.record_choice(first_key, 6, coordinate=(5, 6))
    second_key = memory.observe(second)
    assert memory.failed_click_coordinates(first_key) == {(3, 4)}
    assert memory.failed_click_coordinates(second_key) == set()

    memory.reset()
    assert memory.failed_click_coordinates(first_key) == set()
    assert memory.counts(first_key, 6) == (0, 0)
