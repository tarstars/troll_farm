---
schema_version: 2
type: handoff
task_id: 20260809-oscillation-attack
from: chatgpt_1
to: local_claude_1
cc: ["user", "claude_1", "local_codex_1"]
message_id: coordination/messages/chatgpt_1/20260809T150000Z-20260809-oscillation-cross-review-handoff.md
requires_ack: true
ack_for: []
supersedes: []
artifact_ref: agent/chatgpt_1
artifact_commit: 5b854aea48a1d24a5e204c0fc501f02367306d05
artifact_paths: ["chatgpt_1/oscillation-cross-review-2026-08-09.md"]
created_utc: 2026-08-09T15:00:00Z
---

# Handoff: oscillation cross-review complete — merge the mechanism, revise the cure

I reviewed all three independent answers and the exact submitted source. Synthesis disposition:
**`MERGE_WITH_CORRECTIONS`**.

## Accepted shared mechanism

The useful merged model has three parts:

1. **M1 path/corridor block:** semantic targets differ, but a stationary peer occupies the only
   route and the resolver silently invents a retreat.
2. **M2 stationary occupation is absent from planning:** `WAIT` carries `Target::None`, which is
   universally compatible, so an idle unit may physically occupy the moving unit's semantic goal
   without pair compatibility seeing it.
3. **M3 scorer cycle:** `endgame_candidates` evaluates only the current door when standing on a
   door but all doors one step away, creating a one-worker Bellman/value discontinuity.

The mover/resolver is not the whole bug. The contract between planner and executor is broken:
target-only compatibility is followed by an invisible one-turn detour with no typed feedback or
target invalidation.

## Corrections that matter for the merged plan

- A previous-cell or monotone-movement fix alone can turn every terminal oscillation into a
  terminal WAIT/stall. D-1 silence is not success; liveness and task disposition are mandatory.
- The Gold same-position watchdog remains a non-fix. The joint solver is reusable only when paired
  with explicit stationary occupation and a bounded yield/retarget policy.
- `Target::None` cannot be fixed by one expression: `WAIT` needs an explicit stay/occupation
  action, and compatibility must reason over predicted landings and stationary cells.
- “Standing on a plant” is not “working.” The capable-worker Elost rule misses idle/incapable
  blockers.
- Per-unit `d_goal` monotonicity is too broad as a universal contract; a deliberate joint
  corridor handoff may require a temporary retreat. What is forbidden is an **unplanned silent
  retreat**.
- M3 should be repaired by one consistent door-candidate universe before adding generic target
  commitment.
- The exact 21/13/1 split, 20/20 idle count and potential-step totals are scratch-only and must be
  committed/reproduced before becoming frozen project truth.
- The new `m040-s1` row is useful but provisional because its `fuzz-panel/2-train` referee revision
  was not accepted. Rerun it after referee revision 2.
- D176a's `+0.045` is not an upper bound on a proper root-cause repair: it changed visible motion
  without proving progress restoration.

## Correct implementation order

1. Commit a machine-readable classification/evidence packet and literal red fixtures for
   `m110-s1`, `m014-s1`, `m085-s0`, and provisional `m040-s1`.
2. Red tests must assert executable-plan compatibility, bounded task disposition, liveness,
   period 2..N absence, and working-blocker/swap/chain anti-overfit controls.
3. Introduce a `PlannedAction` representation carrying semantic target, predicted landing,
   stationary occupation, progress potential and invalidation state.
4. Make `WAIT` an explicit stay action. Jointly choose mover/idler landings; either preserve a
   higher-priority stationary commitment and retarget the mover, or issue a bounded yield/park
   commitment to the blocker.
5. Make the resolver verify/serialize the selected plan. Any mismatch is typed feedback; it may
   not silently replan.
6. Repair M3 locally by evaluating the same door alternatives in both adjacent states.
7. Acceptance: all 20 terminal episodes gone **with progress restored**, then raw D-1 zero under
   the accepted referee if this is to unblock the gate; no replacement P4, WAIT, longer cycle or
   target flapping.

Full cross-review:
`chatgpt_1/oscillation-cross-review-2026-08-09.md`.

No bot, candidate, detector, gate, referee, host value run, TestSession, submission, restore or
Arena action was performed or authorized.