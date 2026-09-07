# V600--V602 low-power producer-chop orchard conversion

## Verdict

Replacing only V468 producer wood opportunities preserved the intended command boundary but did
not create a second crop lane. Cap-one V600 scored `+0.00/-1.21/+10.58` at turn 100/200/final on
the 24-game behavior smoke and failed a checkpoint. Cap-two V601 recovered to
`+0.00/+0.92/+12.75`; cap-three V602 was gameplay-identical. Both remained far below the required
`+40` final gain.

The producer did pick more seeds, but V468 did not adopt forced seeds into its active transaction.
Across the V601 panel, all 115 baseline producer `PICK` commands were followed immediately by
`PLANT`. The candidate issued 207 producer picks; only 104 were followed by `PLANT`, while 72 were
followed by `DROP` and 31 by `MOVE`. Producer plants rose just 0.54 per game and axe plants fell
2.46, leaving total plants 1.92 below V468. Harvests remained exactly 2.00.

V601 gained 2.71 wood, broadly retaining V595's maturity benefit, but removed 13.54 ring chops,
added 28.21 moves and 12.96 waits, and ran 16.75 turns longer. This is not a scalable economy.
No frozen 192-game panel, fresh maps, duels, packaging, audit, or platform publication ran.
`bot.rs`, `submission.rs`, and the live V543 agent remain unchanged.

## Isolated candidates

All candidates derive from V595, which itself runs one live V468 controller on every turn. The
opening remains exact through turn 100. With exactly two workers, the added layer can write only
the slot of the harvest-positive/chop-one producer and only if its inherited action is `WAIT`,
`CHOP`, or a `MOVE` whose current target is a tree.

Inherited `PICK`, `PLANT`, `HARVEST`, `DROP`, cargo handling, and training are never replaced. At
an empty producer's own bank, the layer may replace a wood action with a one-fruit `PICK` only
when at least two of that fruit are banked. V468 then retains complete control of routing and
planting. A matching later `PLANT` is tagged as a producer-lane crop; unrelated V468 plants are
not.

The layer protects tagged crops below size two from producer chops, preferring a ripe tagged crop
for harvest and otherwise redirecting to a non-owned tree. Projected landings exclude the axe.
V595 remains responsible for protecting and positively targeting all own crops with the
power-two axe. The only arm difference is the live tagged-crop cap:

| arm | producer-lane cap | compact UTF-16 units |
|---|---:|---:|
| V600 | 1 | 92,953 |
| V601 | 2 | 92,953 |
| V602 | 3 | 92,953 |

The modules normalize to exact equality after replacing the cap constant. Every readable program
compiles independently, every paired runner compiles, and all 226 repository tests pass.

## Behavior smoke

Each arm ran map seed 9,941,000 in both seats against all 12 frozen opponent families: 24 games
per arm. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | candidate W/T/L | wood delta | decision |
|---|---:|---:|---:|---:|---:|---|
| V600 cap one | +0.00 | -1.21 | +10.58 | 19/1/4 | +2.17 | reject |
| V601 cap two | +0.00 | +0.92 | +12.75 | 19/1/4 | +2.71 | reject |
| V602 cap three | +0.00 | +0.92 | +12.75 | 19/1/4 | +2.71 | reject |

V468 scored 94.67/160.67/215.46 and banked 53.21 wood. V601 scored
94.67/161.58/228.21 and banked 55.92. Its own-score delta ranged from -3 against `mybot` to +34
against `silver_boss`; outcomes did not change. Opponents gained 7.46 points while games ran
16.75 turns longer.

All arms retained exactly two workers and the same `TRAIN 3 2 0 2` at median turn 6. First
divergence ranged from turn 101 to 266 with median 234, and V601 differed on 66.42 command turns
per game. V600 had zero issues. V601 and V602 each had one `compact_gold` row with six noncritical
blocked moves, caused after the injected cargo entered inherited routing; there were no critical
or unclassified issues.

V601 and V602 match in every selected TSV field and every command stream. The third slot is never
reachable: two tagged live crops already saturate the seed conversion V468 is willing to retain.

## Mechanism

The structural preservation rule worked, but state coupling made the economic expectation false.
The final candidate-state commands were:

| per-game command count | V468 | V601 | delta |
|---|---:|---:|---:|
| producer `PICK` | 4.79 | 8.62 | +3.83 |
| producer `PLANT` | 4.79 | 5.33 | +0.54 |
| producer `HARVEST` | 2.00 | 2.00 | +0.00 |
| producer `DROP` | 13.50 | 16.42 | +2.92 |
| producer `CHOP` | 95.54 | 93.75 | -1.79 |
| axe `PLANT` | 8.58 | 6.12 | -2.46 |
| axe `CHOP` | 87.25 | 81.25 | -6.00 |

V468's seed behavior is phase-coupled. Its own producer picks are emitted only after it has chosen
a valid planting transaction, which is why all 115 lead directly to a plant. A seed injected on a
wood phase is not equivalent: the planner often banks it again, adding a pick/drop pair with no
crop. Even successful tagged plants never produced an added harvest before V595's size-two axe
felling, so the proposed seed multiplier remained zero.

This also explains why cap one made more picks yet scored less than cap two. Its tagged crop was
cleared sooner, reopening the injection gate and repeating more unproductive pick/drop cycles.
Caps two and three converge because the native planner never maintains a third tagged crop.

The next experiment has a new reason to revisit harvest talent. V470 showed that adding harvest
power to the second worker without a job was unused; V601 now shows that adding seeds without a
complete job is discarded. The missing composition is to reserve the original apple engine,
train a harvest-capable second worker only when its bill fits, and give that worker an explicit
seed, plant, harvest, mature-fell, bank, and refill lifecycle while leaving the starter under V468.

## Reproduction and integrity

- builder/test: `build_v600_low_power_producer_orchard.py` /
  `test_build_v600_low_power_producer_orchard.py`
- canonical runners, smoke panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-05-v600-v602-producer-orchard/`
- V600/V601/V602 panel SHA-256: `e312c093846724605ae878f90495c8a5b99bfed5c5a07c7de33e9c77c31fc375` /
  `29581853d6b9dc1e7bf094010c8c102c27e9082d9cb0eb624999de6c240bb4f8` /
  `35027813f47f56c5fea705cafd4e82e1268346c6e03e296c3e5e71f34364fd1d`
- V600/V601/V602 gate SHA-256: `c6b5edf20bfe906f073f424310496b50aa7f1ce36b639a77a0ea44c4746beaa3` /
  `47a231238f681d9c67cbac4f3fe20dfbdad9916eba94bb4c6e35ab4d1c31ffab` /
  `78405d2487016212fd0c19fde8c93c4529990bf5335ddd0d00bc661e7866c49c`
- V600/V601/V602 diagnostics SHA-256: `666f3a3093cea85a6bcba7bb0b90f4d7cdf302cafb6017e1c0df76c25ef486f9` /
  `0425ae2dd12bae81a886c7d772bb730469f043596de394249f697c9fd73618c2` /
  `c5ac6525225b7a0134178f0de701e700ed5a266e4e98f0c559dbd640ef23351e`
- V600/V601/V602 module SHA-256: `04a0dceccb64dac5bd3dfd8f9136a1d2ad8279e9b51cc0cbbfbb7b38132d864f` /
  `527340d806b3b920f079cec1a525451db9d28e24f83e2b49c34da0a32024b753` /
  `a88d4db06bceae898f36e4daf02bf758e11889a4d604cb8fa61a2b3c5cafe913`
- V600/V601/V602 compact SHA-256: `38f5e76c0d40d0d5badb8f9d288e99739b96ecac648634be7afc166869b15ebd` /
  `55d1fa9d06a1c2013189fe140f4f9d9bde8f599da23f2025b504fd682d516c43` /
  `7c3f146362af87307198d91b0ea0b2dc639c18edcb041a4c40596a0ec0719070`
- V600/V601/V602 runner SHA-256: `dd84ac911242648ac4a19d62f16145761e16e8e3c186d5bb1c5148f4e0ba3a5a` /
  `bb05d529ea4301d4ab547975aae1337416dc73c1b1c7abcd87461c353fb1130b` /
  `9a00f89eab8e00f94aac3dceca2e76974afa3fff12bac1dd160a258320e2fbf2`
- builder/test SHA-256: `87f216e3473133bd1f2e5edbfaef59ddc9949bd61ff7d4ca93918f5e5ffad8cd` /
  `86d990961540ab110fd98f45d9274bde4e888fce05642cdec5fa057c710353d2`
- production hashes retained: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
