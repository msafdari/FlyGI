# Task 10 runbook — the science menu (user-executed, local)

Registrations: killtest_design.md (frozen 2026-10-23, one commit,
before any instrument code). Run order matters only for item 1:
**run the reservoir control FIRST, before the 2026-11-01 release**,
because its FLAT outcome changes release prose. Everything else can
run in any order, any time. Every instrument BLOCKS (exit 3) rather
than guessing when something it needs is missing. Paste back each
JSON (all are gitignored) plus the printed lines and the branch tip.

## 0. Once per machine

```bash
cd <FlyGI repo root>
git pull
PYTHONPATH=src python -m pytest tests/test_stagea_nulls2.py -q   # 9 passed
```

## 1. H-ARC-HARNESS-SENSITIVITY — reservoir positive control (BEFORE the release)

No new instrument: this launches machinery you already have. The
bundle was built 2026-09-22; if `data/processed/male-cns-v1.0/
literal-rate-signed/reservoirs/edge_of_chaos/seed-20260922` is
missing, rebuild with `uv run flygi graph reservoirs` (~2 min).

```bash
uv run python scripts/evaluate_connectome.py \
  --config configs/literal_rate_signed.yaml \
  --runtime-dir data/processed/male-cns-v1.0/literal-rate-signed/reservoirs/edge_of_chaos/seed-20260922 \
  --condition reservoir-positive-control \
  --seeds 0 1 2 --games all --action-budget 500
# context arm (the control's dumb twin):
uv run python scripts/evaluate_connectome.py \
  --config configs/literal_rate_signed.yaml \
  --runtime-dir data/processed/male-cns-v1.0/literal-rate-signed/reservoirs/matched_random/seed-20260922 \
  --condition reservoir-matched-random \
  --seeds 0 1 2 --games all --action-budget 500
uv run python scripts/league.py --write-md LEAGUE.md
```

Cost: the real graph ran ~0.148 s/action; 75 rows x 500 actions is
roughly a long afternoon per arm (A-RES-3: untimed assumption — if it
is much slower, say so and we re-plan). Both conditions are already
registered in EXPERIMENTS.yaml (regime gain0.9-dead for the league's
cross-regime rule; the note records the reservoir is dynamically
ALIVE there). Report: the two new LEAGUE.md rows and their CIs vs
eff-real-signed and eff-null-degree-preserving. The frozen readings
(CERTIFIED / DETECTS-BUT-HURTS / FLAT) are in killtest_design.md §1 —
on FLAT, the release prose edits listed there happen BEFORE 11-01.

## 2. H-STAGEA-NULL-DECOMPOSITION — second null family on Stage A

```bash
PYTHONPATH=src python -m pytest tests/test_stagea_nulls2.py -q   # 9 passed
python scripts/arenas/cx_topology_nulls2.py       # the one command
```

Cost: Stage A ran 30.6 s at 200 rewires; the shuffles are cheaper
generators on the same 148-neuron subcircuit — expect ~1-3 min for
all three families (600 nulls total). Exit 0 = readings complete
(this instrument has no KILL: refinement, never a reopening). Report
results/arenas/cx_topology_nulls2.json — the decomposition readings
per family.

## 3. H-CX-BISWAS-FITTED — fetch first (cloud cannot reach the hosts)

Fetch these three locally (do NOT commit the PDFs; we extract a small
reviewed provenance file of the parameter tables afterwards):

1. bioRxiv 10.1101/2024.11.01.621596 — full PDF + supplementary
   material (check for a published 2026 version; alternate:
   par.nsf.gov/servlets/purl/10609135).
2. bioRxiv 10.64898/2026.05.18.725766 (the 2026 follow-up — the
   MaleCNS realizations may live here).
3. Duan, Dong & Fiete — bioRxiv 10.1101/2025.05.26.655406 + NeurIPS
   2025 poster 115017 page (for the necessity claim and any code
   link).

Then either paste the MaleCNS parameter tables (or the derivation
recipe) into the session, or drop the files somewhere local and tell
me the paths — the numeric completion of the registration lands as a
dated addendum, and only then does the instrument get built.

## 4-7. Remaining instruments

Sections appended when each instrument lands (FB structural probe,
class-3 T4/T5, naturalistic statistics, FlyBench SFA/terminal). The
naturalistic-statistics run additionally needs a small natural-image
corpus fetched locally (van Hateren subset; the instrument's BLOCKED
message names exactly what and where).
