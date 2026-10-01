# LinkedIn article draft

*(Post AFTER the repo is public and the Kaggle writeup is submitted. Suggested
cover: media/cover.png. Attach figures 1–3 inline where marked. First person =
you; edit voice freely — the numbers must not drift from the factsheet.)*

---

**Title: I wired a complete fly connectome to an AI benchmark. Here's what it
actually computed — and what it didn't.**

This September, hooking a fruit-fly connectome up to video games became a
genre. Doom, Mario 64, Beat Saber — dozens of projects dropped the newly
mapped fly connectomes (MaleCNS, FlyWire) into a simulator and streamed the
result. The common critique is fair: most of
those demos are a frozen graph plus a hand-written readout. In most of them you can't tell what the wiring did — the survey behind this
post (2026-09-30) found one demo running wiring controls, and none running
validation, input gating and controls together.

For the past weeks I've been running the opposite experiment, in public, on
ARC-AGI-3 — the interactive reasoning benchmark designed to be easy for
humans and hard for current AI. The substrate: the complete MaleCNS
connectome, 166,700 retained neurons in our compiled graph. One rule, written into the repository's operating directive:
**everything goes through the fly, or nothing goes at all.** Every circuit
gets its biology validated first, gets input it can actually use, and then
has to beat its own shuffled twin — the same anatomy, degree-for-degree, with
the specific wiring destroyed. If a component works just as well with the
wiring scrambled, the fly earns no credit.

[figure: fig2_verdict_matrix.png]

Here's what the audit measured.

**The honest headline is a pair.** Our engineered scaffold — thirteen
hand-built, game-specific action grammars — multiplied our local score ~52x
(0.55 → 28.74 on matched competition-mode runs). On Kaggle's hidden games, every rung
of this ladder scored 0.15 — three submissions in a row. 0.15 is the abstention floor: it's
what an agent earns when nothing it knows matches anything it sees. Grammar
transfer to unseen games measured exactly zero, three times.

[figure: fig1_ladder_vs_hidden.png]

Meanwhile the one fly component those agents actually deployed — the eye's
anatomical map, compiled straight from the connectome, no dynamics, no
training — completed first levels at 2.59x the human action baseline, where
an identical agent with a scrambled map needed 11.59x. A 4.5x efficiency gap
attributable to anatomy alone. Small, real — and it survived its own control. (Its hidden-set contribution
was never isolated: no scrambled-map control ever ran on Kaggle. Boundaries
matter.)

**And the deep circuits?** This is where it gets interesting. Our class-2
and class-2.5 models of the fly's motion detectors and learning center (the
mushroom body) both PASSED their biology bands — sparse coding in the
published range, direction selectivity in the published range. Then both lost the ARC task to their own
shuffled twins: one-shot association, real wiring 0.600 vs rewired 0.800;
motion decoding, real 0.3875 vs rewired 0.4306. The simulated circuits work at their fidelities. The specific wiring, on
these tasks, points the wrong way — plausibly because evolution tuned it for
fly inputs, not pixel grids.

[figure: fig3_controls_both_ways.png]

The controls cut both ways, which is how you know they're honest: the same
instrument flagged our own tested, shipped coordinate head as exploring 3.29x *less*
than random clicking, and showed a trained head that was genuinely
connectome-dependent and still generalized zero. Well-tested and worse than
random are compatible. So are connectome-dependent and useless.

**Why publish a 0.15?** Because the field is drowning in "brain plays game"
demos and starving for attribution. No negative here is about the living
fly — every verdict carries its fidelity class and its task. But the method
(validate → gate the input → test against rewired twins) is portable to any
"biology does AI" claim, and the measurement that a 52-fold local gain can
transfer exactly zero is a warning label every benchmark chaser can use.

Everything is open: the code, the full experiment log (including the twelve
failed predictions — our score forecasts went 0 for 12 while the
measurements all held), the preregistrations, and the Kaggle writeup we
submitted to the ARC Prize 2026 Paper Track.

**Repo: https://github.com/msafdari/FlyGI**

*(add Kaggle writeup link once live)*

#neuroscience #connectome #ARCAGI #Drosophila #AI #openscience
