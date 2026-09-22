"""Reward-modulated plasticity at Kenyon-cell-to-MBON synapses.

Everything else in FlyGI freezes the graph. This module unfreezes one specific
block of it, chosen because it is where *Drosophila* actually learns.

The mushroom body is a three-layer associative learning system. Kenyon cells
give a sparse, high-dimensional expansion of sensory input. MBONs read that
expansion out as approach/avoid valence. Dopaminergic neurons supply a teaching
signal, and plasticity occurs at the Kenyon-cell-to-MBON synapse, where
dopamine **depresses** the synapses that were active when it arrived. That
sign is not a modeling choice made for convenience; it is the established
direction of the effect, and it is what lets the circuit learn to avoid what
preceded punishment and to stop avoiding what preceded reward.

Measured in MaleCNS v1.0: 4,064 Kenyon cells, 97 MBONs, 354 dopaminergic
neurons, and 61,210 Kenyon-cell-to-MBON edges at density 0.155. The plastic
block is therefore roughly 61,000 weights sited where biology puts them, rather
than a few hundred in an invented readout.

Three-factor rule, with all three factors required to be nonzero:

    dw[mbon, kc] = -rate * gate[mbon] * kc_activity[kc]

``gate`` is the dopaminergic drive reaching each MBON's compartment, obtained
from the real dopaminergic-to-MBON anatomy and scaled by the reward signal.
Weights are clipped to a declared band and relax toward their frozen baseline,
so the block cannot run away or silently erase the connectome it started from.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import sparse


class MushroomBodyError(ValueError):
    """Raised when the mushroom-body circuit or its parameters are unusable."""


@dataclass(frozen=True)
class MushroomBodyParameters:
    """Declared, recorded plasticity settings."""

    learning_rate: float = 0.05
    decay: float = 0.01
    weight_floor: float = 0.0
    weight_ceiling_scale: float = 2.0
    reward_scale: float = 1.0
    gate_floor: float = 1e-8

    def __post_init__(self) -> None:
        if not np.isfinite(self.learning_rate) or self.learning_rate < 0:
            raise MushroomBodyError("learning_rate must be finite and non-negative")
        if not 0.0 <= self.decay <= 1.0:
            raise MushroomBodyError("decay must lie in [0, 1]")
        if not np.isfinite(self.weight_ceiling_scale) or self.weight_ceiling_scale < 1.0:
            raise MushroomBodyError("weight_ceiling_scale must be finite and at least 1")
        if not np.isfinite(self.reward_scale):
            raise MushroomBodyError("reward_scale must be finite")
        if self.gate_floor <= 0:
            raise MushroomBodyError("gate_floor must be positive")


@dataclass(frozen=True)
class MushroomBodyAnatomy:
    """Index sets and the dopaminergic-to-MBON compartment map."""

    kenyon_cells: NDArray[np.int64]
    mbons: NDArray[np.int64]
    dopaminergic: NDArray[np.int64]
    dan_to_mbon: sparse.csr_matrix

    def describe(self) -> dict[str, Any]:
        return {
            "kenyon_cells": int(self.kenyon_cells.size),
            "mbons": int(self.mbons.size),
            "dopaminergic": int(self.dopaminergic.size),
            "dan_to_mbon_edges": int(self.dan_to_mbon.nnz),
        }


def resolve_mushroom_body(
    matrix: sparse.spmatrix,
    *,
    kenyon_cells: NDArray[np.integer],
    mbons: NDArray[np.integer],
    dopaminergic: NDArray[np.integer],
) -> MushroomBodyAnatomy:
    """Extract the declared populations and the real DAN-to-MBON adjacency."""

    csr = matrix.tocsr(copy=False)
    node_count = int(csr.shape[0])
    sets = {}
    for name, values in (
        ("kenyon_cells", kenyon_cells),
        ("mbons", mbons),
        ("dopaminergic", dopaminergic),
    ):
        array = np.asarray(values, dtype=np.int64)
        if array.ndim != 1 or array.size == 0:
            raise MushroomBodyError(f"{name} must be a nonempty one-dimensional index array")
        if array.min() < 0 or array.max() >= node_count:
            raise MushroomBodyError(f"{name} contains an index outside the graph")
        if np.unique(array).size != array.size:
            raise MushroomBodyError(f"{name} indices must be unique")
        sets[name] = np.sort(array)

    if np.intersect1d(sets["kenyon_cells"], sets["mbons"]).size:
        raise MushroomBodyError("Kenyon cells and MBONs must be disjoint populations")

    gate = csr[np.ix_(sets["mbons"], sets["dopaminergic"])].tocsr()
    return MushroomBodyAnatomy(
        kenyon_cells=sets["kenyon_cells"],
        mbons=sets["mbons"],
        dopaminergic=sets["dopaminergic"],
        dan_to_mbon=gate,
    )


class MushroomBody:
    """A plastic Kenyon-cell-to-MBON block over an otherwise frozen graph."""

    def __init__(
        self,
        matrix: sparse.csr_matrix,
        anatomy: MushroomBodyAnatomy,
        parameters: MushroomBodyParameters | None = None,
    ) -> None:
        if not sparse.isspmatrix_csr(matrix):
            raise MushroomBodyError("mushroom-body plasticity requires a CSR matrix")
        self._parameters = parameters or MushroomBodyParameters()
        self._anatomy = anatomy

        # Locate the plastic entries once. The rest of the graph is never
        # touched, so the connectome outside this block stays exactly frozen.
        rows, columns, positions = [], [], []
        kc_position = {int(node): i for i, node in enumerate(anatomy.kenyon_cells)}
        indptr, indices = matrix.indptr, matrix.indices
        for mbon_row, node in enumerate(anatomy.mbons):
            start, stop = int(indptr[node]), int(indptr[node + 1])
            for offset in range(start, stop):
                column = int(indices[offset])
                found = kc_position.get(column)
                if found is not None:
                    rows.append(mbon_row)
                    columns.append(found)
                    positions.append(offset)
        if not positions:
            raise MushroomBodyError(
                "no Kenyon-cell-to-MBON edges found; the mushroom body is not wired in this runtime"
            )

        self._positions = np.asarray(positions, dtype=np.int64)
        self._rows = np.asarray(rows, dtype=np.int64)
        self._columns = np.asarray(columns, dtype=np.int64)
        self._baseline = np.asarray(matrix.data[self._positions], dtype=np.float32).copy()
        magnitude = np.abs(self._baseline)
        self._ceiling = (magnitude * np.float32(self._parameters.weight_ceiling_scale)).astype(
            np.float32
        )
        self._sign = np.sign(self._baseline).astype(np.float32)
        self._updates = 0
        self._total_absolute_change = 0.0

    @property
    def anatomy(self) -> MushroomBodyAnatomy:
        return self._anatomy

    @property
    def parameters(self) -> MushroomBodyParameters:
        return self._parameters

    @property
    def plastic_edge_count(self) -> int:
        return int(self._positions.size)

    @property
    def updates_applied(self) -> int:
        return self._updates

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "reward_modulated_kc_to_mbon",
            "site": "Kenyon cell -> MBON",
            "plastic_edges": self.plastic_edge_count,
            "anatomy": self._anatomy.describe(),
            "learning_rate": self._parameters.learning_rate,
            "decay": self._parameters.decay,
            "weight_ceiling_scale": self._parameters.weight_ceiling_scale,
            "reward_scale": self._parameters.reward_scale,
            "dopamine_depresses_active_synapses": True,
            "rest_of_graph_frozen": True,
        }

    def mbon_activity(self, state: NDArray[np.floating]) -> NDArray[np.float32]:
        return np.asarray(state, dtype=np.float32)[self._anatomy.mbons].copy()

    def dopaminergic_activity(self, state: NDArray[np.floating]) -> NDArray[np.float32]:
        return np.asarray(state, dtype=np.float32)[self._anatomy.dopaminergic].copy()

    def gate(self, state: NDArray[np.floating], reward: float) -> NDArray[np.float32]:
        """Dopaminergic drive per MBON compartment, scaled by reward.

        The compartment map is the real dopaminergic-to-MBON adjacency, so which
        MBON a teaching signal reaches is decided by the connectome rather than
        by an assumption.
        """

        if not np.isfinite(reward):
            raise MushroomBodyError("reward must be finite")
        dan = np.abs(self.dopaminergic_activity(state))
        drive = np.asarray(self._anatomy.dan_to_mbon @ dan, dtype=np.float32)
        return (drive * np.float32(reward * self._parameters.reward_scale)).astype(np.float32)

    def update(
        self,
        matrix: sparse.csr_matrix,
        state: NDArray[np.floating],
        reward: float,
    ) -> dict[str, Any]:
        """Apply one three-factor update in place and report what changed."""

        parameters = self._parameters
        gate = self.gate(state, reward)
        kenyon = np.asarray(state, dtype=np.float32)[self._anatomy.kenyon_cells]

        current = np.asarray(matrix.data[self._positions], dtype=np.float32)
        # Dopamine depresses the synapses that were active when it arrived.
        delta = -np.float32(parameters.learning_rate) * gate[self._rows] * kenyon[self._columns]
        if parameters.decay:
            delta += np.float32(parameters.decay) * (self._baseline - current)

        updated = current + delta
        # Keep each weight on its original side of zero and inside a declared
        # band, so plasticity can modulate the connectome but never invert or
        # erase it.
        lower = np.where(self._sign >= 0, np.float32(parameters.weight_floor), -self._ceiling)
        upper = np.where(self._sign >= 0, self._ceiling, np.float32(-parameters.weight_floor))
        updated = np.clip(updated, lower, upper).astype(np.float32)
        if not np.isfinite(updated).all():
            raise MushroomBodyError("plastic weights became non-finite")

        change = float(np.abs(updated - current).sum())
        matrix.data[self._positions] = updated
        self._updates += 1
        self._total_absolute_change += change
        return {
            "reward": float(reward),
            "absolute_change": change,
            "mean_gate": float(gate.mean()),
            "active_kenyon_cells": int(np.count_nonzero(np.abs(kenyon) > 1e-9)),
            "mean_plastic_weight": float(updated.mean()),
            "drift_from_baseline": float(np.abs(updated - self._baseline).mean()),
        }

    def reset(self, matrix: sparse.csr_matrix) -> None:
        """Restore the frozen baseline, as at a new environment boundary."""

        matrix.data[self._positions] = self._baseline
        self._updates = 0
        self._total_absolute_change = 0.0
