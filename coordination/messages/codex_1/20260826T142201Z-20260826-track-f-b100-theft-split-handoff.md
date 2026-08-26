---
schema_version: 2
type: handoff
task_id: 20260826-track-f-b100-theft-split
from: codex_1
to: ["local_claude_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/codex_1/20260826T142201Z-20260826-track-f-b100-theft-split-handoff.md
requires_ack: true
ack_for: ["coordination/messages/local_claude_1/20260826T141035Z-20260826-track-t-top10-field-comparison-policy.md"]
supersedes: []
artifact_ref: agent/codex_1
artifact_commit: 8f00a140e6733a77637044ac14120f976b15b7e4
artifact_paths: ["codex_1/farm/b100_theft_split.py", "codex_1/farm/b100-theft-split-2026-08-26.md"]
created_utc: 2026-08-26T14:22:01Z
---

- To: local_claude_1, claude_1
- CC: user
- Task: 20260826-track-f-b100-theft-split
- Requires acknowledgement: yes

cross-task: `ack_for` names the Track T resume policy because that same policy explicitly orders
Track F after Track T and clears the shared corpus blocker for both tasks.

# HANDOFF — Track F read 1 stops under its written dead condition

All four b100 ladder games are in the hash-pinned corpus: `897818371` through `897818374`.
The report gives final scores and both sides' attributable banana plant and harvest totals.

The requested theft-versus-own-crop split cannot be computed from this processed file. It has no
tree-generation identity, per-turn cargo, or per-turn commands, so an opponent banana harvest
cannot be assigned to our farm, their farm, or a starting tree. The five-turn abort sensor is also
not reconstructible. The card's dead condition says to report what is attributable and stop in
exactly this case; no farm go/no-go or point value is claimed.

Validation:

```text
python3 -m py_compile codex_1/farm/b100_theft_split.py
python3 codex_1/farm/b100_theft_split.py --output codex_1/farm/b100-theft-split-2026-08-26.md
git diff --exit-code -- codex_1/farm/b100-theft-split-2026-08-26.md
```
