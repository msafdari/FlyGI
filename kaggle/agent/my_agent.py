"""Official ARC-AGI-3 ``MyAgent`` adapter for the FlyGI core policy.

The competition framework imports this module and requires the class and
method names below.  All behavior lives in ``flygi.arc`` so the scientific
core never imports Kaggle or the official agent harness.
"""

from __future__ import annotations

import hashlib
from typing import Any

from flygi.arc import RandomLegalPolicy

_ARC_IMPORT_ERROR: ModuleNotFoundError | None = None

try:
    from arcengine import FrameData, GameAction
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by import smoke
    _ARC_IMPORT_ERROR = exc
    FrameData = Any  # type: ignore[misc,assignment]
    GameAction = None  # type: ignore[assignment]

try:
    # The official ARC-AGI-3-Agents checkout is placed on sys.path by the
    # starter both locally and in its generated Kaggle notebook.
    from agents.agent import Agent
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by import smoke
    _ARC_IMPORT_ERROR = _ARC_IMPORT_ERROR or exc

    class Agent:  # type: ignore[no-redef]
        """Import-only fallback with an actionable runtime failure below."""

        MAX_ACTIONS = 80

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            del args
            self.game_id = str(kwargs.get("game_id", "unconfigured"))

        @property
        def name(self) -> str:
            return f"{self.game_id}.{self.__class__.__name__.lower()}"


def _seed_for_game(game_id: str) -> int:
    """Create a process-independent replay seed from the framework game id."""

    digest = hashlib.sha256(game_id.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


class MyAgent(Agent):
    """Deterministic random baseline that always respects the action mask."""

    MAX_ACTIONS = 80

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # ``rng_seed`` is a FlyGI-only testing/replay override and must not be
        # forwarded to the official Agent constructor.
        rng_seed = kwargs.pop("rng_seed", None)
        super().__init__(*args, **kwargs)
        if _ARC_IMPORT_ERROR is not None or GameAction is None:
            raise RuntimeError(
                "The ARC adapter requires the official 'arcengine' and "
                "'agents' packages. The dependency-free flygi.arc core can "
                "still be imported and tested without them."
            ) from _ARC_IMPORT_ERROR

        seed = _seed_for_game(str(self.game_id)) if rng_seed is None else int(rng_seed)
        self._policy = RandomLegalPolicy(GameAction, seed=seed)

    @property
    def name(self) -> str:
        return f"{super().name}.{self.MAX_ACTIONS}.random-legal"

    def is_done(self, frames: list[FrameData], latest_frame: FrameData) -> bool:
        del frames
        return self._policy.is_done(latest_frame)

    def choose_action(self, frames: list[FrameData], latest_frame: FrameData) -> GameAction:
        del frames
        return self._policy.choose_action(latest_frame)  # type: ignore[return-value]
