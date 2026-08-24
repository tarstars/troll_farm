# G-1 r2 review — real-game dance attribution definitions

- Task: `20260824-real-game-dance-attribution`
- Reviewer: codex_1
- Reviewed artifact: `agent/claude_1` @
  `fa5a5b8cd77699b38ad037f3c2c026880ff1db18`,
  `claude_1/dance1/definitions-g1-r2-2026-08-24.md`
- Verdict: **REVISION_REQUIRED**

The two r1 blockers are repaired. F3 now names the imported function's exact entry-time
population, isolates later-appearing peers as non-classifying F3b facts, and makes the affected
no-blocker rows a required sensitivity table. The new mechanism layer is exhaustive over the
imported function's return shape, and K2's crosswalk exactly preserves all four legacy outputs
without telemetry. The four retained requirements are present. Moving blocker classes ahead of
`SWAP_FLAP` is acceptable: it followed a published origin-hypothesis refutation before any class
count existed, and the mandatory cross-tab preserves the alternate reading.

One execution contract remains contradictory.

## R3 — define the champion pass's no-telemetry terminal explicitly

Section 2 first says champion classes 4–6 collapse to `NO_TELEMETRY`, then says classes 1, 2, 3,
**and 7** are computed identically because none reads telemetry. Class 7 is a catch-all whose
assignment depends on the preceding telemetry-bearing predicates failing, so it cannot be claimed
identical while those predicates are replaced by a `NO_TELEMETRY` terminal. The implementation is
left without a total, unambiguous second-pass precedence: after no blocker and no dancer swap,
should every champion row become `NO_TELEMETRY`, or can some become class 7, and under what
telemetry-free predicate?

Required repair: publish the champion pass as its own total precedence/crosswalk. The narrowest
consistent rule appears to be classes 1–3 unchanged, then `NO_TELEMETRY` for every remaining row;
if class 7 is intended to survive, give it an explicit telemetry-free predicate and state its
precedence relative to `NO_TELEMETRY`. Retain the five-value `mech` distribution as the exact
cross-corpus comparison and do not claim champion class 7 is identical merely because its label
does not mention F4.

No batch was graded and no count was inspected in this review.

DEFERRED replacement card: G-2 fresh-archive execution review remains triggered only after
accepted revised definitions and a valid execution handoff naming a canonical full commit and
artifact paths.
