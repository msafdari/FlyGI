"""Configuration loading for the versioned FlyGI build pipeline."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    """Raised when a configuration cannot be interpreted safely."""


@dataclass(frozen=True)
class SourceConfig:
    url: str
    sha256: str | None = None


@dataclass(frozen=True)
class DataConfig:
    release: str = "male-cns:v1.0"
    weights_path: Path = Path("data/raw/connectome-weights-male-cns-v1.0-minconf-0.5.feather")
    annotations_path: Path = Path("data/raw/body-annotations-male-cns-v1.0-minconf-0.5.feather")
    neurotransmitters_path: Path = Path("data/raw/body-neurotransmitters-male-cns-v1.0.feather")
    output_dir: Path = Path("data/processed/male-cns-v1.0")
    manifest_dir: Path = Path("data/manifests")
    sources: Mapping[str, SourceConfig] = field(default_factory=dict)


@dataclass(frozen=True)
class GraphConfig:
    matrix_convention: str = "W[post_index, pre_index]"
    output_dir: Path = Path("data/processed/male-cns-v1.0")
    weight_transform: str = "log1p"
    sign_mode: str = "unsigned"
    modulator_treatment: str = "zero"
    normalization: str = "incoming_l1"
    spectral_radius: float | None = None
    epsilon: float = 1e-8
    allow_self_edges: bool = True
    node_filter_column: str | None = None
    node_filter_values: tuple[object, ...] | None = None
    body_id_dtype: str = "uint64"
    weight_dtype: str = "float32"


@dataclass(frozen=True)
class FlyGIConfig:
    schema_version: int
    seed: int
    data: DataConfig
    graph: GraphConfig
    groups: Mapping[str, Any] = field(default_factory=dict)
    future: Mapping[str, Any] = field(default_factory=dict)


def _mapping(value: object, name: str) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ConfigError(f"{name} must be a mapping")
    return dict(value)


def load_config(path: str | Path) -> FlyGIConfig:
    """Load Milestone 0-1 settings while preserving declared future sections."""

    config_path = Path(path).resolve()
    path_base = (
        config_path.parent.parent if config_path.parent.name == "configs" else config_path.parent
    )

    def resolved_path(value: object) -> Path:
        candidate = Path(value)
        return candidate if candidate.is_absolute() else path_base / candidate

    try:
        raw = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigError(f"could not read config {config_path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"invalid YAML in {config_path}: {exc}") from exc

    root = _mapping(raw, "configuration")
    schema_version = int(root.pop("schema_version", 1))
    if schema_version != 1:
        raise ConfigError(f"unsupported schema_version {schema_version}; expected 1")
    experiment = _mapping(root.pop("experiment", None), "experiment")
    legacy_seed = root.pop("seed", 20260919)
    seed = int(experiment.pop("seed", legacy_seed))
    data_raw = _mapping(root.pop("data", None), "data")
    graph_raw = _mapping(root.pop("graph", None), "graph")
    groups = _mapping(root.pop("groups", None), "groups")

    source_raw = _mapping(
        data_raw.pop("sources", root.pop("source_catalog", None)),
        "source_catalog",
    )
    sources: dict[str, SourceConfig] = {}
    for source_name, source_value in source_raw.items():
        source = _mapping(source_value, f"data.sources.{source_name}")
        if "url" not in source:
            raise ConfigError(f"data.sources.{source_name}.url is required")
        digest = source.pop("sha256", None)
        sources[source_name] = SourceConfig(
            url=str(source.pop("url")),
            sha256=None if digest is None else str(digest),
        )
        if source:
            raise ConfigError(f"unknown data.sources.{source_name} keys: {sorted(source)}")

    graph_contract = _mapping(root.pop("graph_contract", None), "graph_contract")
    for key, value in graph_contract.items():
        if key in graph_raw and graph_raw[key] != value:
            raise ConfigError(f"conflicting graph and graph_contract value for {key}")
        graph_raw[key] = value

    raw_dir_value = data_raw.pop("raw_dir", None)
    raw_dir = resolved_path(raw_dir_value if raw_dir_value is not None else "data/raw")
    try:
        data = DataConfig(
            release=str(data_raw.pop("release", "male-cns:v1.0")),
            weights_path=resolved_path(
                data_raw.pop(
                    "weights_path",
                    raw_dir / "connectome-weights-male-cns-v1.0-minconf-0.5.feather",
                )
            ),
            annotations_path=resolved_path(
                data_raw.pop(
                    "annotations_path",
                    raw_dir / "body-annotations-male-cns-v1.0-minconf-0.5.feather",
                )
            ),
            neurotransmitters_path=resolved_path(
                data_raw.pop(
                    "neurotransmitters_path",
                    raw_dir / "body-neurotransmitters-male-cns-v1.0.feather",
                )
            ),
            output_dir=resolved_path(data_raw.pop("output_dir", "data/processed/male-cns-v1.0")),
            manifest_dir=resolved_path(data_raw.pop("manifest_dir", "data/manifests")),
            sources=sources,
        )
        node_filter_column_raw = graph_raw.pop("node_filter_column", None)
        node_filter_values_raw = graph_raw.pop("node_filter_values", None)
        if node_filter_values_raw is not None and not isinstance(
            node_filter_values_raw, (list, tuple)
        ):
            raise ConfigError("graph.node_filter_values must be a list or null")
        graph = GraphConfig(
            matrix_convention=str(graph_raw.pop("matrix_convention", "W[post_index, pre_index]")),
            output_dir=resolved_path(graph_raw.pop("output_dir", "data/processed/male-cns-v1.0")),
            weight_transform=str(graph_raw.pop("weight_transform", "log1p")),
            sign_mode=str(graph_raw.pop("sign_mode", "unsigned")),
            modulator_treatment=str(graph_raw.pop("modulator_treatment", "zero")),
            normalization=str(graph_raw.pop("normalization", "incoming_l1")),
            spectral_radius=(
                None
                if graph_raw.get("spectral_radius") is None
                else float(graph_raw["spectral_radius"])
            ),
            epsilon=float(graph_raw.pop("epsilon", 1e-8)),
            allow_self_edges=bool(graph_raw.pop("allow_self_edges", True)),
            node_filter_column=(
                None if node_filter_column_raw is None else str(node_filter_column_raw)
            ),
            node_filter_values=(
                None if node_filter_values_raw is None else tuple(node_filter_values_raw)
            ),
            body_id_dtype=str(graph_raw.pop("body_id_dtype", "uint64")),
            weight_dtype=str(graph_raw.pop("weight_dtype", "float32")),
        )
        graph_raw.pop("spectral_radius", None)
    except (TypeError, ValueError) as exc:
        raise ConfigError(f"invalid configuration value: {exc}") from exc

    if data_raw:
        raise ConfigError(f"unknown data keys: {sorted(data_raw)}")
    if graph_raw:
        raise ConfigError(f"unknown graph keys: {sorted(graph_raw)}")
    if graph.weight_transform not in {"raw", "log1p", "sqrt", "binary"}:
        raise ConfigError(f"unsupported weight_transform: {graph.weight_transform}")
    if graph.sign_mode not in {"unsigned", "heuristic"}:
        raise ConfigError(f"unsupported sign_mode: {graph.sign_mode}")
    if graph.normalization not in {"none", "incoming_l1", "spectral_radius"}:
        raise ConfigError(f"unsupported normalization: {graph.normalization}")
    if graph.epsilon <= 0:
        raise ConfigError("graph.epsilon must be positive")
    if graph.matrix_convention != "W[post_index, pre_index]":
        raise ConfigError("graph.matrix_convention must be exactly 'W[post_index, pre_index]'")
    if graph.body_id_dtype != "uint64":
        raise ConfigError("graph.body_id_dtype must be uint64")
    if graph.weight_dtype != "float32":
        raise ConfigError("graph.weight_dtype must be float32")

    # Name/track are descriptive and remain available to manifests without
    # coupling Milestone 0-1 code to later experimental tracks.
    root["experiment"] = experiment

    return FlyGIConfig(
        schema_version=schema_version,
        seed=seed,
        data=data,
        graph=graph,
        groups=groups,
        future=root,
    )
