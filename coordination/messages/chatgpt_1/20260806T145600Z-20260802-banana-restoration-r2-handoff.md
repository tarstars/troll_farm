---
schema_version: 2
type: handoff
task_id: 20260802-banana-restoration-r2
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260806T145600Z-20260802-banana-restoration-r2-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 407603d0b4c02a7cd5d20096b48c6873b99a0433
artifact_paths: ["chatgpt_1/banana-restoration-r2-fsm-design-round3-review-2026-08-06.md"]
created_utc: 2026-08-06T14:56:00Z
---

# Handoff: round-3 Banana FSM design remains REVISION_REQUIRED

## Outcome

I completed the owner-directed review of canonical `agent/claude_1` artifact commit
`9369a4ec5e589fc1d057f7ccfb55f83e5e989119`.

Final disposition: **`REVISION_REQUIRED`**. Do not authorize implementation or any downstream gate.

## Blocking findings

1. **EV10 is still pre-referee prediction, not an observed landed fact.** PHASE-4 runs before
   CH3/CH4/CH5 final command edits and before opponent commands/referee CHOP/death/wood allocation.
2. **The “single-chopper” oracle permits impossible zero-cost handoffs.** It can apply a weak
   on-cell chopper at turn `t` and a stronger adjacent chopper at `t+1`, omitting the MOVE-only
   handoff turn required by same-player occupancy and one-command-per-unit mechanics.
3. **The no-aside peer-carrier fallback has no live FSM edge.** EV20 is live only in resident
   S3(Bank)/S8, while the blocked wood carrier can be another worker and the resident can be in
   S3(non-Bank)/S4/S7. “Hand carrier to inner” does not vacate the resident.
4. **The 1,594-row manifest is declarative and stale.** Its transition universe includes removed
   `T6a`, omits new `T3i`, hashes template labels rather than map bytes, and proves coverage by
   unioning self-declared witness strings. Historical-red rows carry no source path/full hash.
5. The §C IBC/AC/EW tally consequently remains overstated.

## Accepted corrections to preserve

- S6 is now correctly only a Mealy output, not a persisted row.
- EV7 has one ownership-independent domain.
- Founding is anchored after the creation tick and equal executable HARVEST turns are unsafe under
  last-fruit duplication.
- Bank reservation uses observable fungible counts rather than fictional lineage.
- CH1/CH2 attribution is captured inside the original planning pass.
- Resident S3(Bank)/S8 occupied-route exits are directionally improved.

## Requested action

Please ACK this exact path, keep Banana R2 at design revision, and route the full itemized review
back to `claude_1`. The next artifact must remain design-only and close the four blockers before
implementation begins.

## Safety

No implementation/source/frozen artifact, game/replay/map range, bulk/LFS object, host/516/value
run, TestSession, submission, restore, or Arena state was opened or changed.
