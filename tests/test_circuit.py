"""APL gain and the mushroom-body input bus: scoped, declared, non-overlapping.

The dangerous failure for both is silent scope creep: an APL gain that touches
one edge outside APL->KC changes the connectome somewhere unaccountable, and a
bus that overlaps the visual projection double-drives neurons invisibly. Every
test here is about scope.
"""

from __future__ import annotations

import numpy as np
import pytest

from flygi.config import CircuitConfig, ConfigError
from flygi.encoding.features import GRID_SIZE, encode_observation
from flygi.encoding.mb_bus import (
    CompositeProjection,
    MushroomBodyBusError,
    PNColourBus,
)


class _Frame:
    def __init__(self, grid: np.ndarray) -> None:
        self.frame = [grid]


def _features(grid: np.ndarray):
    return encode_observation(
        _Frame(grid), previous_grid=None, previous_action_id=None, available_action_ids=(1,)
    )


TYPES = np.asarray(["DA1_lPN", "DM4_adPN", "VA2_l2PN", "KCg-m", "APL", "Mi1", "DNp01", "DL3_vPN"])


def test_the_bus_targets_projection_neurons_and_nothing_else() -> None:
    bus = PNColourBus(TYPES, node_count=8)
    grid = np.full((GRID_SIZE, GRID_SIZE), 3, dtype=np.int8)
    drive = bus.drive_features(_features(grid))
    expected_targets = {0, 1, 2, 7}  # the *PN entries
    assert set(np.flatnonzero(drive != 0).tolist()) <= expected_targets
    assert bus.describe()["neurons"] == 4


def test_the_bus_drive_is_the_colour_histogram() -> None:
    bus = PNColourBus(TYPES, node_count=8, input_scale=2.0)
    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int8)
    grid[:, : GRID_SIZE // 2] = 1  # half the screen colour 1, half colour 0
    drive = bus.drive_features(_features(grid))
    populated = drive[drive != 0]
    assert populated.size > 0
    assert np.allclose(populated, 2.0 * 0.5), "drive is not the screen fraction times scale"


def test_no_projection_neurons_fails_loudly() -> None:
    with pytest.raises(MushroomBodyBusError, match="annotation scheme"):
        PNColourBus(np.asarray(["KCg-m", "APL", "Mi1"]), node_count=3)


def test_the_composite_sums_and_refuses_overlap() -> None:
    class _Stub:
        def __init__(self, indices, value):
            self.sensory_indices = np.asarray(indices, dtype=np.int64)
            self._value = value

        def describe(self):
            return {"kind": "stub"}

        def drive_features(self, _features):
            drive = np.zeros(8, dtype=np.float32)
            drive[self.sensory_indices] = self._value
            return drive

    grid = np.zeros((GRID_SIZE, GRID_SIZE), dtype=np.int8)
    composite = CompositeProjection(_Stub([0, 1], 1.0), _Stub([5, 6], 2.0))
    drive = composite.drive_features(_features(grid))
    assert drive[0] == 1.0 and drive[5] == 2.0
    assert composite.sensory_size == 4
    with pytest.raises(MushroomBodyBusError, match="double-drive"):
        CompositeProjection(_Stub([0, 1], 1.0), _Stub([1, 2], 2.0))


def test_circuit_config_rejects_nonsense() -> None:
    assert CircuitConfig().apl_to_kc_gain == 1.0
    with pytest.raises(ConfigError):
        CircuitConfig(apl_to_kc_gain=0.0)
    with pytest.raises(ConfigError):
        CircuitConfig(apl_to_kc_gain=float("nan"))


def test_the_efference_bus_targets_johnstons_organ_only() -> None:
    from flygi.encoding.mb_bus import EfferenceCopyBus

    types = np.asarray(["JO-A1", "JO-B2", "DA1_lPN", "KCg-m", "Mi1", "JO-C1", "DNp01"])
    bus = EfferenceCopyBus(types, node_count=7, input_scale=2.0)
    drive = bus.drive_action(3)
    assert set(np.flatnonzero(drive != 0).tolist()) <= {0, 1, 5}, "drive escaped Johnston's organ"
    assert bus.drive_action(None).sum() == 0.0, "an unknown action must drive nothing"
    a, b = bus.drive_action(1), bus.drive_action(2)
    assert not np.array_equal(a, b), "distinct actions must be distinguishable"
    assert np.array_equal(bus.drive_action(1), a), "the code must be deterministic"


def test_the_efference_bus_fails_loudly_without_jo_neurons() -> None:
    from flygi.encoding.mb_bus import EfferenceCopyBus, MushroomBodyBusError

    with pytest.raises(MushroomBodyBusError, match="Johnston"):
        EfferenceCopyBus(np.asarray(["KCg-m", "Mi1"]), node_count=2)
