---
schema_version: 2
type: handoff
task_id: 20260824-dance-cure-proposal
from: chatgpt_1
to: ["local_claude_1"]
cc: ["user", "claude_1", "codex_1"]
message_id: coordination/messages/chatgpt_1/20260824T203500Z-20260824-dance-cure-proposal-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260824T194000Z-20260824-dance-cure-proposal-policy.md"]
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 7651e1dda728328110da710edb89ee4f1f9c6792
artifact_paths: ["chatgpt_1/dance-cure/proposal-2026-08-24.md"]
created_utc: 2026-08-24T20:35:00Z
---

- To: local_claude_1
- CC: user, claude_1, codex_1
- Task: 20260824-dance-cure-proposal
- Requires acknowledgement: yes
- Artifact: `agent/chatgpt_1@7651e1dda728328110da710edb89ee4f1f9c6792`

# handoff: build P1 active-work ownership first; do not combine the three dances

**Recommended first build:** a P1-only one-turn `ActiveWorkLease` enforced inside the joint candidate-composition boundary. A selected productive stationary command owns its unit's current cell for that pair; a mover candidate whose projected landing is that cell is infeasible before score comparison. Apply the same contract at ordinary selection and the later route/source merge. Keep the final resolver as a legality backstop, not the intent owner.

The accepted research separates three mechanisms:

- P1: 10 episodes / 430 turns, exactly one stationary working blocker on every blocker tick. This is the strongest and narrowest causal target.
- P2: 15 / 434, no blocker, fixed target, target occupied on 218 turns. This needs stable approach/occupancy state, not the P1 rule.
- P3: 37 / 1,598, no blocker, changing target and source; 29 / 1,374 preserve route, commitment boundary, and blocker set. This needs semantic intent persistence and should initially exclude the eight boundary-changing rows.

Do not build all three together. A combined patch would change joint feasibility, destination memory, semantic intent, specialized commitments, and resolver composition at once, making either success or failure uninterpretable.

The proposal specifies exact predicates, state, preservation obligations, composition risks, detector and liveness kill rules, predicted evidence-table movement, G0-G4 reuse, the 160-game paired named-cost plan, and the real-game structured-trace boundary.

**Recommended next hour, read-only:** classify the exact 10 P1 rows by the candidate-composition site that introduced the conflicting move and write the complete pair-feasibility truth table. Stop with `DESIGN_INPUT_UNOBSERVABLE` if the accepted rows lack pre-resolver/site data; do not create a probe or run a panel inside that hour.

Pinned proposal:

`agent/chatgpt_1@7651e1dda728328110da710edb89ee4f1f9c6792:chatgpt_1/dance-cure/proposal-2026-08-24.md`

No candidate, bot, panel, detector, grader, test, experiment, TestSession, submission, or Arena state was changed or run.
