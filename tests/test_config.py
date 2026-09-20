"""Configuration and seed contracts."""

from __future__ import annotations

from pathlib import Path

from flygi.config import load_config
from flygi.seed import derive_seed


def test_checked_in_configs_parse() -> None:
    for path in sorted(Path("configs").glob("*.yaml")):
        assert load_config(path).schema_version == 1

    literal = load_config("configs/literal_rate.yaml")
    assert literal.graph.node_filter_column == "superclass"
    assert literal.graph.node_filter_values is None
    assert literal.groups["descending_neurons"] == {"superclass": "descending_neuron"}


def test_seed_derivation_does_not_use_salted_python_hash() -> None:
    assert derive_seed(7, "graph") == derive_seed(7, "graph")
    assert derive_seed(7, "graph") != derive_seed(7, "encoder")
