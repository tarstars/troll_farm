# D171a oscillation breaker — result

Date: 2026-07-28
Verdict: **CLOSED** (mechanism gate fails decisively; one value gate also fails).
Provenance note: the executor completed Phases 1–2 and the full gate analysis
(`d171a-oscillation-breaker-result.json`, panel TSVs byte-identical jobs1/jobs20, SHA
`f9d03b3f…`), then was killed by a transient API error while building the (moot)
historical-replay step. This document was assembled by the controller from the executor's
phase markers and result JSON; the verdict is the analyzer's own, not reinterpreted.

## What was built and how it ran

The fix implemented the frozen spec exactly: an `OscillationMemory` per unit, wiring the
existing unused `forbidden_for_non_priority` parameter, arming after 3 confirmed
reversals, disarm on target change or BFS progress vs the arm-time baseline; plus a
structural command-purity safety net (double-resolve with fallback to control on any
non-armed-unit diff). 28/28 bin tests passed; diff confined to the declared scope
(preserved as `d171a-fix-as-tested.patch`; the dev copy was restored byte-exact to the
frozen control snapshot after closure — SHA `fff6669b…` both sides).

Notable infrastructure finding: `rust/src/lib.rs` re-exports the dev copy as
`troll_farm::resident_policy`, so the dev copy IS the library-visible resident for all
D16x-family runners — controls must snapshot it (done here via a git-HEAD-frozen copy),
and any working-tree diff to it contaminates every concurrent experiment. Recorded as a
standing engineering constraint.

Panel: 128 fresh seeds (9,853,000–127) × 8 families × 2 seats = 2,048 paired tasks;
integrity clean (all rows complete; 0/519 inactive-episode mismatches; thread
byte-identity).

## Why it failed

- **Mechanism:** ≥10-turn same-two-cell runs fell only 127 → 69 (**45.7%** vs the ≥80%
  floor); 5–9-turn runs **rose 183 → 398 (+117%)**, failing the no-displacement gate;
  0/107 control-problem tasks fully resolved; **72 tasks with zero control oscillation
  acquired newly created runs** under the fix (worst de-novo run: 88 turns, map
  9,853,047 / script_boss / seat 1).
- **Root cause (traced per-task with temporary debug hooks in the panel bin only):** the
  frozen disarm rule does not cover "the reversal echo stopped on its own." A short
  coincidental 3-reversal blip — not a real chokepoint — arms the unit permanently
  against a stale forbidden cell for the rest of the game; the stale prohibition then
  forces detours that create brand-new oscillations. The four flagged purity anomalies
  are this same stale-arm phenomenon (single-unit isolation intact in all four). This is
  a design limitation of the frozen arm/disarm spec, not an implementation deviation; per
  protocol, no tuning was attempted.
- **Value:** overall neutral — paired mean +0.053, CI [−0.043, +0.148], catastrophes
  74/74 tied, negative-mass ratio 0.998, worst family −0.10 — but the activated-subset
  mean +0.53 misses its ≥+1.0 floor. The mechanism failure alone forces CLOSED
  regardless.

## Standing conclusions

1. Hard-forbidding a remembered cell with the D171a arm/disarm semantics is closed: it
   under-cures long runs and manufactures short ones. Do not retune the reversal floor,
   memory depth, or disarm rule within this spec.
2. The B3.4 diagnosis remains fully valid (the tie-break defect is real and pinned); the
   failure teaches the successor's requirements: any future breaker needs **bounded arm
   lifetime** (hard expiry), **disarm on echo self-termination**, and a strictly limited
   number of forced choices per arming — or a softer tie-break-preference mechanism
   instead of hard prohibition.
3. The candidate was never built (QUALIFIED-only per protocol); the live resident and
   the dev copy are byte-exact and untouched; the owner's standing promotion
   authorization for D171a therefore never triggered.

## Reproducibility

Result JSON: `d171a-oscillation-breaker-result.json` (verdict CLOSED, all gate values);
panel rows `artifacts/experiments/d171a-oscillation-breaker/d171a-jobs{1,20}-9853000-9853127.tsv`
(byte-identical, SHA `f9d03b3f…`); fix diff `d171a-fix-as-tested.patch` (364 lines);
control snapshot `rust/src/d171a_control_resident_snapshot.rs`; panel runner
`rust/src/bin/d171a_oscillation_breaker_panel.rs`; analyzer
`cgauto/analyze_d171a_oscillation_breaker.py`; protocol + phase markers as committed.
