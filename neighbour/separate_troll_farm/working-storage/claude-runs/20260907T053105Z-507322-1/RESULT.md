# RESULT — recurring fruit service: fruit gap halved, gate FAILS

**Verdict: PARK.** Hypothesis confirmed on real trajectories, fixed, measured.
Prerequisites passed, so the panel ran: candidate **142/1/49 = 142.5 vs baseline
167/6/19 = 170.0, delta -27.5**; issues **0 vs 1**, crit 0/0. The positive-W+0.5D
gate is not met. `PLAN.md` frozen before any edit.

**Reproduction (real known maps, not a fixture).** Verbs over all 192 prior games
on unmodified 9947500..07 vs the 12 adaptive opponents (`trace-verbs.txt`):
HARVEST 11520 base vs **754**, CHOP 26484 vs **28126**, DROP 17220 vs 5637 — it
out-chopped the baseline while banking a third as many loads, because `jobs_for`
priced only instantaneous fruit, one trip at 1 point/unit, against CHOP at 4.

**Changed files** (dispatch family only; priors in `archive/`):
`claude_candidate_dispatch_core.rs` `1741a60d`,
`test_claude_candidate_dispatch.rs` `fe543c6c`; regenerated `_a.rs` `eb14e6cb`,
`_a_module.rs` `2e85e9fc`, `_a_tests.rs` `a4615f4b`, compact `53c57361`.
Unchanged: `95ee691e`, `bot.rs` `44e3daca`, `submission.rs` `7f61a6cd`.

**Mechanism.** `fruit_supply` (referee growth law) feeds `fruit_service`:
repeated trips at a worker's real ms/cc/hp, banked = min(trip capacity, supply),
`busy` counting only trips used. HARVEST is priced as that service; CHOP
subtracts the service of a *reserved* asset — one tree per harvester, best first,
released on hp0 roster, contest, unreachability, own grove or endgame.
`plant_job` values a tree's lifetime, so cc1 repeat visits repay a seed.
`Job.bill_busy` rates the hire bonus on the first load; `HIRE_SPECS` gains
(1,2,2,1)/(2,2,2,1).

**Tests: 39 run, 39 pass** (rustc 1.90.0, `--test-threads=1`); 5 new, 4 updated
with in-line reasons; negatives kept.

**Effect.** HARVEST 754 → **6124**; own score 160.88 → **180.04**; fruit points
14.84 → **41.88** (base 61.56), so the 46.72 fruit deficit fell to **19.68**.
Wood 36.51 → 34.54 units, so its deficit grew 23.75 → 31.63; opponent +13.97.
Worst `resident` -8.0; three opponents +0.0.

**Prerequisites.** Compact **83,995 UTF-16**; original==pruned==compact on 16
streams / 4,312 turns, 0 mismatches; per-turn max **0.937 ms**, idle; target
built post-freeze; **192/192 baseline arrays match the gap panel**.

**Evidence** (this run directory): `PLAN.md`, `trace-verbs.txt`,
`verbs-after.txt`, `summary.txt`, `decomposition.txt`, `baseline-verify.txt`,
`panel.tsv`, `tests-4.log`, `stream-equality.log`.

**Limitations.** The ablation fixture is SYNTHETIC (`opening`, passive opponent)
and labelled so; known-map evidence is the panel only. Both hp2 specs stayed
inert. Greedy value/busy still rates one chop above one harvest trip, so
reservation stops felling without making the roster service the assets: WAIT
3091 → 8376. No commit or platform action; all jobs collected.

**Next action.** Price resource *exhaustion*, not just retention: make CHOP
compete against the roster's sustainable fruit rate once board wood runs out, so
workers service reserved assets instead of idling; re-run this panel.
