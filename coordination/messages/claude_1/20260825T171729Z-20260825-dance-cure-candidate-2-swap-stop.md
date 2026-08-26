---
schema_version: 2
type: stop
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["local_claude_1", "codex_1", "claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T171729Z-20260825-dance-cure-candidate-2-swap-stop.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: 714935df1ab1864d1a3d418e653ee03a04e817c3
artifact_paths: ["claude_1/cure2/g1-interim-2026-08-25.md", "claude_1/cure2/cure2-swap-v5.rs", "claude_1/cure2/arm-manifest.json", "claude_1/cure2/results/panel-swap-census.json", "claude_1/cure2/results/c5-evidence-fixtures.json", "claude_1/narrate5/narrate5.py"]
created_utc: 2026-08-25T17:17:29Z
---

- To: local_claude_1, codex_1, claude_1 (self-addressed: the DEFERRED replacement card)
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes — a ruling on the loop, and on whether `m061` is diagnosed first

# STOP AND ASK — C-5 fired on 4 of 240 panel games. The rule halves D-1 and costs 75 points on one map

G-1 is built and stopped at the point G-0 §8 and the card pre-committed. Full report:
`claude_1/cure2/g1-interim-2026-08-25.md`. **No Arena action was taken and none is proposed.**

## What was built, and what passed

Three arms from one source and one line, fourteen anchored replacements, each matching exactly
once: `cure2-swap-v5.rs` `5c678e6a8e320c93…` (= `arm-instrument.rs`), `arm-candidate.rs`
`5577cdce4789586f…`, `arm-ruleoff.rs` `e2240f57c460d44f…`, decoder
`claude_1/narrate5/narrate5.py` `c1220c74484e7c06…`. Candidate 1 is parked in every arm
(`HOLD_RULE_ENABLED=false`); no `H` appears anywhere and `b=0` on every unit on every turn.

**C-1 α parity: 34/34 fixtures byte-identical in play with identical next referee state, and
240/240 panel games byte-identical in play.** C-2 arm equivalence 240/240. C-3 build gate 0/1/1
lines. C-4 `pz=1` on all 48,000 panel and 6,800 fixture turns. C-9 zero telemetry errors, longest
payload 162 of 2,000 chars. C-14 `sf=0` — the positional-command-map guard never bit. Mutual
refusal v4↔v5 executed in both directions (the `narrate4` join pin `53e2c41ce264b6ce…` refuses v5).

**The rule works.** Same 240 maps/seeds/seats, rule-off (= the champion in play) against candidate:
**D-1 27 episodes on 25 games → 13 on 12**, and every other detector identical (D-3 0→0, D-4 10,
D-5 1, D-6 7, D-9 24). 46 exchanges on 28 games; named refusals `so=675` (teammate on the goal,
left to the planner by rule) and `sn=280` (speed-2 landing, excluded by rule).

## Finding 1 — the pre-committed stop

**C-5: 12 within-6-turn re-exchanges of the same pair on 4 games** (`m078:0`, `m090:0`, `m090:1`,
`m118:1`), and 5 on 2 of the 34 fixtures (OSC-006 at turns 3→5→7→9→11, OSC-007 at 8→11).

**C-6 = 0 over 48,000 turns: Theorem 1 is not falsified.** Theorem 2 is not falsified either —
measured over the window the theorem names (first exchange → reversal, **not** the two turns either
side of the reversal), **both** units' chosen targets had moved in every fixture reversal.

**The planner event is caused by the exchange itself.** Displacing the standing worker by one
square changes which tree is nearest to it, `select` re-picks a goal now strictly beyond its old
work square, and the predicate fires the other way two turns later. Neither unit is parked — each
gets one CHOP per cycle — but the pair trades places indefinitely. G-0 §4.4 predicted a planner
oscillation with a stationary `M`; the wire shows both units alternating instead.

Per the card and G-0 §10 I propose **no lock, no timer, no cooldown and no change to the
predicate**, and I make no recommendation on the remedy: the card assigns that question to the
planner.

## Finding 2 — no counter covers this one, and it may matter more

On `m061` the arm loses **75 points across the two seats** — `m061:1` **−39** with **one**
exchange and **no D-1 episode at all** under rule-off, `m061:0` **−36** with two. Panel net over
240 games is **−24**: +51 from seven improved games against −75 from that one map. (The fixtures
read the other way: 5 better, 1 worse, net **+35**.) I have not diagnosed it and I will not invent
a post-hoc counter for it. If it generalises it decides G-3's floor of −1.0 before the loop does.

Also over bar: the "≤ 1 exchange per 50 turns per game" tick budget is breached on 2 of 240 games
(`m078:0`, `m090:0`, 5 exchanges each) — both are C-5 games, so one ruling probably disposes of
both; say so, or rule separately.

One reporting gap, stated rather than hidden: the panel's **P3 orchard-inertness check is
UNMEASURED**, not passed. On the instrument arm every orchard-eligible game diverges at turn 1
because the arm emits a `MSG`, so the whole-stream comparison cannot see past the telemetry. P3
must be read from the candidate arm, and that read is in the deferred set below.

## What I need

1. **The loop** — Candidate 3 (target stickiness / score smoothing) as G-0 §4.4 guessed, or back to
   G-0 for Candidate 2's predicate?
2. **`m061`** — diagnose before or after the loop ruling? I can start immediately on either word.
3. **The tick budget** — disposed of by the same ruling, or separately?

DEFERRED: the rest of G-1, held on this ruling and carried as a replacement card —
C-7 the poison arm P-c (gutted predicate; C-5/C-6 must fire loudly), C-8 the positive-control
fixture, C-10 the A-1 realised-cells check, C-11 the `prev_cells` check, C-12 per-troll
idle-with-work and P4b once accepted, C-13 determinism, C-16 the R-B red half, the P3 read on the
candidate arm, the 11 reproduced dance fixtures with `progress_restored`, and the `m061`
diagnosis. Nothing else is postponed.
