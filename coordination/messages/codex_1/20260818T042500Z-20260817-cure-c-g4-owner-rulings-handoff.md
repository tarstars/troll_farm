---
schema_version: 2
type: handoff
task_id: 20260817-cure-c-implementation
from: codex_1
to: ["local_claude_1", "claude_1"]
cc: ["user"]
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260818T041052Z-20260817-cure-c-owner-rulings.md"]
supersedes: []
message_id: coordination/messages/codex_1/20260818T042500Z-20260817-cure-c-g4-owner-rulings-handoff.md
artifact_ref: agent/codex_1
artifact_commit: b5924d370fb1cc66a84260864e62e9561302048c
artifact_paths: ["codex_1/reviews/cure-c-g4-owner-rulings-review-2026-08-18.md"]
created_utc: 2026-08-18T04:25:00Z
---

- To: local_claude_1, claude_1
- CC: user
- Task: 20260817-cure-c-implementation
- Requires acknowledgement: yes

# G4 green handoff: owner contingencies independently verified; G5 path open

Owner policy is acknowledged by exact path. Pinned independent review:
`codex_1/reviews/cure-c-g4-owner-rulings-review-2026-08-18.md` at
`b5924d370fb1cc66a84260864e62e9561302048c`.

Verdict: **GATE_ACCEPTED / G4 GREEN** under the published owner rulings.

- OSC-009's 4 to 0 and OSC-031's 178 to 89 surprises are mechanized from fresh
  instrumented replays. OSC-031 remains a stall; its reduction is an explained
  classifier-attribution shift, not a cure claim.
- m061 scores 75 versus 48. The original identical-tail argument was insufficient
  because the variant's alternate branch is not entered there, so I directly probed
  the resident endgame generator in the candidate's live states. It returns only
  `WAIT` throughout P4 turns 39--99. Both pre-existing-hole prongs are verified.
- m082 is confirmed as the WAIT-tail cost: 12 to 1 with 184 new D-1 and 185 new P4
  turns; the endgame-tail variant removes both and restores score 12.
- G1 and G2 therefore pass under the owner's new general rules; G3 remains green.

G5 may proceed now through the charter's serialized controller path, with unchanged
candidate SHA-256 `ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1`.
Carry m082 as the named cost and both new measurement rules into the ledger/night
record. The resident remains byte-sacred until an owner KEEP.
