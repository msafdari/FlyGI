"""Public CLI integration over tiny local Feather sources."""

from __future__ import annotations

import json

import pandas as pd
import yaml

from flygi.cli import main


def test_cli_build_then_validate_tiny_asset(
    tmp_path,
    tiny_annotations: pd.DataFrame,
    tiny_neurotransmitters: pd.DataFrame,
    capsys,
) -> None:
    a, b = (int(value) for value in tiny_annotations["bodyId"].iloc[:2])
    weights = pd.DataFrame(
        {
            "body_pre": pd.Series([a], dtype="int64"),
            "body_post": pd.Series([b], dtype="int64"),
            "weight": pd.Series([4], dtype="int64"),
        }
    )
    weights_path = tmp_path / "weights.feather"
    annotations_path = tmp_path / "annotations.feather"
    neurotransmitters_path = tmp_path / "neurotransmitters.feather"
    weights.to_feather(weights_path)
    tiny_annotations.to_feather(annotations_path)
    tiny_neurotransmitters.to_feather(neurotransmitters_path)
    output = tmp_path / "runtime"
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "seed": 7,
                "data": {
                    "release": "male-cns:v1.0",
                    "weights_path": str(weights_path),
                    "annotations_path": str(annotations_path),
                    "neurotransmitters_path": str(neurotransmitters_path),
                    "output_dir": str(output),
                    "manifest_dir": str(tmp_path / "manifests"),
                    "sources": {
                        "weights": {"url": "https://example.invalid/weights", "sha256": None},
                        "annotations": {
                            "url": "https://example.invalid/annotations",
                            "sha256": None,
                        },
                        "neurotransmitters": {
                            "url": "https://example.invalid/neurotransmitters",
                            "sha256": None,
                        },
                    },
                },
                "graph": {
                    "matrix_convention": "W[post_index, pre_index]",
                    "output_dir": str(output),
                    "weight_transform": "raw",
                    "sign_mode": "unsigned",
                    "modulator_treatment": "zero",
                    "normalization": "none",
                    "spectral_radius": None,
                    "epsilon": 1e-8,
                    "allow_self_edges": False,
                    "body_id_dtype": "uint64",
                    "weight_dtype": "float32",
                },
                "groups": {
                    "descending_neurons": {"superclass": "descending"},
                },
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )

    assert main(["graph", "build", "--config", str(config_path)]) == 0
    build_summary = json.loads(capsys.readouterr().out)
    assert build_summary["counts"]["retained_neurons"] == 3
    assert (output / "manifest.json").is_file()

    assert main(["validate", "all", "--config", str(config_path), "--require-data"]) == 0
    validation = json.loads(capsys.readouterr().out)
    assert validation["config"] == "valid"
    assert validation["runtime"]["verified_files"] == 6
    assert validation["runtime"]["groups"] == {"descending_neurons": 1}
