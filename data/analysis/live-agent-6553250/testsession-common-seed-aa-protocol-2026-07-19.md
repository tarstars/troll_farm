# TestSession common-seed A/A capability protocol (frozen 2026-07-19)

## Purpose

Determine whether controlled Troll Farm games can be paired on the same platform map.  This is a
measurement-system test, not a policy experiment and not an arena submission.

CodinGame's current IDE client sets manual `multi.gameOptions` from a prior game's
`refereeInput`.  Authenticated replay `896298158` exposes exactly:

```text
seed=-5687447269333978810
```

For player 0, that replay's normalized turn-one input is 528 bytes with SHA-256
`e14d31e1cdb361ccfe50667ff2fb533d73af79c1ba78a079fffbd329262d0240`.

## Frozen A/A cell

- source A1 and A2: exact resident
  `candidate-agent6553250-preseed-orchard-coverage-slim.min.rs`, SHA-256
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`;
- opponent: delineate agent `6479768`, player 1 in both games;
- requested game options: `seed=-5687447269333978810` plus a trailing newline;
- order: A1 then A2, one second throttle;
- external budget: exactly two `TestSession/play` calls; stop after the first transport,
  compilation, runtime, degenerate-score, or options-echo failure;
- arena budget: zero writes.

## Frozen pass conditions

Common-seed pairing is available only if all conditions hold:

1. both games compile, finish, and return two scores with zero player-0 diagnostics;
2. both responses echo the requested `refereeInput` exactly;
3. both normalized player-0 turn-one inputs are byte-identical to each other;
4. both turn-one inputs have the prior replay's frozen SHA-256 above;
5. scores, final inventories, turn counts, workforce histories, and both agents' complete stdout
   command streams are identical between A1 and A2.

Conditions 1--4 prove map control.  Condition 5 proves full deterministic blocking against this
fixed opponent and is required before treating future same-seed A/B score differences as paired.

## Decision

- **Pass all five:** replace unpaired random-map smoke gates with blocked common-seed panels.  Each
  block uses resident and candidate on the same seed, same side, and same opponent; analyze within-
  block score and margin deltas.
- **Pass map control but fail full determinism:** seeds may block map variance, but opponent/action
  stochasticity remains; use repeated observations within each seed and do not claim exact pairs.
- **Fail map control or options echo:** retire common-seed TestSession pairing and use a prospective
  interleaved field panel with explicit uncertainty and resident controls.

No candidate policy may consume a common-seed field panel until this capability verdict is written.
