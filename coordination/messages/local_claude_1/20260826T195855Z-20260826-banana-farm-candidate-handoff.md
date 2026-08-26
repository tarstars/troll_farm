---
schema_version: 2
type: handoff
task_id: 20260826-banana-farm-candidate
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/local_claude_1/20260826T195855Z-20260826-banana-farm-candidate-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: cc38437aee4521779b1f1462451d36bb44fffdd5
artifact_paths: ["coordination/tasks/20260826-banana-farm-candidate.md", "docs/BANANA-FARM-CONTRACT-2026-08-26.md", "coordination/BOARD.md"]
created_utc: 2026-08-26T19:58:55Z
---

- To: claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260826-banana-farm-candidate
- Requires acknowledgement: yes — new charter, board row F-2; the owner wants this candidate created and queued to the platform (ladder slot 3, after L-1)

# handoff: F-2 — the banana wood farm candidate, from the owner's contract to the ladder queue: claude_1 writes the design packet tonight (≤ 2 rounds with codex_1), then builds, then one validity-first panel; slot 3 is booked by the owner and used only if the validity gates pass

Design input, binding: `docs/BANANA-FARM-CONTRACT-2026-08-26.md` — the owner's nine stages; three owner decisions (the hut ring: orthogonal cells = plots, diagonals = mothers, 2–4 mothers, ≤ 8 plots; a **one-way latch** on planting; **mothers-only planting during denial**, by the second troll, seeds from the shack); the verified rules (score = fruit + **4 × wood**; a seed → a size-4 tree → 16 points; banana cooldown 6, 4 by water; health 2 + size; trees are walkable; chopping an enemy tree gives us the wood; no conversion action — the late wave pays to ~10 turns before the end); the restored worker rules (§3: a banking troll keeps going; never chase another's cell; sticky targets; never two of ours on one ring cell) as **measured tests**; the acceptance shape (§5). Card: `coordination/tasks/20260826-banana-farm-candidate.md` — done / dead / budget.

**claude_1, tonight:** the design packet `claude_1/farm/g0-farm-2026-08-2x.md`: the state machine TRAIN → DENY(+mothers) → FARM → WOOD with one-way edges and each edge's observable; the aim-selection rule; the latch threshold and denial round criterion K **calibrated from the turn corpus** (`data/processed/turns.jsonl.gz` is on codex_1's VM — ask codex_1 for the two numbers if you cannot read it: enemy chops on the leaders' ring cells per turn, and their aim-tree recount behaviour); whether capacity 2 is trained first; the v6 line extended with farm state; the pre-committed panel gates, validity first. Where you depart from the contract, say where and why. **codex_1:** review within two rounds; then the one reproduction of the panel. Build = a diff on `readable/door1-champion.rs`, one flag line, round-trip identity, as 0-3a. The coordinator wakes hourly and rules on anything that blocks; the owner reads the packet in the morning.
