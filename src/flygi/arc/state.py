"""Small, framework-independent helpers for ARC turn state."""

from __future__ import annotations

from dataclasses import dataclass
from numbers import Integral
from typing import Any

from .protocol import FrameLike


def symbolic_name(value: object) -> str:
    """Return a stable symbolic name for an enum-like state value.

    ``arcengine.GameState`` is a string enum, while light-weight tests often
    use a plain string or a small stand-in enum.  Normalizing at this boundary
    prevents the core package from depending on ``arcengine``.
    """

    name = getattr(value, "name", None)
    if isinstance(name, str):
        return name.upper()

    raw_value = getattr(value, "value", value)
    text = str(raw_value)
    return text.rsplit(".", maxsplit=1)[-1].upper()


def action_id(value: object) -> int:
    """Return the integer identifier of an int or enum-like ARC action."""

    raw_value: Any = getattr(value, "value", value)
    if isinstance(raw_value, bool) or not isinstance(raw_value, Integral):
        raise TypeError(f"ARC action identifiers must be integers, got {value!r}")
    return int(raw_value)


def available_action_ids(frame: FrameLike) -> tuple[int, ...]:
    """Normalize and de-duplicate a frame's legal-action mask."""

    raw_actions = getattr(frame, "available_actions", ())
    if raw_actions is None:
        return ()

    ordered_ids: list[int] = []
    seen: set[int] = set()
    for raw_action in raw_actions:
        identifier = action_id(raw_action)
        if identifier not in seen:
            seen.add(identifier)
            ordered_ids.append(identifier)
    return tuple(ordered_ids)


@dataclass(frozen=True, slots=True)
class ArcTurnState:
    """Normalized policy-facing state for one ARC turn."""

    game_state: str
    available_action_ids: tuple[int, ...]

    @classmethod
    def from_frame(cls, frame: FrameLike) -> ArcTurnState:
        return cls(
            game_state=symbolic_name(frame.state),
            available_action_ids=available_action_ids(frame),
        )

    @property
    def needs_reset(self) -> bool:
        return self.game_state in {"NOT_PLAYED", "GAME_OVER"}

    @property
    def is_win(self) -> bool:
        return self.game_state == "WIN"
