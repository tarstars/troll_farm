---
schema_version: 2
type: handoff
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["codex_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260817T134952Z-20260815-banana-farm-two-specs-v12-handoff.md
requires_ack: true
ack_for: ["coordination/messages/codex_1/20260817T122100Z-20260815-banana-farm-two-specs-v11-handoff-ack.md", "coordination/messages/claude_1/20260817T121300Z-20260817-spec-v11-ack.md"]
supersedes: ["coordination/messages/local_claude_1/20260817T120524Z-20260815-banana-farm-two-specs-v11-handoff.md"]
artifact_ref: agent/local_claude_1
artifact_commit: 87245f4643c88bd38063341411e96095a6e042b2
artifact_paths: ["docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md", "docs/superpowers/specs/2026-08-15-banana-farm-spec-b-conditional.md"]
created_utc: 2026-08-17T13:49:52Z
---

- To: codex_1 (**QUEUE NOTE: review AFTER your pool-#2 verdict — do not preempt**), claude_1 (informational)
- CC: user
- Task: 20260815-banana-farm-two-specs (v12)
- Requires acknowledgement: yes (codex_1, after pool #2)

# handoff: Spec v12 — your two v11 executable definitions; explicitly SECOND in your queue

Artifact `87245f46`; shared skeleton §3–§8 re-verified byte-identical; five owner
rulings untouched. Per the queue reassertion published alongside this message, **do
not open this before your pool-#2 verdict is out** — it can wait and says so in its
own status line.

1. **The transition table is ENUMERATED against the referee tick**
   (`rust/src/game/engine.rs:148–185`): T1 cooling (cooldown −1), T2 growth step
   (size +1 AND health + exact kind slope AND cooldown reset to effective), T3 fruit
   step (at max size: fruits +1 AND reset) — each composable with health decreases
   (chops, either side, identity kept) and fruit decreases (harvests, identity
   kept). Everything else — kind change, size decrease or jump ≥ 2, off-slope health
   increase, off-max or jumped fruit increase, out-of-place cooldown increase,
   absence, absence-then-presence — ends the identity permanently. No "consistent
   growth" recursion remains.
2. **The trace schema is fully explicit:** every per-turn row carries the machine
   phase, commitment kind AND target, the suppression event's join identity, branch,
   candidate summary, and the final post-conflict emitted command; the terminal row
   is mandatory — **a trace missing its terminal row is VOID and a panel error**, on
   top of the per-field fail-closed rule.

## For the owner, in plain words

The last two vague phrases in your rule books are now exact: "the same tree" is
defined by the game engine's own three legal changes per turn (cool down, grow,
fruit) — anything else means a different tree; and the no-planting log now has a
fixed form a program can check, including a mandatory last line saying how each
story ended. Nothing here needed a decision from you, and the checker will read
this only AFTER finishing the measuring-tool review that unblocks the main
investigation.

## Boundaries

No implementation, no resident mutation, no Arena action. After this pass the books
return to you for final confirmation only.
