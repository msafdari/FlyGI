"""Fixed, nonlearned ARC observation features.

Every quantity here is computed from what the ARC protocol already gives an
agent: the current frame, the previous frame, the previous action, and the
legal-action mask. Nothing derived from ``levels_completed``, hidden scoring
state, the game id, or any per-game rule enters the primary neutral condition.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

GRID_SIZE = 64
COLOR_COUNT = 16
ACTION_SLOTS = 8

ONE_HOT_DIMENSION = GRID_SIZE * GRID_SIZE * COLOR_COUNT
CHANGE_DIMENSION = GRID_SIZE * GRID_SIZE
FEATURE_DIMENSION = ONE_HOT_DIMENSION + CHANGE_DIMENSION + 2 * ACTION_SLOTS


class FeatureError(ValueError):
    """Raised when an ARC frame cannot be turned into declared features."""


def latest_grid(frame: Any) -> NDArray[np.int8]:
    """Extract the most recent 64x64 grid from an ARC frame.

    ``FrameData.frame`` is a list of sub-frames for one turn. The last entry is
    the state the agent is acting on.
    """

    raw = getattr(frame, "frame", frame)
    if raw is None:
        raise FeatureError("ARC frame carries no grid data")
    array = np.asarray(raw)
    if array.ndim == 3:
        if array.shape[0] == 0:
            raise FeatureError("ARC frame contained an empty sub-frame list")
        array = array[-1]
    if array.ndim != 2:
        raise FeatureError(f"expected a 2-D ARC grid, observed shape {array.shape}")
    if array.shape != (GRID_SIZE, GRID_SIZE):
        raise FeatureError(f"expected a {GRID_SIZE}x{GRID_SIZE} ARC grid, observed {array.shape}")
    values = array.astype(np.int16, copy=False)
    if values.size and (values.min() < 0 or values.max() >= COLOR_COUNT):
        raise FeatureError(
            f"ARC cell values must lie in [0, {COLOR_COUNT - 1}], observed "
            f"[{int(values.min())}, {int(values.max())}]"
        )
    return values.astype(np.int8, copy=False)


@dataclass(frozen=True, slots=True)
class ObservationFeatures:
    """One turn's fixed feature vector plus the grid it was built from."""

    vector: NDArray[np.float32]
    grid: NDArray[np.int8]
    changed_cells: int

    def __post_init__(self) -> None:
        if self.vector.shape != (FEATURE_DIMENSION,):
            raise FeatureError(
                f"feature vector must have shape ({FEATURE_DIMENSION},), "
                f"observed {self.vector.shape}"
            )


def encode_observation(
    frame: Any,
    *,
    previous_grid: NDArray[np.int8] | None,
    previous_action_id: int | None,
    available_action_ids: tuple[int, ...] | list[int],
) -> ObservationFeatures:
    """Build the declared neutral feature vector for one ARC turn.

    Layout, in order:

    1. ``64 * 64 * 16`` one-hot encoding of the current frame;
    2. ``64 * 64`` binary mask of cells that changed since the previous frame;
    3. ``8`` one-hot of the previous action;
    4. ``8`` legal-action mask.
    """

    grid = latest_grid(frame)
    vector = np.zeros(FEATURE_DIMENSION, dtype=np.float32)

    flat = grid.astype(np.int64, copy=False).ravel()
    cell_offsets = np.arange(CHANGE_DIMENSION, dtype=np.int64) * COLOR_COUNT
    vector[cell_offsets + flat] = 1.0

    change_base = ONE_HOT_DIMENSION
    if previous_grid is None:
        changed_cells = 0
    else:
        if previous_grid.shape != grid.shape:
            raise FeatureError("previous grid shape does not match the current grid")
        changed = (previous_grid != grid).ravel()
        vector[change_base : change_base + CHANGE_DIMENSION] = changed.astype(np.float32)
        changed_cells = int(np.count_nonzero(changed))

    action_base = change_base + CHANGE_DIMENSION
    if previous_action_id is not None:
        if not 0 <= int(previous_action_id) < ACTION_SLOTS:
            raise FeatureError(
                f"previous action id must lie in [0, {ACTION_SLOTS - 1}], "
                f"observed {previous_action_id}"
            )
        vector[action_base + int(previous_action_id)] = 1.0

    mask_base = action_base + ACTION_SLOTS
    for identifier in available_action_ids:
        index = int(identifier)
        if not 0 <= index < ACTION_SLOTS:
            raise FeatureError(f"legal action id outside [0, {ACTION_SLOTS - 1}]: {index}")
        vector[mask_base + index] = 1.0

    return ObservationFeatures(vector=vector, grid=grid, changed_cells=changed_cells)
