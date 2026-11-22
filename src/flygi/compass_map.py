"""EPG bridge label -> ellipsoid-body ring position. The ONE place the
compass label map lives (AC-1 and AC-B1, and their dated amendment).

Every compass instrument turns an EPG instance label such as
``EPG(PB08)_L3`` (protocerebral-bridge half L or R, glomerulus 1..8) into
a position on the sixteen-half-wedge ring of the ellipsoid body, or into
one of eight ring units. Until 2026-11-21 nine scripts each carried their
own copy of that expression. They now call the functions below.

Two maps are kept, by name:

``registered``  AC-1 as frozen 2026-10-10 (carried from cx_scratchpad /
    cx_ring, 2026-09-27) and AC-B1 as frozen 2026-10-31. Kept ONLY so
    the registered runs stay reproducible to the last digit. It places
    L_k next to R_k::

        index(L_k) = 2 (k - 1)        index(R_k) = 2 (k - 1) + 1
        unit(L_k)  = unit(R_k) = (k - 1) mod 8

``amended``     AC-1 / AC-B1 as amended 2026-11-21 (instrument-bug
    finding, docs/arenas/compass_map_amendment_20261121.md). The right
    half keeps its registered angle; the left half is reflected::

        index(R_k) = (2 (k - 1) + 1) mod 16      angle 22.5 + 45 (k - 1)
        index(L_k) = (-2 (k - 1)) mod 16         angle 360 - 45 (k - 1)
        unit(R_k)  = (k - 1) mod 8
        unit(L_k)  = (8 - k) mod 8               (L_k shares with R_(9-k))

    Ring order by index 0..15:
    L1 R1 L8 R2 L7 R3 L6 R4 L5 R5 L4 R6 L3 R7 L2 R8.

THE FAULT (MEASURED 2026-11-21, recorded in the amendment): the
registered map ran both bridge halves round the ring in the SAME
direction. In the fly they run in opposite directions, so the registered
map reflected the left half-ring relative to the right one. That is not
a rotation of the ring, and no within-run comparison cancels it.

ESTABLISHED (literature, read at source 2026-11-21): Hulse et al. 2021,
eLife 10:e66039, Fig. 16B prints the wedge angles this map uses (L1 = 0,
L7 = 90, L5 = 180, L3 = 270, right wedges offset by 22.5 deg); Wolff,
Iyer and Rubin 2015, J Comp Neurol 523:997 (the left bridge half wraps
the ellipsoid body clockwise and the right half counterclockwise; left
and right arbors alternate); Wolff and Rubin 2018, J Comp Neurol
526:2585 (the eight tile pairs G1R/G1L, G2R/G8L, ..., G8R/G2L).
ESTABLISHED (connectome annotation): 35 of the 42 MaleCNS Delta7
instance names join L_k with R_(9-k) (for example L8R1R9, L7R2).
MEASURED (this repository, scripts/arenas/compass_map_check.py): the
direct EPG -> EPG synapse counts put each L_k beside R_(9-k) and
R_(10-k) and not beside R_k, except where those coincide (k = 1, 5).

ASSUMPTION (still an assumption, and what it would take to check it):
that MaleCNS instance labels number the bridge glomeruli as the
literature does (1 medial to 8 lateral, per half). The measured
adjacency above is what that numbering predicts, and a different
numbering would not produce it. Which half is called L is not pinned by
adjacency (a wholesale L/R swap mirrors the ring); no registered bar
depends on that sign. What breaks if the map is wrong: every position
bar, every decoded angle and every ring statistic downstream of it.

ASSUMPTION (the eight-unit grouping, AC-B1 as amended): the source
paper (Biswas et al., bioRxiv 10.1101/2024.11.01.621596v2) never states
which left and right glomeruli share a unit. MEASURED from its Fig. 1g
(separator lines read from the rendered page): EPG units of 6, 5, 6, 6,
6, 6, 5, 6 neurons and Delta7 units of 5, 6, 4, 6, 6, 6, 4, 5. Unit
SIZES are measured; unit MEMBERSHIP is INFERRED from them, bridge
stated: that the paper pooled by a regular left-right pairing and that
its per-glomerulus EPG counts are the MaleCNS ones (2, 2, 3, 3, 3, 3,
3, 4 for glomeruli 1..8). Of the sixteen regular pairings only L_k with
R_(9-k) gives those EPG sizes in order; L_k with R_k gives 4, 4, 6, 6,
6, 6, 6, 8 and the other adjacent pairing, L_k with R_(10-k), gives 4,
6, 6, 6, 6, 6, 6, 6. (Among all 40,320 arbitrary left-right matchings,
240 give the same sizes, so sizes alone do not identify the grouping.)
The full evidence, including a cell-by-cell comparison of the figure
with our counts, is in the amendment record.

Glomerulus 9: no EPG cell carries it (the four L9 / R9 cells are type
EPGt, which exact type matching excludes), so no rule about it can move
a result. For completeness the amended functions treat it as glomerulus
1 of the same half (period 8). That is Hulse et al.'s convention for
the PHASE of bridge glomerulus 9 and what the Delta7 names L8R1R9 and
L1L9R8 say. It is NOT where the glomerulus-9 cells arborize: Hulse et
al. place the EPGt wedges between the glomerulus-8 and glomerulus-1
wedges, one position from where this rule would put them. If the type
filter were ever widened to EPGt, this rule would misplace those cells
by 22.5 degrees and must be revisited first.

TERMS. A "ring position" here is one of the sixteen 22.5-degree EPG
sectors, which the literature calls a wedge. A Biswas "unit" under the
amended grouping is two adjacent positions (45 degrees) and is offset
by one position from the anatomical tile of Wolff and Rubin.

Pure functions, standard library only, no data access. The module
lives at the top of the package (flygi.compass_map) so that importing
it pulls in nothing but the standard library: an instrument's BLOCKED
exit for a missing dependency stays reachable.
"""

from __future__ import annotations

import re
from pathlib import Path

N_RING = 16
N_UNITS = 8
DEG_PER_POSITION = 360.0 / N_RING

RING_MAP_REGISTERED = "registered"
RING_MAP_AMENDED = "amended"
RING_MAPS = (RING_MAP_AMENDED, RING_MAP_REGISTERED)
DEFAULT_RING_MAP = RING_MAP_AMENDED

RING_MAP_DESCRIPTION = {
    RING_MAP_REGISTERED: (
        "AC-1 as frozen 2026-10-10 / AC-B1 as frozen 2026-10-31: "
        "index = (glomerulus-1)*2 + (0 if L else 1); unit = "
        "(glomerulus-1) mod 8 with L and R merged. INVALIDATED "
        "2026-11-21 (left half-ring reflected); kept for reproduction "
        "of the registered runs only."),
    RING_MAP_AMENDED: (
        "AC-1 / AC-B1 as amended 2026-11-21: R_k at 22.5 + 45(k-1) deg "
        "(unchanged), L_k at 360 - 45(k-1) deg (reflected); ring order "
        "L1 R1 L8 R2 L7 R3 L6 R4 L5 R5 L4 R6 L3 R7 L2 R8; eight units "
        "pair L_k with R_(9-k). Angles as printed in Hulse et al. 2021 "
        "Fig. 16B."),
}

# The registered label regex, verbatim: first `_L<digit>` / `_R<digit>`.
LABEL_RE = re.compile(r"_([LR])(\d)")


def _check(ring_map: str) -> None:
    if ring_map not in RING_MAPS:
        raise ValueError(
            f"unknown ring map {ring_map!r}; expected one of {RING_MAPS}")


def ring_index(side: str, glomerulus: int, ring_map: str) -> int:
    """Sixteen-position ring index of an EPG cell from its bridge label.

    ``ring_map`` is REQUIRED at every level of this module and of the
    instruments' wrappers: a forgotten argument must raise, never run
    the other map in silence. DEFAULT_RING_MAP is the command-line
    default and nothing else.

    ``registered`` returns the frozen expression untouched (no modulo,
    no range check: callers keep whatever range handling they had), so
    a registered-map run reproduces the registered numbers exactly."""
    _check(ring_map)
    if ring_map == RING_MAP_REGISTERED:
        # AC-1 verbatim (cx_scratchpad_premise.py, 2026-09-27).
        return (glomerulus - 1) * 2 + (0 if side == "L" else 1)
    # ASSUMPTION AC-1 as amended 2026-11-21 (see the module docstring):
    # right half unchanged, left half reflected.
    if side == "R":
        return ((glomerulus - 1) * 2 + 1) % N_RING
    if side == "L":
        return (-(glomerulus - 1) * 2) % N_RING
    raise ValueError(f"bridge side must be 'L' or 'R', got {side!r}")


def ring_angle_deg(side: str, glomerulus: int, ring_map: str) -> float:
    """Ring angle in degrees, 22.5 per position (exact in binary)."""
    return ring_index(side, glomerulus, ring_map) * DEG_PER_POSITION


def ring_unit(side: str, glomerulus: int, ring_map: str) -> int:
    """Eight-unit ring index (the Biswas coarse-graining, AC-B1).

    ``registered``: (glomerulus - 1) mod 8, L and R merged (L_k with
    R_k). ``amended``: L_k with R_(9-k), each unit two adjacent
    half-wedges; equal to ((amended ring index - 1) mod 16) // 2."""
    _check(ring_map)
    if ring_map == RING_MAP_REGISTERED:
        # AC-B1 verbatim (wording corrected 2026-10-31).
        return (glomerulus - 1) % N_UNITS
    # ASSUMPTION AC-B1 as amended 2026-11-21 (see the module docstring).
    if side == "R":
        return (glomerulus - 1) % N_UNITS
    if side == "L":
        return (N_UNITS - glomerulus) % N_UNITS
    raise ValueError(f"bridge side must be 'L' or 'R', got {side!r}")


def ring_label(index: int, ring_map: str) -> tuple[str, int]:
    """Inverse of ``ring_index`` on positions 0..15 and glomeruli 1..8:
    the (side, glomerulus) label sitting at a ring position. Used to
    label synthetic rings so a fixture follows the parser's map."""
    _check(ring_map)
    if not 0 <= index < N_RING:
        raise ValueError(f"ring index must be in 0..{N_RING - 1}")
    for side in ("L", "R"):
        for glomerulus in range(1, N_UNITS + 1):
            if ring_index(side, glomerulus, ring_map) == index:
                return side, glomerulus
    raise AssertionError("ring map is not a bijection")  # pragma: no cover


def parse_label(instance: str) -> tuple[str, int] | None:
    """(side, digit) of the first `_L<digit>` / `_R<digit>` token, or
    None. No range check, exactly as the registered regex behaves."""
    match = LABEL_RE.search(instance)
    if not match:
        return None
    return match.group(1), int(match.group(2))


def default_output(registered_path: Path, ring_map: str) -> Path:
    """Result path for a run under ``ring_map``.

    The registered runs of 2026-09-27 to 2026-10-31 wrote to
    ``<name>.json``; those files are the only full-precision record of
    the registered outcomes and are local and git-ignored. No run
    writes there by default any more: an amended-map run writes
    ``<name>.amended_map.json`` and a re-run of the registered path
    writes ``<name>.registered_map.json``."""
    _check(ring_map)
    registered_path = Path(registered_path)
    return registered_path.with_name(
        f"{registered_path.stem}.{ring_map}_map{registered_path.suffix}")
