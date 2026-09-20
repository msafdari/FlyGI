"""Dependency-free structural types for the ARC adapter boundary.

The production objects satisfying these protocols come from ``arcengine``.
Keeping the types structural lets the FlyGI core run in unit tests and in
non-Kaggle evaluation code without importing the competition framework.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class FrameLike(Protocol):
    """The portion of an ARC frame needed by a policy."""

    state: object
    available_actions: Sequence[object]


@runtime_checkable
class ActionLike(Protocol):
    """The portion of an ARC action used by the random legal baseline."""

    value: int
    reasoning: Any

    def is_complex(self) -> bool:
        """Return whether this action needs an action-data payload."""

    def set_data(self, data: dict[str, Any]) -> object:
        """Attach an action-data payload and return the validated payload."""


class ActionFactory(Protocol):
    """Structural type of the official ``GameAction`` enum class."""

    RESET: ActionLike

    def from_id(self, action_id: int) -> ActionLike:
        """Resolve an integer action identifier."""
