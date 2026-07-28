# D174a opportunistic mining — execution report

Date: 2026-07-28/29. Verdict: **CLOSED-AT-MECHANISM**. Trigger fidelity 100% (211/211
instances); the fix is verified *correct* against its own frozen conditions. It fails
because IRON was never the sole binding constraint on the live resident's real training
target — only one leg of a two-resource bottleneck B3.8/B3.9 already diagnosed.

## Phase 0 — TRAIN-trigger preflight: decisive NO, scope expanded to Variant B

Protocol requires testing, on ≥64 already-consumed tasks, whether the *unmodified*
resident issues TRAIN within 10 turns of its bank being credited to exactly cover a
cheap-helper `(1,1,0,1)` bill at workforce 2. Built a throwaway diagnostic
(`rust/src/bin/d174a_train_trigger_preflight.rs`, removed after use), 64 tasks drawn from
D173b's own already-sealed range (9,854,000-9,854,063, seat 0, resident self-play).

**Result: 0/64 (0.0%)** — decisively below the 80% mining-only threshold. Confirmed
directly in source: `MoisanBot::can_train` (`yamo_orchard_live.rs:834-845`) hard-codes
`if n >= 2 { return false }` **before ever evaluating affordability** — the live
resident cannot train a 3rd worker under any circumstance, independent of bank contents.
This is distinct from, and complementary to, D160's documented "zero affordability
windows" finding (a bank-economics fact; this is a code-gate fact).

Per protocol, this triggers **Variant B**: the same cycle carries both Delta 1
(opportunistic mining, unmodified) and the minimal TRAIN-gate repair — deleting the
`n >= 2 ||` clause from `can_train`, leaving the deadline guard and the (unchanged)
affordability check as the only remaining logic. Same one-site character as Delta 1
itself.

## What was built

**Delta 1** — `YamoBot::opportunistic_mine_rewrite(view, commands, desired)`: a new
stateless post-selection rewrite, called once from `commands()` right after
`apply_opponent_crop_harvest_contact`. It positionally zips a freshly sorted own-unit
list against `commands` (not string-parsing a unit id, so a bare `"WAIT"` — which carries
no id in this engine — is still correctly attributed) and rewrites to `MINE {id}` exactly
when: (a) `is_adjacent(iron, unit.cell)` — the identical check `iron_candidates` itself
uses; (b) `free_capacity() > 0`; (c) `training_cost(n, desired.tuple())[IRON]` exceeds
deposited + carried-across-all-own-units IRON; (d) the unit's currently-assigned command
is not a `DROP` while carrying IRON (nor, defensively, a `PICK ... IRON`, unreachable in
practice since `PICK`'s argument is a `PlantKind`). No MOVE-toward-iron candidates, no
routing, no cross-turn state.

**Delta 2** — the TRAIN-gate repair described above.

**11 new unit tests** (8 for the mining rewrite covering exactly the cases the protocol's
"Unit tests" paragraph lists, including a bare-`"WAIT"` positive case and a
carries-PLUM-not-IRON `DROP` that IS correctly displaced, proving condition (d) is
precise rather than a blanket ban; 3 for the TRAIN-gate repair — allows worker 3 when
genuinely affordable including the IRON leg, still refuses when unaffordable, still
respects the unchanged late-game deadline). `cargo test --bin yamo_orchard_live`: 34/34
pass (23 pre-existing, matching D173b's own count — no drift — + 11 new). `cargo check`:
clean, only pre-existing unrelated warnings.

## Compile-then-restore

Built `rust/src/bin/d174a_opportunistic_mining_panel.rs` (mechanical D173b→D174a
adaptation: identical task-matrix/threading/NDJSON machinery; only seed constants
(`9_855_000`), output filenames, and the debug-task env var name changed) with the fix
present in the dev copy (build-time SHA `e827317f...`). Immediately `git checkout --
rust/src/bin/yamo_orchard_live.rs`: SHA re-verified
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f` (exact match to the
pre-fix value), `git status --porcelain`/`git diff --stat` empty — confirmed clean again
at the very end of the session. Confirmed via `D174A_DEBUG_TASK=<seed>,<seat>,<opp>` that
the already-built binary still exhibits the fix post-restore.

## Delta 2 — pre-panel trigger-fidelity verification: PASS (100%, 211/211)

Ran the full panel first (jobs20, with trajectory dumping) to obtain the activation
sample: 2,048 rows, **1,595 activated (77.9%)** — much higher than D173b's 39.3%, expected
given two independent, frequently-true trigger surfaces. A one-off script
(`/tmp/d174a_trigger_fidelity_check.py`, not checked into the repo) reproduced the
panel's own divergence logic directly from the trajectory NDJSON (0 mismatches vs the
TSV column over 40 sampled tasks), recovered each task's real `desired` bill spec
empirically from its own worker-2 TRAIN command (0/40 tasks had a missing/unrecoverable
value — valid because `desired_second` freezes once workforce reaches 2), then checked
every individual MINE-emission instance attributable to the fix across those 40 tasks
against all four frozen conditions. **Result: 211/211 instances (100.0%)** pass; the
exact-ground-truth first-divergence-turn subset (where condition (d)'s control-proxy is
provably exact, not an approximation) independently confirms **40/40 (100.0%)**. GATE
(≥90%): **PASS**.

## Panel

Two full-panel invocations, 128 seeds (9,855,000–9,855,127) × 8 families × 2 seats = 2,048
tasks each: jobs20 (20 threads, with dump) — 47.29s; jobs1 (1 thread, TSV only) — 427.7s.
`sha256sum` confirms the two TSVs are byte-identical
(`402fccebbf60d3bef7250781197c6baf1e279a7e24531726954f2a2c5f9dec20`). Trajectory NDJSON:
control always (2,048 lines, ~267MB), candidate only for the 1,595 activated tasks
(~213MB). Outputs under `artifacts/experiments/d174a-opportunistic-mining/`.

## Integrity — clean

All pass: 2,048/2,048 rows, task matrix exact, all games done, 453/453 inactive tasks
byte-exact to control (0 mismatches), jobs1/jobs20 byte-identical.

## Mechanism — 1 of 4 sub-gates passes

| Gate | Result | Threshold | Pass? |
|---|---:|---:|---|
| IRON acquired per game | control 0.51, candidate **5.40** | ≥ 4.0 | **pass** |
| Unmined-reachable iron episodes at workforce≥2 | 54,354 → 51,843 (**−4.6%**) | ≥ 50% reduction | **FAIL** |
| Worker-3 TRAIN rate | control 0.0%, candidate **0.0%** | ≥ 25% | **FAIL** |
| No waste-sweep detector worse by >10% | `door_queue` +16.8%, `unbanked_carry` +13.7% | ≤ 10% each | **FAIL** |

Detector detail: `door_queue` +16.8% (1,539→1,798), `unbanked_carry` +13.7% (102→116) —
both exceed tolerance; `harvest_slack` +3.3%, `idle_with_work` +6.8%, `late_train_window`
+0.0%, `repeated_failed_command` 0/0 — all four within tolerance.

### Root cause of the mechanism failure — the decisive finding

Mining itself works exactly as designed: IRON acquisition rose **10.6×** (0.51 → 5.40
per game), comfortably clearing the ≥4.0 gate, and the trigger is 100% faithful. But
**worker-3 TRAIN is still 0/2,048 (0.0%) — the causal test B3.8/B3.9 anticipated, and the
shortfall against the 84.4% counterfactual prediction is the full 84.4 percentage
points.**

The 84.4% counterfactual figure was built around a synthetic **cheap_helper `(1,1,0,1)`**
spec. The live resident does not target that spec: it targets whatever
`YamoOpeningPolicy::TUNED_CARRY` (`preferred_min_carry: 2`) selects. Recovering the real
`desired` from all 1,595 activated candidate games via their own worker-2 TRAIN command,
the mean `training_cost(n=2, desired)` is **PLUM 6.23, LEMON 5.87, APPLE 2.00, IRON
7.12** — roughly double `cheap_helper`'s PLUM/LEMON cost of 3 each. Tracking each game's
*peak* post-workforce-2 bank against this real bill: the PLUM leg was never reached in
**1,595/1,595 games (100.0%)**; the LEMON leg was never reached in **1,587/1,595
(99.5%)**. The dominant shortfall combination — **1,264/1,595 (79.2%)** — is PLUM **and**
LEMON short simultaneously; IRON alone is essentially never the sole remaining blocker
any more (mining fixed that leg). This is exactly B3.8's own prediction, sharpened:
crediting iron alone barely moves the needle because the *real* (not synthetic-cheap)
fruit trajectory remains independently binding, and this fix — scoped by the frozen
protocol to mining only — never touches fruit accumulation.

This same mechanism explains the unmined-reachable-episode gate's near-total failure
(only 4.6% reduction against a required 50%): the ~10,000 extra IRON captured comes from
a comparatively small number of episodes where a unit, once mining, keeps re-satisfying
condition (c)'s persistent deficit turn after turn until its own carry capacity fills
(self-limiting to 1–3 turns, not a dedicated trip) — most reachable opportunities still
go unconverted. It also explains the two detector regressions: `unbanked_carry` rises
because units now hold mined IRON longer before banking it; `door_queue` rises from the
resulting extra shack traffic. Both are sensible, mechanistically-explained side effects
of opportunistic mining working as designed, not evidence of a broken trigger.

## Value — fails all six sub-gates, strongly negative

| Gate | Result | Threshold | Pass? |
|---|---:|---:|---|
| Overall mean | **−10.76** | ≥ +1.0 | **FAIL** |
| Map-clustered 95% CI | **[−13.16, −8.36]** | lower ≥ 0.0 | **FAIL** |
| Activated-subset mean (n=1,595) | **−13.82** | ≥ +1.0 | **FAIL** |
| Worst family (compact_gold) | **−21.96** | ≥ −1.0 | **FAIL** |
| Catastrophes | 95 vs control 71 | not above control | **FAIL** |
| Negative-margin mass ratio | **1.363** | ≤ 1.05× | **FAIL** |

Every one of the 8 opponent families is negative (best: `resident` −3.55; worst:
`compact_gold` −21.96). This follows directly from the mechanism finding: IRON is not
itself a scored resource (score = banked PLUM+LEMON+APPLE+BANANA+4×WOOD), and since
worker-3 training essentially never completes, every turn diverted to `MINE` is pure
opportunity cost against whatever productive fruit/wood action it displaced, with no
offsetting benefit.

## Standing conclusions

1. Delta 1 (opportunistic mining) is verified correct and effective at its own narrow
   job: 100% trigger fidelity, IRON acquisition up 10.6×, the IRON leg of the training
   bill decisively cleared.
2. The mechanism gate fails for a precisely diagnosed reason: the live resident's real
   training target's PLUM/LEMON legs (not IRON) are the binding constraint in
   effectively all games (100.0% / 99.5% never-reached), exactly matching B3.8's own
   "iron alone barely moves the needle" prediction, now confirmed directly rather than
   by counterfactual.
3. Phase 0's second finding — `can_train`'s unconditional `n >= 2` cap — was real,
   correctly diagnosed, and correctly repaired (11 unit tests, verified in isolation);
   its repair was necessary but not sufficient, because the resource bottleneck it was
   gating on remains unmet on the fruit side.
4. Because IRON is not itself scored and the trained worker it was meant to fund
   essentially never arrives, diverting productive turns to mining is a pure cost —
   explaining the uniformly, strongly negative value result across every opponent
   family.
5. A successor attempt would need to pair this mining fix with a working fruit-
   acquisition improvement addressing the *real* (TUNED_CARRY-priced) PLUM/LEMON bill,
   not the synthetic cheap_helper spec — D173's own harvest-before-chop lineage (D173a/b,
   both independently CLOSED on a different mechanism gate) is the nearest existing
   attempt at that other half, and is not a drop-in fix as-is.
6. Per protocol: no tuning of any threshold, condition, or scope attempted after any
   outcome was seen. Dev copy restored byte-exact (`fff6669b...`, re-verified twice); no
   candidate pair built (QUALIFIED-only step, not reached).

## Outputs

- `data/analysis/live-agent-6553250/d174a-opportunistic-mining-lock.json`
- `data/analysis/live-agent-6553250/d174a-opportunistic-mining-result.json`
- `data/analysis/live-agent-6553250/d174a-opportunistic-mining-result-2026-07-28.md` (this file)
- `data/analysis/live-agent-6553250/d174a-fix-as-tested.patch`
- `rust/src/bin/d174a_opportunistic_mining_panel.rs` (new panel runner)
- `cgauto/analyze_d174a_opportunistic_mining.py` (new analyzer)
- `artifacts/experiments/d174a-opportunistic-mining/` (2 TSVs + 2 trajectory NDJSON +
  `d174a-trigger-fidelity-check.json`)
- `.superpowers/sdd/d174a-phase-markers.md` / `.superpowers/sdd/d174a-report.md`

No git add/commit performed. No docs/ or ledger files touched (ledger integration is the
controller's, per protocol). No arena or network access. B4.4's files (peer-cohort
analysis, running concurrently) were never touched.
