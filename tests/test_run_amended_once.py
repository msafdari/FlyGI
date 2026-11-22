"""The once-only wrapper of the compass map amendment (2026-11-21).

scripts/arenas/run_amended_once.sh is what makes "each amended instrument
runs once, against the freeze" (amendment section 7, decision 7) true
rather than promised. These tests build a throwaway git repository with
stub instruments at the eleven registered paths, freeze it under the real
tag name, pin its stand-in inputs, and drive the real wrapper through the
cases its third, fourth and fifth reviews found broken in earlier versions:
a free label that let a finished instrument run again, protocol-changing
flags passed through, an outcome rule that disagreed with section 10, a
direct kill of the instrument recorded as a crash, two launches at once,
unpinned inputs, a re-run that could be put off until after other runs, a
record that fits two classes, a finished no-verdict run that read as a
failure, a freeze check that passed when git failed, and (sixth review) a
prerequisite exit left in place by a wrapper that died.

The trivial alternative is no wrapper at all, under which every refusal
below is simply a run that happens. Each test asserts the refusal or the
classification the amendment states. A fuller harness (204 checks)
lives outside the repository and is described in decision 7.

The wrapper reads system memory from kern.memorystatus_level, so it runs
on macOS only (the amended runs are made on one macOS machine).
"""
from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "arenas" / "run_amended_once.sh"
W = "scripts/arenas/run_amended_once.sh"
OUT = "results/arenas/amended_runs_20261121"
RT = "data/processed/male-cns-v1.0/literal-rate-signed-modulators"
CAPTURE = "results/diagnostics/recognizer_frames.npz"

pytestmark = [
    pytest.mark.skipif(sys.platform != "darwin",
                       reason="the wrapper reads kern.memorystatus_level (macOS)"),
    pytest.mark.skipif(shutil.which("git") is None, reason="needs git"),
]

INSTRUMENTS = [
    "arenas/cx_biswas_killtest", "arenas/cx_topology_killtest",
    "arenas/cx_heading_killtest", "arenas/cx_seeding_killtest",
    "arenas/cx_class3_killtest", "arenas/cx_biswas_context_nulls",
    "arenas/cx_topology_nulls2", "benchmarks/cx_ring",
    "benchmarks/fc2_eb_ring", "cx_scratchpad_premise", "arenas/other_script",
]

# The wrapper runs instruments under env -i, so the stub takes its mode
# from a file in the throwaway repository, not from the environment.
STUB = r'''
import json, os, signal, sys, time
from pathlib import Path
here = Path(__file__).resolve().relative_to(Path.cwd().resolve())
stem = here.stem
if "--settle-map" in sys.argv[1:]:
    stem = "cx_scratchpad_settle_map"
out = {"arenas": Path("results/arenas"),
       "benchmarks": Path("results/benchmarks")}.get(here.parent.name, Path("results"))
json_path = out / f"{stem}.amended_map.json"
mf = Path("stub_mode.txt")
mode = mf.read_text().strip() if mf.exists() else "pass"
print(f"stub {stem} mode {mode}", flush=True)
if mode == "prereq":
    print("BLOCKED -- the kill test cannot run here. Missing:")
    sys.exit(3)
out.mkdir(parents=True, exist_ok=True)
json_path.with_suffix(".log").write_text("log\n")
print("real: bandedness 0.5, mirror-peak 0.3", flush=True)
def write():
    json_path.write_text(json.dumps({"stem": stem}))
if mode == "pass":
    write(); print("VERDICT: PASS"); sys.exit(0)
if mode == "kill":
    write(); print("VERDICT: KILL"); sys.exit(1)
if mode == "traceback":
    raise RuntimeError("stub crash")
if mode == "segv":
    os.kill(os.getpid(), signal.SIGSEGV)
if mode == "self_term":
    os.kill(os.getpid(), signal.SIGTERM)
if mode == "teardown":
    import atexit
    def boom():
        raise RuntimeError("teardown")
    atexit.register(boom)
    write(); print("VERDICT: KILL", flush=True); sys.exit(1)
if mode == "ok":
    write(); sys.exit(0)
if mode == "nojson":
    sys.exit(0)
if mode == "env":
    print("ENV-KEYS " + " ".join(sorted(os.environ)), flush=True)
    write(); print("VERDICT: PASS"); sys.exit(0)
if mode == "sleep":
    time.sleep(30); write(); print("VERDICT: PASS"); sys.exit(0)
raise SystemExit(f"unknown mode {mode}")
'''


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=repo, check=True,
                   capture_output=True, text=True)


@pytest.fixture()
def repo(tmp_path: Path) -> Path:
    """A frozen throwaway repository with stub instruments and pinned inputs."""
    r = tmp_path / "repo"
    for d in ("scripts/arenas", "scripts/benchmarks", ".venv/bin", "src",
              "docs", "configs", "tests", RT, "results/diagnostics"):
        (r / d).mkdir(parents=True, exist_ok=True)
    shutil.copy(WRAPPER, r / W)
    for p in INSTRUMENTS:
        (r / "scripts" / f"{p}.py").write_text(STUB)
    shim = r / ".venv/bin/python"
    shim.write_text(f'#!/bin/sh\nexec "{sys.executable}" "$@"\n')
    shim.chmod(0o755)
    (r / RT / "graph.npz").write_text("graph")
    (r / CAPTURE).write_text("capture")
    pins = subprocess.run(["shasum", "-a", "256", f"{RT}/graph.npz", CAPTURE],
                          cwd=r, check=True, capture_output=True, text=True).stdout
    (r / "scripts/arenas/run_amended_once.inputs.sha256").write_text(pins)
    (r / ".gitignore").write_text("results/\n.venv/\ndata/\nstub_mode.txt\n")
    for f, text in (("WORKLOG.md", "log"), ("docs/x.md", "doc"),
                    ("configs/c.yaml", "c"), ("tests/t.py", "t"),
                    ("src/s.py", "s")):
        (r / f).write_text(text)
    _git(r, "init", "-q")
    _git(r, "config", "user.email", "t@example.invalid")
    _git(r, "config", "user.name", "t")
    _git(r, "add", "-A")
    _git(r, "commit", "-qm", "freeze")
    _git(r, "tag", "compass-map-freeze-20261121")
    return r


def _env() -> dict:
    """An explicit environment for the wrapper. The suite's own process can
    carry variables an earlier test left behind: tests/test_random_baseline.py
    runs scripts/evaluate_random_baseline.py in-process, which sets a 64-bit
    PYTHONHASHSEED, and no new Python interpreter starts with that value."""
    path = os.environ.get("PATH", "") + ":/usr/sbin:/sbin:/usr/bin:/bin"
    return {"PATH": path, "HOME": os.environ.get("HOME", "/tmp")}


def run(repo: Path, *args: str, mode: str = "pass", extra_env=None):
    (repo / "stub_mode.txt").write_text(mode)
    env = _env()
    env.update(extra_env or {})
    try:
        p = subprocess.run(["bash", W, *args], cwd=repo, env=env,
                           capture_output=True, text=True, timeout=120)
    finally:
        (repo / "stub_mode.txt").unlink(missing_ok=True)
    out = p.stdout + p.stderr
    print(out)  # shown by pytest when a test fails
    return p.returncode, out


def record(repo: Path, name: str) -> str:
    return (repo / OUT / name).read_text()


def consoles(repo: Path) -> list:
    return sorted((repo / OUT).glob("*.console.txt")) if (repo / OUT).exists() else []


# --- the eleven commands, verbatim -----------------------------------------

def test_a_script_outside_the_eleven_is_refused(repo):
    code, out = run(repo, "scripts/arenas/other_script.py")
    assert code == 92 and "not one of the eleven" in out


@pytest.mark.parametrize("args", [
    ("scripts/benchmarks/fc2_eb_ring.py", "--smoke"),
    ("scripts/benchmarks/cx_ring.py", "--points", "2.0:0.3"),
    ("scripts/cx_scratchpad_premise.py", "--trials", "3"),
    ("scripts/arenas/cx_biswas_killtest.py", "--settle-map"),
    ("scripts/arenas/cx_biswas_killtest.py", "--ring-map", "registered"),
    ("scripts/arenas/cx_heading_killtest.py", "--config", "x.yaml"),
])
def test_protocol_changing_arguments_are_refused_and_use_nothing_up(repo, args):
    code, out = run(repo, *args)
    assert code == 93 and "take no arguments" in out
    assert consoles(repo) == []
    assert "REFUSED (exit 93)" in (repo / OUT / "launch.log").read_text()


# --- against the freeze, with pinned inputs ------------------------------------

def test_a_changed_tracked_file_is_refused_but_a_worklog_change_is_not(repo):
    (repo / "docs/x.md").write_text("changed")
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py")[0] == 96
    _git(repo, "checkout", "-q", "docs/x.md")
    (repo / "WORKLOG.md").write_text("run 1 hashes")
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py")
    assert code == 0 and "CLASSIFICATION: finished" in out


def test_an_untracked_file_under_scripts_is_refused(repo):
    (repo / "scripts/new.py").write_text("x")
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py")[0] == 96


def test_a_changed_input_is_refused_before_any_record(repo):
    (repo / CAPTURE).write_text("tampered")
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py")
    assert code == 85 and "differs from its pinned SHA-256" in out
    assert consoles(repo) == []


# --- the Stage A gate ----------------------------------------------------------

def test_the_dynamics_instruments_need_a_stage_a_pass(repo):
    assert run(repo, "scripts/arenas/cx_heading_killtest.py")[0] == 89
    assert run(repo, "scripts/arenas/cx_topology_killtest.py", mode="kill")[0] == 1
    assert run(repo, "scripts/arenas/cx_class3_killtest.py")[0] == 89


def test_a_stage_a_pass_opens_the_gate(repo):
    assert run(repo, "scripts/arenas/cx_topology_killtest.py")[0] == 0
    code, out = run(repo, "scripts/arenas/cx_seeding_killtest.py")
    assert code == 0 and "CLASSIFICATION: finished" in out


# --- once, keyed on the instrument -----------------------------------------------

def test_a_finished_instrument_cannot_run_again_by_any_route(repo):
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="kill")[0] == 1
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py")[0] == 98
    code, out = run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")
    assert code == 99 and "classified 'finished'" in out


def test_one_rerun_after_a_crash_then_no_more(repo):
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="traceback")[0] == 1
    assert "failed to finish -- not an outcome" in record(repo, "cx_biswas_killtest.console.txt")
    code, out = run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py",
                    mode="traceback")
    assert code == 1 and "failed to finish a second time" in out
    moved = repo / OUT / "cx_biswas_killtest.first_attempt" / "cx_biswas_killtest.amended_map.log"
    assert moved.exists()
    assert run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")[0] == 91


def test_a_native_crash_earns_its_rerun(repo):
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="segv")
    assert code == 139 and "failed to finish -- not an outcome" in out
    code, out = run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")
    assert code == 0 and "CLASSIFICATION: finished" in out


def test_a_verdict_followed_by_a_teardown_traceback_is_an_outcome(repo):
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="teardown")
    assert code == 1 and "CLASSIFICATION: finished" in out
    assert "Traceback" in record(repo, "cx_biswas_killtest.console.txt")
    assert run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")[0] == 99


def test_a_prerequisite_exit_is_set_aside_and_uses_nothing_up(repo):
    code, out = run(repo, "scripts/arenas/cx_biswas_context_nulls.py", mode="prereq")
    assert code == 3 and "prerequisite exit" in out
    assert not (repo / OUT / "cx_biswas_context_nulls.console.txt").exists()
    assert list((repo / OUT).glob("cx_biswas_context_nulls.prerequisite_exit.*"))
    assert run(repo, "scripts/arenas/cx_biswas_context_nulls.py", mode="ok")[0] == 0


def test_a_rerun_must_be_the_same_command(repo):
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="traceback")[0] == 1
    rec = repo / OUT / "cx_biswas_killtest.console.txt"
    rec.write_text(rec.read_text().replace(
        "# command: PYTHONPATH=src .venv/bin/python -B scripts/arenas/cx_biswas_killtest.py",
        "# command: something else"))
    code, out = run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")
    assert code == 99 and "was not this command" in out


def test_the_settle_map_and_the_main_mode_are_separate_slots(repo):
    assert run(repo, "scripts/cx_scratchpad_premise.py", "--settle-map",
               mode="traceback")[0] == 1
    code, out = run(repo, "--rerun", "scripts/cx_scratchpad_premise.py", mode="ok")
    assert code == 99 and "no first attempt of cx_scratchpad_premise" in out
    assert run(repo, "--rerun", "scripts/cx_scratchpad_premise.py",
               "--settle-map", mode="ok")[0] == 0


# --- instruments with no verdict line ---------------------------------------------

def test_a_no_verdict_instrument_finishes_only_with_its_json(repo):
    code, out = run(repo, "scripts/benchmarks/fc2_eb_ring.py", mode="nojson")
    assert code == 0 and "failed to finish -- not an outcome" in out
    code, out = run(repo, "--rerun", "scripts/benchmarks/fc2_eb_ring.py", mode="ok")
    assert code == 0 and "CLASSIFICATION: finished" in out


# --- the instrument stopped by a signal; the environment ------------------------------

def test_an_instrument_stopped_by_term_is_abandoned_not_crashed(repo):
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="self_term")
    assert code == 143 and "abandoned after partial output" in out
    code, out = run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")
    assert code == 99 and "classified 'abandoned'" in out


def test_the_instrument_sees_only_the_explicit_environment(repo):
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="env",
                    extra_env={"LEAKED_FOR_TEST": "1"})
    assert code == 0
    keys = [ln for ln in record(repo, "cx_biswas_killtest.console.txt").splitlines()
            if ln.startswith("ENV-KEYS ")][0].split()[1:]
    assert "LEAKED_FOR_TEST" not in keys
    assert {"PATH", "HOME", "PYTHONPATH", "PYTHONDONTWRITEBYTECODE"} <= set(keys)


# --- prerequisites before the record; one run at a time; interrupts -------------------

def test_a_missing_interpreter_is_refused_before_any_record(repo):
    (repo / ".venv/bin/python").write_text("#!/bin/sh\nexit 1\n")
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py")
    assert code == 88 and "nothing recorded" in out
    assert consoles(repo) == []


def test_a_stale_lock_is_reported_not_overridden(repo):
    lock = repo / OUT / ".run.lock"
    lock.mkdir(parents=True)
    (lock / "pid").write_text("999999")
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py")
    assert code == 86 and "stale lock" in out
    assert consoles(repo) == []


def test_an_interrupt_is_abandonment_and_a_second_launch_waits(repo):
    (repo / "stub_mode.txt").write_text("sleep")
    p = subprocess.Popen(["bash", W, "scripts/arenas/cx_topology_killtest.py"],
                         cwd=repo, env=_env(), stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, text=True)
    rec = repo / OUT / "cx_topology_killtest.console.txt"
    deadline = time.time() + 30
    while time.time() < deadline:
        if rec.exists() and "real: bandedness" in rec.read_text():
            break
        time.sleep(0.2)
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py")
    assert code == 86 and "in progress" in out
    p.send_signal(signal.SIGTERM)
    p.communicate(timeout=60)
    text = rec.read_text()
    assert "# WRAPPER INTERRUPTED by SIGTERM" in text
    assert "CLASSIFICATION: abandoned after partial output" in text
    assert not (repo / OUT / ".run.lock").exists()
    code, out = run(repo, "--rerun", "scripts/arenas/cx_topology_killtest.py")
    assert code == 99 and "classified 'abandoned'" in out


# --- round 5: the re-run is the next launch; the ordered tests; the trailer -------------

def test_a_failure_to_finish_holds_every_other_first_attempt_until_its_rerun(repo):
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="traceback")[0] == 1
    for args in (("scripts/arenas/cx_biswas_context_nulls.py",),
                 ("scripts/arenas/cx_topology_killtest.py",),
                 ("scripts/cx_scratchpad_premise.py", "--settle-map")):
        code, out = run(repo, *args, mode="ok")
        assert code == 90 and "cx_biswas_killtest failed to finish and has not been re-run" in out
    assert [c.name for c in consoles(repo)] == ["cx_biswas_killtest.console.txt"]
    assert "REFUSED (exit 90)" in (repo / OUT / "launch.log").read_text()
    assert run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")[0] == 0
    assert run(repo, "scripts/arenas/cx_biswas_context_nulls.py", mode="ok")[0] == 0


def test_a_second_failure_an_abandonment_or_a_prerequisite_exit_does_not_hold_it(repo):
    assert run(repo, "scripts/arenas/cx_topology_killtest.py", mode="traceback")[0] == 1
    assert run(repo, "--rerun", "scripts/arenas/cx_topology_killtest.py",
               mode="traceback")[0] == 1
    assert run(repo, "scripts/arenas/cx_topology_nulls2.py", mode="ok")[0] == 0
    assert run(repo, "scripts/benchmarks/cx_ring.py", mode="self_term")[0] == 143
    assert run(repo, "scripts/benchmarks/fc2_eb_ring.py", mode="ok")[0] == 0
    assert run(repo, "scripts/cx_scratchpad_premise.py", mode="prereq")[0] == 3
    assert run(repo, "scripts/cx_scratchpad_premise.py", "--settle-map", mode="ok")[0] == 0


FIRST_CMD = "# command: PYTHONPATH=src .venv/bin/python -B scripts/arenas/cx_biswas_killtest.py"
TB = ["Traceback (most recent call last):", "RuntimeError: stub crash"]
INTR = "# WRAPPER INTERRUPTED by SIGTERM (the instrument was stopped)"
END = "# ---- end of output ----"
PRE = "BLOCKED -- the kill test cannot run here. Missing:"


@pytest.mark.parametrize("body, cls", [
    (TB, "abandoned"),
    (["Traceback (most recent call last):", "KeyboardInterrupt", END,
      "# exit status: 130"], "abandoned"),
    (TB + [INTR, END, "# exit status: 1"], "abandoned"),
    ([PRE, INTR, END, "# exit status: 3"], "abandoned"),
    (["# WATCHDOG KILL at resident 9100000 KB"], "failed"),
    ([PRE, "# RESOURCE STOP: system memory free 4% is below 5%", END,
      "# exit status: 3"], "failed"),
])
def test_the_order_decides_a_record_that_fits_two_classes(repo, body, cls):
    rec = repo / OUT / "cx_biswas_killtest.console.txt"
    rec.parent.mkdir(parents=True, exist_ok=True)
    rec.write_text("\n".join(["# instrument: cx_biswas_killtest", "# attempt: first",
                              FIRST_CMD, "# ---- output ----", *body]) + "\n")
    code, out = run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")
    if cls == "failed":
        assert code == 0 and "# attempt: rerun" in out
    else:
        assert code == 99 and f"classified '{cls}'" in out


def test_the_json_line_is_written_before_the_exit_status(repo):
    code, out = run(repo, "scripts/benchmarks/fc2_eb_ring.py", mode="ok")
    assert code == 0 and "CLASSIFICATION: finished" in out
    lines = record(repo, "fc2_eb_ring.console.txt").splitlines()
    json_at = [i for i, ln in enumerate(lines) if ln.startswith("# JSON written: ")]
    exit_at = [i for i, ln in enumerate(lines) if ln == "# exit status: 0"]
    assert len(json_at) == 1 and len(exit_at) == 1 and json_at[0] < exit_at[0]


def test_a_freeze_check_that_git_cannot_make_refuses_the_run(repo):
    (repo / ".git" / "index").write_text("x")
    code, out = run(repo, "scripts/arenas/cx_biswas_killtest.py")
    assert code == 96 and "cannot be checked against the freeze" in out
    assert consoles(repo) == []


def test_the_record_names_the_interpreter_and_its_packages(repo):
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py")[0] == 0
    line = [ln for ln in record(repo, "cx_biswas_killtest.console.txt").splitlines()
            if ln.startswith("# interpreter: ")][0]
    for name in ("Python", "numpy", "scipy", "pandas", "pyarrow", "PyYAML"):
        assert f" {name} " in line


# --- round 6: a prerequisite exit left by a dead wrapper is set aside at the next launch ----

def test_a_prerequisite_exit_a_dead_wrapper_left_is_set_aside_at_the_next_launch(repo):
    out = repo / OUT
    out.mkdir(parents=True, exist_ok=True)
    pre = ["# ---- output ----", "BLOCKED -- the kill test cannot run here. Missing:",
           "# ---- end of output ----", "# exit status: 3"]
    (out / "cx_topology_killtest.console.txt").write_text(
        "\n".join(["# instrument: cx_topology_killtest", "# attempt: first", *pre]) + "\n")
    assert run(repo, "scripts/arenas/cx_topology_killtest.py")[0] == 0
    assert "VERDICT: PASS" in record(repo, "cx_topology_killtest.console.txt")
    assert list(out.glob("cx_topology_killtest.prerequisite_exit.*"))
    assert "SET ASIDE cx_topology_killtest.console.txt" in (out / "launch.log").read_text()
    # A re-run's prerequisite exit left in place: the re-run is still owed and the next launch.
    assert run(repo, "scripts/arenas/cx_biswas_killtest.py", mode="traceback")[0] == 1
    (out / "cx_biswas_killtest.rerun.console.txt").write_text(
        "\n".join(["# instrument: cx_biswas_killtest", "# attempt: rerun", *pre]) + "\n")
    assert run(repo, "scripts/arenas/cx_biswas_context_nulls.py", mode="ok")[0] == 90
    assert run(repo, "--rerun", "scripts/arenas/cx_biswas_killtest.py")[0] == 0
