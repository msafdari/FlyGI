#!/usr/bin/env python3
"""Thin wrapper for the FlyGI MaleCNS fetch command."""

from __future__ import annotations

import sys
from pathlib import Path

from flygi.cli import main

if __name__ == "__main__":
    default_config = Path(__file__).resolve().parents[1] / "configs/literal_rate.yaml"
    arguments = list(sys.argv[1:])
    if "--config" not in arguments:
        arguments.extend(["--config", str(default_config)])
    if "--release" not in arguments:
        arguments.extend(["--release", "male-cns:v1.0"])
    raise SystemExit(main(["data", "fetch", *arguments]))
