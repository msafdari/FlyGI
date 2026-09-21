"""Shared interfaces for persistent neural-dynamics backends."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray

FloatState = NDArray[np.float32]


@runtime_checkable
class DynamicsBackend(Protocol):
    """Minimal contract shared by CPU and future accelerator backends.

    :meth:`step` runs exactly one neural update. :meth:`advance` holds one input
    current fixed for multiple internal steps of an external agent decision.
    Implementations return a new state and do not mutate caller arrays.
    """

    @property
    def backend_name(self) -> str:
        """Stable backend identifier written to experiment provenance."""

    @property
    def node_count(self) -> int:
        """Number of neurons in the persistent state vector."""

    @property
    def dtype(self) -> np.dtype[np.float32]:
        """State and connectivity dtype."""

    def initial_state(self, *, seed: int | None = None, scale: float = 0.0) -> FloatState:
        """Return a deterministic initial state."""

    def step(
        self,
        state: NDArray[np.floating],
        input_current: NDArray[np.floating] | None = None,
    ) -> FloatState:
        """Advance a persistent state by exactly one internal update."""

    def advance(
        self,
        state: NDArray[np.floating],
        input_current: NDArray[np.floating] | None = None,
        *,
        internal_steps: int | None = None,
    ) -> FloatState:
        """Advance a persistent state through one external decision."""


class DynamicsValidationError(ValueError):
    """Raised when a dynamics parameter, state, or input violates its contract."""
