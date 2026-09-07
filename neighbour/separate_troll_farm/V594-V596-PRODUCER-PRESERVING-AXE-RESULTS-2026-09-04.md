# V594--V596 producer-preserving owned-crop axe

## Verdict

Redirecting only V468's harvest-zero axe preserves producer throughput and produces a small,
consistent gain, but it cannot supply the required step change from V468's existing crop count.
Protection-only V594 scores +0.00/+1.79/+9.75 at turn 100/200/final on the 24-game behavior smoke.
V595's positive size-two priority improves that to +0.00/+1.50/+10.46. V596, which requires empty
fruit before the same priority, is gameplay-identical to V595.

V595 keeps V468's 2.00 harvests exactly on this seed and gains 2.25 wood, accounting for almost all
of its 10.46-point score gain. The intervention is safe but begins too late and has too little raw
material: median first divergence is turn 234, V468 supplies only 13.38 plant commands, and the
candidate actually performs 1.42 fewer plant/refill cycles after protecting saplings. It reaches
only 26% of the required `+40` final gain, so no arm is credible for the frozen 192-game panel.

The next mechanism must retain this producer boundary while using otherwise empty axe time and
banked surplus fruit to establish additional parallel crop slots. Protection alone can improve
wood yield per existing crop; it cannot create the roughly threefold plant throughput seen in the
public leader.

No full panel, fresh maps, duels, packaging, or platform publication ran. `bot.rs`,
`submission.rs`, and the live V543 platform agent remain unchanged.

## Isolated candidates

All candidates derive from exact V468 after removing only unreferenced controller and analysis
code. One real V468 controller runs on every turn. Its chosen harvest-positive producer action is
never replaced. The outer `RecklessCropFinishBot` records its own final `PLANT` commands from turn
one and reconciles a persistent crop set against the next state.

Commands remain exact through turn 100. Afterward, modification is allowed only with exactly two
workers, on the harvest-zero/chop-positive axe, and only while that axe carries nothing. Training,
cargo banking, the producer, and any later roster are outside the override scope.

An axe target on a recorded size-one crop is blocked while maturation to size two and banking fit
before the end. The replacement chooses the best reachable nonprotected tree and is accepted only
if its projected landing differs from the producer's. A forced protection collision yields
`WAIT`; an optional mature-tree redirect collision retains the real V468 action.

The modes are:

| arm | behavior after turn 100 | compact UTF-16 units |
|---|---|---:|
| V594 | protect owned size-one crops only | 87,573 |
| V595 | protect, then prioritize any owned size-two crop | 87,573 |
| V596 | protect, prioritize owned size two only with zero fruit | 87,573 |

Every readable and compact program compiles independently, all paired runners compile, the arms
normalize to exact equality after replacing the mode constant, and all 205 repository tests pass.

## Behavior smoke

Each arm ran seed 9,941,000 in both seats against all 12 frozen opponent families: 24 games per
arm. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | candidate W/T/L | wood delta | decision |
|---|---:|---:|---:|---:|---:|---|
| V594 protection | +0.00 | +1.79 | +9.75 | 22/0/2 | +2.00 | reject |
| V595 mature-any | +0.00 | +1.50 | +10.46 | 20/1/3 | +2.25 | reject |
| V596 mature-empty | +0.00 | +1.50 | +10.46 | 20/1/3 | +2.25 | reject |

V468 scores 94.67/160.67/215.46, banks 53.21 wood, and goes 19/1/4. V595 scores
94.67/162.17/225.92 and banks 55.46 wood. It gains against 11 opponent families, from +2 against
`compact_gold` to +21.5 against `script_boss`, and loses two points against `mybot`. Opponent mean
score rises 7.71 as games run 7.75 turns longer, so outcome changes remain a safety observation,
not the selector.

V594 and V595 first differ from V468 in all 24 games between turns 102 and 266, with median turn
234. V595 differs on 56.75 command turns per game. There are zero legality, critical, or
unclassified issues. Every arm retains exactly two workers and V468's `TRAIN 3 2 0 2` at median
turn 6.

V595 and V596 have identical selected gameplay fields and full command streams in all 24 rows.
Thus the fruit-empty condition does not expose a distinct regime: crops eligible for positive
size-two redirection are already empty whenever the choice matters. Relative to protection-only,
positive priority changes seven rows, adds just 0.71 final score and 0.21 wood, and gives up 0.29
at turn 200.

## Mechanism

The direct producer-preservation objective succeeds. V591's whole-policy handoff removed 30.97
harvests and 39.18 deposits on the diverse panel. V595 changes neither of this smoke's two
harvests and changes deposits by only -1.54, despite 56.75 command-divergence turns. Only axe slots
are assigned by the new code; the producer always retains the command selected by the live V468
controller for the candidate state.

The cap is crop supply:

| per-game mean | V468 | V595 | change |
|---|---:|---:|---:|
| `HARVEST` | 2.00 | 2.00 | +0.00 |
| `CHOP` | 182.79 | 183.25 | +0.46 |
| final wood | 53.21 | 55.46 | +2.25 |
| `PLANT` | 13.38 | 11.96 | -1.42 |
| `PICK` | 13.38 | 11.96 | -1.42 |
| `DROP` | 38.71 | 37.17 | -1.54 |
| `MOVE` | 275.67 | 286.62 | +10.95 |
| `WAIT` | 11.00 | 19.46 | +8.46 |

Protection lets some crops reach size two and converts the extra wood to about nine score, but
waiting and rerouting also suppress about one and a half of V468's existing renewals. Positive
priority cannot act until a recorded crop exists and matures; the median turn-234 first divergence
shows why it has no early economic multiplier. It rearranges the fate of V468's small orchard
rather than increasing concurrent crop count.

The difference from V591 is useful. V591 actively built 19.73 crops per game and demonstrated that
the lifecycle can add wood, but replaced the valuable producer. V595 retains that producer but
builds no additional slots. A viable synthesis therefore needs the axe to establish a bounded
secondary orchard from already-banked fruit while leaving all producer choices under V468.

## Consequence

The next experiment should preserve this exact single-controller/axe-only boundary and add a
small state machine for the empty axe: when post-turn-100 bank fruit is safely available and the
producer's landing is clear, pick one seed, plant a near-bank slot, protect it to size two, fell it,
and refill it. Sweeping one, two, and three additional live slots tests whether crop multiplication
can repay the axe travel without touching producer harvests. This is newly supported by V595's
clean +2.25 wood conversion and V591's evidence that additional slots, rather than later maturity,
are the missing scale variable.

## Reproduction and integrity

- builder/test: `build_v594_producer_preserving_axe.py` /
  `test_build_v594_producer_preserving_axe.py`
- canonical runners, smoke panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v594-v596-producer-axe/`
- V594/V595/V596 panel SHA-256: `45725871c754582717f6023db619a935e1b76272cc48550aa828d09255fac859` /
  `fb1968469e3a138c878e28c211be3b410805fa6eea7e7d91fb4c782f4f3f2c07` /
  `adc308470aa970f780a0446f1fb00692e5fbb57cea3b85b437c3beb482092da4`
- V594/V595/V596 gate SHA-256: `778ea7ed5e6b47382b41469ba78ad7b3f3ea727a18465889e7b280d739dbb214` /
  `cd3093b2e64cd4ee087d3fac88e05b8735cfa911b2f6e49b5417c0490492d21c` /
  `60a07f407aa2810ad730d4fd18dae6444c46bad0623a088a28c4c0bd06c8e0e4`
- V594/V595/V596 diagnostics SHA-256: `59e62df206060d16dd23e59196b21f2f05457e4c30424daf056f465edee825ef` /
  `a1ce2b01d8c7624a781378d5867581a7f12d4b8784c5306304acfcbb02b6a2bd` /
  `8c1353f63cf32ccac945ba5929e5aaf14f76cdc76f3bf719244d4a92f078905a`
- V594/V595/V596 module SHA-256: `ab477634e22be51d506a7511ddec04d34dfbc2ec1971896de71564bbacd9526b` /
  `07adf69b4c6a037c924519b0a767de6b9d7eb99a260c4115b4f19b5d5f11a4a0` /
  `dc3ed20c954b38b24a69b1ddea3bf1940e50c86939e97d4b4bcd2fd646ab1edf`
- V594/V595/V596 compact SHA-256: `d61373d881c094f4206532f400910f72b48f7cce1f773dbd4c479e0e5f20e017` /
  `0aa1dc86a53745a0afec90bce05dc6017c400d70b7c81e60b12bd27a55486098` /
  `b18a84cb3ac4bd33487de0ff8b6869b530ebeec4c1a623d484859b1d3f51a759`
- V594/V595/V596 runner SHA-256: `85da01e99a085ebf46b482166faedc73017d75a8f4ca926aef3d3a60b770ba54` /
  `600796ac51f6535d484a98b1c016c894b4a302d64eb1c2c3009fbf6fb63c4eed` /
  `b672d5cb44e691e9368424416d22c498bbb324b20bb5b63427f7819542b73887`
- builder/test SHA-256: `29e2a58cdda9af70fb8fb64ff26ea535862e9dd79595a1faf1d5178bfb4a7ec8` /
  `112941d8d2962291c0ad21969b8fa78b23ce6244614ebeff7cfae01bf8150e16`
- production hashes retained: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
