# D170b family-robust closed-loop option policy — mechanics-repaired result

Date: 2026-07-28
Verdict: **CLOSED-AT-PHASE-2.** The Delta-1 sticky-flag repair fully fixed
D170a's structural bug: all 8 Phase 1 fits (4 objectives × 2 seeds) now
train cleanly to completion, passing both the Stage-A and final-budget
mechanics gates under Delta-3's corrected exploration semantics. But every
one of the 8 trained policies' *deterministic* (argmax) behavior collapsed
identically to the exact-resident control (never invoking any option) on
the held-out LOBO selection blocks, so Phase 2 admitted 0/8 fits. Per the
protocol's own pre-adjudicated decision tree ("Phase 2 no admission →
CLOSE") and kill rule ("no fit admitted → the closed-loop program CLOSES
... No rescue, no budget extension"), Phase 3 (veto panel, sealed
confirmation block) was not executed; both remain untouched.

## Resume, repair-verification, and lock (before Phase 1)

Resumed after a prior agent was killed by an API connection error; its
repair work (env fix + activation diagnostic, verdict PASS) was on disk
and independently re-verified in full before freezing the lock:

- **Storage preflight**: PASS, 456,809,893,888 bytes free on `medium_data`.
- **Frozen `mod inherited` vocabulary block**: byte-identical between the
  D170a-locked env file (git commit `845d5b4`, whole-file hash matching the
  D170a lock exactly) and the repaired working tree — verified by
  extracting lines 1-771 (through the file's own "D170a-specific" banner)
  from both and sha256-hashing the slice (`5256701de0...` both sides,
  match). All 6 `git diff` hunks between the two versions begin at line
  ≥998, strictly inside the D170a-specific composition layer, nowhere near
  the frozen prefix boundary.
- **Rust focused test suite** (`cargo test --release --lib
  rl_d170a_option_policy_env`): **12/12 passed** — the 10 pre-existing tests
  plus 2 new trig-timing tests (`trig_arm_never_offered_before_the_trigger_fires`,
  `trig_arm_is_offered_on_the_decision_boundary_after_the_trigger_fires`).
- **Delta-2 activation diagnostic rerun** (same seed_base 9,850,000,
  map_pool 256, all-KEEP): field-identical to the inherited verification
  JSON except `elapsed_seconds`/`generated_at` (760.6s → 992.2s wall
  clock; both PASS; trig arms 24.5% of episodes / 100% of trigger episodes,
  opt_return 14.7% of episodes).
- All other D170a-lock-recorded file hashes (python wrapper, D170a
  trainer, frozen Rust modules `lib.rs`/`d169a_resident_option_envelope.rs`/
  `d162_resident_native_capital_option.rs`/`build.rs`/`engine.rs`/
  `official_mapgen.rs`/`state.rs`/`rl_macro.rs`) re-verified byte-identical,
  0 mismatches.

**Delta 3 required new machinery.** The Stage-A "every option ≥ 2% of
sampled decisions" gate's corrected ("conditional") semantics require
per-decision (arm, sampled-action) instrumentation inside the training
rollout loop — data the byte-unmodified D170a trainer does not capture
(only offer counts, not invoke-vs-keep per arm). The inherited
`cgauto/run_d170b_phase1_fit.py` (a thin output-path wrapper built before
Delta 3 was implemented) could not provide this and was removed,
superseded by a standalone `cgauto/train_d170b_family_robust_option_policy.py`
(full diff against the untouched D170a trainer reviewed — only Delta-3
gating + D170b output paths differ; `cgauto/train_d170a_family_robust_option_policy.py`
itself was left byte-unmodified to preserve D170a's own frozen record).
**Executor's documented reading of Delta 3's text** ("sampled-share is
computed conditional on decisions where that option was offered (≥ 2% of
its offered decisions)"): for each arm X, conditional_share(X) =
P(sampled action == INVOKE | X was the offered candidate) =
arm_invoke_counts[X] / arm_offer_counts[X]. This is the only reading under
which the quantity is not trivially 100% (a naive "X's own decisions"
denominator would coincide with the numerator), it matches the stated
intent verbatim ("the learner explores every option enough to learn about
it"), and it leaves `opt_return` a genuine, independently-failable check
post-repair — matching D170a's own flag that `opt_return`'s ~1%
unconditional share "may still fail Stage-A even after the trig fix."
Smoke-tested (synthetic telemetry + a live 2-update out-of-protocol-seed
`train_variant()` call) before committing to the real run; full rationale
in `train_d170b_family_robust_option_policy.py`'s `stage_a_gates()`
docstring and the lock's `resume_and_repair_integrity_verification_2026_07_28`
section.

Lock: `d170b-family-robust-option-policy-lock.json` (hashes of the
repaired env, both trainers, both analyzers, the activation-diagnostic
script and its JSON, all frozen Rust modules, both protocols).

## Phase 1 — all 8 fits reach `decision: "trained"`

Complete reversal of D170a's all-8-mechanics-fail outcome:

| variant | seed | stage_a pass | final pass | min conditional share | min unconditional share | fit-side mean margin |
|---|---|---|---|---|---|---|
| pooled_margin | 170101 | true | true | 0.0392 | 0.0109 | -1.622 |
| pooled_margin | 170102 | true | true | 0.0339 | 0.0126 | -1.192 |
| capped_margin | 170201 | true | true | 0.0377 | 0.0116 | -1.562 |
| capped_margin | 170202 | true | true | 0.0405 | 0.0117 | -1.240 |
| own_protected | 170301 | true | true | 0.0497 | 0.0113 | -1.239 |
| own_protected | 170302 | true | true | 0.0340 | 0.0125 | -0.958 |
| group_dro_own | 170401 | true | true | 0.1016 | 0.0089 | -2.260 |
| group_dro_own | 170402 | true | true | 0.1075 | 0.0090 | -1.928 |

All 13 arms (including the three previously-unreachable `_trig` arms) show
non-zero offer *and* invoke counts in every fit's final telemetry — the
repair holds through full training, not just the pre-training diagnostic.
Note every fit's `min_unconditional_offer_share` stays **below 0.02** —
under D170a's original (unconditional) gate formula, every one of these 8
fits would *still* have failed Stage-A (now on `opt_return`, not the trig
arms). Delta 3 is load-bearing for all 8 fits reaching `trained`, not a
formality that only mattered for the three originally-broken arms. Fit-side
mean margin is training-time telemetry from the exploring (stochastic)
policy and is **not a selector** (D131/D134 — forbidden); it is reported
for continuity only.

## Phase 2 — 0/8 fits admitted

Evaluated all 8 checkpoints deterministically (argmax) on the 8
independent 16-map LOBO selection blocks (seeds 9,851,000–9,851,127, 2,048
tasks/fit each). 1-vs-20-thread byte identity of the evaluation mechanism
confirmed (`d170b-family-robust-option-policy-phase2-thread-parity.json`,
seed base 9,851,000, map_pool 16 → identical digests).

**Every fit's deterministic policy chose "control" (KEEP) on every single
decision, for all 2,048 held-out tasks each** —
`chosen_arm_counts: {"control": 2048}`, `budget_used_rate: 0.0` in every
one of the 8 per-fit summaries. Since the policy's realized behavior is
then row-for-row identical to the exact-resident control, every
evaluation-product statistic is exactly 0.0 by construction: pooled_mean,
all 8 block_means, all 8 family_means, mean_own_score_delta, in all 8
fits. Only the `lobo_pooled_mean_at_least_1_5` admission gate fails
(0.0 < 1.5) in all 8; every other gate trivially passes (policy==control
implies catastrophes_policy==catastrophes_control, worst_block=0.0≥0,
worst_family=0.0≥-1, mean_own_score_delta=0.0≥-0.5, crop/workforce safety
exact).

**Verified not an evaluation-code defect.** Direct logit inspection of one
checkpoint (`pooled_margin`/170101) on 1,920 real decision states drawn
from the training pool (all-KEEP rollout, budget never spent, so states are
genuine mid-episode observations): P(INVOKE) ranged 0–3.27% (mean 2.33%)
across the batch; the KEEP-minus-INVOKE logit gap was ≥ 3.39 for every one
of the 1,920 states; `argmax == KEEP` for 1,920/1,920. The policy's
stochastic training-time exploration — which is exactly what fed the
non-zero Stage-A/final conditional-invoke shares reported above
(3.4%–10.8% depending on fit) — never crosses 50% confidence for INVOKE on
any observed state, so switching from sampling to greedy argmax collapses
every fit identically to the control baseline. This is a genuine trained-
policy property (the learned INVOKE probability mass stays a wide margin
under the argmax threshold everywhere sampled), not a bug in
`evaluate_deterministic` or the environment.

`admitted_count: 0`, `selected: null`, `decision: "no_admission_close"`
(`d170b-family-robust-option-policy-phase2-result.json`).

## Phase 3 — not executed

Per the frozen decision tree ("Phase 2 no admission → CLOSE"), Phase 3
(veto-panel evaluation on the consumed 1,024-task panel, sealed
confirmation on seeds 9,852,000–9,852,063) was **not run**. Both remain
untouched: the veto panel stays veto-only/unconsumed for a future
dispatch, and the sealed confirmation block stays sealed for its one
legitimate opening.

## Decision

Per the protocol's pre-adjudicated decision tree: *"Phase 2 no admission →
CLOSE."* Per the backlog kill rule: *"no fit admitted → the closed-loop
program CLOSES... No rescue, no budget extension."* **Verdict:
CLOSED-AT-PHASE-2.**

This is scientifically distinct from D170a's CLOSED-AT-PHASE-1
(implementation invalidation — the mechanics were broken, no valid outcome
was ever computed). Here the mechanics are fully valid end-to-end (repair
confirmed by the Rust unit tests, the activation diagnostic, and Phase 1's
own clean completion of all 8 fits under Delta 3), and Phase 2 produced a
real, reproducible, non-bug scientific outcome: on this architecture (16-
unit GRU + linear KEEP/INVOKE head, 4,786 actor parameters, entropy_coef
0.02, actor_keep_bias +2.0), this reward scale (paired margin / 100), and
this budget (32,768 decision-transitions ≈ 4k games), none of the four
objectives learned an INVOKE probability that clears the 50% argmax
threshold on any observed state — i.e., no objective learned a policy
whose *committed* behavior differs from "always defer to the exact-
resident baseline." Consistent with D169's own established finding that
every option is negative when always-on, and with the KEEP-favoring
architecture prior chosen for exactly that reason: the training signal
here was never strong/consistent enough, within this budget, to push any
option's learned value confidently positive.

Per dispatch scope, this is not further diagnosed or re-run here (no
threshold/architecture/budget tuning after outcomes; Phase 4 excluded from
this dispatch; no rescue attempt per the kill rule) — recorded as the
closing verdict for a future Fable review of whether a follow-on
experiment (larger budget, different reward scale, a lower KEEP prior, or
a different exploration schedule) is warranted.

## Reproducibility

- D170a protocol (inherited unchanged): `1e2ff6597969d0d2670e1c84c0871a3b595405df8114884ad39713f9920e8ec0`
- D170b repair protocol: `6f8780b19a761aec434c0e27b6712fac1efa1818bc400ac087a06933dc3b9653`
- D170a lock (cross-checked, untouched): `670f4415ba6b9f9aae173f3d63306785761813d183b20fe3e28862117898965b`
- D170b lock: see `d170b-family-robust-option-policy-lock.json` (self-hash
  in `d170b-family-robust-option-policy-result.json.lock_sha256`)
- env (`rust/src/rl_d170a_option_policy_env.rs`, repaired): `f9d47d119dcd8d443976ccb1154081eb54e99493cbcdd5012a5b4491b81c542d`
- frozen `mod inherited` prefix (lines 1-771, both old and new): `5256701de077aa42747b61c1195a62ea38bfa1348c93b4740a364d0c53faceb8`
- D170a trainer (inherited, unmodified — preserved for D170a's own record): `37da37c9eb6f9d104c1794c0b3b845f27a78a56ca77f5db929f809af9b841b9c`
- D170b trainer (new, Delta 3): `3315633ceead404919c516b2fa53f3e1edf969ea126bb38839685ad96082f0bf`
- env python wrapper (inherited, unmodified): `febc4377b9141e8253fb24330f73b25e5d96071483775a8c1b88278e0033de9f`
- D170a analyzer (reused unmodified): `d5a971d503bb055f25f306e284f7317595f32140a2a4defe5d0e639761fffa6f`
- D170b analyzer driver (new, thin): `c12527a8e8fc6639e1bb3d96b4b47601107ca32aae579c2d857aee000fd78b41`
- activation verification script: `8170a4749c31981ac2937e1b4e7130a13563accac71ab8eb26846f13c348282e`
- 8 Phase 1 fits: per-fit `checkpoint_pt_sha256`/`checkpoint_npz_sha256`
  recorded in each `d170b-family-robust-option-policy-{variant}-seed{seed}-result.json`
  and mirrored in `d170b-family-robust-option-policy-result.json.phase1.fits`.
- git rev: see `d170b-family-robust-option-policy-result.json.git_rev`
