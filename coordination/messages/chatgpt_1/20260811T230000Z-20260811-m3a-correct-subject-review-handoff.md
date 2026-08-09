---
schema_version: 2
type: handoff
task_id: 20260810-manifest-implementation
from: chatgpt_1
to: ["local_claude_1", "claude_1"]
cc: ["user", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260811T230000Z-20260811-m3a-correct-subject-review-handoff.md
requires_ack: true
ack_for: []
supersedes: ["coordination/messages/chatgpt_1/20260810T160000Z-20260810-m3a-independent-replication-handoff.md"]
artifact_ref: agent/chatgpt_1
artifact_commit: 9a4bf9bec0f09c021f0465f8b455f5cbf7f53a08
artifact_paths: ["chatgpt_1/m3a-correct-subject-library-review-2026-08-11.md"]
created_utc: 2026-08-11T23:00:00Z
---

- To: local_claude_1, claude_1
- CC: user, local_codex_1
- Task: 20260810-manifest-implementation
- Requires acknowledgement: yes

# Correct-subject M3a: data integrity passes, clean-machine replay fails

Disposition: **`REVISION_REQUIRED — DATA INTERNALLY CONSISTENT, SOURCE REPLAY NOT PORTABLE`**.

On the exact artifact commit, the loader verified 34 situations / 46 represented episodes and the
internal identity, integrity, classification, and idle-blocker tests passed. With
`OSC_LIB_REPLAY=1`, both replay suites failed because their committed configs point to
`/home/tarstars/...` and `/tmp/claude-1000/...` source paths absent from a clean runner.

Required repair: materialize the exact source from its pinned Git ref into a temporary directory,
verify its SHA, evaluate historical corpus skips before compilation, and rerun all replay tests on
a fresh checkout.

The c5 46-episode diagnostic library is also not the same population as the renewed base-panel
golden v2 record of 34 exact D-1 episodes across 32 source games. The coordinator must select and
version the M3b substrate explicitly; neither may silently replace the other.