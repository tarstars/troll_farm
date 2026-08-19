# T-1 Stage 4 swap review — 2026-08-16

Verdict: **STAGE-4 FIXTURE MEASUREMENT ACCEPTED; FROZEN PREDICTION MISSES RECORDED;
T-1 ACCEPTANCE REMAINS OPEN.**

Reviewed pinned artifact `b487fd0193ac2576fb4bce04ef6e495c2058d95f`. Independent execution
reproduced the 13-case harness self-test and the committed 34-row JSON exactly:

- FIXED: OSC-001, OSC-028;
- detector-quiet but no progress, therefore NOT_FIXED: OSC-008, OSC-009, OSC-012;
- all remaining rows NOT_FIXED with their detector still firing.

The Stage 4 code emits adjacent reciprocal moves for an actively moving unit and an adjacent idle
peer that is strictly closer to the mover's goal. Those commands pass through the existing
conflict resolver and the authoritative replay runner. Changed traces show the expected exchange
(for example OSC-001 turn 7 changes from `MOVE 0 6 2;WAIT` to
`MOVE 0 4 2;MOVE 2 5 2`) and subsequent productive actions. The two accepted FIXED rows satisfy
both frozen clauses; OSC-009 is correctly not promoted merely because its detector becomes quiet.

## Frozen prediction grading

The coordinator already froze conservative progress-only grading with disclosure, and Stage 4 is
the full three-primitive candidate. Comparing it with the pre-registered 25/9 registry yields:

- **24 predicted-fixed misses:** OSC-002 through OSC-025 except OSC-001. Explicitly:
  OSC-002, 003, 004, 005, 006, 007, 008, 009, 010, 011, 012, 013, 014, 015, 016, 017,
  018, 019, 020, 021, 022, 023, 024, 025.
- Of these, OSC-008/009/012 are conservative-grader cases: detector quiet, no observed progress;
  a target-only cure could be undercounted. The other **21 still fire the detector**, so the
  omitted target arm cannot change their NOT_FIXED verdict.
- **One unexpected cure:** OSC-028 was pre-registered NOT_FIXED but grades FIXED.

Thus the registry comparison is 1/25 predicted cures realized, plus one cure in the nine-case
predicted residue. These 25 named misses are owner-session material under the frozen contract.
The H-STARVE-1 direction remains contextual only; it is not a causal explanation for these misses.

## Gates still open

This handoff does not complete T-1 acceptance. The charter still requires:

- dedicated observed-failing controls for legal atomic swap and illegal/non-swap collisions (the
  34-fixture outcome is useful integration evidence, not the requested negative-control suite);
- the 240-game panel with zero de-novo oscillation and D-1 rate versus 8.50% / 2.88%;
- warm p95 below 50 ms and thread parity.

No resident promotion, Arena action, or value claim is authorized by this review.
