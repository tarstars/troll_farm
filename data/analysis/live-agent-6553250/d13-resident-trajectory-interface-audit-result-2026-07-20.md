# D13 resident trajectory interface audit — development result (2026-07-20)

## Decision

**Build a spatial `KEEP + action` resident residual environment.  Encode previous resident intent
and the other worker's proposed intent.  Begin training with `KEEP + legal local actions`; retain
the same spatial actor shape so point-of-interest moves can be enabled in a later stage.**

This authorizes environment construction and smoke testing only.  No candidate, resident,
submission, prospective, or Arena state changes.

## Complete execution

All 192 planned resident games completed on seeds 24--39, both seats, and the frozen six-opponent
panel.  They produced 104,192 exact resident unit decisions—median 588 per game—with 52,471
distinct full-state fingerprints and 103,423 distinct state/unit pairs.

The resident trained exactly two workers in all 192 games.  Its development-block mean terminal
margin was +40.97, but the range remained broad (-275 to +360), providing both successful and
adverse trajectories for subsequent full-game learning.

## Interface gates

| Frozen measurement | Result | Rule | Decision |
|---|---:|---:|---|
| resident commands directly decodable | **100%** | at least 95% | pass |
| residual options, nearest-rank p95 | **45** | at most 64 | pass |
| eligible target persistence | **45.02%** | at least 20% | include previous intent |
| multi-worker decisions | **98.31%** | at least 10% | include other-worker intent |
| states with a legal local action | **53.90%** | retain POI moves if below 20% | local-only Stage A is viable |

The complete point-of-interest vocabulary averages 32.20 options, has p95 45 and maximum 63,
so it is also tractable.  `KEEP` is encoded as the move-plane cell under the active unit; the
remaining executable actions use the existing 13 × 22 × 11 spatial head.

## Why intent must be explicit

The resident repeats the same verb in 71.55% of consecutive unit decisions, repeats the exact
command in 26.54%, and preserves a nonempty target in 45.02% of eligible decisions.  Intent age
has median one, p95 eight, and maximum 77 turns.  These long tails are invisible to the D11
observation except for one previous action plane.

Almost every post-opening decision is joint: 102,428/104,192 decisions occur with two workers.
The resident never gives both workers the same nonempty target in this block.  That zero-collision
property is a concrete coordination invariant; a residual actor must see the other worker's
proposed command and target before overriding anything.

Consecutive `MOVE` commands never repeat the same explicit target in this data.  The resident
often emits the next routed cell rather than a persistent high-level destination.  Therefore the
new observation should encode both the current resident command and short history rather than
mistake raw move coordinates for the complete task assignment.

## Action distribution

The resident's decisions are 53.42% `MOVE`, 30.36% `CHOP`, 7.38% `DROP`, 3.10% `WAIT`, 2.27%
each `PICK` and `PLANT`, 1.04% `HARVEST`, and 0.16% `MINE`.  The starter and trained worker are
nearly balanced in volume.  Local productive actions are available in 51.79% of starter states
and 56.09% of trained-worker states.

Stage A therefore keeps every resident route and asks the learner to choose among `KEEP` and
currently executable local actions.  Unlike the rejected D11 advisory layer, the new policy will
be trained on these exact resident states, observe joint intent, and receive full-game margin
reward.  If Stage A learns a safe positive residual, Stage B can expose the already-audited
point-of-interest move mask without changing the network layout.

The shadow D11 actor agrees exactly with only 9.01% of resident decisions and agrees on the verb
in 37.16%.  This is descriptive confirmation of the distribution mismatch; D11 remains closed
and those rates do not define the new policy or any gate.

## Next implementation

Construct a vectorized exact environment with these invariants:

1. compute the stable resident's full joint command once per referee turn;
2. expose one unit at a time with current, previous, and other-worker command planes;
3. interpret the active unit's move-plane/current-cell action as `KEEP`;
4. permit only exact legal local alternatives in Stage A;
5. retain all other resident commands and run the resulting joint command through the exact
   referee;
6. use score-margin change so the episodic return telescopes to the full-game terminal margin;
7. prove deterministic `KEEP` parity against the resident and measure random-action degradation,
   action-mask validity, and batch throughput before PPO.

## Evidence

- protocol: `d13-resident-trajectory-interface-audit-protocol-2026-07-20.md`;
- games: `d13-resident-trajectory-interface-audit-games-seeds24-39.tsv`, SHA-256
  `2c74c019db2a6ae970f782559b90529a257535afbbe7e570111f992c34476060`;
- decisions: `d13-resident-trajectory-interface-audit-decisions-seeds24-39.tsv`, SHA-256
  `d4184600ef9d7f5d10da0e13bab6443d99daea093600512c22db909b10b221e8`;
- analysis: `d13-resident-trajectory-interface-audit-2026-07-20.json`, SHA-256
  `981a3562977eab4a057e4c3532505c86717213c653d472dc2bcf2366aee89694`;
- analyzer: `cgauto/d13_resident_trajectory_analysis.py`, SHA-256
  `7c380da8a3fd790da5e2b291b746352aeeb0cdffda487b3007314d1f3d8cfaf9`;
- instrumented exact runner: `rust/src/bin/d11_recipe_catalog.rs`, SHA-256
  `2a859ba16e7fce36764432852feb5ccedf53e45921a254d0e2baeb23264b137f`.
