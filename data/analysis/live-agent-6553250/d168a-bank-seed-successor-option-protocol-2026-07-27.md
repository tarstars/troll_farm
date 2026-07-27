# D168a bounded BANK_SEED successor option — frozen protocol

Date: 2026-07-27
Status: frozen before implementation, running, or looking at any outcome row.

## Question

D167 froze BANK_SEED (PICK a deposited shack seed → walk → PLANT) as the resident's only
eligible successor-job class after a producer→suppressor (P→S) transition: 135/237 local
entries return this way (median latency 16 turns), and it is the dominant field path too
(71.4% of top-5 PLANT returns). D164/D167 additionally show that 22/49 field PLANT-return
cycles carry the seed *through* the suppression CHOP itself (pre-carry), while the resident
never does (0/1,024). D168 asks the causal question directly:

> Over the exact resident, does explicitly executing the BANK_SEED return — either right after
> the natural P→S transition (post-return) or by pre-fetching the seed before executing the
> suppression CHOP (pre-carry) — improve terminal value relative to leaving the resident alone?

This is a resident-relative bounded-option causal test in the tradition of D162/D165: KEEP is the
exact, unmodified resident on every task; two bounded options each route **one** worker for a
finite window, then commit or abort back to exact resident. It does not train a selector, retune
D162/D165/D166/D167 thresholds, construct a candidate, touch the platform/YT, or open reserved
maps. A pass authorizes recording a qualified option only — never Arena, submission, or resident
replacement.

## Frozen panel

Reuse the unchanged exact Yamo/Orchard resident replay on the same 1,024 consumed D148/D161 tasks
D165/D166/D167 already used: maps `9,844,136–9,844,199` (64 seeds), both seats, all eight frozen
`MacroOpponentMode` families. Reserved maps `9,844,200–9,844,215` remain untouched. No fresh maps
or seeds of any kind.

Three policies × 1,024 tasks = 3,072 rows per run. Run the complete matrix once with 1 thread and
once with 20 threads; require byte-identical sorted TSV output (SHA-256 both directions). Bulk
per-task rows go under the verified external-backed path
`artifacts/experiments/d168a-bank-seed-successor-option/` (preflight
`python3 cgauto/check_external_storage.py` before any bulk write). Protocol, lock, runner source,
analyzer, aggregate result, and human report stay in the repository.

## The shared trigger event (identical detection for both arms)

Both arms hinge on exactly **one** task-level event, defined identically to D166/D167's own
frozen "entry" (P→S transition): scanning the resident's own per-turn command list for our seat in
ascending `unit_id` order, the **first turn** on which some unit issues `CHOP <id>` while (a)
`chop power > 0`, (b) the unit's current cell is a live plant classified `Opponent`-owned under the
same-turn PLANT-attempt provenance bookkeeping frozen in D162/D166/D167, and (c) that same
`unit_id` has a confirmed prior successful-production record (a PLANT that created an `Own` crop
at its cell, or a HARVEST that gained fruit from an already-`Own`/`Natural` cell) — i.e. it is a
historical producer. Because this predicate depends only on state and commands that exist before
either option ever overrides anything, **the detected `(entry_turn, unit_id)` is identical across
all three policies for a given task** — this is verified as an integrity gate, not assumed.

- **ARM_A ("post-return")** intercepts this event *after* the referee resolves it (i.e. after
  `step()` applies the CHOP this turn) — the natural suppression action itself is never touched.
- **ARM_B ("pre-carry")** intercepts it *before* the referee resolves it — this turn's CHOP command
  for that unit is replaced by the detour's first action, delaying (not skipping) the suppression.

Each arm considers only this single, unique candidate event per task ("one arming per task per
arm, the first qualifying event only" — there is no second candidate to fall back to if the extra
gating condition below fails; the task then stays permanently inactive for that arm).

## ARM_A — post-return

Gate (checked once, using state immediately after the entry turn's `step()`): the deposited bank
holds ≥1 unit of any of PLUM/LEMON/APPLE/BANANA. If not met, ARM_A never activates for this task.
If met, activate with `activation_turn = entry_turn`, `deadline = activation_turn + 24`, and route
only the entry unit starting the *next* turn:

1. if the worker is not adjacent to its own shack (`manhattan(pos, shack) == 1`), `MOVE` toward it;
2. else, if the deposited bank holds ≥1 unit of any fruit species (re-checked fresh this turn —
   see "self-healing checks" below), `PICK` the species with the largest deposited count, ties
   broken `BANANA > APPLE > PLUM > LEMON`; otherwise **abort** (`EMPTY_BANK_AT_PICK`);
3. once the worker's total carry (all six slots) is nonzero, recompute the nearest legal empty
   cell (BFS distance from the worker's *current* cell over `walkable`, excluding every cell that
   currently holds any plant regardless of owner, ties broken by `(distance, x, y)` ascending —
   this is exactly D166/D167's own frozen `p_empty` computation, reused unchanged as "the
   resident's own legal-plant-cell preference" proxy); if none exists, **abort**
   (`NO_LEGAL_CELL`); if the worker is not there, `MOVE`; if it is there, `PLANT` the carried
   species;
4. the episode commits the instant the PLANT referee-confirms (a new `Own` crop appears at the
   intended cell and the carried count drops) — from then on the worker reverts to the exact
   resident;
5. if `game.turn >= deadline` before commit, **abort** (`HORIZON`).

Armed-worker vocabulary is strictly `{MOVE, PICK, PLANT, hold}` (`hold` = no command issued this
turn, i.e. deterministic WAIT) — never HARVEST/CHOP/PICK-of-other-species/DROP/MINE/TRAIN.

## ARM_B — pre-carry

Gate (checked once, using state immediately *before* `step()` resolves the entry turn's CHOP): the
entry unit's total carry (all six slots) is zero, **and** the deposited bank holds ≥1 unit of any
fruit species. If not met, ARM_B never activates for this task. If met, activate with
`activation_turn = entry_turn`, `deadline = activation_turn + 32`, remember
`assigned_chop_cell = ` the unit's current cell (the opponent crop the resident wanted suppressed),
and *this same turn* replace the resident's CHOP command for that unit with the detour's first
action:

1. **AcquireSeed** (while total carry is zero): identical to ARM_A steps 1–2 (MOVE to shack /
   PICK, same tie-break, same `EMPTY_BANK_AT_PICK` abort);
2. **ReturnToChop** (once carry is nonzero and the CHOP has not yet been (re-)issued): if
   `assigned_chop_cell` no longer holds any plant, **abort** (`CHOP_JOB_INVALIDATED`); if the
   worker is not there, `MOVE`; if it is there, issue `CHOP <id>` exactly once (regardless of
   whether the tree dies) and mark the CHOP phase done;
3. **SeekPlantCell** (once the CHOP has been issued): identical to ARM_A step 3 (nearest legal
   empty cell recomputed fresh, `NO_LEGAL_CELL` abort, MOVE/PLANT);
4. commit/horizon/abort semantics identical to ARM_A, deadline 32 turns from arming.

Armed-worker vocabulary is strictly `{MOVE, PICK, CHOP, PLANT, hold}` — the one addition over
ARM_A being the single re-issued CHOP.

## Operational definitions frozen here (not left to implementation discretion)

- **"Carry is empty"** = all six carry slots (`PLUM/LEMON/APPLE/BANANA/IRON/WOOD`) are zero, i.e.
  `unit.total() == 0` — the engine-native definition, stricter than a fruit-only reading, chosen
  before any row is generated.
- **"Bank holds ≥1 seed"** = the seat's deposited inventory has ≥1 unit summed over the four fruit
  species (any species qualifies; species choice is decided separately at PICK time).
- **Species tie-break** (identical for both arms, always evaluated at the moment of PICK from the
  *then-current* deposited inventory, never memoized from arming time): maximize deposited count;
  ties broken `BANANA > APPLE > PLUM > LEMON`.
- **Plant-cell selection** is recomputed fresh every turn from the worker's current position (not
  memoized at arming or at PICK time) so a cell taken by anyone else while walking is naturally
  skipped in favor of the next-nearest legal cell; this mirrors the no-memoization style already
  used by D162a's own acquisition-command routing.
- **Self-healing checks, not one-shot predictions**: the arming-time bank/carry gate only decides
  *whether to arm at all*; the PICK-time bank recheck and the plant-time legal-cell recheck are
  independent, re-evaluated every turn against the true current state, because other untouched
  own workers keep acting independently and may drain or replenish the bank, or occupy a
  candidate cell, while the armed worker is walking. A command that is generated but fails to
  transact (e.g. a same-turn race with another own worker's PICK) is not itself a forced abort;
  it is counted in telemetry and the next turn's fresh recheck naturally re-decides.
- **Defensive-only abort**: `WORKER_MISSING` (the selected unit vanished) is tracked for safety
  but is not expected to fire; it is not one of the three named abort reasons in the scientific
  question and any occurrence is reported explicitly rather than silently absorbed.

## Shared option invariants (identical to the D162 bounded-option pattern)

- Every policy calls the unmodified resident bot every turn (including every override turn) so its
  internal state stays warm; only the entry unit's own command is ever replaced, and only while its
  option is active.
- Every other worker, every turn, for every policy, executes exactly the exact resident's own
  command — this is enforced structurally (the rewrite only ever touches the one selected
  `unit_id`) and is re-verified as an integrity gate (controller-command purity).
- A task where the arm's gate never fires must be **byte-identical** to CONTROL on every terminal,
  score, hash, and workforce field (inactive-task parity).
- Each arm arms at most once per task; a completed or aborted episode never restarts.
- No opponent-identity branch, score branch, map-identity branch, outcome lookup, or learned
  coefficient anywhere in either arm.

## Integrity gates (must all pass before any value number is interpreted)

1. 1-thread and 20-thread summary TSVs are byte-identical (SHA-256 both directions);
2. CONTROL reproduces D161 exactly on every shared terminal/score/workforce/crop/action-hash/
   state-hash field for all 1,024 tasks;
3. CONTROL additionally reproduces D166/D167's own entry/return facts on this identical panel
   (1,024 tasks, 237 entries, 135 natural PLANT returns) using the byte-for-byte reused detection
   logic — an internal cross-check that this implementation's entry predicate matches the frozen
   one exactly;
4. `(entry_turn, unit_id)` is identical across CONTROL/ARM_A/ARM_B for every one of the 1,024
   tasks (the shared-trigger-event claim above, checked, not assumed);
5. every task where an arm's gate never fires is byte-identical to CONTROL (action_hash,
   state_hash, own/opponent score, workforce, crops);
6. controller-command purity: on every turn of every task, every unit other than the currently
   armed `unit_id` carries the exact resident's own command; the armed unit's command, whenever
   overridden, is drawn only from that arm's frozen vocabulary;
7. zero provenance/ownership/deposit-prediction failures, zero reward-identity error above
   `1e-6`, and workforce/crop accounting paired within each task (own/opponent/joint/ambiguous
   crop counts and successful-TRAIN counts identical in method to D161/D162/D166/D167);
8. zero platform, YT, sealed-map, candidate, resident-mutation, or Arena side effects.

A failed integrity item is repaired before any class/value number is interpreted; no threshold,
horizon, or entry-condition tuning is permitted after this run starts regardless of outcome.

## Mechanism gate (per arm, evaluated before value)

An arm is **mechanism-supported** only if, among the 1,024 tasks, its gate fires (`activated`)
on **≥32 tasks**, spanning **both seats** and **≥6 of the 8 opponent families**. If not met, that
arm **closes at mechanism** (exactly the D165 precedent) and its value numbers below are reported
descriptively only, never interpreted as a pass/fail causal result, and never rescued by loosening
the gate, adding a second candidate event, or expanding the panel.

## Value gates (per arm, only interpreted if the mechanism gate passes)

All comparisons are **paired by task against CONTROL, restricted to that arm's activated
subgroup** (inactive tasks are byte-identical to CONTROL by gate 5 above and would only dilute a
per-activation effect toward zero in exact proportion to the activation rate — the mechanism gate
already establishes that the subgroup is broad enough for this restriction to be meaningful, the
same reasoning D165 used to report an "active-subgroup" effect alongside its intention-to-treat
number). The intention-to-treat mean (paired delta over all 1,024 tasks) is reported alongside for
transparency but is not itself gated.

An arm **PASSES** only if, over its activated subgroup:

1. mean paired margin delta ≥ **+2.0**, with a map-clustered 95% CI (per-map mean deltas across
   every map contributing ≥1 activated task for that arm, normal approximation
   `mean ± 1.96·SD/√n_maps`, identical method to D162a's own clustered interval);
2. mean paired own-score delta ≥ **−0.5**;
3. the worst opponent-family mean paired margin delta (computed over each family's own activated
   tasks) is **≥ 0**;
4. catastrophe count (`margin ≤ −100`) for the arm, counted over the full 1,024-task panel, is
   **not above** CONTROL's (mathematically equivalent to comparing over the activated subgroup
   alone, since inactive tasks contribute identically to both sides of the comparison);
5. negative-margin mass (`Σ max(-margin, 0)`), same full-panel convention as (4), is **≤ 1.10 ×**
   CONTROL's.

If **either** arm passes all five, it is **QUALIFIED** (recorded only — this does not by itself
authorize a candidate, Arena, or submission; a qualified option would still need whatever a real
deployment step requires next). If **both** arms fail, the verdict is: **hand-written successor
controllers close**; BANK_SEED survives only as an option inside a future rollout-valued semantic
interface (e.g. the B2.1 direction already on the backlog), not as a hand-written controller. No
subgroup selection, no rescue, no reruns with adjusted thresholds/horizons/gates after any outcome
is seen.

## Telemetry schema (recorded per row, in addition to the D161/D162/D167a shared fields)

Per task: `entry_captured`, `entry_turn`, `entry_unit_id` (identical across policies, gate 4);
descriptive `generic_return_captured/turn/latency/verb` (the same D166/D167 "next successful
production by that unit" detector, run unmodified for all three policies — for ARM_A/ARM_B this
should coincide with the option's own committed PLANT when one occurs, an additional
cross-check); `gate_bank_ok`, `gate_carry_ok` (ARM_B only); `activated`, `activation_turn`,
`deadline`; `committed`, `committed_turn`; `aborted`, `abort_reason`
(`NONE`/`EMPTY_BANK_AT_PICK`/`NO_LEGAL_CELL`/`HORIZON`/`CHOP_JOB_INVALIDATED`/`WORKER_MISSING`);
`species_picked`, `species_planted`; `chop_cell_x/y` (ARM_B only); `plant_cell_x/y`;
per-verb override counts (`move/pick/chop/plant/hold_commands`); transaction counters
(`pick_attempts/successes`, `plant_attempts/successes`, `chop_attempts` for ARM_B);
`vocabulary_violations` (must be 0 by construction; asserted, not just counted).

## Reproducibility block (recorded in the result, `d168a`-prefixed)

SHA-256 of: this protocol; the lock file; `rust/src/bin/d168a_bank_seed_successor_option.rs`;
`cgauto/analyze_d168a_bank_seed_successor_option.py`; each of the two summary TSVs (jobs1/jobs20);
reference-input hashes (D161's resident panel, D167a's runner/local-summary, D166a's runner) to
prove the frozen upstream dependencies are unchanged. Plus exact row counts and the determinism
match/no-match boolean.

## Infrastructure

Run locally; the panel is the same size as D165/D166/D167a and finishes in minutes. Verify
`medium_data` before any bulk write. The canonical unused YT root remains
`//home/delivery_ml/research/tarstars/troll_farm`; D168a makes zero YT or platform requests.
