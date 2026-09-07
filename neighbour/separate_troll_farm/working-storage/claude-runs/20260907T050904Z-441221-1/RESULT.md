# RESULT — regenerative timber: mechanism works, panel gate FAILS (-23.5)

**Verdict: PARK.** Every prerequisite passed, so the panel ran. Candidate
**146/1/45 = 146.5 vs baseline 167/6/19 = 170.0, delta -23.5** (prior dispatch
139.0). Issues **0 candidate vs 1 baseline**, crit 0/0. Gate needs positive
W+0.5D: not met. PLAN frozen before any edit (`PLAN.md`).

**Changed files** (dispatch family only; prior sources in `archive/`):
`claude_candidate_dispatch_core.rs` `6f64ced9`,
`test_claude_candidate_dispatch.rs` `05942383`; regenerated `_a.rs` `f07c76f1`,
`_a_module.rs` `36ac381d`, `_a_tests.rs` `7a00da9d`. Unchanged: parent
`95ee691e`, `bot.rs` `44e3daca`, `submission.rs` `7f61a6cd`, WORKSTATE
(full list in `hashes.txt`).

**Mechanism.** `Task::Timber(cell,kind,target)`: seed (1 banked point) → carry →
PLANT → `1+(target-1)*cooldown` growth → `ceil((base+slope*target)/chop)` felling
→ capacity-capped wood → DROP. Predeclared `KINDS x {1,2,3,4}`, no tuning.
`Job.busy` (worker-turns) split from `turns` (elapsed horizon), so growth is
serviced by other work. `Grove` ownership survives the whole cycle; a carried
seed suppresses all other offers; groves are invisible to non-owners and
pre-maturity to their owner; seeds spend a budget net of the TRAIN reservation.
Gated on chop, not harvest power, per `PlantTask`/`PickTask`.

**Tests: 34 run, 34 pass** (rustc 1.90.0, `--test-threads=1`). New: 1/1/1/1 and
hp0 1/1/0/1 full cycles, positive seed-net score; hp0 never HARVESTs; capacity
caps every delivery; carried seed never banked or re-aimed; two workers, one
seed, one plot; growth serviced by real work; near-horizon cycle rejected.
Known-map fixture ablation (ore-free known opening, same policy): ON 52 points,
**10 planted / 10 felled**; OFF 37; **+15**. Counter-case kept: with ore the hire
ledger reserves the only seeds, so the family is inert there.

**Export/latency.** Compact **81,598 UTF-16** (was 102,712) after cutting
`SearchBot`, its sim adapters and `mod simulation` as candidate-local dead
regions; all three binaries compile. original==pruned==compact on **16 streams /
4,312 turns, 0 mismatches**; per-turn max **0.935 ms**. `exact_stream_latency.py`
corrected: EOF/blank/exit/stderr rejection, bounded select, timer before flush.

**Panel** (9947500..07, 12 opponents, both seats, `ALLOW_ANY_MAP_SEED=1`, runner
`daa41e61`). **192/192 baseline command arrays match `20260906T210944Z-3184968-1`**.
Own 160.88 vs 231.35, opponent 113.86 vs 116.92, margin 47.02 vs 114.43. Worst
`resident` -9.0, `legend_balanced` -5.0; three opponents +0.0. Ring plants **329
vs 1197** (was 0), chops 2200/9851, drops 5637/17220, harvests **311/11239**,
picks 0/1065; wood 36.51/42.45; workers 2.22/2.00; TRAIN median turn 14.

**Evidence:** `PLAN.md`, `summary.txt`, `stats.txt`, `panel.tsv`,
`tests-full.log`, `stream-equality.json`, `export.txt`, `hashes.txt`.

**Limitations.** All 329 plants reuse fruit already carried (0 PICKs), so bank
withdrawal is unexercised on the panel. The dominant deficit is fruit, not
timber: harvests 311 vs 11239, own score -70.47. Ablation is a fixture, not a
panel variant. No platform action, no commit. All jobs collected.

**Next action.** Find why `jobs_for` almost never issues HARVEST on panel maps,
with a focused fixture on a harvest-rich map, then re-run this same 192 panel.
