# Social and outreach kit

Drafts for publishing FlyGI's results. Nothing here is published automatically;
these are copy for a human to review, fill in, and post.

## Files

| File | Audience |
| --- | --- |
| [FACTS.md](FACTS.md) | **Read first.** Every number allowed in a post, with its source. |
| [VIRALITY_NOTES.md](VIRALITY_NOTES.md) | **Read second.** Why every draft opens with awe rather than the negative result, with citations. |
| [linkedin.md](linkedin.md) | Long form, professional |
| [x.md](x.md) | Single post and a 9-post thread |
| [instagram.md](instagram.md) | 8-slide carousel plus caption |
| [longform.md](longform.md) | Hacker News, Reddit, blog |

An earlier draft set is at [../social_announcement.md](../social_announcement.md);
it predates the controls and is superseded by this directory.

## Placeholders

| Token | Fill with |
| --- | --- |
| `{{BEST_SCORE}}` | The best **completed Kaggle submission** score. Not a local public-set number. |
| `{{BEST_RANK_LINE}}` | One sentence of rank context, or delete. |
| `{{REPO_LINK}}` | Public repo or write-up URL, once one exists. |

> **2026-10-08:** The best completed submission is **0.15** (`56620463` /
> `56650224` / `56683298`), earned by the engineered FAP-archetype scaffold
> with `neuronal_dynamics_active=false`; the only fly content in those runs
> is the compiled static retinotopic eye map. Any draft written in the "fly
> is playing live" voice must be recast to the controlled-run past tense and
> checked against FACTS.md before this number is inserted — pasting 0.15
> into a zero-trainable-parameter full-connectome framing misattributes it.
> (The drafts' openings were recast on this date.)

If the best score is still 0.00, say so. A zero with controls is a stronger
artifact than a small number without them, and the posts are written to work
either way.

## Rules

1. **Every number comes from `FACTS.md`.** If it isn't there with a source, it
   doesn't go out.
2. **Never name another project.** The argument is stronger as "mine included,"
   and a blanket claim that connectome work lacks controls is false — at least
   one published study reported a parameter-matched control that beat its own
   connectome condition.
3. **Never imply zero-shot generality.** Training used public games.
4. **Never revive the retracted efficiency claim.** See `FACTS.md`.
5. **Don't soften the negative result.** It is the contribution, and softening it
   removes the only thing that distinguishes this from a demo. Framing controls
   *order and emphasis*, never what is true.
6. **Don't open with the failure.** The evidence is specific about this: a flat
   negative is low-arousal, the weakest opening there is, and the Pratfall Effect
   only rewards admitting mistakes once competence is established. Awe first,
   real finding second, failures once they have something to land on.
