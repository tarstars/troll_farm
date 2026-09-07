# V587 fresh rank-seven replay gap re-baseline

## Verdict

The live seventh-place threshold remains 26.99, but rank is not a stable proxy for one policy's
absolute strength. The current rank-seven entry is putibuzu agent `6479779`, submission
`40708982`. The exact same agent and submission was rank 13 at 24.92 on 2026-08-02 and is now rank
7 at 26.99: a gain of 2.07 rating points and six places without a program-version change. The two
public replay windows overlap in 63 games and contain 198 unique games in union, confirming that
the platform has re-evaluated the unchanged agent on a materially different schedule.

The fresh replay evidence still identifies a useful architectural direction. Rank seven finishes
114 of 116 current games with exactly two workers, and rank eight finishes 121 of 122 with two.
More importantly, the rank-one bot's 58 two-worker games already average 278.10 score, 60.71 wood,
34.72 planted crops, 47.53 wood recovered from its own crops, and a 43/1/14 outcome record. It
replants 95.43% of reaped crops with the same type. Parallel orchard throughput can therefore be a
step change before a third worker exists; scaling the roster is not its prerequisite.

The next candidate line should be a scratch two-worker task allocator that owns a multi-cell crop
pipeline from planting through harvest, size-four felling, banking, and immediate same-type
replanting. This is deliberately not another protected-tree overlay on V468, another third-worker
bill, or the previously rejected putibuzu door-factory graft. No gameplay candidate was built or
published in this evidence iteration. `bot.rs`, `submission.rs`, and the live V543 agent remain
unchanged.

## Captured field

At 2026-09-04 22:49 UTC the read-only collector fixed the exact current top-15 leaderboard
identities, then fetched and decoded every terminal game returned by their public recent-battle
endpoints:

- 15 exact agents and submissions;
- 1,861 listed finished occurrences;
- 1,735 unique games;
- 1,861 decoded occurrences;
- zero fetch/decode failures;
- zero unknown state-diff updates.

The stored audit rebuilds to summary SHA-256
`e33cf23ba2f2beef5350837793fadf89ec9ccfc114128989440c7d22651558da`.
An offline validation of the captured inventory and summary passed.

The live boundary was:

| rank | player | rating | exact agent | games in window | W/T/L |
|---:|---|---:|---:|---:|---:|
| 1 | delineate | 30.91 | 6479768 | 137 | 111/1/25 |
| 6 | viewlagoon | 26.99 | 6481504 | 109 | 65/0/44 |
| 7 | putibuzu | 26.99 | 6479779 | 116 | 74/0/42 |
| 8 | tonigineer | 26.94 | 6505289 | 122 | 87/1/34 |
| 10 | R1FA | 26.73 | 6479863 | 116 | 75/1/40 |
| 15 | Bondo416 | 26.22 | 6480941 | 108 | 72/0/36 |

Only 0.05 rating points separate ranks seven and eight, while rankings one through fifteen span
4.69 points. V543 remains 13.92/rank 155 in the authoritative arena room.

## Version and schedule boundary

The historical 2026-08-02 inventory contained 145 games for the same putibuzu agent/submission;
the current one contains 116. Sixty-three game IDs overlap, 53 are current-only, and 82 are
historical-only. The current window goes 74/0/42 (63.79% wins); the 198-game deduplicated union goes
112/0/86 (56.57%). The change in replay-window composition is large enough that the current win
rate must not be read as a controlled improvement by the unchanged code.

The mismatch is even stronger against V543. Rank seven's current window has 52 distinct opponent
agent identities; V543's mature 160-game archive has 35. Exactly one identity appears in both.
Consequently the following raw facts are descriptive, not a causal head-to-head:

| current public window | games | win rate | mean score | mean wood | mean margin |
|---|---:|---:|---:|---:|---:|
| putibuzu rank 7 | 116 | 63.79% | 243.86 | 46.47 | +23.48 |
| V543, all | 160 | 53.75% | 320.69 | 71.33 | +10.31 |
| V543, excluding its seven startup timeouts | 153 | 56.21% | 335.46 | 74.59 | +11.69 |

V543 has much higher raw score and wood yet a much lower rating. This does not show that score is
harmful; it shows that cross-schedule means cannot select a rating patch. The frozen paired gate
remains necessary for candidate decisions.

## Rank-seven behavior

Putibuzu's current program is a two-worker adaptive factory:

- 114/116 games finish with two workers; the other two are catastrophes with no successful train;
- the most common second-worker specification is `2/2/2/2` in 49 games;
- `2/2/1/2` appears in 16 and `2/2/3/2` in ten, with the remaining games spread across affordable
  movement/carry/harvest/chop combinations;
- the current window averages 19.80 planted crops, 64.02 harvests, 104.89 chops, 46.47 final wood,
  and 25.94 wood collected from its own crops;
- 244 of 293 reaped crops are replanted with the same type, an 83.28% rate.

Wins do not reveal a narrow target-selection patch. Against losses, they have only 11.54 more own
score and 1.34 more final wood; the much larger difference is opponent score, 180.04 in wins versus
291.45 in losses. Wins also have 3.83 more own plants and 7.15 more own-crop wood, but these are
partly opponent-strength effects. With only one common V543 opponent, they cannot justify copying
one rank-seven action rule.

This also prevents reopening V441--V454. Those candidates already grafted putibuzu's measured
door factory and adaptive second-worker purchase onto the champion, and none gained four own
points consistently. The fresh data contains no version change or new causal evidence that would
repair that specific graft.

## Repeatable two-worker bridge

The cross-agent commonality is stronger than the rank-seven win/loss correlation:

| exact current subset | games | W/T/L | mean score | wood | plants | own-crop wood | same-type replant |
|---|---:|---:|---:|---:|---:|---:|---:|
| rank 7, two workers | 114 | 74/0/40 | 246.81 | 47.02 | 19.77 | 26.14 | 82.93% |
| rank 8, two workers | 121 | 86/1/34 | 237.57 | 51.12 | 30.14 | 36.21 | 86.40% |
| rank 1, two workers | 58 | 43/1/14 | 278.10 | 60.71 | 34.72 | 47.53 | 95.43% |

Rank one's two-worker subset averages 143.14 chops and 60.86 harvests, so the orchard is not
created by idling an axe. It lands 39.17 chops and 10.31 plants by turn 100, then continues the
same crop lifecycle without movement blockages. The whole rank-one window creates 40.69 crops and
banks 97.12 wood per game, but these 58 games prove that its productive lifecycle already works
before the third-worker branch.

This isolates the missing architecture from the failed lineage. V455--V586 tried to preserve or
wrap V468's job planner; protected saplings made its assigned worker wait, while third-worker bills
took resources from the active income loop. The supported alternative is one controller that
jointly assigns both workers across several concurrent crops and always has harvest, chop, bank,
or replant work available. A scratch controller can then earn the crop surplus before deciding
whether any later worker is affordable.

## Reproduction and integrity

- analysis/test: `analyze_v587_rank7_gap.py` / `test_analyze_v587_rank7_gap.py`
- current inventory:
  `/data/separate_troll_farm-working/analysis/2026-09-04-v587-rank7-gap/top15-inventory.json`
- current top-15 audit:
  `/data/separate_troll_farm-working/analysis/2026-09-04-v587-rank7-gap/top15-audit.json`
- version-aware report:
  `/data/separate_troll_farm-working/analysis/2026-09-04-v587-rank7-gap/rank7-gap-report.json`
- inventory/audit/report SHA-256: `7c9c6d4e3a50937b1c7dc000c4d86b684b097b2011ab02217e4278e06bea5698` /
  `019c9f68534d83601ad739ec6bf51446b4221568f6e762b06a72ed8148957110` /
  `8c1f7677ef93b4c04c542cd54efce78c1dc4c526c4aeea2924ce8579c56440fa`
- analysis/test SHA-256: `c72d2ad9c014bf029f3af1a2100d06cc967103bd65c2399ef036b89fea72b149` /
  `37895d9f5bce619d8c8eb177e447bdff63b1a6074a2fdb050d27ca5caf5f7265`
- historical inventory/audit SHA-256:
  `74e0b0d9c8ed630abbfa4cba6c132611950454e8b8d18c751a53d085ecc49bc4` /
  `8c29f433982fa9df05e16203bccdc15f290bae36ff5801084e862a882547af5a`
- V543 mature replay summary SHA-256:
  `b6dfaf1e16c9697e2ba0d67318a542f3b6c8c0d6cd4a4107e83e9f6f1c83ea02`
- all 181 repository tests pass; the captured top-15 audit also passes its independent offline
  inventory/summary reconstruction
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
