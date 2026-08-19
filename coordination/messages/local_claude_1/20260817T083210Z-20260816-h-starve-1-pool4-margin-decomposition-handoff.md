---
schema_version: 2
type: handoff
task_id: 20260816-h-starve-1-standing-troll-audit
from: local_claude_1
to: ["codex_1", "claude_1"]
cc: ["user"]
message_id: coordination/messages/local_claude_1/20260817T083210Z-20260816-h-starve-1-pool4-margin-decomposition-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/local_claude_1
artifact_commit: 561a5353be0ab0c91e880d5c6220e9417c4675d7
artifact_paths: ["local_claude_1/pool4/decompose.py", "local_claude_1/pool4/margin-decomposition-2026-08-17.md"]
created_utc: 2026-08-17T08:32:10Z
---

- To: codex_1 (method verification per charter), claude_1 (informational)
- CC: user
- Task: 20260816-h-starve-1-standing-troll-audit (pool item #4)
- Requires acknowledgement: yes (codex_1 method check)

# handoff: pool #4 — margin decomposition delivered. The stall is the billable event; the dance is mostly a marker.

Artifact `561a5353`, pushed and remote-verified: a deterministic, seed-pinned script
plus the written analysis. Everything recomputed from the committed
`claude_1/t1/t1-matched-floor.json` (the resident's own 240-game replay). No new
runs, no cause labels — the evidence gate holds; this is pricing, not causation.

## Result (margins are panel-internal units, valid within-corpus only; par = 17.40)

| group | n | vs par |
|---|---|---|
| clean | 197 | +2.50 |
| dance only (D-1, no stall) | 16 | **−9.58** (mean dance: 14 turns) |
| stall only (P4 liveness, no D-1) | 8 | −5.02 |
| dance + stall | 19 | **−15.71** (windows ≈ 170 turns, coincident) |

- Stall games vs the rest: −14.13 points, one-sided permutation p ≈ 0.0001.
- **Dance-without-stall vs clean: −12.08 points (p ≈ 0.005) with only ~14 dancing
  turns** — fourteen turns of pacing cannot mechanically cost twelve points, and
  T-1's grading already priced the dance at ≈ nothing. The dance is a MARKER of
  hard game states, not the mechanism.
- Ceiling if all stall games were brought to par (causality NOT established here):
  ≈ 1.4 corpus points. Material against the ≈2-point goal gap IF pools #3/#5 show
  the stalls to be assignment failures rather than lost-position consequences.

## For codex_1 — the method surface to attack

1. Stall turns = live-trimmed P4 windows (`min(window_end, live_end) −
   window_start`); dance turns = summed D-1 episode windows; both straight from the
   committed rows.
2. The dance+stall group is collinear by construction (windows coincide) — I make
   no within-group attribution there and say so.
3. Two pre-named contrasts only; no correction beyond that; strata of 8 and 16 are
   named as small.
4. The reproduction path is one command: `python3 local_claude_1/pool4/decompose.py`.

## For the owner, in plain words

The price question has a first answer. Games where the bot stops making progress
while work remains run about fourteen points below normal, and fixing all of them
is worth at most about 1.4 points on this internal scale — real money against our
two-point gap, IF the ongoing audit shows those freezes are fixable planner
failures rather than symptoms of already-lost games. Meanwhile the dancing itself
keeps looking innocent: games with brief dancing and no freeze still score badly,
which means hard positions cause both the low score and the dance — curing the
dance there cures a symptom of a symptom. Your verdict session will get this table
next to the cause table.

## Boundaries

No cause labels, no cure code, no resident mutation, no Arena action. Registry
frozen. Margins are not arena rating points and are never quoted as such.
