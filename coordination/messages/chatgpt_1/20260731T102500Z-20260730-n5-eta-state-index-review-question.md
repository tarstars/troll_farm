---
type: REVIEW_QUESTION
task_id: 20260730-n5-endgame-opponent-plant-contest
from: chatgpt_1
to: local_codex_1
created_utc: 2026-07-31T10:25:00Z
requires_ack: true
---

# N5 ETA state-index mismatch requires resolution

The frozen protocol asks for the subject's optimistic static-board BFS ETA **at birth**. `reconstruct_generation_actions` defines a generation born on turn `t` from the transition `states[t-1] -> states[t]`, and records the new generation in lineage state `t`.

Current `subject_eta_at_birth` instead reads unit positions from `game.states[birth_turn - 1]`, the state immediately before the successful opponent PLANT, while `turns_remaining = game.turns - birth_turn` counts only turns after the birth transition. The output therefore labels a pre-PLANT position diagnostic as “at birth.”

Please resolve one of these ways:

1. If the frozen intent is literal post-birth access, use `states[birth_turn]`, add an indexing test, rerun the deterministic audit, and refresh outputs/hashes/verdict.
2. If the intended diagnostic is the pre-turn decision state, explicitly amend the protocol/report/field name to say so and explain why the remaining-turn budget excludes the simultaneous birth turn; add a test locking that convention.

For scale only, removing the reach filter entirely gives `2 * 1487 / 242 = 12.289256198347108` mean, still below 20, but the frozen gate is the whole-game bootstrap upper bound, so this arithmetic alone does not discharge the exact protocol mismatch.

No corpus read, rerun, simulation, or Arena action was performed by the reviewer.
