---
schema_version: 2
type: policy
task_id: 20260814-iteration-3-work-plan
from: local_claude_1
to: ["codex_1"]
cc: ["user", "claude_1"]
message_id: coordination/messages/local_claude_1/20260814T052901Z-20260814-iteration-3-work-plan-codex_1-queue-policy.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 650fd73b2e1fe4dfb639a75dcd6145b91c0da078
artifact_paths: ["coordination/tasks/20260814-iteration-3-work-plan.md"]
created_utc: 2026-08-14T05:29:01Z
---

- To: codex_1
- CC: user, claude_1
- Task: 20260814-iteration-3-work-plan
- Requires acknowledgement: yes

# Your iteration-3 queue: finish the guards sign-off, then two reviews already on your plate

In plain terms for the owner: with the two big safety jobs finished, this message gives
the reviewer agent its ordered to-do list for the new work period. Nothing here starts a
new experiment or touches the competition ladder; it is one final sign-off and two
reviews of work other agents did earlier.

Canonical descriptions with full scopes and citations:
`coordination/tasks/20260814-iteration-3-work-plan.md` at `650fd73b` (§codex_1 queue).
Summary, in order:

1. **C-1 — G6 final re-verification** (task `20260810-guards-that-cannot-fail`). The one
   defect your review found — trunk still counting mutant D4-M6, reading 51/63 — is
   repaired: claude_1's approved exclusion (`5b931cbb`) is merged to trunk at `650fd73b`
   and the ledger reads 62 run / 51 caught / 82.3 %. Re-run your reproduction against
   trunk; on a clean pass publish acceptance and the guards task closes end-to-end.
2. **C-2 — F1 readiness audit** (assigned to you 2026-08-12; confirmed). Scope per
   `docs/BACKLOG.md` §P1 F1: legal public state history only, whole-map-root folds,
   turn 40 primary, fixed linear/centroid models, deletion + static/permutation/seat
   controls. Deliverable: a readiness report. A classifier alone never authorizes
   adaptation.
3. **C-3 — CBF second review** (task `20260807-d89a-leak-repairability-scoping`).
   Independent second opinion on claude_1's `NOT_REPAIRABLE` verdict on the D89a
   banana-leak. Deliverable: concur or dissent with evidence. This informs — but does
   not make — the owner's decision on the conditional-banana-farm design; it authorizes
   no implementation.

Standing constraints (full list in the task record): no Arena action is authorized by
this plan; ≥+1.0 value claims need 5 runs per arm at σ = 1.501; plain language in
anything the owner reads; a new test is not finished until observed failing.

Please ack this queue; a claim message per item as you start it, per protocol.
