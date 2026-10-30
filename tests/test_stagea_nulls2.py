"""Tests for the second null family (H-STAGEA-NULL-DECOMPOSITION:
src/flygi/connectome/nulls.py weight_shuffle / sign_shuffle /
shuffle_invariants, and scripts/arenas/cx_topology_nulls2.py). The
registration's in-cloud dissociation gate runs here, BOTH directions,
before any data contact: a magnitude-tuned synthetic must separate
under the weight family at the empirical floor, and a topology-banded
jittered-weight synthetic must NOT separate under the weight family
while the degree-preserving rewire on the same graph does. Plus the
declared invariants and degeneracy floors."""

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pytest
from scipy import sparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from flygi.connectome.nulls import (  # noqa: E402
    NullValidationError,
    degree_preserving_rewire,
    shuffle_invariants,
    sign_shuffle,
    weight_shuffle,
)


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


nl2 = _load("cx_topology_nulls2", "scripts/arenas/cx_topology_nulls2.py")
cx = nl2.cx
ring_mod = _load("test_cx_topology_killtest_fixture",
                 "tests/test_cx_topology_killtest.py")


def _random_signed(n=40, density=0.15, seed=3):
    """Small random graph with per-presynaptic-column sign constancy
    (the biological convention the sign family requires)."""
    rng = np.random.default_rng(seed)
    column_sign = np.where(rng.random(n) < 0.3, -1.0, 1.0)
    W = np.zeros((n, n), dtype=np.float32)
    for pre in range(n):
        targets = rng.choice(n, size=max(2, int(density * n)), replace=False)
        for post in targets:
            if post != pre:
                W[post, pre] = column_sign[pre] * rng.uniform(0.5, 5.0)
    return sparse.csr_matrix(W)


# --- generator invariants ----------------------------------------------------

@pytest.mark.parametrize("within", [True, False])
def test_weight_shuffle_invariants(within):
    real = _random_signed()
    shuffled, stats = weight_shuffle(real, seed=11, within_presynaptic=within)
    record = shuffle_invariants(real, shuffled, family="weight",
                                within_presynaptic=within)
    assert record["valid"], record["failures"]
    assert record["edge_set_identical"]
    assert stats["fraction_magnitudes_changed"] > 0.5
    # topology fixed: degrees trivially identical
    assert (shuffled != 0).sum() == (real != 0).sum()


def test_weight_shuffle_preserves_per_edge_signs():
    real = _random_signed()
    shuffled, _ = weight_shuffle(real, seed=4)
    assert np.array_equal(np.sign(real.toarray()), np.sign(shuffled.toarray()))


def test_sign_shuffle_invariants_and_dale_consistency():
    real = _random_signed()
    shuffled, stats = sign_shuffle(real, seed=7)
    record = shuffle_invariants(real, shuffled, family="sign")
    assert record["valid"], record["failures"]
    assert not stats["constant_sign_multiset"]
    # per-edge magnitudes untouched
    assert np.allclose(np.abs(real.toarray()), np.abs(shuffled.toarray()))
    # Dale consistency of the result: each column single-signed
    dense = shuffled.toarray()
    for pre in range(dense.shape[1]):
        signs = np.unique(np.sign(dense[:, pre]))
        assert len(signs[signs != 0]) <= 1


def test_sign_shuffle_rejects_mixed_sign_column():
    W = np.zeros((4, 4), dtype=np.float32)
    W[1, 0], W[2, 0] = 1.0, -1.0           # column 0 carries both signs
    W[3, 1] = 1.0
    with pytest.raises(NullValidationError):
        sign_shuffle(sparse.csr_matrix(W), seed=0)


def test_sign_shuffle_constant_multiset_flag():
    real = _random_signed()
    allpos = sparse.csr_matrix(np.abs(real.toarray()))
    _, stats = sign_shuffle(allpos, seed=0)
    assert stats["constant_sign_multiset"]


# --- degeneracy floors (frozen) ----------------------------------------------

def test_weight_shuffle_degenerate_on_uniform_weights():
    """Uniform magnitudes make the permutation a near-identity; the
    runner's frozen floor (fraction changed >= 0.5) must BLOCK it."""
    W, types, instances = ring_mod._ring()
    probe = nl2.degeneracy_check(sparse.csr_matrix(W), "weight_within_pre")
    assert probe["blocked"] is not None
    assert "degenerate weight shuffle" in probe["blocked"]


# --- the registered dissociation gate, direction (a) --------------------------

def _magnitude_tuned(seed=0):
    """Banding lives ONLY in |w|: EPG<->PEN topology is DENSE (every
    pair connected at a small background weight); the ring structure is
    written in magnitudes (2.0 on same/offset-wedge pairs)."""
    rng = np.random.default_rng(seed)
    W, types, instances = ring_mod._ring()
    types = np.asarray(types)
    epg = np.flatnonzero(types == "EPG")
    pen = np.flatnonzero((types == "PEN_a(PEN1)") | (types == "PEN_b(PEN2)"))
    for e in epg:
        for p in pen:
            if W[p, e] == 0:
                W[p, e] = 0.05 * (1 + 0.2 * rng.random())
            if W[e, p] == 0:
                W[e, p] = 0.05 * (1 + 0.2 * rng.random())
    return sparse.csr_matrix(W), types, np.asarray(instances)


def test_gate_a_magnitude_tuned_separates_under_weight_family():
    matrix, types, instances = _magnitude_tuned()
    record = nl2.cx.run_pipeline(
        matrix, types, instances, 100, lambda *_: None,
        rewire_fn=nl2.family_fn("weight_within_pre"))
    assert "blocked" not in record
    # the empirical floor at 100 nulls is (1+0)/101 = 0.009901
    assert record["p_banded"] <= 1.0 / 101 + 1e-12
    assert record["real"]["bandedness"] > record["null_bandedness_max"]


# --- the registered dissociation gate, direction (b) --------------------------

def test_gate_b_topology_banded_inert_under_weight_family_but_not_rewire():
    """Jittered-weight ring: banding is placement-carried, so the weight
    family must NOT separate (p >= 0.2, frozen) while the rewire on the
    SAME graph does."""
    W, types, instances = ring_mod._ring(noise=0.3, seed=5)
    matrix = sparse.csr_matrix(W)
    types, instances = np.asarray(types), np.asarray(instances)

    shuffled = nl2.cx.run_pipeline(
        matrix, types, instances, 50, lambda *_: None,
        rewire_fn=nl2.family_fn("weight_within_pre"))
    assert "blocked" not in shuffled
    assert shuffled["p_banded"] >= 0.2

    rewired = nl2.cx.run_pipeline(
        matrix, types, instances, 25, lambda *_: None)   # default rewire
    assert "blocked" not in rewired
    assert rewired["p_banded"] < 0.05


# --- runner structure ----------------------------------------------------------

def test_run_decomposition_yields_readings_never_verdicts():
    W, types, instances = ring_mod._ring(noise=0.3, seed=9)
    record = nl2.run_decomposition(sparse.csr_matrix(W), np.asarray(types),
                                   np.asarray(instances), 10,
                                   lambda *_: None)
    assert set(record["families"]) == set(nl2.FAMILIES)
    flat = str(record)
    assert "'verdict'" not in flat           # readings only, by design
    for family, entry in record["families"].items():
        assert ("blocked" in entry) or ("na" in entry) or \
            ("reading_banded" in entry), (family, entry)


def test_family_fn_unknown_raises():
    with pytest.raises(ValueError):
        nl2.family_fn("mystery")
