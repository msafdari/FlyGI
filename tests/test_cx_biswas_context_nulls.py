"""Tests for scripts/arenas/cx_biswas_context_nulls.py -- the
non-decisional context reading registered with the 2026-11-21 compass
map amendment. The data-gated run is local; what is testable anywhere
is that the script redefines nothing from the instrument, that its
declared seeds do not touch the registered bar or the seeds already
looked at, and that its summary counts what it says."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

_spec = importlib.util.spec_from_file_location(
    "cx_biswas_context_nulls",
    ROOT / "scripts/arenas/cx_biswas_context_nulls.py")
ctx = importlib.util.module_from_spec(_spec)
sys.modules["cx_biswas_context_nulls"] = ctx
_spec.loader.exec_module(ctx)
bk = ctx.bk


def test_declared_seeds_are_unseen():
    seeds = set(range(ctx.CONTEXT_SEED_FIRST,
                      ctx.CONTEXT_SEED_FIRST + ctx.CONTEXT_SEED_COUNT))
    registered_bar = {bk.REWIRE_SEED_BASE + k for k in bk.REWIRE_SEEDS}
    assert registered_bar == {4242, 4243, 4244}
    looked_at_2026_11_21 = set(range(4245, 4265))
    assert not seeds & registered_bar
    assert not seeds & looked_at_2026_11_21
    assert (min(seeds), max(seeds), len(seeds)) == (4265, 4464, 200)


def test_the_reading_reuses_the_instrument_and_redefines_no_constant():
    source = (ROOT / "scripts/arenas/cx_biswas_context_nulls.py").read_text()
    for name in ("MIRROR_SEED_CAP", "RETENTION_MIN", "CIRCVAR_MAX",
                 "ERR_MAX_DEG", "G1_MIN_PASS", "A_DELTA_CONFIGS",
                 "TIE_MARGIN", "FIT_ATOL_MIRROR"):
        assert f"{name} =" not in source
    assert "bk.run_graph(" in source
    assert "bk.epg_unit_from_instance(" in source
    assert "assemble_verdict" not in source     # it decides nothing
    # one declared seed window, no flag to read another
    assert "--seed" not in source and "--count" not in source


def test_summarize_counts_valid_fits_passes_and_errors():
    def rec(seed, v8=False, p8=False, v6=False, p6=False):
        return {"seed": seed, "configs": {
            "8": {"valid_fit": v8, "pass": p8},
            "6": {"valid_fit": v6, "pass": p6},
            "4": {"valid_fit": False, "pass": False}}}
    records = [rec(1), rec(2, v8=True), rec(3, v8=True, p8=True, v6=True),
               {"seed": 4, "error": "boom"}]
    s = ctx.summarize(records)
    assert s["n_rewires"] == 4 and s["n_errors"] == 1
    assert s["n_evaluated"] == 3                # an error is not "no fit"
    assert s["error_seeds"] == [4]
    assert s["n_valid_fit_any_config"] == 2
    assert s["valid_fit_seeds"] == [2, 3]
    assert s["n_pass_g1_any_config"] == 1 and s["pass_g1_seeds"] == [3]
    assert s["per_config"]["8"] == {"valid_fit": 2, "pass": 1}
    assert s["per_config"]["6"] == {"valid_fit": 1, "pass": 0}
    assert s["per_config"]["4"] == {"valid_fit": 0, "pass": 0}
