"""The literal, untrained descending-neuron to ARC action mapping.

Track A has no ARC-specific trained parameter. Its action logits therefore come
from a partition of the descending population that the dataset itself fixes:
the readout is stored in ascending body-ID order, and it is split into eight
contiguous blocks, one per ARC action slot. Each block's mean standardized
activity is that action's logit.

No seed, no tuning, and no per-game branch enters this mapping. It is arbitrary
in the sense that fly descending neurons do not encode ARC actions, which is
stated plainly in the documentation rather than disguised by biological naming.
What it is not is *fitted*: the same partition applies to every graph condition
and every game.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from .dn_trace import ReadoutError, contiguous_groups

ACTION_SLOTS = 8


@dataclass(frozen=True, slots=True)
class ActionDecision:
    """One decoded action together with the evidence behind it."""

    action_id: int
    logits: NDArray[np.float32]
    masked_logits: NDArray[np.float32]
    legal_action_ids: tuple[int, ...]
    argmax_was_unique: bool


class LiteralActionMap:
    """Fixed contiguous descending-neuron blocks, one per ARC action slot."""

    def __init__(self, readout_size: int, *, action_slots: int = ACTION_SLOTS) -> None:
        if action_slots <= 0:
            raise ReadoutError("action_slots must be positive")
        self._readout_size = int(readout_size)
        self._action_slots = int(action_slots)
        self._blocks = contiguous_groups(readout_size, action_slots)

    @property
    def readout_size(self) -> int:
        return self._readout_size

    @property
    def action_slots(self) -> int:
        return self._action_slots

    def describe(self) -> dict[str, object]:
        return {
            "kind": "literal_contiguous_dn_blocks",
            "action_slots": self._action_slots,
            "readout_size": self._readout_size,
            "block_sizes": [int(block.size) for block in self._blocks],
            "ordering": "ascending body id",
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
    ) -> ActionDecision:
        """Choose the highest-scoring legal action; masking is never bypassed."""

        legal = tuple(int(identifier) for identifier in legal_action_ids)
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
        if best not in legal:
            raise ReadoutError("masking failed to restrict the decision to legal actions")
        return ActionDecision(
            action_id=best,
            logits=scores,
            masked_logits=masked,
            legal_action_ids=legal,
            argmax_was_unique=unique,
        )
