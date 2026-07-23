# D29b spatial option critic — controlled Arena transfer protocol (2026-07-20)

## Status and authorization

**CLOSED — do not execute.**  The preregistered D29c official-field activation audit selected the
farm branch on only 7/80 roots (`8.75%`), failing the minimum-decision-count and 17%--67%
activation gates.  This protocol is retained as an immutable record, not as an executable draft.
See `d29c-official-field-activation-audit-result-2026-07-20.md`.

No Arena write occurred.  Explicit user authorization cannot reopen this exact transfer: a new
representation hypothesis and prospective protocol are required by the frozen D29c stop rule.

## Frozen identities

Resident and mandatory rollback:

- source: `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`;
- bytes: 62,725;
- SHA-256: `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`;
- submission: `41015603`;
- agent: `6561795`.

D29b candidate:

- source: `candidate-agent6553250-d29b-spatial-option-critic.min.rs`;
- bytes: 96,414;
- SHA-256: `f074a553804a638d32cf97fe6e2e3cd2c718c4205ad79d6dfb2d6c7dde21c528`.

No regeneration, source edit, model/threshold change, or selector change is allowed after the first
Arena write.  The activation rule remains converted raw prediction strictly greater than `+4.0`.

## Fixed mature bracket

The read-only pretransfer checkpoint at `2026-07-20T19:14:48Z` is identity-clean on both room and
filtered ladder:

- 171 finished games, zero pending, 171/171 parsed;
- score 23.05, rank 34/107 Legend;
- 88 wins, one tie, 82 losses;
- 20 catastrophic losses (`11.696%`);
- negative-margin mass 5,537; and
- zero validity/runtime signals.

The platform's saved-source endpoint independently recovered the exact 62,725-byte resident SHA.
This mature same-source bracket is fixed; another control reset would consume scheduling capacity
without adding a strategy comparison.

For count-adjusted safety comparisons, use the first `N` resident rows in the saved checkpoint,
where `N` is the candidate row count (or all 171 resident rows if `N > 171`).  Compare catastrophic
rates directly.  Compare negative-margin mass per game, allowing the candidate no more than 110%
of the resident rate.  Frozen reference prefixes are:

| Games | Catastrophes | Catastrophic rate | Negative mass |
|---:|---:|---:|---:|
| 60 | 3 | 5.000% | 1,470 |
| 120 | 15 | 12.500% | 4,439 |
| 150 | 17 | 11.333% | 4,946 |
| 160 | 19 | 11.875% | 5,276 |
| 171 | 20 | 11.696% | 5,537 |

## Mandatory preflight

Immediately before any authorized write:

1. recover the platform source read-only and require the exact resident SHA and current agent;
2. verify both source sidecars and compile both artifacts as standalone optimized Rust 2021;
3. regenerate D29b to a temporary path and require byte identity with the frozen candidate;
4. require the complete deployment result, integrated qualification, and 160-case compiled
   protocol replay artifacts to remain passing and hash-clean;
5. capture a new resident checkpoint and require agent `6561795`, submission `41015603`, at least
   150 finished games, zero pending, zero fetch/identity/runtime failures, and score at least
   `22.55`; and
6. stop and refreeze the protocol if source identity, resident identity, league, or platform state
   differs.  Do not silently substitute another baseline.

## Fixed execution and decisions

1. Submit the frozen candidate path explicitly exactly once.  Never invoke an implicit/default
   submission path.
2. As soon as a finished battle appears, verify the new submission/agent identity and recover the
   platform source.  The recovered source must be 96,414 bytes at the frozen candidate SHA.
3. At the first 10 finished games, inspect only source identity, validity, runtime, and parser
   health.  Any failure rejects immediately; performance cannot promote or reject at this read.
4. At 60 finished games, reject only for identity/runtime/validity failure or score at most
   **21.55** (resident 23.05 minus 1.50).  Never promote at 60.
5. At 120 finished games, reject for a safety failure, score below **22.55** (delta below -0.50),
   catastrophic rate above the matched resident rate by more than two percentage points, or
   negative-margin mass per game above 110% of matched resident.  A score at least **23.85**
   (delta at least +0.80) is provisional only; every non-rejected result continues to terminal.
6. The terminal read is the first identity-clean read with at least 150 finished games and zero
   pending.  Capture a second full read at least 15 minutes later, even if the platform has
   plateaued at the same game count.
7. Promote only if both terminal reads have score at least **23.55** (delta at least +0.50), zero
   identity/runtime/validity failure, catastrophic rate no more than two percentage points above
   the matched resident prefix, and negative-margin mass per game no more than 110% of the matched
   resident rate.
8. Any terminal score below 23.55, safety failure, inability to reach 60 finished games within 60
   minutes, or unresolved infrastructure/identity ambiguity rejects the transfer.  Explicitly
   restore the exact resident and verify its saved-source SHA.
9. Promotion records the new source/submission/agent and field metrics first.  Changing the submit
   default remains a separate deliberate action.  Rank 3 is not claimed without a mature verified
   rank-3 read.

## Stop rule

This Arena sample decides this exact D29b controller.  Do not tune the `+4` threshold, worker guard,
features, model, quantization, option policy, or rating gates using its games.  Rejection closes
this exact transfer and the next experiment must use a new preregistered hypothesis and new field
sample.  Promotion rebases subsequent residual analysis on the new resident.
