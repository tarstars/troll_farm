# V616--V618 persistent producer seed transaction: completion without throughput -- 2026-09-05

## Verdict

V616--V618 repaired V600's broken action boundary: every explicitly routed producer seed reached
a matching `PLANT`, with zero transaction drops or unfinished jobs. That correctness did not
create an additional crop lane. Caps one, two, and four scored respectively
`+0.00/-4.79/+5.13`, `+0.00/-2.63/+8.75`, and `+0.00/-3.42/+9.88` at turn 100/200/final on the
24-game behavior smoke. Every arm failed the turn-200 checkpoint and the required +40 final gain.

V618 was the most active arm, completing 48 routed plants across ten games. Compared directly
with its V595 parent on the same rows, it nevertheless planted 0.21 fewer crops per game, made
28.54 more moves, made 6.83 fewer chops, and finished 0.54 points lower. Its explicit plants
replaced native one-turn producer plants rather than adding to them. The V468 two-worker action
and seed schedule is saturated; transaction continuity alone cannot produce the required economic
step change.

No frozen 192-game panel, fresh-map panel, duel, packaging audit, production change, or platform
publication ran.

## Candidate family

`build_v616_persistent_producer_seed_transaction.py` derives the family from V595, ultimately
exact V468, and retains one live inherited controller plus V595's carry-matched size-two axe
policy. It adds one durable producer job and varies only the number of confirmed transaction
crops allowed to remain live:

| arm | live crop cap | compact UTF-16 units |
|---|---:|---:|
| V616 | 1 | 94,645 |
| V617 | 2 | 94,645 |
| V618 | 4 | 94,645 |

The transaction may start only after turn 100, before turn 251, with exactly the inherited two
roles, an empty harvest-positive producer at its bank, at least two matching bank fruits, and an
inherited idle or wood action. It selects a reachable own-half plot outside V468's native ring,
within two bank steps, excluding resources, doors, units, plants, and the axe's projected landing.
Once a seed is picked, the job persists across turns, retargets an occupied or collision-prone
plot, and emits only `MOVE`, `PLANT`, or `WAIT`; it never drops the cargo.

The wrapper records a typed attempt only when the real producer issues the matching plant command,
then confirms that type from the next real state. Confirmed crops remain real for wrapper routing
and V595's axe but are masked as inert occupied cells for the inherited planner, preventing the
producer from cutting them. The modules normalize to exact equality after replacing the cap
constant. All three readable programs compile independently, and each compact artifact is 5,355
units below the platform limit.

## Standard-map smoke

Each arm ran map 9,941,000 in both seats against all 12 frozen opponent families, for 24 paired
games. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | own wood | opponent score | ring plants | candidate W/T/L |
|---|---:|---:|---:|---:|---:|---:|---:|
| V616 cap 1 | +0.00 | -4.79 | +5.13 | +0.83 | +10.96 | -0.63 | 18/2/4 |
| V617 cap 2 | +0.00 | -2.63 | +8.75 | +1.75 | +10.33 | -0.96 | 19/1/4 |
| V618 cap 4 | +0.00 | -3.42 | +9.88 | +2.04 | +12.38 | -1.08 | 19/1/4 |

V468 scored 94.67/160.67/215.46, banked 53.21 wood, allowed 145.21 opponent score,
recorded 7.96 ring plants, and went 19/1/4. All candidates retained two workers, the same
`3/2/0/2` train specification, and median train turn 6.

The cap response confirms that the branch was live. V616/V617/V618 completed 22/37/48 routed
producer plants. Their candidate wood rose to 54.04/54.96/55.25, while ring chops fell from
V468's 71.08 to 62.29/57.54/55.75 and mean game length rose from turn 272.46 to
287.88/285.75/290.92. Larger transaction capacity bought a little wood but surrendered more
wild-tree pressure and gave opponents 10.33--12.38 additional score.

V616 and V617 reported no issues. V618 had one noncritical `move_blocked` report in the
seat-one `compact_gold` row and no critical or unclassified issues. The wrapper excludes its
deterministic projected axe landing on every pickup and route turn; the remaining event follows a
later referee tie between shortest paths. One row cannot explain the broad economic response.

## Transaction completion

The producer command streams distinguish V468's native immediate transactions from wrapper-routed
ones. Every native V468 producer pickup was followed immediately by a plant. In each candidate,
the extra route contained one or more `MOVE`/`WAIT` actions and still ended in a matching plant:

| producer stream | picks/plants | immediate plants | routed plants | routed kinds B/L/A | mean route delay | routed plants per game |
|---|---:|---:|---:|---:|---:|---:|
| V468 baseline | 115/115 | 115 | 0 | 0/0/0 | -- | 0.00 |
| V616 | 148/148 | 126 | 22 | 11/5/6 | 3.55 turns | 0.92 |
| V617 | 143/143 | 106 | 37 | 19/10/8 | 3.76 turns | 1.54 |
| V618 | 151/151 | 103 | 48 | 22/12/14 | 3.94 turns | 2.00 |

All 107 routed jobs across the family ended in `PLANT`; none ended in `DROP` or remained
unfinished. V618's routed-count distribution was zero in 14 rows, one in three, four in one, six
in three, seven in one, and eight in two. Its activation is therefore concentrated in the ten
rows where surplus and geometry permit it, rather than being a weak effect in every game.

This exactly repairs V600--V602, where 72 injected pickups were immediately dropped. It also
shows why repair is insufficient: V618's 48 routed plants coexist with 12 fewer immediate plants
than V468, and total producer planting rises only from 4.79 to 6.29 per game. The second role's
planting simultaneously falls through the altered downstream state.

## Comparison with the V595 parent

The V595 smoke uses the same row keys and exact V468 baseline fingerprints. Fourteen of 24 V618
candidate command streams remain byte-identical to V595; the ten active rows isolate the
transaction layer. Mean deltas below are V616--V618 minus V595, not minus V468:

| arm | turn 100 | turn 200 | final | own wood | opponent score | ring plants |
|---|---:|---:|---:|---:|---:|---:|
| V616 | +0.00 | -6.29 | -5.29 | -1.42 | +3.29 | -0.46 |
| V617 | +0.00 | -4.13 | -1.67 | -0.50 | +2.67 | -0.79 |
| V618 | +0.00 | -4.92 | -0.54 | -0.21 | +4.71 | -0.92 |

The per-role command budget makes the substitution explicit:

| commands per game | V595 producer | V618 producer | V595 axe | V618 axe |
|---|---:|---:|---:|---:|
| PICK / PLANT | 6.58 / 6.58 | 6.29 / 6.29 | 5.38 / 5.38 | 5.46 / 5.46 |
| HARVEST | 2.00 | 2.08 | 0.00 | 0.00 |
| CHOP | 105.04 | 95.21 | 78.21 | 81.21 |
| MOVE | 134.79 | 151.71 | 151.83 | 163.46 |
| DROP | 15.71 | 13.00 | 21.46 | 22.67 |

Across both roles, planting falls from 11.96 to 11.75 per game, moves rise from 286.62 to
315.17, and chops fall from 183.25 to 176.42. V618 also extends games by 10.71 turns and loses
V595's extra win-equivalent outcome: V595 went 20/1/3, V618 19/1/4. The new lane consumes the
same finite seeds and producer turns that supported native immediate plants and wood collection;
it does not operate in parallel.

This closes explicit post-turn-100 producer seeding on V468's inherited wood slots. Further cap,
plot-radius, or persistence tuning cannot resolve the measured action-and-seed ceiling. The next
iteration changes the controller architecture using the independent rank-one replay evidence: a
shack-local farmer, rapid capable second worker, banana-dominant mature orchard, and explicit
role allocation, rather than another mutation of V468's saturated schedule.

## Verification and integrity

- focused builder suite: 13 passed, including exact lineage, prefix and action ownership, cargo
  persistence, retargeting, geometry and projected-collision exclusion, typed next-state
  reconciliation, planner masking, cap normalization, compact size, standalone compilation, and
  registered outputs;
- complete repository suite: 295 passed in 78.14 seconds;
- canonical runners, build logs, standalone binaries, smoke panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-05-v616-v618-persistent-producer-transaction/`;
- V616/V617/V618 runner SHA-256:
  `947a5cf55495a2a6162ec8390310cc351fb662b9f7f9481a52636ee6236acef8` /
  `90e5820feffa74cda0d72ec5f8d6f29e0ce8962e8c63e9d59b4cbf9f42ba2b49` /
  `a67fc21338bbea6a696ab23e34378ac0ed7f6d18efdb95c064107e1adf53043a`;
- smoke panel SHA-256:
  `1a78ced7b21630222b43da5835e3f157ca4645ea6a132639df9fa3c31738e602` /
  `176690798cb0e7208cdeb7f647e7e6e3a1491de6329623be55c67e79685d667c` /
  `2f96131239e03a88c28e7435254ceba2761f08e695f2a1c7d033864fcfcacff9`;
- smoke gate SHA-256:
  `945af232198e289c942e247bf49c43c0bafda3e07a3d46b11939a389eb2bc8bc` /
  `0fe2f32065a5a5fcf39ebc75d1e5e19072238ce6b83a46e14624bf4d8ece98b9` /
  `204b519e28dd802bc4d694b86a7a86ec21224429a5734dc9241709009710ddc6`;
- smoke diagnostics SHA-256:
  `424dc02ab90736d8dd419cde60caf349ff2297264a23a6f7be55b5ceae932b5d` /
  `7e4ec0fe671ea268d230c0cdb71162edb85e56f5da2ecda33b059229738a9041` /
  `d269116ca6525c37d86e23bb76c8b927cc6d5d6617c7d74ecf5a90d0662e31e1`;
- module SHA-256:
  `503033067a89185d73b6487bdf69e69820db8ad5747dad19b18774b6abf54031` /
  `25a0fd5c4c304b2bdee90355935928de93059683aa55ce0e463e5213556846d1` /
  `1118007938ed3d5aacd1fdecc1c657ebbbee80f13379035c4d953390e3ced506`;
- compact SHA-256:
  `f056ca7bd7540f1a0fccd7d1525c6457e8362bef0bd624c35578fbd950aaadf8` /
  `c9d58d00f80d7935f32d2a986c0dfec1420c291a0a0dfaebe044d3cdfecbfe83` /
  `475476fb302f2b38b77261363a70b39f4acf777f016e50b4d597d3b8954fd478`;
- builder/test SHA-256:
  `b211d755aa1d37d25b4ac8fc2ff9421b01e361ffbc6df7aacb9becdc2fbe3cbf` /
  `e0efeba41f3b41945a5c89375aafd5a07b37b9c46d42226b23102385b562ed1e`;
- production remained unchanged: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`,
  `submission.rs`
  `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`;
- the neighboring checkout remained read only at
  `370fa63cae12eda129ff5553c33a7086dfcb87c2`, with its pre-existing modified
  `data/processed/stats.json` and untracked `data/panels/top5-ab-20260902T115338Z.json`.
