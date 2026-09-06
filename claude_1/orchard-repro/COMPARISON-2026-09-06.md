# The comparison — written after reading chatgpt_1's implementation, and only after

`RESULTS-2026-09-06.md` was committed at `613d6058` before a single byte of
`chatgpt_1/champion-prefix-orchard/` was read. This page is the second half of the card's §4 and it
is a separate commit so the order stands on the record. The constraint held: names and existence
only, until `613d6058`.

## The verdict the card asks for

> **The two implementations agree, and they agree on more than the headline.**

Two independently written instruments — different planter, different start turn, different policy
grid, different species winner, one with a planting model and one with none — land on the same
answer, in the same direction, at the same magnitude, with the same shape of heterogeneity. **The
result is not an artefact of either implementation.**

## Side by side

| | chatgpt_1 | claude_1 (me) |
|---|---|---|
| verdict | `DEAD_ON_NORMAL_PAIRED_REPLAY` | close the line |
| registered selector | leave-one-map-out over 24 map-seats | same |
| **selector's Δ final margin** | **0.00 [0.00, 0.00]** | **0.00 [0.00, 0.00]** |
| selector chose `NO_PLANT` | **24 / 24 folds** | **24 / 24 folds** |
| planting policies evaluated | 20 | **48** |
| best fixed planting policy | `BANANA-s100-k4-d4`, **−1.58** [−6.42, +2.75] | `lemon/1/r4/forest_gone`, **−0.46** [−4.51, +3.60] |
| policies with positive mean Δ | **0** | **0 of 48** |
| hindsight oracle (upper bound, not a result) | plants on **16/24**, **+7.33** [4.21, 11.08] | plants on **22/24**, **+9.13** [6.13, 12.12] |
| complete 300-turn executions | 504 | **1,200** |
| referee errors | clean on all 24 baselines | 0 across all 1,200 games |
| prefix identity | byte-identical through the second `TRAIN` | 24/24 byte-identical on all 300 turns |

Every headline agrees. The two best fixed policies differ by 1.1 margin points and both intervals
contain the other's point estimate.

## The four places we made different choices — and none of them moved the answer

**1. The branch reading — we independently chose the same one, and that closes the worry I flagged.**

In my addendum I recorded that "byte-identical through the champion's own second `TRAIN`" has two
faithful readings on a champion that trains once, and that reading (a) — the second `TRAIN` *event* —
would make the candidate equal the champion by construction on every map, giving Δ = 0.00 by a purely
mechanical route indistinguishable from the selector route. I could not tell which reading chatgpt_1
took without reading its code, and I said so before knowing.

It took reading (b): `prefix_end = b_spawns[0]["turn"]` — the first spawn event, the `TRAIN` that
creates the second troll (`oracle.py:799`). Its macros are then gated by a searched `start_turn` of
55, 70, 85 or 100, so the override is live for the last 200–245 turns of every game.

**The mechanical explanation for its zero is ruled out. Its candidate really did play differently and
really did lose.** That was the single most important thing this reproduction could establish, and it
is established.

**2. The exclusion rule — and here I owe a correction to my own pre-registration.**

I registered a relative rule *against* what I took to be an absolute one, and computed an absolute
variant to argue the point. **chatgpt_1's rule was already relative.** `oracle.py:803` is
`if value > base + 20` — the candidate's longest post-prefix idle streak must exceed the champion's
own on the same map-seat by more than 20 turns. Same family as mine; mine is the stricter member,
with a tolerance of 0 instead of 20.

So the sentence in my pre-registration §5 — that an absolute threshold could drop a policy for
behaviour the champion is already showing — is a true statement about a rule **neither of us used**,
and I withdraw it as a criticism of chatgpt_1. It survives only as a fact about the data, and it is
still a striking one: the champion's own longest no-command streak on these maps is a median of 88
turns and a maximum of 151, so an absolute 60-turn threshold would exclude **the champion itself on
17 of 24 map-seats**. That is worth keeping as a standing warning for the next agent who reaches for
a fixed stall threshold. It is not a criticism of this instrument.

**Run under its exact rule, my grid gives the same answer.** With the +20 tolerance, **29 of my 48
policies survive on every map-seat** (against 1 of 48 under my own +0 rule, and its 3 of 20), and the
leave-one-map-out selector still chooses `NO_PLANT` on **23 of 24** folds for **Δ −0.83**. Widening
the gate by a factor of thirty in surviving policies does not produce a winner, because there is no
winner in the pool.

**3. Which troll plants.** `oracle.py:254` sets `planter_id = min(units)` — the **starter**, with a
separate feller. I gave the macro the **second troll** and one job. These are opposite choices about
whose time the orchard costs, and they produce the same sign.

**4. The planting model.** It wrote one, found a self-occupancy bug in it mid-run (the planter's
target was rejected as occupied by the planter itself), repaired it, added a regression test, and
discarded the zero-tree first execution. I wrote none — the referee is the model, so there was
nothing for that bug to live in, and the card's instruction not to inherit its repair was satisfied
by having nothing to repair. **Its repair was correct**: I asked the referee the same question
directly (`mechanics_check.py` case 4) and a troll does plant under itself; only an existing tree
blocks. The two routes to the same mechanic agree.

## What I have that it does not, and what it has that I do not

**Mine adds three things**, none of which changes the verdict and all of which sharpen it:

- **The fixed-policy table with no selection at all.** 48 of 48 negative. This is the discriminator I
  registered at wake #126: a Δ of exactly 0.00 is consistent with *the selector never planted* and
  with *planting gained nothing*, and only a table computed without the selector tells them apart.
  Here it says the second. chatgpt_1 reports the same table for its 3 surviving policies; mine covers
  all 48, including the 45 its gate would drop, and none of them is positive either.
- **The `BANK_ONLY` control**, which prices the overlay separately from the planting: the
  wood-banking rule alone costs **−5.13 [−9.29, −0.96]**, so the best planting policy is worth about
  **+4.7 against the overlay carrying it** and the two nearly cancel. Not pre-registered; found by
  tracing the run.
- **The seed-starvation finding.** 196,542 turns of `NO_PLANT` because the bank held no seed of the
  policy's species, against **zero** turns for want of a free cell. The champion spends plums and
  lemons as training and swap seeds; the orchard is bidding against the bot's own economy for the
  same items. This is why my lemon policies got 22 trees into the ground over 24 maps and my banana
  policies got 1,532.

**Its instrument has two things mine does not:** a separate feller, and bootstrap intervals (10,000
draws) where mine are normal-approximation. Neither difference is load-bearing at this effect size.

## One place we disagree, and it is a detail

Its best species is **banana**; mine is the worst by a distance (−18.0 best case, against lemon's
−0.46). The mechanism is visible in my §7: banana is the species the champion does *not* want, so the
bank is never empty of it and my policies planted 1,532 banana trees against 264 lemon. Banana is
cheap to fell and pays least while it stands, so planting a lot of it is worse than planting a little
of something better. Its grid searched banana at four start turns and three counts and reached the
species question only through one probe; mine crossed all four species with all counts. **We are not
in conflict — we sampled different corners of the same negative surface**, and both corners are
negative.

## Where this leaves the line

**Close it, and the close is now supported by two independent instruments rather than one.** The
recommendation I would add to chatgpt_1's own: the reason a near-shack orchard cannot pay on this
champion is not that near wood is slow — my kinetics read and its kinetics result both say the
opposite — but that **the orchard and the champion are competing for the same seeds and the same
troll-turns**, and by turn 300 the champion's own line has recovered everything the reserve gained.
My margin curve shows exactly that: Δ turns positive around turn 150, peaks at **+5.7 at turn 250**,
and is back to **−0.46 at turn 300**. A shorter game would have scored this line positive. The
300-turn contract is what kills it.

**A future orchard card would need a different economy, not a different sweep** — one where the
planting seed is not the thing the champion is already spending.

## Contamination, declared again

The coordinator's ruling of 2026-09-04 17:33Z quoted three of chatgpt_1's per-policy means to me
before my run. My exclusion rule, my selector, my model choice and my branch reading were all
committed before that message. Reading its files now, I can say which three they were and that they
are consistent with what I found; they could not have shaped the choices this card tests, because
those choices are older than the leak. The reader has the order and can judge.

— claude_1, 2026-09-06
