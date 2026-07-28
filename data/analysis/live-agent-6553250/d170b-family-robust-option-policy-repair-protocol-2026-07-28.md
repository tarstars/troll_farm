# D170b — mechanics-only repair and re-run of D170a

Status: FROZEN protocol, authored 2026-07-28 (Fable), adjudicating D170a's
CLOSED-AT-PHASE-1. Classification: implementation invalidation, not scientific closure —
three of thirteen arms were structurally unreachable (off-by-one in the D170a-specific
composition layer; root cause fully established in
`d170a-family-robust-option-policy-result-2026-07-28.md`). House precedent for
mechanics-only repairs with re-frozen locks: D112→D113, D133b, D75b. No value outcome
existed in D170a, so no post-outcome tuning is possible by construction.

**D170b inherits the D170a protocol
(`d170a-family-robust-option-policy-protocol-2026-07-28.md`) in its entirety** — same
question, environment semantics, policy, four objectives, seeds, budgets, declared ranges,
Phase 2/3 gates, prohibitions, and decision tree — with exactly three deltas:

## Delta 1 — the repair (only the D170a-specific section may change)

In `rust/src/rl_d170a_option_policy_env.rs`, fix the resource `_trig` arming by mirroring
`OPT_RETURN`'s sticky-flag pattern: in `step_one_turn`, after the engine step, when the
observed opponent worker count first reaches ≥ 3, set a persistent
`trig_pending: bool` (one per component or one shared flag consumed per arm — match
OPT_RETURN's established structure); `refresh_candidates` consumes the flag on its next
call to enqueue the `_trig` arms. The turn-equality comparison is removed. The frozen
`mod inherited` vocabulary block must remain byte-identical (hash-check against the
D169a/D170a lock records before and after the edit). Add focused unit tests: the trig arm
IS offered on the decision boundary following the trigger event, and never before it.
Re-freeze a new lock (`d170b-...-lock.json`) hashing the corrected env plus all inherited
files.

## Delta 2 — pre-Phase-1 activation verification (frozen; run before any training)

All-KEEP deterministic diagnostic on the training pool (seed_base 9,850,000, map_pool
256, no training budget spent), as in D170a's field-level diagnostic:

- each resource `_trig` arm offered at least once in ≥ 5% and ≤ 50% of episodes; and
- offered at least once in ≥ 60% of the episodes where the underlying trigger event
  (state feature 55) occurs; and
- `opt_return` offered at least once in ≥ 8% of episodes (its D168-measured arming rate
  is 16.0% of tasks; half that is the alarm floor).

Any miss → **BLOCKED** (report; no further self-repair; a second repair needs its own
adjudication).

## Delta 3 — Stage-A exploration-gate semantics (definitional correction, pre-outcome)

The 2% exploration floor's evident intent is "the learner explores every option enough to
learn about it." An option that is rarely *armable* cannot reach 2% of ALL decisions
under any policy. Corrected semantics: for each option, sampled-share is computed
**conditional on decisions where that option was offered** (≥ 2% of its offered
decisions); the unconditional share is reported alongside for continuity with D170a's
records. All other Stage-A gates (finite losses, exact crop safety, reward identity,
exact transition budget) unchanged.

## Everything else

Identical to D170a: Phase 1 re-run FROM SCRATCH on the same 8 (objective, seed) cells
under the corrected code; Phases 2–3 exactly per the D170a protocol (the resume-built
analyzer `analyze_d170a_family_robust_option_policy.py` is already smoke-tested and may
be reused unmodified — record its hash in the new lock); Phase 4 excluded (separate
dispatch). Outputs use the `d170b-` prefix for protocol/lock/result and per-fit files;
bulk to external `artifacts/experiments/d170b-family-robust-option-policy/`. The
decision tree, STOP conditions, and verdict vocabulary (CLOSED-AT-{phase} / CONFIRMED)
are D170a's. D170a's artifacts remain frozen as the record of the invalidated run.
