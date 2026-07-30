# progress: 20260730-x1-mechanics-rederivation

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T15:02:22Z
- Task: 20260730-x1-mechanics-rederivation
- Branch: agent/local_codex_1
- Head: 8a5fe2fbc31573ee1a489eb035d226525beb2214
- Requires acknowledgement: no
- Supersedes: none

## Summary

Primary referee source is pinned at upstream commit
`290129129db7a7539d98739ebdb0ed63ee6ceb50`. The first source-to-local inventory has one
confirmed documentation omission, one already-qualified implementation, and two explicit
A2 parity gaps:

- Legend starts with five independent uniform 2..10 draws for PLUM, LEMON, APPLE,
  BANANA, and IRON; the same inventory is assigned to both players. Expected starting
  fruit is 24, expected iron is 6, and initial score includes the four fruit draws.
- `rust/src/game/official_mapgen.rs` models this and its D33 confirmation remains
  120/120 exact on turn-one referee streams.
- Referee movement chooses randomly among equal best in-range cells; maintained Python
  and Rust engines choose lexicographic minimum. This is an explicit A2-0b parity item.
- Local command parsing intentionally omits parts of referee validation (ownership,
  league/skill limits, and invalid-command failure). A2 must either implement these
  semantics or prove zero invalid commands at the harness boundary.

No simulator semantics have been changed. The audit continues across task ordering,
training, plant lifecycle, resource actions, scoring, and termination.

## Evidence

- Upstream `engine/Board.java`, `engine/Constants.java`, `engine/Unit.java`,
  `com/codingame/game/Player.java`, and `engine/task/*.java` at commit `290129129db7...`
- `data/analysis/live-agent-6553250/d33-official-mapgen-parity-result-2026-07-20.json`:
  confirmation 120/120, zero failures
- Local `sim/engine.py`, `rust/src/game/engine.rs`, and
  `rust/src/game/official_mapgen.rs`

## Requested action

None.
