# D168a bounded BANK_SEED successor option — result

Date: 2026-07-27
Verdict: **hand-written successor controllers CLOSE.** Both bounded options (ARM_A
post-return, ARM_B pre-carry) pass the mechanism gate cleanly (164/1,024 tasks each,
both seats, 7/8 opponent families) but **fail the value gate decisively** — mean paired
margin over the activated subgroup is strongly *negative* for both arms (ARM_A −6.73,
ARM_B −8.21), the opposite sign of the required ≥+2.0. BANK_SEED survives only as an
option inside a future rollout-valued semantic interface (e.g. B2.1), never as a
hand-written controller.

## Reproducible execution

D168a extends D166/D167's frozen entry-detection predicate byte-for-byte (new Rust bin
`d168a_bank_seed_successor_option.rs`) and adds two bounded options keyed to the shared
trigger event (the task's first historical-producer CHOP on a live opponent-owned
plant), each routing at most one worker for a finite window before committing or
aborting back to the exact resident. All 1,024 consumed D148/D161 tasks × 3 policies
(control, ARM_A, ARM_B) = 3,072 rows were run at 1 and 20 threads.

- **Determinism**: 1-thread (309.694s) and 20-thread (33.451s, 9.26×) summary TSVs are
  byte-identical, SHA-256 `d0620184bb3bbb9a959d0d4bf88de3e2cc727f9c2d028b45f07370b46b7814c1`
  both directions.
- **CONTROL reproduces D161** exactly on all 20 shared terminal/score/workforce/crop/
  hash fields for all 1,024 tasks (0 mismatches).
- **CONTROL reproduces D166/D167's own entry/return facts** on this identical panel: 237
  entries, 135 natural PLANT returns — exact match against D167a's frozen local summary
  (0 mismatches on `entry_turn`/`entry_unit_id`/`generic_return_turn`/verb).
- **Entry event is identical across all 3 policies** for every one of the 1,024 tasks (0
  mismatches on `entry_captured`/`entry_turn`/`entry_unit_id`) — confirming neither arm's
  bookkeeping silently diverges before its own first override, exactly as the shared-
  trigger-event design requires.
- **Inactive tasks are byte-exact vs CONTROL**: checked across all 1,720 (task, arm)
  pairs where that arm's gate never fired — 0 mismatches on the full game-relevant field
  set (scores, action/state hash, workforce, crops).
- **Controller-command purity** is verified empirically (not just by code inspection): a
  new per-turn check compares, for every turn of every task/policy, the resident's own
  raw command list against the final applied list with the armed unit's command
  excluded from both sides — `purity_violations` sums to **0** across all 3,072 rows.
  `vocabulary_violations` (any override command outside `{MOVE, PICK, PLANT}` for ARM_A
  or `{MOVE, PICK, CHOP, PLANT}` for ARM_B) is also **0**.
- Reward identity error ≤ 1e-6 on all rows; zero provenance/ambiguous-crop failures;
  zero double commit-and-abort; episode active-turn bounds respected; CONTROL never
  activates. All 17 integrity gates pass (see `integrity` in the result JSON).
- Rust suite: 13/13 (4 tests inherited unmodified from D162's frozen module + 9 new
  D168a-specific tests covering species tie-break, nearest-empty-cell selection,
  determinism, cross-policy entry identity, inactive-task parity, horizon/commit
  bounds, and controller purity).
- Zero platform, YT, sealed-map, candidate, resident-mutation, or Arena side effects.
  `medium_data` preflight passed before the bulk write.

## Mechanism gate (per arm)

| Arm | Activated | Rate | Seats | Families (of 8) | Gate |
|---|---:|---:|---|---|---|
| ARM_A post-return | 164 / 1,024 | 16.0% | {0, 1} | 7 (all but `script_boss`) | **PASS** |
| ARM_B pre-carry | 164 / 1,024 | 16.0% | {0, 1} | 7 (all but `script_boss`) | **PASS** |

Both arms activate on the **identical set** of 164 tasks (not merely the same count).
This is a direct consequence of two established facts: the resident's carry is empty at
100% of the 237 entry events (D166/167's own 0/237 fact, reconfirmed here as
`gate_carry_ok` true for all 237 ARM_B entries), so ARM_B's extra carry-empty condition
never binds; and the deposited-bank check happens to agree between ARM_A's post-CHOP
read and ARM_B's pre-CHOP read in every one of these 237 cases (no other own worker's
same-turn PICK/DROP/TRAIN ever straddles the ≥1-seed threshold at that exact turn). Both
arms therefore isolate the *same* causal question — script the same natural event two
different ways — on the same task set, which is exactly what a clean comparison needs.

Episode completion: ARM_A commits 105/164 (64.0%), aborts 55/164 (33.5%: 50 `HORIZON`, 5
`EMPTY_BANK_AT_PICK`). ARM_B commits only 77/164 (47.0%), aborts 78/164 (47.6%: 56
`CHOP_JOB_INVALIDATED`, 17 `HORIZON`, 5 `EMPTY_BANK_AT_PICK`).

## Value gate (per arm, activated subgroup, paired vs CONTROL)

| Metric | ARM_A post-return | ARM_B pre-carry | Requirement |
|---|---:|---:|---|
| Mean paired margin | **−6.732** | **−8.207** | ≥ +2.0 |
| Map-clustered 95% CI | [−8.398, −4.077] | [−10.528, −5.709] | lower bound informative only |
| Mean own-score Δ | −3.610 | −3.951 | ≥ −0.5 |
| Mean opponent-score Δ | +3.122 | +4.256 | (descriptive) |
| Worst family mean margin | −17.111 (`gold_adaptive`) | −15.556 (`gold_adaptive`) | ≥ 0 |
| Catastrophes (arm / control, full panel) | 24 / 22 | 22 / 22 | not above control |
| Negative-margin mass (arm / 1.10×control) | 5,430 / 5,501.1 | 5,486 / 5,501.1 | ≤ 1.10× control |
| Strict improve / regress / tie (active) | 31 / 123 / 10 | 24 / 121 / 19 | (descriptive) |
| Intention-to-treat mean margin (all 1,024, descriptive) | −1.078, CI [−1.52, −0.64] | −1.314, CI [−1.72, −0.91] | not gated |

Gate-by-gate: ARM_A passes only `negative_margin_mass_within_1.10x` (1/5); ARM_B passes
`catastrophes_not_above_control` (tied) and `negative_margin_mass_within_1.10x` (2/5).
**Neither arm passes all five value gates — both FAIL.**

Family means are negative in all 7 activated families for both arms (worst:
`gold_adaptive` at −17.1/−15.6; best: `resident`-opponent at −4.6/−5.3). There is no
positive family for either arm — this is not a subgroup effect masked by aggregation.

## Mechanistic reading (descriptive, not a gate)

Both arms lose even when they succeed, for related but distinct reasons:

- **ARM_A**: even the 105 *committed* episodes average margin delta −7.22 (not just the
  55 aborted ones at −5.95) — forcibly scripting MOVE→PICK→PLANT the instant suppression
  resolves is worse than the resident's own natural timing/cell/species choice and
  whatever else the worker would otherwise have done, even when the forced script
  completes exactly as designed. A quarter of activations (50/164) burn the full 24-turn
  horizon without completing, i.e. spend real turns walking under our control before
  reverting to the resident empty-handed.
- **ARM_B**: pre-fetching the seed *before* suppressing delays the suppression itself;
  by the time the worker returns to the target cell, the opponent crop is gone in 56/164
  activations (`CHOP_JOB_INVALIDATED`, worse than ARM_A's mechanism-comparable failure
  rate) — trading suppression timeliness for a preparatory detour that field-observed
  agents apparently obtain opportunistically (an incidental HARVEST before an unrelated
  CHOP), not via a deliberate multi-turn round trip. This is consistent with the
  project's standing denial-timeliness finding (`docs/CONSTRAINTS.md`, "Late-throughput
  ceiling" / "Denial-vs-production frontier").

Both readings are consistent with this project's broader, repeated finding
(`docs/CONSTRAINTS.md` "Meta-lessons"): hand-written wrappers that override the resident's
own judgment underperform trusting it, even when the wrapper targets a motif (BANK_SEED)
the resident already executes correctly on its own 135/237 times.

## Verdict (frozen rule)

Both arms fail their value gates while passing mechanism → **hand-written successor
controllers close**. The BANK_SEED motif survives only as an option inside the B2.1
rollout-valued semantic interface (short resident-backed rollouts choosing among
KEEP/acquire-and-PLANT/current-own-crop-HARVEST), exactly as D166/D167 already
recommended — not as a hand-scripted controller. No rescue, subgroup selection, or
rerun with adjusted thresholds/horizons was performed.

## Reproducibility

- protocol: `d513177473a4be06fa71e8873588a22a76ed66cb8f61a18f7f8b7fe9829823d1`
- lock: `79618784cd2fcb48ab82011f0af7a2c9f8086032f3a1d9e960cd0de9135e69ee`
- Rust runner (`rust/src/bin/d168a_bank_seed_successor_option.rs`):
  `02efa8ff95f55b8e1bf24122cfd1ed7d5b2dab213ea45621ce074691e7884eb3`
- analyzer (`cgauto/analyze_d168a_bank_seed_successor_option.py`):
  `edf7b3c9ef77575775b4f717385cf63834e49879c75df429aa179a4dc7f2f250`
- summary rows (jobs1 == jobs20, 3,072 rows):
  `d0620184bb3bbb9a959d0d4bf88de3e2cc727f9c2d028b45f07370b46b7814c1`
- reference inputs (unchanged from their own freeze, reverified byte-for-byte before
  this run): D161 resident panel
  `144d8f880be8eb58e19e1ef0a3547c04280dac8644340628b60101c1c47c988b`; D167a local summary
  `a2a3c6fec2c87f740903ad875d8b2cb943a0120ac161ed4c928a34718e57759c`; `rust/build.rs`
  `e06e96bf7ba9f1b2a3eb99444a7cd380058e493f4377a0116f13d287921e5c6f`.

Row counts: 1,024 tasks × 3 policies = 3,072 rows per run (both thread counts). Full
machine-readable detail (per-family/seat breakdowns, all integrity booleans, both
determinism hashes, complete gate tables) is in
`d168a-bank-seed-successor-option-result.json`. Bulk per-task rows:
`artifacts/experiments/d168a-bank-seed-successor-option/d168a-jobs{1,20}-9844136-9844199.tsv`.
