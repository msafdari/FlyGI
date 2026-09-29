"""Subcircuit extraction: selection semantics plus a real-data ring check."""

from __future__ import annotations

import numpy as np
import pytest

from flygi.connectome.subcircuit import (
    SubcircuitError,
    extract_subcircuit,
    select_nodes,
)

RUNTIME = "data/processed/male-cns-v1.0/literal-rate-signed-modulators"


class TestSelection:
    def test_type_pattern_selects_epg(self) -> None:
        ring = select_nodes(RUNTIME, type_patterns=("EPG",))
        assert 40 <= ring.size <= 60  # 46 in this compilation

    def test_empty_selection_raises(self) -> None:
        with pytest.raises(SubcircuitError):
            select_nodes(RUNTIME, type_patterns=("NOPE_NO_SUCH_TYPE",))


class TestRealRing:
    def test_ring_signs_follow_nt_convention(self) -> None:
        ring = select_nodes(
            RUNTIME, type_patterns=("EPG", "PEN_a", "PEN_b", "Delta7", "PEG")
        )
        sub = extract_subcircuit(RUNTIME, ring)
        assert sub.node_count == ring.size
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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
