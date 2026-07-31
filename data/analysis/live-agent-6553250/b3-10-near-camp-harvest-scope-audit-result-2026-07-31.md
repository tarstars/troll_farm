# B3.10 near-camp opportunistic harvest — scope audit result

Date: 2026-07-31
Verdict: **`CLOSED_BY_EXISTING_VALUE_AND_ROBUSTNESS_EVIDENCE`**

## What the B3.8 count means

B3.8 enumerates individual ripe fruit units that the resident never harvested, but that
were within BFS distance three of an own unit at some point. Its near-camp subset contains
1,144 units within two cells of an own door, including 956 PLUM/LEMON/APPLE units. Of the
1,144, 71.8% are outside D173b's chop-dominant scope.

That last percentage is a scope statement, not an action-value estimate. The “cheaply
capturable” subset contains 496 individual units, 425 bill-relevant, whose optimistic
walking detour is at most two turns. The audit explicitly excludes HARVEST and DROP from
that detour and credits the fruit at the first reachable turn. It is an intentionally
generous stock-accounting counterfactual, not evidence that a live policy can collect the
fruit without displacing another task.

## Direct-value ceiling

Each fruit unit contributes one own score point when banked. Crediting all 496 units across
all 205 resident games gives only **2.4195 own score/game**. An even more generous
deny-plus-capture ceiling, pretending every unit would otherwise have become opponent
score, is **4.8390 margin/game**. Both omit the mandatory action and scheduling cost.

This is far below the current 20-margin residual materiality reference used to close
stronger exact-resident opportunity bounds. It also cannot use the old worker-scaling
rationale: B3.8's bill used a synthetic cheap helper, D174a established the live policy's
larger fruit bill and unconditional two-worker cap, and this audit is direct-fruit-only.

## Existing intervention evidence

The two closest causal interventions already demonstrate the cost that the stock count
omits:

- D173a: +2.9351 overall, but compact_gold −2.0625, catastrophes 54 versus 49,
  negative-margin mass 1.0959, and every mechanism gate failed.
- D173b: +1.0625 overall with CI [−0.0562, 2.1812], compact_gold −1.3906,
  catastrophes 52 versus 49, negative-margin mass 1.0812, and every mechanism gate
  failed despite exact trigger fidelity.

Moving toward fruit outside the chop-shadow is mechanically distinct from those same-cell
rewrites, but no value headroom survives to justify it. “Outside D173b” does not erase the
HARVEST/DROP turns, walking displacement, family loss, or tail risk.

## Disposition

Close B3.10. Do not add a near-camp fruit target, tune a distance threshold, change worker
harvest capability, reuse the scaling story, or run a new panel. Reopening requires new
independent evidence whose conservative direct terminal-value lower bound clears the
current experiment bar; the old B3.8 event count is not such evidence.

This audit read only compact/frozen source and result records. It ran no analyzer, opened
no replay/map/range, and changed no source, frozen artifact, candidate, platform, or Arena
state.
