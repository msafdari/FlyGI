"""Clean-room tests for generic scene extraction and state identity."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pytest

from flygi.controller.scene import (
    BackgroundConfig,
    FrozenVolatileMask,
    SceneConfig,
    SceneError,
    SceneTracker,
    VolatileMaskConfig,
    canonical_state_key,
    component_click_candidates,
    extract_components,
    infer_background,
)


@dataclass
class Frame:
    frame: list[np.ndarray]


def _grid(background: int = 7) -> np.ndarray:
    return np.full((64, 64), background, dtype=np.int8)


def _slow_volatility_frames() -> list[np.ndarray]:
    frames = [_grid() for _ in range(8)]
    # Three changes across the six comparisons used to freeze the learner.
    frames[2][0, 10] = 5
    frames[3][0, 10] = 5
    frames[6][0, 10] = 5
    return frames


def test_slow_border_volatility_is_observed_then_frozen() -> None:
    tracker = FrozenVolatileMask(
        VolatileMaskConfig(
            border_width=2,
            comparisons_to_freeze=6,
            minimum_changes=2,
            minimum_change_rate=0.25,
        )
    )
    frames = _slow_volatility_frames()
    snapshots = [tracker.observe(frame) for frame in frames[:7]]

    assert not snapshots[-2].frozen
    assert snapshots[-1].frozen
    assert snapshots[-1].just_frozen
    assert snapshots[-1].mask[0, 10]

    frozen = snapshots[-1].mask.copy()
    after = tracker.observe(frames[7])
    assert after.frozen
    assert not after.just_frozen
    assert np.array_equal(after.mask, frozen)


def test_interior_motion_is_never_inferred_as_ui() -> None:
    tracker = FrozenVolatileMask(
        VolatileMaskConfig(
            border_width=3,
            comparisons_to_freeze=4,
            minimum_changes=2,
            minimum_change_rate=0.25,
        )
    )
    for step in range(5):
        grid = _grid()
        grid[30, 30] = 2 if step % 2 else 4
        snapshot = tracker.observe(grid)

    assert snapshot.frozen
    assert not snapshot.mask[30, 30]
    assert not snapshot.mask[3:-3, 3:-3].any()


def test_state_hash_stabilizes_for_masked_border_changes_after_freeze() -> None:
    config = SceneConfig(
        volatile_mask=VolatileMaskConfig(
            border_width=2,
            comparisons_to_freeze=6,
            minimum_changes=2,
            minimum_change_rate=0.25,
        )
    )
    tracker = SceneTracker(config)
    for grid in _slow_volatility_frames()[:7]:
        scene = tracker.observe(grid, (1, 2, 6))
    assert scene.mask_frozen

    first = _grid()
    first[0, 10] = 5
    second = _grid()
    second[0, 10] = 12
    first_scene = tracker.observe(first, (1, 2, 6))
    second_scene = tracker.observe(second, (1, 2, 6))

    assert first_scene.state_key.digest == second_scene.state_key.digest
    assert first_scene.state_key.canonical == second_scene.state_key.canonical
    assert first_scene.canonical_grid[0, 10] == 16


def test_legal_action_mask_is_part_of_state_identity() -> None:
    grid = _grid()
    first, _ = canonical_state_key(grid, (1, 2))
    reordered, _ = canonical_state_key(grid, (2, 1))
    different, _ = canonical_state_key(grid, (1, 3))

    assert first.digest == reordered.digest
    assert first.canonical == reordered.canonical
    assert first.digest != different.digest
    assert first.canonical != different.canonical
    assert len(first.digest) == 32


def test_legal_action_validation_rejects_duplicates_and_out_of_range_ids() -> None:
    grid = _grid()
    with pytest.raises(SceneError, match="duplicate"):
        canonical_state_key(grid, (1, 1))
    with pytest.raises(SceneError, match="must lie"):
        canonical_state_key(grid, (8,))


def test_components_are_four_connected_not_diagonally_connected() -> None:
    grid = _grid()
    grid[10, 10] = 3
    grid[11, 11] = 3

    components = extract_components(grid, background_color=7)
    color_three = [component for component in components if component.color == 3]

    assert len(color_three) == 2
    assert [component.pixels_xy for component in color_three] == [((10, 10),), ((11, 11),)]


def test_background_inference_is_not_tied_to_color_zero() -> None:
    grid = _grid(background=11)
    grid[20:24, 30:34] = 4

    assert infer_background(grid) == 11
    components = extract_components(grid, background_color=infer_background(grid))
    assert {component.color for component in components} == {4}


def test_ambiguous_background_is_kept_instead_of_guessed() -> None:
    grid = np.empty((64, 64), dtype=np.int8)
    grid[:, :32] = 6
    grid[:, 32:] = 9

    assert infer_background(grid) is None


def test_hollow_component_centroid_snaps_to_an_actual_pixel() -> None:
    grid = _grid()
    grid[20:25, 20] = 3
    grid[20:25, 24] = 3
    grid[20, 20:25] = 3
    grid[24, 20:25] = 3

    component = extract_components(grid, background_color=7)[0]

    assert component.centroid_xy == (22.0, 22.0)
    assert grid[22, 22] == 7
    assert component.representative_xy in component.pixels_xy
    x, y = component.representative_xy
    assert grid[y, x] == component.color


def test_click_candidates_are_actual_foreground_pixels() -> None:
    grid = _grid(background=13)
    grid[8:12, 9:14] = 2
    grid[40, 50] = 5
    background = infer_background(grid)
    components = extract_components(grid, background_color=background)

    candidates = component_click_candidates(components, max_tier=3)

    assert candidates
    assert len({candidate.coordinate for candidate in candidates}) == len(candidates)
    for candidate in candidates:
        assert grid[candidate.y, candidate.x] != background
        assert grid[candidate.y, candidate.x] == candidate.color
        assert candidate.coordinate in components[candidate.component_index].pixels_xy


def test_click_candidate_tiers_are_deterministic_and_monotonic() -> None:
    grid = _grid()
    grid[10:15, 10:15] = 2
    components = extract_components(grid, background_color=7)

    tier_zero = component_click_candidates(components, max_tier=0)
    tier_two_first = component_click_candidates(components, max_tier=2)
    tier_two_second = component_click_candidates(components, max_tier=2)

    assert tier_two_first == tier_two_second
    assert tier_two_first[: len(tier_zero)] == tier_zero
    assert [candidate.tier for candidate in tier_two_first] == [0, 1, 2]
    assert len({candidate.coordinate for candidate in tier_two_first}) == 3


def test_component_cap_round_robins_over_more_than_64_spatial_groups() -> None:
    grid = _grid()
    # Two isolated components in every 8x8 spatial bin: 128 components total.
    for bin_y in range(8):
        for bin_x in range(8):
            y = bin_y * 8 + 1
            x = bin_x * 8 + 1
            grid[y, x] = 2
            grid[y + 2, x + 2] = 2

    config = SceneConfig(
        component_limit=64,
        max_click_tier=1,
        max_clicks_per_tier=64,
    )
    first = SceneTracker(config).observe(grid, (1, 6))
    second = SceneTracker(config).observe(grid, (1, 6))

    assert len(first.components) == 64
    assert len(first.click_candidates) == 64
    assert first.components == second.components
    assert first.click_candidates == second.click_candidates
    represented_bins = {
        (candidate.y // 8, candidate.x // 8) for candidate in first.click_candidates
    }
    assert represented_bins == {(y, x) for y in range(8) for x in range(8)}
    assert {candidate.tier for candidate in first.click_candidates} == {0}

    click_capped = SceneTracker(SceneConfig(max_clicks_per_tier=64)).observe(grid, (1, 6))
    assert len(click_capped.components) == 128
    assert len(click_capped.click_candidates) == 64
    assert {
        (candidate.y // 8, candidate.x // 8) for candidate in click_capped.click_candidates
    } == represented_bins


def test_tracker_uses_the_last_subframe_and_returns_read_only_arrays() -> None:
    first = _grid(background=3)
    last = _grid(background=12)
    last[30, 30] = 6
    scene = SceneTracker().observe(Frame(frame=[first, last]), (1, 6))

    assert np.array_equal(scene.grid, last)
    assert scene.background_color == 12
    assert not scene.grid.flags.writeable
    assert not scene.volatile_mask.flags.writeable
    assert not scene.canonical_grid.flags.writeable


def test_background_configuration_is_conservative_and_validated() -> None:
    grid = _grid()
    grid[:32] = 2
    strict = BackgroundConfig(minimum_global_fraction=0.75)

    assert infer_background(grid, config=strict) is None
    with pytest.raises(SceneError):
        BackgroundConfig(minimum_border_fraction=0.0)
