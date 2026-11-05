# LinkedIn release copy (v4, restored voice, November 4)

The live post (urn:li:activity:7523777525907357697) carries the text below the
rule: the October 31 voice and structure, with the eye-map paragraph rewritten
to the paired result and two precision edits ("Zero trained parameters in the
wiring", "bought nothing on the hidden games"). 2,975 characters. The November 3
flat version is superseded (user's call, Nov 4). Every number is in
docs/social/FACTS.md; the withdrawn 2.59x / 11.59x / 4.5x figures never appear.
Attached media on the live post are the October fig1 and fig3 exports (LinkedIn
locks media after publication). No @-mentions; the post works as plain text.

---

You have seen the videos: a fly's brain map hooked up to Doom. The question those clips leave open: is the wiring doing the work, or would a scrambled copy run just as well?

I spent a season answering that, in public.

A fruit fly's brain has now been mapped neuron by neuron. In the version I run: 166,700 neurons, 25 million connections, from the MaleCNS dataset by HHMI Janelia. I put that map on ARC-AGI-3, the ARC Prize benchmark of novel hidden games, easy for humans and hard for current AI. Why that arena? It is built to make memorization useless, and the fly brings none: its wiring is a prior shaped by 400 million years of evolution. If innate structure transfers anywhere unpaid, it is here. Zero trained parameters in the wiring.

One rule separated this from a demo: every component had to beat a scrambled copy, where every neuron keeps its number of connections but who talks to whom is destroyed. If the scramble does just as well, the fly gets no credit.

The fly lost. All season.

The scrambled copies kept winning or tying. The fly's motion and memory circuits passed their biology checks, then lost the AI tasks to their own scrambled twins (memory 0.600 vs 0.800, motion 0.3875 vs 0.4306). My own engineering fared no better. A 52x local score gain bought nothing on the hidden games: 0.15, three times. Every failure went public, pass bars written down in advance. All sixteen of my score predictions were wrong. Published too.

One thing looked like a survivor: the eye's anatomical map, no dynamics, no training. On one public game: 6 actions to clear level one, 199 with the map scrambled, then 15 against 255. Across all 14 runs where both finished, the median cost ratio was 1.06. One game, not a trend.

Then the fly won one back.

Its compass, the circuit that tracks which way the fly faces, had failed in all three earlier versions. So I gave each neuron type electrical properties fitted by Biswas et al.'s published recipe, applied once to the wiring counts. With those, the simplified compass held its heading where it was put: 8 of 8 angles, 0.0 degrees of error. None of the three scrambled copies could form a working compass at all.

That win earned zero benchmark points. My fitted numbers differ from the published ones, and I flagged it. It is still the measurement I care most about. The wiring itself carries something the scramble destroys.

The instrument cut against me too: it flagged my own shipped component as exploring 3.29x less than random clicking. That is what makes the rest believable.

Every "biology does AI" claim should be tested this way: check the biology, feed it real input, make it beat its scrambled twin.

Everything is open, wrong predictions included. Kick the tires, poke holes.

Code and full log: https://github.com/msafdari/FlyGI
Writeup on Kaggle: https://www.kaggle.com/competitions/arc-prize-2026-paper-track/writeups/flygi-connectome-attribution-audit

#ARCPrize #neuroscience #openscience #AI
