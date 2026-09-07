# Frozen PLAN — complete funding commitment + actual parent continuation

Frozen 2026-09-07 07:22Z, BEFORE any source edit, in reply to the 062139
PRIMARY-REVIEW ("source only appends TRAIN if already affordable; no acquisition
phase; rollout calls model_commands on BOTH seats, not the parent continuation").
Owned: `claude_candidate_macroplan*` + `test_claude_candidate_macroplan.rs` +
this run directory. Parent `claude_candidate_policy_flat.rs` 95ee691e read-only.
The 062139 family files are archived under `archive-062139/` before editing.

## 1. Complete commitment: acquire -> deliver -> pay -> produce

`Commitment { spec, bill = training_cost(2, spec), opened, paid }`, one per game.
Every turn the state machine re-derives from the REAL state (nothing speculative
is stored):

* `outstanding[i] = max(0, bill[i] - bank[i] - carried_by_our_workers[i])` over
  the referee's own `pay` set (IRON only when iron terrain exists). Bank and
  cargo are counted once, so a reserved unit of fruit is never double-spent.
* Acquire: each worker, in id order, takes the nearest *unclaimed* source it is
  capable of working — a fruit tree of the outstanding kind (requires `hp >= 1`),
  or a walkable cell adjacent to iron (requires `chop >= 1`) — and issues one
  legal `MOVE`/`HARVEST`/`MINE`. Claimed quantity is decremented by the worker's
  free capacity, so two workers do not fund the same unit twice.
* Deliver: a worker whose cargo the bill needs banks it (`MOVE` home, then
  `DROP`) when it is full or when no source is left for it.
* Pay: when the bank alone covers the whole bill and no unit stands on the
  shack, the turn's commands carry the single `TRAIN spec`; `paid` closes the
  commitment.
* Produce: after payment the controller stops overriding; the unchanged parent
  commands the third worker for the rest of the game.

Ownership/reconciliation: a worker whose parent command this turn is `PICK`/
`PLANT` is NEVER displaced, so parent memory always describes commands that were
really issued. Cancellation restores the parent completely, and fires on roster
change, `paid`, `> 45` turns since `opened`, or no capable worker/source for an
outstanding item.

Specs (<= 2, capability-aware, predeclared): `(2,1,0,2)` chopper-miner and
`(2,1,1,1)` harvester. The controller evaluates the ONE whose outstanding
acquisition work is smaller and whose every missing item is actually gatherable
by the current roster. No parameter scan, no forced hire.

## 2. Own-side simulated continuation

Root 0 = parent commands, no commitment. Root 1 = parent commands with the
funded workers re-tasked. In BOTH branches the own-side continuation is
`self.inner.own.clone()` — the ACTUAL committed parent leaf `Policy`, the same
object the parent's own rollout uses — plus the SAME `funding_commands` state
machine on a cloned commitment. `model_commands` is used only for the opponent.
No recursion: the window ends at turn 150 and the horizon is 60, so every
simulated turn is `< START_TURN = 220`, where the real parent returns exactly
its leaf-policy commands. Clones isolate memory; the parent's own memory is
committed only by its own real call.

Horizon 60 with checkpoints at 30 and 60, identical for both roots, covering
acquisition AND payback. Selection uses the FINAL checkpoint only
(`gain = macro[60] - parent[60] >= 1.0`); the midpoint is recorded as a
diagnostic, never as a gate. ONE predeclared cheap opponent continuation
(`model_commands`, own-side) is used, identical for both roots, with the
parent's adaptive V439 opponent policy supplying the root turn — the second
permitted hypothesis is dropped to hold the interactive latency budget. This is
an explicit MODEL, not a prediction of the real opponent.

Budget: window `40 <= turn <= 150`, `>= 90` turns left, roster exactly 2, no
parent `TRAIN` this turn, `>= 20` turns between evaluations, at most 3
evaluations per game, at most 2 roots. Any `Unsupported`/critical rollout ⇒
deterministic parent fallback.

## 3. HARD prerequisite before any panel

Real activation on the actual unmodified known map family 9947500..07 against an
adaptive opponent, both seats, exact state and prefix, OFF (baseline arm) vs ON
(candidate arm) in the same paired runner: the candidate must open the plan,
obtain missing resources, bank them, pay, spawn a third worker
(`candidate_workers = 3`) and go on producing. No synthetic fixtures and no
frozen opponent command streams count for this gate. If no profitable plan
completes, NO 192-pair panel is run and the remaining budget goes to a
feasibility diagnosis of this same macro family.

## 4. Panel (only if section 3 passes)

ONE 192-pair development panel: 9947500..07 x 12 existing adaptive opponents x
both seats, `ALLOW_ANY_MAP_SEED=1`, parent 95ee691e, all 192 baseline command
arrays must match gap `20260906T210944Z-3184968-1`. Positive whole-panel
W+0.5D AND 0 candidate issues supports further evaluation. Prerequisites before
the panel: real activation, focused tests, compact <= 100,000 UTF-16, absolute
Rust 1.90, 16 original/pruned/compact equality streams including an ACTIVE macro
stream, interactive max < 50 ms measured idle. No second variant, no post-panel
tuning, no fresh maps, no subset scoring. Full referee error counts are
reported, not only the critical count.
