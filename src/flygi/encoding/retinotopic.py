"""Retinotopic injection of the ARC grid into the optic lobe.

The sparse projection this replaces sends the 64x64 grid through a random matrix
into a declared sensory set. That is fair across graph conditions, and it is
also the single largest unfairness in the interface: it destroys retinotopy.
Two neighbouring ARC cells land on unrelated neurons, so every spatial relation
the optic lobe is built to compute is gone before the graph sees anything.

This encoder preserves it. The ARC grid is mapped onto the fly's own columnar
lattice by a fixed affine assignment, so cells that are adjacent on the screen
drive columns that are adjacent in the eye.

Where it injects, and why not photoreceptors. Measured in MaleCNS v1.0,
``ol_sensory`` neurons carry **no** column assignment -- 0 of 6,098 -- so they
cannot be targeted retinotopically at all. The coordinates live on 23,720
``ol_intrinsic`` neurons over 892 occupied columns of a 36x39 lattice: L1, L2,
L3, L5, Mi1, Mi4, Mi9, T1, C2, C3 and relatives. Those are the lamina and
medulla interneurons that carry the visual signal one synapse downstream of the
photoreceptors, and they are the only population the data lets us address
spatially.

Channel assignment is a **declared heuristic, not a fact**. In the fly, L1 and
L2 head the ON and OFF pathways and T1/C2/C3 are associated with temporal
change. Luminance is therefore injected with positive sign to the declared ON
types, negative sign to the declared OFF types, and the changed-cell signal goes
to the declared change types. Everything else receives luminance. The mapping
lives in configuration so it can be varied and ablated rather than assumed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .features import (
    CHANGE_DIMENSION,
    COLOR_COUNT,
    GRID_SIZE,
    ONE_HOT_DIMENSION,
    ObservationFeatures,
)

# Declared, overridable channel assignment. Not a claim about physiology.
DEFAULT_ON_TYPES = ("L1", "Mi1", "Mi4", "Tm3")
DEFAULT_OFF_TYPES = ("L2", "L3", "Tm1", "Tm2", "Tm4", "Tm9")
DEFAULT_CHANGE_TYPES = ("T1", "C2", "C3", "L5", "Mi9")


class RetinotopyError(ValueError):
    """Raised when the retinotopic asset or its configuration is unusable."""


@dataclass(frozen=True)
class RetinotopicOptions:
    """Declared, recorded choices that change the retinotopic injection."""

    input_scale: float = 1.0
    on_types: tuple[str, ...] = DEFAULT_ON_TYPES
    off_types: tuple[str, ...] = DEFAULT_OFF_TYPES
    change_types: tuple[str, ...] = DEFAULT_CHANGE_TYPES
    change_gain: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not np.isfinite(self.input_scale) or self.input_scale <= 0:
            raise RetinotopyError("input_scale must be finite and positive")
        if not np.isfinite(self.change_gain) or self.change_gain < 0:
            raise RetinotopyError("change_gain must be finite and non-negative")
        overlap = set(self.on_types) & set(self.off_types)
        if overlap:
            raise RetinotopyError(f"a type cannot be both ON and OFF: {sorted(overlap)}")


def load_retinotopy(runtime_dir: str | Path) -> dict[str, NDArray[Any]]:
    """Load the compiled column map written by ``scripts/build_retinotopy.py``."""

    path = Path(runtime_dir) / "retinotopy.npz"
    if not path.is_file():
        raise RetinotopyError(
            f"{path} is missing; build it with scripts/build_retinotopy.py before "
            "using the retinotopic encoder"
        )
    with np.load(path, allow_pickle=False) as archive:
        required = ("node_indices", "hex1", "hex2", "type")
        missing = [name for name in required if name not in archive]
        if missing:
            raise RetinotopyError(f"{path} is missing arrays: {missing}")
        return {name: np.asarray(archive[name]) for name in (*required, "superclass")}


class RetinotopicProjection:
    """Map the ARC grid onto the optic-lobe column lattice, preserving adjacency."""

    def __init__(
        self,
        columns: dict[str, NDArray[Any]],
        node_count: int,
        *,
        options: RetinotopicOptions | None = None,
    ) -> None:
        settings = options or RetinotopicOptions()
        indices = np.asarray(columns["node_indices"], dtype=np.int64)
        hex1 = np.asarray(columns["hex1"], dtype=np.int64)
        hex2 = np.asarray(columns["hex2"], dtype=np.int64)
        types = np.asarray(columns["type"]).astype(str)
        if indices.size == 0:
            raise RetinotopyError("retinotopic map is empty")
        if indices.min() < 0 or indices.max() >= node_count:
            raise RetinotopyError("retinotopic map addresses a node outside the graph")

        self._node_count = int(node_count)
        self._indices = indices
        self._options = settings

        # Fixed affine mapping from ARC cells to columns. Adjacent cells land on
        # adjacent columns, which is the entire point of this encoder.
        span1 = max(int(hex1.max()) - int(hex1.min()), 1)
        span2 = max(int(hex2.max()) - int(hex2.min()), 1)
        self._hex1_min, self._hex2_min = int(hex1.min()), int(hex2.min())
        self._span1, self._span2 = span1, span2

        column_key = (hex1 - self._hex1_min) * (span2 + 1) + (hex2 - self._hex2_min)
        self._column_key = column_key
        self._column_count = int((span1 + 1) * (span2 + 1))

        on = np.isin(types, settings.on_types)
        off = np.isin(types, settings.off_types)
        change = np.isin(types, settings.change_types)
        sign = np.where(off, -1.0, 1.0).astype(np.float32)
        sign[change] = 0.0  # change types carry the change channel, not luminance
        self._luminance_sign = sign
        self._change_mask = change.astype(np.float32)
        self._counts = {
            "on": int(on.sum()),
            "off": int(off.sum()),
            "change": int(change.sum()),
            "other": int((~on & ~off & ~change).sum()),
        }

        # Precompute, for each ARC cell, which column it drives.
        rows = np.arange(GRID_SIZE)
        cell_hex1 = np.rint(rows / (GRID_SIZE - 1) * span1).astype(np.int64)
        cell_hex2 = np.rint(rows / (GRID_SIZE - 1) * span2).astype(np.int64)
        self._cell_column = (cell_hex1[:, None] * (span2 + 1) + cell_hex2[None, :]).ravel()

    @property
    def sensory_indices(self) -> NDArray[np.int64]:
        return self._indices

    @property
    def sensory_size(self) -> int:
        return len(self._indices)

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "retinotopic_optic_lobe",
            "neurons": self.sensory_size,
            "lattice": [self._span1 + 1, self._span2 + 1],
            "occupied_columns": len(np.unique(self._column_key)),
            "channel_counts": dict(self._counts),
            "on_types": list(self._options.on_types),
            "off_types": list(self._options.off_types),
            "change_types": list(self._options.change_types),
            "channel_assignment": "declared heuristic, not a physiological claim",
            "input_scale": self._options.input_scale,
            "change_gain": self._options.change_gain,
            "preserves_retinotopy": True,
            "trainable": False,
            "trainable_parameters": 0,
        }

    def _column_means(self, values: NDArray[np.float32]) -> NDArray[np.float32]:
        """Average an ARC-cell field into the column lattice."""

        totals = np.bincount(
            self._cell_column, weights=values.ravel(), minlength=self._column_count
        )
        counts = np.bincount(self._cell_column, minlength=self._column_count)
        with np.errstate(invalid="ignore", divide="ignore"):
            means = np.where(counts > 0, totals / np.maximum(counts, 1), 0.0)
        return means.astype(np.float32)

    def drive_features(self, features: ObservationFeatures) -> NDArray[np.float32]:
        """Build the graph-space drive for one turn from the grid itself."""

        grid = np.asarray(features.grid, dtype=np.float32)
        if grid.shape != (GRID_SIZE, GRID_SIZE):
            raise RetinotopyError(f"expected a {GRID_SIZE}x{GRID_SIZE} grid, got {grid.shape}")
        # Normalize colour index to [0, 1]; ARC values are categorical, so this
        # is a declared ordering choice, recorded rather than implied.
        luminance = grid / float(COLOR_COUNT - 1)
        changed = np.asarray(
            features.vector[ONE_HOT_DIMENSION : ONE_HOT_DIMENSION + CHANGE_DIMENSION],
            dtype=np.float32,
        ).reshape(GRID_SIZE, GRID_SIZE)

        luminance_columns = self._column_means(luminance)
        change_columns = self._column_means(changed)

        per_neuron = luminance_columns[self._column_key] * self._luminance_sign + change_columns[
            self._column_key
        ] * self._change_mask * np.float32(self._options.change_gain)
        drive = np.zeros(self._node_count, dtype=np.float32)
        np.add.at(drive, self._indices, per_neuron.astype(np.float32))
        drive *= np.float32(self._options.input_scale)
        if not np.isfinite(drive).all():
            raise RetinotopyError("retinotopic drive became non-finite")
        return drive


def build_retinotopic_projection(
    runtime_dir: str | Path,
    node_count: int,
    *,
    options: RetinotopicOptions | None = None,
) -> RetinotopicProjection:
    """Load the compiled column map and build the projection."""

    return RetinotopicProjection(load_retinotopy(runtime_dir), node_count, options=options)
