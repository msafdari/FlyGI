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
- [ ] History audit before flipping visibility: run GitHub secret scanning
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

- [ ] LICENSE: relicense to MIT-0 before the repo goes public
  (REOPENED 2026-10-02: arcprize's overview makes CC0/MIT-0 an
  eligibility condition — register AP-4, confirmed after a one-day
  detour through the Kaggle-Rules-only reading). Prepared commit lands
  on the user's go. The Kaggle CC-BY 4.0 winner grant is separate and
  binds only on winning.
- [ ] Kaggle forum post on the day the repo goes public (Rules §3.6.b,
  register AP-12): repo link in the Paper Track and ARC-AGI-3 discussion
  forums.
- [ ] THIRD_PARTY_NOTICES.md: present; re-read once before release to
  confirm every vendored/embedded third-party piece is listed with a
  compatible license.
- [ ] MaleCNS data terms (register AP-6): the repo tracks NO connectome
  arrays (ignore rules held), only manifests/hashes — good. The compiled
  arrays live in the private Kaggle dataset
  megusalexandrus/flygi-malecns-runtime. Before pointing the public at
  that dataset (or making it public), confirm male-cns:v1.0 redistribution
  terms (neuPrint datasets are typically CC-BY 4.0 — verify at
  neuprint.janelia.org / the MaleCNS paper's data availability) and that
  data/manifests + docs/data_provenance.md carry the required attribution.

## Repository hygiene

- [x] .fly-or-fake-work/ (foreign workspace) is untracked and will not be
  published. MEASURED: git status --ignored.
- [x] No large artifacts in history per the operating directive (raw
  downloads, compiled arrays, caches all ignored; 2026-09-28 compaction
  note confirms results stayed local).
- [ ] Branch state: this program's work lives on
  claude/admiring-goldberg-wtqkbg. Merge to main (or open and merge a PR)
  before going public so the default branch shows the current record.
- [ ] README refresh: the current README leads with milestone-era framing.
  A public-audience rewrite is prepared as part of the Task-1 package
  (leads with the question, the verdict matrix, the paper link, how to
  reproduce, claim boundaries). Apply before visibility change.
- [x] CITATION.cff (2026-10-02): author = Mustafa Safdari (alias
  msafdari; the name every commit is already authored under; no email
  added), repository-code link, and the MaleCNS paper as a reference
  (DOI from README). Validated: cffconvert "valid according to schema
  version 1.2.0". GitHub renders it as a "Cite this repository" button.
  Zenodo DOI stays optional: after the repo is public, enable the repo at
  zenodo.org -> GitHub, then cut a GitHub release; Zenodo mints a DOI.
- [ ] Optional: enable GitHub Issues template pointing hypothesis
  discussions at EXPERIMENTS.yaml semantics (nice-to-have, not blocking).
- [ ] Record reconciliation found by the 2026-09-30 fact-check pass:
  LEAGUE.md (generated snapshot, 2026-09-26) still lists H-EFFERENCE as
  "open" while EXPERIMENTS.yaml and WORKLOG say null. Regenerate LEAGUE.md
  on the local machine (`scripts/league.py`; needs the result bundles this
  container lacks) before release. The registry's duplicate-status-key
  landmine in H-MB-CLASS2-ASSOCIATION was fixed in-container 2026-09-30
  (run the full pytest suite locally to confirm nothing depended on it).

## Final order of operations

1. Complete Step-0 rule verification (runbook) -> update ASSUMPTIONS.md.
2. License decision -> commit.
3. README refresh + CITATION decision -> commit.
4. Merge branch to main.
5. Secret-scan pass on the final state.
6. Flip visibility to Public.
7. Only then: Kaggle notebook upload, Writeup, posts.
