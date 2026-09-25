"""H-TAXIS: the spatial-taxis model on a synthetic avatar world."""

from __future__ import annotations

import numpy as np

from flygi.controller.taxis import SpatialTaxis


def _world(avatar_rc: tuple[int, int], goal_rc: tuple[int, int] = (50, 50)) -> np.ndarray:
    grid = np.full((64, 64), 4, dtype=np.int8)
    r, c = avatar_rc
    grid[r : r + 3, c : c + 3] = 9  # avatar sprite
    gr, gc = goal_rc
    grid[gr : gr + 2, gc : gc + 2] = 14  # unique rare goal
    return grid


_STEP = {1: (-2, 0), 2: (2, 0), 3: (0, -2), 4: (0, 2)}


def _teach(taxis: SpatialTaxis, start=(10, 10), moves=(1, 2, 3, 4) * 5):
    pos = list(start)
    grid = _world(tuple(pos))
    for aid in moves:
        dr, dc = _STEP[aid]
        new = [min(max(pos[0] + dr, 0), 60), min(max(pos[1] + dc, 0), 60)]
        new_grid = _world(tuple(new))
        taxis.observe_transition(grid, aid, new_grid)
        pos, grid = new, new_grid
    return tuple(pos), grid


def test_learns_movers_and_pulls_toward_goal() -> None:
    taxis = SpatialTaxis()
    pos, grid = _teach(taxis)
    assert len(taxis._movers) >= 2, taxis._movers
    # Avatar at ~(10,10)-ish, goal at (50,50): down (2) and right (4) reduce
    # distance; up (1) and left (3) increase it.
    down, right = taxis.bonus(2, grid), taxis.bonus(4, grid)
    up, left = taxis.bonus(1, grid), taxis.bonus(3, grid)
    assert down > 0 and right > 0, (down, right)
    assert up < 0 and left < 0, (up, left)


def test_comparison_random_target_differs() -> None:
    real = SpatialTaxis()
    control = SpatialTaxis(random_target_seed=7)

    # world with TWO stable rare objects: the true goal (rarest) + decoy
    def world2(avatar_rc):
        g = _world(avatar_rc)
        g[5:8, 55:58] = 13  # decoy component (9 cells, rarer than field)
        return g

    pos = [10, 10]
    grid = world2(tuple(pos))
    for aid in (1, 2, 3, 4) * 5:
        dr, dc = _STEP[aid]
        new = [min(max(pos[0] + dr, 0), 60), min(max(pos[1] + dc, 0), 60)]
        ng = world2(tuple(new))
        real.observe_transition(grid, aid, ng)
        control.observe_transition(grid, aid, ng)
        pos, grid = new, ng
    real.bonus(2, grid)  # forces target selection
    # The control picks an arbitrary stable component; across a few seeds it
    # must be able to land on the decoy while the real rule stays on the
    # rarest (true) goal.
    diverged = False
    for seed in range(10):
        c2 = SpatialTaxis(random_target_seed=seed)
        c2._movers = dict(control._movers)
        c2._avatar = control._avatar
        c2._recent_grids = list(control._recent_grids)
        c2._transitions = control._transitions
        c2._border_change = control._border_change.copy()
        c2.bonus(2, grid)
        if c2._target is not None and real._target is not None and c2._target != real._target:
            diverged = True
            break
    assert diverged, (real._target,)


def test_no_avatar_no_pull() -> None:
    taxis = SpatialTaxis()
    grid = _world((10, 10))
    assert taxis.bonus(2, grid) == 0.0  # nothing learned yet -> inert


def test_timer_cells_excluded() -> None:
    taxis = SpatialTaxis()
    grid = _world((10, 10))
    # feed transitions where ONLY a border timer cell changes
    for t in range(30):
        g2 = grid.copy()
        g2[63, t % 64] = 1
        taxis.observe_transition(grid, 2, g2)
        grid = g2
    assert 2 not in taxis._movers  # clock ticks must not register as movement


def test_deterministic() -> None:
    a, b = SpatialTaxis(), SpatialTaxis()
    _, ga = _teach(a)
    _, gb = _teach(b)
    assert [a.bonus(i, ga) for i in (1, 2, 3, 4)] == [b.bonus(i, gb) for i in (1, 2, 3, 4)]
