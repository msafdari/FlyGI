# Has the fly reached its limit, and where else could it compete?

Survey date: 2026-09-30. Sources: this repository's durable record (WORKLOG.md,
LEAGUE.md, EXPERIMENTS.yaml — tier MEASURED), plus a two-agent web survey run
this date (tier SOURCED: link-backed but externally unverified except where
noted; direct fetches of arcprize.org and dsec.ifi.uzh.ch were proxy-blocked,
so those details come from search snippets and deadlines must be re-verified
before committing to them). Every fit assessment below is INFERRED or
EXPECTED; this project's base rate on expected-score claims is 0 for 11.

## Part A — the internal ledger (MEASURED, this repository)

What the fly has given, per module, at the deepest fidelity tried:

| Module | Verdict | Key numbers |
| --- | --- | --- |
| Optic-lobe eye map (static retinotopy) | **USEFUL** — the only deployed fly content | real map 2.59x human baseline vs scrambled twin 11.59x; load-bearing twice |
| Mushroom body, one-shot association (class 2 LIF, calibrated) | **NOT USEFUL** (earned) | real 0.600 < rewired 0.800; perceptron 0.917 |
| T4/T5 ARC motion decoding (class 2.5, trained flyvis params, DS validated DSI 0.32) | **NOT USEFUL** (earned) | real 0.3875; uniform-tau 0.3917; rewire 0.4306; engineered 1.0000 |
| CX ring (EPG/PEN/Delta7/PEG) | UNVALIDATABLE at classes 1 and 2 (210 LIF configs, all alive rows delocalized) + no honest ARC heading mapping | min circvar 0.853 vs 0.6 band |
| LC/LPLC object code | class-1 sign-inverted (rho −0.20..−0.31 vs +0.5 band); recognizer premise-killed; untested at class 2 | held-out dead-vs-live ≤ chance |
| KC sparse coding (class 2) | biology VALIDATED (first dynamical pass), ARC use refuted downstream | held-out fraction 0.0741 in [0.03, 0.15]; APL load-bearing |
| FlyHash state keys + MBON novelty | refuted for ARC state fragmentation | — |
| Efference copy, MBON→DAN metaplasticity, SEZ/VNC | null / null / no native mapping | gate difference crushed ~250–500x, plateaus |

Score track: three consecutive 0.15 hidden-set submissions; game-specific
grammars transfer zero, measured three times. Local 28.74 is thirteen
engineered Python archetypes with neuronal dynamics OFF. The search layer
failed its preregistered gateway gate (28.4596 vs 28.7423) and did not ship.
The worklog's standing conclusion (2026-09-30): the score track's non-LLM
levers are exhausted by measurement; what remains score-side is the
LLM-hybrid scope decision (the user's) or banking 0.15.

## Part B — what the outside world did while we worked (SOURCED)

The context changed materially in September 2026, and it changes what is worth
doing next.

1. **"Fly connectome plays a game" is now a commodity.** After the MaleCNS
   v1.0 release, a viral wave of ~50+ projects wired the whole graph to Doom,
   Mario 64, Beat Saber, Minecraft, chess, trading, etc. (curated lists:
   github.com/cobanov/awesome-fly, github.com/townie/awesome-fruit-fly; press:
   Hackaday 2026-09-14, PC Gamer, Slashdot). The public critique (P. Mineault,
   neuroai.science, "Are flies playing Beat Saber?") is exactly this
   repository's first principle: most demos are a frozen graph plus a
   hand-written readout. A game demo, as such, is worth nothing now.
2. **Nobody is on ARC.** Targeted searches found zero connectome-based or
   fly-circuit attempts on any ARC version. FlyGI appears to be the only one.
3. **Nobody has the innate-wiring claim.** No control-backed demonstration of
   *untrained* innate wiring doing useful external task work was found —
   every near-neighbor trains something (FlyGM arXiv:2602.17997 and FLYNN
   arXiv:2607.00025 train on the connectome scaffold; flyvis trains
   physiology params; "train-your-fly" trains per-synapse gains; hobbyist
   demos train readouts). Three independent lines cut *against* the claim:
   - "Digital sphinx" (Tuthill lab, bioRxiv 2026.03.20.713233): a worm
     connectome + trained mapping produces realistic fly walking —
     behavioral fidelity without biological fidelity.
   - fly-hero (github.com/bsgelman/fly-hero): dopamine-RPE learning needs
     real wiring (99.3% vs 21.9% shuffled), but a *trained* readout hits
     100% on a random network.
   - Connectome reservoir benchmarks (arXiv:2609.30508 and others):
     randomized nulls often match or beat real wiring.
   - Closest pure-form study: the larval frozen rate operator
     (arXiv:2606.17745) bounds the wiring-specific increment over
     degree/weight-matched nulls at ≤ ~37%, on dynamics, not tasks.
   Consequence: both a positive AND a cleanly measured negative at task
   level with degree-preserving nulls are novel. This repository already
   holds two of the negatives (MB, T4/T5) at publication grade.
4. **FlyBench exists** (github.com/brandoncho369/flybench; verified by local
   clone and read this date — real, active, solo author, 50 commits
   2026-09-11..23, Zenodo DOI, no paper yet). 36 pre-registered,
   citation-anchored *reflex* tasks on FlyWire v783 AND MaleCNS v1.0,
   shuffled-wiring controls on every row, uniform-parameter LIF reference,
   fitting-on-tasks forbidden by governance. Same epistemics as this
   repository, different target: reproducing fly biology, not external task
   competence. Its measured findings bear directly on our module premises:
   plain-LIF antennal lobe is a broadcast (one odor drives 84–91% of PNs);
   through a real flyvis eye the loom never reaches LPLC2/LC4/GF while a
   flash fires the GF; the EPG bump task sits in its expected-fail tier; and
   two no-free-parameter mechanisms move its scores — terminal-aware synapse
   placement (0.6–4% off-soma; MaleCNS core tier 0.57 → 0.90) and
   spike-frequency adaptation (best open-division row).
5. **The one unclaimed composition:** every whole-brain agent treats the
   connectome as one undifferentiated graph; all module-level work builds
   motifs by hand. A pipeline of actual connectome-*extracted* executable
   modules (eye map → T4/T5 → LC → MB → CX), which is what this repository
   is, was not found anywhere else.

## Part C — answer 1: is there anything else extractable from the fly?

**On ARC-AGI-3: the limit is reached, and it is a measured limit, not a
shrug.** The four-requirements program closed with a per-module answer; the
two modules that validated at depth (KC sparse code, T4/T5 DS) then lost to
their own degree-preserving nulls on the ARC task; the remaining modules
either fail their biology benchmarks at two fidelity classes or have no
honest ARC quantity to read. The score track's non-LLM levers are exhausted
by preregistered gates. Nothing in the external survey suggests a missed
fly-side lever *for ARC*: the computations ARC pays for (program induction,
goal inference, credit assignment over symbols) have no fly module, and the
fly's real modules (motion, looming, heading, odor association) have no ARC
quantity that maps onto them without the plumbing doing the work.

Fly-side levers that remain open at all, stated with their tier:

- **Class-3 fidelity ingredients, now with externally measured candidates**
  (SOURCED → would need in-repo measurement): FlyBench found terminal-aware
  synapse placement and spike-frequency adaptation move whole-brain LIF
  scores with no free parameters. These are precisely "physiological
  ingredients outside the swept space" — the registered condition under
  which our ring verdict could reopen, and a candidate cure for the
  dense-or-silent MB/AL transition. EXPECTED value for ARC score: none
  (the validated modules already lost to nulls downstream); value is
  scientific (module verdicts at better fidelity).
- **LC at class 2** — untested; the class-1 sign inversion may be a
  fidelity artifact. Same caveat: recognition's ARC seat was premise-killed
  independently.
- Everything else on the inventory is closed with a measured verdict.

So: further extraction on ARC is science, not score. The extractable value
that remains is (a) the write-up of the record, which the external survey
shows is unique, and (b) pointing the already-built modules at arenas where
they have native mappings — Part D.

## Part D — answer 2: other arenas, ranked

Ranked by native fit (no engineered intelligence needed), enterability,
novelty (per Part B), and whether a *measured* number results even on a
loss. Trivial alternative and cheapest kill test named per the operating
directive.

1. **ARC Prize 2026 Paper Track** (Kaggle; pool $450K; deadline SOURCED as
   2026-11-09 — re-verify). Requires a ≤1,500-word paper documenting a real
   ARC-AGI-2/3 submission, scored on Accuracy/Universality/Progress/Theory/
   Completeness/Novelty. We own three scored submissions, the only
   connectome ARC attempt found anywhere, two earned control-backed
   fly-negatives, one validated-biology result, and a preregistration
   discipline the digital-sphinx / fly-hero literature now shows is the
   entire scientific content. Near-zero marginal build; Accuracy scores low
   and everything else scores high. Trivial alternative: not writing it —
   the record then exists only as a private worklog. Kill test: re-verify
   deadline + rubric on the Kaggle page (minutes).
2. **DSEC-Flow** (standing event-camera optical-flow leaderboard, open
   submission; SOTA ~0.66 px EPE). The most native module fit found: events
   are the luminance-change input T4/T5 evolved for, the compiled eye map
   supplies retinotopy, and no fly/connectome entry exists. Honesty
   constraint from our own record: frozen-count T4/T5 has DSI 0.042 —
   an *innate untrained* entry would be measuring noise; a class-2.5 entry
   (trained flyvis physiology, zero DSEC-trained parameters) is the
   defensible claim, stated as connectome-constrained + physiology-fitted,
   not innate. FlyBench's flyvis→LIF hand-off failure is a measured warning
   about composing stages. Trivial alternatives: event-count argmax /
   plane-fitting flow. Kill test: one DSEC training sequence, T4/T5 vs both
   trivial baselines, before any dense-flow plumbing exists.
3. **FlyBench itself** (standing, submission = a config/simulator PR).
   Direct engagement: run its 36 tasks with our class-2 engine and
   Litwin-Kumar-calibrated MB (its own AL/MB finding is that plain LIF has
   no sparse code — our threshold-calibrated pass on held-out odors is a
   candidate open-division row); test its two mechanisms in our ring sweep.
   Cheap, community-visible, and the closest independent instrument to our
   question. Trivial alternative: their own reference configs. Kill test:
   run `flybench run -c toy` locally, then one MaleCNS task overlapping our
   subcircuits.
4. **NeuroBench algorithm track** (standing; metrics are synaptic ops,
   sparsity, footprint, accuracy). The only benchmark family whose scoring
   natively rewards a sparse innate spiking circuit; no connectome entry
   exists. Event-vision tasks overlap with target 2. Kill test: score one
   existing module on one NeuroBench task offline before any harness work.
5. **Brain-Score** (standing, open submission). Oddball, cheapest of all:
   score the compiled fly visual system as a primate ventral-stream model.
   Whatever the number, no connectome model is on the board. Static images
   suit the eye map + early filters.
6. **Olfaction: UCI gas-sensor drift corpus (standing) / DREAM Olfaction 3
   (watch).** The one modality where the fly is the acknowledged gold
   standard and where AL→KC association is native. Encoder risk (16 MOX
   channels → ORN classes) is exactly where the intelligence could leak;
   declared-assumption + scrambled-encoder control mandatory. FlyBench's
   PN-broadcast finding says plain LIF won't sparse-code — our calibrated
   MB is the differentiator or it fails the same way (either is a result).
7. **MLPerf Tiny anomaly detection + energy** (next round ~early 2027;
   working-group membership needed). The "X% of SOTA at 1e-6 of the energy"
   headline format fits the MB novelty circuit; moderate embedded
   engineering, none of it intelligence.
8. **Community venues, not benchmarks:** Telluride 2027 (apply ~Feb 2027) and
   CVPR 2027 event-vision / VAND 5.0 windows (Dec 2026–Feb 2027
   announcements). Animal-AI is philosophically aligned but its natural
   module (ring attractor) is the one that doesn't hold position.

**Not worth doing, per the survey:** another game demo (commoditized
Sept 2026); drone/robotics competitions (the stack is engineered scaffold by
construction); LLM-agent leaderboards (BALROG, PokeAgent — not enterable by
a circuit); ARC-AGI-2 score track (no native mapping).

## Claim-boundary summary

MEASURED: everything in Part A. SOURCED: everything in Parts B and D about
external projects, deadlines, and leaderboards (FlyBench additionally
verified by local clone and read). INFERRED: the fit assessments and the
"limit reached on ARC" synthesis (bridge: the tested fidelity classes and
module inventory are exhaustive for ARC-relevant computation; a class-3
reversal on a module that then also beat its null on ARC would break it).
EXPECTED: any suggestion that an entry above produces a competitive score —
base rate 0/11.
