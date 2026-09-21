"""The literal, untrained descending-neuron to ARC action mapping.

Track A has no ARC-specific trained parameter. Its action logits therefore come
from a partition of the descending population that the dataset itself fixes:
the readout is stored in ascending body-ID order, and it is split into eight
contiguous blocks, one per ARC action slot. Each block's mean standardized
activity is that action's logit.

No fitting or per-game branch enters this mapping. It is arbitrary in the sense
that fly descending neurons do not encode ARC actions, which is stated plainly
in the documentation rather than disguised by biological naming. What it is
not is *trained*: the same partition and scale-aware sampler apply to every
graph condition and every game.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .dn_trace import ReadoutError, contiguous_groups

ACTION_SLOTS = 8
SAMPLING_METHOD = "zscore_softmax_categorical"
_SCALE_EPSILON = 1e-8


def _validate_temperature(value: float, name: str = "temperature") -> float:
    temperature = float(value)
    if not np.isfinite(temperature) or temperature <= 0.0:
        raise ReadoutError(f"{name} must be finite and positive")
    return temperature


def scale_aware_probabilities(
    logits: NDArray[np.floating], temperature: float
) -> tuple[NDArray[np.float64], float]:
    """Turn finite logits into probabilities without depending on raw scale.

    The logits are centered and divided by their population standard deviation
    before the temperature is applied. A singleton or numerically flat vector
    becomes a point mass or a uniform distribution respectively. This prevents
    a fixed raw temperature from becoming nearly uniform merely because one
    graph condition has smaller readout magnitudes than another.
    """

    values = np.asarray(logits, dtype=np.float64)
    if values.ndim != 1 or values.size == 0:
        raise ReadoutError("categorical logits must be a nonempty one-dimensional vector")
    if not np.isfinite(values).all():
        raise ReadoutError("categorical logits must all be finite")
    checked_temperature = _validate_temperature(temperature)
    if values.size == 1:
        return np.ones(1, dtype=np.float64), 0.0

    scale = float(values.std())
    if scale <= _SCALE_EPSILON:
        return np.full(values.size, 1.0 / values.size, dtype=np.float64), scale

    standardized = (values - float(values.mean())) / scale
    exponent = standardized / checked_temperature
    exponent -= float(exponent.max())
    weights = np.exp(exponent)
    probabilities = weights / float(weights.sum())
    if not np.isfinite(probabilities).all() or not np.isclose(probabilities.sum(), 1.0):
        raise ReadoutError("scale-aware categorical normalization failed")
    return probabilities, scale


@dataclass(frozen=True, slots=True)
class ActionDecision:
    """One decoded action together with the evidence behind it."""

    action_id: int
    logits: NDArray[np.float32]
    masked_logits: NDArray[np.float32]
    legal_action_ids: tuple[int, ...]
    argmax_was_unique: bool
    probabilities: NDArray[np.float64]
    selected_probability: float
    entropy_bits: float
    logit_scale: float


class LiteralActionMap:
    """Fixed contiguous descending-neuron blocks, one per ARC action slot."""

    def __init__(
        self,
        readout_size: int,
        *,
        action_slots: int = ACTION_SLOTS,
        temperature: float = 0.35,
    ) -> None:
        if action_slots <= 0:
            raise ReadoutError("action_slots must be positive")
        self._readout_size = int(readout_size)
        self._action_slots = int(action_slots)
        self._temperature = _validate_temperature(temperature, "action temperature")
        self._blocks = contiguous_groups(readout_size, action_slots)

    @property
    def readout_size(self) -> int:
        return self._readout_size

    @property
    def action_slots(self) -> int:
        return self._action_slots

    @property
    def temperature(self) -> float:
        return self._temperature

    def describe(self) -> dict[str, object]:
        return {
            "kind": "literal_contiguous_dn_blocks",
            "action_slots": self._action_slots,
            "readout_size": self._readout_size,
            "block_sizes": [int(block.size) for block in self._blocks],
            "ordering": "ascending body id",
            "selection": SAMPLING_METHOD,
            "scale": "population standard deviation of legal logits",
            "temperature": self._temperature,
            "trainable": False,
            "trainable_parameters": 0,
        }

    def logits(self, trace: NDArray[np.float32]) -> NDArray[np.float32]:
        values = np.asarray(trace, dtype=np.float32)
        if values.shape != (self._readout_size,):
            raise ReadoutError(
                f"action map expects shape ({self._readout_size},), observed {values.shape}"
            )
        if not np.isfinite(values).all():
            raise ReadoutError("action map received a non-finite trace")
        return np.asarray(
            [float(values[block].mean()) if block.size else 0.0 for block in self._blocks],
            dtype=np.float32,
        )

    def decide(
        self,
        trace: NDArray[np.float32],
        legal_action_ids: tuple[int, ...] | list[int],
        *,
        rng: np.random.Generator,
    ) -> ActionDecision:
        """Sample one legal action; illegal actions have exactly zero mass."""

        legal = tuple(dict.fromkeys(int(identifier) for identifier in legal_action_ids))
        if not legal:
            raise ReadoutError("cannot decode an action from an empty legal-action mask")
        for identifier in legal:
            if not 0 <= identifier < self._action_slots:
                raise ReadoutError(
                    f"legal action id {identifier} is outside the declared "
                    f"{self._action_slots} action slots"
                )

        scores = self.logits(trace)
        masked = np.full(self._action_slots, -np.inf, dtype=np.float32)
        legal_index = np.asarray(legal, dtype=np.int64)
        masked[legal_index] = scores[legal_index]

        best = int(np.argmax(masked))
        top = masked[legal_index]
        unique = bool(np.count_nonzero(top == masked[best]) == 1)
        legal_probabilities, logit_scale = scale_aware_probabilities(top, self._temperature)
        selected_offset = int(rng.choice(len(legal), p=legal_probabilities))
        selected = legal[selected_offset]
        probabilities = np.zeros(self._action_slots, dtype=np.float64)
        probabilities[legal_index] = legal_probabilities
        positive = legal_probabilities[legal_probabilities > 0.0]
        entropy = float(-np.sum(positive * np.log2(positive)))
        if selected not in legal or probabilities[selected] <= 0.0:
            raise ReadoutError("masking failed to restrict the decision to legal actions")
        return ActionDecision(
            action_id=selected,
            logits=scores,
            masked_logits=masked,
            legal_action_ids=legal,
            argmax_was_unique=unique,
            probabilities=probabilities,
            selected_probability=float(probabilities[selected]),
            entropy_bits=entropy,
            logit_scale=logit_scale,
        )
