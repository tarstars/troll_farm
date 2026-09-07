# RESULT — event-timed fruit service: defect reproduced and fixed, panel FAILS

**Verdict: PARK the tested candidate.** The named defect was reached on a real
map, repaired with one event-timed model, and measured. Panel: candidate
**137/0/55 = 137.0 vs baseline 167/6/19 = 170.0, delta -33.0**; issues **0 vs 1**,
crit 0/0. The positive W+0.5D gate is not met. No post-panel tuning.

**Reproducer (first, real state, not aggregates).** `repro/` replays candidate
`eb14e6cb` as the actual seat on unmodified 9947500..07 against the 12 adaptive
opponents in map/seat/opponent/turn order. FIRST occurrence: **9947503, seat 1,
mybot, turn 250** — worker 5 (ms1/cc2/hp1) on a near-water BANANA (4,3) s4 **f1**
cd4, door 7 away. `fruit_service` promised a first load of **2** banked at offset
**9**; the referee can put **1** fruit in it, and 2 needs 5 turns of standing,
banking at **12**. Full state, cooldown/ripening, alternatives (HARVEST 6pts/41busy vs CHOP
2 wood/8pts) and 20 following referee turns: `REPRODUCER.txt`.

**Changed files** (dispatch family only; prior family in `archive/`):
`claude_candidate_dispatch_core.rs` `1b809193`,
`test_claude_candidate_dispatch.rs` `21b93e80`; regenerated `_a.rs` `2d486601`,
`_a_module.rs` `63d08501`, `_a_tests.rs` `81cdb13e`, compact `0f20a00d`.
Unchanged: `95ee691e`, `bot.rs` `44e3daca`, `submission.rs` `7f61a6cd`.

**Mechanism.** `ripen` restates `tick_plants`; `fruit_service` now takes the
plant's real `cooldown` and simulates travel, per-turn harvesting of what is
actually hanging, the carry home and each later trip on one clock, returning the
true first load and first bank time. `jobs_for` offers on arrival-time fruit
(gate `fruits>0` removed), bills only the real first load, and the emitter WAITs
instead of harvesting an empty tree. `service_reservations` carries the worker id.

**Tests: 43 run, 43 pass** (rustc 1.90.0, `--test-threads=1`); 39 prior retained,
4 new (real-map regression, ripe-on-arrival, late ripening, no duplicate promises).

**Prerequisites (all passed).** Compact **84,562 UTF-16**; original==pruned==
compact on 16 streams/4,312 turns, 0 mismatches; per-turn max **1.08 ms**, idle;
run-local target built after freeze; **192/192 baseline arrays match gap 210944**.

**Evidence:** `PLAN.md`, `REPRODUCER.txt`, `repro/`, `summary.txt`, `panel.tsv`,
`baseline-verify.txt`, `verbs-after.txt`, `tests-4.log`, `stream-equality.log`,
`export.txt`, `hashes.txt`.

**Limitations.** Honest accounting makes service busy == elapsed, so waiting
dominates: WAIT 3091 base → **15,773**; HARVEST 11520 → 5510, CHOP 26484 → 22680.
Own score fell 231.4 → 171.1, opponent +16.4. Worst `resident` -9.0. Correct
timing did not buy strength. No commit/platform action; all jobs collected.

**Next action.** Stop waiting: forbid scheduled idle in `fruit_service` (a trip
must be fully loadable on arrival) and let the worker do other priced work in the
gap, then re-run this same 192 panel before any other change.
