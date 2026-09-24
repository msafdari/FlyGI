#!/usr/bin/env python3
"""Generate FlyGI's offline ARC-AGI-3 Kaggle submission notebook.

The execution pattern follows the official ARC-AGI-3 Kaggle Starter interface
at revision eeb1535404f321d280a8f9194bbc1d7aca5f05fc. FlyGI adds a deterministic
embedded source bundle so the thin adapter can import its core without network
access. See THIRD_PARTY_NOTICES.md.
"""

from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
from textwrap import dedent
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "src"
AGENT_SOURCE = ROOT / "kaggle" / "agent" / "my_agent.py"
NOTEBOOK_PATH = ROOT / "notebooks" / "submission.ipynb"
METADATA_PATH = ROOT / "notebooks" / "kernel-metadata.json"
FIXED_ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
ACCELERATOR = "cpu"
ACCELERATORS = {
    "cpu": {"name": "none", "gpu": False},
    "t4": {"name": "nvidiaTeslaT4", "gpu": True},
    "p100": {"name": "nvidiaTeslaP100", "gpu": True},
    "rtx6000": {"name": "nvidiaRtx6000", "gpu": True},
}


def _code_cell(source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "metadata": {"trusted": True},
        "outputs": [],
        "execution_count": None,
        "source": source,
    }


def _markdown_cell(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def _runtime_zip() -> bytes:
    """Return a deterministic zip containing only repository-owned Python."""

    from io import BytesIO

    buffer = BytesIO()
    manifest_files: list[dict[str, str]] = []
    with ZipFile(buffer, "w") as archive:
        for path in sorted((SOURCE_ROOT / "flygi").rglob("*.py")):
            data = path.read_bytes()
            name = path.relative_to(SOURCE_ROOT).as_posix()
            info = ZipInfo(name, date_time=FIXED_ZIP_TIMESTAMP)
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, data)
            manifest_files.append({"path": name, "sha256": hashlib.sha256(data).hexdigest()})
        manifest = {
            "format": "flygi-kaggle-runtime-v1",
            "contains_connectome_assets": False,
            "files": manifest_files,
        }
        info = ZipInfo("flygi_kaggle_manifest.json", date_time=FIXED_ZIP_TIMESTAMP)
        info.compress_type = ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, json.dumps(manifest, sort_keys=True).encode())
    return buffer.getvalue()


def build() -> dict[str, object]:
    if not AGENT_SOURCE.is_file():
        raise SystemExit(f"Could not find {AGENT_SOURCE}")
    if ACCELERATOR not in ACCELERATORS:
        raise SystemExit(f"Unknown accelerator {ACCELERATOR!r}")

    runtime_b64 = base64.b64encode(_runtime_zip()).decode("ascii")
    runtime_cell = _code_cell(
        "import base64, sys\n"
        f"_flygi_zip = base64.b64decode({runtime_b64!r})\n"
        "open('/tmp/flygi_runtime.zip', 'wb').write(_flygi_zip)\n"
        "sys.path.insert(0, '/tmp/flygi_runtime.zip')\n"
    )
    install_cell = _code_cell(
        "!pip install --no-index --find-links "
        "/kaggle/input/competitions/arc-prize-2026-arc-agi-3/arc_agi_3_wheels "
        "arc-agi python-dotenv"
    )
    write_agent_cell = _code_cell(
        "%%writefile /tmp/my_agent.py\n" + AGENT_SOURCE.read_text(encoding="utf-8")
    )
    preflight_cell = _code_cell(
        dedent(
            """\
            import importlib.util, os

            if not os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
                _flygi_adapter_spec = importlib.util.spec_from_file_location(
                    '_flygi_submission_adapter', '/tmp/my_agent.py'
                )
                if _flygi_adapter_spec is None or _flygi_adapter_spec.loader is None:
                    raise RuntimeError('could not import /tmp/my_agent.py for runtime preflight')
                _flygi_submission_adapter = importlib.util.module_from_spec(_flygi_adapter_spec)
                _flygi_adapter_spec.loader.exec_module(_flygi_submission_adapter)
                _flygi_runtime_identity = _flygi_submission_adapter.preflight_runtime()
            """
        )
    )
    slim_registry = dedent(
        """\
        from typing import Type
        from dotenv import load_dotenv
        from .agent import Agent, Playback
        from .swarm import Swarm
        from .templates.random_agent import Random
        from .templates.my_agent import MyAgent
        load_dotenv()
        AVAILABLE_AGENTS: dict[str, Type[Agent]] = {
            'random': Random,
            'myagent': MyAgent,
        }
        """
    )
    gateway_environment = dedent(
        """\
        SCHEME=http
        HOST=gateway
        PORT=8001
        ARC_API_KEY=test-key-123
        ARC_BASE_URL=http://gateway:8001/
        OPERATION_MODE=online
        ENVIRONMENTS_DIR=
        RECORDINGS_DIR=/kaggle/working/server_recording
        """
    )
    run_cell = _code_cell(
        dedent(
            f"""\
            import json, os, subprocess, time

            if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
                # Every step below previously ran through bare `!` shell lines,
                # which swallow exit codes: a dead gateway or a crashed main.py
                # still produced a "Succeeded" submission, making 0.00
                # indistinguishable from "never played". Three submissions were
                # ambiguous for exactly this reason. Now every failure raises,
                # so the submission STATUS itself is the diagnostic: Error means
                # infrastructure, Succeeded means the agent truly played.
                t0 = time.time()
                subprocess.run(
                    ['curl', '--fail', '--retry', '999', '--retry-all-errors',
                     '--retry-delay', '5', '--retry-max-time', '600',
                     'http://gateway:8001/api/games'],
                    check=True,
                )
                print(f'FLYGI_RERUN_GATEWAY_OK t={{time.time() - t0:.1f}}s', flush=True)
                subprocess.run(['cp', '-r',
                    '/kaggle/input/competitions/arc-prize-2026-arc-agi-3/ARC-AGI-3-Agents',
                    '/kaggle/working/ARC-AGI-3-Agents'], check=True)
                subprocess.run(['cp', '/tmp/my_agent.py',
                    '/kaggle/working/ARC-AGI-3-Agents/agents/templates/my_agent.py'],
                    check=True)
                with open('/kaggle/working/ARC-AGI-3-Agents/agents/__init__.py', 'w') as handle:
                    handle.write({slim_registry!r})
                with open('/kaggle/working/ARC-AGI-3-Agents/.env', 'w') as handle:
                    handle.write({gateway_environment!r})
                environment = dict(os.environ)
                environment['PYTHONPATH'] = '/tmp/flygi_runtime.zip'
                environment['MPLBACKEND'] = 'agg'
                completed = subprocess.run(
                    ['python', 'main.py', '--agent', 'myagent'],
                    cwd='/kaggle/working/ARC-AGI-3-Agents',
                    env=environment,
                )
                print(
                    'FLYGI_RERUN_SUMMARY='
                    + json.dumps({{
                        'main_returncode': completed.returncode,
                        'wall_s': round(time.time() - t0, 1),
                    }}),
                    flush=True,
                )
                if completed.returncode != 0:
                    raise RuntimeError(
                        f'main.py exited {{completed.returncode}}; failing the '
                        'submission loudly instead of scoring a ghost'
                    )
            """
        )
    )
    dummy_cell = _code_cell(
        dedent(
            """\
            import os
            if not os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
                import pandas as pd
                submission = pd.DataFrame(
                    data=[['1_0', '1', True, 1]],
                    columns=['row_id', 'game_id', 'end_of_game', 'score'],
                )
                submission.to_parquet('/kaggle/working/submission.parquet', index=False)
                submission.head()
            """
        )
    )
    accelerator = ACCELERATORS[ACCELERATOR]
    return {
        "metadata": {
            "kernelspec": {
                "language": "python",
                "display_name": "Python 3",
                "name": "python3",
            },
            "language_info": {"name": "python", "pygments_lexer": "ipython3"},
            "kaggle": {
                "accelerator": accelerator["name"],
                "isInternetEnabled": False,
                "isGpuEnabled": accelerator["gpu"],
                "language": "python",
                "sourceType": "notebook",
            },
        },
        "nbformat_minor": 4,
        "nbformat": 4,
        "cells": [
            _markdown_cell(
                "# FlyGI — ARC-AGI-3 submission\n\nGenerated; edit source files, not this notebook."
            ),
            install_cell,
            runtime_cell,
            write_agent_cell,
            preflight_cell,
            run_cell,
            dummy_cell,
        ],
    }


def main() -> None:
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    NOTEBOOK_PATH.write_text(json.dumps(build(), indent=1), encoding="utf-8")
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    metadata["enable_gpu"] = bool(ACCELERATORS[ACCELERATOR]["gpu"])
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"[build_notebook] wrote {NOTEBOOK_PATH.relative_to(ROOT)} ({ACCELERATOR})")


if __name__ == "__main__":
    from flygi.telemetry import entrypoint

    raise SystemExit(entrypoint("build_notebook", main))
