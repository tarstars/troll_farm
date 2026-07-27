# D167a successor-job acquisition-path recovery — frozen protocol

Date: 2026-07-27
Status: frozen before running the new extractor/runner or looking at any acquisition-path row

## Question

D166 shows that the untouched resident, after a same-worker producer→suppressor (`P→S`)
transition, naturally returns to production via PLANT in 135/237 local tasks and that field
PLANT-returns are broad (21/36 top-five, 28/41 ranks 6–20) but neither immediate affordance
(ripe own-crop HARVEST, carried-seed PLANT) is available at entry. Because carried-seed PLANT is
0/237 at entry (D166), every one of these returns is a **multi-step acquisition-and-PLANT**
continuation. D167 asks:

> What is the concrete acquisition path — where does the seed that gets PLANTed come from — between
> the suppression entry and the natural PLANT return, and does one path class dominate broadly
> enough (field breadth + local coverage) to freeze as a semantic job class?

This is a read-only representation/support audit over already-consumed data. It does not
intervene, estimate causal value, train a selector, modify the resident, create a candidate or
submission, contact the platform or YT, or open reserved/sealed maps. It does not tune D165, force
a single verb, or reopen D87/D89 grammars.

## Frozen inputs (identical to D164/D165/D166 — no new acquisition)

### Immutable field panel

Reuse snapshot `20260723T074715Z-d164a` and precisely the 392 open actor occurrences admitted by
D164/D166 (50 rank 1–5, 150 rank 6–20, 192 exact-resident). D167 additionally restricts to the
**PLANT-return subsequence** already selected by D166's frozen field extraction:

- rank 1–5: the 21/36 cycles with `return_verb == "PLANT"`;
- rank 6–20: the 28/41 cycles with `return_verb == "PLANT"`.

The exact-resident cohort is out of scope for D167 field gates (D166 already showed 21/21 resident
cycles are PLANT, but the resident cohort is not a "top agent" for the rule-3 field gate). Do not
read the eleven sealed confirmation games.

### Consumed local panel

Reuse the unchanged exact Yamo/Orchard resident replay on the identical D148/D161 maps
`9,844,136–9,844,199`, both seats, all eight frozen `MacroOpponentMode` families: the same 1,024
tasks D165/D166 already consumed. D167 restricts interpretation to the **135/237** tasks where
D166's own frozen entry+natural-return criteria both fire and `natural_return_verb == PLANT`
(D166 already proved this is all 135). Reserved maps `9,844,200–9,844,215` remain untouched.

Bulk per-turn/per-event products go under the verified external-backed path
`artifacts/experiments/d167a-successor-acquisition-path` (preflight
`cgauto/check_external_storage.py` first). Compact protocol, lock, extractor/runner, aggregate
result, and report remain in the repository.

## Concretized extraction algorithm

### Local (Rust): `rust/src/bin/d167a_successor_acquisition_path.rs`

Extends `d166_producer_job_successor_affordance.rs` byte-for-byte on entry/return detection: same
map generation, same resident, same eight opponent modes, same `Owner` provenance bookkeeping
(`Own`/`Opponent`/`Natural`/`Joint`/`Ambiguous`), same historical-producer→suppression entry rule,
and the same natural-return rule (next successful production event by the identical `unit_id`).
Integrity requires this replay to reproduce D166's 1,024/237/135 counts and all D161-shared
terminal/score/workforce/crop/hash fields exactly.

New instrumentation, active only for a task once entry is captured (`entry_captured == 1`):
starting at `entry_turn` (the turn of the triggering CHOP, included as the trace's first waypoint
for context) through `natural_return_turn` inclusive (or through game end if no natural return
occurs), record one trace row per turn in which the selected `unit_id` executes a command,
covering **every** verb (not only own-crop verbs): MOVE, HARVEST, PLANT, CHOP, PICK, DROP, MINE.
Each row carries: turn, position before/after, verb, success, per-item (PLUM/LEMON/APPLE/BANANA/
IRON/WOOD) gained and spent counts, the target cell's pre-action ownership (`Own`/`Opponent`/
`Natural`/`Joint`/`Ambiguous`/`None`) and plant kind, and (for PLANT) the created crop's ownership.
Recording stops the turn the natural return fires (that PLANT row is the trace's last row).

**Species-provenance ledger (applied identically here and in the field extractor).** Let `k` be the
species of the return PLANT (`natural_return`'s crop kind). Walk the trace in turn order
maintaining a multiset of class tags currently "held" for species `k` (empty at `entry_turn`,
matching D166's confirmed 0/237 carried-seed-at-entry fact):

- a successful PICK that gains `k` adds a `BANK` tag (one per unit gained);
- a successful HARVEST that gains `k` from a cell whose pre-action ownership is `Own` or `Natural`
  adds a `FIELD` tag;
- a successful HARVEST that gains `k` from a cell whose pre-action ownership is `Opponent` adds an
  `OPPONENT` tag;
- a successful HARVEST that gains `k` from a `Joint`/`Ambiguous` cell adds an `OTHER` tag;
- a successful DROP that spends `k` clears every tag for `k` (the referee banks the whole carry, so
  any later PLANT of `k` must be re-acquired after this point — a fresh PICK from the newly banked
  stock is legitimately `BANK` again);
- the terminal PLANT spends exactly one unit of `k`; the **path class** is the single tag present
  in the multiset at that instant if exactly one distinct tag is present, otherwise
  `OTHER_MIXED` (recorded together with the distinct tag set, e.g. `BANK+FIELD`).

An empty tag multiset at the terminal PLANT is impossible given the engine (fruit carry can only
increase via HARVEST or PICK: verified from `apply_harvest`/`apply_pick`/`apply_plant`/
`apply_chop`/`apply_mine`/`apply_train` in `rust/src/game/engine.rs`) and is treated as an integrity
failure, not a silent classification, if it ever occurs.

**Descriptive fields (non-gating).** Per task: `path_length_turns` (= `return_turn - entry_turn`,
cross-checked against D166's `natural_return_latency`), `distinct_cells_visited` (count of distinct
worker cells strictly after `entry_turn` through `return_turn`), `material_waypoints` (count of
successful HARVEST/PICK/DROP/CHOP/MINE actions strictly between `entry_turn` and
`natural_return_turn`), `species_planted`, and `single_persistent_job` — **operationalized** as
`idle_turns == 0`, where an idle turn is a turn strictly between `entry_turn` and
`natural_return_turn` in which the worker's position is unchanged from the previous turn **and** it
executes no successful material action. This is a coarse behavioral proxy for "the scheduler is
already following one committed plan with no wasted turns" — the resident bot is a closed-source
heuristic with no exposed persistent per-worker job state, so this is observational, not an
inspection of bot internals, and it is diagnostic only (it gates nothing in §Gates).

Output: two TSVs per thread count (`jobs1`/`jobs20`): (a) a per-task summary row extending D166's
existing 106-column schema with appended columns (`acquisition_class`, `acquisition_tags`,
`acquisition_event_count`, `bank_units`, `field_units`, `opponent_units`, `other_units`,
`path_length_turns`, `distinct_cells_visited`, `material_waypoints`, `single_persistent_job`,
`species_planted`, `ledger_integrity_ok`); (b) a long-format per-event table (one row per recorded
turn, all 1,024 tasks' `entry_captured` rows only). Row order is sorted by
`(map_seed, seat, opponent_index[, turn])` regardless of thread count, matching D166's determinism
convention.

### Field (Python): `cgauto/extract_d167a_field_acquisition_classes.py`

Reuses `cgauto.analyze_d164a_current_field_macro_transitions.reconstruct_generation_actions` (the
same generation/origin reconstruction already cross-validated against an independent legacy
reference in D101) and `cgauto.extract_d166a_field_return_classes` (`occurrences`, `first_cycle`,
`role`, cycle selection) with **zero changes to either file**. For each of the 21 top-5 and 28
rank-6-20 PLANT-return cycles already selected by D166, take the full actor event list (every verb,
not just material-successful P/S events) for the cycle's `worker_ordinal`, restricted to
`suppression_turn < turn <= return_turn`, and apply the **identical species-provenance ledger**
above, with `target_origin` read directly from the event's `target_origin`/`created_origin` field
(`actor`→`Own`, `opponent`→`Opponent`, `natural`→`Natural`, `joint`/`ambiguous`/`unknown`→`Other`).
Additionally verify, from the decoded state at `suppression_turn`, that the cycle's worker carries
zero units of every fruit species immediately after the suppression turn (the field-side analogue
of D166's local 0/237 carried-seed-at-entry fact); record this as an integrity diagnostic.

Output: sorted JSONL (one row per of the 49 cycles), byte-identical whether produced with
`--jobs 1` or `--jobs 20` (`ProcessPoolExecutor`, matching D166's field-extractor pattern).

### Orchestrator: `cgauto/analyze_d167a_successor_acquisition_path.py`

Verifies the lock (frozen input hashes), reads both local TSVs and both field JSONL files,
reproduces D166's integrity gates over the local panel (1,024/237/135 counts; D161 parity on
shared columns; zero provenance/ownership/history/restart failures) and D164/D166's field cohort
counts (36/41 cycles; 21/28 PLANT subsets), checks the two determinism requirements (§Determinism),
computes the class-distribution tables, evaluates the frozen gates (§Gates), and writes the result
JSON plus the numbers backing the result Markdown.

## Determinism (frozen requirement 4)

- Run the local Rust extraction with `THREADS=1` and `THREADS=20` on the full 1,024-task matrix;
  SHA-256 both the per-task summary TSV and the per-event trace TSV; require byte-identical pairs.
- Run the field Python extraction with `--jobs 1` and `--jobs 20`; SHA-256 both JSONL outputs;
  require byte-identical pairs.
- Record all four SHA-256 pairs (and match/no-match) in the result.

## Gates (frozen — preregistered, not adjusted after seeing data)

A path class is **FROZEN-ELIGIBLE** iff:

1. **Field:** it accounts for at least 60% of the 21 top-five PLANT returns, **and** it appears in
   at least 4 of the 5 top-five agents, **and** it appears in both seats (all measured over the
   21 top-5 PLANT-return cycles only — ranks 6–20 are reported descriptively, not gating); **and**
2. **Local:** at least 90 of the 135 local natural PLANT returns fall in the same class.

If no class passes both (i) and (ii) simultaneously, the verdict is: **close hand-written successor
controllers; the successor branch proceeds only as trajectory-valued semantic actions with short
resident-backed rollouts** (record the verdict; do not implement those rollouts here). Local
coverage or outcome data may never rescue a class that fails the field gate, and vice versa — no
post-hoc threshold, horizon, or entry-condition tuning is permitted after this run starts.

## Integrity gates (must pass before any class-distribution number is interpreted)

1. local one-thread and 20-thread summary TSVs are byte-identical; likewise the per-event trace
   TSVs;
2. the local summary reproduces D166 exactly on every shared column (1,024 rows; 237 entries; 135
   natural PLANT returns; identical `entry_turn`/`selected_unit_id`/`prior_verb`/`natural_return_*`
   values) and reproduces D161 on every shared terminal/score/workforce/crop/hash field;
3. `ledger_integrity_ok` is true for all 135 local returns and all 49 field cycles (nonempty tag
   multiset at the terminal PLANT, and — where independently checkable — the ledger's running
   per-species total matches the unit's actual simulated/decoded carry count);
4. field one-process and 20-process JSONL outputs are byte-identical and each contains exactly 21
   top-5 and 28 rank-6-20 rows reproducing D166's cycle selection exactly (same actor/game/turns);
5. carried-seed-at-entry is confirmed zero for every local return task (already established by
   D166) and for every field cycle (new check here); and
6. zero platform, YT, sealed-map, candidate, resident-mutation, or arena side effects.

A failed integrity item is repaired without interpreting the class distribution or gates.

## Reproducibility block (recorded in the result, `d167a`-prefixed)

SHA-256 of: this protocol file; the lock file; `rust/src/bin/d167a_successor_acquisition_path.rs`;
`cgauto/extract_d167a_field_acquisition_classes.py`;
`cgauto/analyze_d167a_successor_acquisition_path.py`; each of the four local TSVs (jobs1/jobs20 ×
summary/events); each of the two field JSONLs (jobs1/jobs20). Plus exact row counts for every
product and the two determinism match/no-match booleans.

## Decision

- If a class passes both field and local gates: record which class and that it is FROZEN-ELIGIBLE.
  This alone does not authorize a candidate, Arena, fresh maps, or submission — a hand-written
  D168 successor option would still need its own resident-fallback causal test.
- If no class passes both gates: close hand-written successor controllers; the next representation
  is trajectory-valued semantic successor-job value (KEEP / acquire-and-PLANT / current-own-crop
  HARVEST) evaluated with short resident-backed rollouts, exactly as D166 already recommended — do
  not implement the rollout controller in D167a itself.

Run locally; both panels are small (135 and 49 rows of interest, 1,024 and 392 rows of scaffolding)
and expected to finish in minutes. Verify `medium_data` before all bulk writes. The canonical unused
YT root remains `//home/delivery_ml/research/tarstars/troll_farm`.
