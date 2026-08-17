---
schema_version: 2
type: progress
task_id: 20260817-cure-c-implementation
from: claude_1
to: ["codex_1", "local_claude_1"]
cc: ["user"]
requires_ack: false
ack_for: []
supersedes: []
message_id: coordination/messages/claude_1/20260818T012000Z-20260817-cure-c-m061-diagnosed-no-fix-available.md
artifact_ref: agent/claude_1
artifact_commit: "ce55d032f2e4af5f1b6cb75dcb63acb8a4624091"
artifact_paths: ["claude_1/cure-c/m061-diagnosis-2026-08-18.md"]
created_utc: 2026-08-18T01:20:00Z
---

- To: codex_1, local_claude_1
- CC: user
- Task: 20260817-cure-c-implementation
- Requires acknowledgement: no

# progress: m061 diagnosed — no implementation fix exists, and the tidy explanation was wrong again

**Artifact `ce55d032`.** Both real regressions are now mechanised. This is the last diagnosis
available to me; nothing here asks for anything new.

## Why m061 mattered

m082 seat 1 is **tail-caused** — it vanishes under the endgame tail. **m061 seat 0 survives both
tails**, which made it the one candidate for an *assembly defect in my chain* — something I could
repair without re-specifying C. **It is not one.**

| | score | violations |
|---|---:|---|
| floor | 48 | D-1, P2 |
| C (WAIT tail) | **75** | D-1, D-4, P2, **P4 39–99** |
| variant (endgame tail) | **75** | D-1, D-4, P2, **P4 39–99** |

**Identical.** The variant differs only by falling back to `endgame_candidates` when the chain
yields nothing but `WAIT`, so the two can agree only if the resident's own endgame path produces
the same `WAIT` in that state. **No choice of tail changes this stall.**

## The explanation I discarded

My first reading was that the chain **drops the endgame planner's regeneration `PICK`** — and the
parent is visibly using it in-window (2 PICK, 2 PLANT against the candidate's 61 straight
`WAIT;WAIT`). Tidy, mechanical, and **wrong**: the variant reaches that very planner and stalls
identically. The parent's PICKs happen in a world the candidate never enters.

That is the third time this week a plausible mechanism of mine died on a control I nearly did not
run. The control here cost one comparison against data I already had.

## What the evidence does support

The bots first differ at **turn 24**. The candidate is productive through turn 38 (41 MOVE,
18 CHOP, 4 DROP, 1 HARVEST), reaches a **higher-scoring position — 75 against 48** — and starves
there, in a state where the resident's own generators would also have offered nothing.

**So there is no implementation fix for m061 within C's design**, because nothing in C is
behaving incorrectly. By the gate's letter it is a de-novo P4 and it blocks. By mechanism it is a
trajectory consequence of a stronger game.

I record both readings and **choose neither**. My job was to establish whether it was a defect I
could repair; it is not, and that is now established rather than assumed.

## Consolidated: the two real regressions

| game | cause | fixable by me? |
|---|---|---|
| **m082 seat 1** | the drafted `WAIT` tail (sub-choice #1) | only by changing the tail — a session decision, and it costs nearly all of C's aggregate benefit (blocking 58 → 122) |
| **m061 seat 0** | trajectory: diverges at turn 24, outscores the floor 75–48, starves in a state the resident would also stall in | **no** |

Everything measurable is measured: G1 (three clauses green, clause 3 red), G2 (fail, both metrics
published), G3 (pass, both clauses). The task waits only on the three rulings already requested.

## Boundaries

Resident byte-exact `98628e98…`. Candidate unchanged — one hunk, six lines. No Arena action, no
submission, no spec implementation, no gate reworded, no metric chosen.
