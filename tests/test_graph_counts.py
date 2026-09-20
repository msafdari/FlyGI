"""End-to-end tiny graph compilation, counts, groups, and immutability."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from flygi.connectome.build import BuildOptions, build_connectome, load_runtime_graph
from flygi.connectome.groups import load_groups
from flygi.connectome.manifest import sha256_file, verify_manifest_hashes


def test_build_writes_sparse_assets_and_observed_counts(
    tmp_path, tiny_annotations: pd.DataFrame, tiny_neurotransmitters: pd.DataFrame
) -> None:
    a, b, c = (int(value) for value in tiny_annotations["bodyId"])
    weights = pd.DataFrame(
        {
            "body_pre": pd.Series([a, a, b, c], dtype="int64"),
            "body_post": pd.Series([b, b, c, c], dtype="int64"),
            "weight": pd.Series([2, 3, 4, 7], dtype="int64"),
        }
    )
    output = tmp_path / "runtime"
    options = BuildOptions(
        weight_transform="raw",
        sign_mode="unsigned",
        normalization="none",
        allow_self_edges=False,
        node_filter_column=None,
    )

    manifest = build_connectome(
        weights,
        tiny_annotations,
        tiny_neurotransmitters,
        output,
        options=options,
        group_definitions={"descending": {"type": "descending"}},
    )

    counts = manifest["counts"]
    assert counts["annotated_neurons"] == 3
    assert counts["retained_neurons"] == 3
    assert counts["aggregated_directed_edges"] == 2
    assert counts["runtime_nonzero_edges"] == 2
    assert counts["synaptic_contact_weight_sum"] == 9
    assert counts["source_synaptic_contact_weight_sum"] == 16
    assert counts["source_self_edges"] == 1
    assert counts["self_edges"] == 0
    assert counts["missing_annotations"] == 0
    assert counts["disconnected_nodes"] == 0

    matrix, node_index = load_runtime_graph(output / "graph.npz")
    assert matrix.shape == (3, 3)
    assert matrix.nnz == 2
    assert matrix.dtype == np.float32
    assert node_index.body_ids.dtype == np.uint64
    ia, ib, ic = node_index.indices_for([a, b, c])
    assert matrix[ib, ia] == 5
    assert matrix[ic, ib] == 4
    assert matrix[ic, ic] == 0

    groups = load_groups(output / "groups.npz")
    np.testing.assert_array_equal(groups["descending"], [ic])
    verified = verify_manifest_hashes(manifest, root=output)
    assert len(verified) == 3
    on_disk = json.loads((output / "manifest.json").read_text(encoding="utf-8"))
    assert on_disk == manifest

    with pytest.raises(FileExistsError, match="refusing to overwrite"):
        build_connectome(
            weights,
            tiny_annotations,
            tiny_neurotransmitters,
            output,
            options=options,
        )


def test_missing_annotation_is_counted_not_silently_retained(
    tmp_path, tiny_annotations: pd.DataFrame, tiny_neurotransmitters: pd.DataFrame
) -> None:
    known = int(tiny_annotations.iloc[0]["bodyId"])
    unknown = 2**50 + 123
    weights = pd.DataFrame(
        {
            "body_pre": pd.Series([known], dtype="int64"),
            "body_post": pd.Series([unknown], dtype="int64"),
            "weight": pd.Series([9], dtype="int64"),
        }
    )

    manifest = build_connectome(
        weights,
        tiny_annotations,
        tiny_neurotransmitters,
        tmp_path / "runtime",
        options=BuildOptions(normalization="none", node_filter_column=None),
        group_definitions={},
    )

    assert manifest["counts"]["missing_annotations"] == 1
    assert manifest["counts"]["edges_dropped_missing_annotations"] == 1
    assert manifest["counts"]["aggregated_directed_edges"] == 0


def test_file_backed_feather_build_records_source_provenance(
    tmp_path, tiny_annotations: pd.DataFrame, tiny_neurotransmitters: pd.DataFrame
) -> None:
    a, b = (int(value) for value in tiny_annotations["bodyId"].iloc[:2])
    weights = pd.DataFrame(
        {
            "body_pre": pd.Series([a], dtype="int64"),
            "body_post": pd.Series([b], dtype="int64"),
            "weight": pd.Series([6], dtype="int64"),
        }
    )
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    weights_path = source_dir / "weights.feather"
    annotations_path = source_dir / "annotations.feather"
    neurotransmitters_path = source_dir / "neurotransmitters.feather"
    weights.to_feather(weights_path)
    tiny_annotations.to_feather(annotations_path)
    tiny_neurotransmitters.to_feather(neurotransmitters_path)
    output = tmp_path / "runtime"

    manifest = build_connectome(
        weights_path,
        annotations_path,
        neurotransmitters_path,
        output,
        options=BuildOptions(normalization="none", node_filter_column=None),
        group_definitions={},
        source_expected_hashes={"weights": sha256_file(weights_path)},
    )

    for source in manifest["sources"]:
        assert Path(source["path"]).is_absolute()
        assert len(source["sha256"]) == 64
        assert source["downloaded_at"].endswith("Z")
        assert source["timestamp_source"] == "file_mtime"
    assert manifest["sources"][0]["hash_verified"] is True
    assert manifest["sources"][1]["hash_verified"] is False
    assert len(verify_manifest_hashes(manifest, root=output)) == 6


def test_declared_superclass_filter_is_applied_and_recorded(
    tmp_path, tiny_annotations: pd.DataFrame, tiny_neurotransmitters: pd.DataFrame
) -> None:
    annotations = tiny_annotations.copy()
    annotations.loc[annotations.index[0], "superclass"] = pd.NA
    retained_ids = [int(value) for value in annotations["bodyId"].iloc[1:]]
    weights = pd.DataFrame(
        {
            "body_pre": pd.Series([retained_ids[0]], dtype="int64"),
            "body_post": pd.Series([retained_ids[1]], dtype="int64"),
            "weight": pd.Series([1], dtype="int64"),
        }
    )

    manifest = build_connectome(
        weights,
        annotations,
        tiny_neurotransmitters,
        tmp_path / "runtime",
        options=BuildOptions(
            normalization="none",
            node_filter_column="superclass",
            node_filter_values=None,
        ),
        group_definitions={"descending": {"superclass": "descending"}},
    )

    assert manifest["counts"]["annotated_neurons"] == 3
    assert manifest["counts"]["retained_neurons"] == 2
    assert manifest["preprocessing"]["node_filter_column"] == "superclass"
    assert manifest["preprocessing"]["node_filter_semantics"] == "non-null/non-empty"
