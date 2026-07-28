# D172a dense counterfactual-credit option policy — result

Date: 2026-07-28
Verdict: **CLOSED-AT-SELECTION.** Phase 0 (label-pipeline byte-exact validation), Phase 1
(80K-row training corpus), and Phase 2 (signal floor) all pass cleanly — the exact,
zero-noise counterfactual labels are real and dense (40.4% of armable states clear the
+2.0 floor, 5× the 8% requirement). But the two frozen function classes (linear;
16-unit-trunk MLP), fit by supervised Huber regression on those exact labels and run
closed-loop with the frozen τ=+1.0 threshold, admit **0/4** on the LOBO selection blocks —
every fit's decisive, consistent failure is the pooled-mean gate (all four land
+0.14…+0.26, roughly 6–10× short of the +1.5 floor), with at least one of each fit's 8
held blocks net-negative. Per the protocol's pre-adjudicated decision tree ("Phase 3 no
admission → CLOSED-AT-SELECTION"), Phase 4 (veto panel, sealed confirmation) was never
executed.

## Phase 0 — label-pipeline validation: PASS

Recomputed a stride-sampled 256-(task,arm) subset of D169a's own consumed 1,024-task
panel (8× the protocol's 32-sample floor) via this experiment's own copy of `d169a_play`,
against **both** bulk TSVs (`d169a-jobs1-...tsv` and `d169a-jobs20-...tsv`, the
thread-parity twin). **0/256 mismatches on `own_score`/`opponent_score`/`action_hash`/
`state_hash`, both files.**

An additional, non-gate defensive check cross-validated the 81-field feature vectors
against the live, already-compiled `tf_d170a_*` FFI (`D170aVecEnv`, driven all-KEEP).
This caught and fixed two real bugs before either could contaminate the corpus:

1. **Trig-arm offering timing.** An early draft copied D170b's Delta-1 "sticky-flag,
   consume next turn" pattern for the resource `_trig` arms, by analogy with `OPT_RETURN`.
   D169a's own native trig-arm check is pre-step, same-turn
   (`opp_worker_trigger_turn == current_turn`, evaluated fresh — independently confirmed
   by D169a's own test `trig_arm_configured_start_equals_observed_opponent_trigger_turn`).
   D170a's env offers it one turn later only because *that file's* `refresh_candidates`/
   `step_one_turn` split can never observe the trigger mid-turn — an architecture-specific
   workaround, not D169a's native semantics, and not what this experiment's labels
   (sourced from `d169a_play`) require. Fixed by reordering the scan to update the
   trigger/entry-detection state before the candidate scan and checking the equality
   directly (no sticky flag needed for trig; `OPT_RETURN`'s own genuine post-step sticky
   flag is unaffected and correct).
2. **`decisions_seen_so_far` (state field 62) within a simultaneous-candidate group.**
   D170a's own env calls `observe_input()` once per candidate, sequentially, with
   `decisions_seen` incremented *inside* `decide()` between successive same-turn
   candidates — so candidate *i* (0-indexed within a group) sees
   `decisions_seen_so_far = baseline + i`, not one shared snapshot. Fixed by recomputing
   `state_family` fresh per candidate instead of once per group.

After both fixes, the extended check has zero mismatches on any fixed-mark or
`opt_return` candidate; the only remaining 63/639 mismatches are isolated to `opt_*_trig`
candidates, always as complete 3-candidate groups — fully explained by the deliberate,
already-validated same-turn-vs-turn+1 divergence from D170a's env (item 1 above), not a
residual defect. Full detail: `d172a-dense-counterfactual-option-policy-phase0-result.json`.

## Phase 1 — training corpus: 79,997 rows

Seeds 9,860,000–9,860,511 (512 fresh maps × 8 families × 2 seats = 8,192 tasks). Pre-lock
seed-overlap grep clear (zero hits outside the protocol/lock themselves, across both
ledger volumes and every `docs/**/*.md`; sealed ranges and D170's own ranges numerically
disjoint by construction). Generated in 1,435s (~24 min) at 20 threads — well under the
protocol's own rough "~5–10h" estimate; no YT needed. 4 shards streamed to the external
root as they completed (every 128 maps, never only at the end), row counts
20,149/19,906/19,939/20,003 summing to 79,997 exactly. Manifest with all shard hashes:
`d172a-dense-counterfactual-option-policy-corpus-manifest.json`.

## Phase 2 — signal floor: PASS, 5× over

Grouped the corpus by decision state (map_seed, seat, opponent, turn); for each state,
took the max label among its simultaneously-offered candidates.

- **Rate: 40.4%** (11,077/27,392 states) have max-option label ≥ +2.0, vs the frozen 8%
  floor.
- Both seats represented; **all 8/8 opponent families** represented (vs the ≥6 floor).

This rules out the "value density too thin even for perfect labels" failure mode the
floor exists to catch cheaply — the signal is real and dense, not marginal.

## Phase 3 — fits and selection: 0/4 admitted

Two frozen function classes, two seeds each, Huber loss (δ=1.0) on the exact labels, one
deterministic thread per fit, all training hyperparameters frozen before any outcome was
observed:

| fit | params | pooled mean | worst block | worst family | activation | admitted |
|---|---|---|---|---|---|---|
| linear/172101 | 1,066 | +0.139 | −0.074 | −0.094 | 6.69% | NO |
| linear/172102 | 1,066 | +0.229 | −0.031 |  0.000 | 6.79% | NO |
| mlp/172201    | 1,533 | +0.178 | −0.078 | −0.059 | 4.35% | NO |
| mlp/172202    | 1,533 | +0.262 | −0.094 | −0.414 | 9.91% | NO |

All four fits pass `worst_family ≥ −1`, crop/workforce safety exact (zero purity
violations / invalid direct commands / provenance failures), and
`catastrophes ≤ control` (49 vs 49, every fit). Every fit fails
`lobo_pooled_mean_at_least_1_5` (all ~6–10× short) and `worst_held_block_at_least_0` (≥1
of 8 blocks net-negative in every fit); `mlp/172201` additionally falls just under the
5% activation floor (4.35%). **0/4 admitted → no selection.**

Chosen arms concentrate almost entirely on `opt_fruit_*` (t072/t104/t136/trig), with a
handful of `opt_iron_*` in `mlp/172202`, and **zero** selections of `opt_protect_*` or
`opt_return` in any fit. This is mechanistically sensible, not noise: D169a's own
per-arm `mean_paired_margin_active` table shows the fruit arms are the *least*-negative
always-on options (−2.9…−3.7 for fixed marks) while iron and return are strongly
negative always-on (−6…−12); a model that learned to invoke fruit selectively while
almost never touching iron/return/protect is acting consistently with the underlying
value landscape D169 already established, not selecting at random.

**Weight-export and mechanism validation** (beyond the frozen gates): the exported,
Rust-consumable weight files were cross-checked against the PyTorch-trained models
directly (max abs diff 1.07×10⁻⁶ over sampled rows × 13 heads) — the Python→Rust bridge
is correct. A 1-vs-20-thread run of the closed-loop evaluator on an 8-map sample produced
byte-identical row digests — the mechanism is deterministic and thread-count-invariant,
matching the house pattern.

Full detail: `d172a-dense-counterfactual-option-policy-phase3-result.json` and the four
per-fit result files.

## Phase 4 — not executed

Per the protocol's pre-adjudicated decision tree ("Phase 3 no admission →
CLOSED-AT-SELECTION"), the veto panel (D169a/D170a/D170b's own consumed 1,024-task panel)
was **not** evaluated and stays veto-only/unconsumed for any future dispatch. The sealed
confirmation block (seeds 9,862,000–9,862,063) was **not** opened and remains sealed.

## Interpretation

D169 proved a +10.671 hindsight-envelope ceiling exists. D170b proved on-policy
terminal-reward learning cannot find it (all four objectives converge to always-KEEP,
P(invoke) ≤ 3.3%, ~200 invoke samples/arm vs SD≈26 terminal-reward noise — the signal is
there but on-policy sampling never resolves it). D172a asked the harder-to-dismiss
question: give the policy the *exact* answer at every decision (zero-noise counterfactual
labels, not on-policy Monte Carlo) — can a small function class still turn that into
closed-loop value?

The answer here is a qualified **no, not at this magnitude, with these two function
classes**. Unlike D170b's total collapse to always-KEEP (pooled_mean exactly 0.0 in all
8 fits), every one of D172a's four fits genuinely learns to invoke a small, non-trivial
fraction of the time (4–10%) with a real, consistently positive (not zero, not negative)
expected value — proving the underlying decision problem *is* learnable to a first
approximation from the 81-field observable feature set under direct supervision, which
on-policy learning could not establish. But "learnable to a first approximation, with the
wrong magnitude and an unreliable worst block" is exactly what the frozen admission gate
(pooled mean ≥ +1.5, every held block ≥ 0) exists to reject, not to grandfather in as a
partial pass. The gap between Phase 2's dense signal (40.4% of states) and Phase 3's
realized value (~0.2 pooled mean, an order of magnitude under the bar) is itself the
finding: exact per-decision labels are necessary but evidently not sufficient here — the
81-field feature set plus a 1,066–1,533-parameter linear/shallow-MLP scorer cannot
generalize the labeled signal to held maps at the value density D169's hindsight ceiling
implies is theoretically available.

Per the protocol, no τ/threshold/feature/class retuning is permitted after this outcome;
whether a larger function class, a richer feature set, more corpus, or a different
non-frozen configuration could close the gap is explicitly **not** answered here and
would require a new protocol under a new authorization — the same house discipline
D170b's own closure was recorded under. This CLOSES the dense-counterfactual-credit route
as specified and, per the protocol text ("Any CLOSED = the final closure of the Tier-2
learning route over this option vocabulary"), is the terminal outcome for this program.

## Reproducibility

- Protocol: `577d1c9798d593d2c62939492f6ef2db3fe99aa13a074078b2ae9283eae753cc`
- Lock: see `d172a-dense-counterfactual-option-policy-lock.json` (self-contained sha256
  table of every frozen-machinery file, all re-verified unchanged throughout)
- `rust/src/bin/d169a_resident_option_envelope.rs` (unmodified):
  `ec51121a1a49251f4a3ee001cbc2fe832179be7db7dba41ea247a8aa1862760a`
- `rust/src/rl_d170a_option_policy_env.rs` (unmodified):
  `f9d47d119dcd8d443976ccb1154081eb54e99493cbcdd5012a5b4491b81c542d`
- New corpus generator + policy runtime: `rust/src/bin/d172a_dense_counterfactual_corpus.rs`
  (9/9 Rust unit tests passing; compiled binary sha256 `c9afde7daa701067ff2d9a960bfe1e86adc41623b69f1e44a2056a7c77e909bc`,
  used unmodified for Phase 0/1/3 — see the frozen-module-integrity note below)
- New trainer: `cgauto/train_d172a_dense_counterfactual_option_policy.py`
- New analyzer: `cgauto/analyze_d172a_dense_counterfactual_option_policy.py`
- Corpus manifest with per-shard hashes: `d172a-dense-counterfactual-option-policy-corpus-manifest.json`
- git rev at writing: `d29cb52d4e057d410fbe0af065a698ad2d5aa897`

**Frozen-module integrity note.** An unrelated concurrent agent ("D173a: harvest-before-
chop") edited the D171a-frozen dev copy (`rust/src/bin/yamo_orchard_live.rs`,
`troll_farm::resident_policy`) mid-session — not caused by this task (verified: this task
never opened that file for writing; the diff's own content is a distinct, self-labeled
experiment). Timeline reconciliation shows this task's compiled binary (built 20:39:39)
predates that diff (observed at 21:12:17), and both Phase 0 and Phase 1 (20:49–21:13)
completed using that already-compiled binary before the diff appeared — Rust binaries
statically embed source at compile time, so the already-running/already-built process was
unaffected. No `cargo build`/`cargo test` was run after that point in this session,
specifically to guarantee no artifact here ever embeds the concurrent change. Full
detail in `.superpowers/sdd/d172a-phase-markers.md`.
