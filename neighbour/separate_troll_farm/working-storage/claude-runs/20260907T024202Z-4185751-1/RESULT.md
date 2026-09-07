# RESULT — orchard / near-bank fruit-production economy

**Verdict: PARK.** Runnable, high-activation controller; the frozen gate fails
both clauses. 192 pairs: **155.0 vs 170.0 (-15.0)**, own 210.88 vs 231.35,
opponent 132.00 vs 116.92, margin 78.88 vs 114.43, W154/D2/L36 vs W167/D6/L19,
issues 1 vs 1 (`move_blocked:1`); no opponent gained, worst -3 script_boss.

**Mechanism.** Unlike producer 223602 (PLANT proposed, never executed) this lives
in `main_candidates`, the executed controller: `PICK` (6200) → MOVE (6300-d) →
`PLANT` (6400) → grow → `HARVEST` (6100+f) → the parent's bank candidates —
beating chopping, losing to banking. Role: the least-valuable *hp>=1* forester.
Finite (<=2 trees, BFS<=2 of a shack door, stops turn 210); crops protected only
while the bill is unmet; `orchard_hire` trains a producer-capable spec at n==2.

**New files only** (sha256): `claude_candidate_orchard.py` d630dbd4,
`test_claude_candidate_orchard.rs` 4dc4265a, `_a.rs` bf95e979,
`_a_module.rs` 90df2c5c, `_a_tests.rs` b948f3cd, `_a.pruned.rs` bd371ca4,
`_a.min.rs` 305f15b0 (**92,661** UTF-16, guarded pruning + keep-guards),
`_control_module.rs` 526cd9cc (parent verbatim). Parent 95ee691e, `bot.rs`,
`submission.rs` unchanged.

**Checks.** rustc 1.90.0 `--test`: **13 pass, 0 fail** — real-referee
plant→growth→harvest→bank, capability-aware role (hp0 never works the orchard),
finite plan with the bill paid at `training_cost(2,spec)` (3/3/3 fruit + 3 iron,
spawned 1/1/1/1, workers 3 vs parent's 2), blocked-bank recovery, late-game
dormancy identical to the parent. Bench first, nothing else running: 16 streams, 4,312 turns, max **27.1 ms**, over_50ms 0,
`packaging_different_games` **0**. Panel 9947500..9947507, both seats, 12
opponents, `ALLOW_ANY_MAP_SEED=1`, run-local target, binary f0bb5cf3, 302.0 s.
**All 192 baseline rows match run 20260906T210944Z-3184968-1 exactly**, including
`baseline_commands` (only run-relative divergence columns differ).

**Activation is real but one-sided:** 152/192 pairs changed commands, harvests
+1,325, drops +1,223, chops -181, wood 35.19 vs 42.45. **Recruitment fired zero
times** (0 pairs reached 3 workers): 328/376 checkpoints hold 0 IRON — the
opening hire spends the dealt iron, nothing ever MINEs — and the un-kind-gated
harvest branch grinds one plum tree (20-25 PLUM, 0 LEMON). We paid ~29 points of
wood for 1-point fruit and never bought the worker.

**Evidence** (run dir): `PLAN.md` (frozen 02:47Z, pre-measurement), `tests.log`,
`bench/report.json`, `panel.tsv`, `headline.txt`, `activation.txt`,
`control-check.txt`, `hashes.txt`.

**Limitations.** One synthetic fixture board; local development pool, no ladder
claim. One failed crop-cycle does not refute the fruit economy: the recruitment
leg never actually ran.

**Next action.** Do not re-tune this variant. The blocking defect is iron: no hire
is payable (`cost[IRON] = n + chop² >= 3`) without a MINE step. Re-run only with
harvest gated to the deficit kind *and* an iron leg, else park the family.
