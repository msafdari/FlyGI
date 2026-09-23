"""The connectome as a guarded tiebreaker inside the state-graph controller.

This is the point of the whole project: find out what computation the fly's
innate wiring gives us *for free*, without training it and without letting it
pretend to knowledge it does not have.

The controller ranks candidate actions by a tuple:

    (retry_prefix, attempts, -(priority + exploration), TIEBREAK, bytes)

Everything before ``TIEBREAK`` encodes what the controller has actually learned:
which actions it has already retried, how often each has been attempted, and the
estimated effect of each. By default ``TIEBREAK`` is a deterministic hash --
arbitrary, reproducible, and carrying no information.

The fly goes exactly there, and nowhere else. It therefore **cannot** override
legality, a known death state, a verified plan, or any learned effect estimate.
It speaks only when the controller is genuinely indifferent between candidates,
which is precisely the situation where a useful prior would help and a useless
one would cost nothing.

That placement also makes the experiment clean. Swapping the real connectome for
a degree-preserving rewiring, or for the hash, changes one thing and nothing
else. If the real graph breaks ties better than a hash does, that is computation
obtained from anatomy alone.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray


class FlyTiebreakError(RuntimeError):
    """Raised when the connectome tiebreaker cannot be assembled."""


class FlyTiebreaker:
    """Scores candidate actions from descending-neuron activity."""

    def __init__(
        self,
        config: Any,
        *,
        runtime_dir: str | Path | None = None,
        bundle: Any | None = None,
        projection: Any | None = None,
    ) -> None:
        from flygi.arc.factory import build_connectome_policy

        class _NullActions:
            """The tiebreaker never emits an action, so it needs no factory."""

            RESET = 0

            @staticmethod
            def from_id(identifier: int) -> int:
                return identifier

        try:
            # ``bundle``/``projection`` let a caller that has already paid for the
            # 24.5M-edge load reuse it. On Kaggle every game constructs a fresh
            # agent, so reloading per game would dominate the action budget.
            assembled = build_connectome_policy(
                config,
                _NullActions,
                runtime_dir=runtime_dir,
                bundle=bundle,
                projection=projection,
            )
        except Exception as exc:  # A missing runtime must fail loudly, not silently.
            raise FlyTiebreakError(f"could not assemble the connectome: {exc}") from exc

        self._policy = assembled.policy
        self._bundle = assembled.bundle
        self._network = self._policy._network
        self._readout = self._policy._readout
        self._action_map = self._policy._action_map
        self._coordinates = self._policy._coordinates
        self._standardizer = self._policy._standardizer
        self._projection = assembled.projection
        self._state = self._network.initial_state()
        self._previous_grid: NDArray[np.int8] | None = None
        self._trace: NDArray[np.float32] | None = None
        self._action_logits: NDArray[np.float32] | None = None
        self._x_scores: NDArray[np.float32] | None = None
        self._y_scores: NDArray[np.float32] | None = None
        self._turns = 0

    @property
    def turns_observed(self) -> int:
        return self._turns

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "connectome_tiebreak",
            "placement": "tie position only; cannot override legality, death states, "
            "verified plans, or learned effect estimates",
            "nodes": self._bundle.node_count,
            "edges": self._bundle.edge_count,
            "readout": self._readout.size,
            "internal_steps": self._policy.internal_steps,
            "trainable_parameters": 0,
            "turns_observed": self._turns,
        }

    def observe(self, grid: NDArray[np.integer], legal_action_ids: tuple[int, ...]) -> None:
        """Advance the connectome on this turn's frame and cache its readout."""

        from flygi.encoding.features import encode_observation

        class _Frame:
            def __init__(self, g: Any) -> None:
                self.frame = [g]

        features = encode_observation(
            _Frame(np.asarray(grid)),
            previous_grid=self._previous_grid,
            previous_action_id=None,
            available_action_ids=tuple(legal_action_ids),
        )
        drive = self._projection.drive_features(features)
        self._state = self._network.advance(
            self._state, drive, internal_steps=self._policy.internal_steps
        )
        self._previous_grid = features.grid
        raw = self._readout.raw(self._state)
        self._trace = (
            self._standardizer.transform(raw)
            if self._standardizer is not None
            else self._readout.standardized(self._state)[0]
        )
        self._action_logits = self._action_map.logits(self._trace)
        self._x_scores, self._y_scores = self._coordinates.axis_scores(self._trace)
        self._turns += 1

    def preference(self, action_id: int, x: int | None, y: int | None) -> float:
        """Higher means the connectome prefers this candidate.

        Returns 0.0 before any observation, so an unobserved turn degrades to the
        controller's own ordering rather than to noise.
        """

        if self._action_logits is None:
            return 0.0
        score = float(self._action_logits[int(action_id)])
        if x is not None and y is not None:
            assert self._x_scores is not None and self._y_scores is not None
            score += float(self._x_scores[int(x)]) + float(self._y_scores[int(y)])
        return score

    def reset(self) -> None:
        self._state = self._network.initial_state()
        self._previous_grid = None
        self._trace = None
        self._action_logits = None
        self._x_scores = None
        self._y_scores = None
        self._turns = 0
        if self._standardizer is not None:
            self._standardizer.reset()


class GridHashTiebreaker:
    """A state-dependent tiebreaker with no connectome in it at all.

    This is the control that decides whether the fly result means anything.
    ``_tie_digest`` is constant with respect to what is on screen; the
    connectome is not, and that difference alone buys exploration diversity.
    So a gain over the hash does not yet implicate anatomy -- it may only show
    that varying the tiebreak with the observation helps.

    This class varies with the observation and contains no anatomy: a
    deterministic keyed digest of the grid, the action, and the coordinate. If
    it reproduces the connectome's gain, the honest report is that
    state-dependent tiebreaking helps and the fly is incidental.
    """

    def __init__(self, seed: int = 0) -> None:
        self._seed = int(seed)
        self._digest: bytes | None = None
        self._turns = 0

    @property
    def turns_observed(self) -> int:
        return self._turns

    def describe(self) -> dict[str, Any]:
        return {
            "kind": "grid_hash_tiebreak",
            "placement": "tie position only; identical seam to the connectome",
            "nodes": 0,
            "edges": 0,
            "readout": 0,
            "seed": self._seed,
            "trainable_parameters": 0,
            "turns_observed": self._turns,
        }

    def observe(self, grid: NDArray[np.integer], legal_action_ids: tuple[int, ...]) -> None:
        from hashlib import blake2b

        array = np.ascontiguousarray(np.asarray(grid, dtype=np.int8))
        self._digest = blake2b(array.tobytes(), digest_size=16).digest()
        self._turns += 1

    def preference(self, action_id: int, x: int | None, y: int | None) -> float:
        from hashlib import blake2b

        if self._digest is None:
            return 0.0
        key = f"{self._seed}:{int(action_id)}:{x}:{y}".encode()
        raw = blake2b(self._digest + key, digest_size=8).digest()
        # Map to [0, 1) so the scale is comparable to a standardized readout.
        return int.from_bytes(raw, "big") / float(1 << 64)

    def reset(self) -> None:
        self._digest = None
        self._turns = 0
