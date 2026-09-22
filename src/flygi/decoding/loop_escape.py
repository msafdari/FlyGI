"""Finite, state-conditioned exploration memory for the literal policy.

The connectome still supplies every action logit.  This module only remembers
which legal actions were tried from an exact observation and which of those
attempts returned the same observation.  Its output is an additive bias in the
already-standardized logit space, so the strength has the same meaning across
graph conditions without depending on raw readout magnitude.
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

STATE_HASH = "blake2b_128"
COORDINATE_MEMORY = "per_observation"


class LoopEscapeError(ValueError):
    """Raised when loop-escape settings or inputs are invalid."""


@dataclass(frozen=True, slots=True)
class LoopEscapeParameters:
    """Declared nonlearned strengths for state-conditioned loop escape."""

    enabled: bool = False
    exploration_bonus: float = 0.0
    unchanged_failure_penalty: float = 0.0
    state_hash: str = STATE_HASH
    coordinate_memory: str = COORDINATE_MEMORY

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise LoopEscapeError("enabled must be a boolean")
        for name, value in (
            ("exploration_bonus", self.exploration_bonus),
            ("unchanged_failure_penalty", self.unchanged_failure_penalty),
        ):
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise LoopEscapeError(f"{name} must be numeric")
            if not math.isfinite(float(value)) or float(value) < 0.0:
                raise LoopEscapeError(f"{name} must be finite and non-negative")
        if self.enabled and self.exploration_bonus <= 0.0:
            raise LoopEscapeError("enabled loop escape requires a positive exploration_bonus")
        if self.state_hash != STATE_HASH:
            raise LoopEscapeError(f"unsupported state_hash: {self.state_hash}")
        if self.coordinate_memory != COORDINATE_MEMORY:
            raise LoopEscapeError(f"unsupported coordinate_memory: {self.coordinate_memory}")

    def describe(self) -> dict[str, object]:
        return {
            "enabled": self.enabled,
            "exploration_bonus": float(self.exploration_bonus),
            "unchanged_failure_penalty": float(self.unchanged_failure_penalty),
            "state_hash": self.state_hash,
            "coordinate_memory": self.coordinate_memory,
            "trainable": False,
            "trainable_parameters": 0,
        }


class LoopEscapeMemory:
    """Episode-local action and coordinate memory keyed by exact observation."""

    def __init__(self, parameters: LoopEscapeParameters) -> None:
        self.parameters = parameters
        self._attempts: dict[tuple[bytes, int], int] = {}
        self._unchanged_failures: dict[tuple[bytes, int], int] = {}
        self._failed_click_coordinates: dict[bytes, set[tuple[int, int]]] = {}
        self._pending_choice: tuple[bytes, int, tuple[int, int] | None] | None = None
        self.last_choice_failed = False

    @staticmethod
    def observation_key(grid: NDArray[np.integer]) -> bytes:
        """Return a stable 128-bit identity for one exact ARC grid."""

        values = np.asarray(grid)
        if values.ndim != 2 or not np.issubdtype(values.dtype, np.integer):
            raise LoopEscapeError("observation grid must be a two-dimensional integer array")
        canonical = np.ascontiguousarray(values, dtype=np.int8)
        digest = hashlib.blake2b(digest_size=16)
        digest.update(len(canonical.shape).to_bytes(1, "little"))
        for dimension in canonical.shape:
            digest.update(int(dimension).to_bytes(4, "little", signed=False))
        digest.update(canonical.tobytes(order="C"))
        return digest.digest()

    def reset(self) -> None:
        self._attempts.clear()
        self._unchanged_failures.clear()
        self._failed_click_coordinates.clear()
        self._pending_choice = None
        self.last_choice_failed = False

    def observe(self, grid: NDArray[np.integer]) -> bytes:
        """Resolve the prior choice once and return the current observation key."""

        state_key = self.observation_key(grid)
        pending = self._pending_choice
        self.last_choice_failed = pending is not None and pending[0] == state_key
        if self.last_choice_failed:
            assert pending is not None
            choice_key = (pending[0], pending[1])
            self._unchanged_failures[choice_key] = self._unchanged_failures.get(choice_key, 0) + 1
            if pending[2] is not None:
                self._failed_click_coordinates.setdefault(state_key, set()).add(pending[2])
        self._pending_choice = None
        return state_key

    def standardized_bias(
        self,
        state_key: bytes,
        legal_action_ids: tuple[int, ...] | list[int],
        *,
        action_slots: int,
    ) -> NDArray[np.float64]:
        """Return the declared additive bias in standardized-logit units."""

        bias = np.zeros(action_slots, dtype=np.float64)
        if not self.parameters.enabled:
            return bias
        for raw_identifier in dict.fromkeys(legal_action_ids):
            identifier = int(raw_identifier)
            if not 0 <= identifier < action_slots:
                raise LoopEscapeError(
                    f"legal action id {identifier} is outside {action_slots} action slots"
                )
            attempts, failures = self.counts(state_key, identifier)
            bias[identifier] = float(self.parameters.exploration_bonus) / math.sqrt(
                1.0 + attempts
            ) - float(self.parameters.unchanged_failure_penalty) * failures / max(1, attempts)
        return bias

    def counts(self, state_key: bytes, action_id: int) -> tuple[int, int]:
        key = (state_key, int(action_id))
        return self._attempts.get(key, 0), self._unchanged_failures.get(key, 0)

    def count_vectors(self, state_key: bytes, *, action_slots: int) -> tuple[list[int], list[int]]:
        attempts: list[int] = []
        failures: list[int] = []
        for identifier in range(action_slots):
            attempted, unchanged = self.counts(state_key, identifier)
            attempts.append(attempted)
            failures.append(unchanged)
        return attempts, failures

    def record_choice(
        self,
        state_key: bytes,
        action_id: int,
        *,
        coordinate: tuple[int, int] | None = None,
    ) -> None:
        key = (state_key, int(action_id))
        self._attempts[key] = self._attempts.get(key, 0) + 1
        self._pending_choice = (state_key, int(action_id), coordinate)

    def discard_pending_choice(self) -> None:
        """Ensure a protocol-forced reset is never learned as a policy choice."""

        self._pending_choice = None

    def failed_click_coordinates(self, state_key: bytes) -> set[tuple[int, int]]:
        return self._failed_click_coordinates.setdefault(state_key, set())
