# FlyGI Experiment 000 biological specification

**Protocol version:** `flygi-exp000-v1-draft`

**Status:** pre-implementation; equations and inference frozen, four blind gates open

**Created:** 2026-09-23 PDT
**Integration gate:** develop only on `codex/experiment-000`; merge after the
FlyARC closure commit is reconciled and compatibility goldens pass

## 0. Objective and claim boundary

Experiment 000 asks whether a reduced, whole-bilateral mushroom-body circuit
extracted reproducibly from MaleCNS v1.0 can perform elementary online
associative learning when:

1. synthetic cues enter only through measured ALPN→KC edges;
2. KC sparsity is produced by measured APL feedback rather than a silent top-k;
3. value is read through fixed opponent MBON populations;
4. reinforcement gates only existing, compartment-designated KC→MBON edges;
5. no trainable encoder, decoder, or bypass can solve the task; and
6. the native topology is compared with conservative matched nulls.

Two claims are intentionally separate:

- **H000-MECH:** the declared circuit plus reinforcement-gated local plasticity
  learns better than the three nonredundant primary controls: frozen gains,
  within-phase reward-time shuffle, and graph-off. Lesions and DAN-off remain
  required diagnostic kill/equivalence tests.
- **H000-TOPO:** native weighted PN→KC plus KC→all-MBON partner wiring performs
  better than the preregistered distribution of degree-exact topology nulls.

Passing H000-MECH while tying the topology null supports a generic
mushroom-body-like mechanism, not superiority of the exact fly wiring.
Because KC↔APL is held fixed in the primary null, no outcome supports a claim
about superiority of the entire native mushroom-body topology.

This experiment does **not** claim:

- a biophysically complete fly-brain simulation;
- that the synthetic cues are odors;
- native reward-prediction-error computation;
- delayed-credit learning in the core test;
- relevance to personalization before Experiment 001 independently passes.

## 1. Evidence labels

Every model statement must carry exactly one primary label:

- `MEASURED_CONNECTOME`: computed directly from pinned MaleCNS artifacts;
- `LITERATURE_ESTABLISHED`: supported biological organization/function;
- `MODEL_ASSUMPTION`: a necessary mathematical choice not specified by anatomy;
- `ENGINEERING_CHOICE`: a reproducibility or implementation convention;
- `HYPOTHESIS`: an empirical claim tested by this experiment.

References support biological interpretation. They do not turn an assumed
dynamical parameter into a connectome measurement.

### 1.1 Implementation-critical sources

| ID | Primary/official source | What it supports here |
| --- | --- | --- |
| R1 | [Berg et al., Cell (2026)](https://doi.org/10.1016/j.cell.2026.08.015) | MaleCNS scope and publication context; its paper count is 166,691, distinct from the 166,700 rows measured in the pinned annotation file |
| R3 | [Official MaleCNS v1.0 downloads](https://male-cns.janelia.org/download/) | source filenames, release identity, schemas, and licensing—not FlyGI's locally observed hashes |
| R10 | [Modi, Shuai & Turner (2020)](https://doi.org/10.1146/annurev-neuro-080317-0621333) | review-level support for sparse KC coding, MB compartmental learning, and MBON output organization |
| R11 | [Bennett, Philippides & Nowotny (2021)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8105414/) | a separate computational RPE model and literature oracle; it does not specify FlyGI's gain update |
| R14 | [Dasgupta, Stevens & Navlakha (2017)](https://doi.org/10.1126/science.aam9868) | expansion/sparsification as a transferable fly-inspired algorithm; not an exact APL or 5% biological rule |
| R38 | [Lin et al. (2014)](https://doi.org/10.1038/nn.3660) | KC activates GABAergic APL; APL inhibits KC and promotes sparse, decorrelated coding |
| R39 | [Aso et al., architecture (2014)](https://elifesciences.org/articles/04577) | compartmental KC–MBON–DAN organization and historical PAM08/PPL101/MBON05/MBON11 mappings |
| R40 | [Aso et al., valence (2014)](https://elifesciences.org/articles/04580) | broad opposite behavioral biases of MBON05 and MBON11, with ensemble/combinatorial caveat |
| R41 | [Huetteroth et al. (2015)](https://pubmed.ncbi.nlm.nih.gov/25728694/) | PAM gamma4 sweet-reward reinforcement context |
| R42 | [Aso & Rubin (2016)](https://elifesciences.org/articles/16135) | cell-type- and timing-specific learning rules; warning against calling one equation physiological |

Official type pages corroborate type counts/transmitters and major modulatory
partners for [PAM08](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/PAM08.html),
[PPL101](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/PPL101.html),
[MBON05](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/MBON05.html),
[MBON11](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/MBON11.html),
and [APL](https://reiserlab.github.io/celltype-explorer-drosophila-male-cns/types/APL.html).
Exact IDs, counts, joins, and edges remain pinned-file measurements, not facts
borrowed from those pages.

### 1.2 Decision/evidence ledger

| Design element | Primary label | Basis |
| --- | --- | --- |
| Source release, rows, selected bodies, contacts, laterality, transmitters | `MEASURED_CONNECTOME` | recomputed from the three pinned R3 artifacts |
| PN→KC, KC↔APL, and KC→MBON edge support | `MEASURED_CONNECTOME` | raw `body_pre→body_post` rows at declared threshold |
| Contact count as dynamical strength and target normalization | `MODEL_ASSUMPTION` | anatomy does not specify effective strength |
| Whole-bilateral inclusion and stable body-ID ordering | `ENGINEERING_CHOICE` | reproducibility and avoidance of hemisphere cherry-picking |
| Synthetic 16-type cues and amplitude split | `ENGINEERING_CHOICE` | ARC/personalization-independent harness input |
| KC↔APL inhibition promotes sparse/decorrelated coding | `LITERATURE_ESTABLISHED` | R38 |
| ReLU/Jacobi dynamics, 5% target, thresholds, binary KC code | `MODEL_ASSUMPTION` | not specified by connectome or R38 |
| DAN/KC/MBON compartment organization | `LITERATURE_ESTABLISHED` | R39, R41 |
| Exact MaleCNS PAM08/PPL101/MBON05/MBON11 cells and edges | `MEASURED_CONNECTOME` | pinned tables plus official-type corroboration |
| Two-MBON opponent scalar value | `MODEL_ASSUMPTION` | motivated, but not established, by ensemble result R40 |
| Uniform DAN clamp and bounded gain update | `MODEL_ASSUMPTION` | distinct from R11; cell-specific caveat R42 |
| Trial reset, frozen schedules, numerical tolerances, and hashes | `ENGINEERING_CHOICE` | deterministic falsifiability |
| Native topology beats conservative degree-exact rewires | `HYPOTHESIS` | H000-TOPO |
| Declared graph plus local plasticity beats primary controls | `HYPOTHESIS` | H000-MECH |

## 2. Pinned MaleCNS v1.0 inputs

Use only these official flat-connectome artifacts:

| Artifact | Bytes | Rows | Expected SHA-256 |
| --- | ---: | ---: | --- |
| `body-annotations-male-cns-v1.0-minconf-0.5.feather` | 14,483,314 | 211,577 total; 166,700 non-null `superclass` | `2177e246113e4cfbf1e7772ec37c6da1955ff22e8063d0b1f833101f99a9a3b2` |
| `body-neurotransmitters-male-cns-v1.0.feather` | 43,282,834 | 1,835,518 | `95c9289220663abeb3409f3ad9e5a7f8a53f8093f5139d15502cd08da8879621` |
| `connectome-weights-male-cns-v1.0-minconf-0.5.feather` | 1,051,241,946 | 151,856,684 | `e35da783d1c686b2b58b3b87cd6a403ae43bfcfba8bff28e08ef752c1a56afc1` |

The manifest must say `observed_sha256`, not imply that these are
publisher-supplied checksums.

Hard-stop on any source filename, byte count, row count, schema, or hash change.
Do not “repair” a new release into conformance.

Exact Arrow schema contracts, in column order, are:

```text
annotations:
  assignedOlHex1:double, assignedOlHex2:double, bodyId:int64,
  flywireType:string, group:double, instance:string, somaSide:string,
  statusLabel:dictionary<string,int8,ordered>, superclass:string, type:string,
  vfbId:string, hemibrainType:string, itoleeHl:string, supertype:string,
  birthtime:string, mancBodyid:double, mancGroup:double, mancType:string,
  subclass:string, synonyms:string, class:string, rootSide:string,
  somaNeuromere:string, trumanHl:string, dimorphism:string,
  matchingNotes:string, entryNerve:string, mancSerial:double,
  mcnsSerial:double, serialMotif:string, fruDsx:string, exitNerve:string,
  receptorType:string, somaLocation:list<int64>, tosomaLocation:list<int64>,
  status:string

neurotransmitters:
  body:int64, cell_type:string, total_nt_predictions:int32,
  predicted_nt_confidence:double, predicted_nt:string, ground_truth:string,
  celltype_total_nt_predictions:int32, celltype_predicted_nt:string,
  celltype_predicted_nt_confidence:double, consensus_nt:string

weights:
  body_pre:int64, body_post:int64, weight:int64
```

## 3. Exact populations

Use exact equality, never prefix/substring/regex selectors:

| Role | Predicate | Count | Additional invariant |
| --- | --- | ---: | --- |
| PN | `class == "ALPN"` | 686 | 343 L / 343 R |
| KC | `class == "Kenyon_Cell"` | 4,064 | 2,019 L / 2,045 R |
| MBON | `class == "MBON"` | 97 | 48 L / 49 R |
| DAN | `class == "DAN"` | 340 | 170 L / 170 R |
| APL | `type == "APL"` | 2 | body IDs 10540 R, 10977 L |

For every selected neuron require:

- `superclass == "cb_intrinsic"`;
- `status == "Traced"`;
- a one-to-one neurotransmitter join from annotation `bodyId` to NT `body`.

Do not filter on `statusLabel`. Use `consensus_nt`, never raw `predicted_nt`.
The raw prediction would incorrectly label most KCs dopamine; the consensus
label resolves all 4,064 KCs to acetylcholine.

The complete annotation table must contain exactly 211,577 rows, of which
166,700 have non-null `superclass`. The four PN/KC/MBON/DAN pools must be
disjoint and total 5,187.
The 166,700 figure is a `MEASURED_CONNECTOME` property of the pinned artifact;
R1 reports 166,691 neurons and must not be cited as support for the file row
count.

## 4. Graph extraction and orientation

### 4.1 Canonical edge artifact

- Keep every released directed edge whose endpoints belong to the extracted
  union.
- Primary threshold: `weight >= 1`.
- Sensitivity threshold: `weight >= 5`, preregistered and never substituted
  after observing behavior.
- Preserve raw integer contact count.
- Require unique `(body_pre, body_post)` pairs.
- Preserve the three observed self-edges in the canonical artifact; any
  no-autapse model is an explicit ablation.
- Preserve both hemispheres. `somaSide` is not a synapse-side label.

Expected four-class induced graph at threshold 1:

- 1,051,621 directed edges;
- 2,768,198 contacts;
- self-edges on ALPN 116827, KC 157281, and MBON 523060, all weight 1.

### 4.2 Orientation

- tabular edge: `body_pre → body_post`;
- sparse matrix: `W[post, pre]`;
- propagation: `u_post = W @ x_pre`.

Direction sentinel:

- PN→KC: 22,586 edges / 390,928 contacts;
- KC→PN: 5,154 edges / 6,154 contacts.

A transposition or count mismatch is a hard stop.

Canonical node order is ascending unsigned `bodyId`. Duplicate released pairs,
if ever encountered after a source-version change, are summed before
normalization and trigger a source-contract review. For the preregistered
`weight >= 5` sensitivity, retain the primary artifact's 314 PN column
identities and frozen cue panels; only edges are filtered. A newly disconnected
PN therefore remains an explicit zero column rather than silently changing the
interface.

### 4.3 Weight transform

For each directed block `x → y`, define a target-normalized matrix:

```text
Wbar_yx[y, x] = n_x→y / sum_x' n_x'→y
```

Rows with zero incoming contact mass remain zero. Never insert synthetic edges.
The edge mask is fixed across binary/count/log/normalized sensitivity variants.

Classification: contact counts are `MEASURED_CONNECTOME`; treating normalized
contact mass as effective dynamical strength is a `MODEL_ASSUMPTION`.

### 4.4 Provenance graph versus runtime block whitelist

The 1,051,621-edge four-class induced artifact covers ALPN, KC, MBON, and DAN
for provenance/audit. APL is selected by exact type and its blocks are extracted
separately. Experiment 000 runtime propagation is restricted to:

```text
PN→KC
KC→APL
APL→KC
KC→all 97 MBONs
```

Only inputs to MBON05/MBON11 carry mutable gains; all other KC→MBON contacts are
retained for complete-layer null construction but do not enter the four-cell
primary readout. PAM08/PPL101 activities are external teaching clamps, so DAN
edges are measured/provenanced but not propagated.

Every other measured direction is omitted from the core dynamics, including
the three APL→APL pair rows / 22 contacts and all recurrent/cross-class PN, KC,
MBON, and DAN paths not listed above. Self-edges remain in the provenance
artifact but are likewise not silently activated. This whitelist is a
`MODEL_ASSUMPTION`; each omitted block must be named in the extracted-circuit
manifest so absence cannot masquerade as missing data.

## 5. Cue interface

The anatomical PN pool contains 686 ALPNs. The fly-facing cue interface is the
derived subset with at least one released PN→KC edge:

- 314 ALPN bodies;
- 88 types;
- 303 ACh, 6 GABA, 5 glutamate by `consensus_nt`;
- 22,586 PN→KC pair edges / 390,928 contacts;
- reaches 3,812 of 4,064 KCs.

Do not relabel the 314 cells as “all PNs.”

Eligible synthetic cue channels are the 74 PN types that:

1. are represented on both soma sides;
2. have at least one direct PN→KC edge; and
3. are uniformly cholinergic by `consensus_nt`.

Those 74 types comprise exactly 294 of the 314 direct-interface bodies. Keep
all 686 exact ALPNs in extraction provenance, store the 314-column direct
interface in the runtime artifact, and permit cue drive only on the 294 eligible
bodies. Gate 0 must distinguish these three counts explicitly.

### 5.1 Frozen smoke-test cues

Cue A types:

```text
M_l2PNm16, VA6_adPN, VM5v_adPN, VM7v_adPN,
VM3_adPN, VM7d_adPN, VC3_adPN, VP2+_adPN,
DC4_adPN, DA4m_adPN, DL1_adPN, VM4_adPN,
DM5_lPN, VC5_lvPN, DL4_adPN, VP5+Z_adPN
```

Cue B types:

```text
V_ilPN, DC2_adPN, VA1d_adPN, VP1m+VP5_ilPN,
M_lPNm11C, VM5d_adPN, DL3_lPN, DM6_adPN,
M_lPNm13, M_lPNm11A, DA1_lPN, VC4_adPN,
VA2_adPN, VA4_lPN, DA4l_adPN, DA3_adPN
```

For a cue with 16 types:

1. each type receives total amplitude `1/16`;
2. split that amplitude equally between L and R;
3. within each side, split equally across bodies of that type;
4. all other PNs receive zero;
5. never stimulate KCs directly.

This makes total cue amplitude exactly 1 and prevents type cell count or
laterality from carrying the label.

World generation is library-RNG-independent. For world `w`, assign each of the
74 lexicographically sorted UTF-8 type names the key:

```text
SHA256("flygi-exp000-cue-world-v1\0" || uint32_be(w) || "\0" || type_name)
```

Sort by `(digest,type_name)`; the first 16 types are A and the next 16 are B.
Reject an exact duplicate of an earlier world, including A/B reversal, by
adding a deterministic counter to the namespace and repeating. Confirmatory
worlds are indices 0–127. Calibration, the 16-world software pilot, and the
untouched 128-world replication use distinct namespaces. Each world is run in
both reinforcement orientations from reset. Persist the complete small
world/schedule artifact and its SHA-256; never regenerate it implicitly from a
library RNG version.

Every stochastic draw uses purpose-separated SHA-256. Interpret the first 64
digest bits as unsigned big-endian `v` and map to
`u=(v+0.5)/2^64`. Gaussian draws use two separately tagged uniforms and
float64 Box–Muller. Cue order, Bernoulli rewards, Gaussian noise, and
missingness are materialized once so every condition receives identical common
random numbers.

Except for the cue-type key specified above, stochastic schedule keys are the
canonical UTF-8 bytes of:

```text
flygi-exp000-v1|<purpose>|<world>|<task>|<orientation>|<phase>|<trial>|<draw>
```

Integers use unpadded ASCII decimal; enum values are the lowercase strings
stored in the schedule schema. Never use Python `hash()` or implicit generator
state. Persist both the values and their derivation fields.

## 6. Selected opponent learning modules

### 6.1 Appetitive/reward arm

- DAN selector: exact `class == "DAN" and type == "PAM08"`, yielding 50 cells, all dopamine
  consensus; `gamma4`/`y4` is compartment interpretation, not table text;
- plastic-target selector: exact `class == "MBON" and type == "MBON05"`, yielding two cells, IDs
  10495 R and 519371 L; `gamma4→gamma1/gamma2` is compartment interpretation,
  not table text;
- MBON consensus transmitter: glutamate;
- interpretation: avoidance-promoting output whose depression reduces
  avoidance bias;
- KC→MBON05: 1,999 edges / 36,320 contacts from 1,717 KCs.

### 6.2 Aversive/punishment arm

- DAN selector: exact `class == "DAN" and type == "PPL101"`, yielding two cells, IDs 11327 R and
  11900 L; `gamma1-peduncle`/`y1ped` is compartment interpretation, not table
  text;
- plastic-target selector: exact `class == "MBON" and type == "MBON11"`, yielding two cells, IDs
  10704 L and 11402 R; `gamma1-peduncle→alpha/beta` is compartment
  interpretation, not table text;
- MBON consensus transmitter: GABA;
- interpretation: approach-promoting output whose depression reduces approach
  bias;
- KC→MBON11: 4,184 edges / 41,460 contacts from 3,623 KCs.

Primary adaptive state: one bounded gain for each of the 6,183 existing
KC→selected-MBON edges. No missing KC→MBON edge may be created.

Direct DAN→MBON adjacency corroborates the anatomical pairing but does not
define the plasticity gate; compartment co-location does. Bilateral morphology
and synapse-overlap review for PAM08/MBON05 in γ4 and PPL101/MBON11 in
γ1-peduncle is a Gate 0 hard stop. Runtime code must use a reviewed explicit
type→compartment registry, never parse `instance` strings or treat biological
display names as exact MaleCNS `type` values.

The compartmental organization is `LITERATURE_ESTABLISHED` [R39]; PAM gamma4
reward context is literature-supported [R41], and the broad MBON05/MBON11
behavioral signs are literature-supported [R40]. Selecting only these two
opponent MBON types and broadcasting one scalar DAN clamp within each arm are
`MODEL_ASSUMPTION`s. R40 explicitly describes ensemble/combinatorial valence.

## 7. APL feedback circuit

Use actual `type == "APL"` neurons 10540 R and 10977 L.

Measured blocks:

- KC→APL: 4,693 edges / 210,352 contacts;
- APL→KC: 4,633 edges / 196,200 contacts, reaching 4,063/4,064 KCs;
- APL→APL: 3 edges / 22 contacts.

A top-k KC sparsifier is a non-biological surrogate/ablation, never the native
baseline.

KC↔APL feedback and its role in sparse/decorrelated coding are
`LITERATURE_ESTABLISHED` [R38]. The exact two-neuron matrices are
`MEASURED_CONNECTOME`; the rate equation and scalar gain below remain assumed.

## 8. Neural dynamics

Let:

- `x ∈ R^314` be the direct-interface PN cue vector, with nonzero drive
  permitted only on the 294 bodies in eligible cue types;
- `k^(l) ∈ R^4064` be nonnegative KC activity;
- `a^(l) ∈ R^2` be nonnegative APL activity;
- `W_KP ∈ R^(4064×314)` be target-normalized PN→KC contacts;
- `W_KA ∈ R^(4064×2)` be target-normalized APL→KC contacts;
- `W_AK ∈ R^(2×4064)` be target-normalized KC→APL contacts.

Initialize `k^(0)=0`, `a^(0)=0`. With `ReLU(v)=max(v,0)` elementwise and
`alpha=0.5`, update **simultaneously**:

```text
k^(l+1) = (1-alpha) k^(l)
          + alpha ReLU(W_KP x - gamma_A W_KA a^(l) - theta_K)

a^(l+1) = (1-alpha) a^(l)
          + alpha ReLU(W_AK k^(l))
```

Primary arithmetic is float64. Converge when:

```text
max(max_abs(k^(l+1)-k^(l)), max_abs(a^(l+1)-a^(l))) < 1e-10
```

with an inclusive maximum of 256 updates. Non-convergence is a failed cue-world
evaluation, not a silently accepted final state: do not use the last iterate and
do not update plasticity. Reject NaN, infinity, or negative state immediately.
Both right-hand sides use the old state (Jacobi, never Gauss-Seidel), and the
residual is evaluated after every full simultaneous update. Canonical sparse
indices are sorted so float64 summation order is reproducible.

Final KC eligibility code:

```text
z_k = 1[k_k > 1e-12]
```

### 8.1 Reward-free calibration

Before revealing any task reward, use a separately namespaced 256-cue ensemble.
No complete panel may duplicate a pilot, confirmatory, or replication panel;
individual PN types necessarily recur because only 74 are eligible.

1. With `gamma_A=0`, compute feedforward activations for all calibration cues.
   Let the ordered threshold candidates be zero, every midpoint between
   consecutive sorted unique positive activations, and
   `nextafter(max_activation,+inf)`. Because active count is non-increasing in
   threshold, binary-search for the first candidate whose median active fraction
   is `<=0.10`; evaluate it and its immediate predecessor (plus endpoints if
   applicable). Choose minimum absolute error from 0.10, ties choosing the
   larger threshold. Do not enumerate all roughly one million candidates.
2. Freeze `theta_K`. Evaluate `gamma_A=0` and `1`. If median activity at 1 is
   still above 0.05, double through `2,4,...,2^20` until the first value at or
   below 0.05. Failure to bracket by `2^20` is Gate 0 failure.
3. Within the resulting bracket, run exactly 60 float64 midpoint bisections.
   Retain both bracket endpoints and every midpoint; choose minimum absolute
   error from 0.05, ties choosing the smaller `gamma_A`.
4. Across all evaluated gains sorted ascending, require the integer active-KC
   count for every individual calibration cue to be non-increasing. Require the
   chosen ensemble median fraction in `[0.045,0.055]`.
5. Freeze both scalars across native, lesions, tasks, and all topology nulls.

Any nonconvergent calibration cue at any evaluated candidate fails calibration;
it is never skipped. Failure to find the declared target is Gate 0 failure.
Calibration may use only KC
activity—not reward, MBON value, learning accuracy, or native-vs-null
performance. Do not recalibrate interventions or nulls; altered sparsity is
part of their measured effect.

APL-mediated sparsening is established [R38], but 10% feedforward activity,
5% feedback activity, and the `[0.045,0.055]` band are `MODEL_ASSUMPTION`s, not
measured universal fly set points. R14's top-5% WTA is an algorithmic analogy,
not biological calibration evidence.

## 9. Fixed MBON readout

Initialize every plastic gain `g_kj=1`. For selected MBON `j`, define:

```text
m_j = (1 / 0.05) * sum_k [ n_kj / sum_k' n_k'j ] * g_kj * z_k
```

The denominator includes every existing KC input in the selected plastic mask
for `j` and is frozen before plasticity. Multiply normalized contacts by `g`;
never renormalize after `g` changes, which would cancel depression. A
zero-denominator target is a hard extraction failure.

Fixed value:

```text
V = mean_j∈MBON11(m_j) - mean_j∈MBON05(m_j)
```

Positive `V` means approach preference; negative `V` means avoidance. There is
no fitted bias, scale, or downstream classifier.

The opponent sign is literature-motivated [R40], but this two-type scalar and
the fixed factor `1/0.05` are `MODEL_ASSUMPTION`s. Do not describe `V` as the
fly's complete biological value signal.

## 10. Trial state machine

Each trial is exactly:

1. reset neural activities `k=a=0`; retain plastic gains `g`;
2. present cue A through PNs, solve from zero, record `z_A`, MBON activities,
   and `V_A`, then reset neural activity;
3. present cue B through PNs, solve from zero, record `z_B`, MBON activities,
   and `V_B`, then reset neural activity;
4. record the pre-reward ranking margin and the scheduled cue's already
   computed `z` and `V`;
5. reveal either numeric reward `r` (including explicit zero) or the tagged
   state `MISSING`;
6. if numeric, form DAN teaching scalars and update designated existing
   KC→MBON gains once using the scheduled cue's `z`; if `MISSING`, copy gains
   bit-for-bit;
7. assert bounds and record update diagnostics;
8. reset all PN/KC/APL/MBON/DAN activities before the next trial.

No activity trace, DAN state, reward label, or optimizer state persists. Only
`g` persists. Changing the current reward while holding `g` and the cue fixed
must leave the current pre-reward predictions bit-identical. Reversal does not
reset `g`; a mirrored reinforcement orientation always starts from fresh
all-ones `g`.

## 11. Plasticity

Reward lies in `[-1,1]`.

The environment supplies reward; Experiment 000 does not compute a native RPE.
Clamp every exact PAM08 cell to `D_PAM08` and every exact PPL101 cell to
`D_PPL101`; their population means therefore equal the scalar clamps. Broadcast
those means only through the fixed compartment registry below.

```text
D_PAM08  = max(r, 0)
D_PPL101 = max(-r, 0)
eta      = 1 - 2^(-1/20) ≈ 0.0340636710751544

g_kj(new) = g_kj + eta * z_k * ((1 - D_j) - g_kj)
```

- MBON05 edges use `D_PAM08`.
- MBON11 edges use `D_PPL101`.
- Clamp only as a postcondition against numerical overshoot; analytical updates
  must already remain in `[0,1]`.
- `r=0` is explicit recovery/extinction toward gain 1 on active edges.
- missing/unobserved feedback performs **no update at all**.
- a DAN ablation also bypasses the plasticity update exactly; it must be
  bit-identical to `eta=0` when both start from `g=1`.
- applying the equation with `D=0` is a distinct **recovery-only** condition,
  never called DAN-off or missing feedback.
- delayed eligibility is excluded from core Experiment 000.

This is a stable `MODEL_ASSUMPTION` inspired by compartment-specific
reinforcement-gated depression/recovery [R39, R42]. It is not R11's equation,
contains no predicted-reward term or MBON→DAN feedback, and must be called
**reinforcement-gated local plasticity**, not RPE learning or an exact
physiological rule.

## 12. Task battery

All outcomes are evaluated pre-update. Cue order is deterministically
counterbalanced within a world. Every A+/B− world has an A−/B+ copy from reset.

For trial `t`, with the positive-reward cue under the current contingency
denoted `c+`, define:

```text
Delta_t = V(c+; g_t) - V(c-; g_t)
score_t = 1.0  if Delta_t >  1e-12
          0.5  if abs(Delta_t) <= 1e-12
          0.0  otherwise
```

| ID | Frozen schedule | Primary endpoint |
| --- | --- | --- |
| 000A | 200 trials; exactly 100 A/100 B; positive cue `r=+1`, negative cue `r=-1` | full-curve mean `score_t` |
| 000B | 200 acquisition + 200 reversal trials; exactly 100/100 per phase; contingency swaps at trial 201 without resetting `g` | full-curve mean `score_t`, with sign swapped at trial 201 |
| 000C | 256 trials; 128/128; `r=+1` iff frozen `u<p_c`, else `-1`; `p_good=.75`, `p_bad=.25` | full-curve mean `score_t`; fixed-link Brier is secondary |
| 000D-noise | 256 trials; 128/128; always observe `clip(latent + N(0,.1),-1,1)` | full-curve mean `score_t` |
| 000D-sparse | 256 trials; 128/128; deterministic latent `+1/-1` is independently revealed with `q=.20`; missing skips update | full-curve mean `score_t` |

Each adjacent pair within each even-length phase contains one A and one B; a
frozen hash bit determines AB versus BA. Mirrored orientations reuse the same
cue order and reveal mask and use exact sign-negated realized rewards. Thus
stochastic Bernoulli complements and Gaussian noise signs are coupled rather
than independently redrawn.

Define `S_000D` as the equal mean of the noise and sparse subarm scores. Noise
sensitivities `sigma in {0,.5}` with `q=1` are secondary. Reversal latency is
the first post-switch trial beginning 20 consecutive correct rankings,
right-censored at 201. Acquisition interference and stochastic convergence are
descriptive until a later protocol version defines inferential endpoints.

For 000C's descriptive calibration only, use the frozen non-trainable link
`p_hat=(clip(V_scheduled,-1,1)+1)/2`, outcome `y=(r+1)/2`, and ordinary mean
squared Brier loss. This mapping is a `MODEL_ASSUMPTION` and is not part of any
primary gate.

Cue corruption/APL robustness (000E) starts only after Gate 2. Delayed reward
(000F) is deferred and makes no core claim; no eligibility trace may enter
Experiment 000 by implication.

## 13. Controls and null families

### 13.1 Mechanism controls

- **primary C1 — frozen gains:** `eta=0`;
- **primary C2 — reward-time shuffle:** permute complete
  `(reward,observed_or_missing)` records within each task phase with a frozen
  world-specific permutation, preserving cue order and phase marginals;
- **primary C3 — graph-off:** zero PN→KC and KC→MBON propagation and return
  fixed `V=0`; no hidden adapter may learn;
- DAN-off (skip the plasticity update; expected bit-identity with frozen gains
  from the same initial state, retained as an implementation kill test);
- recovery-only (`D=0` with the update equation still applied), reported as a
  mechanistic sensitivity rather than an independent negative control;
- PN→KC lesion;
- selected plastic-mask lesion;
- MBON readout lesion;
- APL lesion;
- ideal schedule oracle that sets `(V_A,V_B)` to the task's current frozen
  expected rewards before each trial and therefore verifies scoring/evaluator
  orientation; it never enters a biological comparison.

Only C1–C3 define the conjunctive H000-MECH gate. DAN-off is deliberately not
an independent contrast because it must equal C1 from pristine gains. In this
four-MBON readout, removing the entire selected plastic mask also collapses the
readout and is therefore not independent of graph-off. PN→KC, plastic-mask,
MBON-readout, APL, and recovery-only interventions are diagnostic/secondary and
cannot rescue a failed primary claim.

### 13.2 Topology/weight nulls

Primary topology inference uses 39 independently generated, whole-bilateral,
degree-exact nulls. The primary null rewires both PN→KC and the complete
97-MBON KC→MBON layer, within frozen biological strata, then applies the same
selected target mask/readout. This prevents the null algorithm from knowing
which four MBONs are favored by the evaluation.

Required families:

- PN→KC-only exact rewire;
- KC→MBON-only exact rewire;
- combined PN→KC + complete KC→MBON exact rewire (primary);
- fixed-edge weight multiset shuffle;
- random sparse expansion matched on dimensions/density;
- Erdős–Rényi weak floor;
- laterality/sign/compartment sensitivity controls.

The complete KC→all-MBON block contains 61,210 edges. Rewire that full block
before deriving the selected mask as all rewired inputs to the fixed MBON05 and
MBON11 body IDs. Exact target degrees must therefore retain 1,999 + 4,184 =
6,183 selected edges. Never condition a null by rewiring only the four
result-bearing MBONs.

#### 13.2.1 Frozen anatomical strata

Run Curveball independently within these strata:

```text
PN→KC:    (PN.somaSide, KC.somaSide, KC.type)
KC→MBON:  (KC.type, KC.somaSide, MBON.somaSide, MBON.input_family)
```

PN type is intentionally not a stratum: PN-type-to-KC partner identity is part
of the topology under test. `MBON.input_family` comes from a versioned,
manually reviewed registry of all 37 exact MBON types; it represents only the
input compartment. No confirmatory run may derive that registry by parsing
`instance` strings.

The v1 registry proposed for morphology signoff is:

```yaml
gamma:
  [MBON05, MBON20, MBON21, MBON25, MBON25-like, MBON27,
   MBON29, MBON30, MBON32, MBON33, MBON34, MBON35]
alpha_beta:
  [MBON06, MBON07, MBON14, MBON18, MBON19, MBON23]
alpha_prime_beta_prime:
  [MBON03, MBON04, MBON10, MBON13, MBON15, MBON15-like,
   MBON16, MBON17, MBON17-like, MBON26, MBON28, MBON31]
gamma_plus_alpha_prime_beta_prime: [MBON01, MBON09, MBON12]
alpha_beta_plus_alpha_prime_beta_prime: [MBON02]
gamma_plus_alpha_beta: [MBON24]
gamma_plus_peduncle: [MBON11]
calyx: [MBON22]
```

Until every entry is checked against official morphology documentation, this is
a provisional engineering registry and Gate 0 remains closed.

These strata preserve every individual's relevant in/out degree, laterality,
KC subtype, and coarse MBON input family while randomizing exact partners.

#### 13.2.2 Curveball transition and weights

Within one stratum, represent each presynaptic row as a set of postsynaptic
cards. For two uniformly sampled distinct rows `i,j`, retain their common
neighbors, uniformly repartition the symmetric-difference cards while keeping
row `i`'s original exclusive-card count, and give the complement to `j`.
Allow the identity repartition so the Markov chain has a self-loop. The output
support must remain simple.

After support rewiring and before normalization, uniformly permute each
`(presynaptic body,stratum)` raw positive-weight multiset onto that source's new
edges using a purpose-distinct weight seed. This exactly preserves every
source-stratum outgoing weight multiset and strength, but not each target's raw
weighted in-strength; record that limitation. Apply the ordinary target
normalization only after rewiring/weight assignment.

#### 13.2.3 Structural pilot and production ensemble

An edge is structurally switchable only if another row in its stratum can
exchange at least one exclusive neighbor with it. Require at least 80% of edges
switchable separately in PN→KC and KC→MBON. Failure stops the protocol; it does
not silently relax strata.

Calibrate burn-in outcome-blind with four independent chains from native
support. Save diagnostics every eight sweeps at candidate burn-ins
`64,128,256,512,1024`, where a sweep is one sampled row-pair proposal per active
row per stratum. Track native edge overlap, weighted mean row-pair Jaccard,
`log1p` bipartite four-cycle count, the leading singular value after subtracting
the stratum configuration expectation, and nontrivial-trade rate. Select the
smallest candidate for which every diagnostic has split `R-hat<=1.05`, ESS>=100,
native overlap changes by <0.01 on doubling, and other medians change by <1% on
doubling. Failure at 1,024 sweeps stops null inference.

For null index `r=0..38`, derive independent topology and weight seeds from:

```text
first_uint64_be(SHA256("flygi-exp000-null-v1|r|block|purpose"))
```

Create paired PN-only, MBON-only, and joint rewires; only the 39 joint rewires
are the primary topology null. Every null must have exact node sets, per-stratum
degree vectors on both partitions, total degrees, edge counts, source-stratum
weight multisets, finite normalized weights, unchanged APL/DAN blocks, unique
support hash, calibrated diagnostics, and the exact selected-mask counts. Any
violation invalidates the generator and requires regenerating all 39 before
behavior is inspected.

## 14. Independent unit and inference

The independent unit is the **cue world**, not a trial, neuron, edge, hemisphere,
seed, or null instance. Native and controls receive the identical ordered
outcomes within each world.

For task or subarm `q`, world `w`, orientation `o`, let:

```text
S_task[q,w,o] = mean_t(score_t)
S_A[w] = mean_o(S_task[000A,w,o])
S_B[w] = mean_o(S_task[000B,w,o])
S_C[w] = mean_o(S_task[000C,w,o])
S_D[w] = mean(mean_o(S_task[000D-noise,w,o]),
              mean_o(S_task[000D-sparse,w,o]))
S_world[w] = mean(S_A[w], S_B[w], S_C[w], S_D[w])
```

Thus each task has equal weight despite unequal trial counts, both mirrored
orientations stay inside the same world, and `S_world` lies in `[0,1]`. The
orientation pairing makes every deterministic frozen cue bias average exactly
0.5. Trials, tasks, orientations, graph-null indices, and repeated software
seeds never inflate `n` beyond 128.

### 14.1 Mechanism inference

For each primary control `c in {C1,C2,C3}`, compute paired world differences:

```text
d[w,c]   = S_world[native learned,w] - S_world[control c,w]
delta[c] = mean_w(d[w,c])
```

For each contrast, run 50,000 paired bootstrap resamples of the 128 world IDs.
Report the one-sided 95% lower bound (fifth percentile) and ordinary two-sided
95% percentile interval. Also run a one-sided paired sign-flip test with 99,999
purpose-seeded random sign vectors and add-one p-value:

```text
p = (1 + count(T_perm >= T_observed)) / 100000
```

H000-MECH is an intersection-union claim and passes only if every primary
control has `delta>=0.10`, one-sided lower bound `>0`, and `p<=0.05`. Report
`max(p)` as the global mechanism p-value; no multiplicity correction is needed
for this conjunctive global statement.

### 14.2 Topology inference

Topology inference is serially gated on H000-MECH. For graph `g`, compute
`T_g=mean_w(S_world[g,w])`. With joint nulls `J_r`, `r=0..38`:

```text
p_rank = (1 + count_r(T_Jr >= T_native)) / 40
S_nullmean[w] = mean_r(S_world[J_r,w])
d_topo[w] = S_world[native,w] - S_nullmean[w]
delta_topo = mean_w(d_topo[w])
```

Ties count against native. The rank test represents graph Monte Carlo
uncertainty; the same 50,000 paired-world bootstrap supplies the topology
effect interval. Null graphs are Monte Carlo samples, not biological
replicates.

### 14.3 Gates

- **Gate 0 — extraction:** all source, population, direction, transmitter,
  compartment, registry, block-count, calibration, and structural-null
  invariants pass.
- **Gate 1 — deterministic evaluator assertions:** ideal schedule-oracle score
  is exactly 1.0, fixed-zero score exactly 0.5, and deliberately inverted-label
  score exactly 0.0; mirror/reset/no-mutation fixtures are exact; frozen,
  all-feedback-missing, and DAN-off are bit-identical from pristine gains. The
  16-world harness additionally checks that each active negative control remains
  below 0.60, but fixture confidence intervals are not treated as evidence.
- **Gate 2 — H000-MECH:** all three primary contrasts meet the conjunctive
  `delta`, interval, and p-value criteria above.
- **Gate 3 — H000-TOPO:** Gate 2 passed; `p_rank<=0.05`, `delta_topo>=0.05`, and
  paired-world one-sided lower 95% bound `>0`.
- **Gate 4 — replication:** rerun unchanged code/config on the untouched 128
  replication worlds; require mechanism contrasts in the same direction plus
  `delta_topo>0` with lower bound `>0`.

If more than 20% of nulls are dynamically unstable under frozen parameters,
Gate 3 is invalid; preregister a common-stable sensitivity rather than counting
instability as native superiority. Apply Holm correction separately within
each declared secondary family (task-specific outcomes, lesions, localization
nulls, or weight/ER sensitivities). Secondary results cannot rescue a failed
primary gate.

## 15. Validation ladder

No stage may be skipped:

1. source/hash/schema extraction tests;
2. exact population/ID/NT/edge invariants;
3. bilateral compartment morphology signoff;
4. hand-calculated microcircuit with orientation and one update;
5. separate Bennett/literature reproduction oracle, explicitly not evidence for
   native PN→KC topology;
6. one-cue dynamics pulse and convergence diagnostics;
7. one-trial reward update with exact expected gains;
8. 20-trial kill battery for learning direction, reward-swap, reset, missing
   feedback, and bounds;
9. 16-world pilot used only for software/numerical failures;
10. locked 128-world mechanism run;
11. topology run against all 39 accepted nulls;
12. fresh locked replication.

At every stage, real/native, control, and null paths must share the same public
interface and instrumentation.

### 15.1 Normative analytic kill tests

Before the 16-world pilot, all of these must pass:

1. **Extraction:** exact population/type/body counts; 314 direct-interface PNs;
   294 eligible bodies/74 types; recomputed 1,999 + 4,184 plastic edges; all
   smoke-cue types bilateral, cholinergic, and direct; sampled edges prove
   `body_pre→body_post` and `W[post,pre]`.
2. **KC/APL microcircuit:** one KC/one APL with unit weights, `x=1`,
   `theta=0`, and `gamma=.25` has fixed point `k=a=.8`; the simultaneous
   float64 solver reaches it. A deliberately inadmissible/nonconvergent case
   raises and performs no plastic update.
3. **Plasticity pulse:** positive reward depresses only active MBON05 edges and
   makes the next-trial opponent value more positive; negative reward does the
   symmetric MBON11 operation; inactive edges are unchanged; explicit zero
   recovers; missing feedback is bit-identical no-update.
4. **Half-life:** with active `z=1`, 20 consecutive `D=1` updates take gain
   exactly from 1 to 0.5 within float64 tolerance; 20 recovery updates halve
   the distance `1-g`.
5. **Causality/order:** changing current reward with cue and pre-update gain
   fixed cannot change current `V`; reward becomes visible only after both
   pre-reward probes are recorded.
6. **Reset:** a repeated cue at unchanged gains produces bit-identical
   `k,a,z,m,V`; a preceding different cue cannot affect it.
7. **Ideal positive:** an orthogonal synthetic two-cue circuit learns and
   reverses the ordering in both mirrored orientations. Failure is evaluator
   failure, not a biological result.
8. **Statistical harness:** orientation pairing collapses fixed cue bias to
   0.5; resampling occurs only by world; add-one p-values are never zero; rank
   ties count against native; 39 nulls have minimum possible `p_rank=.025`.

### 15.2 Literature oracle boundary

Pin R11's archived code/data version and reproduce its mixed-valence model plus
one conditioning and one blocking result using the paper's own synthetic KC
patterns, equations, and parameters. Keep this in a separate oracle namespace:
it uses no MaleCNS PN→KC extraction, no Experiment 000 APL dynamics, and no
claim about native topology. It validates faithful implementation of a
published reference model; it does not validate FlyGI's different gain rule.

## 16. Instrumentation contract

Every run records:

- source/data/config hashes and dirty state;
- population/block counts and selected body IDs;
- cue-world ID and generation seed;
- topology-null seed plus invariant/mixing diagnostics;
- `theta_K`, `gamma_A`, calibration ensemble hash, and calibration outcome;
- iterations/residual for every fixed-point solve;
- PN input mass by type/side;
- KC active count/fraction and cue-overlap diagnostics;
- APL activity;
- each selected MBON activity and fixed value `V`;
- pre-reward prediction, revealed/missing reward, DAN scalars;
- number and norm of modified gains by target, plus min/max/bounds;
- trial/task phase and reset events;
- failures without coercing them into zero-score rows.

Generated traces and graph arrays remain outside Git. Commit only schemas,
small manifests, provenance, code, tests, aggregate reports, and hashes.

## 17. Remaining blind empirical gates

The mathematical/protocol choices above are frozen. Only these observations
remain open, and none may be tuned using behavioral native-vs-null outcomes:

- [ ] Recompute the raw PN→KC support from pinned files and resolve the new
      exact-selector result (22,586 edges / 3,812 reached KCs) against the
      legacy heuristic-selector record (22,581 / 3,811).
- [ ] Manually review bilateral PAM08/MBON05 and PPL101/MBON11 overlap and every
      entry in the 37-type MBON input-family registry against official
      morphology documentation.
- [ ] Measure >=80% switchability and calibrate Curveball burn-in using only
      structural diagnostics.
- [ ] Run the 16-world harness pilot after analytic kill tests; it may repair
      software/evaluator defects but may not tune biological parameters toward
      native superiority.
- [ ] Attach verified reference IDs/URLs to each literature-established claim
      before merging this specification to the protected default branch.

No behavioral confirmatory run begins until all four blind gates are closed.

## 18. Additive-first migration boundary

Experiment 000 must not be implemented as a small variant of the ARC runtime.
The following compatibility boundary is frozen before integration:

### 18.1 Reuse unchanged

- domain-separated deterministic seeding from `flygi.seed`;
- append-only telemetry and inspection machinery;
- official MaleCNS download, hash, and strict raw-table schema utilities;
- `NodeIndex`, raw `W[post, pre]` count construction, and generic provenance
  primitives;
- exact-conjunction group filtering, wrapped by new expected-count and
  biological-invariant checks.

### 18.2 New Experiment 000 implementations

- a raw-table MB extractor and a distinct extracted-circuit manifest;
- an explicit project/data-root config loader for nested experiment configs;
- synchronous float64 PN/KC/APL dynamics and the fixed opponent MBON readout;
- local existing-edge plasticity and the pre-reward trial state machine;
- bilateral degree-exact bipartite nulls with mixing diagnostics;
- cue-world-aware result rows, symmetric pairing checks, and inference;
- an Experiment 000 ledger adapter rather than direct reuse of the ARC league.

### 18.3 Quarantine as Experiment 002/FlyARC legacy

Do not import the current ARC encoder, controller, decoder, dynamics runtime,
plasticity, config model, result schema, or MB bus into Experiment 000. Measured
reasons include:

- compiled ARC metadata omits fields required by the extraction contract;
- ARC weights are heuristic-signed, transformed, incoming-L1 normalized
  float32 values rather than raw contact counts;
- legacy MB selectors use type-name substring/prefix rules and produce the
  wrong PN/DAN pools;
- the legacy MB null does not preserve KC output degree;
- the legacy pairing helper checks row coverage only left-to-right;
- existing config discovery/path resolution does not safely support nested
  Experiment 000 configs.

### 18.4 Integration order after the FlyARC closure SHA

1. Add ARC public-import, CLI, config, result-adapter, and resume goldens.
2. Add the new Experiment 000 extractor without moving old code.
3. Land and validate the deterministic extracted-circuit artifact contract.
4. Add dynamics/readout, then plasticity/trial runner, each behind microtests.
5. Add mechanism ablations; add topology nulls only after mechanism gates pass.
6. Add cue-world inference and the umbrella ledger adapter.
7. Physically relocate FlyARC only after wrappers reproduce the frozen closure.

This additive sequence is a deliberate anti-rewrite constraint: no legacy
generalization and no directory move is allowed to precede executable
compatibility evidence.
