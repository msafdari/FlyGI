"""Spatial taxis: move the controlled sprite toward the displayed goal.

HYPOTHESIS H-TAXIS (registered under H-DEAD-GAMES-TAXONOMY, premise-killers
PASSED 2026-09-25, results/taxis_premise_v2.json): the 14 never-scoring
games share one architecture -- a short exact program whose goal is
displayed on screen -- and the missing capability is attraction of the
controlled object toward the unique salient target. Both components were
validated offline: the avatar is segmentable as the action-correlated
translating region in 11/14 games (recovering measured per-game step sizes
exactly), and the goal as the rare-colour stable component (all four
forensics-named targets hit).

Fly framing, stated honestly: object fixation-and-approach is the fly's
most basic visual behaviour, but THIS implementation is engineered image
processing over raw grids (shift matching, connected components). It is
recorded as scaffold engineering unless a fly-featured variant beats it;
the preregistered controls are the random-target twin (same machinery,
arbitrary stable component as goal) and the no-taxis champion.

Mechanics, all online and deterministic:
  * Timer mask: border-row cells (rows 0-1, 62-63) that change in >2% of
    observed transitions -- the measured clock strips -- are excluded from
    every computation.
  * Avatar: after each directional action whose diff (timer-masked) is
    small, the best translation of the diff bounding box is found; a
    consistent per-action modal displacement (>=3 observations) makes that
    action a known mover, and the diff centroid updates the avatar position.
  * Goal: rare-colour (<120 cells) connected components, stable over the
    recent frames, outside the timer strip, size 3-200; the target is the
    component of the rarest colour (ties: nearest to the avatar).
  * Bonus (primary ranking term, directional candidates only, evidence-
    scaled by the caller like the click head): predicted Manhattan-distance
    change to the target under the action's learned displacement, clipped
    to [-1, 1]. Zero whenever the avatar or the target is unknown, so an
    episode where segmentation fails is byte-identical to the champion.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

_GRID = 64
_TIMER_ROWS = (0, 1, 62, 63)
_RARE_MAX = 120
_COMPONENT_MIN = 3
_COMPONENT_MAX = 200
_DIFF_MIN = 4
_DIFF_MAX = 400
_SHIFT_RANGE = 8
_SHIFT_AGREE = 0.8
_MOVER_MIN_OBS = 3
_MOVER_MODE_FRAC = 0.5
_STABLE_WINDOW = 12


class SpatialTaxis:
    """Per-game online taxis model; injected into the policy like the head."""

    def __init__(self, *, weight: float = 1.0, random_target_seed: int | None = None) -> None:
        self.weight = float(weight)
        self._random_target = (
            np.random.default_rng(random_target_seed) if random_target_seed is not None else None
        )
        self._transitions = 0
        self._border_change = np.zeros((len(_TIMER_ROWS), _GRID), dtype=np.int64)
        self._shift_obs: dict[int, list[tuple[int, int]]] = {1: [], 2: [], 3: [], 4: []}
        self._movers: dict[int, tuple[int, int]] = {}
        self._avatar: tuple[float, float] | None = None
        self._recent: list[bytes] = []
        self._recent_grids: list[NDArray[np.int16]] = []
        self._target: tuple[float, float] | None = None
        self._target_key: bytes | None = None
        self.active_turns = 0
        # Wall memory: (rounded avatar position, action) pairs measured to
        # produce NO sprite motion. The first live gate measured 117
        # consecutive presses into a wall -- the timer tick makes bumps
        # look like effects to the controller, so the taxis module must
        # veto its own pull where it has seen the sprite not move.
        self._blocked: set[tuple[int, int, int]] = set()

    # ------------------------------------------------------------- learning

    def _timer_mask(self) -> NDArray[np.bool_]:
        mask = np.zeros((_GRID, _GRID), dtype=bool)
        if self._transitions >= 10:
            frac = self._border_change / max(self._transitions, 1)
            for i, row in enumerate(_TIMER_ROWS):
                mask[row] = frac[i] > 0.02
        return mask

    def observe_transition(
        self, previous_grid: NDArray[np.int8], action_id: int, new_grid: NDArray[np.int8]
    ) -> None:
        prev = np.asarray(previous_grid, dtype=np.int16)
        new = np.asarray(new_grid, dtype=np.int16)
        diff = prev != new
        self._transitions += 1
        for i, row in enumerate(_TIMER_ROWS):
            self._border_change[i] += diff[row]
        self._recent_grids.append(new)
        if len(self._recent_grids) > _STABLE_WINDOW:
            self._recent_grids.pop(0)
        if action_id not in (1, 2, 3, 4):
            return
        masked = diff & ~self._timer_mask()
        count = int(masked.sum())
        if count < _DIFF_MIN:
            # Nothing but the clock moved: a wall bump. Remember it for this
            # avatar position so the pull yields here instead of pinning.
            if self._avatar is not None:
                self._blocked.add((round(self._avatar[0]), round(self._avatar[1]), action_id))
            return
        if count > _DIFF_MAX:
            return
        rows, cols = np.where(masked)
        # Score each candidate shift ON THE CHANGED CELLS ONLY: a sprite that
        # moved by d satisfies new[x] == prev[x - d] exactly on its pixels.
        # Scoring whole boxes instead lets uniform backgrounds endorse any
        # large shift (measured failure on the synthetic world). Ties break
        # toward the smallest displacement (parsimony).
        best_score, best_shift = 0.0, (0, 0)
        for dr in range(-_SHIFT_RANGE, _SHIFT_RANGE + 1):
            for dc in range(-_SHIFT_RANGE, _SHIFT_RANGE + 1):
                if dr == 0 and dc == 0:
                    continue
                sr, sc = rows - dr, cols - dc
                inside = (sr >= 0) & (sr < _GRID) & (sc >= 0) & (sc < _GRID)
                if inside.sum() < max(3, 0.5 * rows.size):
                    continue
                score = float(
                    (prev[sr[inside], sc[inside]] == new[rows[inside], cols[inside]]).mean()
                )
                better = score > best_score + 1e-9
                tie = abs(score - best_score) <= 1e-9 and (abs(dr) + abs(dc)) < (
                    abs(best_shift[0]) + abs(best_shift[1])
                )
                if better or tie:
                    best_score, best_shift = score, (dr, dc)
        if best_score < _SHIFT_AGREE:
            return
        observations = self._shift_obs[action_id]
        observations.append(best_shift)
        if len(observations) > 40:
            observations.pop(0)
        values, counts = np.unique(np.asarray(observations), axis=0, return_counts=True)
        if counts.max() >= _MOVER_MIN_OBS and counts.max() / len(observations) >= _MOVER_MODE_FRAC:
            self._movers[action_id] = tuple(int(v) for v in values[np.argmax(counts)])
        # The diff region straddles erase+draw; its centroid tracks the
        # sprite to within half a sprite, which Manhattan taxis tolerates.
        self._avatar = (float(rows.mean()), float(cols.mean()))

    # --------------------------------------------------------------- target

    def _find_target(self, grid: NDArray[np.int8]) -> None:
        from scipy import ndimage

        key = grid.tobytes()
        if key == self._target_key:
            return
        self._target_key = key
        self._target = None
        if len(self._recent_grids) < 4:
            return
        frame = np.asarray(grid, dtype=np.int16)
        stack = np.stack(self._recent_grids[-4:])
        stable = (stack == frame).all(axis=0) & ~self._timer_mask()
        counts = np.bincount(frame.ravel(), minlength=16)
        rare_colours = np.flatnonzero((counts > 0) & (counts < _RARE_MAX))
        if rare_colours.size == 0:
            return
        mask = np.isin(frame, rare_colours) & stable
        labels, n = ndimage.label(mask)
        if n == 0:
            return
        sizes = ndimage.sum(mask, labels, range(1, n + 1))
        keep = [i + 1 for i, s in enumerate(sizes) if _COMPONENT_MIN <= s <= _COMPONENT_MAX]
        if not keep or len(keep) > 10:
            return
        centroids = ndimage.center_of_mass(mask, labels, keep)
        if self._random_target is not None:
            # Preregistered control: an arbitrary stable component.
            choice = int(self._random_target.integers(0, len(keep)))
            self._target = tuple(float(v) for v in centroids[choice])
            return

        # Rarest colour first; ties broken by distance to the avatar.
        def colour_count(label_index: int) -> int:
            cells = labels == keep[label_index]
            return int(counts[frame[cells]].min())

        order = sorted(
            range(len(keep)),
            key=lambda i: (
                colour_count(i),
                (
                    abs(centroids[i][0] - self._avatar[0]) + abs(centroids[i][1] - self._avatar[1])
                    if self._avatar is not None
                    else 0.0
                ),
            ),
        )
        self._target = tuple(float(v) for v in centroids[order[0]])

    # ---------------------------------------------------------------- bonus

    def bonus(self, action_id: int, grid: NDArray[np.int8]) -> float:
        if action_id not in self._movers or self._avatar is None:
            return 0.0
        key = (round(self._avatar[0]), round(self._avatar[1]), action_id)
        if key in self._blocked:
            return 0.0
        self._find_target(grid)
        if self._target is None:
            return 0.0
        dr, dc = self._movers[action_id]
        ar, ac = self._avatar
        tr, tc = self._target
        current = abs(ar - tr) + abs(ac - tc)
        predicted = abs(ar + dr - tr) + abs(ac + dc - tc)
        step = abs(dr) + abs(dc)
        if step == 0:
            return 0.0
        if current <= step:
            # Endgame: within one step of the goal every move overshoots the
            # centroid, so plain distance-reduction DEMOTES the winning move
            # (measured on ls20: pulled to distance 2, then stalled until the
            # timer death). Reward landing near the goal instead.
            raw = (step - predicted) / step
        else:
            raw = (current - predicted) / step
        return self.weight * float(np.clip(raw, -1.0, 1.0))

    def describe(self) -> dict[str, object]:
        return {
            "kind": "spatial_taxis" + ("_random_target" if self._random_target is not None else ""),
            "weight": self.weight,
            "movers": {str(k): list(v) for k, v in self._movers.items()},
            "avatar_known": self._avatar is not None,
            "blocked_pairs": len(self._blocked),
            "active_turns": self.active_turns,
            "fly_content": "engineered segmentation over raw grids (recorded as scaffold)",
        }
