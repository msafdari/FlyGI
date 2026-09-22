"""A small trained action head over a frozen connectome readout (Track B).

Why this exists. The literal decoder splits the 1,314 descending neurons into
eight contiguous blocks by body-ID order and uses each block's mean as an action
logit. That map is arbitrary: fly descending neurons encode commands for a body
that is not present, and nothing aligns them with ARC's action slots. The
encoder is equally arbitrary. Freezing *both* the graph and its interface means
the composition is arbitrary no matter how good the graph is, which is the
simplest explanation for the measured result that the connectome does not beat
a matched bypass.

Track B unfreezes exactly one thing: a small readout. The graph, the encoder,
the descending population and the standardizer all stay frozen, so whatever the
head learns, it learns *through* the connectome's dynamics.

The parameter budget is kept deliberately small, and the same budget is
available to every graph condition including the no-recurrent-graph bypass. A
head large enough to solve the task by itself would prove nothing; the
specification's section 19.3 warning is that a parameter-matched adapter which
bypasses the graph can match it, and only an equal budget makes that comparison
meaningful.

Shape: the standardized descending trace is compressed by a *fixed seeded*
projection to ``feature_dim``, concatenated with the previous action one-hot and
the legal-action mask, and mapped linearly to eight action logits.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from .dn_trace import ReadoutError
from .literal import ACTION_SLOTS


@dataclass(frozen=True)
class TrainedHeadSpec:
    """Declared, recorded shape of the trainable readout."""

    readout_size: int
    feature_dim: int = 48
    action_slots: int = ACTION_SLOTS
    projection_seed: int = 20260922

    def __post_init__(self) -> None:
        if self.readout_size <= 0:
            raise ReadoutError("readout_size must be positive")
        if not 0 < self.feature_dim <= self.readout_size:
            raise ReadoutError("feature_dim must be in (0, readout_size]")
        if self.action_slots != ACTION_SLOTS:
            raise ReadoutError(f"action_slots must be {ACTION_SLOTS} for ARC-AGI-3")

    @property
    def input_dim(self) -> int:
        """Compressed readout, previous action one-hot, legal-action mask."""

        return self.feature_dim + 2 * self.action_slots

    @property
    def parameter_count(self) -> int:
        return self.input_dim * self.action_slots + self.action_slots


class TrainedActionHead:
    """A linear action head over a fixed compression of the frozen readout."""

    def __init__(self, spec: TrainedHeadSpec, parameters: NDArray[np.floating] | None = None):
        self._spec = spec
        generator = np.random.default_rng(spec.projection_seed)
        # Fixed, never trained, and identical across every graph condition.
        projection = generator.standard_normal((spec.feature_dim, spec.readout_size))
        projection /= np.sqrt(spec.readout_size)
        self._projection = projection.astype(np.float32)
        self._projection.flags.writeable = False
        self._parameters = np.zeros(spec.parameter_count, dtype=np.float32)
        if parameters is not None:
            self.set_parameters(parameters)

    @property
    def spec(self) -> TrainedHeadSpec:
        return self._spec

    @property
    def parameter_count(self) -> int:
        return self._spec.parameter_count

    def get_parameters(self) -> NDArray[np.float32]:
        return self._parameters.copy()

    def set_parameters(self, parameters: NDArray[np.floating]) -> None:
        values = np.asarray(parameters, dtype=np.float32).ravel()
        if values.shape != (self._spec.parameter_count,):
            raise ReadoutError(
                f"expected {self._spec.parameter_count} parameters, observed {values.shape}"
            )
        if not np.isfinite(values).all():
            raise ReadoutError("head parameters must be finite")
        self._parameters = values.copy()

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "trained_linear_head",
            "readout_size": self._spec.readout_size,
            "feature_dim": self._spec.feature_dim,
            "input_dim": self._spec.input_dim,
            "action_slots": self._spec.action_slots,
            "projection_seed": self._spec.projection_seed,
            "projection_trainable": False,
            "trainable": True,
            "trainable_parameters": self._spec.parameter_count,
        }

    def features(
        self,
        trace: NDArray[np.floating],
        previous_action_id: int | None,
        legal_action_ids: tuple[int, ...] | list[int],
    ) -> NDArray[np.float32]:
        """Compress the readout and append the protocol context."""

        values = np.asarray(trace, dtype=np.float32)
        if values.shape != (self._spec.readout_size,):
            raise ReadoutError(
                f"trace must have shape ({self._spec.readout_size},), observed {values.shape}"
            )
        if not np.isfinite(values).all():
            raise ReadoutError("trained head received a non-finite trace")

        vector = np.zeros(self._spec.input_dim, dtype=np.float32)
        vector[: self._spec.feature_dim] = self._projection @ values
        base = self._spec.feature_dim
        if previous_action_id is not None:
            if not 0 <= int(previous_action_id) < self._spec.action_slots:
                raise ReadoutError(f"previous action id out of range: {previous_action_id}")
            vector[base + int(previous_action_id)] = 1.0
        mask_base = base + self._spec.action_slots
        for identifier in legal_action_ids:
            index = int(identifier)
            if not 0 <= index < self._spec.action_slots:
                raise ReadoutError(f"legal action id out of range: {index}")
            vector[mask_base + index] = 1.0
        return vector

    def logits(
        self,
        trace: NDArray[np.floating],
        previous_action_id: int | None,
        legal_action_ids: tuple[int, ...] | list[int],
    ) -> NDArray[np.float32]:
        """Return eight action logits. Masking remains the caller's job."""

        vector = self.features(trace, previous_action_id, legal_action_ids)
        weights = self._parameters[: self._spec.input_dim * self._spec.action_slots]
        weights = weights.reshape(self._spec.action_slots, self._spec.input_dim)
        bias = self._parameters[self._spec.input_dim * self._spec.action_slots :]
        result = weights @ vector + bias
        return np.asarray(result, dtype=np.float32)
