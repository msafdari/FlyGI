"""Offline notebook packaging must carry the FlyGI import path into the runner."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType

ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "scripts" / "build_notebook.py"


def _load_builder() -> ModuleType:
    spec = importlib.util.spec_from_file_location("_flygi_notebook_builder", BUILDER_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_notebook_is_offline_and_deterministic() -> None:
    builder = _load_builder()
    first = json.dumps(builder.build(), sort_keys=True).encode()
    second = json.dumps(builder.build(), sort_keys=True).encode()

    assert hashlib.sha256(first).digest() == hashlib.sha256(second).digest()
    notebook = json.loads(first)
    assert notebook["metadata"]["kaggle"]["isInternetEnabled"] is False
    assert notebook["metadata"]["kaggle"]["isGpuEnabled"] is False
    run_source = notebook["cells"][4]["source"]
    assert "PYTHONPATH=/tmp/flygi_runtime.zip" in run_source


def test_embedded_runtime_imports_in_a_fresh_interpreter(tmp_path) -> None:
    builder = _load_builder()
    runtime = tmp_path / "flygi_runtime.zip"
    runtime.write_bytes(builder._runtime_zip())
    environment = dict(os.environ)
    environment["PYTHONPATH"] = str(runtime)

    completed = subprocess.run(
        [sys.executable, "-c", "from flygi.arc import RandomLegalPolicy; print('ok')"],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert completed.stdout.strip() == "ok"
