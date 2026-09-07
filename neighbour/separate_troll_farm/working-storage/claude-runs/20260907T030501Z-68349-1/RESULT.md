# RESULT — orchard acquisition repair

**Verdict: PRESERVE, no panel.** The acquisition plan works end-to-end on the
real referee (iron map); one regression still fails on an iron-free map. It was
not weakened, and no panel was run.

**Repair.** One fixed target `(1,1,1,1)` drives every deficit, affordability test
and the TRAIN, ending strongest-spec funding vs cheapest-spec hiring.
`orchard_bill` = `training_cost(2,target)` − bank − *all own carry*, so transit
cargo and seed withdrawals count exactly as the referee sees them; IRON is billed
only when `!view.iron.is_empty()`. New `orchard_iron_candidates`
(MOVE beside iron → `MINE`, chop≥1) and `orchard_deliver_candidates` (bank scores
−1950: under foraging, over chopping) deliver mined ore.
Harvesting is gated to kinds with open bill, over *any* reachable tree, so the
two-site cap cannot deadlock a third kind. `orchard_miner`/`orchardist` allocate
by capability; joint legality still runs through `select` +
`resolve_move_conflicts`. `orchard_feasible` abandons an unreachable target;
dormant once worker 3 exists.

**Changed files** (sha256): `claude_candidate_orchard.py` 46377f3d,
`test_claude_candidate_orchard.rs` c808f148, `_a.rs` aea57d7c, `_a_module.rs`
368710c5, `_a_tests.rs` 373060a9, `_a.pruned.rs` c5a59f4d, `_a.min.rs` b59f1d59
(**95,353** UTF-16), `_a.mapping.json` db43ec20, `_control_module.rs` 526cd9cc
(parent verbatim). `bot.rs` 44e3dace, `submission.rs` 7f61a6cd, parent 95ee691e
unchanged. Prior family archived to `archive-prev/`.

**Non-vacuous evidence.** The old prefunded fixture is **deleted** (bank
[3,3,4,6,3,0], TRAIN before first HARVEST, IRON-skipping payment loop, no-spawn
else). New `the_plan_really_acquires_fruit_and_ore_and_then_hires`: two 1/1/1/1
starters, bank `[3,0,0,0,0,0]`, zero banked/carried iron, LEMON+APPLE both short.
Candidate: `mined=[(43,1),(53,1),(65,1)]`, `iron_banked=3`, harvests LEMON×3 then
APPLE, `bill_paid=[3,3,3,0,3,0]` == `training_cost(2,(1,1,1,1))`, bank held the
full price *before* the charge, `train_turn=90`, workers **3 vs parent 2**,
`critical=0`, `blocked=0`, `commands_checked=554`; net banked score 77 vs 40.
Removing MINE, missing-kind harvest, delivery or TRAIN fails an assertion.

**Tests** (rustc 1.90.0 absolute path, `--test --crate-name`): **14 pass, 1 fail**
(`a_map_without_iron_needs_no_ore`). Unreachable-target abandonment is byte-
identical to the parent; blocked-bank and late-game dormancy pass.

**Limitations / unresolved defect.** On the iron-free board the plan banks 3
APPLE + 1 LEMON, then from t66 a layer above `YamoBot::commands` overrides the
starter (`PICK 0 LEMON`→`PLANT`→`CHOP`, then forced WAITs), unpaying the bill;
LEMON never funds and no hire occurs. A PICK veto in `YamoBot::commands` and a
`reserve_orchard` gate in `AppleOrchardBot::commands` (both shipped) leave the
stream byte-identical, so the override lives in a wrapper I did not locate. No
timing bench, no panel, no platform action.

**Evidence** (run dir): `tests-full.log`, `hashes.txt`, `build.log`,
`unchanged.txt`, `archive-prev-hashes.txt`, binary `orchard-tests`.

**Next action.** Find the wrapper rewriting the starter's command above
`AppleOrchardBot::commands` (`SecureOrchardBot`, ~L3967/L4287), gate it on
`orchard_active`, re-run all 15 fixtures, then panel.
