---
schema_version: 2
type: handoff
task_id: 20260802-banana-restoration-r2
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260806T123500Z-20260802-banana-restoration-r2-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 3afd187fc80a6f0a4bbefb300ff8f12f3f601fd2
artifact_paths: ["chatgpt_1/banana-restoration-r2-fsm-design-rereview-2026-08-06.md"]
created_utc: 2026-08-06T12:35:00Z
---

# Handoff: revised Banana R2 FSM design remains REVISION_REQUIRED

## Outcome

I completed the owner-directed design-only review of canonical `agent/claude_1` artifact commit
`46588155b2c4cd59d21f7334f407878b537ed83d`.

Final disposition: **`REVISION_REQUIRED`**. Do not authorize implementation or any host/value/Arena
gate from the reviewed draft.

## Blocking findings

1. A.2 selects transitions before commands exist, but EV10 is command-produced on that same turn;
   the atomic model has no causal phase for it.
2. S6 is declared non-persisted while remaining a transition target and full A.4 row; EV7 is also
   defined both as co-occurring with flip and as `not flip`/mutually exclusive.
3. `_opp_destroy_turn` adds simultaneous power from multiple same-player choppers on one tree cell,
   which referee movement conflicts make unreachable; the oracle is conservative, not exact.
4. Founding has no exact post-PLANT/tick time anchor and compares arrival order rather than actual
   opponent HARVEST safety; cross-player co-location and last-fruit duplication defeat exclusivity.
5. Carrier yield covers only full, speed-one-like carriers; its no-aside WAIT fallback does not free
   the blocked articulation landing and can conflict with tight conversion deadlines.
6. A “latched-lineage” bank PICK is not observable in the referee's fungible species inventory;
   no deterministic lot/count accounting is specified.
7. EV20 tests static BFS only and only in S8, so occupied/unusable routes can still loop in S3/S8.
8. The packet has no concrete 1,588-row manifest artifact or stable IDs/hashes. ST6/ST7,
   historical red rows, and per-T-id edge coverage do not reconcile with the prose count.
9. Post-divergence CH1/CH2 indirect effects lack a defined side-effect-free attribution method.
10. The §C 13/3/1 tally consequently still overclaims impossible-by-construction closure.

## Accepted directions to preserve

Aligned-prefix-only parent comparison, latched mother identity, finite lost-asset claim intent,
worker-two funding dormancy, explicit infeasibility exits, and contract→enumeration→fuzz→host order
are directionally accepted.

## Requested action

Please ACK this exact path, keep Banana R2 at design revision, and route the itemized report back to
`claude_1`. A later request must be another design-only artifact; no implementation or host gate
should begin first.

## Validation boundary

The artifact commit is on canonical `agent/chatgpt_1` and contains the complete review. I opened no
additional replay/map/range or bulk artifact and performed no implementation/source/frozen edit,
host/516/value run, TestSession, submission, restore, or Arena mutation.
