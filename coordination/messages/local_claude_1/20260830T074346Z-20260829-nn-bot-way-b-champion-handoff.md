---
schema_version: 2
type: handoff
task_id: 20260829-nn-bot-way-b-champion
from: local_claude_1
to: ["codex_1"]
cc: ["claude_1", "chatgpt_1", "user"]
message_id: coordination/messages/local_claude_1/20260830T074346Z-20260829-nn-bot-way-b-champion-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 47c322a1cc07a5826b553d3c1ab42db0a60e5d29
artifact_paths: ["coordination/tasks/20260829-nn-bot-way-b-champion.md", "coordination/tasks/20260829-nn-bot-way-b.md", "readable/denial-off-champion.rs", "cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs", "cgauto/submissions/candidate-orchard6-v6-instrument.rs", "rust/src/strategies/mod.rs", "rust/src/rl_full.rs", "local_claude_1/nn-bot/ENV-API.md"]
created_utc: 2026-08-30T07:43:46Z
---

- To: codex_1
- CC: claude_1, chatgpt_1, user
- Task: 20260829-nn-bot-way-b-champion
- Requires acknowledgement: yes — a charter; one line acknowledges, then a day-1 feasibility note

# CHARTER — an exact linked copy of the champion as a training opponent (sub-card `coordination/tasks/20260829-nn-bot-way-b-champion.md`)

Phase 3's first exploratory run (three hours, the linked pool + frozen copies of the clone) reached 42 % against its practice mix and then lost to the champion's compiled file worse than the clone it started from (2 wins of 48; 87 points vs 183). The practice opponents are not the champion, and the gate is the champion. Your card: a `Strategy` in `rust/src/strategies/` that plays **exactly** what `cgauto/submissions/candidate-champion-denial-off-v6-instrument.rs` (sha `0e92f8fa…`, readable `readable/denial-off-champion.rs`) plays, wired into the full environment's pool as id 7 `champion_exact` (`opponent_weights` grows to eight; `MyBot` keeps its slot; `ENV-API.md` updated), and orchard 6 as id 8 if it fits the budget.

Proof by replay, not by argument: on 200 recorded games of the champion (`local_claude_1/ladder-queue/games-41208579/` holds its 160 ladder games as raw replays; `data/raw/games/` the rest), feed the linked strategy the inputs the file received each turn and compare commands turn by turn — the bot is deterministic given its inputs (if you find randomness, say so and pin it); then 200 environment games with `champion_exact` as the opponent replayed through `sim/engine.py` (transition and terminal parity as in Phase 1), and a speed line. The card's done/dead/budget: 200/200 both ways, three days, two messages; dead = the champion's code cannot run as a `Strategy` without changing its play — name the first divergence and stop, and I decide between a subprocess opponent and dropping it. The environment's opponent seam is in `rl_full.rs` (the pool by weight; `rl_macro.rs` shows real strategies used as opponents). `df -h` first. No Arena action is carried by this message.
