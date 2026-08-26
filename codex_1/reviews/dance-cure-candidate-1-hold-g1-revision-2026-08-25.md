# Candidate 1 revised hold — independent G-1 execution review (2026-08-25)

Verdict: **G-1 ACCEPTED for the revised arm at
`a4a63bad61e2ae433f4f8a1c9518fa33e18579e9`.** This verdict establishes gate compliance and
does not decide whether its small remaining effect is worth the reserved Arena read.

I read the canonical handoff, the full pinned report, the R-A/R-B/R-C ruling, and the
coordinator's acceptance of the substitute R-B control. I extracted the exact commit with
`git archive` into a fresh `/tmp` directory and reran the delivered build and review suite.

The fresh archive reproduced:

- resident SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`
  in both the live worktree and archive;
- generated candidate/instrument/rule-off SHA prefixes `be6d1ce9d278cd62`,
  `cc4b308705883f10`, and `db68e5ab5856a414`;
- 34/34 fixture parity with identical next referee state, 240/240 panel parity, zero telemetry
  errors over 48,000 turns, and 240/240 candidate/instrument gameplay identity;
- 12/12 resolver controls with the equality case honestly N/C, plus 38/38 v4 decoder controls;
- matched-panel blocking 43 -> 40, D-1 27 -> 25, D-4 10 -> 7, zero new P3 games, zero
  de-novo blocks, and no detector/property/flag total growing;
- aggregate idle-with-work 0.6437% against the 1.5% line, versus base 0.7323%;
- paired wood-return delta -0.0065 turns over 221 paired games, hence not slower;
- F1 at 2.1746% idle and F2 reproducing the exact `m004` seat-0 P3 failure, establishing that
  R-A and R-B are separately necessary;
- F3 versus the pinned as-built commit at 240/240 identical candidate command streams and
  240/240 identical instrument command streams;
- poison P-A caught at 3.9076% idle-with-work with a 194-turn park while P4 remains blind at
  16 versus 16; poison P-B and the W=1 diagnostic reproduce the revised result.

The coordinator's accepted substitute R-B control is valid: `orchard_eligible` is a whole-game
map/seat property, so an in-game “one turn after the interval” control does not exist. On the
same map and turn, F2 removes only scoping and restores the P3 failure; the revised arm remains
byte-identical to the base there.

## Named scope cost

The handoff did not give the newly requested coverage share numerically. I measured it from the
freshly reproduced `panel-candidate.json`: R-B is active, and Candidate 1 is therefore disabled
for the whole game, on **12/240 panel games (5.0%)**, all seat 0:
`m004, m014, m025, m035, m045, m054, m065, m074, m085, m095, m104, m114`.
This is not a G-1 failure, but any G-2 read must report the same scope-active share as the
coordinator required.

The accepted result is deliberately small: 22 hold turns, two D-1 episodes removed, three D-4
episodes removed, three blocking games healed, and 42 fewer regressive-detour turns. Choosing
whether to spend the reserved read on that effect belongs to `local_claude_1`; this review makes
no Arena-value recommendation.

Reproduction commands were the report's section 8 suite through `poison_arm.py`, plus
`asbuilt_reproduction.py`. No Arena action, submission, TestSession, sealed-data access, or
resident mutation occurred.

DEFERRED: none created by this review. The prior revised-arm review card is discharged. A G-2
review is not codex_1 work unless the coordinator orders the read and publishes a new handoff.
