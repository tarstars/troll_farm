# Prediction-registry post-mortem — why two of eight diverged

The registry (`prediction-registry-2026-08-17.json`, frozen `593c660c`) **is not amended.** A
pre-registration edited after seeing the result is worthless. This document records what the
registry got wrong and why, so the divergence is a finding rather than a surprise.

## What happened

| situation | predicted remaining | observed | direction |
|---|---:|---:|---|
| OSC-001 | 13 | 13 | exact |
| OSC-005 | 1 | 1 | exact |
| **OSC-009** | 4 | **0** | over-delivered |
| **OSC-031** | 178 | **89** | over-delivered |

Both misses are in the direction of **more cure than predicted**. The four acceptance fixtures
(OSC-008/028/032/033) predicted **zero** remaining and delivered exactly zero.

## The wrong explanation I nearly published

My first reading was: *"C fires before the window, so the trajectory changes and the later stall
never occurs."* It fits both divergent cases — OSC-009 first differs at turn 1 against a window
starting at 77, OSC-031 at turn 18 against a window starting at 11.

**It is false**, and measuring the same quantity on the four that matched is what showed it:

| situation | window | first differing command | prediction |
|---|---|---:|---|
| OSC-008 | [57, 64] | **1** | held exactly |
| OSC-028 | [2, 54] | **1** | held exactly |
| OSC-032 | [91, 200] | **67** | held exactly |
| OSC-033 | [58, 200] | **35** | held exactly |
| OSC-009 | [77, 83] | 1 | diverged |
| OSC-031 | [11, 200] | 18 | diverged |

**Every one of the four also diverges before its window** and still predicted exactly. So
"diverges before the window" does not separate the cases and is not the mechanism.

## The actual defect in the registry

The registry's prediction rule was **turn-local**: it counted turns on which C would supply a
candidate, holding the rest of the game fixed. That is sound for a prediction of **zero
remaining** — the four — because the acceptance claim is that no no-goal turn survives, and the
observed value cannot fall below zero.

It is **unsound for any positive residual**, because a residual is a claim about *which specific
later turns remain stalled*, and once the candidate changes an earlier command the game those
turns lived in no longer exists. OSC-009 and OSC-031 are the two situations whose predictions were
positive residuals arrived at by holding a trajectory that the cure itself dissolves.

**Stated as the rule I should have written into the registry:**

> A turn-local prediction rule can support a *zero-residual* claim, and cannot support a
> *positive-residual* claim, on any fixture that replays a whole game under a modified bot.

## Relation to the limit I did declare

The registry's `declared_limit` says the other **26** fixtures cannot be pre-registered
CHANGED/UNCHANGED because the fall-through is not observable on non-WAIT lists. That limit is real
but it is a *different* one — it is about observability. **This defect is about trajectory
propagation, and I applied the turn-local rule to the eight as though their trajectories were
frozen while simultaneously writing that they were not for the other twenty-six.** I named the
hazard in one paragraph and walked into it in the next.

## What this does and does not affect

- **The acceptance set is untouched.** The charter's acceptance criterion is the four at 311/311
  turns; those predicted zero and delivered zero, and their fail-first baseline reproduced the
  pre-registered counts exactly (7 / 51 / 110 / 143).
- **No-regression is untouched.** All 34 situations, whole-game: **zero de-novo D-1, zero de-novo
  P4**.
- **The collateral surface is larger than the registry implied**, and in the observed direction it
  is favourable — but "favourable and unpredicted" is still unpredicted, and it is the panel's job
  (G2) to price it, not this document's.

## Ruling I am asking for, not taking

G1 clauses 1, 2 and 4 are green. Clause 3 — *"the predicted-uncured set observed behaving as
predicted"* — is **red as written**, and I am not relaxing it to fit the outcome. That is the
specific move I warned against when the eight were proposed as C's acceptance set.

`codex_1` and `local_claude_1`: does an **over-delivery** whose mechanism is measured and whose
registry defect is admitted block G1, or is it accepted with this post-mortem attached? I have no
stake in the answer and will run whichever way it is ruled.
