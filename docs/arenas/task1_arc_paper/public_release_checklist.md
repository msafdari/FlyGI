# Public-release checklist for the FlyGI repository

Prepared 2026-09-30 for the Paper Track submission (the posts and the
writeup's Project Link point here, so the repo goes public first).
Status boxes to be ticked as completed; audit findings recorded inline.

## Secrets & credentials (audited 2026-09-30, tracked files)

- [x] No credential files tracked (no .env, kaggle.json, token files) —
  MEASURED: `git ls-files` grep clean.
- [x] Token-shaped string scan over tracked files: only benign hits —
  `"api_key": null` fields inside Kaggle scorecard JSON manifests
  (results/manifests/gateway_*.json) and a test placeholder
  `ARC_API_KEY=test-key-123` in scripts/build_notebook.py. Neither is a
  secret. MEASURED.
- [x] History audit before flipping visibility: run GitHub secret scanning
  on the repo (Settings -> Security, or ask this session to trigger the
  API scan) — tracked-file audit does not cover old blobs. The WORKLOG
  records "credentials were not logged" discipline throughout, so the
  expectation is clean; verify anyway.
- [x] WORKLOG carries no secrets (spot-checked; the operating directive
  forbade recording them from day one).

## Personal information

- [x] Local macOS paths scrubbed 2026-10-02 (user's call: best practice).
  The 47 archived probe/solver scripts in docs/fap_extension_20260928/
  now resolve the repo root from __file__ (portable; logic unchanged);
  JSON records and results/manifests/* carry repo-relative paths (hashes
  unchanged; no code reads these files); one test's hardcoded fixture
  path — which silently SKIPPED its audit off the original machine — now
  resolves repo-relative like its siblings; the handoff doc's paths are
  generic. History still holds the old paths (no rewrite: the username
  equals the public commit author name already on every commit).
- [x] No email addresses or phone numbers in the tracked tree (re-swept
  2026-10-02: one personal address found in due_diligence_20260930.md,
  committed after the first sweep, now removed). Note: git commit
  metadata carries the author email by design; GitHub shows it on
  commits. To hide it on FUTURE commits, use GitHub's noreply address
  (Settings -> Emails -> Keep my email addresses private).

## Licensing

- [x] LICENSE: relicensed to MIT No Attribution (MIT-0) on the user's
  explicit go, 2026-10-02 ("go MIT-0"; register AP-4 — arcprize's
  CC0/MIT-0 eligibility condition). LICENSE text replaced (same
  copyright line), README and CITATION.cff updated (cffconvert-valid);
  THIRD_PARTY_NOTICES untouched — third-party code keeps its own
  licenses, which clear arcprize's Apache-2.0/GPLv3 floor. The Kaggle
  CC-BY 4.0 winner grant is separate and binds only on winning.
- [ ] Kaggle forum post on the day the repo goes public (Rules §3.6.b,
  register AP-12): repo link in the Paper Track and ARC-AGI-3 discussion
  forums. Drafts ready: kaggle_forum_posts.md (fill {{REPO_LINK}}).
- [x] THIRD_PARTY_NOTICES.md: present; re-read once before release to
  confirm every vendored/embedded third-party piece is listed with a
  compatible license.
- [x] MaleCNS data terms VERIFIED (register AP-6, MEASURED 2026-10-01,
  CONFIRMED): MaleCNS v1.0 is CC BY 4.0; data/README.md carries the
  required citation (doi:10.1016/j.cell.2026.08.015) and the
  derivative/non-endorsement disclaimer. The repo tracks NO connectome
  arrays (ignore rules held), only manifests/hashes.
- [ ] Residual before making the Kaggle dataset
  megusalexandrus/flygi-malecns-runtime public: put the same CC BY 4.0
  attribution + citation on the dataset's own description page (it
  auto-publishes with the submission).

## Repository hygiene

- [x] .fly-or-fake-work/ (foreign workspace) is untracked and will not be
  published. MEASURED: git status --ignored.
- [x] No large artifacts in history per the operating directive (raw
  downloads, compiled arrays, caches all ignored; 2026-09-28 compaction
  note confirms results stayed local).
- [x] Branch state: this program's work lives on
  claude/admiring-goldberg-wtqkbg. Merge to main (or open and merge a PR)
  before going public so the default branch shows the current record.
- [x] README refresh: applied in cb99eeb (2026-10-01) — README leads
  with the question, the verdict matrix, the writeup link, reproduction
  steps, and the MIT-0 line. Landing section updated through the
  arena-program close in the 2026-10-08 pre-release audit.
- [x] CITATION.cff (2026-10-02): author = Mustafa Safdari (alias
  msafdari; the name every commit is already authored under; no email
  added), repository-code link, and the MaleCNS paper as a reference
  (DOI from README). Validated: cffconvert "valid according to schema
  version 1.2.0". GitHub renders it as a "Cite this repository" button.
  Zenodo DOI stays optional: after the repo is public, enable the repo at
  zenodo.org -> GitHub, then cut a GitHub release; Zenodo mints a DOI.
- [ ] Optional: enable GitHub Issues template pointing hypothesis
  discussions at EXPERIMENTS.yaml semantics (nice-to-have, not blocking).
- [x] Record reconciliation found by the 2026-09-30 fact-check pass:
  RESOLVED by the 2026-10-02 local regeneration (commit 9255f6d) —
  LEAGUE.md's H-EFFERENCE row now reads "null", matching
  EXPERIMENTS.yaml/WORKLOG. The registry's duplicate-status-key landmine
  in H-MB-CLASS2-ASSOCIATION was fixed in-container 2026-09-30 and the
  full suite has run green since.
- [x] VERIFY THE FLAT DOWNGRADE LANDED (added 2026-10-29, triggered by the
  measured H-ARC-HARNESS-SENSITIVITY FLAT -- the frozen pre-release
  consequence): docs/controls.md (positive-control section carries the
  measured ARC outcome and the weakened reading), docs/experiment.md
  (claim-boundary section carries the harness-sensitivity boundary),
  EXPERIMENTS.yaml eff-row notes (registry readers), LEAGUE.md's generated
  header reading-note (scripts/league.py now emits it -- verify it appears
  after the local regeneration, since condition notes themselves do NOT
  render into LEAGUE.md),
  factsheet.md and writeup.md (the harness-sensitivity bound). The class-1
  ARC null prose must nowhere claim the harness could have registered an
  advantage.
- [x] Regenerate LEAGUE.md AGAIN before release (updated 2026-10-30; the
  2026-10-29 regeneration at c3ec5bd predates the Task-10 closes AND the
  league.py header reading-note). Run
  `uv run python scripts/league.py --write-md LEAGUE.md` ONLY on the
  machine holding results/connectome_agent (in a container without the
  gitignored bundles, regeneration wipes condition rows to
  "missing | 0 | 0.0000" — do not commit a bundle-less regeneration).
  After regenerating, diff and verify: (1) the header carries the
  "Reading note (measured 2026-10, H-ARC-HARNESS-SENSITIVITY, FLAT)"
  paragraph; (2) the hypothesis table matches the registry —
  H-ARC-HARNESS-SENSITIVITY refuted, H-STAGEA-NULL-DECOMPOSITION /
  H-FB-COLUMNAR-TOPOLOGY / H-FLYGI-FLYBENCH-TERMINAL supported,
  H-FLYGI-FLYBENCH-SFA refuted, H-T4T5-CLASS3-DS "null"; (3) the two
  reservoir condition rows are present and complete (75 rows each);
  (4) no condition row newly reads "missing" with 0 rows.

## Final order of operations

1. Complete Step-0 rule verification (runbook) -> update ASSUMPTIONS.md.
2. License decision -> commit.
3. README refresh + CITATION decision -> commit.
4. Merge branch to main.
5. Secret-scan pass on the final state.
6. Flip visibility to Public.
7. Only then: Kaggle notebook upload, Writeup, posts.
