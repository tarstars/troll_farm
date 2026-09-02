---
schema_version: 2
type: update
task_id: 20260902-endgame-move-gap
from: claude_1
to: ["claude_1"]
cc: ["local_claude_1", "codex_1", "user"]
message_id: coordination/messages/claude_1/20260902T082912Z-20260902-endgame-move-gap-corpus-on-laptop-deferred.md
requires_ack: false
ack_for: []
supersedes: []
created_utc: 2026-09-02T08:29:12Z
---

- To: claude_1 (self)
- CC: local_claude_1, codex_1, user
- Task: 20260902-endgame-move-gap
- Requires acknowledgement: no

# DEFERRED — Track E starts after P-0; the per-turn corpus is on the laptop, not the VM

Replacement card for what this session postponed, so the next wake finds it in the queue.

**Postponed:** the endgame-gap read (`claude_1/endgame-gap/READ-2026-09-02.md`, due
2026-09-04 12:00Z). P-0 was delivered first as charted; Track E is next.

**The first thing to do on wake, and the blocker it may raise:** the per-turn command corpus
`data/processed/turns.jsonl.gz` (174 MB, 23,613 games, manifest sha `1e0ea236…`) is not on
this VM — only its manifest is — and the raw replays it was cut from (23,613 files) are not here
either (the main checkout's `data/raw/games` holds 290). One lead to check first:
`/data/separate_troll_farm-working/profiles/2026-09-02/corpus/data/raw/games` holds 691 raw
games dated this morning (the reconstruction profiles' working corpus); if the four top agents'
games are among them, `scripts/extract_turns.py` cuts a per-turn file from them and the read
proceeds on that subset, stated as such. If not, the read needs `turns.jsonl.gz` copied to
`/data/scratch/` — then this becomes a blocker to the coordinator, sent in the first hour of
Track E. The champion's 160 collected games and the row R-1 fits are on `main` and need
nothing.

**Also carried:** the panel's final draw from the pinned corpus
(`/home/tarstars/nn-data/maps-host-corpus-0901-31088.jsonl`) waits for its copy under
`/data/scratch/` — one command, `make_panel.py --corpus …`, and the new sha on the Track P
card. Not urgent before 09-06.
