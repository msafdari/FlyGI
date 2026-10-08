"""Subcircuit extraction: selection semantics plus a real-data ring check."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from flygi.connectome.subcircuit import (
    SubcircuitError,
    extract_subcircuit,
    select_nodes,
)

RUNTIME = "data/processed/male-cns-v1.0/literal-rate-signed-modulators"

# Compiled-runtime data is gitignored (AGENTS.md): on a fresh clone these
# tests must SKIP, not fail (same guard pattern as needs_recognizer_frames).
pytestmark = pytest.mark.skipif(
    not (Path(RUNTIME) / "node_metadata.npz").is_file(),
    reason="compiled MaleCNS runtime absent (gitignored data)",
)


class TestSelection:
    def test_type_pattern_selects_epg(self) -> None:
        ring = select_nodes(RUNTIME, type_patterns=("EPG",))
        assert 40 <= ring.size <= 60  # 46 in this compilation

    def test_empty_selection_raises(self) -> None:
        with pytest.raises(SubcircuitError):
            select_nodes(RUNTIME, type_patterns=("NOPE_NO_SUCH_TYPE",))


class TestRealRing:
    def test_ring_signs_follow_nt_convention(self) -> None:
        # The PEN patterns need wildcards: select_nodes is exact fnmatch and
        # the MaleCNS type names are "PEN_a(PEN1)"/"PEN_b(PEN2)", so bare
        # "PEN_a"/"PEN_b" match ZERO nodes and the "ring" silently degrades
        # to 106 EPG+Delta7+PEG cells with no PEN population (the bug this
        # list carried until 2026-09-30). MEASURED 2026-09-29
        # (scripts/benchmarks/fc2_eb_ring.py registration header): corrected
        # patterns select 148 neurons = 46 EPG + 20 PEN_a(PEN1) +
        # 22 PEN_b(PEN2) + 42 Delta7 + 18 PEG, all PENs acetylcholine.
        ring = select_nodes(
            RUNTIME, type_patterns=("EPG", "PEN_a*", "PEN_b*", "Delta7", "PEG")
        )
        sub = extract_subcircuit(RUNTIME, ring)
        assert sub.node_count == ring.size
        assert 130 <= sub.node_count <= 170  # 148 in this compilation
        assert sub.matrix.nnz > 1000
        coo = sub.matrix.tocoo()
        inhibitory = np.isin(
            sub.consensus_nt[coo.col], ["gaba", "glutamate", "histamine"]
        )
        excitatory = sub.consensus_nt[coo.col] == "acetylcholine"
        assert (coo.data[inhibitory] < 0).all()
        assert (coo.data[excitatory] > 0).all()
        # ESTABLISHED compass motif: Delta7 is the ring's inhibition.
        delta7 = sub.indices_where("Delta7")
        assert (sub.consensus_nt[delta7] == "glutamate").all()
        # Regression guard for the pattern bug above: both PEN populations
        # must actually be in the ring, and cholinergic per consensus_nt.
        pen_a = sub.indices_where("PEN_a*")
        pen_b = sub.indices_where("PEN_b*")
        assert pen_a.size > 0
        assert pen_b.size > 0
        assert (sub.consensus_nt[pen_a] == "acetylcholine").all()
        assert (sub.consensus_nt[pen_b] == "acetylcholine").all()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
