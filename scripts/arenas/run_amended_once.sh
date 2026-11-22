#!/bin/bash
# One amended-map run of one compass instrument: once, against the frozen
# registration, watched. Part of the compass map amendment of 2026-11-21
# (docs/arenas/compass_map_amendment_20261121.md, sections 7, 10 and 11).
#
#   scripts/arenas/run_amended_once.sh [--rerun] <script> [--settle-map]
#
# Launch it detached, in a session of its own, and wait for the record's
# trailer. macOS has no setsid(1), and the fork keeps setsid from failing
# when an interactive shell has made the job a process-group leader:
#   nohup perl -MPOSIX -e 'fork and exit; POSIX::setsid() > 0 or die "setsid: $!"; exec @ARGV or die "exec: $!"' \
#     scripts/arenas/run_amended_once.sh scripts/arenas/cx_biswas_killtest.py >/dev/null 2>&1 &
# (POSIX::setsid returns -1 on failure, which Perl counts as true, hence
# the "> 0"), then check results/arenas/amended_runs_20261121/launch.log,
# where every refusal, start and end is written. Stopping a run before the
# instrument finishes, by TERM to this wrapper or to the instrument, by
# INT to this wrapper, or by HUP (INT and HUP only where the launch does
# not ignore them), abandons it; a SIGKILL or any other signal that kills
# the instrument is a failure to finish, because it cannot be told apart
# from a crash. The instrument itself ignores INT and QUIT (bash starts it
# in the background), and HUP as well under nohup. A run must not be tied
# to a terminal, a tool call or a process group that can be signalled.
#
# What it enforces, because the amendment promises it:
#   - THE ELEVEN COMMANDS, VERBATIM. <script> must be one of the eleven
#     instrument commands of section 11, and it takes no argument except
#     --settle-map with scripts/cx_scratchpad_premise.py. Everything else
#     is refused, so no run through this wrapper can change the map, the
#     output path, the grid, the trials or the config.
#   - AGAINST THE FREEZE. The freeze is the git tag
#     compass-map-freeze-20261121. Every tracked file except WORKLOG.md
#     must be identical to the freeze, in the working tree, and there must
#     be no untracked file under src/, scripts/, configs/, tests/ or docs/.
#     If git cannot make either comparison, the run is refused. WORKLOG.md
#     is the one file that changes between runs: each run's hashes are
#     entered there and committed before the next run.
#   - THE STAGE A GATE. cx_heading_killtest, cx_seeding_killtest and
#     cx_class3_killtest are refused unless a Stage A record
#     (cx_topology_killtest, first attempt or re-run) has the line
#     "VERDICT: PASS".
#   - ONE RUN AT A TIME. A lock directory is held for the whole run, so a
#     second launch is refused while one is going. A lock left by a
#     wrapper that was killed is reported and must be removed by hand, and
#     only once the instrument whose process ID it holds has exited: until
#     then that instrument can still be writing to its record.
#   - PINNED INPUTS, PREREQUISITES AND RESOURCES BEFORE THE RECORD. Every
#     file listed in scripts/arenas/run_amended_once.inputs.sha256 (the
#     compiled runtime, the raw MaleCNS pair table from which six of the
#     instruments rebuild every synaptic weight, and the capture file)
#     must match its SHA-256; the compiled runtime (and the capture file,
#     for the two visual instruments) must be present; numpy, scipy,
#     pandas, pyarrow and yaml must import under the instrument's own
#     environment, and their versions are written into the record; and at
#     least 1 GiB of disk and 25% of system memory must be free. All of it
#     is checked before any record exists, so a wrong checkout or a busy
#     machine uses nothing up.
#   - AN EXPLICIT ENVIRONMENT. The instrument runs with only PATH, HOME,
#     PYTHONPATH=src and PYTHONDONTWRITEBYTECODE=1 set (env -i), and the
#     record says so.
#   - ONCE, KEYED ON THE INSTRUMENT. The record is named after the
#     instrument: results/arenas/amended_runs_20261121/<instrument>.console.txt,
#     where <instrument> is the script's stem, or cx_scratchpad_settle_map
#     with --settle-map. A first attempt is refused if that record exists
#     (unless test 3 below calls it a prerequisite exit, which is set aside
#     first) or if the instrument's amended output is already on disk.
#   - FINISHED IS POSITIVE, AND THE TESTS ARE ORDERED. classify() decides
#     an attempt by tests on its record's own lines, in this order, the
#     first that matches deciding:
#       1. FINISHED, an outcome: a line beginning "VERDICT: ", "BLOCKED: "
#          or "BLOCKED ("; or, for the six instruments that print no
#          verdict line, this wrapper's lines "# JSON written: " and
#          "# exit status: 0", which it writes in that order once the
#          instrument has exited. A record without both has not finished,
#          whatever is on disk: an instrument whose wrapper was killed can
#          still exit 0 and write its JSON, but its exit status is then
#          never recorded. Nothing after an attempt has finished, an
#          interrupt included, changes it.
#       2. FAILED TO FINISH: a "# WATCHDOG KILL" or "# RESOURCE STOP" line,
#          whatever else the record shows.
#       3. PREREQUISITE EXIT: a line beginning "BLOCKED -- " and the line
#          "# exit status: 3", with no "# WRAPPER INTERRUPTED" line. The
#          instrument printed its "BLOCKED -- ... cannot run here" line
#          before opening its log and computed nothing, so it is neither an
#          outcome nor a counted attempt: the record is set aside as
#          <instrument>.prerequisite_exit.<UTC time>.console.txt and the
#          slot stays free. The wrapper that ran it sets it aside; if that
#          wrapper died first, the next launch that takes the lock does,
#          before it reads any record for its once-only checks, and says so
#          in launch.log.
#       4. ABANDONED AFTER PARTIAL OUTPUT: a "# WRAPPER INTERRUPTED" line,
#          or no "# exit status: " line, or exit status 129, 130, 131 or
#          143 (the instrument stopped by HUP, INT, QUIT or TERM). It was
#          stopped from outside before it finished, by whoever or whatever:
#          an operator, a shutdown that signals the wrapper, or a crash of
#          the machine, which this wrapper cannot tell apart. It is an
#          attempt, it earns no re-run, and the status written for it
#          quotes what it printed.
#       5. FAILED TO FINISH: anything else, such as a Python traceback, a
#          native crash, or a SIGKILL of the instrument with no marker
#          (exit 137, which cannot be told apart from the system's own
#          memory kill). It earns one re-run.
#   - ONE RE-RUN, ONLY AFTER A FAILURE TO FINISH, AND AS THE NEXT LAUNCH.
#     --rerun runs the same command again, once, into
#     <instrument>.rerun.console.txt, if the first record is a failure to
#     finish and its "# command:" line is this command. The first attempt's
#     outputs are moved, not overwritten, into <instrument>.first_attempt/
#     beside the records. While any instrument's first record is a failure
#     to finish and it has no re-run record, every other first attempt is
#     refused (exit 90), so the re-run is the next launch. Each record is
#     classified by its own instrument's tests, so a record whose wrapper
#     died is covered too. A failure to finish that is never re-run is read
#     as two failures to finish (amendment section 10).
#   - WATCHED. Every 2 s the instrument is killed above 9 GB resident
#     (WATCHDOG KILL, the resource rule), and stopped if free disk falls
#     below 512 MiB or system memory free below 5% (RESOURCE STOP). Each
#     writes its measurement into the record. System memory free is read
#     from kern.memorystatus_level (the figure memory_pressure prints), so
#     the wrapper runs on macOS only; elsewhere it refuses to start.
#   - RECORDED. Everything the instrument prints, the exit status, the
#     peak sampled memory, the hash of every output and the classification
#     go to the record (git-ignored; hashed into the WORKLOG after the run,
#     and copied to results/manifests/compass_amended_20261121/ at the
#     close). A record whose wrapper died has none, part or all of its
#     trailer, and is classified by the same tests, in the same order, once
#     its instrument has exited.
#   - SIGNALS AT THE NEXT CHECK. The wrapper acts on a signal at its next
#     check, within about 2 s. A signal it acts on after the instrument has
#     exited changes nothing, and launch.log records it; a signal that
#     arrives while the trailer is written, or one the wrapper inherited as
#     ignored (HUP under nohup), is neither acted on nor logged.
set -u
FREEZE_TAG=compass-map-freeze-20261121
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
cd "$ROOT" || exit 97
OUT_REL=results/arenas/amended_runs_20261121
OUT=$ROOT/$OUT_REL
LAUNCH_LOG=$OUT/launch.log
LOCK=$OUT/.run.lock
PINS=scripts/arenas/run_amended_once.inputs.sha256
RUNTIME=data/processed/male-cns-v1.0/literal-rate-signed-modulators
CAPTURE=results/diagnostics/recognizer_frames.npz
PY=.venv/bin/python
WATCHDOG_KB=9000000
START_DISK_KB=1048576
START_MEM_PCT=25
STOP_DISK_KB=524288
STOP_MEM_PCT=5
ARGS="$*"

stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
note() { { mkdir -p "$OUT" && echo "$(stamp) $1" >> "$LAUNCH_LOG"; } 2>/dev/null; }
refuse() { echo "REFUSING: $1"; note "REFUSED (exit $2) [$ARGS]: $1"; exit "$2"; }
is_num() { case "${1:-}" in ''|*[!0-9]*) return 1 ;; esac; return 0; }
disk_kb() { df -k "$ROOT" 2>/dev/null | awk 'NR==2 {print $4}'; }
mem_pct() { sysctl -n kern.memorystatus_level 2>/dev/null; }

ATTEMPT=first
if [ "${1:-}" = "--rerun" ]; then ATTEMPT=rerun; shift; fi
[ "$#" -ge 1 ] || refuse "usage: $0 [--rerun] <script> [--settle-map]" 64
SCRIPT=$1; shift

# The eleven commands of section 11, verbatim. VISUAL: whether the
# instrument reads the capture.
VISUAL=no
case "$SCRIPT" in
  scripts/arenas/cx_biswas_killtest.py) STEM=cx_biswas_killtest ;;
  scripts/arenas/cx_topology_killtest.py) STEM=cx_topology_killtest ;;
  scripts/arenas/cx_heading_killtest.py) STEM=cx_heading_killtest ;;
  scripts/arenas/cx_seeding_killtest.py) STEM=cx_seeding_killtest ;;
  scripts/arenas/cx_class3_killtest.py) STEM=cx_class3_killtest ;;
  scripts/arenas/cx_biswas_context_nulls.py) STEM=cx_biswas_context_nulls ;;
  scripts/arenas/cx_topology_nulls2.py) STEM=cx_topology_nulls2 ;;
  scripts/benchmarks/cx_ring.py) STEM=cx_ring; VISUAL=yes ;;
  scripts/benchmarks/fc2_eb_ring.py) STEM=fc2_eb_ring ;;
  scripts/cx_scratchpad_premise.py) STEM=cx_scratchpad_premise; VISUAL=yes ;;
  *) refuse "not one of the eleven amended-run commands of section 11: $SCRIPT" 92 ;;
esac
EXTRA=
if [ "$#" -gt 0 ]; then
  if [ "$STEM" = cx_scratchpad_premise ] && [ "$#" -eq 1 ] && [ "$1" = --settle-map ]; then
    STEM=cx_scratchpad_settle_map; EXTRA=--settle-map
  else
    refuse "the amended runs take no arguments (only --settle-map, with scripts/cx_scratchpad_premise.py): $*" 93
  fi
fi
CMD="PYTHONPATH=src .venv/bin/python -B $SCRIPT"
[ -n "$EXTRA" ] && CMD="$CMD $EXTRA"
case "$STEM" in
  cx_ring|fc2_eb_ring) JSON=results/benchmarks/$STEM.amended_map.json ;;
  cx_scratchpad_premise|cx_scratchpad_settle_map) JSON=results/$STEM.amended_map.json ;;
  *) JSON=results/arenas/$STEM.amended_map.json ;;
esac

FREEZE=$(git rev-parse -q --verify "refs/tags/$FREEZE_TAG^{commit}") \
  || refuse "the freeze tag $FREEZE_TAG does not exist" 94
CHANGED=$(git diff --name-only "$FREEZE" -- . ':(exclude)WORKLOG.md') \
  || refuse "git diff failed, so the tree cannot be checked against the freeze" 96
[ -z "$CHANGED" ] || refuse "tracked files differ from the freeze: $(echo $CHANGED)" 96
UNTRACKED=$(git ls-files --others --exclude-standard -- src scripts configs tests docs) \
  || refuse "git ls-files failed, so the tree cannot be checked against the freeze" 96
[ -z "$UNTRACKED" ] || refuse "untracked files under frozen paths: $(echo $UNTRACKED)" 96

mkdir -p "$OUT"
FIRST="$OUT/$STEM.console.txt"
RERUN="$OUT/$STEM.rerun.console.txt"
exists() { [ -e "$1" ] || [ -L "$1" ]; }
existing_outputs() {
  find results -path "$OUT_REL" -prune -o -type f -name "$STEM.amended_map.*" -print 2>/dev/null
}

case "$STEM" in
  cx_heading_killtest|cx_seeding_killtest|cx_class3_killtest)
    GATE=closed
    for r in "$OUT/cx_topology_killtest.console.txt" "$OUT/cx_topology_killtest.rerun.console.txt"; do
      [ -f "$r" ] && grep -q -x -F 'VERDICT: PASS' "$r" && GATE=open
    done
    [ "$GATE" = open ] || refuse "the Stage A gate is closed: no Stage A record has the line 'VERDICT: PASS'" 89
    ;;
esac

# One run at a time: the lock is held until this wrapper exits.
if ! mkdir "$LOCK" 2>/dev/null; then
  HOLDER=$(cat "$LOCK/pid" 2>/dev/null); CHILD=$(cat "$LOCK/child" 2>/dev/null)
  if { is_num "$HOLDER" && kill -0 "$HOLDER" 2>/dev/null; } \
     || { is_num "$CHILD" && kill -0 "$CHILD" 2>/dev/null; }; then
    refuse "another amended run is in progress (wrapper ${HOLDER:-?}, instrument ${CHILD:-none yet})" 86
  fi
  refuse "a stale lock $LOCK was left by a wrapper that died (wrapper ${HOLDER:-?}, instrument ${CHILD:-none}); check that no run is going, then remove it by hand" 86
fi
echo $$ > "$LOCK/pid"
trap 'rm -rf "$LOCK"' EXIT
trap 'exit 130' INT
trap 'exit 143' TERM
trap 'exit 129' HUP

# Whether an instrument prints a VERDICT line, by its record's stem.
verdict_line_of() {
  case "$1" in
    cx_biswas_context_nulls|cx_topology_nulls2|cx_ring|fc2_eb_ring|cx_scratchpad_premise|cx_scratchpad_settle_map) echo no ;;
    *) echo yes ;;
  esac
}

# classify <record> <stem>: finished | failed | prerequisite_exit | abandoned
# The header's five tests, in their order; the first that matches decides.
classify() {
  if grep -q -E '^(VERDICT: |BLOCKED: |BLOCKED \()' "$1"; then echo finished; return; fi
  if [ "$(verdict_line_of "$2")" = no ] && grep -q -x -F '# exit status: 0' "$1" \
     && grep -q '^# JSON written: ' "$1"; then echo finished; return; fi
  if grep -q -E '^# (WATCHDOG KILL|RESOURCE STOP)' "$1"; then echo failed; return; fi
  if grep -q -x -F '# exit status: 3' "$1" && grep -q '^BLOCKED -- ' "$1" \
     && ! grep -q '^# WRAPPER INTERRUPTED' "$1"; then
    echo prerequisite_exit; return
  fi
  if grep -q '^# WRAPPER INTERRUPTED' "$1" || ! grep -q '^# exit status: ' "$1" \
     || grep -q -E '^# exit status: (129|130|131|143)$' "$1"; then
    echo abandoned; return
  fi
  echo failed
}

# Test 3's record is set aside before the once-only checks read any record, so a wrapper
# that died between writing a prerequisite exit's exit status and setting
# the record aside cannot hold that slot, or stand in for an owed re-run.
# This runs under the lock, so no instrument is running, and it moves only
# records whose exit status a wrapper wrote.
for r in "$OUT"/*.console.txt; do
  [ -f "$r" ] || continue
  case "$r" in *.prerequisite_exit.*) continue ;; esac
  s=$(basename "$r" .console.txt); s=${s%.rerun}
  [ "$(classify "$r" "$s")" = prerequisite_exit ] || continue
  a="$OUT/$s.prerequisite_exit.$(date -u +%Y%m%dT%H%M%SZ).console.txt"
  exists "$a" && refuse "cannot set aside $r: $a exists" 97
  mv "$r" "$a" || refuse "could not set aside $r" 97
  note "SET ASIDE $(basename "$r") as $(basename "$a"): a prerequisite exit whose wrapper died before setting it aside"
done

if [ "$ATTEMPT" = first ]; then
  REC=$FIRST
  exists "$FIRST" && refuse "$STEM already has a first attempt ($FIRST); only a failure to finish earns a re-run, with --rerun" 98
  exists "$RERUN" && refuse "$STEM already has a re-run record ($RERUN)" 98
  EX=$(existing_outputs)
  [ -z "$EX" ] || refuse "amended output already exists: $(echo $EX)" 95
  # The re-run a failure to finish earns is the next launch: no other
  # instrument's first attempt starts while one is owed. Each record is
  # classified with its own stem, so a record whose wrapper died counts too.
  for r in "$OUT"/*.console.txt; do
    [ -f "$r" ] || continue
    case "$r" in *.rerun.console.txt|*.prerequisite_exit.*) continue ;; esac
    s=$(basename "$r" .console.txt)
    exists "$OUT/$s.rerun.console.txt" && continue
    [ "$(classify "$r" "$s")" = failed ] \
      && refuse "$s failed to finish and has not been re-run; its re-run (--rerun) is the next launch, and no other instrument starts first" 90
  done
else
  REC=$RERUN
  [ -f "$FIRST" ] || refuse "no first attempt of $STEM to re-run" 99
  exists "$RERUN" && refuse "$STEM has already been re-run once; a second re-run is not allowed" 91
  grep -q -x -F "# command: $CMD" "$FIRST" || refuse "the first attempt of $STEM was not this command" 99
  C=$(classify "$FIRST" "$STEM")
  [ "$C" = failed ] || refuse "the first attempt of $STEM is classified '$C'; only a failure to finish earns a re-run" 99
fi

[ -f "$PINS" ] || refuse "the pinned input list $PINS is missing" 85
shasum -a 256 -c --status "$PINS" >/dev/null 2>&1 \
  || refuse "an input differs from its pinned SHA-256 in $PINS, nothing recorded: $(shasum -a 256 -c "$PINS" 2>&1 | grep -v ': OK$' | tr '\n' ' ')" 85
[ -d "$RUNTIME" ] || refuse "prerequisite missing, nothing recorded: compiled runtime $RUNTIME" 88
PKGS=$(env -i PATH="$PATH" HOME="${HOME:-/tmp}" PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 \
  "$PY" -B -c 'import sys, numpy, scipy, pandas, pyarrow, yaml; print("Python", sys.version.split()[0], "numpy", numpy.__version__, "scipy", scipy.__version__, "pandas", pandas.__version__, "pyarrow", pyarrow.__version__, "PyYAML", yaml.__version__)' 2>/dev/null) \
  || refuse "prerequisite missing, nothing recorded: $PY with numpy and scipy (and pandas, pyarrow and yaml) under the run's environment" 88
if [ "$VISUAL" = yes ]; then
  [ -f "$CAPTURE" ] || refuse "prerequisite missing, nothing recorded: capture file $CAPTURE" 88
fi
D=$(disk_kb); M=$(mem_pct)
is_num "$D" || refuse "cannot read free disk" 87
is_num "$M" || refuse "cannot read system memory free (kern.memorystatus_level)" 87
[ "$D" -ge "$START_DISK_KB" ] || refuse "resource rule, nothing recorded: free disk ${D} KB is below 1 GiB" 87
[ "$M" -ge "$START_MEM_PCT" ] || refuse "resource rule, nothing recorded: system memory free ${M}% is below ${START_MEM_PCT}%" 87

MOVED=no
if [ "$ATTEMPT" = rerun ]; then
  EX=$(existing_outputs)
  if [ -n "$EX" ]; then
    mkdir -p "$OUT/$STEM.first_attempt"
    for f in $EX; do mv "$f" "$OUT/$STEM.first_attempt/" || refuse "could not move $f" 97; done
    MOVED=yes
  fi
fi

( set -C; : > "$REC" ) 2>/dev/null || refuse "the record $REC appeared while starting" 98
{
  echo "# instrument: $STEM"
  echo "# attempt: $ATTEMPT"
  echo "# started: $(stamp)"
  echo "# freeze: $FREEZE_TAG = $FREEZE"
  echo "# git HEAD: $(git rev-parse HEAD) (tracked files other than WORKLOG.md identical to the freeze)"
  echo "# command: $CMD"
  echo "# environment: env -i, then PATH, HOME, PYTHONPATH=src and PYTHONDONTWRITEBYTECODE=1 only"
  echo "# interpreter: $PKGS (imported under that environment)"
  echo "# inputs: the $(grep -c . "$PINS") files of $PINS match their pinned SHA-256"
  [ "$VISUAL" = yes ] && echo "# input: $CAPTURE sha256 $(shasum -a 256 "$CAPTURE" | cut -d' ' -f1)"
  echo "# resources at start: free disk ${D} KB; system memory free ${M}%"
  [ "$MOVED" = yes ] && echo "# the first attempt's outputs were moved to $STEM.first_attempt/"
  echo "# ---- output ----"
} >> "$REC"
note "STARTED $STEM ($ATTEMPT): $CMD"

if [ -n "$EXTRA" ]; then
  env -i PATH="$PATH" HOME="${HOME:-/tmp}" PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 \
    "$PY" -B "$SCRIPT" "$EXTRA" >> "$REC" 2>&1 &
else
  env -i PATH="$PATH" HOME="${HOME:-/tmp}" PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 \
    "$PY" -B "$SCRIPT" >> "$REC" 2>&1 &
fi
PID=$!
echo "$PID" > "$LOCK/child"
INTERRUPTED=
# An interrupt is recorded only if it stopped a live instrument. Once the
# instrument has exited, bash has reaped it and the kill fails, so a signal
# that arrives before the loop notices the exit changes nothing.
on_signal() {
  kill -TERM "$PID" 2>/dev/null \
    || { note "SIG$1 found the instrument already exited at the wrapper's next check (it arrived up to about 2 s earlier); nothing changed"; return 0; }
  INTERRUPTED=$1
  sleep 2
  kill -KILL "$PID" 2>/dev/null
}
trap 'on_signal INT' INT
trap 'on_signal TERM' TERM
trap 'on_signal HUP' HUP
MAXK=0
STOPPED=
while kill -0 "$PID" 2>/dev/null; do
  R=$(ps -o rss= -p "$PID" 2>/dev/null | tr -d ' ')
  if is_num "$R"; then
    [ "$R" -gt "$MAXK" ] && MAXK=$R
    if [ -z "$STOPPED" ] && [ "$R" -gt "$WATCHDOG_KB" ]; then
      kill -KILL "$PID" 2>/dev/null
      echo "# WATCHDOG KILL at resident ${R} KB" >> "$REC"
      STOPPED=watchdog
    fi
  fi
  if [ -z "$STOPPED" ]; then
    D=$(disk_kb); M=$(mem_pct)
    if is_num "$D" && [ "$D" -lt "$STOP_DISK_KB" ]; then
      kill -KILL "$PID" 2>/dev/null
      echo "# RESOURCE STOP: free disk ${D} KB is below 512 MiB" >> "$REC"
      STOPPED=resource
    elif is_num "$M" && [ "$M" -lt "$STOP_MEM_PCT" ]; then
      kill -KILL "$PID" 2>/dev/null
      echo "# RESOURCE STOP: system memory free ${M}% is below ${STOP_MEM_PCT}%" >> "$REC"
      STOPPED=resource
    fi
  fi
  sleep 2
done
# The instrument has exited: its status is fixed, and the trailer is
# written whatever arrives now.
trap '' INT TERM HUP
wait "$PID"; CODE=$?
# The JSON line goes BEFORE the exit status, with nothing that forks
# between them. A no-verdict instrument has finished only when its record
# has both, so a wrapper killed part-way through this block can leave a
# finished run with no exit status (abandoned), but never one with
# "# exit status: 0" and no JSON line (a failure, which would earn a second
# run of an instrument that had finished). Bash writes each line with its
# own write(2), so it is the order, not one printf, that makes this hold.
{
  [ -n "$INTERRUPTED" ] && echo "# WRAPPER INTERRUPTED by SIG$INTERRUPTED (the instrument was stopped)"
  echo "# ---- end of output ----"
  [ -f "$JSON" ] && echo "# JSON written: $JSON"
  echo "# exit status: $CODE"
  echo "# peak sampled resident memory: ${MAXK} KB"
  for f in $(existing_outputs); do
    echo "# output: $f sha256 $(shasum -a 256 "$f" | cut -d' ' -f1)"
  done
  echo "# finished: $(stamp)"
} >> "$REC"

C=$(classify "$REC" "$STEM")
case "$C" in
  finished)
    echo "# CLASSIFICATION: finished -- an outcome (amendment section 10)" >> "$REC" ;;
  failed)
    if [ "$ATTEMPT" = first ]; then
      echo "# CLASSIFICATION: failed to finish -- not an outcome; its one re-run, with --rerun, is the next launch" >> "$REC"
    else
      echo "# CLASSIFICATION: failed to finish a second time -- no verdict; the status written for it quotes what both attempts printed" >> "$REC"
    fi ;;
  abandoned)
    echo "# CLASSIFICATION: abandoned after partial output -- stopped from outside before it finished; no verdict and no re-run; the status written for it quotes what it printed" >> "$REC" ;;
  prerequisite_exit)
    echo "# CLASSIFICATION: prerequisite exit -- nothing computed; neither an outcome nor a counted attempt, and the slot stays free" >> "$REC"
    ASIDE="$OUT/$STEM.prerequisite_exit.$(date -u +%Y%m%dT%H%M%SZ).console.txt"
    mv "$REC" "$ASIDE" && REC=$ASIDE ;;
esac
note "ENDED $STEM ($ATTEMPT): exit $CODE, $C"
tail -40 "$REC" | cut -c1-400
exit $CODE
