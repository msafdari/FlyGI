"""Reflex sprint: the vectorized scene paths must be BIT-identical to the
reference Python implementations on randomized grids -- component identity
feeds canonical state keys, so any divergence silently forks every arm."""

from __future__ import annotations

import numpy as np

from flygi.controller.scene import (
    SceneComponent,
    _next_farthest_pixel,
    _representative_pixel,
    component_click_candidates,
    extract_components,
)


def _reference_representative(pixels_xy, centroid_xy):
    cx, cy = centroid_xy
    return min(
        pixels_xy,
        key=lambda p: ((p[0] - cx) ** 2 + (p[1] - cy) ** 2, p[1], p[0]),
    )


def _reference_farthest(component, selected):
    selected_set = set(selected)
    best, best_distance = None, -1
    for pixel in component.pixels_xy:
        if pixel in selected_set:
            continue
        distance = min(
            (pixel[0] - prior[0]) ** 2 + (pixel[1] - prior[1]) ** 2 for prior in selected
        )
        if distance > best_distance:
            best, best_distance = pixel, distance
    return best


class _Frame:
    def __init__(self, grid):
        self.frame = [grid]


def test_extract_and_candidates_match_reference_on_random_grids() -> None:
    rng = np.random.default_rng(20260927)
    for trial in range(120):
        grid = rng.integers(0, rng.integers(2, 9), size=(64, 64)).astype(np.int8)
        components = extract_components(
            _Frame(grid), background_color=int(grid.ravel()[0]), minimum_area=1
        )
        # representative equivalence per component
        for component in components:
            assert component.representative_xy == _reference_representative(
                component.pixels_xy, component.centroid_xy
            ), f"trial {trial} component {component.index}"
        # farthest-point equivalence across three tiers of selections
        for component in components[:20]:
            selected = [component.representative_xy]
            for _ in range(3):
                ours = _next_farthest_pixel(component, selected)
                ref = _reference_farthest(component, selected)
                assert ours == ref, f"trial {trial} component {component.index}"
                if ours is None:
                    break
                selected.append(ours)
        # full candidate pipeline determinism
        a = component_click_candidates(components, max_tier=2, max_clicks_per_tier=64)
        b = component_click_candidates(components, max_tier=2, max_clicks_per_tier=64)
        assert a == b
