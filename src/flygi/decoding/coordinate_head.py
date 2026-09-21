"""Fixed, seeded coordinate decisions for the ARC ``ACTION6`` click action.

The connectome head remains factorized: descending activity produces one set of
64 logits for ``x`` and another for ``y``. Each axis is sampled with the same
scale-aware categorical rule as the action head. Two spatially grounded rules
can override that raw proposal without adding learned parameters:

* the centroid of cells that changed since the previous observation; and
* a seeded, not-yet-clicked grid cell after a click yields no change.

All three routes are game-agnostic, bounded to the ARC grid, and consume the
single policy-owned NumPy generator.
"""

from __future__ import annotations

from collections.abc import Set
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .dn_trace import ReadoutError, contiguous_groups
from .literal import SAMPLING_METHOD, _validate_temperature, scale_aware_probabilities

GRID_MIN = 0
GRID_MAX = 63
GRID_BINS = GRID_MAX - GRID_MIN + 1
GRID_CELLS = GRID_BINS * GRID_BINS


@dataclass(frozen=True, slots=True)
class CoordinateDecision:
    """One bounded click plus the factorized proposal that preceded it."""

    x: int
    y: int
    method: str
    proposed_x: int
    proposed_y: int
    x_selected_probability: float
    y_selected_probability: float
    x_entropy_bits: float
    y_entropy_bits: float
    x_logit_scale: float
    y_logit_scale: float


def novelty_centroid(
    previous_grid: NDArray[np.integer] | None,
    current_grid: NDArray[np.integer],
) -> tuple[int, int] | None:
    """Return the rounded centroid of changed cells as ``(x, y)``.

    The first observation has no temporal novelty and returns ``None``. Ties at
    half a cell round upward, making the transform independent of Python's
    banker-rounding behavior.
    """

    current = np.asarray(current_grid)
    if current.shape != (GRID_BINS, GRID_BINS):
        raise ReadoutError(
            f"current grid must have shape ({GRID_BINS}, {GRID_BINS}), observed {current.shape}"
        )
    if previous_grid is None:
        return None
    previous = np.asarray(previous_grid)
    if previous.shape != current.shape:
        raise ReadoutError("previous grid shape does not match current grid")
    changed_y, changed_x = np.nonzero(previous != current)
    if changed_x.size == 0:
        return None
    x = int(np.floor(float(changed_x.mean()) + 0.5))
    y = int(np.floor(float(changed_y.mean()) + 0.5))
    return min(max(x, GRID_MIN), GRID_MAX), min(max(y, GRID_MIN), GRID_MAX)


class CoordinateHead:
    """Map a standardized readout trace to a legal ``(x, y)`` ARC coordinate."""

    def __init__(self, readout_size: int, *, temperature: float = 0.5) -> None:
        if readout_size < 2 * GRID_BINS:
            raise ReadoutError(
                f"coordinate head needs at least {2 * GRID_BINS} readout neurons, "
                f"observed {readout_size}"
            )
        self._readout_size = int(readout_size)
        self._temperature = _validate_temperature(temperature, "coordinate temperature")
        split = readout_size // 2
        self._x_slice = slice(0, split)
        self._y_slice = slice(split, readout_size)
        self._x_bins = contiguous_groups(split, GRID_BINS)
        self._y_bins = contiguous_groups(readout_size - split, GRID_BINS)

    @property
    def readout_size(self) -> int:
        return self._readout_size

    @property
    def temperature(self) -> float:
        return self._temperature

    def describe(self) -> dict[str, object]:
        return {
            "kind": "literal_factorized_bins",
            "bins_per_axis": GRID_BINS,
            "readout_size": self._readout_size,
            "x_neurons": int(self._x_slice.stop - self._x_slice.start),
            "y_neurons": int(self._y_slice.stop - self._y_slice.start),
            "selection": SAMPLING_METHOD,
            "scale": "population standard deviation per coordinate axis",
            "temperature": self._temperature,
            "novelty_fallback": "changed_cell_centroid",
            "unchanged_click_exploration": "seeded_untried_uniform",
            "trainable": False,
            "trainable_parameters": 0,
        }

    @staticmethod
    def _axis_scores(
        values: NDArray[np.float32], bins: list[NDArray[np.int64]]
    ) -> NDArray[np.float32]:
        return np.asarray(
            [float(values[block].mean()) if block.size else 0.0 for block in bins],
            dtype=np.float32,
        )

    @staticmethod
    def _entropy_bits(probabilities: NDArray[np.float64]) -> float:
        positive = probabilities[probabilities > 0.0]
        return float(-np.sum(positive * np.log2(positive)))

    def sample(
        self,
        trace: NDArray[np.float32],
        *,
        rng: np.random.Generator,
        centroid: tuple[int, int] | None = None,
        explore_unchanged_click: bool = False,
        clicked_coordinates: Set[tuple[int, int]] = frozenset(),
    ) -> CoordinateDecision:
        """Sample both axes, then apply the declared grounded fallback if needed."""

        values = np.asarray(trace, dtype=np.float32)
        if values.shape != (self._readout_size,):
            raise ReadoutError(
                f"coordinate head expects shape ({self._readout_size},), observed {values.shape}"
            )
        if not np.isfinite(values).all():
            raise ReadoutError("coordinate head received a non-finite trace")

        x_scores = self._axis_scores(values[self._x_slice], self._x_bins)
        y_scores = self._axis_scores(values[self._y_slice], self._y_bins)
        x_probabilities, x_scale = scale_aware_probabilities(x_scores, self._temperature)
        y_probabilities, y_scale = scale_aware_probabilities(y_scores, self._temperature)
        proposed_x = int(rng.choice(GRID_BINS, p=x_probabilities))
        proposed_y = int(rng.choice(GRID_BINS, p=y_probabilities))

        if explore_unchanged_click:
            x, y = self._seeded_untried_coordinate(rng, clicked_coordinates)
            method = "seeded_untried_uniform"
        elif centroid is not None:
            x, y = self._validate_coordinate(*centroid)
            method = "novelty_centroid"
        else:
            x, y = proposed_x, proposed_y
            method = "factorized_sample"

        x, y = self._validate_coordinate(x, y)
        return CoordinateDecision(
            x=x,
            y=y,
            method=method,
            proposed_x=proposed_x,
            proposed_y=proposed_y,
            x_selected_probability=float(x_probabilities[proposed_x]),
            y_selected_probability=float(y_probabilities[proposed_y]),
            x_entropy_bits=self._entropy_bits(x_probabilities),
            y_entropy_bits=self._entropy_bits(y_probabilities),
            x_logit_scale=x_scale,
            y_logit_scale=y_scale,
        )

    def coordinates(
        self,
        trace: NDArray[np.float32],
        *,
        rng: np.random.Generator | None = None,
    ) -> tuple[int, int]:
        """Compatibility wrapper returning a factorized sampled coordinate.

        Supplying a generator is required by the closed-loop policy. A fixed
        local seed is retained here only for direct diagnostic calls that need a
        side-effect-free coordinate tuple.
        """

        generator = np.random.default_rng(0) if rng is None else rng
        decision = self.sample(trace, rng=generator)
        return decision.x, decision.y

    @staticmethod
    def _seeded_untried_coordinate(
        rng: np.random.Generator,
        clicked_coordinates: Set[tuple[int, int]],
    ) -> tuple[int, int]:
        excluded = np.zeros(GRID_CELLS, dtype=np.bool_)
        for x, y in clicked_coordinates:
            checked_x, checked_y = CoordinateHead._validate_coordinate(x, y)
            excluded[checked_y * GRID_BINS + checked_x] = True
        candidates = np.flatnonzero(~excluded)
        if candidates.size == 0:
            candidates = np.arange(GRID_CELLS, dtype=np.int64)
        selected = int(rng.choice(candidates))
        return selected % GRID_BINS, selected // GRID_BINS

    @staticmethod
    def _validate_coordinate(x: int, y: int) -> tuple[int, int]:
        if isinstance(x, (bool, np.bool_)) or isinstance(y, (bool, np.bool_)):
            raise ReadoutError("coordinates must be integers, not booleans")
        checked_x, checked_y = int(x), int(y)
        if not (GRID_MIN <= checked_x <= GRID_MAX and GRID_MIN <= checked_y <= GRID_MAX):
            raise ReadoutError(f"coordinate head produced out-of-range ({checked_x}, {checked_y})")
        return checked_x, checked_y
