---
schema_version: 2
type: update
task_id: 20260826-p4b-narrator-param
from: claude_1
to: ["claude_1"]
cc: ["codex_1", "local_claude_1", "user"]
message_id: coordination/messages/claude_1/20260826T135008Z-20260826-p4b-proof-inputs-not-durable-deferred.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-08-26T13:50:08Z
---

- To: claude_1 (self)
- CC: codex_1, local_claude_1, user
- Task: 20260826-p4b-narrator-param
- Requires acknowledgement: no — replacement card for work I am deliberately not doing inside the re-review

# DEFERRED — the two inputs that prove D-2 live in `/tmp` and will not survive the next sweep

The re-review (`134853Z`, ACCEPT) is complete and its **conclusions** are durable: the
evaluated v6 packet is committed at `claude_1/cure3/p4b-rereview-v6-packet-2026-08-26.json`.
What is **not** durable is the two inputs that produced it:

- `/tmp/claude-1000/cure3/instrument/games/games.jsonl.gz` — Candidate 3's v6 instrument
  archive, 915 KB, the sole copy of the 240 games behind "0 decode errors / 15 episodes".
- `/tmp/codex1-p4b-v5-repro/p4b-v5-rerun.json` — codex_1's regenerated v5 packet, 437 KB.

Our own standing scratch rule trap-cleans `/tmp`. When it fires, D-2's proofs become
re-derivable only by re-running the panel, not by re-reading a file. That is acceptable for a
closed instrument task and it is why I am not treating it as a blocker — but it is a fact about
the record, not a risk I want discovered later.

I am not committing the archives myself: a 1.3 MB binary drop into the repo is a storage
decision, not a reviewer's, and the standing rule is that medium data does not go in the tree.

**Resume only if** the coordinator or owner wants the inputs preserved, and says where — LFS, an
out-of-tree archive path, or an explicit exemption. Until then the packet and the re-review
document are the record, and neither claims the raw archives are still on disk.
