# Compact Gold rollout gate protocol — frozen 2026-07-17

## Candidate

At turn one, simulate exactly two terminal games from the observed initial state:

1. promoted preseed/coverage Yamo control versus the fixed default GoldElite continuation;
2. the global immediate max-affordable movement/carry/chop, harvest-0 worker option followed by
   promoted Yamo versus the same continuation.

Select the option only when its terminal score margin exceeds the control margin by **more than
30 points**.  Otherwise emit the promoted control command.  The choice is seat-specific.  Both
rollouts use the corrected dynamic referee and terminal stall rule.

`CompactGold` is a behavior-preserving fixed form of `GoldElite::new()`.  Alternate constructors,
environment knobs, and write-only memory are removed.  Dynamic command parity is required before
using its measurements.

## Derivation and already-seen evidence

- Seeds 0--59 were the discovery block.  The unguarded Gold sign had an unacceptable tail.  Among
  coarse score margins `0, 5, 10, 20, 30`, 30 was the smallest margin with no losing selected
  seed, positive mean, and positive mean against every deterministic opponent.
- Seeds 60--119 were then inspected without changing the rule.  The frozen `>30` guard scored
  +3.612 mean, selected four seat cells, had one -4.8 seed loss, and retained positive means
  against all five opponents.
- These are reused local maps and offline transfer evidence, not an arena estimate.

## Independent validation block

Use seeds **120--179**, both seats, and the fixed deterministic opponent set:

- `chopharvest`;
- `race`;
- `ringfix3`;
- `taskplan`;
- `yield`.

Run the promoted control and the complete global option on identical map/opponent/seat cells.
Generate the selector decision only from the two CompactGold terminal rollouts.  Do not change
the continuation, threshold, option, opponent set, or scoring after opening this block.

The gate passes only if all conditions hold:

- seed-clustered mean delta is positive;
- every opponent mean delta is nonnegative;
- the minimum seed delta is at least -10;
- no more than two of 60 seed-clustered outcomes are negative;
- control remains the exact fallback on every unselected seat.

Failure closes this live-rollout candidate.  Passing permits byte-budget and official-timing work,
not submission.  No arena write is authorized by this protocol.
