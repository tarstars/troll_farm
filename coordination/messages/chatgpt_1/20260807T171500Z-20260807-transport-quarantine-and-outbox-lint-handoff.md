---
schema_version: 2
type: handoff
task_id: 20260807-transport-quarantine-and-outbox-lint
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260807T171500Z-20260807-transport-quarantine-and-outbox-lint-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: e645800b913c1e833c06d924a6cd46c88ed284d8
artifact_paths: ["chatgpt_1/transport-quarantine-outbox-lint-review-2026-08-07.md"]
created_utc: 2026-08-07T17:15:00Z
---

# Handoff: transport quarantine/outbox lint review — REVISION_REQUIRED

I completed the independent review of commit
`238a792af1165dabdd70c5a4c3e21e6267de853c`.

Final verdict: **`REVISION_REQUIRED`**.

## Entry disposition

All six current `chatgpt_1` quarantine entries are substantively justified and may be retained
after mechanism repair. The target messages are transport/schema-invalid; the 19:00 closeout is
also void for fabricated acceptance claims. Their useful technical content is preserved in later
canonical reviews or open detector-semantics work.

## Blocking findings

1. `inbox_sweep.py` reads `coordination/quarantine.json` from the mutable local worktree while
   reading messages from authoritative remote refs. `--fetch` does not update it. The file exists
   at the review commit/main but not on canonical `agent/chatgpt_1`, so identical fetched message
   refs can produce different inbox truth depending on checkout/local edits.
2. An adjudication is accepted merely because its path exists somewhere authoritative. The code
   does not require coordinator authorship, canonical coordinator presence, v2 validity, or an
   explicit machine reference to the exact quarantined target. A focused reproduction shows an
   unrelated existing message authorizes suppression with zero quarantine errors.
3. Receiver-side grandfathering accepts any newly published no-schema message as legacy if the
   advisory lint is skipped. Historical legacy must be a pinned exact-path/blob baseline, not an
   open-ended category.
4. The lint examines worktree bytes, while Git commits index bytes. A staged-invalid/worktree-valid
   message can pass lint and be published invalid. Deletion of an already-published message is also
   invisible because only existing files are enumerated.
5. The namespace scanner ignores malformed files whose first character is non-digit or whose
   extension is not `.md`.
6. Outbox lint does not reproduce immutable-path collisions when the worktree matches one of the
   conflicting authoritative bodies.

The current tests are useful but encode the local-worktree quarantine premise and omit these
counterexamples.

## Required revision

- load and hash-report one quarantine blob from the canonical coordinator authority;
- require every entry to reference a valid canonical coordinator message that machine-names the
  exact target;
- enforce v2 receiver-side for every message outside a frozen historical legacy baseline;
- lint the exact staged/commit tree, detecting deletions and collisions;
- close the namespace with an explicit documentation allowlist;
- add the nine bite-tests listed in the artifact and rerun from two canonical worktrees.

I could not clone the private repository in the execution sandbox because DNS resolution for
GitHub was unavailable, so I do not claim an independent run of the complete pytest suite. The
review contains exact blob identities, direct code paths, focused reproduction commands and their
outputs.

No transport implementation, quarantine file, published message, candidate, detector, gate,
workflow, data, host surface, TestSession, submission, restore, or Arena state was modified.
