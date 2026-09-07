# RESULT — orchard command ownership fixed; one fixture still fails

**Verdict: PARK, no panel.** The override is proven and fixed, but
`a_map_without_iron_needs_no_ore` still fails, so the gate is not met.

**Causal evidence (not assumed).** `AppleOrchardBot::commands` called
`replace_action(starter_id, forced)` *unconditionally* after `inner.commands`;
`reserve_orchard` only set `external_idle_unit`/`external_protected_tree` and
never disabled that path. Fix: while `orchard_active && orchardist ==
starter_id`, the layer returns inner commands verbatim after
`remember_own_plant_attempts` (memory/reconcile preserved). Three more causes,
from run-local `ORCHARD_TRACE` stderr probes (`trace-no-iron.log`,
`trace-layers.log`; probes absent from shipped artifacts, `grep -c` = 0):

1. Ignored TRAIN: `apply_pick` runs **before** `apply_train`, so a same-turn
   withdrawal drops the bank under the price. PICK is now vetoed on the hiring
   turn, and the *banked price*, not merely the open bill, is reserved
   (`orchard_reserved`) — previously all 3 funded PLUM were picked and planted.
2. `endgame_candidates` force-pushes a stand-here `CHOP` at score 10_000 and
   **returns before** `main_candidates`' crop protection runs; our idle
   orchardist thus felled the plan's own sapling 1 health/turn (t68–74) until
   the target went infeasible. Gated by `orchard_chop_forbidden`.
3. `orchard_obtainable` now tests BFS reachability, not tree existence.

`LegacyCompactLeanBananaFarmBot` was probed and **never fires**: a type-name
lead, not a callsite.

**Measured.**
 Iron fixture: hire t90→**t78**; ignored TRAINs 2→**1**; harvests
bounded `[1,1,1,2,2,2,2,2]`; `bill_paid` `[3,3,3,0,3,0]` ==
`training_cost(2,(1,1,1,1))`; workers 3 vs 2; critical 0, blocked 0, noops 1.
**Acquisition and paid spawn work; profit does not** — banked 24 vs parent 40
(the old "77 vs 40" was the parent apple-surplus loop). No-iron went from 1 to
**all 3 LEMON** harvested, surplus loop gone, still no hire.

**Changed files** (sha256): `claude_candidate_orchard.py` 64594f52,
`test_claude_candidate_orchard.rs` 54047240, `_a.rs` ebe4cd05, `_a_module.rs`
e31dc564, `_a_tests.rs` cd75c9d2, `_a.pruned.rs` ed0a23a8, `_a.min.rs` 8392b03d
(**96,153** UTF-16), `_a.mapping.json` f5e90f2b. `_control_module.rs` 526cd9cc,
`bot.rs` 44e3daca, `submission.rs` 7f61a6cd, parent 95ee691e unchanged. Prior
snapshot in `archive-prev/`.

**Tests** (rustc 1.90.0, absolute path): **16 run, 15 pass, 1 fail**. Fixture
score corrected 16→3 (its real bank). New non-vacuous
`a_sealed_fruit_source_is_not_obtainable` (live but water-sealed fruit) passes.

**Remaining failure.** No-iron map: the *opponent* fells the only LEMON by t64;
the plan replants and harvests all 3, but PLUM leaks 3→1 and banked LEMON
reaches 0, so no TRAIN fires.

**Limitations.** No panel, no timing or 16-stream certification, no
post-opening-trajectory fixture.

**Evidence** (run dir): `tests-full.log`, `tests-summary.txt`,
`trace-no-iron.log`, `trace-layers.log`, `hashes.txt`, `generate.log`.

**Next action.** Trace where banked LEMON/PLUM leave the bank after t74 in
`a_map_without_iron_needs_no_ore` (same probe, printing `inv` and every own
command per turn); close that leak, re-run all 16 fixtures, only then panel.
