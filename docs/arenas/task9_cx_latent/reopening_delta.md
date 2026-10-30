# Task 9 reopening — due diligence, 2026-10-11

User go ("Do them both"): the seeding-protocol reconciliation AND the
class-3 CX build. Both registrations are frozen jointly (one commit,
killtest_design_reopening.md) so neither can be tuned on the other;
the probe runs first because its outcome shapes what class-3 must
answer (a protocol under which class-1 persists would reopen Stage B
at class-1; none would make class-3 the only path).

## New in-repo findings from this due diligence (MEASURED/recovered)

1. **The committed grid record is stronger than the close knew.** The
   verdict program's cx_ring grid was preserved as TRACKED provenance
   (git commit 09a998a, results/manifests/verdict_program_20260930/
   cx_ring.json; later removed from the tree, recoverable from
   history; the live copy is the local results/benchmarks/
   cx_ring.json). Its rows: C1 wedge-write persistence FAILS at every
   measured point — including gain 2.0 (best retention 0.0177/0.0163/
   0.0178 across leaks; gain 1.5: 0.0001-0.0004) — while C2
   opposite-signed steering PASSES at 1.5/0.3 AND 2.0/0.3 (from the
   best-retention angle's settled state, per that benchmark's
   registered amendment). So: steering is measured at two operating
   points; wedge-write persistence is measured dead at ALL of them;
   the ONLY persistence measurement in the record (Sept-25 premise
   run, mass 0.27 sustained 120+ steps, null dead by t=40) used the
   arc-seeded protocol.
2. **The arc protocol is unreproducible from the committed record.**
   The scripts that produced results/cx_ring_premise.json /
   cx_ring_rotation.json / cx_ring_regime_sweep.json never existed in
   git (checked: no cx-named deleted paths in history beyond the
   current files). What survives: the registry prose ("darkness after
   a 90-degree seeded arc", "whole network at gain 1.5 -> ring
   works") and the local JSONs. A load-bearing measurement whose
   protocol cannot be reproduced from the repo is itself a recorded
   lesson (the probe fixes it by freezing a DECLARED protocol set).

## What each reopening tests

- **Probe (H-CX-SEEDING-PROTOCOL):** is Stage B's failure
  protocol-bound rather than regime-bound? A frozen 4-protocol x
  2-operating-point set, every cell reported; pass rules pre-stated.
  Priors, both directions: FOR — steering measured at both chosen
  points; the one arc-seeded run measured strong persistence AND the
  wiring-specific separation. AGAINST — wedge-write persistence
  measured dead at every grid point, twice at 1.5/0.3.
- **Class-3 (H-CX-CLASS3-COMPASS):** does a physiologically richer
  model class — conductance/spiking parameters pinned from the
  published fly ring-attractor models, applied to the REAL MaleCNS CX
  weights — pass the compass gate (localized persistent bump,
  position continuum, opposite steering) where class-1 tanh and
  class-2 Shiu-LIF both failed, and where its CX rewire fails?
  Priors: Kakaria & de Bivort 2017 and Pisokas et al. 2020 show
  fly-TOPOLOGY ring attractors work in spiking models with suitable
  synaptic parameters — but on idealized/by-class weights; whether a
  CONNECTOME-WEIGHTED fly CX sustains a bump is (pending the
  literature sweep's confirmation) unmeasured anywhere. Parameter
  values are pinned from the literature table in this delta's
  companion (filled from the registered research sweep BEFORE the
  instrument exists), never searched to pass; a small declared
  variant grid is reported in full.

## Trivial alternatives (named)

- Probe: P1 (cx_ring's own wedge-write) is the built-in reproduction
  control, measured dead — the probe must beat its OWN baseline cell.
  The rewire arms carry the wiring burden at any passing cell.
- Class-3: the same CX-block rewire, same parameters, same gate; plus
  the synthetic idealized ring (the literature's own object), which
  the instrument must pass IN-CLOUD before data contact — if the
  engine cannot sustain a bump on the ideal ring, there is no
  instrument.

## Tier statement

Neither registration is score-adjacent (the 0-for-16 counter is not
incremented). Both are expected-tier circuit-function predictions
with priors stated above; the probe is explicitly an exploratory
reconciliation with pre-stated pass rules — the frozen protocol set
and full-cell reporting are what keep it from being an
operating-point search tuned to pass.
