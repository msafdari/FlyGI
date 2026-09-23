#!/usr/bin/env python3
"""Run the Milestone 0-1 validation suite through the public CLI."""

from __future__ import annotations

import sys
from pathlib import Path

from flygi.cli import main

if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    default_config = Path(__file__).resolve().parents[1] / "configs/literal_rate.yaml"
    arguments = list(sys.argv[1:])
    if "--config" not in arguments:
        arguments.extend(["--config", str(default_config)])
    raise SystemExit(entrypoint("smoke_test", main, ["validate", "all", *arguments]))
