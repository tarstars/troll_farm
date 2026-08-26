---
schema_version: 2
type: handoff
task_id: 20260826-banana-farm-candidate
from: local_claude_1
to: ["codex_1", "claude_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T203037Z-20260826-banana-farm-candidate-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 780e3437305663928e9f5b6630bce32428826da0
artifact_paths: ["local_claude_1/farm/ring-pressure-full-2026-08-26.md", "local_claude_1/farm/ratio.py"]
created_utc: 2026-08-26T20:30:37Z
---

- To: codex_1, claude_1
- CC: user, chatgpt_1
- Task: 20260826-banana-farm-candidate
- Requires acknowledgement: yes — an input to round 1 that changes one claim in the packet

# handoff: Q2 answered at scale — `ring_pressure.py` unchanged over all 23,613 replays: the packet's 290-replay numbers reproduce exactly, but at scale **17 % of leader seats exceed the 1.0 latch whole-game, and 46 % in games that end early** (a game-length confound); ours ≈ 0 because we do not plant on the ring; the 300-turn cap is real

Read: `local_claude_1/farm/ring-pressure-full-2026-08-26.md` (tables, per-leader rows, the confound, the command). Not a ruling — an input for codex_1's round-1 verdict and claude_1's round-2 packet: the latch as written ("leader-like play never latches") holds on full-length games (12 % > 1.0) and fails on short ones (46 %); the design must say what the windowed latch does when the game is ending early, or condition on turns remaining. The threshold itself (1.0 = 5× the full-game leader median 0.19) is the reviewer's call. The 66 MB per-seat JSON is on the host, not committed; ask if you want a slice.
