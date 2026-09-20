"""Framework-independent ARC policies used by competition adapters."""

from __future__ import annotations

import random
from contextlib import suppress
from typing import Any

from .protocol import ActionFactory, ActionLike, FrameLike
from .state import ArcTurnState, action_id


class NoLegalActionError(RuntimeError):
    """Raised when an active frame declares no action the policy can take."""


class RandomLegalPolicy:
    """Choose uniformly from the actions declared legal by the latest frame.

    ``actions`` is normally ``arcengine.GameAction``.  It is injected rather
    than imported so this module remains usable when the optional ARC runtime
    and Kaggle agent framework are not installed.
    """

    def __init__(
        self,
        actions: ActionFactory,
        *,
        seed: int | None = None,
        coordinate_min: int = 0,
        coordinate_max: int = 63,
    ) -> None:
        if coordinate_min > coordinate_max:
            raise ValueError("coordinate_min must not exceed coordinate_max")
        self._actions = actions
        self._rng = random.Random(seed)
        self._coordinate_min = coordinate_min
        self._coordinate_max = coordinate_max

    def is_done(self, latest_frame: FrameLike) -> bool:
        """Stop after a win; a game-over frame is reset and retried."""

        return ArcTurnState.from_frame(latest_frame).is_win

    def choose_action(self, latest_frame: FrameLike) -> ActionLike:
        """Return RESET when required, otherwise sample the legal-action mask."""

        turn = ArcTurnState.from_frame(latest_frame)
        reset = self._actions.RESET
        if turn.needs_reset:
            return reset

        reset_id = action_id(reset)
        candidates = [
            self._resolve_action(identifier)
            for identifier in turn.available_action_ids
            if identifier != reset_id
        ]
        if not candidates:
            # A reset-only mask is unusual but still has a legal answer.
            if reset_id in turn.available_action_ids:
                return reset
            raise NoLegalActionError(
                f"active ARC frame in state {turn.game_state!r} declares no legal actions"
            )

        action = self._rng.choice(candidates)
        self._prepare_action(action, turn.available_action_ids)
        return action

    def _resolve_action(self, identifier: int) -> ActionLike:
        resolver = getattr(self._actions, "from_id", None)
        if callable(resolver):
            try:
                return resolver(identifier)
            except ValueError as exc:
                raise NoLegalActionError(
                    f"frame declared unknown ARC action id {identifier}"
                ) from exc

        # The fallback keeps simple enum fakes convenient without weakening
        # production behavior, where GameAction.from_id is available.
        for action in self._actions:  # type: ignore[union-attr]
            if action_id(action) == identifier:
                return action
        raise NoLegalActionError(f"frame declared unknown ARC action id {identifier}")

    def _prepare_action(self, action: ActionLike, legal_action_ids: tuple[int, ...]) -> None:
        complex_check = getattr(action, "is_complex", None)
        is_complex = bool(complex_check()) if callable(complex_check) else False
        if is_complex:
            payload = {
                "x": self._rng.randint(self._coordinate_min, self._coordinate_max),
                "y": self._rng.randint(self._coordinate_min, self._coordinate_max),
            }
            setter = getattr(action, "set_data", None)
            if not callable(setter):
                raise TypeError("complex ARC actions must implement set_data(data)")
            setter(payload)
            reasoning: Any = {
                "policy": "random-legal",
                "legal_action_ids": list(legal_action_ids),
            }
        else:
            reasoning = "random-legal baseline"

        # Reasoning is optional policy metadata.  Official GameAction members
        # accept it, but omitting it is safe for minimal test doubles.
        with suppress(AttributeError, TypeError):
            action.reasoning = reasoning
