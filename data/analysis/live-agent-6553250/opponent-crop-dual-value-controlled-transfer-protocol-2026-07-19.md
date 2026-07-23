# Opponent-crop dual value — controlled arena protocol, 2026-07-19

## Frozen identities and baseline

Exact resident/fallback: 62,725 bytes, SHA-256
`a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`, submission
`41012593`, agent `6560289`.

Candidate: 64,536 bytes, SHA-256
`083107f53e412be49fa06163f511a1453f7dc5447baed51ecda6d567785044cf`.
No regeneration or source change is allowed after the first arena write.

The active resident is already a mature same-source control.  Its immediately pre-transfer audit
contains 160/160 parsed games, zero pending, score 24.28, rank 23/107, 22 catastrophic losses
(13.75%), negative-margin mass 6,693, zero runtime/validity signals, and clean agent/submission
identity.  Repeating another same-source reset would consume the platform's observed 160-game cap
without adding a strategy control, so this mature read is the fixed bracket.

## Fixed execution

1. Reverify candidate and fallback hashes, sidecars, standalone compile, saved platform-source
   hash, and that the baseline audit is identity-clean.
2. Submit the frozen candidate explicitly once.  Do not change `cgauto/api_submit.py`.
3. Verify the new submission and agent identity as soon as a finished battle appears.
4. At 60 games, reject only for a runtime/validity/identity failure or score at most 22.78
   (baseline minus 1.50).  Never promote at 60.
5. At 120 games, reject for a safety failure or score below 23.78 (delta below -0.50).  A score at
   least 25.08 (delta at least +0.80) with clean safety is provisional only; otherwise continue to
   the terminal read.
6. The terminal read is the first read with at least 150 finished games and zero pending, followed
   by a second read at least 15 minutes later.  This accommodates the observed hard plateau near
   160 without inventing an unavailable 180-game requirement.
7. Promote only if both terminal reads are at least 24.78 (baseline +0.50), identity/runtime clean,
   catastrophic rate no more than two percentage points above 13.75%, and negative-margin mass no
   more than 110% of the count-matched resident mass.  Use the first 150/160 resident rows for a
   count-matched tail comparison when required.
8. Any terminal delta below +0.50, safety failure, failure to reach 60 games within 60 minutes, or
   unresolved infrastructure ambiguity rejects the transfer.  Explicitly restore the exact
   resident and verify its saved-source hash.
9. Promotion updates results and candidate identity first.  Changing the submit default remains a
   separate deliberate action.  Rank 3 still requires a mature live read and later confirmation.

## Stop rule

The arena attempt decides this exact 1:1 dual-value treatment.  Do not tune a multiplier, ETA,
activation threshold, or rating band using its games.  Rejection closes the branch and advances to
an ownership-aware closed-loop economy; promotion rebases the next residual analysis on the new
agent.
