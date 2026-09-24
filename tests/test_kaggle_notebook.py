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

import pytest

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
    preflight_source = notebook["cells"][4]["source"]
    run_source = notebook["cells"][5]["source"]
    assert "spec_from_file_location" in preflight_source
    assert "'/tmp/my_agent.py'" in preflight_source
    assert ".preflight_runtime()" in preflight_source
    assert "if not os.getenv('KAGGLE_IS_COMPETITION_RERUN')" in preflight_source
    # The rerun now sets PYTHONPATH through subprocess env rather than a shell
    # prefix, and every step must fail loudly: `!` lines swallowed exit codes
    # for three straight ambiguous submissions.
    assert "environment['PYTHONPATH'] = '/tmp/flygi_runtime.zip'" in run_source
    assert "check=True" in run_source
    assert "main_returncode" in run_source
    assert "raise RuntimeError" in run_source


def test_preflight_cell_imports_adapter_and_runs_without_a_game(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("KAGGLE_IS_COMPETITION_RERUN", raising=False)
    builder = _load_builder()
    notebook = builder.build()
    source = notebook["cells"][4]["source"]
    adapter = tmp_path / "my_agent.py"
    adapter.write_text(
        "def preflight_runtime():\n"
        '    print(\'FLYGI_PREFLIGHT={\\"mode\\":\\"connectome\\",'
        '\\"verified\\":true}\')\n'
        "    return {'mode': 'connectome', 'verified': True}\n",
        encoding="utf-8",
    )
    namespace: dict[str, object] = {}

    exec(source.replace("/tmp/my_agent.py", str(adapter)), namespace)

    assert namespace["_flygi_runtime_identity"] == {
        "mode": "connectome",
        "verified": True,
    }
    assert (
        capsys.readouterr().out.strip() == 'FLYGI_PREFLIGHT={"mode":"connectome","verified":true}'
    )


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
