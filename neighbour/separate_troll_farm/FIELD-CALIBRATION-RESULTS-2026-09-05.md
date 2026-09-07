# Field pilot and evaluation reset — 2026-09-05

## Decision

Do not publish V564 or resume the late-worker queue. The frozen pilot against actual ranked agents
found no competitive support for either dense policy over V468. All three policies lost all three
matchups; V468 had the smaller losing margin in every block. This is a useful negative screen, not
a calibrated rank estimator or proof that V468 is the best archived policy.

The local-to-platform disagreement is real, not merely an exported-code discrepancy: after fixing
our replay reader, the exact local compacts reproduced all 2,552 turns of the nine scored games.
The goal monitor and evaluation contract were corrected. No gameplay source or ladder submission
changed. A post-pilot room read still showed agent 6701731 at 13.92, rank 155/177, fully evaluated.

## Frozen experiment and integrity

`FIELD-CALIBRATION-PROTOCOL-2026-09-05.md` was written before any new game. Ten unranked games
were requested sequentially, counting the A/A repeat; no play request was retried. Sources were
hash-checked and independently compiled before the run. No credentials were copied or printed.

The first response omitted opponent identity. The collector stopped immediately, and the same
game's owner-authenticated replay supplied it. A null-owner replay read returned HTTP 422; the
correct owner-scoped read succeeded. The stopped manifest remains intact. A second manifest reused
the already completed first response and requested only the remaining nine games. Both raw play
responses and full replays are archived, with game/score/rank/seed equality checked before identity
was joined. Every opponent matched the requested agent, and each three-policy block matched its
normalized initial input. There were no runtime diagnostics or negative referee failure scores.

V468's A/A games 901533781 and 901534017 against putibuzu produced identical scores (88–126),
ranks, inventories, workforce, 152-turn duration, initial input, and both command streams. The
repeat is excluded from competitive totals. This demonstrates determinism for that block; it
does not guarantee every opponent's future determinism.

## Results against the real field

All games use player zero. Opponents were ranks 7, 1 and 60 in the fresh pre-run leaderboard.
Each table cell is own score–opponent score; all are losses.

| Opponent / seed | V468 | V543 | V564 |
|---|---:|---:|---:|
| putibuzu / 2609050701 | 88–126 | 100–272 | 117–289 |
| delineate / 2609050102 | 160–445 | 228–661 | 224–601 |
| PonyPonyCodeCode / 2609056003 | 128–219 | 39–251 | 71–299 |

| Policy | W / D / L | W+0.5D | Mean own score | Mean margin |
|---|---|---:|---:|---:|
| V468 | 0 / 0 / 3 | 0 | 125.33 | -138.00 |
| V543 | 0 / 0 / 3 | 0 | 122.33 | -272.33 |
| V564 | 0 / 0 / 3 | 0 | 137.33 | -259.00 |

V564's mean own score exceeds V468 by 12, but its margin is 121 worse. Against putibuzu and
delineate, both dense policies raise own score while increasing the opponent's score still more.
This is precisely the interaction excluded by the old own-score selector. It is not evidence
that margin alone now predicts rank: the outcome measure has no separation in this tiny pilot.

Game IDs in block/policy order (V468, V543, V564):

- putibuzu: 901533781, 901534044, 901534095;
- delineate: 901534217, 901534142, 901534190;
- PonyPonyCodeCode: 901534283, 901534308, 901534254.

Three different seed/opponent blocks do not separately estimate map and opponent effects. They
cover one seat and are too few for meaningful superiority confidence or a rating conversion.
These maps are now development data. A larger prospective confirmation must use new maps and
broader opponent coverage; the pilot cannot justify an automatic submission or top-seven claim.

## Concrete strategic failure

Against putibuzu, V543 and V564 both buy a `2/1/1/3` second worker on turn 2. That worker has
power three but only one carrying slot. Neither policy ever buys worker three. V543 performs 99
harvest actions and 96 drops; V564 performs 117 and 112. **Neither issues a single CHOP, and both
finish with zero wood.** Putibuzu finishes with 60 and 72 wood, respectively. V468 chops 78 times,
banks 22 wood and ends its different trajectory at turn 152 instead of 300.

The replays show repeated planted lemon sources being felled by the opponent. The last midgame
lemon source disappears by turn 78 in V543 and turn 75 in V564. Both have zero banked lemons at
every sampled checkpoint from turn 50 through 300. V543 ends with 100 fruit points and V564 with
117, but the required lemon component for the planned third worker never arrives.

The source explains the missing fallback: the first two workers are permanently classified as
producers (`ordinal < 2`). `choose_goal` prioritizes bill acquisition and then unrestricted ripe
fruit harvesting before considering chopping. An unavailable fruit deficit can also keep iron
acquisition behind an impossible fruit task. The roster bill remains active indefinitely. Thus
the policy can spend the entire game harvesting abundant irrelevant fruit while a capable chopper
never reaches the wood branch. This is an observed full-game failure, not a claim that every
two-worker or dense-orchard strategy fails.

Against PonyPonyCodeCode, V543 buys its third worker only on turn 244 and V564 on turn 229;
they chop just 3 and 9 times and bank 2 and 6 wood. Against delineate they do acquire four workers,
but finish with 48/51 wood against 157/146. Avoiding worker starvation is necessary on some maps
but does not alone establish a competitive orchard economy on others.

## Validation tooling defects found and repaired locally

The initial command audit matched eight games exactly but differed on V468 turns 42 and 44 in
game 901534283. Three reruns reproduced the same local mismatch. This was not a random timeout.

The official Java `Board` retains plants in creation order. `SpritePool` allocates increasing tree
sprite IDs; `CompressionModule` serializes plants through a Java `HashMap`. Its diff iteration
order need not be creation order. The neighboring decoder's insertion-order assumption therefore
does not reproduce the protocol's tie-breaking order. Sorting reconstructed plants by their
sprite creation IDs removed both discrepancies. Our `audit_candidate_command_streams.py` now
restores that ordering without changing any neighboring file. Tests cover reversed diff order
and replanting a cell with a new sprite identity.

The same audit had omitted the decoder's existing optional CHOP context. When damage cancels
same-turn growth, a visual health diff can omit both changes. Our adapter now supplies effective
commands from both players, respecting the first-command-per-unit rule. A behavioral fixture
reproduces health 8 from the old context-free path versus the correct 6. This independent fix did
not explain the two real-game mismatches; creation order did. Other historical analyses that
directly use the neighboring decoder may still need auditing before relying on exact states.

All nine scored games now match their platform commands on all 2,552 turns. Ninety local
startup/first-turn/exit trials are also recorded. Local startup timing is not a reproduction of
platform startup and does not establish the cause of V543's historical seven first-action timeouts.
The earlier two failing audit JSONs were preserved alongside the corrected audit.

`monitor_platform_agent.py` now requires rank 1–7 in the highest division, exact agent/submission
identity, 160 distinct finished games, full rollout, and a five-minute confirmation interval by
default. Score 25 or rank 9 can no longer count as success. Missing evidence resets confirmation;
duplicate or pending games cannot manufacture maturity. `EVALUATION.md` replaces the old charter's
goal and selection assumptions, while leaving `panel_gate.py` intact as a legacy diagnostic.

Validation: the full repository suite passed 384 tests in 108.46 seconds. The final focused replay,
collector, outcome-summary, monitor and legacy-gate suite passed all 41 tests after the source
snapshot handling was finalized. `git diff --check` was clean. These checks validate tooling and
specific fixtures, not seventh-place playing strength.

## Next gameplay work

1. Freeze executable fixtures from the putibuzu denial trajectory: a depleted training resource,
   two existing workers, surviving payable wood, and enough remaining time to bank it. Verify
   that the controller abandons unattainable acquisition and gives existing capacity a productive
   job. Test complete harvest/plant/chop/drop transactions, not just marker substitutions.
2. Evaluate one capability-based continuation with collectible full-trip value, explicit
   resource-source reachability and a funded worker-payback decision. Compare with exact V468,
   V543, V564 and an earlier archived reference; do not assume a turn-100 prefix or fixed roster.
3. Test it prospectively against real resource denial and productive orchard opponents on new
   maps, then expand both-seat and opponent coverage before any ladder claim. The old eight-map
   panel is a regression screen, not the selector.

V368 should be included as an earlier reference, not an assumed champion: its exact source once
reached 25.21/rank 17 and later 21.06/rank 37. That spread cautions against selecting an archive
by its single best rollout. Neither this pilot nor the old local gates establishes that V468 is
the strongest historical source.

## Artifacts and reproduction

All generated data and binaries are below
`/data/separate_troll_farm-working/analysis/2026-09-05-field-calibration/`:

- `dry-run/`: frozen source identities and the three compiled compacts;
- `pilot/`: original stopped manifest and first response;
- `verified-pilot/`: complete manifest, three immutable source snapshots, ten raw responses,
  ten full replays and three audit reports.

Manifest SHA-256:
`9378d1c326b00606883c34105334d63befbc536f7b167452c823b9244d6d9a1d`.
Corrected audit SHA-256:
`1a3fbcd8db208c1ec70c5740d5a38717cfa8502f9e06ffc8bb2f815939e999bf`.

The collector is intentionally a frozen pilot, not a general benchmark tuner. Its default is a
dry run; `--run` issues unranked games, and it refuses existing output manifests. The offline
audit can be rerun without network access using `audit_field_pilot.py`, the saved manifest,
`--binaries .../dry-run` and a new `--output` path. Set
`TMPDIR=/data/separate_troll_farm-working/tmp` and `PYTHONDONTWRITEBYTECODE=1`.

Production hashes are unchanged: `bot.rs`
`b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
`submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`.
The neighbor remains at `370fa63cae12eda129ff5553c33a7086dfcb87c2` with only its pre-existing
modified stats and untracked panel. No submission, repository cleanup or neighbor write occurred.
