"""Literal coordinate head for the ARC ``ACTION6`` click action.

The head is factorized: one distribution over ``x`` and one over ``y``, each on
``{0, ..., 63}``. The specification recommends this as sufficient for a first
submission, with a pointer head only if factorization proves too restrictive.

The literal rule involves no trainable parameter. The standardized descending
trace is split into two contiguous halves, each half is folded into 64
contiguous bins, and the coordinate is the argmax bin. Ties resolve to the
lowest index so the mapping is deterministic on every backend.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .dn_trace import ReadoutError, contiguous_groups

GRID_MIN = 0
GRID_MAX = 63
GRID_BINS = GRID_MAX - GRID_MIN + 1


class CoordinateHead:
    """Map a standardized readout trace to a legal ``(x, y)`` ARC coordinate."""

    def __init__(self, readout_size: int) -> None:
        if readout_size < 2 * GRID_BINS:
            raise ReadoutError(
                f"coordinate head needs at least {2 * GRID_BINS} readout neurons, "
                f"observed {readout_size}"
            )
        self._readout_size = int(readout_size)
        split = readout_size // 2
        self._x_slice = slice(0, split)
        self._y_slice = slice(split, readout_size)
        self._x_bins = contiguous_groups(split, GRID_BINS)
        self._y_bins = contiguous_groups(readout_size - split, GRID_BINS)

    @property
    def readout_size(self) -> int:
        return self._readout_size

    def describe(self) -> dict[str, object]:
        return {
            "kind": "literal_factorized_bins",
            "bins_per_axis": GRID_BINS,
            "readout_size": self._readout_size,
            "x_neurons": int(self._x_slice.stop - self._x_slice.start),
            "y_neurons": int(self._y_slice.stop - self._y_slice.start),
            "trainable": False,
        }

    @staticmethod
    def _axis_scores(
        values: NDArray[np.float32], bins: list[NDArray[np.int64]]
    ) -> NDArray[np.float32]:
        return np.asarray(
            [float(values[block].mean()) if block.size else 0.0 for block in bins],
            dtype=np.float32,
        )

    def coordinates(self, trace: NDArray[np.float32]) -> tuple[int, int]:
        """Return an integer ``(x, y)`` guaranteed to lie in ``[0, 63]^2``."""

        values = np.asarray(trace, dtype=np.float32)
        if values.shape != (self._readout_size,):
            raise ReadoutError(
                f"coordinate head expects shape ({self._readout_size},), observed {values.shape}"
            )
        if not np.isfinite(values).all():
            raise ReadoutError("coordinate head received a non-finite trace")

        x_scores = self._axis_scores(values[self._x_slice], self._x_bins)
        y_scores = self._axis_scores(values[self._y_slice], self._y_bins)
        x = int(np.argmax(x_scores))
        y = int(np.argmax(y_scores))
        if not (GRID_MIN <= x <= GRID_MAX and GRID_MIN <= y <= GRID_MAX):
            raise ReadoutError(f"coordinate head produced out-of-range ({x}, {y})")
        return x, y
