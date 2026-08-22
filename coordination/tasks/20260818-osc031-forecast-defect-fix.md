# 20260818-osc031-forecast-defect-fix — cure the forecast's silent "nothing there"

- Status: **CLOSED 2026-08-19T18:39Z — Door-1 candidate GATE REJECTED at
  Phase 2** (honest, reproducible negative: 9 de-novo vs the frozen
  zero-de-novo gate, incl. 4 P3 orchard-dormancy divergences the
  pre-existing-hole exception cannot cover by its own terms; review
  `codex_1/reviews/osc031-phase2-unified-review-2026-08-19.md`). Everything
  learned stands: mechanism verified (fictional decay), gate-1 attribution
  accepted (530-unexplained control, 103/103 evidenced), 15 games healed,
  panels/parity/latency instruments accepted. **OWNER CHARTERED THE SUCCESSOR
  same session: `coordination/tasks/20260819-osc031-forecast-fix-door1b.md`
  (Door 1b — the same evidence rule, scoped to preserve orchard dormancy).**
  Prior: OPEN — OWNER-CHARTERED 2026-08-18T15:36Z by ruling on the 4c brief
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

## OWNER DESIGN RULING (2026-08-18, in session) — DOOR 1

The owner ruled on the three-door proposal: **Door 1 — demand evidence for the
guess.** The "assume a damaged tree is being chopped" inference
(`DAMAGED_FLAT1`) may fire only when an opponent is actually observed at the
tree; historical damage alone is not evidence of ongoing chopping. The exact
presence predicate (on-tree / adjacent / in-reach) is claude_1's to propose
with measurements and codex_1's to verify; if that sub-choice turns out
load-bearing, it escalates to the owner. The integrator's door-3
recommendation (death-as-cost) was considered and declined as the primary; it
remains a possible later refinement if the panel/night shows wasted-walk or
recurrence patterns. **Conditional:** this go is against the provisional
Phase-1 mechanism; if codex_1's probe review changes the mechanism, the design
decision returns to the owner before any build.

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
