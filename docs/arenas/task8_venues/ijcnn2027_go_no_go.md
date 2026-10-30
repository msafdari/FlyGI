# IJCNN 2027 competition proposal — go/no-go analysis, 2026-10-07

The survey's Task 8 hard date. The decision is whether to propose
ORGANIZING a competition at IJCNN 2027 — not whether to submit a
paper; the regular-paper option is analyzed as the alternative.

## The call, verified today

SOURCED, ijcnn.org/2027 via web search; the site is read through
search snippets — re-verify the exact cutoff time zone in the
submission system before any submit.

- Conference: June 14-18, 2027, Cape Town, South Africa (standalone
  IJCNN; INNS + IEEE CIS).
- Competition proposal: a 4-page PDF (excluding references), due
  **2026-11-30**. Required sections: (1) title, task, motivation,
  expected impact; (2) justification for the competition format;
  (3) target community, accessibility, expected participation;
  (4) datasets — provenance, licenses, access, train-test splits.
- Timeline if accepted: notification 2026-12-15; public launch
  2027-01-01; entries close 2027-02-28 (competitions "normally run
  3-4 months"); competition papers due 2027-04-01; up to three
  leading teams invited into the IEEE Xplore proceedings; organizers
  may submit a competition report. A dry run / readiness review may
  be required before launch. Organizers, co-organizers and their
  direct advisees may not compete.
- Alternative vehicle: regular papers, 6 pages IEEE two-column, due
  **2027-01-31** (one official page says 2027-01-15 for
  workshop-bound papers — re-verify whichever is used).

## What we would actually propose (the only honest candidate)

"Beat the Null": entrants receive the compiled MaleCNS runtime, the
repo's kill-test harnesses (MIT-0 after the ~Nov 1 release), and the
frozen rules of this program — find ANY task, encoder and readout
under which a declared fly circuit beats its degree-preserving rewire
under preregistered bars. The program's 0-for-7 rewire record is the
gauntlet; any winning entry is exactly the falsifier SYNTHESIS.md
says would be the most informative next measurement. Scientific value
is real and symmetric: wins break our synthesis productively, a
silent board hardens it.

## The case against proposing (and it is decisive this cycle)

1. **Operational commitment vs. capacity.** An accepted proposal is a
   Jan-Jun 2027 obligation: platform setup and hosting of multi-GB
   compiled arrays (per AGENTS.md, as versioned release assets — the
   hosting itself is unresolved AP-6-adjacent work), a possible
   readiness review, 2-3 months of live participant support, judging
   against preregistered bars, shepherding up to three teams' papers
   by Apr 1, a competition report, and presence in Cape Town in June.
   This is a team's workload; the program is one person plus
   sessions. Solo organization is also a credibility weakness
   against section (3) of the proposal itself.
2. **Participation risk.** The target community is the intersection
   of connectomics and benchmark practice — small. A launched
   competition with near-zero entries costs reputation that a
   never-proposed one does not. (Participation estimates here are
   EXPECTED-tier guesses, flagged as such; no program base rate exists
   for participation predictions — the 0-for-16 record covers
   score-adjacent claims only.)
3. **Calendar collision.** Proposal work lands Nov (against the
   Kaggle submission, due Nov 8, and release sequence ~Nov 1);
   acceptance/launch land Dec 15-Jan 1, exactly across the Dec 4 ARC
   results and, if placed, the 1-week/2-week winner-obligation
   clocks (AP-13).
4. **The cheap alternative buys most of the value.** The repo goes
   public MIT-0 with the harnesses and SYNTHESIS.md's standing
   falsifier list anyway. Anyone can run "beat the null" the day the
   repo is public; a paper can state it as an open challenge without
   us operating a platform. The competition's unique addition —
   prizes, deadline pressure, proceedings slots — is the part that
   costs six months.

## Recommendation

**NO-GO on the IJCNN 2027 competition proposal.** The format fits
the science, but not this cycle's capacity or calendar, and the
downside of an under-attended competition is worse than the upside
over a public-repo-plus-paper route.

**The better IJCNN vehicle is the regular paper (due 2027-01-31):**
the synthesis is already paper-shaped (six preregistered kill tests,
seven rewire comparisons, the transformation-vs-wiring reading, a
stated falsifier), 6 IEEE pages is the right size, the deadline sits
AFTER the Dec 4 ARC results (so the paper can cite the competition
outcome either way), and it carries zero operational tail. Decision
on that can wait until after Dec 4 with no cost.

**Reconsider the competition format later, under conditions:** if
the ARC paper placement or the public release brings co-organizers,
the natural targets are IJCNN 2028, Telluride 2027 (applications
~Feb 2027, exploratory format fits "find what the wiring does"), or
the CVPR 2027 event-vision workshop windows (Dec 2026-Feb 2027
announcements) — all in the survey's Task 8 list.

## If overridden to GO, the minimum path

Draft the 4-page PDF the week of Nov 10 (after the Kaggle submit):
section 4 is the long pole (hosting plan for the compiled arrays +
license table: MaleCNS CC BY 4.0 attribution, harnesses MIT-0, task
data fetched by entrants under their own licenses); name a platform
(CodaBench is the zero-cost default); recruit at least one
co-organizer before submitting — a solo proposal should not ship.
