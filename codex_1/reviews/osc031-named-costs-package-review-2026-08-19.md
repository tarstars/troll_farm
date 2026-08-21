# OSC-031 named-costs package review — ACCEPTED

Reviewer: `codex_1`  
Artifact: `20fef6398f0fc73cb6067a5b67490d5cfdee1680`  
Task: `20260819-osc031-forecast-fix-door1b`

## Verdict

**PACKAGE COMPLETE AND HONEST under owner Ruling B.** This is a package-integrity verdict, not a
value verdict and not a reversal of the predecessor's zero-de-novo rejection. The M-1 paired
night is the value decider; the owner rules KEEP/REVERT.

## Independent checks

- Assembler rerun is byte-identical to the committed package at SHA-256
  `882d6b885ae815a38b5185ffc339f33e2a47f9a9a40502aaa45c85b84a69a92b`.
- Candidate source SHA is `547fa706...`; direct diff against cure-C `ad3bfefe...` is one hunk:
  the damaged-tree flat-1 block becomes literal `0`, with no additions or orchard predicate.
- All 9 de-novo `(map_id, seat)` keys exactly equal the accepted decomposition and each has a
  structured property/detector diagnosis. The four P3 rows carry first-divergence evidence.
- All 15 healed keys exactly equal the accepted decomposition.
- Aggregate is candidate 47 versus floor 53 blocking.
- Parity is identical over 240 rows and 8,160 field comparisons, excluding only `attempt`.
- Both latency arms meet the 50 ms budget and the host/coverage limits travel with the values.
- Withdrawn first/second-order labels are absent. Opponent-stream equality is explicitly a
  measurement only; causal order is not established without targeted replay.
- The package states that nothing was newly measured and preserves the predecessor rejection.

The m090 record exposes both D-1 and D-4 in its structured detector field; its diagnosis names
the P1 oscillation mechanism and the handoff explicitly names the D-4 no-progress episode. No
recorded cost is hidden by a friendlier causal claim.

## Scope

Acceptance satisfies only the named-costs completeness/honesty gate. The owner pre-registered
provisional paired sigma 1.5 before the night: winner bar 1.315 at 5 pairs, extension to 10 pairs
at 0.930, with the 1.0 materiality floor unchanged. Arena serialization, exact artifact checks,
night execution, and terminal KEEP/REVERT remain solely with the integrator/arena controller.
