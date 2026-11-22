"""Tests for flygi.compass_map -- the one place the compass label map
lives (AC-1 / AC-B1 and the 2026-11-21 amendment).

Three kinds of test, deliberately:

  * the REGISTERED map is the frozen expression, digit for digit, so a
    registered-map run reproduces the registered numbers;
  * the AMENDED map is the ring the literature and the wiring describe;
  * COMPARISON and GUARD tests that fail on the pre-amendment code:
    they state what separates the two maps without using any fitted
    value, they refuse a silent default, and they catch a verbatim
    typed copy of the frozen expression reappearing in a script.
"""

import ast
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flygi import compass_map as cm  # noqa: E402

AM, REG = "amended", "registered"
SIDES = ("L", "R")
GLOMERULI = range(1, 9)

# Hulse et al. 2021 (eLife 10:e66039) Fig. 16B, clockwise from the
# wedge labelled 180: the anatomical ring. Read at source 2026-11-21
# (hatching and colour by eye; the four angles are printed).
HULSE_FIG16B_CLOCKWISE_FROM_180 = [
    "L5", "R4", "L6", "R3", "L7", "R2", "L8", "R1",
    "L1", "R8", "L2", "R7", "L3", "R6", "L4", "R5"]
HULSE_PRINTED_ANGLES = {"L1": 0.0, "L7": 90.0, "L5": 180.0, "L3": 270.0}

# Wolff and Rubin 2018 (J Comp Neurol 526:2585): the eight tile pairs of
# the P-EG tile cell. Wolff, Iyer and Rubin 2015 say tile and wedge
# regions coincide for cell types in glomeruli 1-8, which carries the
# pairs over to the EPG wedges.
WOLFF_RUBIN_TILE_PAIRS = [("R1", "L1"), ("R2", "L8"), ("R3", "L7"),
                          ("R4", "L6"), ("R5", "L5"), ("R6", "L4"),
                          ("R7", "L3"), ("R8", "L2")]

# MaleCNS EPG cells per glomerulus 1..8, per bridge half (label inventory).
EPG_PER_GLOMERULUS = (2, 2, 3, 3, 3, 3, 3, 4)


def _split(label):
    return label[0], int(label[1:])


def _idx(label, ring_map):
    return cm.ring_index(*_split(label), ring_map)


def _circ(a, b, n=16):
    return min((a - b) % n, (b - a) % n)


# --- the registered map is the frozen expression -----------------------------

def test_registered_ring_index_is_the_frozen_expression_verbatim():
    for side in SIDES:
        for wedge in range(0, 12):              # incl. out-of-range digits
            frozen = (wedge - 1) * 2 + (0 if side == "L" else 1)
            assert cm.ring_index(side, wedge, REG) == frozen
            assert (cm.ring_angle_deg(side, wedge, REG)
                    == frozen * 22.5 == frozen * (360.0 / 16.0))


def test_registered_ring_unit_is_the_frozen_expression_verbatim():
    for side in SIDES:
        for digit in range(0, 12):
            assert cm.ring_unit(side, digit, REG) == (digit - 1) % 8


# --- naming, and no silent default -------------------------------------------

def test_maps_are_named_and_unknown_names_raise():
    assert cm.DEFAULT_RING_MAP == AM            # the command-line default
    assert set(cm.RING_MAPS) == {AM, REG}
    assert set(cm.RING_MAP_DESCRIPTION) == set(cm.RING_MAPS)
    for bad in ("", "Amended", "corrected", None):
        with pytest.raises(ValueError):
            cm.ring_index("L", 1, bad)
        with pytest.raises(ValueError):
            cm.ring_unit("L", 1, bad)
        with pytest.raises(ValueError):
            cm.ring_label(0, bad)
        with pytest.raises(ValueError):
            cm.default_output(Path("x.json"), bad)
    with pytest.raises(ValueError):
        cm.ring_index("X", 1, AM)


def test_the_map_is_a_required_argument_of_every_helper():
    """A forgotten argument must raise. If the helpers defaulted to the
    amended map, a --ring-map registered run that dropped the argument
    at one call would write amended numbers into a file named
    registered, with no error."""
    for call in (lambda: cm.ring_index("L", 1),
                 lambda: cm.ring_angle_deg("L", 1),
                 lambda: cm.ring_unit("L", 1),
                 lambda: cm.ring_label(0),
                 lambda: cm.default_output(Path("x.json"))):
        with pytest.raises(TypeError):
            call()


def test_the_helper_imports_nothing_but_the_standard_library():
    """flygi.compass_map sits at the top of the package so that importing
    it does not run flygi/connectome/__init__ (pandas, scipy). Otherwise
    an instrument on a host without scipy would die at import with exit
    status 1, the KILL code, and never reach its BLOCKED exit."""
    tree = ast.parse((ROOT / "src/flygi/compass_map.py").read_text())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported <= {"__future__", "re", "pathlib"}
    # and the import really works with the heavy packages unavailable,
    # including whatever flygi/__init__.py pulls in
    import subprocess
    probe = (
        "import sys\n"
        "for name in ('numpy', 'scipy', 'pandas'):\n"
        "    sys.modules[name] = None\n"
        "import flygi.compass_map as cm\n"
        "assert cm.ring_index('L', 2, 'amended') == 14\n")
    done = subprocess.run([sys.executable, "-B", "-c", probe],
                          env={"PYTHONPATH": str(ROOT / "src"),
                               "PATH": "/usr/bin:/bin"},
                          capture_output=True, text=True)
    assert done.returncode == 0, done.stderr


# --- the amended map ---------------------------------------------------------

def test_both_maps_are_bijections_onto_sixteen_positions():
    for ring_map in cm.RING_MAPS:
        seen = sorted(cm.ring_index(s, k, ring_map)
                      for s in SIDES for k in GLOMERULI)
        assert seen == list(range(16))
        for index in range(16):
            side, k = cm.ring_label(index, ring_map)
            assert cm.ring_index(side, k, ring_map) == index


def test_amended_order_and_angles():
    order = ["%s%d" % cm.ring_label(i, AM) for i in range(16)]
    assert order == ["L1", "R1", "L8", "R2", "L7", "R3", "L6", "R4",
                     "L5", "R5", "L4", "R6", "L3", "R7", "L2", "R8"]
    for k in GLOMERULI:
        assert cm.ring_angle_deg("R", k, AM) == 22.5 + 45.0 * (k - 1)
        assert cm.ring_angle_deg("L", k, AM) == (360.0 - 45.0 * (k - 1)) % 360.0
    # every angle is an exact multiple of 22.5 (exact in binary)
    for s in SIDES:
        for k in GLOMERULI:
            assert math.fmod(cm.ring_angle_deg(s, k, AM), 22.5) == 0.0


def test_amendment_changes_only_the_left_half_and_by_a_reflection():
    for k in GLOMERULI:
        assert cm.ring_index("R", k, AM) == cm.ring_index("R", k, REG)
        assert cm.ring_index("L", k, AM) == (-cm.ring_index("L", k, REG)) % 16
    moved = [k for k in GLOMERULI
             if cm.ring_index("L", k, AM) != cm.ring_index("L", k, REG)]
    assert moved == [2, 3, 4, 6, 7, 8]          # L1 and L5 are fixed points


def test_right_centred_angles_keep_their_centre_cell_left_centred_do_not():
    """The dynamics instruments write at 22.5 + 45j (right-centred): the
    centre cell is the same under both maps. The scratchpad settle map
    writes at 0, 45, ..., 315 (left-centred): six of its eight centre
    cells change, so a settle-map row is only like-for-like across the
    two maps at 0 and 180."""
    for j in range(8):
        index = 2 * j + 1
        assert cm.ring_label(index, AM) == cm.ring_label(index, REG) == ("R", j + 1)
    changed = [45 * j for j in range(8)
               if cm.ring_label(2 * j, AM) != cm.ring_label(2 * j, REG)]
    assert changed == [45, 90, 135, 225, 270, 315]
    assert cm.ring_label(0, AM) == cm.ring_label(0, REG) == ("L", 1)
    assert cm.ring_label(8, AM) == cm.ring_label(8, REG) == ("L", 5)


def test_amended_map_agrees_with_hulse_2021_fig16b():
    # cyclic order: consecutive wedges in the figure are consecutive
    # ring positions (the figure runs in the direction of DEcreasing
    # angle, a drawing convention)
    idx = [_idx(label, AM) for label in HULSE_FIG16B_CLOCKWISE_FROM_180]
    steps = {(b - a) % 16 for a, b in zip(idx, idx[1:] + idx[:1])}
    assert steps == {15}
    for label, angle in HULSE_PRINTED_ANGLES.items():
        assert cm.ring_angle_deg(*_split(label), AM) == angle
    # the registered map does not have this property
    reg = [_idx(label, REG) for label in HULSE_FIG16B_CLOCKWISE_FROM_180]
    assert len({(b - a) % 16 for a, b in zip(reg, reg[1:] + reg[:1])}) > 1


def test_amended_map_puts_each_left_wedge_between_the_right_neighbours():
    # MEASURED 2026-11-21 on the direct EPG -> EPG counts and
    # ESTABLISHED in the literature: L_k lies between R_(9-k) and R_(10-k)
    for k in GLOMERULI:
        left = cm.ring_index("L", k, AM)
        neighbours = {cm.ring_label((left + d) % 16, AM) for d in (-1, 1)}
        expect = {("R", (9 - k - 1) % 8 + 1), ("R", (10 - k - 1) % 8 + 1)}
        assert neighbours == expect
    # under the registered map L_k sits beside R_k instead, which is a
    # true neighbour only where k is 9-k or 10-k modulo 8 (k = 1, 5)
    truly_adjacent = [k for k in GLOMERULI
                      if _circ(cm.ring_index("L", k, AM),
                               cm.ring_index("R", k, AM)) == 1]
    assert truly_adjacent == [1, 5]
    for k in GLOMERULI:
        assert _circ(cm.ring_index("L", k, REG),
                     cm.ring_index("R", k, REG)) == 1


def test_wolff_rubin_tile_pairs_under_the_two_maps():
    # all eight are ring neighbours under the amended map
    for a, b in WOLFF_RUBIN_TILE_PAIRS:
        assert _circ(_idx(a, AM), _idx(b, AM)) == 1
    # under the registered map only G1R/G1L and G5R/G5L are
    apart = [_circ(_idx(a, REG), _idx(b, REG))
             for a, b in WOLFF_RUBIN_TILE_PAIRS]
    assert apart == [1, 5, 7, 3, 1, 5, 7, 3]


def test_a_wholesale_left_right_swap_only_mirrors_the_amended_ring():
    """Which bridge half MaleCNS calls L is not pinned by adjacency. If
    the labels were swapped wholesale, the amended ring is reflected
    (index i -> (1 - i) mod 16) and every unit pair is unchanged, so no
    statistic that is blind to reflection can move."""
    for s in SIDES:
        other = "R" if s == "L" else "L"
        for k in GLOMERULI:
            assert cm.ring_index(other, k, AM) == (1 - cm.ring_index(s, k, AM)) % 16
            assert cm.ring_unit(other, k, AM) == 7 - cm.ring_unit(s, k, AM)
    # the registered map has no such symmetry: its swap is a shift of
    # one half against the other, not a reflection of the ring
    assert any(cm.ring_index("R", k, REG) != (1 - cm.ring_index("L", k, REG)) % 16
               for k in GLOMERULI)


# --- the eight-unit grouping (AC-B1) -----------------------------------------

def test_amended_unit_is_two_adjacent_positions_l_k_with_r_9_minus_k():
    for k in GLOMERULI:
        assert cm.ring_unit("R", k, AM) == k - 1
        assert cm.ring_unit("L", 9 - k, AM) == k - 1
        assert _circ(cm.ring_index("R", k, AM), cm.ring_index("L", 9 - k, AM)) == 1
    for s in SIDES:
        for k in GLOMERULI:
            assert cm.ring_unit(s, k, AM) == ((cm.ring_index(s, k, AM) - 1) % 16) // 2
    # glomerulus 9 = glomerulus 1 of the same half (period 8); no EPG
    # cell carries it, see the module docstring for the EPGt caveat
    assert cm.ring_unit("R", 9, AM) == cm.ring_unit("R", 1, AM)
    assert cm.ring_unit("L", 9, AM) == cm.ring_unit("L", 1, AM)
    assert cm.ring_index("R", 9, AM) == cm.ring_index("R", 1, AM)
    assert cm.ring_index("L", 9, AM) == cm.ring_index("L", 1, AM)


def _unit_sizes(unit_of):
    sizes = [0] * 8
    for side in SIDES:
        for k, n in zip(GLOMERULI, EPG_PER_GLOMERULUS):
            sizes[unit_of(side, k)] += n
    return sizes


def test_amended_grouping_gives_the_source_figure_unit_sizes():
    """COMPARISON TEST (no fitted value involved). Biswas et al. v2
    Fig. 1g: EPG units of 6,5,6,6,6,6,5,6 neurons (separator lines read
    from the rendered figure, 2026-11-21). The amended grouping gives
    them, the registered one and the other neighbour pairing do not.
    Sizes alone do not IDENTIFY a grouping (240 of the 40,320 arbitrary
    left-right matchings share them); the cell-by-cell figure comparison
    in the amendment record is what does."""
    figure = [6, 5, 6, 6, 6, 6, 5, 6]
    assert _unit_sizes(lambda s, k: cm.ring_unit(s, k, AM)) == figure
    assert (_unit_sizes(lambda s, k: cm.ring_unit(s, k, REG))
            == [4, 4, 6, 6, 6, 6, 6, 8])
    # the other adjacent pairing (L_k with R_(10-k), the anatomical tile)
    tile = _unit_sizes(lambda s, k: cm.ring_index(s, k, AM) // 2)
    assert sorted(tile) == [4, 6, 6, 6, 6, 6, 6, 6]
    assert tile != figure


def test_of_the_sixteen_regular_pairings_only_one_gives_the_figure_sizes():
    figure = [6, 5, 6, 6, 6, 6, 5, 6]
    c = EPG_PER_GLOMERULUS
    hits = []
    for shift in range(8):
        for kind in ("L_(shift-k)", "L_(k+shift)"):
            partner = [((shift - (u + 1)) % 8) if kind == "L_(shift-k)"
                       else ((u + 1 + shift) % 8) for u in range(8)]
            if [c[u] + c[partner[u]] for u in range(8)] == figure:
                hits.append([p + 1 for p in partner])
    assert hits == [[8, 7, 6, 5, 4, 3, 2, 1]]   # R_k with L_(9-k)


# --- outputs and plumbing guards ---------------------------------------------

def test_default_output_never_points_at_a_registered_run_file():
    base = Path("results/arenas/cx_topology_killtest.json")
    amended = cm.default_output(base, AM)
    registered = cm.default_output(base, REG)
    assert amended.name == "cx_topology_killtest.amended_map.json"
    assert registered.name == "cx_topology_killtest.registered_map.json"
    assert base not in (amended, registered)
    assert amended.with_suffix(".log").name == \
        "cx_topology_killtest.amended_map.log"


COMPASS_SCRIPTS = (
    "scripts/arenas/cx_topology_killtest.py",
    "scripts/arenas/cx_topology_nulls2.py",
    "scripts/arenas/cx_biswas_killtest.py",
    "scripts/arenas/cx_heading_killtest.py",
    "scripts/arenas/cx_seeding_killtest.py",
    "scripts/arenas/cx_class3_killtest.py",
    "scripts/benchmarks/cx_ring.py",
    "scripts/benchmarks/fc2_eb_ring.py",
    "scripts/cx_scratchpad_premise.py",
)
MAP_USERS = COMPASS_SCRIPTS + (
    "scripts/arenas/cx_biswas_context_nulls.py",
    "scripts/arenas/compass_map_check.py",
    "scripts/arenas/biswas_fig1g_check.py",
)

# The frozen index and unit expressions, VERBATIM. This guard catches a
# copy-paste of the registered code; it does not catch a re-spelling.
_VERBATIM_INDEX = re.compile(r"-\s*1\)\s*\*\s*2\s*\+\s*\(?\s*0\s+if")
_VERBATIM_UNIT = re.compile(r"-\s*1\)\s*%\s*N_UNITS")


def _code_without_comments_and_docstrings(path):
    code = "\n".join(line for line in path.read_text().splitlines()
                     if not line.lstrip().startswith("#"))
    return re.sub(r'"""(?:.|\n)*?"""', "", code)


@pytest.mark.parametrize("relative", COMPASS_SCRIPTS)
def test_every_compass_script_takes_the_map_from_the_one_helper(relative):
    source = (ROOT / relative).read_text()
    body = _code_without_comments_and_docstrings(ROOT / relative)
    assert not _VERBATIM_INDEX.search(body) and not _VERBATIM_UNIT.search(body), (
        f"{relative} carries a verbatim copy of the frozen label map; "
        "use flygi.compass_map")
    assert '"--ring-map"' in source
    assert "DEFAULT_RING_MAP" in source
    assert "compass_map_amendment_20261121.md" in source
    assert "flygi.connectome.compass_map" not in source


def test_no_other_script_or_module_carries_a_verbatim_copy_of_the_map():
    offenders = []
    for folder in ("scripts", "src"):
        for path in sorted((ROOT / folder).rglob("*.py")):
            relative = path.relative_to(ROOT).as_posix()
            if relative == "src/flygi/compass_map.py":
                continue
            if _VERBATIM_INDEX.search(_code_without_comments_and_docstrings(path)):
                offenders.append(relative)
    assert offenders == []


# Every function through which a ring map travels, with the 0-based
# position its map argument takes when passed positionally.
_MAP_FUNCTIONS = {
    "ring_index": 2, "ring_angle_deg": 2, "ring_unit": 2,
    "ring_label": 1, "default_output": 1,
    "wedge_index": 1, "epg_unit_from_instance": 1,
    "run_pipeline": None, "run_decomposition": None,   # keyword-only
}


# Scripts in which a LITERAL map name would be a bug: the map must come
# from the --ring-map flag. (biswas_fig1g_check.py names "amended"
# deliberately; compass_map_check.py loops over both maps.)
_FLAG_DRIVEN = COMPASS_SCRIPTS + ("scripts/arenas/cx_biswas_context_nulls.py",)


@pytest.mark.parametrize("relative", MAP_USERS)
def test_every_call_that_carries_a_map_names_it_explicitly(relative):
    """An AST walk of each script: every call to a map-carrying function
    passes the map, positionally or as ring_map=, and in the flag-driven
    scripts never as a string literal. With the required arguments the
    first half is also enforced at run time; the walk catches it before a
    once-only run does. It does not follow a function through an alias."""
    path = ROOT / relative
    assert path.exists(), f"{relative} is listed but absent"
    tree = ast.parse(path.read_text())
    seen = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
        if name not in _MAP_FUNCTIONS:
            continue
        if isinstance(func, ast.Attribute) and getattr(func.value, "id", None) == "fb":
            continue                            # the FB instrument's own pipeline
        seen += 1
        position = _MAP_FUNCTIONS[name]
        given = [kw.value for kw in node.keywords if kw.arg == "ring_map"]
        if position is not None and len(node.args) > position:
            given.append(node.args[position])
        assert given, (
            f"{relative}:{node.lineno}: {name}(...) does not pass the ring map")
        if relative in _FLAG_DRIVEN:
            assert not isinstance(given[0], ast.Constant), (
                f"{relative}:{node.lineno}: {name}(...) hard-codes the map; "
                "it must come from --ring-map")
    assert seen >= 1, f"{relative} never calls a map-carrying function"


def test_the_guard_would_catch_a_dropped_or_hard_coded_map():
    """The AST guard above, run on mutated copies of a real call site:
    it must flag a dropped argument and a hard-coded map name."""
    good = "ring_angle_deg(side, wedge, args.ring_map)"
    for bad in ("ring_angle_deg(side, wedge)",
                "ring_angle_deg(side, wedge, 'amended')",
                "ring_angle_deg(side, wedge, ring_map='registered')"):
        for source, should_flag in ((good, False), (bad, True)):
            call = ast.parse(source).body[0].value
            given = [kw.value for kw in call.keywords if kw.arg == "ring_map"]
            if len(call.args) > 2:
                given.append(call.args[2])
            flagged = (not given) or isinstance(given[0], ast.Constant)
            assert flagged == should_flag, source
