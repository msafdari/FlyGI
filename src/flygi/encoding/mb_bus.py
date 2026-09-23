"""The mushroom body's input bus: the screen presented as an odour mixture.

WORKLOG section 11 found that the mushroom body was taught while receiving
0.00% of its input from any driven sensory population -- the learning circuit
never heard the agent's senses, which invalidated the learning test rather than
the learning hypothesis (H-MB-LEARNING). This module is the fix's first half:
give the Kenyon cells sensory content through the pathway they actually read.

Measured in this graph, 2026-09-23: 627 uniglomerular antennal-lobe projection
neurons across 162 glomerular types (DA1_lPN, DM4_adPN, ...), whose 22,581
direct synapses reach 3,811 of 4,064 Kenyon cells -- one hop, 7.23% of total KC
input weight. The pathway exists and is short; it has simply never been driven.

ASSUMPTION (H-MB-INPUT-BUS / assumption G, and it is a large one): ARC has no
odours. This bus presents the screen's global colour histogram to the antennal
lobe as if it were an odour mixture -- each colour a component, its screen
fraction the concentration, glomerular types assigned to colours by sorted
type order, colour c to types t with t_index % 16 == c. Nothing about that
mapping is biology. The defensible claim is only that the mushroom body is an
associative memory whose input bus is the PN pathway, and that bus is being
used; no claim about olfaction is made or permitted. If learning works through
this bus, the result is "the MB can associate screen composition with
reinforcement", not "flies smell ARC".

Why a *global* histogram rather than something spatial: PNs are not
retinotopic. Each glomerulus pools one receptor channel for the whole animal;
its natural analogue is a scene-level composition signal, not a location
signal. Spatial structure belongs to the optic-lobe encoder; forcing it onto
the PN pathway would be a second scrambled-input mistake in the opposite
direction.
"""

from __future__ import annotations

from typing import Any

import numpy as np
from numpy.typing import NDArray

from .features import COLOR_COUNT, GRID_SIZE, ObservationFeatures

# ASSUMPTION: these substrings identify uniglomerular projection neurons in
# MaleCNS v1.0 type names (e.g. DA1_lPN, DM4_adPN, VA2_l2PN). Verified by
# measurement: 627 neurons, 162 types, all cb_intrinsic, 22,581 direct
# synapses onto Kenyon cells. If the annotation scheme changes, the count
# assertions in the constructor fail loudly.
PN_TYPE_PATTERNS = ("adPN", "lPN", "vPN", "ilPN", "lvPN", "l2PN")


class MushroomBodyBusError(ValueError):
    """Raised when the projection-neuron pathway cannot be resolved."""


class PNColourBus:
    """Drive the antennal-lobe projection neurons from the screen's colours."""

    def __init__(
        self,
        types: NDArray[Any],
        node_count: int,
        *,
        input_scale: float = 1.0,
    ) -> None:
        names = np.asarray(types).astype(str)
        mask = np.zeros(names.size, dtype=bool)
        for pattern in PN_TYPE_PATTERNS:
            mask |= np.char.find(names, pattern) >= 0
        indices = np.flatnonzero(mask)
        if indices.size == 0:
            raise MushroomBodyBusError(
                "no projection neurons matched; the annotation scheme has changed "
                f"or the wrong metadata was loaded (patterns: {PN_TYPE_PATTERNS})"
            )
        self._node_count = int(node_count)
        self._indices = indices.astype(np.int64)
        self._scale = np.float32(input_scale)

        # Glomerular types sorted by name, assigned round-robin to the 16
        # colours. Deterministic, compile-order independent, and -- like the
        # visual encoder's colour map -- convention rather than biology. The
        # permutation control pattern from H-COLOUR-MAP applies here too if
        # this bus ever shows an effect.
        type_names = sorted(set(names[indices].tolist()))
        colour_of_type = {name: i % COLOR_COUNT for i, name in enumerate(type_names)}
        self._neuron_colour = np.asarray(
            [colour_of_type[name] for name in names[indices]], dtype=np.int64
        )
        self._glomerular_types = len(type_names)
        counts = np.bincount(self._neuron_colour, minlength=COLOR_COUNT)
        self._colours_covered = int((counts > 0).sum())

    @property
    def sensory_indices(self) -> NDArray[np.int64]:
        return self._indices

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "pn_colour_histogram_bus",
            "neurons": int(self._indices.size),
            "glomerular_types": self._glomerular_types,
            "colours_covered": self._colours_covered,
            "assignment": "sorted glomerular types round-robin over 16 colours (convention)",
            "input_scale": float(self._scale),
            "claim_boundary": "MB as associative memory via its real input bus; not olfaction",
            "trainable": False,
            "trainable_parameters": 0,
        }

    def drive_features(self, features: ObservationFeatures) -> NDArray[np.float32]:
        grid = np.asarray(features.grid, dtype=np.int64)
        if grid.shape != (GRID_SIZE, GRID_SIZE):
            raise MushroomBodyBusError(f"expected {GRID_SIZE}x{GRID_SIZE}, got {grid.shape}")
        histogram = np.bincount(grid.ravel(), minlength=COLOR_COUNT).astype(np.float32)
        histogram /= np.float32(grid.size)
        drive = np.zeros(self._node_count, dtype=np.float32)
        drive[self._indices] = histogram[self._neuron_colour] * self._scale
        return drive


class CompositeProjection:
    """Sum of a primary sensory projection and supplementary buses.

    Exists so the mushroom-body bus can be added to any visual encoder without
    touching it: each part keeps its own indices, description and scale, and
    the drives are summed in graph space. The parts never overlap -- the bus
    targets antennal-lobe PNs, the encoders target the optic lobe -- and the
    constructor verifies that, because a silent overlap would double-drive
    neurons and be invisible in any score.
    """

    def __init__(self, primary: Any, *buses: Any) -> None:
        self._primary = primary
        self._buses = list(buses)
        primary_set = set(np.asarray(primary.sensory_indices).tolist())
        for bus in self._buses:
            overlap = primary_set & set(np.asarray(bus.sensory_indices).tolist())
            if overlap:
                raise MushroomBodyBusError(
                    f"supplementary bus overlaps the primary projection on "
                    f"{len(overlap)} neurons; refusing to double-drive them"
                )

    @property
    def sensory_indices(self) -> NDArray[np.int64]:
        parts = [np.asarray(self._primary.sensory_indices, dtype=np.int64)]
        parts += [np.asarray(b.sensory_indices, dtype=np.int64) for b in self._buses]
        return np.unique(np.concatenate(parts))

    @property
    def sensory_size(self) -> int:
        return int(self.sensory_indices.size)

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "composite",
            "primary": self._primary.describe(),
            "buses": [bus.describe() for bus in self._buses],
        }

    def drive_features(self, features: ObservationFeatures) -> NDArray[np.float32]:
        drive = np.asarray(self._primary.drive_features(features), dtype=np.float32).copy()
        for bus in self._buses:
            drive += bus.drive_features(features)
        return drive
