# D176a — oscillation breaker, successor to D171a (preference tie-break with bounded arming)

Status: FROZEN protocol, authored 2026-07-29 (Fable / `claude_1`) from the H13 fidelity
audit. Execute exactly; no scope, threshold, or gate change after any outcome is seen.

**Why this is not a prohibited retune of a closed branch.** D171a closed with explicit
successor requirements recorded in its own result document and in CONSTRAINTS: *bounded
arm lifetime, echo-stop disarm, ≤2 forced choices per arming, or preference-based
tie-breaking instead of hard prohibition.* This protocol implements those requirements and
adds genuinely new evidence rather than a threshold sweep: **a measured achievable ceiling
from a same-architecture reference bot** (yamo: 2.9% of games oscillate, worst case 6
turns, against our 18.2% and 133 turns — H13). Thresholds below are anchored to that
reference, not chosen freely.

**Expected value is honestly marginal.** D171a's partial cure (45.7%) was worth **+0.53 on
its activated subset**; oscillation touches 18.2% of games, so even a good successor
plausibly returns ~+0.1 overall. This runs because it is execution-class — the only family
that has ever transferred to the arena — the machinery already exists, and a negative
result is cheap and informative. It is not expected to move rank on its own.

## Root cause (unchanged from B3.4, re-confirmed by H13)

`resolve_move_conflicts_with_priority_and_forbidden`
(`rust/src/bin/yamo_orchard_live.rs:1440–1520`; detour tie-break `:1505–1521`): candidate
generators recompute targets fresh each turn with zero cross-turn memory; when the natural
step is blocked by an own unit treated as reserved, the detour's `min_by_key((BFS_dist,
Cell))` can tie between "retreat" and "go around", broken by incidental lexicographic Cell
order, and the identical choice regenerates every turn. D171a's failure mode was that a
**hard** prohibition with **unbounded** arm lifetime manufactured new oscillations
elsewhere (+117% displacement into 5–9-turn runs; de-novo runs in 72 clean tasks).

## Delta 1 — preference, not prohibition (the core change)

The remembered cell is **not forbidden**. Instead, when a unit's detour tie-break is
otherwise exactly tied, the cell it occupied two turns ago receives a **fixed additive
penalty of +1 in the sort key only** — i.e. it loses ties but still wins when it is
genuinely strictly better. This is the "preference-based tie-breaking" successor option;
it cannot make a strictly-better move illegal, which is what produced D171a's de-novo runs.

## Delta 2 — bounded arming

- Arms after **3 confirmed reversals** (unchanged from D171a: the corpus histogram elbow).
- **Hard expiry: the preference applies for at most 4 turns after arming**, then clears
  unconditionally regardless of state. This is the "bounded arm lifetime" requirement.
- **Echo-stop disarm:** if a full turn passes with no reversal, the memory clears
  immediately. This is the requirement D171a's spec omitted and which caused stale arms.
- **At most 2 turns per arming may have their tie-break altered** (the "≤2 forced choices"
  requirement); after that the arm is spent even if unexpired.
- Also disarms on target change or BFS progress (retained from D171a).

Edit only the formatted dev copy; the diff must be the tie-break penalty plus the memory
field and its plumbing. Compile-then-restore flow: apply, build the panel binary, restore
byte-exact and re-verify SHA prefix `fff6669b` **before** running the panel; preserve the
change as `d176a-fix-as-tested.patch`.

Unit tests: penalty applied only on an exact tie; a strictly-better remembered cell still
wins; arming exactly at 3 reversals; expiry at 4 turns; echo-stop disarm after one
reversal-free turn; the ≤2-altered-turns cap; no effect absent a reversal pattern.

## Panel

Fresh seeds **9,857,000–9,857,127** (pre-lock: grep both ledger volumes for `9,857`;
sealed ranges untouched) × 8 families × both seats = **2,048 paired episodes** vs the exact
resident control (frozen snapshot `rust/src/d171a_control_resident_snapshot.rs`,
SHA-verified equal to the dev copy). Byte-identity jobs1-vs-jobs20; `LC_ALL=C`.

## Integrity gates

Inactive episodes byte-exact vs control; command purity (diffs begin at an altered
tie-break under the stated conditions); crop/workforce/reward accounting paired; dev-copy
scope check; `troll_farm::resident_policy` re-export intact; all six waste-sweep detectors
run on both arms. Trigger fidelity verified on ≥64 activations before the panel (≥90%
must satisfy the full arming conjunction) — the check that saved D174a and caught D173a.

## Mechanism gates (anchored to the reference bot, not chosen freely)

- Games containing a ≥10-turn same-two-cell run fall from the control's rate to
  **≤ 6.0%** (yamo's measured 2.9% is the ceiling; 6.0% is roughly the midpoint between
  his rate and our 18.2%, and is the pass mark).
- **Worst-case run length ≤ 20 turns** (yamo: 6; ours: 133).
- **No displacement:** 5–9-turn runs must not increase by more than 10% (D171a failed here
  at +117%).
- **No de-novo oscillation:** tasks with zero control oscillation acquiring a ≥10-turn run
  must be **≤ 1%** (D171a: 72 tasks).
- No waste-sweep detector worsens by > 10%.

## Value gates (retained from the family that killed D171a/D173/D174)

Overall paired mean ≥ **0.0** with clustered 95% CI lower bound ≥ **−0.5**;
activated-subset mean ≥ **+0.5** (lowered from D171a's +1.0 *before* seeing any result,
and justified by the honest expectation stated above — this is a preregistered floor, not
a post-hoc relaxation); worst opponent family ≥ **−1.0**; catastrophes ≤ control;
negative-margin mass ≤ **1.05 ×** control.

## Verdict

All mechanism AND value gates pass → **QUALIFIED**: build the candidate pair (formatted +
slim via the pruning pipeline, sha256 sidecars,
`candidate-agent6561795-oscillation-preference.{rs,min.rs}`) and **STOP at the arena
gate** — promotion requires a NEW owner authorization; note that at this expected
magnitude a dedicated arena trial is likely *not* worth its churn cost, and the natural
disposition is a ride-along on some future submission. Mechanism fails →
**CLOSED-AT-MECHANISM**; value fails → **CLOSED-AT-VALUE**. Either closure ends the
oscillation line permanently: two designed attempts against a known ceiling is enough.
No tuning in any case.

## Outputs

`d176a-oscillation-breaker-successor-{lock,result-2026-07-29.md,result.json}`; the patch;
phase markers to `.superpowers/sdd/d176a-phase-markers.md` after every stage; bulk rows
external (`artifacts/experiments/d176a-oscillation-breaker-successor/`). Ledger
integration is the controller's.
