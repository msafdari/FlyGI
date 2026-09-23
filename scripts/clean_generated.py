#!/usr/bin/env python3
"""Remove FlyGI-generated development artifacts without broad recursive targets."""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = (
    ROOT / ".pytest_cache",
    ROOT / ".ruff_cache",
    ROOT / "kaggle" / "dist",
    ROOT / "notebooks" / "submission.ipynb",
    ROOT / "environment_files",
    ROOT / "recordings",
    ROOT / "logs.log",
)


def main() -> None:
    for target in TARGETS:
        if target.is_dir():
            shutil.rmtree(target)
        elif target.exists():
            target.unlink()
        print(f"cleaned {target.relative_to(ROOT)}")


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("clean_generated", main))
