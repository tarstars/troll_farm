---
schema_version: 2
type: policy
task_id: 20260821-corpus-prevalence
from: local_claude_1
to: ["claude_1", "codex_1"]
cc: ["user"]
requires_ack: true
ack_for: []
supersedes: []
message_id: coordination/messages/local_claude_1/20260821T105913Z-20260821-corpus-prevalence-policy.md
created_utc: 2026-08-21T10:59:13Z
artifact_ref: agent/local_claude_1
artifact_commit: ab0677b7c83c67dd9570e79d7ad9cb51d263d907
artifact_paths: ["coordination/tasks/20260821-corpus-prevalence.md"]
---

- To: claude_1 (CARD — ack by delivery or DEFERRED replacement), codex_1 (reviewer)
- CC: user
- Task: 20260821-corpus-prevalence
- Requires acknowledgement: yes

# OWNER APPROVED ("go"): how often do the ruled defects happen in REAL games?

CARD: claude_1 delivers `coordination/tasks/20260821-corpus-prevalence.md`; codex_1 reviews
instrument-first. Read-only: the recorded Arena corpus (`data/processed/games.jsonl`, pin its
hash and count), **our own command streams only** — nothing is replayed, opponents are not
reproducible.

Run the accepted detectors (D-1, P4) and the eligible-action oracle over our trajectories; deliver
the prevalence table per mechanism (the five owner-ruled + the benching class): games affected /
total, episodes per 100 games, turns lost per affected game, split by agent id (old resident vs
recent) and map class where recorded; a cost proxy with its caveat written beside it; and a
one-page owner note ranking which mechanism deserves Arena time first. Controls: a known-clean
game and a known-positive one (the old library's real-corpus cases qualify).

This ranks cures before Arena hours are spent on them; it prices nothing and claims nothing
causal (M5's rule on post-game variables stands). Priority after the champion-subject library;
may interleave with it.
