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

- [x] Local macOS paths embed the username (e.g.
  /Users/mustafasafdari/Documents/... in docs/fap_extension_20260928/*
  probe scripts) and CLAUDE_CODE_REFACTOR_HANDOFF.md names msafdari.
  DECISION NEEDED (default: leave as-is — the repo will be publicly
  attributed to you anyway; say the word if you want the paths scrubbed).
- [x] No email addresses or phone numbers found in tracked files.

## Licensing

- [ ] LICENSE: currently MIT. Paper-track prize eligibility reportedly
  requires CC0 or MIT-0 for submitter-authored code (register AP-4;
  verify wording in runbook Step 0). Relicensing is the copyright
  holder's decision; a prepared MIT-0 LICENSE text will be committed on
  your go.
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
- [ ] CITATION.cff: update `authors` (currently "FlyGI contributors") if
  you want your name on citations, and add the Zenodo/DOI step if you
  want one (optional).
- [ ] Optional: enable GitHub Issues template pointing hypothesis
  discussions at EXPERIMENTS.yaml semantics (nice-to-have, not blocking).

## Final order of operations

1. Complete Step-0 rule verification (runbook) -> update ASSUMPTIONS.md.
2. License decision -> commit.
3. README refresh + CITATION decision -> commit.
4. Merge branch to main.
5. Secret-scan pass on the final state.
6. Flip visibility to Public.
7. Only then: Kaggle notebook upload, Writeup, posts.
