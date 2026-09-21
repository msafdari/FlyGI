"""Configuration and seed contracts."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from flygi.config import ConfigError, load_config
from flygi.seed import derive_seed


def test_checked_in_configs_parse() -> None:
    for path in sorted(Path("configs").glob("*.yaml")):
        config = load_config(path)
        assert config.schema_version == 1
        # K must never be silent: it is the deployment setting and the
        # anatomical measurement says the default of 2 is too small.
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert "internal_steps" in document.get("dynamics", {}), path.name
        assert config.dynamics.internal_steps >= 4, path.name

    literal = load_config("configs/literal_rate.yaml")
    assert literal.graph.node_filter_column == "superclass"
    assert literal.graph.node_filter_values is None
    assert literal.groups["descending_neurons"] == {"superclass": "descending_neuron"}
    assert literal.dynamics.backend == "rate"
    assert literal.dynamics.execution_backend == "scipy-csr-cpu"
    assert literal.dynamics.activation == "tanh"
    assert literal.dynamics.internal_steps == 4
    assert literal.dynamics.leak == 0.3
    assert literal.dynamics.recurrent_gain == 0.9
    assert literal.dynamics.bias == 0.0
    assert literal.dynamics.frozen_graph is True
    assert literal.dynamics.initial_state == "zeros"
    assert literal.dynamics.state_dtype == "float32"
    assert literal.decoder.sampling_method == "zscore_softmax_categorical"
    assert literal.decoder.action_temperature == 0.35
    assert literal.decoder.coordinate_temperature == 0.5
    assert literal.decoder.decision_seed_policy == "explicit_per_policy_or_config_derived"
    assert literal.decoder.coordinate_fallback == "novelty_centroid"
    assert literal.decoder.unchanged_click_exploration == "seeded_untried_uniform"


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


@pytest.mark.parametrize(
    ("key", "value", "message"),
    [
        ("sampling_method", "raw_softmax", "unsupported decoder.sampling_method"),
        ("action_temperature", 0.0, "action_temperature must be finite and positive"),
        ("action_temperature", True, "action_temperature must be numeric"),
        ("coordinate_temperature", float("nan"), "coordinate_temperature must be finite"),
        ("decision_seed_policy", "global", "unsupported decoder.decision_seed_policy"),
        ("coordinate_fallback", "none", "unsupported decoder.coordinate_fallback"),
        (
            "unchanged_click_exploration",
            "repeat",
            "unsupported decoder.unchanged_click_exploration",
        ),
        ("unexpected", 1, "unknown decoder keys"),
    ],
)
def test_invalid_stochastic_decoder_config_fails_closed(
    tmp_path: Path, key: str, value: object, message: str
) -> None:
    document = yaml.safe_load(Path("configs/literal_rate.yaml").read_text(encoding="utf-8"))
    document["decoder"][key] = value
    path = tmp_path / "invalid.yaml"
    path.write_text(yaml.safe_dump(document), encoding="utf-8")

    with pytest.raises(ConfigError, match=message):
        load_config(path)


def test_graph_conditions_share_the_stochastic_decoder_contract() -> None:
    unsigned = load_config("configs/literal_rate.yaml").decoder
    signed = load_config("configs/literal_rate_signed.yaml").decoder
    reservoir = load_config("configs/reservoir_rate.yaml").decoder
    assert signed == unsigned
    assert reservoir == unsigned


def test_transmitter_treatments_are_declared_not_defaulted() -> None:
    """Sign handling changes the compiled edge set, so it must be explicit."""

    for name in ("literal_rate", "literal_rate_signed"):
        document = yaml.safe_load(Path(f"configs/{name}.yaml").read_text(encoding="utf-8"))
        assert "modulator_treatment" in document["graph"]
        assert "unknown_transmitter_treatment" in document["graph"]

    signed = load_config("configs/literal_rate_signed.yaml")
    assert signed.graph.sign_mode == "heuristic"
    assert signed.graph.modulator_treatment == "zero"
    assert signed.graph.unknown_transmitter_treatment == "zero"


def test_signed_config_differs_from_unsigned_only_where_intended() -> None:
    """The signed condition must not silently change any other build choice."""

    unsigned = load_config("configs/literal_rate.yaml").graph
    signed = load_config("configs/literal_rate_signed.yaml").graph

    assert unsigned.sign_mode == "unsigned"
    assert signed.sign_mode == "heuristic"
    assert unsigned.output_dir != signed.output_dir

    for field in (
        "matrix_convention",
        "weight_transform",
        "modulator_treatment",
        "unknown_transmitter_treatment",
        "normalization",
        "spectral_radius",
        "epsilon",
        "allow_self_edges",
        "node_filter_column",
        "node_filter_values",
        "body_id_dtype",
        "weight_dtype",
    ):
        assert getattr(unsigned, field) == getattr(signed, field), field


def test_signed_and_unsigned_runtimes_are_separate_assets() -> None:
    unsigned = load_config("configs/literal_rate.yaml")
    signed = load_config("configs/literal_rate_signed.yaml")

    assert unsigned.data.output_dir == unsigned.graph.output_dir
    assert signed.data.output_dir == signed.graph.output_dir
    assert signed.graph.output_dir != unsigned.graph.output_dir
    assert signed.dynamics == unsigned.dynamics
    assert dict(signed.groups) == dict(unsigned.groups)


@pytest.mark.parametrize("key", ["modulator_treatment", "unknown_transmitter_treatment"])
def test_invalid_transmitter_treatment_fails_closed(tmp_path: Path, key: str) -> None:
    document = yaml.safe_load(Path("configs/literal_rate.yaml").read_text(encoding="utf-8"))
    document["graph"][key] = "excitatory"
    path = tmp_path / "invalid.yaml"
    path.write_text(yaml.safe_dump(document), encoding="utf-8")

    with pytest.raises(ConfigError, match=f"unsupported {key}"):
        load_config(path)
