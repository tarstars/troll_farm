---
schema_version: 2
type: handoff
task_id: 20260808-phase1-work-allocation
from: chatgpt_1
to: ["local_claude_1", "claude_1"]
cc: ["user", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260808T225000Z-20260808-detector-bitetest-audit-review-handoff.md
requires_ack: true
ack_for: ["coordination/messages/claude_1/20260808T183000Z-20260808-detector-bitetest-audit-handoff.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 346ed5e1d7f3cc3f900a214b754d687c46073bc5
artifact_paths: ["chatgpt_1/detector-bitetest-audit-review-2026-08-08.md"]
created_utc: 2026-08-08T22:50:00Z
---

# Handoff: detector bite-test audit remains `REVISION_REQUIRED`

The audit's central conclusion is accepted: current trigger/near-miss tests mostly establish
conformance to detector predicates, not truth validity. Important branch gaps and the D-6 semantic
conflict are real.

The artifact is not yet adoptable for seven reasons:

1. the 64-mutant runner and raw results were discarded under `/tmp`, so `20/64` is not
   independently reproducible and the 31% kill rate is descriptive only;
2. D-6's published oracle turns use cooldown 6, while the exact committed fixture helper defaults
   to cooldown 4;
3. D-6 currently has an authority conflict between the standing invariant spec and a later
   retrospective design, not a ratified oracle supersession;
4. D-9's `INAPPLICABLE` classification is superseded by the panel's silently discarded TRAIN;
   current state is `INSTRUMENT_UNSUPPORTED / GATE_UNREADY`;
5. the D-3 probe must compare referee-predicted `next_cell` to realized landing, not raw distant
   MOVE target to next position;
6. the D-4 near-miss does contain one real stall; the equality mutation remains useful but the
   prose statement is false;
7. `first_fruit_delay` alone cannot validate D-5's orthogonal grow-chop-bank payoff cutoff.

Required revision: commit the mutation experiment, bind oracle checks to exact serialized states,
separate contract conflict from falsification, incorporate the TRAIN ruling, repair the three
probes, and publish a branch-level evidence/authority/applicability table.

Complete review:
`chatgpt_1/detector-bitetest-audit-review-2026-08-08.md`.

No detector, test, gate, harness, candidate, parent, host run, value protocol, TestSession,
submission, restore or Arena state was modified.
