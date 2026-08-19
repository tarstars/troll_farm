# OSC-031 two-truths pre-build review — structurally gate-ineligible

Reviewer: `codex_1`  
Artifact: `7f2dfd002dfe605930b0548e7d64f9719835a7ba`  
Task: `20260819-osc031-forecast-fix-door1b`

## Verdict

**STOP BEFORE BUILD.** The chartered two-truths design cannot satisfy the frozen zero-de-novo
gate.

- Item 1, deleting the damaged-tree flat-1 inference, is exactly the already-tested Door-1 source
  change. On non-orchard views, item 2 is inactive, so the five known non-P3 de-novo games replay
  unchanged. The lower bound is therefore 5, not an estimate.
- P3 is absolute command-stream equality on orchard-eligible views. Any command changed by item
  2's orchard exclusion produces a P3 violation and a block. Among 12 orchard games, the floor
  already blocks 3 and is clean on 9, so item 2 may add 0–9 de-novo games.
- The total design range is therefore 5–14 against a frozen gate of 0.

## Independent checks

The exposure script was rerun from the pinned commit against the accepted Phase-2 raw arms. Its
output is byte-identical at SHA-256
`636efdb80be0fe49ae97665bf6b57b31f687a922a8983e242ea9d62550aae46f`.
Direct source inspection confirms the parent damaged-tree block and Door-1's deletion; direct
inspection of `eval_p3()` confirms that any orchard-eligible command-stream inequality returns a
violation. The floor has 0 P3 violations, structurally and in the 12 measured games.

The exact landing point inside 5–14 requires a build, but no landing point can pass. Spending a
panel to choose among failing counts is measurement work, not a ready-with-gates attempt, and
needs an explicit owner charter if desired. The predicate-source question is real but no longer
the first blocker: the design fails before that implementation choice matters.

Reopening requires an owner-approved design that can change the five non-orchard failures while
remaining compatible with P3, or a deliberate separately reviewed instrument-policy change. The
gate must not be relaxed after observing this result.
