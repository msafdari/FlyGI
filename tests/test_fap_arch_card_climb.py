"""Offline acceptance tests for the dc22 card_climb archetype.

Oracle: docs/fap_extension_20260928/dc22/ -- the render dumps there are
MEASURED frames of the real game (drive.py / probe scripts), and the
verified programs prog_l1/l2/l3.json completed levels 1-3 against the
offline arcade (verify_l123_stdout.txt, score 0 -> 3). The parser tests
below pin the parse of those measured frames to the coordinates the
verified programs actually clicked; the planner tests run the archetype
closed-loop against a toy simulator that implements the decoded grammar
(2-cell moves refused into background, involutive card toggles, {6,7}
pad teleports), which is a MODEL of the game, not the game -- the
end-to-end evidence is the executor run recorded in the module docstring
and worklog (3 levels, matching the dossier's verified 3).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from flygi.controller.fap_archetypes.card_climb import CardClimbArchetype
from flygi.controller.fap_library import Step

ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "docs/fap_extension_20260928/dc22"
RECOGNIZER_NPZ = ROOT / "results/diagnostics/recognizer_frames.npz"

FRAME, BG, PANEL, DASH, STRUCT, CARRIER, PLAYER = 3, 4, 5, 0, 2, 11, 14
ROW0, ROW1, SEP = 10, 54, 32


def load_render(path: Path) -> np.ndarray:
    rows = []
    for line in path.read_text().splitlines()[1:]:
        rows.append([int(ch, 16) for ch in line[4:]])
    return np.asarray(rows, dtype=np.int16)


# --------------------------------------------------------------- board kit


def blank_board() -> np.ndarray:
    g = np.full((64, 64), FRAME, dtype=np.int16)
    g[ROW0:ROW1, :SEP] = BG
    g[ROW0:ROW1, SEP:] = PANEL
    for r in range(ROW0, ROW1):
        if ((r - ROW0) // 2) % 2 == 0:
            g[r, SEP : SEP + 2] = DASH
    return g


def add_card(g: np.ndarray, colour: int, top: int = 17) -> None:
    g[top : top + 5, 45:52] = colour


class ToySim:
    """Closed-loop stub implementing the decoded dc22 grammar.

    The world array holds the field without the player; ``display`` draws
    the 2x2 player over it. Moves are 2-cell steps refused when any
    destination cell is background (or listed in ``refuse``, standing in
    for an unwalkable colour the model does not know about). A click on a
    card blob flips that card's toggle cells; a click on the teleport
    card moves the player pad-to-pad when it stands on one.
    """

    def __init__(self, world, player, carrier, toggles=None, teleport=None, refuse=None):
        self.world = world.copy()
        self.pos = player
        self.carrier = carrier
        self.toggles = toggles or {}  # card colour -> list[(r, c, off, on)]
        self.state = {colour: 0 for colour in self.toggles}
        self.teleport = teleport  # (card colour, pad_a, pad_b) | None
        self.refuse = refuse or set()
        self.clicks = []

    def display(self) -> np.ndarray:
        g = self.world.copy()
        r, c = self.pos
        g[r : r + 2, c : c + 2] = PLAYER
        return g

    def apply(self, step: Step) -> None:
        if step.action == 6:
            colour = int(self.world[step.y, step.x])
            self.clicks.append(colour)
            if colour in self.toggles:
                bit = self.state[colour] ^ 1
                self.state[colour] = bit
                for r, c, off, on in self.toggles[colour]:
                    self.world[r, c] = on if bit else off
            if self.teleport is not None and colour == self.teleport[0]:
                _, pad_a, pad_b = self.teleport
                if self.pos == pad_a:
                    self.pos = pad_b
                elif self.pos == pad_b:
                    self.pos = pad_a
            return
        dr, dc = {1: (-1, 0), 2: (1, 0), 3: (0, -1), 4: (0, 1)}[step.action]
        nr, nc = self.pos[0] + 2 * dr, self.pos[1] + 2 * dc
        if not (ROW0 <= nr and nr + 1 < ROW1 and 0 <= nc and nc + 1 < SEP):
            return
        if (nr, nc) in self.refuse:
            return
        if (self.world[nr : nr + 2, nc : nc + 2] == BG).any():
            return
        self.pos = (nr, nc)


def drive(arch: CardClimbArchetype, sim: ToySim, max_steps: int = 120) -> int:
    for i in range(max_steps):
        if sim.pos == sim.carrier:
            return i
        g = sim.display()
        parse = arch.match(g)
        assert parse is not None, f"parser abstained mid-game at step {i}"
        steps = arch.next_actions(parse, g)
        assert steps, f"planner abstained at step {i} (pos={sim.pos})"
        sim.apply(steps[0])
    raise AssertionError(f"carrier not reached in {max_steps} steps (pos={sim.pos})")


# ------------------------------------------------- parser: measured frames


def test_parses_measured_l1_frame_to_verified_click_targets():
    g = load_render(DOSSIER / "after_click_card8.txt")
    parse = CardClimbArchetype().match(g)
    assert parse is not None
    assert parse.player == (40, 10)
    assert parse.carrier == (20, 24)
    assert parse.sep == 32
    # The verified L1 program (prog_l1.json) clicks exactly (48,19) and
    # (48,36); the parser must land its card clicks inside those blobs.
    assert [c.click for c in parse.cards] == [(48, 19), (48, 36)]
    assert [c.colour for c in parse.cards] == [8, 9]
    assert parse.pads == []


def test_parses_measured_l3_frame_with_teleport_pads():
    g = load_render(DOSSIER / "l2_final.txt")  # the L3 entry board
    parse = CardClimbArchetype().match(g)
    assert parse is not None
    assert parse.player == (18, 30)
    assert parse.carrier == (38, 32)
    pads = {pos for pos, pair in parse.pads}
    pairs = {pair for pos, pair in parse.pads}
    assert pads == {(16, 6), (46, 12)}
    assert pairs == {frozenset({6, 7})}
    # 3 visible cards before the F pickup, 4 after (l3_cardF1.txt).
    assert len(parse.cards) == 3
    later = CardClimbArchetype().match(load_render(DOSSIER / "l3_cardF1.txt"))
    assert later is not None and len(later.cards) == 4


# ------------------------------------------------------ parser: abstention


def test_abstains_on_random_grids():
    rng = np.random.default_rng(0)
    arch = CardClimbArchetype()
    for _ in range(40):
        g = rng.integers(0, 16, size=(64, 64), dtype=np.int16)
        assert arch.match(g) is None


def test_abstains_on_structured_non_matching_boards():
    arch = CardClimbArchetype()
    # A dc22-like board missing each strict signature element in turn.
    base = blank_board()
    base[38:44, 8:14] = STRUCT
    base[40:42, 10:12] = PLAYER
    base[20:22, 24:26] = CARRIER
    add_card(base, 8)
    assert arch.match(base) is not None  # sanity: the full signature parses

    no_carrier = base.copy()
    no_carrier[20:22, 24:26] = BG
    assert arch.match(no_carrier) is None

    two_players = base.copy()
    two_players[46:48, 20:22] = PLAYER
    assert arch.match(two_players) is None

    off_lattice = base.copy()
    off_lattice[20:22, 24:26] = BG
    off_lattice[20:22, 25:27] = CARRIER  # odd column parity vs the player
    assert arch.match(off_lattice) is None

    no_cards = base.copy()
    no_cards[ROW0:ROW1, SEP + 2 :] = PANEL
    assert arch.match(no_cards) is None

    no_separator = base.copy()
    for r in range(ROW0, ROW1):
        no_separator[r, SEP : SEP + 2] = PANEL
    assert arch.match(no_separator) is None


@pytest.mark.skipif(not RECOGNIZER_NPZ.exists(), reason="recognizer frames absent")
def test_negative_audit_recognizer_frames():
    z = np.load(RECOGNIZER_NPZ)
    arch = CardClimbArchetype()
    offenders = []
    for key in z.files:
        if key.startswith("dc22"):
            continue
        for i, frame in enumerate(z[key]):
            if arch.match(np.asarray(frame, dtype=np.int16)) is not None:
                offenders.append((key, i))
    assert offenders == []


# ------------------------------------------------------------ planner unit


def test_planner_walks_a_direct_bridge():
    world = blank_board()
    world[20:42, 10:12] = STRUCT  # vertical corridor
    world[20:22, 10:26] = STRUCT  # top band
    world[20:22, 24:26] = CARRIER
    add_card(world, 8)
    toggles = {8: [(46, 24, BG, 9), (46, 25, BG, 9), (47, 24, BG, 9), (47, 25, BG, 9)]}
    sim = ToySim(world, player=(40, 10), carrier=(20, 24), toggles=toggles)
    arch = CardClimbArchetype()
    drive(arch, sim)
    # 2 fingerprint clicks (click + restoring re-click), then pure moves.
    assert sim.clicks == [8, 8]
    assert sim.state[8] == 0


def test_planner_toggles_a_card_to_bridge_a_gap():
    world = blank_board()
    world[20:42, 10:12] = STRUCT
    world[20:22, 10:16] = STRUCT
    world[20:22, 20:26] = STRUCT
    world[20:22, 24:26] = CARRIER
    add_card(world, 8)
    # the card's item is a plank filling the top-band gap (involutive)
    toggles = {8: [(r, c, BG, 9) for r in (20, 21) for c in (16, 17, 18, 19)]}
    sim = ToySim(world, player=(40, 10), carrier=(20, 24), toggles=toggles)
    arch = CardClimbArchetype()
    drive(arch, sim)
    # fingerprint pair plus exactly one planned click, leaving the plank in
    assert sim.clicks == [8, 8, 8]
    assert sim.state[8] == 1


def test_planner_uses_pad_teleport():
    world = blank_board()
    world[30:42, 10:12] = STRUCT  # corridor up to pad A
    world[28, 10], world[28, 11] = 6, 7  # pad A checker
    world[29, 10], world[29, 11] = 7, 6
    world[20, 24], world[20, 25] = 6, 7  # pad B checker
    world[21, 24], world[21, 25] = 7, 6
    world[20:22, 26:30] = STRUCT
    world[20:22, 28:30] = CARRIER
    add_card(world, 6)
    sim = ToySim(
        world,
        player=(40, 10),
        carrier=(20, 28),
        teleport=(6, (28, 10), (20, 24)),
    )
    arch = CardClimbArchetype()
    drive(arch, sim)
    # the home fingerprint click is a no-op (marked inert), the teleport
    # click happens on the pad; nothing else is clickable
    assert sim.clicks.count(6) == 2


def test_planner_learns_a_refused_move_and_detours():
    world = blank_board()
    world[20:42, 10:12] = STRUCT  # corridor A (short route)
    world[30:32, 10:12] = 12  # looks walkable to the model...
    world[20:42, 16:18] = STRUCT  # corridor B (detour)
    world[40:42, 10:18] = STRUCT  # bottom band joins A and B
    world[20:22, 6:18] = STRUCT  # top band
    world[20:22, 6:8] = CARRIER
    add_card(world, 8)
    toggles = {8: [(46, 24, BG, 9), (46, 25, BG, 9), (47, 24, BG, 9), (47, 25, BG, 9)]}
    sim = ToySim(
        world,
        player=(40, 10),
        carrier=(20, 6),
        toggles=toggles,
        refuse={(30, 10)},  # ...but the game refuses entry
    )
    arch = CardClimbArchetype()
    drive(arch, sim)
    assert (((32, 10), 1, frozenset()) in arch._banned) or (
        ((28, 10), 2, frozenset()) in arch._banned
    )


def test_planner_abstains_when_nothing_reaches_the_carrier():
    world = blank_board()
    world[38:44, 8:14] = STRUCT
    world[20:22, 24:26] = CARRIER  # isolated island
    add_card(world, 8)
    toggles = {8: [(46, 24, BG, 9), (46, 25, BG, 9), (47, 24, BG, 9), (47, 25, BG, 9)]}
    sim = ToySim(world, player=(40, 10), carrier=(20, 24), toggles=toggles)
    arch = CardClimbArchetype()
    emitted = []
    for _ in range(8):
        g = sim.display()
        parse = arch.match(g)
        assert parse is not None
        steps = arch.next_actions(parse, g)
        emitted.append(steps)
        if not steps:
            break
        sim.apply(steps[0])
    assert emitted[-1] == []  # abstained after the fingerprint pair
    assert sim.pos == (40, 10)  # never wandered
