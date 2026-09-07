# V609--V611 carry-aligned mature worker: smoke pass reverses on frozen panel -- 2026-09-05

## Verdict

V609 discovered a large standard-map gain from changing V595's second worker from carry two to
carry three. Its native selected train became `TRAIN 2 3 0 2` at turn 14 and scored
+12.00/+20.38/+39.83 against exact V468 at turns 100/200/final. Adding the isolated mature lane
in V610 raised the smoke to +12.00/+29.83/+40.00 and passed every smoke gate exactly. This was a
real, active improvement on map 9,941,000, not a protocol or traffic artifact.

The frozen eight-map panel decisively rejected it. Across 192 paired games V610 scored
-34.72/-49.37/-42.01, went 131/0/61 against V468's 177/3/12, banked 4.0 less wood, and let
opponents gain 46.01 score. Mandatory carry three delayed the successful train from mean turn
9.5 to 54.3; two games never trained. The standard smoke map was the only map where the carry
bill completed by turn 20. V611's carry-four bill was already untenable on that map, moving the
train to turn 98 and scoring -79.67/-65.58/+2.71.

No fresh maps, 400-game duels, packaging audit, production change, or platform publication ran.

## Candidate family

`build_v609_carry_aligned_mature_worker.py` derives every arm from V595, ultimately V468:

- V609 changes only the opening policy's preferred and maximum carry to three and makes that
  preference mandatory; it has no new orchard code;
- V610 applies the same carry-three policy to V607's harvest-free cap-six lane, which activates
  at turn 101 and masks typed worker plots from the starter planner;
- V611 changes only V610's carry requirement from three to four and raises each carry enumeration
  clamp from three to four;
- harvest remains zero, chop and movement are chosen by the native opening objective, and the
  native bill collector decides when the requested worker is affordable.

The policy chooses movement to match the feasible bill rather than retaining V468's movement
three: V609/V610 train `2/3/0/2` at turn 14 on the smoke map, while V611 trains `2/4/0/2` at turn
98. This behavior is intentional and measured by the capability-only V609 control.

| arm | role | compact UTF-16 units |
|---|---|---:|
| V609 | mandatory carry-three capability control | 87,572 |
| V610 | carry-three isolated mature lane | 97,781 |
| V611 | carry-four isolated mature lane | 97,781 |

V610 and V611 normalize to exact equality after changing the two carry-policy constants and the
three carry clamps. All three readable programs compile independently, and every compact artifact
is below 100,000 UTF-16 units.

## Standard-map smoke

Each arm ran map seed 9,941,000 in both seats against all 12 frozen opponent families: 24 paired
games per arm. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | wood delta | train | candidate W/T/L | smoke gate |
|---|---:|---:|---:|---:|---|---:|---|
| V609 carry-three control | +12.00 | +20.38 | +39.83 | +9.79 | `2/3/0/2`, turn 14 | 19/0/5 | fail by 0.17 final |
| V610 carry-three lane | +12.00 | +29.83 | +40.00 | +10.42 | `2/3/0/2`, turn 14 | 17/0/7 | PASS |
| V611 carry-four lane | -79.67 | -65.58 | +2.71 | +0.83 | `2/4/0/2`, turn 98 | 10/0/14 | fail checkpoints |

V610 adds 9.46 turn-200 points over its capability-only control but only 0.17 final point. Its
opponents gain 53.92 score and it adds two losses versus V609, so the smoke pass was never enough
to bypass the frozen panel. V609 had zero issues, V610 three rows with noncritical blocked moves,
and V611 ten such rows; all had zero critical and unclassified issues.

The carry-policy change affects the opening collector immediately. Median first command
divergence was turn 1.5 for all smoke arms, and mean changed command turns were 264.08, 266.71,
and 269.50. The improvement comes from a different complete economy, not only from collecting one
more wood on a late fell.

## Frozen 192-game gate

V610 ran the mandated maps 9,941,000 through 9,941,007, both seats and all 12 families. Deltas are
candidate minus exact V468.

| measure | V468 | V610 | delta |
|---|---:|---:|---:|
| score turn 100 | 93.01 | 58.29 | -34.72 |
| score turn 200 | 176.18 | 126.81 | -49.37 |
| final score | 247.25 | 205.24 | -42.01 |
| final wood | 45.00 | 41.00 | -4.00 |
| opponent score | 108.19 | 154.20 | +46.01 |
| ring harvests | 68.29 | 39.08 | -29.21 |
| ring drops | 97.52 | 62.13 | -35.39 |
| all chop commands | 155.08 | 117.65 | -37.43 |
| all move commands | 193.29 | 264.29 | +71.00 |
| outcomes | 177/3/12 | 131/0/61 | 46 additional losses |

The full panel had 25 rows with only noncritical blocked moves and zero critical or unclassified
issues. Removing every such row cannot explain checkpoint losses of 35--49 points. First command
divergence ranged from turn 1 to 8 with median 1, and 273.78 command turns per game changed.

## Train-time mechanism

The carry-three lemon cost is ten for the second worker, versus five at carry two. On the smoke
map, nearby supply lets V610 complete that extra bill at turn 14 and the larger worker pays. On
the other seven frozen maps, mandatory preference makes the sole starter collect or wait for the
larger bill while V468 has already trained its second worker. The loss scales with that delay:

| candidate effective train cohort | rows | mean train | turn-100 delta | turn-200 delta | final delta |
|---|---:|---:|---:|---:|---:|
| through turn 20 | 24 | 14.0 | +12.0 | +29.8 | +40.0 |
| turns 21--40 | 71 | 34.7 | -16.0 | -36.1 | -38.1 |
| turns 41--60 | 33 | 54.5 | -28.4 | -31.3 | -9.6 |
| turns 61--100 | 44 | 83.1 | -72.5 | -92.0 | -87.9 |
| after 100 or never | 20 | 133.6 effective | -84.7 | -127.8 | -106.9 |

Per-map evidence makes the smoke selection bias explicit:

| map seed | completed train mean | turn 100 | turn 200 | final | wood |
|---:|---:|---:|---:|---:|---:|
| 9,941,000 | 14.0 | +12.0 | +29.8 | +40.0 | +10.4 |
| 9,941,001 | 60.6 | -31.2 | -26.0 | -3.2 | +8.7 |
| 9,941,002 | 107.3, 2 never | -87.6 | -122.6 | -103.6 | -1.5 |
| 9,941,003 | 57.9 | -37.3 | -37.1 | -8.4 | -1.9 |
| 9,941,004 | 36.0 | -11.0 | +2.6 | +35.2 | +8.8 |
| 9,941,005 | 38.0 | -27.9 | -50.7 | -65.1 | -8.8 |
| 9,941,006 | 31.2 | -9.8 | -61.4 | -86.8 | -18.3 |
| 9,941,007 | 94.2 | -85.1 | -129.6 | -144.1 | -29.5 |

The candidate adapts movement and chop downward to make the mandatory carry bill feasible:
the full field includes `2/3/0/2`, `1/3/0/2`, `1/3/0/1`, `2/3/0/1`, and `3/3/0/2` workers.
That preserves the requested capacity but not the smoke map's productive speed/chop combination.

## Conditional-purchase upper bound

An obvious response is to request carry three only when it is cheap. The frozen rows rule out that
line as a path to the required +40 by itself:

- a hindsight selector using V610 only when it beats V468 at all three checkpoints selects 21
  rows and gains just +1.54/+3.87/+4.82;
- selecting all 64 final-positive rows gains +12.66 final but loses 2.70 at turn 100;
- selecting only completed trains through turn 20 is exactly the smoke map and gains
  +1.50/+3.73/+5.00 over the whole panel;
- even a perfect map selector can select only 9,941,000 without a checkpoint loss and has the
  same +5.00 final ceiling.

Therefore an ETA cutoff could make carry three safe, but cannot deliver the required step change.
The next iteration will not optimize that bounded line. It will inventory every structurally
distinct frozen 192-game candidate already measured, align their exact rows, and compute
cross-lineage per-map and static-feature portfolio bounds. This will show whether complementary
architectures can support a real selector or which map regimes still have no candidate advantage.

## Verification and integrity

- focused builder tests: 12 passed, covering capability-only scope, carry-three/four requirements,
  enumeration clamps, harvest/chop invariants, structural normalization, standalone compilation,
  and compact limit;
- complete repository suite: 262 passed in 64.19 seconds;
- all V609--V611 readable programs compiled independently;
- canonical runners, build logs, smoke panels, full panel, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-05-v609-v611-carry-aligned/`;
- V609/V610/V611 runner SHA-256:
  `de8c733406a7366a6017f1b4c91b0fed54954bfe824a0ca11f485c6629633168` /
  `0044b1aa929e214accbdba1c83b49979c66d2398e16af7e9fc1f8829dde1d405` /
  `c7fe3d7b2886c3e16201867671ecb949a68ef4c2f9ac9983ef9f9c59837fdc28`;
- smoke panel SHA-256:
  `deb888791898904ddb4fcd721e795e19042fb5f50cc325759a8c578d41f74fb5` /
  `ac30a65cd2c0a3d21c84eda2f87a893f2339d067f157a046234245d4731e2995` /
  `dda5093b3f6f480d7a1c0ca69145cd9e26b6e2b1b9d5982df42d75774d73a877`;
- smoke gate SHA-256:
  `8c941cbecb364834350fb8c2fd7678332d41fe6a185297daddb1776bdba7d957` /
  `2ce4239ba3a628afec8c847c6a5a93e2a6b93b7a5f06b804d296144e9692d4b2` /
  `caea24db4e43e24304472e33a3402b7208a334cd7d513f2910a973ffaa1871e6`;
- smoke diagnostics SHA-256:
  `6437a6fa55192da350ee5a29ed0c189864d8c75019c797ce729649f94aac3a6e` /
  `c67a11a84af9d17f35745d7bcbeee039e24bff5e78d9c42d2281fb3f450ea192` /
  `78fff8c1ad946709b06176919a6365b40fcb61984bced3bf75f42ecc93d062b3`;
- V610 full panel/gate/diagnostics SHA-256:
  `4fc0da7e38ff0f93e6211b4b23df16cd57ecb69f4312b49a1f808ee6cdc93bb1` /
  `78bea81e7b52238cb2ec1622bd3678fb45fe6c6e5a4a76e2b5898a0baac173ec` /
  `e9935ae75ee856dc2c4c8e76192fbcdbebcf1a48c5eb1d9ce8a2c091b321da65`;
- V609/V610/V611 module SHA-256:
  `0a177e7f4e86677d11f686ceb222d4276dbce60bab6da75ba333278f601eb0ec` /
  `62aa611d243d5c96f3a53e6e69eecb52f0be4cdaba4ff80f270c293c8eb55e2e` /
  `a6dcf6d5cd471d9ab8b34067d0cc6dd7cb335eabcf480b0a7913a9135bd45c27`;
- V609/V610/V611 compact SHA-256:
  `c181ae297367cc2b3fb2b87a5635b2309f3318012dc90e3d754f571e0080b12b` /
  `89fe9c52f6daa5c6faf53728165ba2355a2b7686e2474ac29fb12a24b74f875e` /
  `45e3168062c711516c043d25cf50db8e2bda122c013270bacf52f21e51ef8449`;
- builder/test SHA-256:
  `7e55e84eb56e5619833e040ac708de9baef6f3c8258740dfa0946686cc5caf9d` /
  `887da4e6b7aec83175db1c8ab290b19e949806cf489d5b807957b982a33bec14`;
- production remained unchanged: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`,
  `submission.rs`
  `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`;
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`, retaining its pre-existing
  modified `data/processed/stats.json` and untracked
  `data/panels/top5-ab-20260902T115338Z.json`.
