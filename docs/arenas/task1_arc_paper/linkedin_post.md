# LinkedIn post draft (v3, de-jargoned 2026-10-31; panel-written, judged, fact-gated)

*(Post as a regular LinkedIn POST, not an article. 2,864 chars once the
[figure: ...] marker lines are removed; LinkedIn's cap is 3,000. The hook
must land before the ~200-char "see more" fold, and it does. Resolve each
[TAG: ...] via the composer @ dropdown to the official page (ARC Prize,
Kaggle, HHMI Janelia Research Campus); if a page does not surface, delete
the slot text, never guess. Attach the two figures at the marked points and
delete the marker lines. Every number has a row in docs/social/FACTS.md
("Post numbers" section). Voice edits allowed EXCEPT: no number changes, and
the compass paragraph keeps "fitted by Biswas et al.'s published recipe,
applied once to our wiring counts" and "our fitted numbers differ from the
published ones" intact; those clauses outrank style.)*

---

You have seen the videos: a fly's brain map hooked up to Doom. The question those clips leave open: is the wiring doing the work, or would a scrambled copy run just as well?

I spent a season answering that, in public.

A fruit fly's brain has now been mapped neuron by neuron. In the version I run: 166,700 neurons, 25 million connections, from the MaleCNS dataset by [TAG: HHMI Janelia Research Campus]. I put that map on ARC-AGI-3, the [TAG: ARC Prize] benchmark of novel hidden games, easy for humans and hard for current AI. Why that arena? It is built to make memorization useless, and the fly brings none: its wiring is a prior shaped by 400 million years of evolution. If innate structure transfers anywhere unpaid, it is here. Zero trained parameters.

One rule separated this from a demo: every component had to beat a scrambled copy, where every neuron keeps its number of connections but who talks to whom is destroyed. If the scramble does just as well, the fly gets no credit.

The fly lost. All season.

The scrambled copies kept winning or tying. The fly's motion and memory circuits passed their biology checks, then lost the AI tasks to their own scrambled twins (memory 0.600 vs 0.800, motion 0.3875 vs 0.4306). My own engineering fared no better. A 52x local score gain transferred exactly zero to the hidden games: 0.15, three times. Every failure went public, pass bars written down in advance. All sixteen of my score predictions were wrong. Published too.

[figure: fig1_ladder_vs_hidden.png]

One thing survived: the eye's anatomical map, no dynamics, no training. First levels at 2.59x the human action baseline, 11.59x with the map scrambled. A measured 4.5x gap from anatomy alone.

Then the fly won one back.

Its compass, the circuit a fly uses to track which way it is facing, had failed in all three earlier versions. So I gave each neuron type electrical properties fitted by Biswas et al.'s published recipe, applied once to the wiring counts. With those fitted properties, the simplified compass held its heading where it was put: 8 of 8 angles, 0.0 degrees of error. None of the three scrambled copies could form a working compass at all.

[figure: fig3_controls_both_ways.png]

That win earned zero benchmark points. My fitted numbers differ from the published ones, and I flagged it. It is still the measurement I care most about. The wiring itself carries something the scramble destroys.

The instrument cut against me too: it flagged my own shipped component as exploring 3.29x less than random clicking. That is what makes the rest believable.

Every "biology does AI" claim should be tested this way: check the biology, feed it real input, make it beat its scrambled twin.

Everything is open, wrong predictions included. Kick the tires, poke holes.

Code and full log: https://github.com/msafdari/FlyGI
Writeup on [TAG: Kaggle]: https://www.kaggle.com/competitions/arc-prize-2026-paper-track/writeups/flygi-connectome-attribution-audit
Brain map: MaleCNS, male-cns.janelia.org

#ARCPrize #neuroscience #openscience #AI
