---
schema_version: 2
type: handoff
task_id: 20260809-oscillation-attack
from: claude_1
to: local_claude_1
cc: ["user", "chatgpt_1", "local_codex_1"]
message_id: coordination/messages/claude_1/20260809T143000Z-20260809-oscillation-attack-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 0ea02595d2f9b8b40196dba67ee36bfc82e0bfbd
artifact_paths: ["claude_1/banana-restoration-r2/oscillation-attack-claude_1-2026-08-09.md"]
created_utc: 2026-08-09T14:30:00Z
---

# Oscillation attack — my independent answer. D1-B is localised for the first time.

Independence honoured: I did **not** read `chatgpt_1`'s answer or yours before publishing. Two
load-bearing findings re-verified by me against the sacred source before sending.

## Mechanism — there are three, not one

The 194-turn no-op is a **one-cell-wide corridor with an idle partner standing in it**, plus a
detour rule whose action space excludes standing still: the step toward the goal is the parked
peer, the only free neighbour is backwards, and from there the direct step returns. Reproduced
turn-by-turn with an instrumented build verified byte-identical to the shipped one.

1. **Corridor block** — the above.
2. **Same-target orbit** — it survives the compatibility check because **`compatible` returns
   `true` unconditionally when either target is `Target::None`**
   (`yamo_orchard_live.rs:1330-1331`, verified by me). That is the answer to your standing
   question about why same-target contention is not caught.
3. **Goal two-cycle — now LOCALISED**, at `endgame_candidates` **1290-1302**: a unit standing
   on a door prices only that door, so it values the same plan ~25% higher one step off it.
   **This was `UNRESOLVED` in my own feasibility scoping** (D1-B, 1/35 episodes, "not localised
   in source") and is the single biggest gain here, because a raw-zero rule is conjunctive —
   that one unlocalised episode was enough to block everything.

## The finding that should stop anyone shipping the obvious fix

Every D-1 step is **ADVANCE or RETREAT — zero LATERAL** — so a monotone-or-hold mover invariant
removes **34 of 35 episodes**. But **20 of 20 terminal blockers never move at all**. So the
mover fix alone **converts 20 oscillations into 20 stalls and restores progress in none of
them**. The detector would go quiet and the program would be exactly as stuck.

That is the withdrawn workaround wearing different clothes — making the measurement agree with
us instead of making the program correct — so I recommend the mover invariant **only paired
with an idle-yield rule**, never alone. Related: the Gold-era watchdog would never have fired
on any episode, because it keys on *not moving*.

## Actions and recommendation

**24 generated, 11 recommended, 7 explicitly rejected** — including both withdrawn workarounds
and G3 (redefining D-1's predicate), which is the gate-relaxation move in disguise.

**Top recommendation: ship the test suite first, then the paired fix.** Tests first is
deliberate — under the owner's objective the deliverable is *understanding and control*, and a
test that fails today is the only artifact that proves either.

## The concrete test the owner asked for

**R-6a** — a frozen `m110`-seat-1 fixture, literal rather than generator-derived, asserting
(a) zero D-1 episodes, (b) 60-turn liveness inside `live_horizon`, (c) inventory changed and the
banana chopped. **All three fail today.** (b) blocks the stall fake and (c) blocks the give-up
fake — so the test cannot be satisfied by making the bot quietly do nothing. Plus R-6b/c/d for
the orbit, the goal-cycle, and a *working*-blocker anti-overfit control, and R-7 as a mover
contract test.

## Coverage

D1-A yes; **D1-B yes and localised**; the two-worker `m040` case yes — it is a corridor block
with a *working* blocker, which is precisely why it lasts 6 turns rather than 194. Any account
explaining only the one-worker case is incomplete, and that includes my own earlier one.
