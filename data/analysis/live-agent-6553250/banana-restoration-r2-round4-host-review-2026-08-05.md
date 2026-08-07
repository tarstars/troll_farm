# Banana restoration R2 round-4 host review

Date: 2026-08-05

Task: `20260802-banana-restoration-r2`

Candidate: `candidate-banana-r2.min.rs`, 77,397 bytes, SHA-256
`9f5ef8336c5268927dd3aef873a1a348dd9e0bb43c2cc1e505b14730352db8a2`, canonical artifact
commit `b358124f9d39139dbbde87a70a1a36bf5625debe`.

## Verdict

**IMPLEMENTATION_INVALID pending another revision.** Round 4 repairs all three findings from the
round-3 review: the conversion race now has one absolute-time oracle, the real candidate responds
to a real ownership flip, and the strict feasible/infeasible boundary is candidate-driven and
red/green. The first broad host panel nevertheless exposes a separate, terminal contract failure:
a full second worker carrying two wood oscillates between two cells for 225 consecutive turns
instead of returning to a door and dropping its cargo.

This violates the original owner contract and the candidate's own I-19/I-20/I-21 and D-1 rules.
The remaining banana-live, exact game `897829265`, value, and Arena gates stop for this exact hash.
No Arena or TestSession mutation occurred.

## Independently reproduced local gates

- deterministic rebuild gives 77,397 bytes and exact SHA `9f5ef833...`; inverse-transform asserts
  pass;
- optimized compact and readable sources compile; readable SHA is `f2406fe7...`;
- detector tests pass 28/28 and `conversion_race_oracle.py` self-test passes;
- compact and readable binaries both pass the complete R-1, R-2a/b, R-3a/b, R-4, and control
  suite;
- the real R-4 trace plants at turn 3, flips at turn 11, begins conversion at turn 12, and chops
  turns 15--19 under oracle result `completion 18 < opponent harvest 27`;
- old SHA `2f58edef...` remains RED for the right reason: R-3b emits no mother chop at the feasible
  one-turn edge and R-4 emits `WAIT` after the flip;
- transport/pipeline adjunct checks pass 41/41 and 24/24 respectively; those do not override the
  host failure below.

The build rewrites only the manifest's absolute local path in the detached review worktree; source
bytes remain exact.

## Broad host panel — terminal failure

The candidate was embedded as the actual outer `BananaBot`, not as its inner
`SecureOrchardBot`, in the existing continued-referee runner. The exact stable parent
`a8eb3b2b...` was the baseline. The already-consumed open range was 43 maps beginning at
`9,854,000`, both seats, and all six opponent families: 516 paired tasks total. Referee library
SHA was `1802bd8d...`; base runner SHA was `d9a118d7...`; the generated BananaBot runner SHA was
`7948478f...`.

The run completed all 516 tasks in 127.867 seconds. It is not a value estimate. Its role is to
exercise the implementation broadly before replay/value gates.

- 444/516 tasks differ in terminal outcomes;
- the candidate has a longer position period-2 episode than the parent in 298/516 tasks;
- candidate maximum period-2 length is 225 turns;
- candidate p95 decision latency is 0.778 ms and maximum is 6.059 ms, so timeout is not the cause;
- panel TSV SHA is `548c103d...`.

Terminal divergence alone is expected on activated banana maps and is not the rejection. The
225-turn no-progress episode is.

## Exact counterexample

Task: map seed `9,854,000`, seat 0, opponent family `gold_adaptive`. Both parent and candidate
train the second worker at turn 1. A single-thread candidate replay with per-turn pre-state and
commands reproduces:

- worker 2 obtains two wood and starts the failing interval full: carry vector
  `[0,0,0,0,0,2]`;
- turns 34--258 inclusive, 225 turns total, it alternates `(8,4) -> (8,3) -> (8,4)`;
- commands alternate exactly `MOVE 2 8 3` and `MOVE 2 8 4`;
- no `DROP`, cargo loss, inventory credit, or other progress occurs during the episode;
- at turn 258 it still carries both wood;
- baseline terminal margin is +68; candidate terminal margin is -93 (paired delta -161).

The raw diagnostic trace contained 300 candidate turns, 32,885 bytes, SHA `c7d6e033...`. The
decisive first and last commands are:

```text
t34 (8,4), wood=2: MOVE 2 8 3
t35 (8,3), wood=2: MOVE 2 8 4
t36 (8,4), wood=2: MOVE 2 8 3
...
t255 (8,3), wood=2: MOVE 2 8 4
t256 (8,4), wood=2: MOVE 2 8 3
t257 (8,3), wood=2: MOVE 2 8 4
t258 (8,4), wood=2: MOVE 2 8 5
```

This is D-1 by construction: at least three A->B->A cycles with zero progress. It also violates
I-21 because a full wood carrier must enter commitment, I-19 because a committed carrier may only
move monotonically toward a reachable door or drop, and I-20 because non-progress persists far
beyond the one-turn conflict tolerance. The candidate source explicitly declares zero such
episodes as its threshold.

## Pipeline-v2 review finding

Claude's mechanized pre-review at canonical commit `c6ea01ab...` passes 24/24 unit tests and
reports CLEAR on `9f5ef833...`, but its task config names only I-9, I-10a, I-7, and D-8 as critical.
It does not gate I-19/I-20/I-21 or a candidate-driven D-1 full-cargo two-worker trace. Its own
`INSTRUMENT_GAP` answer explicitly defers multi-unit coordination to the host replay gate.

Per the new policy, this review finding must become a permanent failure-ledger class and an
executable red/green gate. A successor needs a candidate-driven two-worker scenario in which a
full wood carrier is exposed to the banana reservation/protection seam and reaches a door and
`DROP`s monotonically. The current `9f5ef833...` bytes must be RED on that scenario; the successor
must be GREEN. A locally CLEAR pre-review may not be described as complete implementation
validity while mandatory host-only gates remain pending.

## Disposition

Do not run the remaining banana-live, exact `897829265`, value, or Arena gates for exact SHA
`9f5ef833...`. Preserve the repaired conversion-oracle regressions. Diagnose the first command
divergence that starts worker 2's turn-34 oscillation, repair the banking/reservation interaction,
add the new failure class to pipeline v2, and return a new source hash and canonical v2 handoff.
