"""Deterministic SciPy backend for the FlyGI leaky rate network."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from .base import DynamicsValidationError, FloatState

_NUMERIC_SCALARS = (int, float, np.integer, np.floating)
_FLOAT32_MAX = float(np.finfo(np.float32).max)


def _effective_float32(name: str, value: object) -> np.float32:
    if isinstance(value, bool) or not isinstance(value, _NUMERIC_SCALARS):
        raise DynamicsValidationError(f"{name} must be numeric and not boolean")
    numeric = float(value)
    if not math.isfinite(numeric) or abs(numeric) > _FLOAT32_MAX:
        raise DynamicsValidationError(f"{name} must be finite and representable as float32")
    effective = np.float32(numeric)
    if numeric != 0.0 and effective == 0.0:
        raise DynamicsValidationError(f"{name} underflows to zero in float32")
    return effective


@dataclass(frozen=True)
class RateParameters:
    """Declared parameters for the leaky rate update.

    The update is ``h <- (1-a) h + a tanh(g W h + input + bias)``. The
    connectivity matrix uses the repository-wide ``W[post, pre]`` convention.
    """

    internal_steps: int = 2
    leak: float = 0.3
    recurrent_gain: float = 0.9
    bias: float = 0.0

    def __post_init__(self) -> None:
        if (
            isinstance(self.internal_steps, bool)
            or not isinstance(self.internal_steps, (int, np.integer))
            or self.internal_steps <= 0
        ):
            raise DynamicsValidationError("internal_steps must be a positive integer")
        leak = _effective_float32("leak", self.leak)
        recurrent_gain = _effective_float32("recurrent_gain", self.recurrent_gain)
        _effective_float32("bias", self.bias)
        if not 0.0 < leak <= 1.0:
            raise DynamicsValidationError("leak must be finite and in (0, 1]")
        if recurrent_gain < 0.0:
            raise DynamicsValidationError("recurrent_gain must be finite and non-negative")


class ScipyRateNetwork:
    """CPU reference implementation of the frozen sparse rate network.

    The graph remains CSR throughout. Its three storage arrays are marked
    read-only after construction so an experiment cannot silently modify the
    connectome weights in place.
    """

    def __init__(
        self,
        connectivity: sparse.spmatrix,
        parameters: RateParameters | None = None,
        *,
        copy_connectivity: bool = True,
    ) -> None:
        if not sparse.isspmatrix_csr(connectivity):
            raise TypeError("connectivity must be a SciPy CSR matrix")
        if connectivity.ndim != 2 or connectivity.shape[0] != connectivity.shape[1]:
            raise DynamicsValidationError("connectivity must be a square matrix")
        if connectivity.shape[0] == 0:
            raise DynamicsValidationError("connectivity must contain at least one neuron")
        if connectivity.dtype != np.float32:
            raise DynamicsValidationError("connectivity dtype must be float32")
        if not connectivity.has_canonical_format or not connectivity.has_sorted_indices:
            raise DynamicsValidationError("connectivity must be canonical CSR with sorted indices")
        if np.count_nonzero(connectivity.data == 0.0):
            raise DynamicsValidationError("connectivity must not store explicit zero weights")

        matrix = connectivity.copy() if copy_connectivity else connectivity
        if not np.isfinite(matrix.data).all():
            raise DynamicsValidationError("connectivity contains NaN or infinity")
        matrix.data.flags.writeable = False
        matrix.indices.flags.writeable = False
        matrix.indptr.flags.writeable = False

        self._connectivity = matrix
        self._parameters = parameters or RateParameters()
        self._zero_input = np.zeros(matrix.shape[0], dtype=np.float32)
        self._zero_input.flags.writeable = False

    @property
    def backend_name(self) -> str:
        return "scipy-csr-cpu"

    @property
    def node_count(self) -> int:
        return int(self._connectivity.shape[0])

    @property
    def dtype(self) -> np.dtype[np.float32]:
        return np.dtype(np.float32)

    @property
    def parameters(self) -> RateParameters:
        return self._parameters

    @property
    def connectivity(self) -> sparse.csr_matrix:
        """Return the frozen CSR matrix for inspection and provenance."""

        return self._connectivity

    def initial_state(self, *, seed: int | None = None, scale: float = 0.0) -> FloatState:
        """Create zeros or a reproducible bounded uniform state.

        Literal FlyGI uses the default all-zero state. A nonzero ``scale`` is
        useful for diagnostics and requires an explicit seed; values are drawn
        uniformly from ``[-scale, scale]``.
        """

        if not np.isfinite(scale) or not 0.0 <= scale <= 1.0:
            raise DynamicsValidationError("initial-state scale must be finite and in [0, 1]")
        if scale == 0.0:
            return np.zeros(self.node_count, dtype=np.float32)
        if seed is None:
            raise DynamicsValidationError("a seed is required for nonzero initialization")
        generator = np.random.default_rng(seed)
        return generator.uniform(-scale, scale, size=self.node_count).astype(np.float32)

    def _vector(
        self,
        value: NDArray[np.floating],
        *,
        name: str,
        copy: bool,
    ) -> FloatState:
        array = np.asarray(value)
        if array.shape != (self.node_count,):
            raise DynamicsValidationError(
                f"{name} must have shape ({self.node_count},), observed {array.shape}"
            )
        if array.dtype != np.float32:
            raise DynamicsValidationError(f"{name} dtype must be float32")
        result = array.copy() if copy else array
        if not np.isfinite(result).all():
            raise DynamicsValidationError(f"{name} contains NaN or infinity")
        return result

    def step(
        self,
        state: NDArray[np.floating],
        input_current: NDArray[np.floating] | None = None,
    ) -> FloatState:
        """Run exactly one internal update without mutating caller arrays."""

        return self.advance(state, input_current, internal_steps=1)

    def advance(
        self,
        state: NDArray[np.floating],
        input_current: NDArray[np.floating] | None = None,
        *,
        internal_steps: int | None = None,
    ) -> FloatState:
        """Hold one input fixed for the configured number of internal steps."""

        steps = self._parameters.internal_steps if internal_steps is None else internal_steps
        if isinstance(steps, bool) or not isinstance(steps, (int, np.integer)) or steps <= 0:
            raise DynamicsValidationError("internal_steps must be a positive integer")

        current = self._vector(state, name="state", copy=True)
        injected = (
            self._zero_input
            if input_current is None
            else self._vector(input_current, name="input_current", copy=False)
        )
        leak = np.float32(self._parameters.leak)
        retain = np.float32(1.0 - self._parameters.leak)
        gain = np.float32(self._parameters.recurrent_gain)
        bias = np.float32(self._parameters.bias)

        for _ in range(int(steps)):
            activated = np.asarray(self._connectivity @ current, dtype=np.float32)
            activated *= gain
            activated += injected
            if bias != 0.0:
                activated += bias
            if not np.isfinite(activated).all():
                raise FloatingPointError("rate-network drive became non-finite")
            np.tanh(activated, out=activated)
            activated *= leak
            current *= retain
            current += activated
            if not np.isfinite(current).all():
                raise FloatingPointError("rate-network state became non-finite")
        return current

    def readout(
        self,
        state: NDArray[np.floating],
        indices: NDArray[np.integer],
    ) -> FloatState:
        """Copy a validated subset of a state, such as descending neurons."""

        current = self._vector(state, name="state", copy=False)
        selected = np.asarray(indices)
        if selected.ndim != 1 or not np.issubdtype(selected.dtype, np.integer):
            raise DynamicsValidationError("readout indices must be a one-dimensional integer array")
        if len(selected) and ((selected < 0).any() or (selected >= self.node_count).any()):
            raise DynamicsValidationError("readout index is outside the neural state")
        return current[selected.astype(np.int64, copy=False)].copy()
