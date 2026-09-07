# RESULT — seed investment priced; no-iron fixture still fails; NO panel

**Verdict: PARK, no panel, no strategic claim.** The seed choice is now a priced
cycle, and a new trace located the *economic* defect, but
`a_map_without_iron_needs_no_ore` still fails, so the ticket's gate (fixtures
pass first) was never reached and the 16-stream freeze and 192-dev comparison
were **not run**.

**Mechanism changed.** `orchard_ripen` prices a fresh seed with the referee's own
law (`apply_plant` -> `size 0, health tree_health(k,0), cd 0`; `tick_plants` adds
one size per `effective_cooldown`, then fruit): dry LEMON 33 ticks, water-adjacent
13. `orchard_seed_job` replaces "plant where I stand" with ONE site chosen by the
whole cycle — bank leg, plant, real ripening, `(need-1)*regrow`, `ceil(need/carry)`
round trips — rejecting sites that cannot finish by `ORCHARD_LAST_HIRE_TURN` or
that the opponent can fell (walk + `tree_health(k,4)/chop`) before first fruit.
Measured from the shack door, not the moving troll, so command scores cannot
re-pick it. `orchard_obtainable` now requires such a job, so the plan abandons
instead of replanting. New `orchard-reckless-own-crop`: `apply_reckless_finish`
rewrites MOVE->CHOP on remembered `opponent_crops`, and `remember_own_plants`
never sees the acquisition layer's PLANT — that is the actual CHOP-after-PLANT
source; a fruit tree within 2 of our own door is now exempt.

**Changed files** (sha256): `claude_candidate_orchard.py` cc161e94,
`test_claude_candidate_orchard.rs` dc8f2f32, `_a.rs` 274e3d6c, `_a_module.rs`
9220255e, `_a_tests.rs` 38391314, `_a.pruned.rs` 9b0b3879, `_a.min.rs` 508e68fa
(**97,799** UTF-16), `_a.mapping.json` 80f7f3a8. `_control_module.rs` 526cd9cc,
`bot.rs` 44e3daca, `submission.rs` 7f61a6cd, parent 95ee691e **unchanged**.

**Tests** (rustc 1.90.0, absolute toolchain path): **17 run, 16 pass, 1 fail** —
all 16 prior fixtures kept, plus `a_fresh_seed_ripens_on_the_referee_growth_
schedule` (passes; 33 vs 13 asserted against the referee, not the bot).
No-iron still: workers 2, no TRAIN, `final_inv=[1,0,3,0,0,4]`, 20 points.

**Root cause found, not fixed.** New trace: the map's only LEMON carried 3 ripe
fruits from t40; the plan emptied the safe APPLE first and the opponent felled
the LEMON at t64. Two attempts to order the deficit harvest by time-to-loss were
**worse** (46-apple surplus loop; then APPLE=1) and were reverted, unchanged.

**Evidence** (run dir): `tests-full.log`, `tests-summary.txt`, `trace.rs`,
`trace-no-iron.log`, `hashes.txt`, `generate.log`, `archive-prev/`.

**Limitations.** No panel, timing, export-equality, post-opening fixture, or
profit measurement. Iron fixture 24 vs 40 remains negative.

**Next action.** Make the orchardist take the contested LEMON before the safe
APPLE without reopening the surplus loop, then rerun
`orchard-tests --test-threads=1`.
