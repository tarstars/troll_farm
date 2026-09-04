---
schema_version: 2
type: handoff
task_id: 20260904-orchard-reproduction
from: local_claude_1
to: ["claude_1"]
cc: ["user", "chatgpt_1", "chatgpt_2", "codex_1"]
message_id: coordination/messages/local_claude_1/20260904T172000Z-20260904-orchard-reproduction-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 9203949297574edb2edc5c0016adb54673e2a80a
artifact_paths: ["coordination/tasks/20260904-orchard-reproduction.md", "coordination/tasks/20260904-champion-prefix-orchard.md"]
created_utc: 2026-09-04T17:20:00Z
---

- To: claude_1
- CC: user, chatgpt_1, chatgpt_2, codex_1
- Task: 20260904-orchard-reproduction (new card)
- Kind: handoff (the charter — your reproduction assignment is live)

# CHARTER — measure it again, from scratch, without looking

chatgpt_1's result landed at 14:40Z. **Your assignment is now live**, exactly as you accepted it at `20260904T133857Z`
and as the parent card pre-committed on the day it was written — **so this is not a reaction to the answer.**

**Two days, to 2026-09-06 17:00Z. No bot, no ladder, no platform.** Card at the pin above.

## The condition that is the entire point

**Do not read chatgpt_1's implementation until your own number exists.** Off limits:
`chatgpt_1/champion-prefix-orchard/oracle.py`, `policies.json`, `finalize.py`, `repair_self_target.py`, `results/`,
`RESULTS.md`, `FINAL.md`. **In force:** the parent charter, the referee, the champion source, the map records — the
same inputs it had. If you read any of it by accident, **say so in your handoff**; a contaminated reproduction
reported honestly is worth something, one reported as clean is worth less than nothing.

## What you are reproducing

The champion is the executable in **both** arms; every candidate command stream **byte-identical through the
champion's own second `TRAIN`**; the second troll's specification and turn never change; **third training disabled**;
**`NO_PLANT` always legal**; same maps, seats, starts, opponent scripts, seeds. Report **Δ paired final margin** and
**Δ paired own score** with 95 % intervals and n, the policy chosen, how often `NO_PLANT` won, and **your action
vocabulary published**. Mechanics clean on both arms before any value number is read.

## The answer you are checking against — you may know this much

chatgpt_1 reports a **clean null**: `Δ final margin 0.00 [0.00, 0.00], n=24`, because its pre-registered
leave-one-map-out selector chose `NO_PLANT` in **all 24 folds**, so its candidate *is* the champion. Dead condition 3
triggered and row 3-8 is closed.

**I am telling you the answer deliberately**, because hiding it would not make your implementation more independent —
you would find it in the graveyard — and because the useful question is no longer "what is the number" but **"does
that number depend on choices an implementer had to make?"**

## The three places to look, which are the three choices it had to make

1. **The mechanics exclusion rule.** It evaluated 20 planting policies and **excluded 17** for introducing a new
   long-inactivity interval. That is a large fraction sitting directly upstream of the result. **Define your own
   rule, state it before you run, report how many it excludes** — and if yours keeps policies its rule dropped, say
   what they score.
2. **The selector.** A cross-map selector that must pick one policy for all maps is a strong constraint, and it is
   why Δ is exactly 0.00 *by construction* rather than by measurement. **State your selector before you run it.**
   Report a per-map choice only as an explicitly-labelled hindsight upper bound — its own hindsight oracle chose an
   orchard on 16 of 24 maps and it correctly refused to claim that, and so must you.
3. **The planting model** — self-occupancy of the planting cell, growth release, raid, felling, carry, banking. It
   found and repaired a self-occupancy bug in its own instrument mid-run. **Write your own; do not inherit that fix**,
   and show your model reproduces the referee on a few planted-tree cases before trusting any aggregate.

## What "done" looks like

**Agreement is the deliverable, not a positive result.** Two independent implementations both finding nothing is a
strong answer that closes the line cleanly. Two disagreeing is more interesting and tells us the result was an
implementation artefact. Either way: your numbers first, then read its files, then a direct comparison and a plain
statement of whether you agree.

**Dead means:** if you cannot build a planting model you can show reproduces the referee, stop and say so rather than
shipping an aggregate you do not trust.

## Two standing rules that now bind you

- **The owner froze the platform** (policy `20260904T140500Z`): *"don't publish programs on platform until I say you
  can."* No submission, by any route, by anyone.
- **No third troll, no roster change, no altered second troll** — closed four independent ways.

Your planting geometry from the closed kinetics read is an input to the parent card and remains yours.

— the coordinator
