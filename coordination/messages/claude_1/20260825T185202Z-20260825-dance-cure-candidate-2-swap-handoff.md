---
schema_version: 2
type: handoff
task_id: 20260825-dance-cure-candidate-2-swap
from: claude_1
to: ["local_claude_1", "codex_1"]
cc: ["user", "chatgpt_1"]
message_id: coordination/messages/claude_1/20260825T185202Z-20260825-dance-cure-candidate-2-swap-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/claude_1
artifact_commit: b6f9413e2fb713aabb56d1913dbf35601d7d9868
artifact_paths: ["claude_1/cure2/c10_a1_check.py", "claude_1/cure2/c10-report-2026-08-25.md", "claude_1/cure2/results/c10-a1-check.json"]
created_utc: 2026-08-25T18:52:02Z
---

- To: local_claude_1, codex_1
- CC: user, chatgpt_1
- Task: 20260825-dance-cure-candidate-2-swap
- Requires acknowledgement: yes

# DELIVERY — **C-10 PASSES: 66 of 66 exchanges, 100.00 %.** A-1 is not an assumption any more; the referee really does execute the circular swap

The coordinator's `20260825T184429Z` put C-10 first because it is the assumption the whole design
rests on and G-0 §10 pre-commits that **C-10 below 100 % withdraws the design**. It is now
measured, on the entire exchange population this programme has produced.

## The number

| corpus | games carrying an exchange | exchanges | observable | exchanged | misses |
|---|---|---|---|---|---|
| fixtures | 12 of 34 | 20 | 20 | **20** | **0** |
| panel (instrument arm) | 28 of 240 | 46 | 46 | **46** | **0** |
| **total** | | **66** | **66** | **66** | **0** |

Per exchange at turn `t` with mover `M`, displaced partner `B`: `c_{t+1}(M) == c_t(B)` **and**
`c_{t+1}(B) == c_t(M)`. The **cells** come from the referee's own transcript
(`trace_detectors.build_trace`); the **pair** comes from the `S`/`X` branch codes on the v5 wire.
Two independent sources by construction — the arm cannot both name the pair and score itself.

## Three gates, each of which fails the run rather than degrading it

- **G-B row identity — PASS.** This is a fresh re-execution, not a re-read: all 28 panel games
  reproduced their `swaps` count from `results/panel-swap-census.json` and all 12 fixtures their
  exact exchange turns from `results/swap-loop-control.json` (`OSC-006` at 3/5/7/9/11, and the
  rest). Without it the population checked would not be the population the G-1 report describes.
- **G-D unambiguous pairing — PASS.** Every exchange turn carried exactly one `S` and one `X`; any
  other shape raises rather than pairing by guesswork.
- **G-E observability — 0 cases.** A final-turn exchange, or one where either unit is absent from
  the `t+1` state, has no observable post-state and is counted `NOT_OBSERVABLE`, excluded from the
  rate and listed by id. **There were none**, so the 100 % is over the whole population and not
  over a survivor subset. I would rather report `62/62 with 4 unobserved` than a laundered 100 %,
  and the tool is built to force that; it simply did not have to.

## Two observations, recorded, neither a gate

- `manhattan(c_t(M), c_t(B)) == 1` on **all 66** — clause 5's adjacency premise for Lemma 1 is
  realised, not merely commanded.
- **No third own unit** stood on either exchanged cell at `t+1`, in any of the 66 — the "both
  cells are `granted`" step of Lemma 1's proof is confirmed against the referee, not assumed.

## What it licenses, and what it does not

It licenses **Lemma 1** and the post-state half of both theorems on the referee we actually run.
It does **not** touch A-2 (`prev_cells`; that is C-11, not yet run). And it does not soften the
C-5 stop — **it hardens it**: the 12 within-6-turn re-exchanges are genuine cell exchanges, not a
telemetry artefact, so the loop is real and the owner's ruling on it still governs. The `m061`
−75 remains undiagnosed. Report: `claude_1/cure2/c10-report-2026-08-25.md`.

No Arena action taken; none proposed.
