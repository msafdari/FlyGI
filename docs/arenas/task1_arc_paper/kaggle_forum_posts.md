# Kaggle forum posts for release day (Rules §3.6.b, register AP-12)

Two short posts, one per forum, posted the day the repo flips public.
Fill {{REPO_LINK}} with the public GitHub URL. Numbers fact-gated
against factsheet.md and the registry 2026-10-30; the FLAT reading is
the current one. Keep them short — the writeup carries the detail.

---

## Post 1 — Paper Track forum

Title: FlyGI: auditing the 166,700-neuron MaleCNS fly connectome on
ARC-AGI-3 (negative-results paper, repo now public)

We ran the full MaleCNS *Drosophila* connectome against ARC-AGI-3 and
published everything: preregistered kill tests, degree-preserving
rewire controls, input gates, and a fidelity ladder up to
literature-pinned spiking physiology.

Headlines, each with its control: our grammar scaffold grew the local
gateway ~52-fold and transferred exactly zero to the hidden set
(0.15, the abstention floor, three submissions). The one deployed fly
component that survived its own control is the static retinotopic eye
map (2.59x human action-cost baseline vs 11.59x for its scrambled
twin). The wiring is measurably non-random — two circuits' topology
beats 200 degree-preserving rewires at the empirical floor — and
still computes nothing we could score at any tested physiology. And
our registered harness-sensitivity control came back FLAT: a reservoir
tuned into the known-good long-memory regime also moved no score, so
our class-1 ARC zeros read as "under this interface, no tested graph
moved score," never as a measured absence of fly advantage.

Repo (MIT-0, full worklog + preregistrations + league):
{{REPO_LINK}}

Writeup: linked from the repo README. Happy to answer anything — every
claim in the writeup carries its tier and its control.

---

## Post 2 — ARC-AGI-3 discussion forum

Title: What a fly connectome did (and measurably did not do) on
ARC-AGI-3 — repo public

We spent two months wiring the MaleCNS fly connectome (166,700
neurons) into ARC-AGI-3 behind preregistered controls. The repo is now
public: {{REPO_LINK}}

Short version: game-specific scaffolding scored locally and
transferred zero (three 0.15 submissions = the abstention floor);
the fly's anatomical eye map is the one component that beat its
scrambled control; every dynamical circuit we tested lost to its own
degree-preserving rewire or could not be scored, measured across five
external benchmarks too. The methods are the contribution: if you
think your structured prior helps, the repo's attribution stack
(fidelity ladder, input gates, rewired nulls, scrambled twins,
engineered ceilings, preregistered kill rules) will tell you whether
it actually does.
