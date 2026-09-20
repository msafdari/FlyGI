"""Sparse-only transforms, signs, and normalization for connectome weights."""

from __future__ import annotations

from collections import Counter
from collections.abc import Iterable
from typing import Literal

import numpy as np
from scipy import sparse

WeightTransform = Literal["raw", "log1p", "sqrt", "binary"]
Normalization = Literal["none", "incoming_l1", "spectral_radius"]
UnknownTreatment = Literal["zero", "positive", "negative", "error"]

EXCITATORY_TRANSMITTERS = frozenset({"acetylcholine"})
INHIBITORY_TRANSMITTERS = frozenset({"gaba", "glutamate", "histamine"})
MODULATORY_TRANSMITTERS = frozenset({"dopamine", "serotonin", "octopamine", "tyramine"})


def transform_weights(
    weights: np.ndarray | Iterable[float], mode: WeightTransform = "raw"
) -> np.ndarray:
    """Transform non-negative aggregated contact counts into float32 weights."""

    values = np.asarray(weights)
    if values.ndim != 1:
        raise ValueError("weights must be a one-dimensional array")
    if not np.issubdtype(values.dtype, np.number):
        raise TypeError("weights must be numeric")
    values64 = values.astype(np.float64, copy=False)
    if not np.isfinite(values64).all() or (values64 < 0).any():
        raise ValueError("weights must be finite and non-negative")

    if mode == "raw":
        transformed = values64
    elif mode == "log1p":
        transformed = np.log1p(values64)
    elif mode == "sqrt":
        transformed = np.sqrt(values64)
    elif mode == "binary":
        transformed = (values64 != 0).astype(np.float64)
    else:
        raise ValueError(f"Unknown weight transform: {mode!r}")
    return transformed.astype(np.float32, copy=False)


def _canonical_transmitter(value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, (float, np.floating)) and np.isnan(value):
        return None
    label = str(value).strip().lower()
    return label or None


def transmitter_signs(
    transmitters: Iterable[object],
    *,
    modulator_treatment: UnknownTreatment = "zero",
    unknown_treatment: UnknownTreatment = "zero",
) -> tuple[np.ndarray, dict[str, object]]:
    """Map presynaptic transmitter labels to explicit heuristic signs.

    The function deliberately keeps modulators separate from unknown values.
    Neither category is silently treated as excitatory by default.
    """

    labels = [_canonical_transmitter(value) for value in transmitters]
    signs = np.empty(len(labels), dtype=np.float32)
    counts: Counter[str] = Counter()

    def treatment_sign(treatment: UnknownTreatment, category: str) -> float:
        if treatment == "zero":
            return 0.0
        if treatment == "positive":
            return 1.0
        if treatment == "negative":
            return -1.0
        if treatment == "error":
            raise ValueError(f"Encountered {category} transmitter in heuristic mode")
        raise ValueError(f"Unknown transmitter treatment: {treatment!r}")

    for index, label in enumerate(labels):
        if label in EXCITATORY_TRANSMITTERS:
            signs[index] = 1.0
            counts["excitatory"] += 1
        elif label in INHIBITORY_TRANSMITTERS:
            signs[index] = -1.0
            counts["inhibitory"] += 1
        elif label in MODULATORY_TRANSMITTERS:
            signs[index] = treatment_sign(modulator_treatment, "modulatory")
            counts["modulatory"] += 1
        else:
            signs[index] = treatment_sign(unknown_treatment, "unknown")
            counts["unknown"] += 1

    return signs, {
        "excitatory": int(counts["excitatory"]),
        "inhibitory": int(counts["inhibitory"]),
        "modulatory": int(counts["modulatory"]),
        "unknown": int(counts["unknown"]),
        "modulator_treatment": modulator_treatment,
        "unknown_treatment": unknown_treatment,
    }


def apply_presynaptic_signs(matrix: sparse.spmatrix, signs: np.ndarray) -> sparse.csr_matrix:
    """Apply a per-neuron sign to CSR columns (the presynaptic axis)."""

    csr = _as_csr(matrix, copy=True)
    sign_array = np.asarray(signs, dtype=np.float32)
    if sign_array.shape != (csr.shape[1],):
        raise ValueError(f"Expected {csr.shape[1]} presynaptic signs, got {sign_array.shape}")
    csr.data = csr.data.astype(np.float32, copy=False)
    csr.data *= sign_array[csr.indices]
    csr.eliminate_zeros()
    return csr


def incoming_l1_normalize(matrix: sparse.spmatrix, *, epsilon: float = 1e-8) -> sparse.csr_matrix:
    """Normalize incoming absolute weight per postsynaptic row.

    With the package convention ``W[post, pre]``, this implements
    ``W[i, j] / (epsilon + sum_k(abs(W[i, k])))``.  Only an O(N) row-sum
    vector is materialized; an N-by-N dense array is never constructed.
    """

    if epsilon <= 0 or not np.isfinite(epsilon):
        raise ValueError("epsilon must be finite and strictly positive")
    csr = _as_csr(matrix, copy=True)
    csr.data = csr.data.astype(np.float32, copy=False)
    row_sums = np.asarray(abs(csr).sum(axis=1), dtype=np.float64).reshape(-1)
    scales = (epsilon + row_sums) ** -1
    for row, scale in enumerate(scales):
        start = int(csr.indptr[row])
        stop = int(csr.indptr[row + 1])
        if start != stop:
            csr.data[start:stop] *= np.float32(scale)
    return csr


def estimate_spectral_radius(
    matrix: sparse.spmatrix,
    *,
    max_iterations: int = 200,
    tolerance: float = 1e-6,
    seed: int = 0,
) -> float:
    """Estimate ``abs(lambda_max)`` by deterministic sparse power iteration."""

    csr = _as_csr(matrix, copy=False)
    if csr.shape[0] != csr.shape[1]:
        raise ValueError("spectral radius requires a square matrix")
    if max_iterations <= 0:
        raise ValueError("max_iterations must be positive")
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if csr.shape[0] == 0 or csr.nnz == 0:
        return 0.0

    generator = np.random.default_rng(seed)
    vector = generator.standard_normal(csr.shape[1])
    vector /= np.linalg.norm(vector)
    previous = 0.0
    estimate = 0.0
    for _ in range(max_iterations):
        product = csr @ vector
        estimate = float(np.linalg.norm(product))
        if not np.isfinite(estimate):
            raise FloatingPointError("spectral-radius iteration became non-finite")
        if estimate == 0.0:
            return 0.0
        vector = np.asarray(product).reshape(-1) / estimate
        if abs(estimate - previous) <= tolerance * max(1.0, estimate):
            break
        previous = estimate
    return estimate


def spectral_radius_scale(
    matrix: sparse.spmatrix,
    *,
    target: float = 0.9,
    max_iterations: int = 200,
    tolerance: float = 1e-6,
) -> sparse.csr_matrix:
    """Scale a sparse matrix to an estimated dominant eigenvalue magnitude."""

    if target < 0 or not np.isfinite(target):
        raise ValueError("target spectral radius must be finite and non-negative")
    csr = _as_csr(matrix, copy=True)
    csr.data = csr.data.astype(np.float32, copy=False)
    observed = estimate_spectral_radius(csr, max_iterations=max_iterations, tolerance=tolerance)
    if observed == 0.0:
        if target == 0.0:
            return csr
        raise ValueError("cannot give a zero-spectral-radius matrix a positive radius")
    csr.data *= np.float32(target / observed)
    return csr


def normalize_matrix(
    matrix: sparse.spmatrix,
    mode: Normalization = "incoming_l1",
    *,
    epsilon: float = 1e-8,
    spectral_radius: float = 0.9,
) -> sparse.csr_matrix:
    """Apply one declared sparse normalization mode."""

    if mode == "none":
        result = _as_csr(matrix, copy=True)
        result.data = result.data.astype(np.float32, copy=False)
        return result
    if mode == "incoming_l1":
        return incoming_l1_normalize(matrix, epsilon=epsilon)
    if mode == "spectral_radius":
        return spectral_radius_scale(matrix, target=spectral_radius)
    raise ValueError(f"Unknown normalization mode: {mode!r}")


def _as_csr(matrix: sparse.spmatrix, *, copy: bool) -> sparse.csr_matrix:
    if not sparse.issparse(matrix):
        raise TypeError("connectome operations require a scipy sparse matrix")
    return matrix.tocsr(copy=copy)
