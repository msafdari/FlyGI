"""Similarity-aware state tags: the engineered defragmentation key.

HYPOTHESIS (registered under H-FLYHASH-STATE-KEY's noted follow-up and the
2026-09-25 submission lesson): the state graph's exact blake2b keys fragment
near-duplicate observations, inflating count-based novelty and drowning
exploration -- the measured symptom behind zero hidden-set transfer. A
locality-sensitive tag lets a new-but-nearly-identical state read as
familiar for LEARNING purposes (novelty signals) while graph bookkeeping
stays exact.

Honesty about fly content, per the first principle: the FEATURES are the
bio-eye retinotopic columns (fly anatomy, measured load-bearing in the
click head); the EXPANSION is a seeded random projection + winner-take-all
-- ENGINEERED, chosen because the premise sweep measured the anatomical
olfactory pathway layout-blind (identical tags for same-palette
different-layout states) and the real PN->KC wiring at parity with a
rewired control. The fly-attribution control for this mechanism is the
permuted-retinotopy twin ("retino_tags_permuted"), which scrambles the
eye-map and keeps everything else.

Premise numbers (results/flyhash_premise.json): retinotopic-input tags
separate near pairs (Hamming<=8) from far pairs (>=128) at AUC 1.0 with
over-merge Jaccard 0.75 on same-palette pairs -- hence the high default
threshold (0.9) so only genuinely near-duplicate states merge.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray

_TAG_DIM = 4096
_TOP_FRAC = 0.05
_DENSITY = 0.01


class StateTagError(RuntimeError):
    pass


class RetinoTagRegistry:
    """Per-game registry of locality-sensitive observation tags."""

    def __init__(
        self,
        runtime_dir: str | Path,
        *,
        threshold: float = 0.9,
        seed: int = 20260925,
        permute_retinotopy: bool = False,
    ) -> None:
        from flygi.encoding.retinotopic import build_columnar_colour_projection

        if not 0.0 < threshold <= 1.0:
            raise StateTagError("threshold must lie in (0, 1]")
        self._projection = build_columnar_colour_projection(Path(runtime_dir), 166_700)
        self._occupied = np.unique(self._projection._column_key)
        feature_dim = self._occupied.size * 15
        rng = np.random.default_rng(seed)
        # Seeded sparse sign expansion, fixed for the registry's lifetime.
        nnz_per_row = max(1, int(_DENSITY * feature_dim))
        cols = rng.integers(0, feature_dim, size=(_TAG_DIM, nnz_per_row))
        signs = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=cols.shape)
        self._cols = cols
        self._signs = signs
        self._permutation: NDArray[np.int64] | None = None
        if permute_retinotopy:
            # Fly-attribution control: scramble WHICH column each feature
            # belongs to, destroying the eye-map's spatial coherence while
            # keeping dimensionality, expansion, and thresholds identical.
            self._permutation = rng.permutation(feature_dim)
        self.threshold = float(threshold)
        self._k = max(1, int(_TOP_FRAC * _TAG_DIM))
        # REFLEX SPRINT: tags stored bit-packed (64 uint64 words instead of
        # 4096 bools); Jaccard via popcount is integer-exact, so behaviour
        # is identical while the per-turn registry scan shrinks ~60x --
        # it grows with every discovered state and dominates long games.
        self._seen = np.zeros((0, _TAG_DIM // 64), dtype=np.uint64)
        self._seen_count = 0
        self._tag_size = max(1, int(0.05 * _TAG_DIM))

    def tag(self, grid: NDArray[np.int8]) -> NDArray[np.bool_]:
        features = (
            self._projection.column_histogram(np.asarray(grid, dtype=np.int8))[self._occupied, :]
            .astype(np.float32)
            .ravel()
        )
        if self._permutation is not None:
            features = features[self._permutation]
        drive = (features[self._cols] * self._signs).sum(axis=1)
        top = np.argpartition(-drive, self._k - 1)[: self._k]
        out = np.zeros(_TAG_DIM, dtype=bool)
        out[top] = True
        return out

    @staticmethod
    def _pack(tag: NDArray[np.bool_]) -> NDArray[np.uint64]:
        return np.packbits(tag).view(np.uint64)

    def seen_similar(self, tag: NDArray[np.bool_]) -> bool:
        if self._seen_count == 0:
            return False
        packed = self._pack(tag)
        seen = self._seen[: self._seen_count]
        inter = np.bitwise_count(seen & packed).sum(axis=1)
        union = np.bitwise_count(seen | packed).sum(axis=1)
        jaccard = inter / np.maximum(union, 1)
        return bool(jaccard.max() >= self.threshold)

    def observe(self, tag: NDArray[np.bool_]) -> None:
        if self._seen_count == len(self._seen):
            grown = np.zeros((max(64, 2 * len(self._seen)), _TAG_DIM // 64), dtype=np.uint64)
            grown[: self._seen_count] = self._seen[: self._seen_count]
            self._seen = grown
        self._seen[self._seen_count] = self._pack(tag)
        self._seen_count += 1

    def describe(self) -> dict[str, object]:
        return {
            "kind": "retino_tags" + ("_permuted" if self._permutation is not None else ""),
            "threshold": self.threshold,
            "tag_dim": _TAG_DIM,
            "top_fraction": _TOP_FRAC,
            "seen": int(self._seen_count),
            "fly_content": "bio-eye retinotopic features; expansion engineered (seeded)",
        }
