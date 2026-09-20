"""Policy entry points at the framework-independent ARC boundary."""

from .agent import NoLegalActionError, RandomLegalPolicy

__all__ = ["NoLegalActionError", "RandomLegalPolicy"]
