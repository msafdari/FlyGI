# Task 10 due diligence — 2026-10-23 (before the joint freeze)

A 7-agent sweep, one agent per menu item, run against the repo at
0b8d44b before any registration text existed. Verdicts and the
measured facts the registrations rest on. Full agent outputs are
session artifacts; everything decision-relevant is restated here or
in killtest_design.md.

## Verdicts

| Item | Verdict | One line |
| --- | --- | --- |
| 1 Reservoir ARC control | ready-to-register | A LAUNCH of existing machinery: the validated edge-of-chaos bundle (rho 0.9924, half-life 3 actions) is format-identical to null runtimes; both ARC runners parse today in-cloud; comparators already measured. |
| 2 Class-3 T4/T5 | ready-to-register | First direct real-vs-rewire comparison on the DS statistic at ANY fidelity; no published spiking motion detector exists to serve as a Pisokas-style gate (absence finding) — an engine-capacity gate stands in. |
| 3 Fitted per-type CX (Biswas) | needs-fetch | Paper/supplement/params exist nowhere in the container; cloud egress denies every serving host (MEASURED proxy 403 for biorxiv/par.nsf/neurips/europepmc). Pre-commitments frozen now; bars that depend on their published realization freeze after the user fetches. |
| 4 FB structural probe | ready-to-register | FB columnar naming RESOLVED IN-CLOUD from the raw release annotation table (annotation-only contact; the weights pair table deliberately NOT fetched, decision statistics stay outcome-blind). |
| 5 Naturalistic statistics | ready-to-register | T4/T5 translating natural scenes with phase-scrambled 2x2 at class 2.5; the plume/AL-MB branch is NOT the cheap one — surveyed-and-deferred. |
| 6 FlyBench mechanisms | ready-to-register | Two hypotheses (SFA; terminal-aware placement) sharing Task-3 machinery. SFA is one state per neuron, pinned b 2.0 mV / tau_a 200 ms. Terminal is NOT 3D-position-based — FlyBench ships the MaleCNS terminal table (2.4 MB, MIT, in-container; ID alignment vs official annotations MEASURED 99.98%). |
| 7 Second null family | ready-to-register | nulls.py's NullKind literal already declares weight_shuffle and sign_shuffle (never implemented — the recorded controls.md gap); registered as a REFINEMENT decomposing the Stage-A PASS, never a reopening. |

## Measured facts established by the sweep (cited by the registrations)

- Reservoir bundle: data/processed/male-cns-v1.0/literal-rate-signed/
  reservoirs/edge_of_chaos/seed-20260922, built by `flygi graph
  reservoirs` (cli `_build_reservoirs`), validation manifest
  results/manifests/positive_control_regime_20260922.json: rho 0.9924,
  memory half-life 3 actions (real 1), retention after 12 silent
  actions 0.07686 vs real 0.00019 vs matched_random 3.1e-7, operating
  point K=4 / leak 0.3 / gain 0.9. Both runners
  (scripts/evaluate_connectome.py, scripts/evaluate_state_graph.py)
  parse under the current venv; tests/test_reservoirs.py +
  test_null_invariants.py 26/26 in-cloud. League trap: league.py
  refuses cross-regime comparisons — the condition must register in
  regime gain0.9-dead.
- Comparators on disk (MEASURED, LEAGUE/EXPERIMENTS): eff-real-signed
  0.0648 (75 rows, 25 games x seeds 0-2 x 500 actions),
  eff-null-degree-preserving 0.0079, eff-no-graph-bypass 0.0008,
  random-500 0.097568. The sg tie seat is score-inert (CONFIRMED 4
  ways, H-CONSEQUENCE-COUPLING) — a tie-seat control certifies
  nothing; the Track A graph seat is the only informative seat.
- T4/T5 gate absence finding: Shiu 2024 never tested vision (the
  repo's own verified finding, lif_whole_brain.md); the scratchpad lit
  XMLs are all CX papers; higher-fidelity published T4/T5 models are
  graded/conductance (flyvis; Gruntman; Borst 2025); the one spiking
  adjacency (FAFB orientation maps) is recorded in-repo as
  parameters-not-verifiable. There is NO published spiking motion
  detector with pinned parameters to reproduce.
- fc2/fc25 protocol constants carried: patch 2,701 nodes / 507 driven
  / 498 scored T4-T5 / 169 columns; Maisak band = pooled median DSI
  >= 0.30, >= 3 distinct preferred directions each for T4 and T5,
  defined-DSI fraction >= 0.5; class-2.5 measured DSI 0.3216
  (uniform-tau twin 0.3365); trained params with provenance at
  docs/fidelity2/flyvis_trained_params.json.
- FB composition (MEASURED in-cloud from
  body-annotations-male-cns-v1.0-minconf-0.5.feather, 211,577 rows,
  etag 50a7718770c57220f160ba4f431ab89e; annotation-only download, no
  weights contact): PFNa 58, PFNd 40, PFNm_a 21, PFNm_b 26, PFNp_a 64,
  PFNp_b 136, PFNp_c 40, PFNp_d 28, PFNp_e 23, PFNv 20 (labelled-PFN
  column coverage 163/165 = 98.8%), hDelta 189 (A..M:
  12/19/20/8/8/8/8/8/17/31/31/11/8; coverage 98.9%), vDelta 430
  (100%), FC 274 (100%), PFL1 14 / PFL2 12 / PFL3 24 (100%), noduli
  4/2/2/4/2/2.
- Biswas/Duan-Fiete: not in /home/user/johnpi/ (Pisokas only), not in
  the scratchpad lit/ (13 eLife XMLs) or repos/ (Kim2017,
  ModelCX_code-data, Shiu, Turner-Evans EMpaper,
  BiologicalRingAttractor-Code), no GitHub code repo found; all
  serving hosts proxy-denied from the cloud. Fetch list is in
  killtest_design.md §3.
- FlyBench mechanisms (from the in-container flybench 0.2.1 clone):
  SFA = adaptive_lif.py, one adaptation state (a += b on spike,
  tau_a decay, subtracted from drive), their best open-division row
  b 2.0 mV / tau_a 200 ms (flywire783: hard 0.512->0.647, graded
  0.644->0.754, spec +0.200->+0.311, core untouched). Terminal =
  terminal.py + terminal_lif.py, synapse classified by their theta
  convention, shipped table data/terminal/malecns_terminal.csv.gz
  (3,782,429 terminal synapses = 4.2%, matching their FINDINGS M1b);
  ID alignment vs official annotations MEASURED 99.98% (76,457 post
  neurons carry terminal synapses). Our uniform baseline (Task 3,
  MEASURED): core 1.000 / hard 0.6044 / graded 0.7113 / specificity
  +0.282 on the local unpinned MaleCNS build (AF-7), 176,422 neurons.
- nulls.py: NullKind already declares "weight_shuffle" and
  "sign_shuffle" (nulls.py:35); only degree_preserving_rewire is
  implemented; docs/controls.md lists both as "Not implemented" (the
  pre-release audit's recorded gap).

## Deferred by this diligence (recorded, not dropped)

- Conductance-based graded T4/T5 tier (Gruntman/Groschner parameter
  set not pinned in-container) — the rung above item 2, declined the
  way AC-8 declined Duan-Fiete fitting; reopening it needs its own
  registration.
- AL/MB plume-statistics branch of item 5 (no small public corpus
  identified; AL local neurons absent from the compiled inventory).
- A combined SFA+terminal arm (FlyBench never measured it; reported
  non-decisionally if both singles pass).
- ARC-scope application of the second null family (item 7 closes the
  controls.md rows by existence + validation + Stage-A application;
  ARC application would need its own registration).
