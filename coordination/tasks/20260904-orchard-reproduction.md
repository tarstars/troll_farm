# Task 20260904-orchard-reproduction — measure the champion-prefix orchard again, from scratch, without looking

- **Born:** 2026-09-04 17:1xZ, the moment chatgpt_1's result landed. Pre-committed on
  `20260904-champion-prefix-orchard.md` §7 the day it was chartered — **this is not a reaction to the answer.**
- **Work owner:** **claude_1.** Verifier: the coordinator, by execution.
- **Kind:** **a second, independently written implementation of one measurement.** No bot, no ladder, no platform.
- **Budget:** one implementation, **two days, to 2026-09-06 17:00Z.**

---

## 1. The one condition that makes this worth doing

**Do not read chatgpt_1's implementation before your own produces a number.**

Off limits until you have your own result written down: `chatgpt_1/champion-prefix-orchard/oracle.py`,
`policies.json`, `finalize.py`, `repair_self_target.py`, `results/`, `RESULTS.md`, `FINAL.md`. You may read the
**charter** (`20260904-champion-prefix-orchard.md`), the referee, the champion source and the map records — the same
inputs it had.

If you read any of it by accident, **say so in your handoff.** A contaminated reproduction reported honestly is worth
something; a contaminated one reported as clean is worth less than nothing.

## 2. What to measure — the same experiment, restated from the charter only

```text
A (baseline):  unchanged champion ────────────────────────────────────────► turn 300
B (candidate): unchanged champion through its own second TRAIN
               → searched near-orchard macros
               → continuously advanced shadow champion ────────────────────► turn 300
```

The champion is the executable in **both** arms. Every candidate command stream must be **byte-identical through the
champion's own second `TRAIN`**, and the second troll's specification and turn must never change. **Third training is
disabled. `NO_PLANT` is always legal.** Same maps, seats, starts, opponent scripts and seeds on both arms.

Report **Δ paired final margin** and **Δ paired own score**, each with a 95 % interval and n; the policy your search
actually chose and how often it chose `NO_PLANT`; and **your action vocabulary, published** — every action the search
could take, listed.

**Mechanics before value, on both arms independently.** No value number is read until both arms run clean and the
prefix is verified identical.

## 3. The three places the two implementations are most likely to disagree — look here first

You are not hunting for a different answer. You are testing whether the answer depends on choices an implementer had
to make. These are the choices:

1. **The mechanics exclusion rule.** chatgpt_1 evaluated 20 planting policies and **excluded 17** because they
   introduced a new long-inactivity interval. That is a large fraction, and the exclusion threshold is a judgement
   call that sits directly upstream of the result. **Define your own rule, state it before you run, and report how
   many policies it excludes.** If your rule keeps policies its rule dropped, say what they score.
2. **The selector.** Its registered selector was leave-one-map-out across 24 development map-seats, and it chose
   `NO_PLANT` in **all 24 folds** — which is why its Δ is exactly 0.00. A cross-map selector that can only choose one
   policy for all maps is a strong constraint. **State your selector before you run it**, and report what a per-map
   choice would have given as an explicitly-labelled hindsight upper bound, never as a result.
3. **The planting model itself** — self-occupancy of the planting cell, growth release, raid, felling, carry and
   banking. chatgpt_1 found and fixed a self-occupancy bug in its own instrument mid-run. **Write your own; do not
   inherit its fix**, and check that your model reproduces the referee on a handful of planted-tree cases before you
   trust any aggregate.

## 4. Done means

One page, plain words, with: your Δ figures and intervals; your action vocabulary; your exclusion rule and its
count; your selector; **and a direct comparison to chatgpt_1's numbers, which you read only after your own are
written down.** Then say plainly whether the two implementations agree.

**Agreement is the deliverable, not a positive result.** Two independent implementations both finding nothing is a
strong, publishable answer and closes the line cleanly. Two disagreeing is a more interesting one and tells us the
result was an implementation artefact.

## 5. Dead means

**If you cannot build a planting model you can show reproduces the referee, stop and say so** rather than shipping an
aggregate you do not trust. That is a real outcome and it is worth more than a number nobody can stand behind.

## 6. What this card must not do

- **No bot, no submission, no platform, no Arena, no ladder** — the owner has frozen the platform entirely
  (*"don't publish programs on platform until I say you can"*, policy `20260904T140500Z`).
- **No third troll, no roster change, no altered second troll.** The roster question is closed four ways.
- **No tuning of anything against the development maps.** You are measuring, not searching for a win.

## 7. Why this still matters now the answer is "nothing"

chatgpt_1's result is a clean null: the pre-registered selector chose `NO_PLANT` in all 24 folds, so the candidate
*is* the champion and Δ is exactly 0.00 by construction. **A null that arrives by that route is exactly the kind that
deserves a second pair of hands** — it can be produced either by the mechanism being absent or by an exclusion rule
and a selector that never gave the mechanism a chance. Its own hindsight oracle chose an orchard on **16 of 24 maps**,
which it correctly refused to claim as a result. Whether that gap is real generalisation failure or an artefact of one
implementation's choices is precisely what a second implementation answers.

This is the same protocol that made the stage-2A field reading trustworthy, when two agents agreed to the digit.

## Log

- 2026-09-04 17:1xZ chartered to claude_1 on delivery of chatgpt_1's result, as pre-committed. — coordinator
