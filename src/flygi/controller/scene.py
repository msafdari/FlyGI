"""Generic ARC scene extraction and stable state identity.

This module deliberately knows nothing about particular games, colors, or
mechanics.  It turns the observable 64x64 grid and legal-action set into the
small deterministic primitives needed by a state-graph controller:

* an observation-derived, eventually frozen mask for volatile border pixels;
* a collision-verifiable BLAKE2b-128 state key;
* conservative background inference;
* per-color, four-connected components; and
* deterministic component-grounded click candidates.

Coordinates exposed to policies use ARC's ``(x, y)`` convention.
"""

from __future__ import annotations

import hashlib
import math
from collections.abc import Callable, Iterable
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from typing import Any

import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

from flygi.encoding.features import ACTION_SLOTS, COLOR_COUNT, GRID_SIZE, latest_grid

STATE_DIGEST_BYTES = 16
MASKED_CELL_SENTINEL = COLOR_COUNT
COARSE_SPATIAL_BIN_SIZE = 8
_CANONICAL_PREFIX = b"flygi.scene.v1\x00"
_FOUR_CONNECTED = np.asarray(
    (
        (False, True, False),
        (True, True, True),
        (False, True, False),
    ),
    dtype=np.bool_,
)


class SceneError(ValueError):
    """Raised when scene configuration or observable policy input is invalid."""


def _readonly_copy(array: NDArray[Any], dtype: np.dtype[Any]) -> NDArray[Any]:
    copied = np.asarray(array, dtype=dtype).copy()
    copied.setflags(write=False)
    return copied


def _validate_mask(mask: NDArray[np.bool_] | None) -> NDArray[np.bool_]:
    if mask is None:
        return np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.bool_)
    array = np.asarray(mask)
    if array.shape != (GRID_SIZE, GRID_SIZE):
        raise SceneError(
            f"scene mask must have shape ({GRID_SIZE}, {GRID_SIZE}), observed {array.shape}"
        )
    if array.dtype != np.bool_:
        raise SceneError(f"scene mask must have boolean dtype, observed {array.dtype}")
    return array


def _border_band(width: int) -> NDArray[np.bool_]:
    border = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.bool_)
    if width:
        border[:width, :] = True
        border[-width:, :] = True
        border[:, :width] = True
        border[:, -width:] = True
    return border


@dataclass(frozen=True, slots=True)
class VolatileMaskConfig:
    """Controls inference of volatile UI pixels from observed transitions.

    ``comparisons_to_freeze`` counts frame-to-frame comparisons, so one more
    frame than this value is required.  Only cells inside ``border_width`` can
    ever be masked.  A cell must meet both the absolute and fractional change
    thresholds.  Once frozen, the mask never changes within that tracker.
    """

    border_width: int = 4
    comparisons_to_freeze: int = 8
    minimum_changes: int = 2
    minimum_change_rate: float = 0.25

    def __post_init__(self) -> None:
        if isinstance(self.border_width, bool) or not 0 <= self.border_width <= GRID_SIZE // 2:
            raise SceneError(f"border_width must lie in [0, {GRID_SIZE // 2}]")
        if isinstance(self.comparisons_to_freeze, bool) or self.comparisons_to_freeze < 1:
            raise SceneError("comparisons_to_freeze must be a positive integer")
        if isinstance(self.minimum_changes, bool) or self.minimum_changes < 1:
            raise SceneError("minimum_changes must be a positive integer")
        if self.minimum_changes > self.comparisons_to_freeze:
            raise SceneError("minimum_changes cannot exceed comparisons_to_freeze")
        if not 0.0 < float(self.minimum_change_rate) <= 1.0:
            raise SceneError("minimum_change_rate must lie in (0, 1]")


@dataclass(frozen=True, slots=True)
class VolatileMaskSnapshot:
    """Immutable public snapshot of the border-mask learner."""

    mask: NDArray[np.bool_]
    comparisons: int
    frozen: bool
    just_frozen: bool

    def __post_init__(self) -> None:
        if self.mask.shape != (GRID_SIZE, GRID_SIZE) or self.mask.dtype != np.bool_:
            raise SceneError("volatile mask snapshot has an invalid mask")
        if self.mask.flags.writeable:
            raise SceneError("volatile mask snapshots must be read-only")
        if self.comparisons < 0:
            raise SceneError("volatile mask comparison count cannot be negative")
        if self.just_frozen and not self.frozen:
            raise SceneError("just_frozen requires a frozen mask")


class FrozenVolatileMask:
    """Learn a volatile border mask, then make it immutable.

    Interior changes are intentionally ignored no matter how frequently they
    occur: moving avatars and objects must remain part of state identity.
    """

    def __init__(self, config: VolatileMaskConfig | None = None) -> None:
        self.config = config or VolatileMaskConfig()
        self._eligible = _border_band(self.config.border_width)
        self._changes = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.uint32)
        self._previous_grid: NDArray[np.int8] | None = None
        self._mask = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.bool_)
        self._comparisons = 0
        self._frozen = False

    @property
    def frozen(self) -> bool:
        """Whether enough comparisons have been observed to freeze the mask."""

        return self._frozen

    def observe(self, frame: Any) -> VolatileMaskSnapshot:
        """Observe a frame and return the current immutable snapshot."""

        grid = latest_grid(frame)
        just_frozen = False

        if self._previous_grid is None:
            self._previous_grid = np.array(grid, dtype=np.int8, copy=True)
        elif not self._frozen:
            changed = self._previous_grid != grid
            self._changes += np.asarray(changed & self._eligible, dtype=np.uint32)
            self._comparisons += 1
            self._previous_grid = np.array(grid, dtype=np.int8, copy=True)

            if self._comparisons >= self.config.comparisons_to_freeze:
                rate_requirement = math.ceil(self.config.minimum_change_rate * self._comparisons)
                required = max(self.config.minimum_changes, rate_requirement)
                self._mask = self._eligible & (self._changes >= required)
                self._frozen = True
                just_frozen = True

        return VolatileMaskSnapshot(
            mask=_readonly_copy(self._mask, np.dtype(np.bool_)),
            comparisons=self._comparisons,
            frozen=self._frozen,
            just_frozen=just_frozen,
        )


def legal_action_mask(available_action_ids: Iterable[int]) -> tuple[bool, ...]:
    """Canonicalize and validate the observable legal-action set."""

    mask = [False] * ACTION_SLOTS
    seen: set[int] = set()
    for raw_identifier in available_action_ids:
        if isinstance(raw_identifier, bool) or not isinstance(raw_identifier, (int, np.integer)):
            raise SceneError(
                f"legal action identifiers must be integers, observed {raw_identifier!r}"
            )
        identifier = int(raw_identifier)
        if not 0 <= identifier < ACTION_SLOTS:
            raise SceneError(
                f"legal action id must lie in [0, {ACTION_SLOTS - 1}], observed {identifier}"
            )
        if identifier in seen:
            raise SceneError(f"duplicate legal action id: {identifier}")
        seen.add(identifier)
        mask[identifier] = True
    return tuple(mask)


@dataclass(frozen=True, slots=True)
class StateKey:
    """Digest and exact canonical bytes for collision-safe graph lookup.

    ``digest`` is a 32-character BLAKE2b-128 hexadecimal key suitable for a
    dictionary index.  Controllers must compare ``canonical`` when an existing
    digest is found rather than assuming a collision cannot occur.
    """

    digest: str
    canonical: bytes
    legal_actions: tuple[bool, ...]

    def __post_init__(self) -> None:
        if len(self.digest) != STATE_DIGEST_BYTES * 2:
            raise SceneError("state digest is not BLAKE2b-128 hexadecimal")
        try:
            bytes.fromhex(self.digest)
        except ValueError as exc:
            raise SceneError("state digest is not hexadecimal") from exc
        if not isinstance(self.canonical, bytes) or not self.canonical.startswith(
            _CANONICAL_PREFIX
        ):
            raise SceneError("state canonical representation has an invalid prefix")
        if len(self.legal_actions) != ACTION_SLOTS or any(
            not isinstance(value, bool) for value in self.legal_actions
        ):
            raise SceneError("state legal-action mask is invalid")


def canonical_state_key(
    frame: Any,
    available_action_ids: Iterable[int],
    *,
    volatile_mask: NDArray[np.bool_] | None = None,
) -> tuple[StateKey, NDArray[np.uint8]]:
    """Return a collision-verifiable state key and its canonicalized grid.

    Masked cells are replaced by value ``16``, which is outside ARC's declared
    0--15 palette.  The fixed-length legal-action mask is part of both the
    canonical bytes and digest.
    """

    grid = latest_grid(frame)
    mask = _validate_mask(volatile_mask)
    action_mask = legal_action_mask(available_action_ids)

    canonical_grid = np.asarray(grid, dtype=np.uint8).copy()
    canonical_grid[mask] = MASKED_CELL_SENTINEL
    action_bytes = bytes(int(value) for value in action_mask)
    canonical = _CANONICAL_PREFIX + canonical_grid.tobytes(order="C") + action_bytes
    digest = hashlib.blake2b(canonical, digest_size=STATE_DIGEST_BYTES).hexdigest()
    canonical_grid.setflags(write=False)
    return (
        StateKey(digest=digest, canonical=canonical, legal_actions=action_mask),
        canonical_grid,
    )


@dataclass(frozen=True, slots=True)
class BackgroundConfig:
    """Conservative, color-agnostic background inference thresholds."""

    border_width: int = 1
    minimum_global_fraction: float = 0.5
    minimum_border_fraction: float = 0.5

    def __post_init__(self) -> None:
        if isinstance(self.border_width, bool) or not 1 <= self.border_width <= GRID_SIZE // 2:
            raise SceneError(f"background border_width must lie in [1, {GRID_SIZE // 2}]")
        for name, value in (
            ("minimum_global_fraction", self.minimum_global_fraction),
            ("minimum_border_fraction", self.minimum_border_fraction),
        ):
            if not 0.0 < float(value) <= 1.0:
                raise SceneError(f"{name} must lie in (0, 1]")


def _unique_mode(values: NDArray[np.int8]) -> tuple[int, int] | None:
    if values.size == 0:
        return None
    counts = np.bincount(values.astype(np.int64, copy=False), minlength=COLOR_COUNT)
    maximum = int(counts.max())
    winners = np.flatnonzero(counts == maximum)
    if len(winners) != 1:
        return None
    return int(winners[0]), maximum


def infer_background(
    frame: Any,
    *,
    ignored_mask: NDArray[np.bool_] | None = None,
    config: BackgroundConfig | None = None,
) -> int | None:
    """Infer a background color only when global and border evidence agree.

    Ambiguous scenes return ``None``.  In that case component extraction keeps
    every color instead of risking deletion of an interactive color.
    """

    settings = config or BackgroundConfig()
    grid = latest_grid(frame)
    ignored = _validate_mask(ignored_mask)
    eligible = ~ignored

    global_mode = _unique_mode(grid[eligible])
    if global_mode is None:
        return None
    candidate, global_count = global_mode

    border_eligible = _border_band(settings.border_width) & eligible
    border_mode = _unique_mode(grid[border_eligible])
    if border_mode is None or border_mode[0] != candidate:
        return None

    global_total = int(np.count_nonzero(eligible))
    border_total = int(np.count_nonzero(border_eligible))
    if global_total == 0 or border_total == 0:
        return None
    if global_count / global_total < settings.minimum_global_fraction:
        return None
    if border_mode[1] / border_total < settings.minimum_border_fraction:
        return None
    return candidate


_TRUSTED_CONSTRUCTION: ContextVar[bool] = ContextVar("scene_trusted_construction", default=False)


@dataclass(frozen=True, slots=True)
class SceneComponent:
    """One per-color four-connected component in deterministic scan order."""

    index: int
    color: int
    pixels_xy: tuple[tuple[int, int], ...]
    bbox_xyxy: tuple[int, int, int, int]
    centroid_xy: tuple[float, float]
    representative_xy: tuple[int, int]

    def __post_init__(self) -> None:
        if _TRUSTED_CONSTRUCTION.get():
            # REFLEX SPRINT: extract_components validates by construction --
            # it computed bbox/centroid/representative from the same arrays
            # one line earlier. Re-deriving them per component per frame was
            # measured at ~45% of per-action cost. External construction
            # still validates fully.
            return
        if self.index < 0:
            raise SceneError("component index cannot be negative")
        if not 0 <= self.color < COLOR_COUNT:
            raise SceneError(f"component color outside ARC palette: {self.color}")
        if not self.pixels_xy:
            raise SceneError("component pixels must be nonempty and unique")
        arr = np.asarray(self.pixels_xy, dtype=np.int64)
        keys = arr[:, 0] * GRID_SIZE + arr[:, 1]
        if np.unique(keys).size != keys.size:
            raise SceneError("component pixels must be nonempty and unique")
        if (arr < 0).any() or (arr >= GRID_SIZE).any():
            raise SceneError(
                f"component pixel outside grid: {tuple(arr[((arr < 0) | (arr >= GRID_SIZE)).any(axis=1)][0])}"
            )
        if self.representative_xy not in self.pixels_xy:
            raise SceneError("component representative must be an actual component pixel")
        xs = arr[:, 0]
        ys = arr[:, 1]
        expected_bbox = (int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max()))
        if self.bbox_xyxy != expected_bbox:
            raise SceneError("component bounding box does not match its pixels")
        expected_centroid = (float(np.mean(xs)), float(np.mean(ys)))
        if not all(
            math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-12)
            for actual, expected in zip(self.centroid_xy, expected_centroid, strict=True)
        ):
            raise SceneError("component centroid does not match its pixels")

    @property
    def area(self) -> int:
        """Number of cells in this component."""

        return len(self.pixels_xy)


def _representative_pixel(
    pixels_xy: tuple[tuple[int, int], ...], centroid_xy: tuple[float, float]
) -> tuple[int, int]:
    # REFLEX SPRINT: numpy lexicographic min with the identical (d2, y, x)
    # tie key -- measured ~40% of per-action cost lived in these Python
    # loops. np.lexsort's last key is primary, so keys are (x, y, d2).
    cx, cy = centroid_xy
    arr = np.asarray(pixels_xy, dtype=np.int64)
    d2 = (arr[:, 0] - cx) ** 2 + (arr[:, 1] - cy) ** 2
    best = int(np.lexsort((arr[:, 0], arr[:, 1], d2))[0])
    return int(arr[best, 0]), int(arr[best, 1])


_EXTRACTION_CACHE: dict[tuple[bytes, int | None, bytes, int], tuple[SceneComponent, ...]] = {}


def extract_components(
    frame: Any,
    *,
    background_color: int | None,
    ignored_mask: NDArray[np.bool_] | None = None,
    minimum_area: int = 1,
) -> tuple[SceneComponent, ...]:
    """Extract per-color four-connected components from observable cells."""

    if background_color is not None and not 0 <= background_color < COLOR_COUNT:
        raise SceneError(f"background color outside ARC palette: {background_color}")
    if isinstance(minimum_area, bool) or minimum_area < 1:
        raise SceneError("minimum component area must be a positive integer")

    grid = latest_grid(frame)
    ignored = _validate_mask(ignored_mask)
    observable = ~ignored
    # REFLEX SPRINT: extraction is a pure function of (grid, background,
    # mask); repeated frames dominate real play, so cache the frozen result.
    cache_key = (grid.tobytes(), background_color, ignored.tobytes(), minimum_area)
    cached = _EXTRACTION_CACHE.get(cache_key)
    if cached is not None:
        return cached
    colors = sorted(int(color) for color in np.unique(grid[observable]))
    components: list[SceneComponent] = []
    token = _TRUSTED_CONSTRUCTION.set(True)

    for color in colors:
        if color == background_color:
            continue
        labels, count = ndimage.label((grid == color) & observable, structure=_FOUR_CONNECTED)
        if not count:
            continue
        # REFLEX SPRINT: group all pixels by label in ONE stable pass instead
        # of scanning the grid per label (argwhere returned raster order;
        # a stable sort of raster-ordered coordinates by label preserves it).
        flat = labels.ravel()
        nz = np.flatnonzero(flat)
        order = nz[np.argsort(flat[nz], kind="stable")]
        label_of = flat[order]
        ys_all, xs_all = np.unravel_index(order, labels.shape)
        starts = np.searchsorted(label_of, np.arange(1, int(count) + 1))
        ends = np.append(starts[1:], label_of.size)
        for label_index in range(int(count)):
            lo, hi = int(starts[label_index]), int(ends[label_index])
            if hi - lo < minimum_area:
                continue
            xs = xs_all[lo:hi]
            ys = ys_all[lo:hi]
            pixels_xy = tuple(zip(xs.tolist(), ys.tolist(), strict=True))
            centroid = (float(np.mean(xs)), float(np.mean(ys)))
            components.append(
                SceneComponent(
                    index=len(components),
                    color=color,
                    pixels_xy=pixels_xy,
                    bbox_xyxy=(
                        int(xs.min()),
                        int(ys.min()),
                        int(xs.max()),
                        int(ys.max()),
                    ),
                    centroid_xy=centroid,
                    representative_xy=_representative_pixel(pixels_xy, centroid),
                )
            )
    _TRUSTED_CONSTRUCTION.reset(token)
    result = tuple(components)
    if len(_EXTRACTION_CACHE) >= 512:
        _EXTRACTION_CACHE.clear()
    _EXTRACTION_CACHE[cache_key] = result
    return result


@dataclass(frozen=True, slots=True)
class ClickCandidate:
    """One deterministic ACTION6 coordinate grounded in a component pixel."""

    x: int
    y: int
    color: int
    component_index: int
    tier: int

    def __post_init__(self) -> None:
        if not 0 <= self.x < GRID_SIZE or not 0 <= self.y < GRID_SIZE:
            raise SceneError(f"click coordinate outside grid: {(self.x, self.y)}")
        if not 0 <= self.color < COLOR_COUNT:
            raise SceneError(f"click color outside ARC palette: {self.color}")
        if self.component_index < 0 or self.tier < 0:
            raise SceneError("click component index and tier cannot be negative")

    @property
    def coordinate(self) -> tuple[int, int]:
        """Return the ARC ``(x, y)`` payload coordinate."""

        return self.x, self.y


def _next_farthest_pixel(
    component: SceneComponent, selected: list[tuple[int, int]]
) -> tuple[int, int] | None:
    # REFLEX SPRINT: identical semantics, vectorized. The reference kept the
    # FIRST strict maximum in pixels_xy (raster) order; np.argmax returns the
    # first occurrence, and excluded pixels get distance -1 exactly as the
    # reference's initial best_distance. Integer arithmetic throughout, so
    # values are bit-identical to the Python loop.
    pixels = np.asarray(component.pixels_xy, dtype=np.int64)
    chosen = np.asarray(selected, dtype=np.int64)
    diff = pixels[:, None, :] - chosen[None, :, :]
    distance = (diff * diff).sum(axis=2).min(axis=1)
    selected_set = set(selected)
    for i, pixel in enumerate(component.pixels_xy):
        if pixel in selected_set:
            distance[i] = -1
    if (distance < 0).all():
        return None
    best = int(np.argmax(distance))
    if distance[best] < 0:
        return None
    return component.pixels_xy[best]


def component_click_candidates(
    components: Iterable[SceneComponent],
    *,
    max_tier: int = 0,
    max_clicks_per_tier: int | None = None,
) -> tuple[ClickCandidate, ...]:
    """Build deterministic, deduplicated component-pixel click candidates.

    Tier zero contributes the actual pixel nearest each component's centroid.
    Every later tier adds the pixel farthest from that component's prior
    selections, giving deterministic spatial coverage without inventing grid
    coordinates or clicking inferred background.
    """

    if (
        isinstance(max_tier, bool)
        or not isinstance(max_tier, (int, np.integer))
        or not 0 <= max_tier < GRID_SIZE
    ):
        raise SceneError(f"max_tier must lie in [0, {GRID_SIZE - 1}]")
    if max_clicks_per_tier is not None and (
        isinstance(max_clicks_per_tier, bool)
        or not isinstance(max_clicks_per_tier, (int, np.integer))
        or max_clicks_per_tier < 1
    ):
        raise SceneError("max_clicks_per_tier must be a positive integer or None")
    ordered = tuple(components)
    if tuple(component.index for component in ordered) != tuple(range(len(ordered))):
        raise SceneError("components must have contiguous indices in deterministic order")

    selected: dict[int, list[tuple[int, int]]] = {component.index: [] for component in ordered}
    emitted: set[tuple[int, int]] = set()
    candidates: list[ClickCandidate] = []

    for tier in range(max_tier + 1):
        tier_candidates: list[ClickCandidate] = []
        for component in ordered:
            if tier == 0:
                coordinate = component.representative_xy
            else:
                coordinate = _next_farthest_pixel(component, selected[component.index])
                if coordinate is None:
                    continue
            selected[component.index].append(coordinate)
            if coordinate in emitted:
                continue
            emitted.add(coordinate)
            tier_candidates.append(
                ClickCandidate(
                    x=coordinate[0],
                    y=coordinate[1],
                    color=component.color,
                    component_index=component.index,
                    tier=tier,
                )
            )
        candidates.extend(
            _coverage_round_robin(
                tier_candidates,
                limit=max_clicks_per_tier,
                group=lambda candidate: (
                    candidate.color,
                    candidate.y // COARSE_SPATIAL_BIN_SIZE,
                    candidate.x // COARSE_SPATIAL_BIN_SIZE,
                ),
            )
        )
    return tuple(candidates)


def _coverage_round_robin[GroupedItem](
    items: Iterable[GroupedItem],
    *,
    limit: int | None,
    group: Callable[[GroupedItem], tuple[int, int, int]],
) -> tuple[GroupedItem, ...]:
    """Select deterministically across groups before revisiting any group."""

    ordered_items = tuple(items)
    if limit is None or len(ordered_items) <= limit:
        return ordered_items

    groups: dict[tuple[int, int, int], list[GroupedItem]] = {}
    for item in ordered_items:
        groups.setdefault(group(item), []).append(item)

    selected: list[GroupedItem] = []
    depth = 0
    ordered_keys = sorted(groups)
    while len(selected) < limit:
        added = False
        for key in ordered_keys:
            members = groups[key]
            if depth < len(members):
                selected.append(members[depth])
                added = True
                if len(selected) == limit:
                    break
        if not added:
            break
        depth += 1
    return tuple(selected)


def components_for_coverage(
    components: Iterable[SceneComponent], *, limit: int | None
) -> tuple[SceneComponent, ...]:
    """Cap components without scan-order starvation.

    Components are grouped by color and the coarse spatial bin containing
    their representative.  Round-robin selection takes one from every group
    before taking a second from any group.  Selected components are reindexed
    contiguously for direct use by :func:`component_click_candidates`.
    """

    if limit is not None and (
        isinstance(limit, bool) or not isinstance(limit, (int, np.integer)) or limit < 1
    ):
        raise SceneError("component limit must be a positive integer or None")
    selected = _coverage_round_robin(
        components,
        limit=limit,
        group=lambda component: (
            component.color,
            component.representative_xy[1] // COARSE_SPATIAL_BIN_SIZE,
            component.representative_xy[0] // COARSE_SPATIAL_BIN_SIZE,
        ),
    )
    return tuple(replace(component, index=index) for index, component in enumerate(selected))


@dataclass(frozen=True, slots=True)
class SceneConfig:
    """Complete configuration for stateful scene extraction."""

    volatile_mask: VolatileMaskConfig = field(default_factory=VolatileMaskConfig)
    background: BackgroundConfig = field(default_factory=BackgroundConfig)
    minimum_component_area: int = 1
    max_click_tier: int = 0
    component_limit: int | None = None
    max_clicks_per_tier: int | None = None

    def __post_init__(self) -> None:
        if isinstance(self.minimum_component_area, bool) or self.minimum_component_area < 1:
            raise SceneError("minimum_component_area must be a positive integer")
        if isinstance(self.max_click_tier, bool) or not 0 <= self.max_click_tier < GRID_SIZE:
            raise SceneError(f"max_click_tier must lie in [0, {GRID_SIZE - 1}]")
        if self.component_limit is not None and (
            isinstance(self.component_limit, bool)
            or not isinstance(self.component_limit, (int, np.integer))
            or self.component_limit < 1
        ):
            raise SceneError("component_limit must be a positive integer or None")
        if self.max_clicks_per_tier is not None and (
            isinstance(self.max_clicks_per_tier, bool)
            or not isinstance(self.max_clicks_per_tier, (int, np.integer))
            or self.max_clicks_per_tier < 1
        ):
            raise SceneError("max_clicks_per_tier must be a positive integer or None")


@dataclass(frozen=True, slots=True)
class SceneObservation:
    """Validated policy-facing view of one ARC observation."""

    grid: NDArray[np.int8]
    volatile_mask: NDArray[np.bool_]
    canonical_grid: NDArray[np.uint8]
    mask_comparisons: int
    mask_frozen: bool
    mask_just_frozen: bool
    background_color: int | None
    components: tuple[SceneComponent, ...]
    click_candidates: tuple[ClickCandidate, ...]
    state_key: StateKey

    def __post_init__(self) -> None:
        for name, array, dtype in (
            ("grid", self.grid, np.dtype(np.int8)),
            ("volatile_mask", self.volatile_mask, np.dtype(np.bool_)),
            ("canonical_grid", self.canonical_grid, np.dtype(np.uint8)),
        ):
            if array.shape != (GRID_SIZE, GRID_SIZE) or array.dtype != dtype:
                raise SceneError(f"scene {name} has an invalid shape or dtype")
            if array.flags.writeable:
                raise SceneError(f"scene {name} must be read-only")
        if self.mask_just_frozen and not self.mask_frozen:
            raise SceneError("mask_just_frozen requires mask_frozen")
        if self.background_color is not None and not 0 <= self.background_color < COLOR_COUNT:
            raise SceneError("scene background color is invalid")
        by_index = {component.index: component for component in self.components}
        for candidate in self.click_candidates:
            component = by_index.get(candidate.component_index)
            if component is None or candidate.coordinate not in component.pixels_xy:
                raise SceneError("click candidate is not grounded in its declared component")


class SceneTracker:
    """Stateful façade used once per turn by a policy."""

    def __init__(self, config: SceneConfig | None = None) -> None:
        self.config = config or SceneConfig()
        self.volatile_mask = FrozenVolatileMask(self.config.volatile_mask)

    def observe(self, frame: Any, available_action_ids: Iterable[int]) -> SceneObservation:
        """Extract the latest strict grid and all generic scene primitives."""

        grid = latest_grid(frame)
        snapshot = self.volatile_mask.observe(grid)
        background = infer_background(
            grid,
            ignored_mask=snapshot.mask,
            config=self.config.background,
        )
        components = components_for_coverage(
            extract_components(
                grid,
                background_color=background,
                ignored_mask=snapshot.mask,
                minimum_area=self.config.minimum_component_area,
            ),
            limit=self.config.component_limit,
        )
        clicks = component_click_candidates(
            components,
            max_tier=self.config.max_click_tier,
            max_clicks_per_tier=self.config.max_clicks_per_tier,
        )
        state_key, canonical_grid = canonical_state_key(
            grid,
            available_action_ids,
            volatile_mask=snapshot.mask,
        )
        return SceneObservation(
            grid=_readonly_copy(grid, np.dtype(np.int8)),
            volatile_mask=snapshot.mask,
            canonical_grid=canonical_grid,
            mask_comparisons=snapshot.comparisons,
            mask_frozen=snapshot.frozen,
            mask_just_frozen=snapshot.just_frozen,
            background_color=background,
            components=components,
            click_candidates=clicks,
            state_key=state_key,
        )
