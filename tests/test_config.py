"""Configuration and seed contracts."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from flygi.config import ConfigError, load_config
from flygi.seed import derive_seed


def test_checked_in_configs_parse() -> None:
    for path in sorted(Path("configs").glob("*.yaml")):
        assert load_config(path).schema_version == 1

    literal = load_config("configs/literal_rate.yaml")
    assert literal.graph.node_filter_column == "superclass"
    assert literal.graph.node_filter_values is None
    assert literal.groups["descending_neurons"] == {"superclass": "descending_neuron"}
    assert literal.dynamics.backend == "rate"
    assert literal.dynamics.execution_backend == "scipy-csr-cpu"
    assert literal.dynamics.activation == "tanh"
    assert literal.dynamics.internal_steps == 2
    assert literal.dynamics.leak == 0.3
    assert literal.dynamics.recurrent_gain == 0.9
    assert literal.dynamics.bias == 0.0
    assert literal.dynamics.frozen_graph is True
    assert literal.dynamics.initial_state == "zeros"
    assert literal.dynamics.state_dtype == "float32"


def test_seed_derivation_does_not_use_salted_python_hash() -> None:
    assert derive_seed(7, "graph") == derive_seed(7, "graph")
    assert derive_seed(7, "graph") != derive_seed(7, "encoder")


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("internal_steps", 0, "internal_steps must be positive"),
        ("internal_steps", 1.5, "internal_steps must be an integer"),
        ("leak", True, "leak must be numeric"),
        ("leak", 0.0, "leak must be in"),
        ("recurrent_gain", -1.0, "recurrent_gain must be non-negative"),
        ("frozen_graph", False, "frozen_graph must remain true"),
        ("state_dtype", "float64", "state_dtype must be float32"),
        ("unexpected", 1, "unknown dynamics keys"),
    ],
)
def test_invalid_dynamics_config_fails_closed(
    tmp_path: Path, key: str, value: object, message: str
) -> None:
    document = yaml.safe_load(Path("configs/literal_rate.yaml").read_text(encoding="utf-8"))
    document["dynamics"][key] = value
    path = tmp_path / "invalid.yaml"
    path.write_text(yaml.safe_dump(document), encoding="utf-8")

    with pytest.raises(ConfigError, match=message):
        load_config(path)
