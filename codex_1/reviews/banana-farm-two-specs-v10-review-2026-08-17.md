# Banana-farm two-spec v10 review — 2026-08-17

Verdict: **REVISION_REQUIRED** (narrow operational definitions).

Pinned artifact: `132f0d8bf8a5b95834bea4899ecbf6a26357a799`.

V10 closes the three v9 headline blockers: only census members pay the frozen quota;
the panel requires zero de-novo D1 and P4; and suppression follow-up is no longer
limited to five commands. Two implementation-critical contracts remain implicit.

## 1. “Generation identity” is not observable without a reconciliation rule

The referee's `Plant` has no ID or owner. “Cell plus generation identity” therefore
does not yet tell an implementer whether the current plant is the census member or a
replacement at the same cell. Define the built census-member lifecycle over previous
state, current state, and our emitted commands:

- the attributes stored at census time;
- which growth/harvest/health transitions preserve the generation;
- which absence, kind/size reset, or other inconsistency ends it;
- how a confirmed own lethal chop is distinguished from other disappearance; and
- fail-closed handling when attribution is ambiguous.

If **any** frozen member is lost without a confirmed own completion, mark the current
round invalid and re-census once its remaining frozen members are gone (or specify an
equally deterministic restart point), with no stall/rise verdict. Gate GK needs a
same-cell replacement arm proving a new generation cannot inherit membership or pay
the old quota.

## 2. Suppression log schema still cannot be joined or differenced exactly

“Full context” currently enumerates turn/plant count/score sign/banked fruits and a
suppressed command, then a per-turn branch/candidate summary/commitment state/command.
Make the schema explicit enough for cross-game adjudication:

- run/situation identity, map seed and seat;
- unit ID and cell, machine phase, turn;
- commitment kind and target before/after reconciliation;
- candidate summaries immediately **before and after** PLANT suppression;
- final post-conflict emitted command; and
- a terminal reason: commitment cleared, DENY exited, unit died, game ended, or trace
  failure.

The follow-up must fail closed if it ends without one of those terminal records. This
is the evidence needed to distinguish “suppression had no behavioral effect” from a
discarded PLANT causing a later WAIT/loop.

No new owner decision is required; these definitions make the already ruled sequence
and log-and-defer mechanisms executable and auditable.

