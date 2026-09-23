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


class ColumnarColourProjection:
    """Retinotopic injection that keeps ARC colours categorical.

    ``RetinotopicProjection`` preserves space and destroys colour: it maps the
    sixteen ARC colours onto a scalar ramp (``grid / 15``) and then *averages*
    that ramp within each column. Both steps are wrong for this benchmark. ARC
    colours are categories, not intensities -- colour 3 is not between 2 and 4 --
    and the mean of colour 3 and colour 9 is colour 6, which is a third
    unrelated category. Measured consequence: that encoder scored 0.003156
    against the random projection's 0.190476.

    The random projection has the opposite defect. It keeps colour as a 16-way
    one-hot and destroys space, giving each photoreceptor 64 uniformly random
    features so that neighbouring receptors see unrelated parts of the screen.
    T4/T5 compute motion by comparing *adjacent* columns and LC neurons
    integrate over retinotopic neighbourhoods, so that projection removes the
    one property those circuits exist to exploit.

    This keeps both. Each column receives the colour *histogram* of the ARC
    cells that map to it, and colour ``c`` drives the neurons of medulla type
    index ``c % 15`` within that column.

    Measured facts this design is built on, none of them assumed:

    - Photoreceptors carry no column assignment at all (0 of 6,098), so the
      injection site is the lamina and medulla interneurons: 23,720 neurons over
      892 occupied columns of a 36x39 lattice.
    - A column carries **15** distinct types, not 16: C2, C3, L1, L2, L3, L5,
      Mi1, Mi4, Mi9, T1, Tm1, Tm2, Tm20, Tm4, Tm9. 814 of 892 columns (91.3%)
      carry all fifteen; the remaining 78 lose their highest channels.
    - Sixteen colours into fifteen channels forces exactly one collision, and it
      falls on colours 0 and 15 by the fixed rule ``c % 15``. The collision is
      **not** chosen from measured colour frequencies: tuning the encoder to the
      games it will be scored on would put engineering in the plumbing, which is
      what this project must not do.

    **HYPOTHESIS, partially verified.** There is deliberately no changed-cell
    channel. The previous encoder spent
    T1, C2 and C3 on a mask computed in Python. Those channels are returned to
    colour, and motion is left to the 13,585 T4/T5 neurons evolved to compute it
    from the frame sequence. Network state persists across actions, so the
    temporal structure that computation needs is present.

    Checked before use, and the first measurement of it was wrong. Population
    mean T4/T5 activity is identical for a moving and a static bar (ratio 1.001),
    which looks like failure; direction-selective cells encode motion in *which*
    cells fire, not how many. At the pattern level the frame-to-frame change in
    T4/T5 activity is **3.41x** larger for a moving bar than a static one, and
    2.53x for LC, with the two conditions separated by ~10% of activity. So
    motion is visible to the circuit. What is *not* established is that it is
    visible as **direction-selective** motion: a frozen rate model has none of
    the explicit delay lines that make T4/T5 direction-tuned in the animal, so
    what is measured here may be undifferentiated change sensitivity.
    """

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

        span1 = max(int(hex1.max()) - int(hex1.min()), 1)
        span2 = max(int(hex2.max()) - int(hex2.min()), 1)
        self._span1, self._span2 = span1, span2
        self._column_key = (hex1 - int(hex1.min())) * (span2 + 1) + (hex2 - int(hex2.min()))
        self._column_count = int((span1 + 1) * (span2 + 1))

        # ASSUMPTION: channel order is the sorted type name. Chosen only so the
        # mapping is deterministic and independent of compile order. Any other
        # fixed order is equally defensible; this one is not special, and the
        # permutation control described below is what tests whether it matters.
        self._channel_names = sorted(set(types.tolist()))
        self._channel_count = len(self._channel_names)
        if self._channel_count == 0:
            raise RetinotopyError("retinotopic map declares no cell types")
        lookup = {name: position for position, name in enumerate(self._channel_names)}
        self._neuron_channel = np.asarray([lookup[name] for name in types], dtype=np.int64)

        # Fixed affine mapping from ARC cells to columns: adjacent cells land on
        # adjacent columns, which is the entire point.
        rows = np.arange(GRID_SIZE)
        cell_hex1 = np.rint(rows / (GRID_SIZE - 1) * span1).astype(np.int64)
        cell_hex2 = np.rint(rows / (GRID_SIZE - 1) * span2).astype(np.int64)
        self._cell_column = (cell_hex1[:, None] * (span2 + 1) + cell_hex2[None, :]).ravel()
        self._cells_per_column = np.bincount(self._cell_column, minlength=self._column_count)

        # ASSUMPTION (largest one in this class, and biologically unmotivated).
        # Medulla and lamina cell types are not colour bins. L1 and L2 head the
        # ON and OFF luminance pathways, Mi and Tm types carry sustained and
        # transient features, and none of them encodes "ARC colour 7". Assigning
        # colour c to type index c % channels is a coding convention we invented
        # because the grid has sixteen categories and a column has fifteen
        # addressable types. It is not a claim about Drosophila.
        #
        # What it buys: colours stay categorical and spatially placed, which is
        # what the previous encoder destroyed. What it costs: the fly's own
        # feature semantics are overwritten, so a type that should signal OFF
        # luminance may be carrying "colour 4". Downstream circuits tuned to
        # those semantics -- T4/T5 direction selectivity in particular -- are
        # therefore being driven off-label.
        #
        # To check it: compare against a permuted colour-to-type assignment. If
        # the permutation scores the same, the specific mapping carries nothing
        # and only the categorical-plus-retinotopic structure matters. That is
        # the control to run before any claim that the fly's visual types are
        # doing work here.
        #
        # If it is wrong: results still hold as "retinotopic categorical input
        # helps", but not as "the fly's visual feature channels help".
        self._colour_channel = np.arange(COLOR_COUNT, dtype=np.int64) % self._channel_count
        # Flat bin index for the (column, channel) histogram.
        self._cell_bin_base = self._cell_column * self._channel_count

    @property
    def sensory_indices(self) -> NDArray[np.int64]:
        return self._indices

    @property
    def sensory_size(self) -> int:
        return len(self._indices)

    def describe(self) -> dict[str, Any]:
        collisions = {}
        for colour in range(COLOR_COUNT):
            collisions.setdefault(int(self._colour_channel[colour]), []).append(colour)
        shared = {
            self._channel_names[channel]: colours
            for channel, colours in collisions.items()
            if len(colours) > 1
        }
        return {
            "kind": "retinotopic_columnar_colour",
            "neurons": self.sensory_size,
            "lattice": [self._span1 + 1, self._span2 + 1],
            "occupied_columns": int(np.unique(self._column_key).size),
            "channels": self._channel_count,
            "channel_names": list(self._channel_names),
            "colour_to_channel": "colour c drives type index c % channels (fixed rule)",
            "colliding_channels": shared,
            "colour_representation": "categorical histogram per column, never averaged",
            "change_channel": "none; motion is left to T4/T5",
            "input_scale": self._options.input_scale,
            "preserves_retinotopy": True,
            "preserves_colour_identity": True,
            "trainable": False,
            "trainable_parameters": 0,
        }

    def column_histogram(self, grid: NDArray[np.integer]) -> NDArray[np.float32]:
        """Fraction of each column's ARC cells carrying each colour channel."""

        values = np.asarray(grid, dtype=np.int64)
        if values.shape != (GRID_SIZE, GRID_SIZE):
            raise RetinotopyError(f"expected a {GRID_SIZE}x{GRID_SIZE} grid, got {values.shape}")
        if values.min() < 0 or values.max() >= COLOR_COUNT:
            raise RetinotopyError(f"grid holds a colour outside 0..{COLOR_COUNT - 1}")

        # ASSUMPTION: drive magnitude is the FRACTION of a column's ARC cells
        # carrying each colour, so a column split between two colours drives both
        # at half strength. The alternative is presence/absence, which would make
        # a single stray cell as loud as a solid block. Fractional occupancy is
        # closer to what a photoreceptor array integrating over a receptive field
        # reports, but the grid-to-column ratio here is ~3.4 cells per column, so
        # the choice is only weakly constrained by anything.
        channels = self._colour_channel[values.ravel()]
        totals = np.bincount(
            self._cell_bin_base + channels,
            minlength=self._column_count * self._channel_count,
        ).astype(np.float32)
        histogram = totals.reshape(self._column_count, self._channel_count)
        counts = np.maximum(self._cells_per_column, 1).astype(np.float32)
        return histogram / counts[:, None]

    def drive_features(self, features: ObservationFeatures) -> NDArray[np.float32]:
        """Build the graph-space drive for one turn from the grid itself."""

        histogram = self.column_histogram(features.grid)
        # ASSUMPTION: all drive is positive. The previous encoder signed ON types
        # positive and OFF types negative, which is established physiology for
        # L1/L2. That distinction is dropped here because the types are carrying
        # colour identity instead, and a negative "amount of colour 4" has no
        # meaning. Cost: the ON/OFF opponency the lamina is built around is not
        # being exercised by this input.
        per_neuron = histogram[self._column_key, self._neuron_channel]
        drive = np.zeros(self._node_count, dtype=np.float32)
        np.add.at(drive, self._indices, per_neuron.astype(np.float32))
        drive *= np.float32(self._options.input_scale)
        if not np.isfinite(drive).all():
            raise RetinotopyError("retinotopic drive became non-finite")
        return drive


def build_columnar_colour_projection(
    runtime_dir: str | Path,
    node_count: int,
    *,
    options: RetinotopicOptions | None = None,
) -> ColumnarColourProjection:
    """Load the compiled column map and build the categorical-colour encoder."""

    return ColumnarColourProjection(load_retinotopy(runtime_dir), node_count, options=options)
