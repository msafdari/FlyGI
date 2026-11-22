# Task 9 kill tests — FROZEN 2026-10-10 (H-CX-RING-TOPOLOGY, H-CX-HEADING-LATENT)

Both stages registered BEFORE any instrument code, in one commit, so
Stage B cannot be tuned on Stage A's outcome. Stage A's instrument
builds now; Stage B's instrument builds ONLY after a Stage-A PASS is
reported (on a KILL, Task 9 ends with no dynamics built). Changes
after first data contact require a recorded instrument-bug finding
and a full re-run, both in the WORKLOG.

Shared substrate: the induced CX subcircuit used by the validated
prior work — select_nodes patterns ("EPG", "PEN_a*", "PEN_b*",
"Delta7", "PEG"), recorded composition 148 neurons = 46 EPG +
20 PEN_a(PEN1) + 22 PEN_b(PEN2) + 42 Delta7 + 18 PEG (asserted;
BLOCKED on mismatch). Wedge coordinates: the cx_ring/cx_scratchpad
mapping VERBATIM (AC-1) — instance regex `_([LR])(\d)`, index =
(wedge-1)*2 + (0 if L else 1), angle = index * 22.5 deg; ESTABLISHED
annotation, ASSUMED interleaving, correct up to a fixed rotation
(which no metric below depends on).

---

## Stage A — H-CX-RING-TOPOLOGY (structural; instrument now)

### Premise

The real MaleCNS CX wiring carries ring-compass topology: (i) the
EPG<->EPG excitatory coupling through PEN is circularly BANDED under
the anatomical wedge ordering, and (ii) left- and right-hemisphere
PEN_a implement OPPOSITE-signed rotational offsets (the shifter the
measured gain-1.5 steering used) — at levels degree-preserving
rewires of the same subcircuit cannot produce.

### Frozen metrics (mechanical; operationalizations are AC-4)

- Two-hop coupling: W2 = relu(W[EPG<-PEN]) @ relu(W[PEN<-EPG]),
  computed per PEN population (PEN_a left, PEN_a right, PEN_b left,
  PEN_b right, and all-PEN combined). relu keeps the excitatory loop
  the compass motif uses; wedge-labelled cells only.
- Wedge aggregation: couplings averaged into a 16x16 matrix over
  (post-wedge, pre-wedge) index pairs (mean over cell pairs, zero
  where no pair exists).
- BANDEDNESS B = (sum of the 16x16 all-PEN matrix within circular
  index distance <= 2) / (total sum). Undefined (BLOCKED) if the
  total is 0.
- OFFSET per PEN population p: profile(d) = mean over wedge pairs
  with circular difference d in {-7..8} of the 16x16 matrix for p;
  offset(p) = argmax_d profile(d). Valid only if offset is in
  {-7..-1, 1..7} (0 and the antipode 8 fail; the antipode's sign is
  ambiguous).
- NULLS: 200 degree-preserving rewires of the full 148-neuron
  subcircuit matrix (flygi.connectome.nulls.degree_preserving_rewire,
  seeds 4242+0..199), identical pipeline. Empirical one-sided
  p-values: p = (1 + #{null >= real}) / 201.

### Frozen bars — PASS iff ALL hold, else KILL

1. **Banded**: B_real exceeds the nulls at p < 0.05.
2. **Shifter**: PEN_a-left and PEN_a-right offsets are both valid and
   OPPOSITE in sign, AND the separation statistic
   S = |offset_L - offset_R| (computed only when signs oppose, else
   S = 0) exceeds the nulls at p < 0.05. PEN_b offsets are reported
   as context and decide nothing.
3. Context, non-decisional: a blind spectral ordering of the all-PEN
   wedge matrix (Laplacian eigenmap angle) and its circular
   correlation with the anatomical ordering — reported as a check on
   AC-1, decides nothing.

KILL closes Task 9 with no dynamics built: a structural null on the
fly's most structured circuit is a recorded result, and Stage B's
premise depends on structure existing.

### BLOCKED (exit 3) — not a verdict

- Population counts deviate from 46/20/22/42/18.
- Wedge labels parse for < 90% of EPG or < 90% of PEN_a cells.
- All-PEN two-hop total weight is 0 (degenerate).
- Compiled runtime absent (cloud).

---

## Stage B — H-CX-HEADING-LATENT (dynamical; instrument ONLY after a Stage-A PASS)

### Premise

At the measured working regime — class-1 rate dynamics on the FULL
compiled graph at gain 1.5, leak 0.3 (the regime where opposite-sign
steering is MEASURED; H-CX-CALIBRATION showed it cannot be
transplanted, so the whole network runs there) — the real CX wiring
maintains a heading CONTINUUM and tracks integrated self-motion:
a latent heading estimate, where the gain-2.0 record found only two
fixed points, and where CX-rewired controls fail.

### Frozen protocol

- Machinery: cx_ring.py's loading, wedge drive, PVA read, and
  rotation-rate conventions verbatim; PRE_SEED/SEED/DARK windows and
  the four preregistered seed angles (22.5 calibration;
  112.5/202.5/292.5 held out) carried from the class-1/fc2_eb_ring
  protocol.
- Arms: REAL / CX-REWIRED x3 — the degree-preserving rewire applied
  to the CX-internal 148x148 block ONLY, rest of the graph intact
  (AC-5: isolates the CX wiring's contribution), seeds 4242+0..2,
  identical drives.
- Tracking sequences: 3 preregistered piecewise-constant PEN
  left/right command sequences (frozen in the instrument at build
  time from seed 20261010, each 6 segments x 200 steps, commands in
  {L, R, off}), decoded against the command integral using the
  rotation-rate calibration measured on the CALIBRATION angle only.

### Frozen bars — PASS iff ALL hold, else KILL

1. **Continuum**: after 2 s darkness, PVA within 45 deg of its own
   seed with circular variance <= 0.6 on ALL THREE held-out angles
   (directly kills the two-fixed-point failure mode).
2. **Tracking**: mean final absolute heading error over the 3
   sequences <= 45 deg (decoded vs integrated command).
3. **Wiring-specific**: REAL beats every CX-rewired arm on mean
   final tracking error, and no rewired arm passes bars 1+2.

Engineered ceiling, context only: a 2-variable Python integrator is
exact by construction; beating it is NOT required (motion-arm
precedent).

### BLOCKED (exit 3) — not a verdict

- The calibration angle fails its own persistence precheck
  (retention >= 0.05, circvar <= 0.6 at 1.5/0.3) — the measured
  regime did not reproduce (AC-2), so the premise never gets tested.
- Runtime absent; numerical instability (NaN/overflow) in > 20% of
  runs in any arm.

---

## Expected-tier statement (both stages)

No benchmark score is predicted; the 0-for-16 score-adjacent counter
does not apply to these registrations and is not incremented by them.
As circuit-function predictions: Stage A's priors FAVOR pass (the
measured gain-2.0 persistence separation; Hulse 2021 structure) — the
program's first such registration; Stage B's priors are mixed
(steering measured at 1.5; position storage never measured there;
class-2 fully delocalized; AC-2 transplant risk). The measurements
publish either way, and a Stage-B KILL on the wiring-favored circuit
is the strongest available confirmation of SYNTHESIS.md's
transformation-not-permutation reading.

## AMENDMENT 2026-10-10, BEFORE ANY DATA CONTACT (Stage A shifter statistic)

The synthetic-ring validation AC-4 mandates (run in-cloud, before the
instrument ever saw real data) measured the frozen shifter statistic
and one candidate replacement to be inadequate, and the decision
statistic was replaced BEFORE any data contact. The full sequence,
all MEASURED on the synthetic +/-1 compass with degree-preserving
nulls through the real rewire machinery:

1. FROZEN ORIGINAL, S = |argmax_L - argmax_R|: anti-informative --
   real S 2.0 vs null argmax pairs up to 14.0; empirical p 0.459
   (60 nulls). The statistic rewards randomness.
2. CANDIDATE, mass-weighted mean offsets |mu_L - mu_R| with opposite
   signs: still weak -- rewired graphs' sparse spiky profiles give a
   heavy null tail (null max 5.4, p 0.230 on the perfect compass).
3. ADOPTED: the MIRROR-PEAK statistic. Per side, q(d) = positive
   profile mass at circular difference d (d in -7..7, antipode
   excluded), normalized to sum 1;
   S = max over d in 1..7 of max(q_L(d)*q_R(-d), q_L(-d)*q_R(d)) --
   chirality-free, and nonzero only when the two hemispheres
   concentrate coupling at OPPOSITE offsets, which is what a shifter
   is. MEASURED on the synthetic gate: real 1.0000 vs null max 0.107
   (95th pct 0.065, median 0.025), empirical p 0.0099 with 100 nulls.

Bar 2 is therefore: mirror-peak S beats the nulls at p < 0.05. The
argmax offsets and per-side mass-weighted mean offsets remain
REPORTED as context. Everything else stands as frozen; the synthetic
compass passes the amended bar and a rewired synthetic kills it, both
asserted by unit test before any data contact.

## Stage-B close note (2026-10-11; frozen text above untouched)

Stage B BLOCKED at the AC-2 precheck (2026-10-10, exit 3, no verdict):
retention 0.0000 / circvar 0.661 at the calibration angle,
reproducing the class-1 cx_ring grid's own wedge-write measurement of
this regime (0.0003 / 0.713, angle_pass false; every gain-1.5 leak
row likewise). H-CX-HEADING-LATENT is closed "null" -- unvalidatable
at class-1 under this protocol, untested rather than refuted: the
premise's two required properties were only ever measured in disjoint
regime x protocol combinations (persistence at gain 2.0 wedge-write,
later shown fixed-point; opposite-signed steering at gain 1.5 under
VISUAL-ARC seeding; no persistence at gain 1.5 wedge-write). The
registration's reliance on the regime sweep's persistence number was
a due-diligence miss against cx_ring.py's own "sign pattern, not
numerically" caveat, recorded in the WORKLOG close. Reopening paths
(each needs an explicit go and its own registration): class-3 CX
fidelity, or a registered visual-arc-seeding reconciliation at 1.5
with pre-stated pass rules.

---

## Instrument-bug finding and amendment (dated 2026-11-21; AFTER data contact; frozen text above untouched)

Filed under this registration's own rule ("Changes after first data
contact require a recorded instrument-bug finding and a full re-run").
The full record is `docs/arenas/compass_map_amendment_20261121.md`.
This section is the pointer and the part that concerns Stage A and
Stage B. Its decisions were made by the local session that wrote it,
under the owner's one-line go.

FINDING. The shared wedge coordinates above (AC-1: index =
(wedge-1)*2 + (0 if L else 1)) ran both bridge halves round the ring in
the same direction. In the fly they run in opposite directions, so the
registered map reflected the left half-ring relative to the right one
(L_k was placed beside R_k and lies between R_(9-k) and R_(10-k)). The
frozen sentence "correct up to a fixed rotation (which no metric below
depends on)" does not cover a reflected half-ring: bandedness, the
mirror-peak, and in Stage B the written cells and every decoded angle
all depend on it. MEASURED 2026-11-21
(`scripts/arenas/compass_map_check.py`): 18.7% of the direct EPG to EPG
synapse count between different ring positions joins ring neighbours
under the registered map (10,000 random maps: mean 13.3%, p 0.197)
against 81.7% under the amended map (p 0.0001, the floor).

THE CONTEXT CHECK HAD SEEN IT. Bar 3 above, the blind spectral
ordering, recorded 46.6 degrees on 2026-10-10 and was closed as
"neither confirmed nor refuted". A perfect synthetic ring read through
the registered map gives 45.0 to 50.6 degrees on that check, depending
on the eigensolver (49.2 with numpy on this machine), and 0 to 11.25
through the right map (now a unit test). The check had no threshold.
It still has none: its value under a corrected order had already been
agent-reported (6.6 degrees) before this section was written, so a
band set now would not be a test. It is reported as it comes.

AMENDMENT. Only the EPG label to position map changes: right half as
registered (R_k at 22.5 + 45(k-1) degrees), left half reflected (L_k
at 360 - 45(k-1) degrees), which agrees with the four wedge angles
printed in Hulse et al. 2021 Fig. 16B (L1 0, L7 90, L5 180, L3 270) and
with the order of all sixteen read from that figure (amendment section
3). It lives in `src/flygi/compass_map.py` and
both instruments take `--ring-map` (`amended` by default, `registered`
to reproduce the 2026-10-10 runs). Every metric, null, seed, bar,
protocol, angle and BLOCKED floor of both stages stands as frozen. The
nominal seed angles keep their numbers and their centre cells.

DISCLOSED. Stage A's bar 1 under a corrected order is effectively
known: a fact-check subagent reported bandedness 0.8505 against a maximum
of 0.334 over the 200 registered rewires, and a blind residual of 6.6
degrees, before this section was written (not reproduced by me). The amended Stage A run is therefore CONFIRMATORY
for bar 1. Bar 2, the mirror-peak, has not been computed by anyone
under the amended map. Before the freeze both instruments were run
with `--ring-map registered` and reproduced their 2026-10-10 records.

RE-RUN, full, once each. Stage A first. Stage B only on a Stage-A PASS
under the amended map, which is the gate this registration already
states. Stage B is re-run as THIS registration under the rule quoted
above. It is not one of the reopening paths named in the close note,
which each need a new registration. The frozen text says a Stage-A
KILL "closes Task 9 with no dynamics built". That is honoured for
every Task 9 dynamics instrument: the reopening probe and the class-3
test are also re-run only on a Stage-A PASS.

PRE-STATED, so the next outcome cannot be reshaped. Stage A PASS:
H-CX-RING-TOPOLOGY stays supported with the amended numbers, and its
statement is narrowed to what the bars measure, with k the number of
rewires at or above the real mirror-peak and both p values as printed:
"the PEN-mediated EPG to EPG coupling is banded on the ring (p = ...
against 200 degree-preserving rewires), and the left and right PEN_a
halves put more joint mass on a mirrored pair of offsets than at least
191 of those 200 rewires (k of 200 at or above it; p = ...)". Bar 2
passes at p < 0.05, which allows up to 9 rewires at or above the real
value. Exactly one of the three clauses of amendment section 8, C6
follows, chosen by the signs of the PEN_a_L and PEN_a_R mean offsets and
quoting both: "and the two halves lean in opposite directions", with
C6's caveat that the amended tile geometry alone could produce that
(inferred), only if the signs are opposite. Apart from that caveat it
never says "shifter" and never claims a PEN shift: bar 2 is large for
symmetric profiles too (a property of the 2026-10-10 statistic, not of
this amendment), and under the amended coordinates an offset of one
position can arise from tile geometry alone (inferred; amendment section
8, C6). MEASURED on the 2026-10-10
record: bar 2 passed with both PEN_a mean offsets of the same sign.
Stage A KILL on either bar: refuted, the 2026-10-10 PASS is recorded as
measured on a mislabelled ring, Task 9 closes, and H-CX-HEADING-LATENT
is recorded not-pursued. Stage A BLOCKED: no verdict, status
`invalidated`, the gate stays closed. Stage B BLOCKED at the precheck or
the rate guard: status stays null as recorded on 2026-10-10, now on the
amended map, and AC-2's invalidation stands there too. Stage B PASS:
supported, and its "heading CONTINUUM" wording is kept only if all three
held-out writes of the real arm follow (amendment section 8, C7: each
settles within 22.5 degrees of its own seed angle, 22.5 included, and no
other surviving write of the real arm settles within 11.25 degrees of its
settled angle, 11.25 included, the 22.5 precheck write included at the
angle printed on its precheck line; each distance rounded to 0.01
degrees); otherwise the statement is
narrowed to "meets the registered position clause" with the final angles
quoted. Stage B KILL: refuted. What counts as finished, failed or
abandoned is amendment section 7, decision 7, by its ordered tests: a crash, a watchdog kill or a resource stop earns one fresh re-run,
unchanged, made as the next launch, and a second failure, or a failure
not re-run, is "no verdict"; stopping a run before the instrument
finishes, by TERM to the wrapper or to the instrument, by INT to the wrapper or
by HUP (INT and HUP only where the launch does not ignore them), is
recorded as abandoned, with no re-run (a SIGKILL or any other signal that
kills the instrument is a failure to finish; the instrument itself ignores
INT and QUIT, and HUP under the prescribed launch). After two failures to finish or an
abandoned attempt, the printed output is quoted beside the status as
section 10 of the amendment defines; a BLOCKED outcome or a closed gate is
recorded with its BLOCKED line or the gate's reason. The
registered-map outcomes stay in the record as history. No benchmark
score is predicted and the 0-for-16 counter is not touched.
