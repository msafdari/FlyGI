"""Deterministic seed helpers used across preprocessing and experiments."""

from __future__ import annotations

import hashlib
import os
import random

import numpy as np


def derive_seed(base_seed: int, namespace: str) -> int:
    """Derive a stable 64-bit seed without depending on Python's salted ``hash``."""

    payload = f"{base_seed}:{namespace}".encode()
    return int.from_bytes(hashlib.sha256(payload).digest()[:8], "big", signed=False)


def seed_everything(seed: int) -> np.random.Generator:
    """Seed supported CPU RNGs and return the preferred NumPy generator.

    ``PYTHONHASHSEED`` only affects new Python interpreters; setting it here records
    the intended value for subprocesses while avoiding a false claim that the
    current interpreter's hash randomization changed.
    """

    normalized = seed & ((1 << 64) - 1)
    os.environ["PYTHONHASHSEED"] = str(normalized)
    random.seed(normalized)
    return np.random.default_rng(normalized)
