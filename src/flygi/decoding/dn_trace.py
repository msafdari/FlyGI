"""Descending-neuron readout and its required standardization.

A measured fact drives this module. On the real graph, settled descending-neuron
activity has a mean absolute value of order ``1e-6`` while network-wide activity
is of order ``1e-2``. An unstandardized linear readout of those values is
dominated by its own bias, so every decoder standardizes the trace first.

Standardization is across the descending population within a single turn. It
introduces no trainable parameter and no additional persistent state, so it
cannot smuggle learning into the literal condition.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

EPSILON = np.float32(1e-12)


class ReadoutError(ValueError):
    """Raised when a readout population or trace violates its contract."""


@dataclass(frozen=True, slots=True)
class ReadoutDiagnostics:
    """Per-turn health of the readout, recorded for zero-score analysis."""

    mean_abs: float
    max_abs: float
    standard_deviation: float
    silent: bool
    saturated_fraction: float


class DescendingTrace:
    """Read a fixed descending-neuron population and standardize it."""

    def __init__(self, indices: NDArray[np.integer], node_count: int) -> None:
        selected = np.asarray(indices, dtype=np.int64)
        if selected.ndim != 1 or selected.size == 0:
            raise ReadoutError("readout population must be a nonempty 1-D index array")
        if selected.min() < 0 or selected.max() >= node_count:
            raise ReadoutError("readout index lies outside the neural state")
        if len(np.unique(selected)) != len(selected):
            raise ReadoutError("readout indices must be unique")
        if np.any(selected[1:] <= selected[:-1]):
            raise ReadoutError("readout indices must be strictly increasing")
        selected.flags.writeable = False
        self._indices = selected
        self._node_count = int(node_count)

    @property
    def indices(self) -> NDArray[np.int64]:
        return self._indices

    @property
    def size(self) -> int:
        return len(self._indices)

    def raw(self, state: NDArray[np.float32]) -> NDArray[np.float32]:
        vector = np.asarray(state)
        if vector.shape != (self._node_count,):
            raise ReadoutError(
                f"state must have shape ({self._node_count},), observed {vector.shape}"
            )
        return vector[self._indices].astype(np.float32, copy=True)

    def standardized(
        self, state: NDArray[np.float32]
    ) -> tuple[NDArray[np.float32], ReadoutDiagnostics]:
        """Return the z-scored descending trace and its diagnostics.

        A population with no variation yields an all-zero trace rather than a
        division by a near-zero standard deviation. That case is reported as
        ``silent`` so a degenerate agent is visible in the results instead of
        being hidden behind amplified numerical noise.
        """

        values = self.raw(state)
        if not np.isfinite(values).all():
            raise ReadoutError("descending trace contains NaN or infinity")

        magnitude = np.abs(values)
        deviation = float(values.std())
        silent = deviation <= float(EPSILON)
        if silent:
            standardized = np.zeros_like(values)
        else:
            standardized = (values - np.float32(values.mean())) / np.float32(deviation)
            standardized = standardized.astype(np.float32, copy=False)

        diagnostics = ReadoutDiagnostics(
            mean_abs=float(magnitude.mean()),
            max_abs=float(magnitude.max()),
            standard_deviation=deviation,
            silent=silent,
            saturated_fraction=float(np.count_nonzero(magnitude >= 0.99) / len(values)),
        )
        return standardized, diagnostics


def contiguous_groups(size: int, count: int) -> list[NDArray[np.int64]]:
    """Split ``range(size)`` into ``count`` contiguous, near-equal blocks.

    The literal decoder uses these blocks to assign descending neurons to
    actions. Because the readout population is stored in ascending body-ID
    order, the partition is fully determined by the dataset: it involves no
    seed, no tuning, and no per-game choice.
    """

    if size <= 0:
        raise ReadoutError("group partition requires a positive size")
    if count <= 0 or count > size:
        raise ReadoutError(f"cannot split {size} readout neurons into {count} groups")
    return [np.asarray(block, dtype=np.int64) for block in np.array_split(np.arange(size), count)]
