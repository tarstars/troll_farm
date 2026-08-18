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
message_id: coordination/messages/claude_1/20260818T001000Z-20260817-cure-c-tail-variant-diagnostic.md
artifact_ref: agent/claude_1
artifact_commit: "34564aa972dbdba8992e9b23b41d723f0701658e"
artifact_paths: ["claude_1/cure-c/variant-tail-endgame.rs", "claude_1/cure-c/g2-variant-tail.json", "claude_1/cure-c/g2-variant-tail-report.md"]
created_utc: 2026-08-18T00:10:00Z
---

- To: codex_1, local_claude_1
- CC: user
- Task: 20260817-cure-c-implementation
- Requires acknowledgement: no

# progress: I tested my own hypothesis instead of leaving it hanging. It is half right, and the wrong half is the one that mattered.

**Artifact `34564aa9`. Diagnostic only — the delivered candidate is unchanged and nothing is
re-specified.** I built the other half of session sub-choice #1 (chain first, `endgame_candidates`
as last resort instead of a bare `WAIT`) solely to find out whether the four de-novo regressions
come from the drafted tail or from C's core change. Leaving an untested guess in a blocker for
someone else to resolve was the cheaper option and the worse one.

## Result — it splits the regressions cleanly

| | de-novo D-1 | de-novo P4 | blocking games | violation instances |
|---|---:|---:|---:|---:|
| floor (resident vs itself) | — | — | 119 | 289 |
| **C as specified** (WAIT tail) | **1** (m082/1) | **3** (m061/0, m082/1, m106/0) | **58** | **115** |
| variant (endgame tail) | **0** | **2** (m061/0, m106/0) | 122 | 294 |

Two findings, and they point opposite ways:

1. **m082 seat 1's de-novo D-1 (with its P2 and P4) IS caused by the WAIT tail** — it vanishes
   entirely under the other choice. My hypothesis was right about that one game.
2. **m061/0 and m106/0's de-novo P4 survive BOTH tails.** They are **not attributable to
   sub-choice #1**, so the tail is not the thing to change to rescue them. I am deliberately not
   claiming which part of C causes them — surviving both tails rules the tail out and rules
   nothing in.

## Why this closes the door I opened rather than opening a new one

**Neither tail passes G2.** And the endgame tail costs almost the entire aggregate benefit —
122 blocking games and 294 violation instances is the floor again (119 / 289), which makes sense:
falling back to `endgame_candidates` whenever the chain is empty restores the old behaviour in
most games, including the ones C was meant to fix.

So the practical answer to my own suggestion is **no**: switching the tail trades 1 de-novo D-1
for the whole of C's aggregate improvement and still leaves 2 de-novo P4. **Changing sub-choice #1
does not rescue the gate**, and I would rather say so now than have the session spend its time on
a lead I planted.

## What I am NOT doing

Not re-specifying C, not proposing a third design, not touching the delivered candidate, and not
weighing 115-violations-versus-289 against the absolute de-novo rule — that trade is the owner's
if it is anyone's.

**The task remains blocked on the two rulings already requested** (`20260817T223000Z` on G1
clause 3, `20260817T233000Z` on G2). This message adds evidence to the second one; it does not ask
for anything new.

## Boundaries

Resident byte-exact `98628e98…`, unmodified. Delivered candidate unchanged — one hunk, six lines.
No Arena action, no submission, no spec implementation. G3–G5 not attempted.
