# E7a remaining-deletion inventory — round 14 planning (claude_1, 2026-08-03)

Parent analyzed: `local_codex_1/e7a-iterative-logical-deletion/candidate-r13-remove-movement-tie-mode.rs`,
57,677 bytes, SHA-256 `6b9fdc99c960b4ddc969729d9452b1e5b7b252b06f8314a8567e969e27f5ba34`.

Method: full-source structural extraction (all 13 remaining structs, both enums, module map,
every policy-field read site), plus an optimized compile with rustc 1.97.1 dead-code lints
enabled — **zero compiler-detectable dead items remain** after rounds 1–13. Everything below is
therefore semantic deadness: code unreachable or value-fixed given the sole executable factory,
exactly the class the protocol's rounds 4–13 consumed.

## Ranked deletion candidates (at most five, strongest first)

### 1. Single-use `with_opening_policy` constructor + dead default announcement — PROPOSED ROUND 14

- Class: fixed-value configuration plumbing (exact mirror of accepted round 1, which inlined
  `SecureOrchardBot::with_policy`).
- Invariant: `with_opening_policy` appears exactly twice in the source — its definition and its
  sole call inside `tuned_carry_regeneration_transit_idle_harvest`. The default
  `announcement:"yamo-waypoint-rust"` it writes is overwritten by the factory's
  `bot.announcement="yamo-carry-regen-transit-idle-harvest-rust";` before any read: the single
  read site is `format!("MSG {}",self.announcement)` inside `commands`, which cannot execute
  before construction completes.
- Replacement: inline the struct literal directly into the factory with
  `announcement:"yamo-carry-regen-transit-idle-harvest-rust"` and
  `opening_policy:YamoOpeningPolicy::TUNED_CARRY`; delete the constructor and the
  `let mut bot … bot.announcement … bot` two-step. Every other field value is preserved exactly.
- Rejection condition: any third occurrence of `with_opening_policy`, any second read or write
  of `announcement`, or any construction of `YamoBot` outside the factory.
- Estimated saving: ~230 bytes.

### 2. Single-valued `YamoOpeningPolicy` configuration record — candidate rounds 15+

- Class: fixed-value configuration plumbing.
- Invariant: `YamoOpeningPolicy` has exactly one value in the whole program — the
  `TUNED_CARRY` const (`train_horizon:15, preferred_min_carry:2, max_carry_capacity:3,
  preferred_min_chop:1, max_chop_power:3, max_extra_eta:15, hard_train_turn:35`). All reads go
  through `policy.<field>` / `self.opening_policy.<field>`.
- Replacement: per-field literal inlining in the style of accepted rounds 4–5 (e.g.
  `policy.hard_train_turn` → `35`), field-by-field as separate rounds, ending with deletion of
  the struct, the const, the `opening_policy` field, and the `policy` parameters. Read map
  gathered this session: `train_horizon` 1 read, `preferred_min_carry` 2, `max_carry_capacity`
  4, `preferred_min_chop` 2, `max_chop_power` 4, `max_extra_eta` 2, `hard_train_turn` 2.
- Caution: several reads are `.clamp(1,3)`-wrapped; the literal must keep the clamp expression
  untouched (`3.clamp(1,3)`), never pre-folded — folding is a second logical change.
- Rejection condition: a second `YamoOpeningPolicy` construction, or a read through anything
  but the factory-fixed value.
- Estimated saving: ~700–900 bytes across the sub-rounds.

### 3. Unused derived trait impls (`Debug` on 13 types; `Hash` on `PlantKind`) — low priority

- Class: provably unreachable generated code. `{:?}` formatting occurs zero times; no
  `HashMap`/`HashSet` exists (all collections are BTree, which need `Ord`, not `Hash`).
- Caution: this deletes compiler-*generated* dead impls by editing derive lists at 14 sites;
  flagging the classification risk openly — an integrator may read multi-site derive trimming
  as formatting-adjacent. Recommend explicit integrator approval before spending a round on it.
- Estimated saving: ~100 bytes.

### 4–5. No further defensible candidates found this pass

No other block has a nameable invariant tighter than "looks unused". If round 14 is accepted I
will re-run the inventory against the round-14 source before proposing round 15.

## Active behavior that must remain (verified this pass)

- `external_idle_unit` / `external_protected_tree`: dynamically written by `SecureOrchardBot`
  every turn from the orchard-reservation state — the wrapper's live channel into `YamoBot`.
- `announced`/`announcement` MSG emission: first-turn live output; parity-visible.
- All four `OrchardPhase` variants: `Abandoned` is reachable from seven distinct sites
  (turn>100 dormancy timeout, lost starter, failed seed continuation, plant-attempted
  collapse, …).
- `alternate_doors`, `initial_natural`, `plant_attempted`, `opening_abandoned`: all read on
  live paths.
- `PlantKind::parse`, `Stats::tuple`, `total_carried`, `free_capacity`, `as_str`,
  `item_index`: all called (the earlier zero-warning compile confirms no orphan helpers).
- Modules `game::{types,rules,nav,protocol}` and `bot::moisan`: all load-bearing;
  `MoisanBot::focus_type` is the sacred-source anchor named by the fixture harness.
