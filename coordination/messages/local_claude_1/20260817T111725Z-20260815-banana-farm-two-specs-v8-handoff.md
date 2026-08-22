---
schema_version: 2
type: handoff
task_id: 20260815-banana-farm-two-specs
from: local_claude_1
to: ["codex_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260817T111725Z-20260815-banana-farm-two-specs-v8-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/local_claude_1/20260817T110615Z-20260815-banana-farm-two-specs-v7-handoff.md"]
artifact_ref: agent/local_claude_1
artifact_commit: 1958a0bca995c3d03ab1ab9476c767189e0be65b
artifact_paths: ["docs/superpowers/specs/2026-08-15-banana-farm-spec-a-unconditional.md", "docs/superpowers/specs/2026-08-15-banana-farm-spec-b-conditional.md"]
created_utc: 2026-08-17T11:17:25Z
---

- To: codex_1 (review v8 — v7's review round is superseded before it began), claude_1 (informational)
- CC: user
- Task: 20260815-banana-farm-two-specs (v8 — FOURTH owner ruling)
- Requires acknowledgement: yes (codex_1)

# handoff: Spec v8 — owner ruling "NO PLANTING DURING DENY"; the v6–v7 exclusion machinery is DELETED

Supersedes the v7 handoff (its review round had not begun). Artifact `1958a0bc`;
shared skeleton §3–§8 re-verified byte-identical.

## What happened

The owner stated in session: "during the target denial phase our bot can't plant
trees." I code-verified before acting: the bot's SOLE planting site is the endgame
planner's PLANT (:1256), reachable during DENY only in a narrow corner — board ≤ 4
plants while losing, or turn > 250 (of 300), or the ≤2-plant banked-fruit PICK
pipeline (:1177 — turn ≥ 100, adjacent to shack, empty-handed). So the statement was
true-by-circumstance except in exactly the bare-board corner your v6 census-1 case
lived in. Presented the options; **the owner RULED: make it true by decree — PLANT
is SUPPRESSED while the machine is in DENY.**

## What changed (v8)

1. **The whole v6–v7 exclusion apparatus is DELETED**: no exclusion tracker, no
   census-eligibility distinction, plain census counts. Your v6 constructed case is
   now impossible by construction rather than guarded by bookkeeping.
2. **The suppression rule** stands in §4 with its code-verified basis and priced
   cost (conversion trick delayed until a doorway fires, in states where denial is
   ending anyway). Pre-DENY-planted trees (degenerate corner) count as ordinary
   census members — extra members make futility harder, the conservative side.
3. **Gate GB** gains its second named exception (DENY-phase PLANT suppression).
   **GK**'s exclusion arm is replaced by suppression twins (resident would PLANT in
   a constructed bare-board DENY state → machine bot must not, and must resume after
   the doorway). **GE** re-anchored (blip hazard closed structurally; telemetry cell
   updated). Register row added in both files (fourth ruling).

## For codex_1

Review surfaces I would attack: whether suppression interacts with the commitment
pipeline (a unit holding a commitment during DENY is routed to the endgame planner
every turn — with PLANT suppressed it will receive MOVE/WAIT-shaped candidates from
that generator; is there a starvation or oscillation hazard there, and should the
commitment itself be prevented or cleared during DENY?); and whether GB's transcript
diff can distinguish the two named exceptions cleanly.

## For the owner, in plain words

Your rule is now law in the books: the bot simply cannot plant while the chopping
war is on — enforced by the code, not by circumstances. All the bookkeeping we had
invented to guard against that case is deleted, which makes the books shorter and
the eventual implementation simpler. The checker reads once more; the register now
carries four rulings of yours.

## Boundaries

No implementation, no resident mutation, no Arena action. After codex_1's pass, the
books return to the owner for final confirmation only.
