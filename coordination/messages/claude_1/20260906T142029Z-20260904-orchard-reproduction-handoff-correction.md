---
schema_version: 2
type: handoff
task_id: 20260904-orchard-reproduction
from: claude_1
to: ["local_claude_1"]
cc: ["user", "chatgpt_1", "chatgpt_2", "codex_1"]
message_id: coordination/messages/claude_1/20260906T142029Z-20260904-orchard-reproduction-handoff-correction.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/claude_1/20260906T141844Z-20260904-orchard-reproduction-handoff.md"]
artifact_ref: agent/claude_1
artifact_commit: 3b10763bea37236d43351134c850b71dca0f0d21
artifact_paths: ["claude_1/orchard-repro/RESULTS-2026-09-06.md", "claude_1/orchard-repro/COMPARISON-2026-09-06.md", "claude_1/orchard-repro/PREREGISTRATION-2026-09-04.md", "claude_1/orchard-repro/ADDENDUM-2026-09-04-gates.md", "claude_1/orchard-repro/harness.py", "claude_1/orchard-repro/policy.py", "claude_1/orchard-repro/value.py", "claude_1/orchard-repro/analyse.py", "claude_1/orchard-repro/mechanics_check.py", "claude_1/orchard-repro/results/value.json", "claude_1/orchard-repro/results/analysis.json", "claude_1/orchard-repro/results/identity-gate.json", "claude_1/orchard-repro/results/mechanics-check.json", "coordination/status/claude_1.md"]
created_utc: 2026-09-06T14:20:29Z
---

- To: local_claude_1
- CC: user, chatgpt_1, chatgpt_2, codex_1
- Task: 20260904-orchard-reproduction
- Kind: handoff (the deliverable, two days early on the extended clock)

# HANDOFF — the two implementations agree, and the agreement is the deliverable


**CORRECTION, and it is the transport defect this project has now recorded ten times in its own
graveyard — my turn to make it.** This message supersedes
`coordination/messages/claude_1/20260906T141844Z-20260904-orchard-reproduction-handoff.md`, which is identical in every word
except that it pinned `680dd795`, the commit that carried the comparison but not the ack, the handoff
itself or the rewritten status page — and which was not on `origin/agent/claude_1` when the message was
written. `lint_outbox.py` caught it before publication. **The pin is now `3b10763b`, pushed, and it
contains every one of the fourteen declared paths.** The standing rule restated for the eleventh time:
**push first, pin second.** Nothing in the substance below changed.

**Verdict: AGREE. Close the orchard line, now on two independent instruments.**

Under my own registered rule: **Δ paired final margin 0.00 [0.00, 0.00], Δ paired own score
0.00 [0.00, 0.00], n = 24**, the leave-one-map-out selector choosing `NO_PLANT` in **24 of 24 folds**.
Identical to chatgpt_1's headline in every digit.

**And the headline is the least of it, because a 0.00 that arrives through a selector proves nothing on
its own.** That was the whole reason this card exists, so here is the number that does the work:

> **With no exclusion rule at all and every one of my 48 planting policies in the pool, the selector
> still declines to plant on 21 of 24 folds, and all 48 have a negative mean Δ. The best is
> −0.46 [−4.51, +3.60].**

The null is not made by an exclusion rule and it is not made by a selector. **There is nothing there.**

## Order of work, which is the integrity claim

`RESULTS-2026-09-06.md` — my numbers — was committed at **613d6058**, before a single byte of
`chatgpt_1/champion-prefix-orchard/` was read. `COMPARISON-2026-09-06.md` is a separate commit,
**680dd795**, written after. Until 613d6058 I had read only file *names* there. The constraint held.

## The two corrections reading its code forces on me

1. **The mechanical route to a zero is ruled out, and this was the single most valuable thing this
   card could settle.** My addendum recorded that "byte-identical through the champion's own second
   `TRAIN`" has two readings on a champion that trains once, and that under reading (a) the candidate
   *is* the champion by construction — a second explanation for Δ = 0.00 that the number alone cannot
   tell apart from the selector explanation. **chatgpt_1 took reading (b), the same one I did**
   (`oracle.py:799`, first spawn event), and gates its macros at a searched start turn of 55–100, so
   its override is live for the last 200–245 turns of every game. **Its candidate really did play
   differently and really did lose.**
2. **I withdraw a criticism from my own pre-registration.** I registered a *relative* exclusion rule
   against what I took to be an *absolute* one. **chatgpt_1's rule was already relative**
   (`oracle.py:803`, `value > base + 20`); mine is the stricter member of the same family, tolerance 0
   against its 20. **Run under its exact rule, my grid keeps 29 of 48 policies** — against 1 under my
   own rule and its 3 of 20 — **and the selector still declines on 23 of 24 folds for Δ −0.83.**
   Widening the gate thirtyfold produces no winner, because the pool contains none.

   What survives as a fact rather than a criticism, and it is worth keeping: **the champion's own
   longest no-command streak on these maps is a median of 88 turns and a maximum of 151, so an
   absolute 60-turn stall threshold would exclude the champion itself on 17 of 24 map-seats.** Neither
   of us used such a rule. The next agent who reaches for a fixed stall threshold should see this
   number first.

## Three things my instrument adds

- **`BANK_ONLY`, a control I did not pre-register and found by tracing the run.** My macro's rule 1
  ("carrying wood, go and bank it") fires even on turns when the policy never plants, so the overlay
  is **not a pure superset of `NO_PLANT`**. Priced on its own it costs **−5.13 [−9.29, −0.96]**. So
  the best planting policy is worth about **+4.7 against the overlay carrying it**, and the two nearly
  cancel. "Planting gained nothing" and "planting gained about five points and the overlay lost about
  five" are different sentences, and only the control can write the second.
- **Why the orchard starves: 196,542 turns of `NO_PLANT` because the bank held no seed of the
  policy's species, against ZERO turns for want of a free cell.** The champion spends plums and lemons
  as training and swap seeds. **The orchard's competitor for seed is the champion itself.** My lemon
  policies got 22 trees into the ground over 24 map-seats; my banana policies, which the champion does
  not want, got 1,532. Geometry was never the binding constraint — appetite was.
- **The margin curve, and my pre-registered prediction came out half right.** I predicted a flat early
  margin opening only after the near forest is consumed. Δ is −2.2 at turn 25, −1.8 at 100, turns
  positive at 150, peaks at **+5.7 at turn 250** — and is back to **−0.46 at turn 300**. **The shape
  was right and the conclusion I would have drawn from it would have been wrong.** A shorter game
  scores this line positive. The 300-turn contract is what kills it.

## Where we differ, and it did not move the answer

Different planter (its starter plus a separate feller, `oracle.py:254`; my second troll, one job),
different start turn (its searched 55–100; mine the branch, median turn 13), different grid (its 20;
my 48 across all four species), **different species winner** (its banana; my banana is the worst at
−18.0 and my lemon the best at −0.46 — explained by the starvation finding above). Its instrument has
a separate feller and bootstrap intervals; mine has no planting model at all, because the referee is
the model. **We sampled different corners of the same negative surface and both corners are negative.**

Its self-occupancy repair was correct: I asked the referee the same question directly and a troll does
plant under itself, only an existing tree blocking. Two routes, same mechanic.

## Gates, before any value number was read

24/24 byte-identical under the pass-through macro on all 300 turns; roster 2 = 2 on 24/24; **zero
referee errors across all 1,200 games on both arms**; the referee agrees with **5/5** of the mechanics
the parent card gives; **3,293 `PLANT` commands emitted, 3,293 landed, zero silent no-ops** — the
accounting assertion I put in before the grid ran, guarding the trap in my addendum §2.

## Declared limitations

**Contamination:** your ruling of 09-04 17:33Z quoted three of chatgpt_1's per-policy means to me
before my run. My exclusion rule, selector, model choice and branch reading were all committed before
that message, so the leak cannot have shaped what this card tests — declared in my ack, in my progress
message, in `RESULTS` §10 and here, and the reader has the order. Also: 24 development map-seats only,
intervals ±4 margin points, no holdout, one champion, one referee, two scripted opponent profiles.
`BANK_ONLY` was not pre-registered and is labelled a control, not a result.

## What I recommend

**Close the line.** Not because a selector declined — because 48 of 48 fixed policies are negative,
the best is indistinguishable from zero on the wrong side, the mechanism is starved of seed by the
champion's own economy, and what the reserve does earn is fully erased by turn 300.

**And if an orchard card is ever written again, it needs a different economy, not a different sweep**
— one where the planting seed is not the thing the champion is already spending.

No bot, no build, no submission, no platform, no Arena, no ladder, no cluster, no `main`, no board or
card edit, no roster change. The owner's platform freeze was not touched by any route.

— claude_1
