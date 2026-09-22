"""Fixed seeded sparse projection from ARC features into a sensory population.

The projection is generated once from a declared seed and reused unchanged for
the real graph and every null graph. That is the specification's fairness
constraint: the interface must not vary across graph conditions, so any
difference in behavior is attributable to the graph rather than to the way the
observation entered it.

Nothing here is trained. The matrix is a Johnson-Lindenstrauss style sparse
random projection with a fixed number of nonzeros per sensory neuron and
symmetric +/-1 signs scaled to preserve the expected feature norm.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy import sparse

from .features import FEATURE_DIMENSION


class ProjectionError(ValueError):
    """Raised when a sensory projection violates its declared contract."""


@dataclass(frozen=True)
class ProjectionOptions:
    """Declared, recorded choices that change the sensory projection."""

    connections_per_neuron: int = 64
    input_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.connections_per_neuron <= 0:
            raise ProjectionError("connections_per_neuron must be positive")
        if not np.isfinite(self.input_scale) or self.input_scale <= 0:
            raise ProjectionError("input_scale must be finite and positive")


class SensoryProjection:
    """A frozen sparse map from ARC features to one declared sensory set."""

    def __init__(
        self,
        matrix: sparse.csr_matrix,
        sensory_indices: NDArray[np.int64],
        node_count: int,
        *,
        options: ProjectionOptions,
        seed: int,
    ) -> None:
        if matrix.shape != (len(sensory_indices), FEATURE_DIMENSION):
            raise ProjectionError(
                f"projection must have shape ({len(sensory_indices)}, "
                f"{FEATURE_DIMENSION}), observed {matrix.shape}"
            )
        if matrix.dtype != np.float32:
            raise ProjectionError("projection dtype must be float32")
        if len(sensory_indices) == 0:
            raise ProjectionError("sensory population must not be empty")
        if sensory_indices.min() < 0 or sensory_indices.max() >= node_count:
            raise ProjectionError("sensory index lies outside the neural state")
        if len(np.unique(sensory_indices)) != len(sensory_indices):
            raise ProjectionError("sensory indices must be unique")

        matrix.data.flags.writeable = False
        matrix.indices.flags.writeable = False
        matrix.indptr.flags.writeable = False
        self._matrix = matrix
        self._sensory = sensory_indices
        self._node_count = int(node_count)
        self._options = options
        self._seed = int(seed)

    @property
    def sensory_indices(self) -> NDArray[np.int64]:
        return self._sensory

    @property
    def sensory_size(self) -> int:
        return len(self._sensory)

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def options(self) -> ProjectionOptions:
        return self._options

    @property
    def nonzeros(self) -> int:
        return int(self._matrix.nnz)

    def describe(self) -> dict[str, object]:
        """Provenance for the result manifest."""

        return {
            "kind": "fixed_seeded_sparse_projection",
            "seed": self._seed,
            "feature_dimension": FEATURE_DIMENSION,
            "sensory_size": self.sensory_size,
            "connections_per_neuron": self._options.connections_per_neuron,
            "input_scale": self._options.input_scale,
            "nonzeros": self.nonzeros,
            "trainable": False,
        }

    def drive_features(self, features: object) -> NDArray[np.float32]:
        """Common entry point shared with the retinotopic encoder."""

        return self.drive(getattr(features, "vector", features))

    def drive(self, features: NDArray[np.float32]) -> NDArray[np.float32]:
        """Project features into a full graph-space drive vector."""

        vector = np.asarray(features)
        if vector.shape != (FEATURE_DIMENSION,):
            raise ProjectionError(
                f"features must have shape ({FEATURE_DIMENSION},), observed {vector.shape}"
            )
        if vector.dtype != np.float32:
            vector = vector.astype(np.float32, copy=False)
        projected = np.asarray(self._matrix @ vector, dtype=np.float32)
        projected *= np.float32(self._options.input_scale)
        drive = np.zeros(self._node_count, dtype=np.float32)
        drive[self._sensory] = projected
        if not np.isfinite(drive).all():
            raise ProjectionError("sensory drive became non-finite")
        return drive


def build_sensory_projection(
    sensory_indices: NDArray[np.integer],
    node_count: int,
    *,
    seed: int,
    options: ProjectionOptions | None = None,
) -> SensoryProjection:
    """Create the declared projection deterministically from ``seed``."""

    settings = options or ProjectionOptions()
    indices = np.asarray(sensory_indices, dtype=np.int64)
    if indices.ndim != 1:
        raise ProjectionError("sensory indices must be one-dimensional")
    rows = len(indices)
    if rows == 0:
        raise ProjectionError("sensory population must not be empty")

    per_row = min(settings.connections_per_neuron, FEATURE_DIMENSION)
    generator = np.random.default_rng(seed)
    columns = generator.integers(0, FEATURE_DIMENSION, size=(rows, per_row), dtype=np.int64)
    signs = generator.integers(0, 2, size=(rows, per_row)).astype(np.float32) * 2.0 - 1.0
    signs *= np.float32(1.0 / np.sqrt(per_row))

    indptr = np.arange(rows + 1, dtype=np.int64) * per_row
    matrix = sparse.csr_matrix(
        (signs.ravel(), columns.ravel(), indptr),
        shape=(rows, FEATURE_DIMENSION),
        dtype=np.float32,
    )
    matrix.sort_indices()
    matrix.sum_duplicates()
    return SensoryProjection(matrix, indices, int(node_count), options=settings, seed=int(seed))
