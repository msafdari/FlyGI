"""Tests for scripts/arenas/cx_seeding_killtest.py
(H-CX-SEEDING-PROTOCOL, Task 9 reopening probe). The measurement is
data-gated and local; testable in-cloud: the frozen design table, the
verbatim reuse of the Stage-B machinery, the P4 injection, the cell
pass rule, the verdict assembly, and the per-cell protocol runner
end-to-end on stub networks (a perfect-memory stub must pass the cell
rule, a decaying stub must fail it)."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load(name):
    spec = importlib.util.spec_from_file_location(
        name, ROOT / f"scripts/arenas/{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


sk = _load("cx_seeding_killtest")
hk = sk.hk     # the Stage-B module instance the probe actually uses


# --- frozen design -----------------------------------------------------------

def test_frozen_operating_points_and_protocols():
    assert sk.OPERATING_POINTS == ((1.5, 0.3), (2.0, 0.3))
    assert set(sk.PROTOCOLS) == {"P1", "P2", "P3", "P4"}
    # P1 is the cx_ring-verbatim reproduction control
    assert sk.PROTOCOLS["P1"] == {"kind": "wedge",
                                  "steps": hk.WRITE_STEPS,
                                  "scale": hk.WRITE_SCALE}
    assert sk.PROTOCOLS["P2"] == {"kind": "wedge", "steps": 100,
                                  "scale": 1.0}
    assert sk.PROTOCOLS["P3"] == {"kind": "wedge", "steps": 20,
                                  "scale": 3.0}
    assert sk.PROTOCOLS["P4"] == {"kind": "inject"}
    assert sk.CELL_MIN_ANGLES == 2


def test_stage_b_machinery_is_reused_verbatim():
    # the probe's functions ARE the Stage-B module's functions
    assert sk.circular_stats is hk.circular_stats
    assert sk.circ_err_deg is hk.circ_err_deg
    assert sk.cx_block_rewire is hk.cx_block_rewire
    assert sk.make_sequences is hk.make_sequences
    assert sk.integrate_commands is hk.integrate_commands
    # and the shared constants carry the Stage-B frozen values
    assert sk.INTERNAL_STEPS == 4
    assert sk.CAL_ANGLE == 22.5
    assert sk.HELDOUT_ANGLES == (112.5, 202.5, 292.5)
    assert sk.WEDGE_SPAN_DEG == 90.0
    assert sk.SETTLE_STEPS == 10
    assert sk.DARK_STEPS == 200
    assert sk.RETENTION_MIN == 0.05
    assert sk.CIRCVAR_MAX == 0.6
    assert sk.ERR_MAX_DEG == 45.0
    assert sk.REWIRE_SEED_BASE == 4242
    assert sk.REWIRE_SEEDS == (0, 1, 2)


# --- injection and masks -----------------------------------------------------

def test_wedge_mask_span_and_wrap():
    angles = np.arange(16) * 22.5
    inside = sk.wedge_mask(angles, 0.0)
    # within +/- 45 deg of 0: 315, 337.5, 0, 22.5, 45
    assert set(np.flatnonzero(inside).tolist()) == {0, 1, 2, 14, 15}


def test_injected_state_registration_verbatim():
    node_count = 30
    epg = np.arange(10, 26)                  # 16 EPG cells
    angles = np.arange(16) * 22.5
    initial = np.full(node_count, 0.123, dtype=np.float32)
    state = sk.injected_state(initial, epg, angles, 90.0)
    inside = sk.wedge_mask(angles, 90.0)
    assert (state[epg[inside]] == 1.0).all()
    assert (state[epg[~inside]] == 0.0).all()
    # all other nodes untouched at initial_state
    others = np.setdiff1d(np.arange(node_count), epg)
    assert np.allclose(state[others], 0.123)
    # the input array is not mutated
    assert np.allclose(initial, 0.123)


# --- cell rule and verdict ---------------------------------------------------

def _row(retention=0.5, circvar=0.2, err=10.0, held=True):
    return {"retention": retention, "circvar": circvar, "err_deg": err,
            "held_out": held, "final_angle": 0.0}


def test_cell_pass_two_of_three_held_out():
    rows = {"22.5": _row(retention=0.0, held=False),   # cal never counts
            "112.5": _row(), "202.5": _row(),
            "292.5": _row(retention=0.0)}
    assert sk.cell_pass(rows)
    rows["202.5"] = _row(circvar=0.7)                  # now 1 of 3
    assert not sk.cell_pass(rows)


def test_cell_pass_requires_position_faithfulness():
    # retention and circvar fine, but PVA off the seed: fails
    rows = {"112.5": _row(err=50.0), "202.5": _row(err=46.0),
            "292.5": _row()}
    assert not sk.cell_pass(rows)
    rows2 = {"112.5": _row(err=float("nan")), "202.5": _row(),
             "292.5": _row()}
    assert sk.cell_pass(rows2)                         # still 2 of 3


def test_assemble_verdict_decisive_logic():
    def cell(real_pass, rw_passes):
        return {"real_pass": real_pass,
                "rewires": [{"pass": p} for p in rw_passes]}
    # real passes, all rewires fail -> PASS
    assert sk.assemble_verdict([cell(True, [False] * 3)]) == "PASS"
    # a rewire passing spoils the cell
    assert sk.assemble_verdict([cell(True, [False, True, False])]) == "KILL"
    # real failing is never decisive
    assert sk.assemble_verdict([cell(False, [False] * 3)]) == "KILL"
    # missing rewire runs cannot be decisive
    assert sk.assemble_verdict([{"real_pass": True}]) == "KILL"
    assert sk.assemble_verdict(
        [cell(True, [False] * 2)]) == "KILL"           # incomplete bar
    # one decisive cell among failures suffices
    assert sk.assemble_verdict(
        [cell(False, []), cell(True, [False] * 3)]) == "PASS"


# --- run_cell end-to-end on stub networks ------------------------------------

class _StubNetwork:
    """Linear stub: advance returns decay * state + drive. decay 1.0 =
    perfect memory (bump persists in darkness); decay 0.0 = total loss."""

    def __init__(self, n, decay):
        self.n = n
        self.decay = decay

    def initial_state(self):
        return np.zeros(self.n, dtype=np.float32)

    def advance(self, state, drive, internal_steps):
        assert internal_steps == sk.INTERNAL_STEPS
        return self.decay * state + drive


def _advance(network, state, drive, steps):
    for _ in range(steps):
        state = network.advance(state, drive,
                                internal_steps=sk.INTERNAL_STEPS)
    return state


def _geometry():
    node_count = 24
    epg = np.arange(4, 20)
    angles = np.arange(16) * 22.5
    return node_count, epg, angles, np.deg2rad(angles)


@pytest.mark.parametrize("pname", ["P1", "P2", "P3", "P4"])
def test_run_cell_perfect_memory_passes_each_protocol(pname):
    node_count, epg, angles, radians = _geometry()
    net = _StubNetwork(node_count, decay=1.0)
    rows = sk.run_cell(net, sk.PROTOCOLS[pname], node_count, epg,
                       angles, radians, _advance)
    assert set(rows) == {"22.5", "112.5", "202.5", "292.5"}
    assert sk.cell_pass(rows)
    for target, row in rows.items():
        assert row["retention"] == pytest.approx(1.0)
        assert row["err_deg"] == pytest.approx(0.0, abs=1e-6)
        assert row["circvar"] <= sk.CIRCVAR_MAX
        assert row["held_out"] == (target != "22.5")


def test_run_cell_decaying_network_fails():
    node_count, epg, angles, radians = _geometry()
    net = _StubNetwork(node_count, decay=0.0)
    rows = sk.run_cell(net, sk.PROTOCOLS["P1"], node_count, epg,
                       angles, radians, _advance)
    assert not sk.cell_pass(rows)
    for row in rows.values():
        assert row["retention"] == 0.0


def test_seed_state_unknown_kind_raises():
    node_count, epg, angles, _ = _geometry()
    net = _StubNetwork(node_count, decay=1.0)
    with pytest.raises(ValueError):
        sk.seed_state(net, {"kind": "mystery"}, 0.0, node_count, epg,
                      angles, _advance)
