# 20260818-osc031-forecast-defect-fix — cure the forecast's silent "nothing there"

- Status: OPEN — OWNER-CHARTERED 2026-08-18T15:36Z by ruling on the 4c brief
  (**"a defect"** — ruling record:
  `local_claude_1/adjudications/OSC-031-ruling-2026-08-18.md`).
- Record owner: local_claude_1 · Work owner: **claude_1** ·
  Reviewer: **codex_1** (gates) · Integrator: local_claude_1
- Area: chop planner, `predict_tree` (`PREDICT_TREE_NONE` terminal); successor
  to `20260818-osc031-chop-clause-instrument` (CLOSED by the ruling)
- Base: diagnostic COPY of resident `98628e98…`; resident byte-sacred.
- Created UTC: 2026-08-18T15:36:14Z

## What the owner ruled

The behavior measured by 4c — the forecast step returning "no tree to plan
against" on all 315 evaluations across the 167 locked turns, starving a
chop-capable troll of every chop — is **a defect**. The cure is chartered; the
mechanism is still unknown (deliberately unmeasured by 4c).

## Phase 1 — WHY (diagnose before designing, the standing lesson)

Small parity-disciplined probe on the accepted 4c toolkit: for the pinned 167
turns, log WHY `predict_tree` returns `None` per evaluation — which internal
branch/condition produces it (unprivileged: every internal exit logged, same
discipline as 4c). Deliverable: mechanism note + **fix design proposal** to the
OWNER for a design go (the fix touches planner core; "two correct doors make a
wall" is the standing hazard — no fix is built before the owner sees WHY and
approves the door). codex_1 reviews the probe instrument-first, then the
mechanism note.

## Phase 2 — the fix (only after the owner's design go)

Implement per the approved design. Gates, fail-first, in order: fixtures
observed failing on the unmodified resident then green under the candidate
(zero de-novo D-1/P4 across all 34 situations, turn-coverage metric); 240-game
panel vs matched floor, zero de-novo both arms, per-game decomposition
published; p95 latency + parity; codex_1 independent reproduction (gate
review). Ready-with-gates is the END STATE of this task.

## Explicitly OUT

**Any Arena action** — the cure-C paired night owns the Arena; a new candidate
submission is a SEPARATE owner decision after the night settles (one change per
night is law). Class-wide incidence sweep (available as a named extension if
the owner asks). Touching the byte-sacred resident or dev copy.

- Authority: owner ruling in session, 2026-08-18.
