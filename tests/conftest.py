"""Small, exact-schema MaleCNS fixtures used by offline acceptance tests."""

from __future__ import annotations

import pandas as pd
import pytest

from flygi.connectome.schema import ANNOTATIONS_COLUMNS, NEUROTRANSMITTER_COLUMNS


@pytest.fixture
def tiny_annotations() -> pd.DataFrame:
    body_ids = pd.Series([101, 2**40 + 7, 2**48 + 9], dtype="int64")
    values: dict[str, pd.Series] = {}
    for column in ANNOTATIONS_COLUMNS:
        if column == "bodyId":
            values[column] = body_ids
        else:
            values[column] = pd.Series(["", "", ""], dtype="string")
    values["type"] = pd.Series(["sensory", "interneuron", "descending"], dtype="string")
    values["superclass"] = pd.Series(["sensory", "central", "descending"], dtype="string")
    return pd.DataFrame(values, columns=ANNOTATIONS_COLUMNS)


@pytest.fixture
def tiny_neurotransmitters(tiny_annotations: pd.DataFrame) -> pd.DataFrame:
    body_ids = tiny_annotations["bodyId"].copy()
    values: dict[str, pd.Series] = {}
    for column in NEUROTRANSMITTER_COLUMNS:
        if column == "body":
            values[column] = body_ids.rename("body")
        elif column in {
            "total_nt_predictions",
            "predicted_nt_confidence",
            "celltype_total_nt_predictions",
            "celltype_predicted_nt_confidence",
        }:
            values[column] = pd.Series([1.0, 1.0, 1.0], dtype="float64")
        else:
            values[column] = pd.Series(["", "", ""], dtype="string")
    values["consensus_nt"] = pd.Series(["acetylcholine", "gaba", "dopamine"], dtype="string")
    return pd.DataFrame(values, columns=NEUROTRANSMITTER_COLUMNS)
