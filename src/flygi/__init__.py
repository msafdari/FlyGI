"""FlyGI: connectome-constrained agents for ARC-AGI-3."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("flygi")
except PackageNotFoundError:  # Source checkout without an installed distribution.
    __version__ = "0.1.0"

__all__ = ["__version__"]
