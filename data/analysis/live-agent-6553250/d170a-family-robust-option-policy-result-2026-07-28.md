# D170a family-robust closed-loop option policy — resume result

Date: 2026-07-28
Verdict: **CLOSED-AT-PHASE-1.** A prior agent's Phase 0 (env/trainer/lock) and Phase 1
launch (8 fits: 4 objectives × 2 seeds) were inherited across a controlled interruption
(USB unmount pause) and their integrity fully verified — but all 8 Phase 1 fits
deterministically and reproducibly **fail their own pre-registered Stage-A mechanics
gate**, root-caused to a structural bug in the new D170a sequential-decision composition
code (not the frozen D162/D163/D167/D168/D169a vocabulary, which remains hash-verified
byte-identical). Per the protocol's own pre-adjudicated decision tree ("Phase 1
mechanics-fail on all fits → CLOSE"), Phase 2/3 were not executed against these fits.
Phase 2/3 evaluation code was built out and independently smoke-tested and is ready for a
future corrected re-run.

## Resume-integrity verification (inheritance)

- **Storage preflight**: PASS, 456,809,893,888 bytes free on `medium_data`.
- **Lock hash re-verification**: all 12 files in the original Phase-0/1 `sha256` table
  re-hashed from the live working tree — 0 mismatches. No mid-edit corruption from the
  interruption.
- **Cross-check vs D169a's own lock**: the 7 frozen-module hashes D170a's lock shares with
  `d169a-resident-option-interface-envelope-lock.json` (`engine.rs`, `build.rs`,
  `official_mapgen.rs`, `d162_resident_native_capital_option.rs`, `rl_macro.rs`,
  `d169a_resident_option_envelope.rs`, `state.rs`) match D169a's own record exactly, not
  merely D170a's self-consistency.
- **Rust unit tests**: `cargo test --release --lib rl_d170a_option_policy_env` — **10/10
  passed**, including the exact tests the Phase-0 marker claimed (control-parity,
  `control_margin`/`paired_margin` identity, budget ≤ 1 activation, deterministic replay,
  `batch_task_assignment_is_thread_count_invariant`, exhaustive `task_index` coverage
  including zero-decision episodes).
- **Phase 2/3 code**: `cgauto/analyze_d170a_family_robust_option_policy.py` was already
  present (written 08:14, six minutes before the first Phase 1 checkpoint existed —
  written but never exercised against a real fit). Read in full: LOBO block-wise
  admission gates, veto gates, confirmation gates, clustered-cluster-bootstrap CI, and the
  selection tie-break (max worst-held-block → max pooled mean → lowest seed) all match the
  protocol/lock text verbatim. Catastrophe (`margin ≤ −100`) and negative-mass
  (`Σ max(0, −margin)`) conventions match the established house pattern (D34/D35c/D80a/
  D89a/D159a/D162a/D168a/D169a). `.pt` confirmed canonical (the analyzer loads `.pt`;
  `.npz` is a numpy mirror, byte-for-byte value-identical to `.pt` on every fit).
  Smoke-tested end-to-end (`evaluate_deterministic` → `summarize_rows` →
  `admission_gates`/`veto_gates`/`confirmation_gates`/`clustered_ci`) against a
  freshly-initialized, untrained model on an out-of-protocol seed base (1, `map_pool=2`,
  disjoint from all three declared D170a ranges, to avoid touching train/selection/veto/
  confirmation data with a throwaway model): ran cleanly, 32/32 rows collected, the
  untrained KEEP-biased policy reproduced byte-exact-control (`paired_margin=0`
  everywhere) as expected, and every gate correctly evaluated False. No code defects
  found in the Phase 2/3 machinery itself.

## Phase 1 fit validation — all 8 fail, reproducibly

Checked each of the 8 inherited result JSONs against the resume checklist (parses;
Stage-A sanity record; final-training summary; checkpoints load; ≤ 12,288 params). All 8
have well-formed, internally-consistent Stage-A telemetry, but **none has a
final-training summary** — the trainer's own `stage_a_gates()` (locked, pre-registered
code) recorded `stage_a.verdict.mechanics_pass = false` and
`decision = "mechanics_fail_at_stage_a"` for every one of the 8, with `final = null` by
design (Stage-A failure stops the fit immediately, per protocol). The failing gate in all
8 is `every_option_at_least_2pct_of_sampled_decisions`: `opt_fruit_trig`,
`opt_iron_trig`, `opt_protect_trig` are at **exactly 0.0 share in all 8 fits** (never once
offered across 8,192 decisions / ~1,350–1,470 episodes each). `opt_return` is also below
the 2% floor in all 8 (0.79%–1.06%) — a much softer, non-structural shortfall, flagged but
not diagnosed further here. Every other Stage-A gate (finite losses, crop safety exact,
zero reward-identity errors, exact transition budget) passed cleanly in all 8.

**Rerun performed per the resume protocol's own instruction** ("delete its outputs and
RERUN that fit exactly per protocol — a rerun reproduces it"): backed up all 8 original
result JSONs + checkpoints, deleted them, and reran all 8 fits from scratch as 8
concurrent single-threaded OS processes (`RAYON_NUM_THREADS=1`,
`torch.set_num_threads(1)`) against the unmodified locked trainer/env code. **All 8
reruns reproduced their originals exactly**: identical `decision`, identical
`stage_a.verdict.gates`, identical `arm_offer_counts` (including the three exact-zero
trig arms), identical `global_decisions`/`total_episodes`/loss means, and byte-identical
checkpoint SHA-256 (both `.pt` and `.npz`) for every fit. This proves the mechanics-fail
is fully deterministic and was **not** an artifact of the interruption — Phase 1 had
already finished writing all 8 outputs before the interruption occurred.

## Root cause

Structural (not stochastic) bug in the new D170a-specific composition layer of
`rust/src/rl_d170a_option_policy_env.rs` (the section below the file's own
"D170a-specific" banner — **not** the frozen `mod inherited` vocabulary block copied
byte-for-byte from D162/D163/D167/D168/D169a, which remains hash-verified unmodified).

In `D170aEnv::step_one_turn` (~line 1270), `self.opp_worker_trigger_turn` is set to
`current_turn` — the **pre-increment** turn value captured at function entry — before
that turn's `step(&mut self.game, …)` engine call (`game/engine.rs:805`) advances
`self.game.turn` by 1. `D170aEnv::refresh_candidates` (~line 1149) later checks
`self.opp_worker_trigger_turn == self.game.turn` to enqueue the corresponding `_trig`
arm — but `refresh_candidates` only ever runs either (a) *before* that turn's
`step_one_turn` call (the trigger isn't set yet for this turn), or (b) on the *next*
`resume()` loop iteration, by which point `self.game.turn` has already advanced past the
stored value. The equality is therefore **never satisfiable**, for any trajectory, on any
seed. `OPT_RETURN` in the same file correctly handles the equivalent post-step timing via
a sticky `self.return_pending` boolean flag set in `step_one_turn` and consumed on the
next `refresh_candidates()` call — the same pattern was simply not applied to the three
resource `_trig` arms.

Evidence (four independent angles, converging):
1. Static trace of the sole enqueue site confirms the condition is unreachable by
   construction.
2. 8/8 independent fits (different seeds/objectives) show the identical exact-zero count
   for all three trig arms across ~11,200 episodes total — 0% is not what stochastic
   rarity looks like.
3. D169a's own frozen, hash-verified reference implementation of the identical
   vocabulary logic shows **nonzero** activity for the same arms:
   `opt_fruit_trig` won 25/1,024 and `opt_iron_trig` won 13/1,024 hindsight-envelope
   tasks (`d169a-resident-option-interface-envelope-result.json`,
   `.lock.selection.selection_counts`) — the underlying game-level event (opponent
   reaching ≥ 3 workers) is not itself rare.
4. Direct empirical field-level diagnostic on the *actual* D170a training pool
   (`seed_base=9,850,000`, `map_pool=256`, 303 episodes, 2,880 decision observations,
   all-KEEP deterministic so as not to spend budget): `opp_worker_trigger_seen` (state
   feature 55) was true in **451/2,880 (15.7%)** of observed decision points — yet
   `trig_candidate_offered` was **0/2,880**. The underlying event fires often; the option
   is never exposed.

## Decision

Per the frozen protocol's own decision tree: *"Phase 1 mechanics-fail on all fits →
CLOSE (record; Tier 0/3)."* No fit reached `decision == "trained"`; there is no valid
checkpoint to LOBO-evaluate in Phase 2. Separately from bare validity, a policy trained
where 3 of the declared 13 arms were structurally unreachable would silently be a test of
a truncated 10-arm vocabulary mislabeled as the full D169 option vocabulary — running
Phase 2/3 against these fits would risk a false research conclusion, not just a
formality violation. This is a distinct, *prior* decision-tree branch from "Phase 2 no
admission" and is recorded as such (not as CLOSED-AT-PHASE-2).

Per the protocol's explicit prohibitions ("no threshold/λ/τ/cap/architecture tuning after
outcomes"; "frozen modules untouched") and the resume dispatch's own framing (the lock is
authoritative for Phase-0/1 code), the resuming agent did **not** patch
`rl_d170a_option_policy_env.rs` and re-run. Fixing the bug, re-freezing a new lock, and
re-running Phase 1 is a new experiment decision requiring its own authorization/dispatch,
not a unilateral resume-agent action.

**Not done, by design:** `.superpowers/sdd/d170a-phase-1-done.md` was not written (its
stated precondition — "only after all 8 validate" — was not met, even after the
prescribed rerun). Phase 2 was not executed against the real checkpoints. Phase 3
veto/confirmation was not reached. Phase 4 was out of scope regardless and is moot here.
No frozen code was patched. No git add/commit; `docs/` and ledger volumes untouched, per
dispatch.

## Recommendation for the next dispatch

Fix the off-by-one in the resource `_trig` arming check (mirror `OPT_RETURN`'s sticky-flag
pattern), re-verify the fix's trig-activation rate is in the same ballpark as D169a's own
reference implementation, re-freeze a new lock (new hash for the env file), and re-run
Phase 1 from scratch on the same seeds under the corrected code. Separately note:
`opt_return`'s own sub-2% share (0.79%–1.06% across all 8 fits, stable and non-zero) may
still fail Stage-A even after the trig fix and would need its own look — flagged, not
diagnosed, here.

## Reproducibility

- protocol: `1e2ff6597969d0d2670e1c84c0871a3b595405df8114884ad39713f9920e8ec0`
- lock (after this resume's additions):
  `670f4415ba6b9f9aae173f3d63306785761813d183b20fe3e28862117898965b`
- env (`rust/src/rl_d170a_option_policy_env.rs`, inherited, unmodified):
  `4ea4a215731e83c73893410579ab1c27e866e7ffbcf2d0531cec3ad7435ed963`
- trainer (`cgauto/train_d170a_family_robust_option_policy.py`, inherited, unmodified):
  `37da37c9eb6f9d104c1794c0b3b845f27a78a56ca77f5db929f809af9b841b9c`
- env wrapper (`cgauto/rl_d170a_option_policy_env.py`, inherited, unmodified):
  `febc4377b9141e8253fb24330f73b25e5d96071483775a8c1b88278e0033de9f`
- analyzer (`cgauto/analyze_d170a_family_robust_option_policy.py`, resume addition,
  reviewed + smoke-tested, unmodified from what the prior agent wrote):
  `d5a971d503bb055f25f306e284f7317595f32140a2a4defe5d0e639761fffa6f`
- 8 Phase 1 fits: each rerun's `checkpoint_pt_sha256`/`checkpoint_npz_sha256` recorded
  per-fit in `d170a-family-robust-option-policy-result-2026-07-28.json`
  (`phase1_fit_validation.per_fit`); every rerun matched its pre-rerun original exactly.
- git rev: `d2e962f7aa16c1ddc4fe71632a1c2e003688f67e`
