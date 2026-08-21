---
schema_version: 2
type: policy
task_id: 20260821-champion-subject-library
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/local_claude_1/20260821T105912Z-20260821-champion-subject-library-policy.md
created_utc: 2026-08-21T10:59:12Z
artifact_ref: agent/local_claude_1
artifact_commit: ab0677b7c83c67dd9570e79d7ad9cb51d263d907
artifact_paths: ["coordination/tasks/20260821-champion-subject-library.md"]
---

- To: claude_1 (CARD — ack by delivery or DEFERRED replacement), codex_1 (reviewer)
- CC: user
- Task: 20260821-champion-subject-library
- Requires acknowledgement: yes

# OWNER APPROVED ("go"): fixtures follow the champion — re-freeze the library on `547fa706`

CARD: claude_1 delivers `coordination/tasks/20260821-champion-subject-library.md`; codex_1 reviews
instrument-first.

The owner saw what the re-grade showed — we were measuring with stale baskets — and approved the
method change in one word. The rule, now written: **a recorded episode belongs to the bot that
produced it.** Fixtures are exhibits for understanding and for the owner's rulings, and regression
checks for that bot; they are regenerated for every kept champion and never outlive it. Cures are
graded on the panel population (gate amendments published on the cure tasks today).

Deliverables: (1) the subject library for the champion from the **unmodified** builder over the
**same panel config** the `98628e98` library used, with episode identity recorded per case and
viewer pages; (2) the mechanism carry-over table — which new cases exhibit each of the five
owner-ruled mechanisms and the benching class, and which old rulings have no exhibit on the
champion ("no exhibit", never "fixed"); (3) the auto-refresh hook for the night-runner after an
owner KEEP — **designed, not deployed** (deployment goes through the VM deploy-card route after
codex_1's review); (4) a one-page owner note with viewer links.

Priority for claude_1, in order: α's current G-1 remedy step → the identity gate (deliverable 1
of `20260821-episode-identity-regrade`; its old-34 re-grade is downgraded to an exhibit) → this
card → `20260821-corpus-prevalence` → benching Phase 3a. Measurement and tooling only; no cure,
no candidate, no Arena action.
