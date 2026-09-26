"""Historical retinotopic readback, including its declared axis defect.

The measurement that forced this module (2026-09-23, 16 trials, structured
scenes, one 6x6 change at a known place) used the legacy-transposed convention:

    hex-map readback of |delta state|      median error  0.8 cells
    prediction-error (surprise) readback   median error  0.8 cells
    the deployed coordinate head           median error 23.5 cells
    chance                                 median error 37.2 cells

Audit on 2026-09-26 established that this implementation returns hex1/grid-row
as ACTION6 x and hex2/grid-column as y, while ARC defines x=column and y=row.
The 0.8-cell number is therefore a real measurement of the legacy-transposed
assay, not evidence of ARC-correct localization. The deployed block decoder
still read that legacy assay at chance. Reference practice agrees: flyvis
(Lappalainen et al., Nature 2024) decodes the optic lobe as instantaneous
per-column, per-cell-type activity, never as unordered population statistics.

Two scores, one mechanism:

- ``state_change``: per column, mean |state_now - state_previous| over its
  neurons -- where the eye registered change.
- ``surprise``: per column, mean |state_now - state_expected| where the
  expectation is the network advanced on the PREVIOUS frame again -- the
  connectome free-running as its own one-step forward model, and the map is
  the deviation of the world from that prediction. Predictive-coding in
  spirit; every parameter of the predictor is the frozen connectome itself,
  zero trained weights (the JEPA-adjacent idea, minus the training).

ASSUMPTION (historical, falsified at the action boundary): screen position for
a column was treated as the inverse of the encoder's affine cell->column
assignment with hex1 owned by x. ARC instead owns x by column/hex2. A column's
neurons inheriting one position remains plumbing; the 0.8-cell legacy result
does not validate the old axis ownership.

HYPOTHESIS H-RETINO-DECODER is invalidated, not refuted: its interface was
transposed. A corrected readback and real-vs-null/no-recurrence comparison must
be preregistered separately before any localization or behavior claim.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

GRID = 64


class RetinotopicSaliencyError(ValueError):
    """Raised when the column map cannot support a spatial readback."""


class RetinotopicSaliency:
    """Map optic-lobe differences through the legacy-transposed screen axes."""

    def __init__(
        self,
        runtime_dir: str | Path,
        *,
        mode: str = "state_change",
    ) -> None:
        if mode not in ("state_change", "surprise"):
            raise RetinotopicSaliencyError(f"unknown saliency mode: {mode!r}")
        self._mode = mode
        path = Path(runtime_dir) / "retinotopy.npz"
        if not path.is_file():
            raise RetinotopicSaliencyError(
                f"{path} is missing; build it with scripts/build_retinotopy.py"
            )
        with np.load(path, allow_pickle=False) as archive:
            self._indices = np.asarray(archive["node_indices"], dtype=np.int64)
            hex1 = np.asarray(archive["hex1"], dtype=np.float64)
            hex2 = np.asarray(archive["hex2"], dtype=np.float64)
        if self._indices.size == 0:
            raise RetinotopicSaliencyError("the retinotopic map is empty")
        span1 = max(hex1.max() - hex1.min(), 1.0)
        span2 = max(hex2.max() - hex2.min(), 1.0)
        # LEGACY ASSUMPTION (invalid at ACTION6): rows/hex1 bin to x and
        # columns/hex2 to y. Keep this exact behavior until a separately
        # declared coordinate-convention flag supplies the ARC-correct inverse.
        self._row = np.clip((hex1 - hex1.min()) / span1 * (GRID - 1), 0, GRID - 1)
        self._col = np.clip((hex2 - hex2.min()) / span2 * (GRID - 1), 0, GRID - 1)
        self._row_bin = np.rint(self._row).astype(np.int64)
        self._col_bin = np.rint(self._col).astype(np.int64)

    @property
    def mode(self) -> str:
        return self._mode

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "retinotopic_saliency",
            "mode": self._mode,
            "neurons": int(self._indices.size),
            "measured_localization_cells": 0.8,
            "measurement_coordinate_convention": "legacy_hex1_x_transposed",
            "measurement_valid_for_arc_coordinates": False,
            "deployed_head_localization_cells": 23.5,
            "expectation_model": (
                "the frozen connectome advanced on the previous frame (zero trained parameters)"
                if self._mode == "surprise"
                else "previous network state"
            ),
            "trainable": False,
            "trainable_parameters": 0,
        }

    def axis_scores(
        self,
        state_now: NDArray[np.floating],
        state_reference: NDArray[np.floating],
    ) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
        """Legacy x(row), y(column) scores from |now-reference| on the map.

        ``state_reference`` is the previous state for ``state_change`` and the
        free-run expectation for ``surprise``; the caller owns producing it,
        because only the caller can advance the network without committing.
        """

        now = np.asarray(state_now, dtype=np.float64)
        reference = np.asarray(state_reference, dtype=np.float64)
        if now.shape != reference.shape:
            raise RetinotopicSaliencyError("state and reference shapes differ")
        weight = np.abs(now[self._indices] - reference[self._indices])
        x = np.bincount(self._row_bin, weights=weight, minlength=GRID)
        y = np.bincount(self._col_bin, weights=weight, minlength=GRID)
        return x.astype(np.float32), y.astype(np.float32)
