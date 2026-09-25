"""Online click-consequence head: H-CONSEQUENCE-COUPLING (EXPERIMENTS.yaml).

HYPOTHESIS: an online per-game logistic head reading LOCAL content at a
candidate click coordinate predicts whether the click will change the frame,
and feeding that prediction into the controller's PRIMARY ranking term
converts to completions and efficiency. Premise measured offline 2026-09-24
(scripts/consequence_premise.py + click-local extension): a 5x5 patch at the
click predicts consequence at AUC 0.998/0.820 in the sparse-change click
games (ft09, lp85); every global feature set, including the connectome's
recurrent state, fails the same test.

The FLY-LOAD-BEARING element is retinotopy: in mode "retinotopic" the patch
is read through the compiled optic-lobe cell->column map, so each patch cell
contributes its retinal column's 15-channel colour histogram -- local content
at the fly's own spatial granularity (~3.4 grid cells per medulla column).
Controls, named before the build (AGENTS.md):

  * "retinotopic_permuted" -- same machinery, seeded permutation of the
    cell->column map. If it matches "retinotopic", the fly's spatial map is
    not load-bearing and only patch-locality matters.
  * "pixel_patch" -- the raw 5x5 one-hot patch, no fly anywhere. The
    engineering alternative.
  * "rote" -- per-coordinate outcome memory, no generalization. The trivial
    alternative: beats the head wherever repetition suffices.

Determinism: no RNG at decision time; plain SGD in float32 with a fixed
update order; the only seed use is the frozen permutation in the permuted
control. An untrained head predicts p=0.5 everywhere, and the bonus is
weight*(2p-1), so the head exerts zero influence until outcomes arrive.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

_GRID = 64
_COLOURS = 16
_PATCH_RADIUS = 2
_PATCH_CELLS = (2 * _PATCH_RADIUS + 1) ** 2  # 5x5 = 25
# One-hot depth: 16 colours plus one out-of-bounds channel.
_PIXEL_CHANNELS = _COLOURS + 1


class ClickHeadError(RuntimeError):
    """Raised when the click head cannot be assembled as configured."""


def load_cell_columns(runtime_dir: str | Path) -> tuple[NDArray[np.int64], int]:
    """Compile the fly's cell->column map from the runtime retinotopy.

    Returns (cell_columns[4096], column_count). Reuses the bio-eye compiler
    so the map is byte-for-byte the one the encoder uses.
    """

    from flygi.encoding.retinotopic import build_columnar_colour_projection

    projection = build_columnar_colour_projection(Path(runtime_dir), 166_700)
    channel_count = projection._channel_count
    cell_columns = (projection._cell_bin_base // channel_count).astype(np.int64)
    if cell_columns.shape != (_GRID * _GRID,):
        raise ClickHeadError(f"cell->column map has shape {cell_columns.shape}")
    return cell_columns, int(projection._column_count)


def _patch_cells(x: int, y: int) -> tuple[NDArray[np.int64], NDArray[np.bool_]]:
    """Flat cell indices of the 5x5 patch at (x, y) plus an in-bounds mask."""

    offsets = np.arange(-_PATCH_RADIUS, _PATCH_RADIUS + 1)
    xs = x + offsets[:, None]
    ys = y + offsets[None, :]
    inside = (xs >= 0) & (xs < _GRID) & (ys >= 0) & (ys < _GRID)
    flat = np.clip(xs, 0, _GRID - 1) * _GRID + np.clip(ys, 0, _GRID - 1)
    return flat.ravel(), inside.ravel()


class OnlineClickHead:
    """Per-game online logistic predictor of click consequence."""

    def __init__(
        self,
        mode: str,
        *,
        cell_columns: NDArray[np.int64] | None = None,
        column_count: int = 0,
        weight: float = 1.0,
        learning_rate: float = 0.3,
        permutation_seed: int = 20260924,
        negative_scale: float = 1.0,
    ) -> None:
        if mode not in {"retinotopic", "retinotopic_permuted", "pixel_patch", "rote"}:
            raise ClickHeadError(f"unknown click head mode: {mode!r}")
        if mode.startswith("retinotopic"):
            if cell_columns is None or column_count <= 0:
                raise ClickHeadError("retinotopic modes need the compiled cell->column map")
            columns = np.asarray(cell_columns, dtype=np.int64).copy()
            if mode == "retinotopic_permuted":
                # Control: destroy spatial coherence of the fly's map while
                # keeping column granularity and every other moving part.
                rng = np.random.default_rng(permutation_seed)
                columns = columns[rng.permutation(columns.size)]
            self._cell_columns = columns
            self._column_count = int(column_count)
            feature_dim = _PATCH_CELLS * _COLOURS  # patch cell x column histogram channel
        elif mode == "pixel_patch":
            self._cell_columns = None
            self._column_count = 0
            feature_dim = _PATCH_CELLS * _PIXEL_CHANNELS
        else:  # rote
            self._cell_columns = None
            self._column_count = 0
            feature_dim = 0
        self.mode = mode
        self.weight = float(weight)
        self.learning_rate = float(learning_rate)
        self.negative_scale = float(negative_scale)
        self._weights = np.zeros(feature_dim + 1, dtype=np.float32) if feature_dim else None
        self._rote_counts: dict[tuple[int, int], tuple[int, int]] = {}
        self._updates = 0
        # Online class balancing: sparse-change games (ft09 measured 5.8%
        # positive) drive a plain SGD to "always no". Each example's gradient
        # is scaled by the sklearn-style balanced weight total/(2*n_class),
        # from running counts, capped so one early example cannot explode.
        self._class_counts = [0, 0]
        # HYPOTHESIS (timer-mask, preregistered under H-DEAD-GAMES-TAXONOMY):
        # clock strips make every action an observation change, saturating
        # the head's labels toward "changed". When enabled, border-row cells
        # changing in >2% of observed transitions are excluded from the
        # change label. Off by default: prior arms stay byte-identical.
        self.timer_mask_enabled = False
        self._border_rows = (0, 1, 62, 63)
        self._border_change = np.zeros((4, 64), dtype=np.int64)
        self._observed = 0
        self._hist_grid_key: bytes | None = None
        self._hist: NDArray[np.float32] | None = None

    # ------------------------------------------------------------------ features

    def _column_histogram(self, grid: NDArray[np.int8]) -> NDArray[np.float32]:
        """Fractional colour occupancy per column of the CURRENT grid,
        computed through the (possibly permuted) cell->column map and cached
        per grid so ranking many candidates costs one pass."""

        key = grid.tobytes()
        if key == self._hist_grid_key and self._hist is not None:
            return self._hist
        values = np.clip(grid.astype(np.int64, copy=False).ravel(), 0, _COLOURS - 1)
        bins = self._cell_columns * _COLOURS + values
        totals = np.bincount(bins, minlength=self._column_count * _COLOURS).astype(np.float32)
        hist = totals.reshape(self._column_count, _COLOURS)
        counts = np.maximum(np.bincount(self._cell_columns, minlength=self._column_count), 1)
        hist /= counts[:, None].astype(np.float32)
        self._hist_grid_key = key
        self._hist = hist
        return hist

    def _features(self, grid: NDArray[np.int8], x: int, y: int) -> NDArray[np.float32]:
        cells, inside = _patch_cells(x, y)
        if self.mode == "pixel_patch":
            out = np.zeros((_PATCH_CELLS, _PIXEL_CHANNELS), dtype=np.float32)
            colours = grid.ravel()[cells]
            rows = np.arange(_PATCH_CELLS)
            out[rows, np.where(inside, np.clip(colours, 0, _COLOURS - 1), _COLOURS)] = 1.0
            return out.ravel()
        hist = self._column_histogram(grid)
        out = hist[self._cell_columns[cells], :].astype(np.float32, copy=True)
        out[~inside] = 0.0
        return out.ravel()

    # ---------------------------------------------------------------- interface

    def probability(self, grid: NDArray[np.int8], x: int, y: int) -> float:
        """P(this click changes the frame), 0.5 until evidence exists."""

        if self.mode == "rote":
            changed, seen = self._rote_counts.get((int(x), int(y)), (0, 0))
            return (changed + 1.0) / (seen + 2.0)
        assert self._weights is not None
        features = self._features(np.asarray(grid, dtype=np.int8), int(x), int(y))
        logit = float(features @ self._weights[:-1] + self._weights[-1])
        return float(1.0 / (1.0 + np.exp(-np.clip(logit, -30.0, 30.0))))

    def bonus(self, grid: NDArray[np.int8], x: int, y: int) -> float:
        """Signed primary-term bonus in the priority+exploration scale.

        The negative side is scaled by negative_scale: at 0.0 the head is
        boost-only and cannot starve discovery of clicks it mispredicts as
        no-ops (the first treatment arm's measured failure mode)."""

        raw = 2.0 * self.probability(grid, x, y) - 1.0
        if raw < 0.0:
            raw *= self.negative_scale
        return self.weight * raw

    def masked_changed(self, source: NDArray[np.int8], destination: NDArray[np.int8]) -> bool:
        """Change label with hyper-frequent border (clock) cells excluded."""

        src = np.asarray(source, dtype=np.int16)
        dst = np.asarray(destination, dtype=np.int16)
        diff = src != dst
        self._observed += 1
        for i, row in enumerate(self._border_rows):
            self._border_change[i] += diff[row]
        if not self.timer_mask_enabled:
            return bool(diff.any())
        if self._observed >= 10:
            frac = self._border_change / self._observed
            for i, row in enumerate(self._border_rows):
                diff[row] &= ~(frac[i] > 0.02)
        return bool(diff.any())

    def update(self, grid: NDArray[np.int8], x: int, y: int, changed: bool) -> None:
        """One online SGD step from an executed click's observed outcome."""

        self._updates += 1
        if self.mode == "rote":
            prior_changed, seen = self._rote_counts.get((int(x), int(y)), (0, 0))
            self._rote_counts[(int(x), int(y))] = (prior_changed + int(changed), seen + 1)
            return
        assert self._weights is not None
        features = self._features(np.asarray(grid, dtype=np.int8), int(x), int(y))
        prediction = self.probability(grid, x, y)
        self._class_counts[int(bool(changed))] += 1
        total = self._class_counts[0] + self._class_counts[1]
        balance = min(total / (2.0 * self._class_counts[int(bool(changed))]), 20.0)
        gradient = np.float32(self.learning_rate * balance * (float(changed) - prediction))
        self._weights[:-1] += gradient * features
        self._weights[-1] += gradient
        # The cached histogram belongs to the pre-click grid; ranking on the
        # next turn recomputes for the new frame anyway, so no invalidation
        # is needed beyond the grid-key check.

    def describe(self) -> dict[str, Any]:
        return {
            "mode": self.mode,
            "weight": self.weight,
            "learning_rate": self.learning_rate,
            "negative_scale": self.negative_scale,
            "timer_mask": self.timer_mask_enabled,
            "updates": self._updates,
            "parameters": 0 if self._weights is None else int(self._weights.size),
        }
