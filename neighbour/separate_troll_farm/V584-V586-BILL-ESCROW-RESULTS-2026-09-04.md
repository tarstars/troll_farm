# V584--V586 minimum third-worker bill escrow

## Verdict

Selectively refusing V468 seed picks does not create a viable third-worker bill. V584, V585, and
V586 produced identical gameplay on the 24-game behavior smoke. They preserved V468 exactly at
turn 100, but fell behind by 3.38 points at turn 200 and 13.17 points at the end, changing the
outcome record from 19/1/4 to 17/0/7. None trained a third worker.

The failure is structural rather than a source-activation tuning miss. Immediate activation, one
living source of every bill fruit, and one ripe source of every bill fruit all reached the same
protected-pick states and emitted the same commands. Refusing a seed pick saved isolated fruit but
also severed the corresponding plant/pick continuation. The bot then waited instead of renewing
the source, lost 25.79 chops per game, and still never held the complete plum/lemon/apple bill.

Every arm fails the checkpoint and +40 final-score gates. No candidate entered the frozen
192-game panel, fresh maps, duels, packaging, or platform publication. `bot.rs`, `submission.rs`,
and the live V543 platform agent remain unchanged.

## Isolated candidates

All three candidates derive directly from V468. They run one V468 controller against the real
state for the authoritative command vector and keep a second V468 controller warm for safe
replacement actions. The wrapper is byte-identical to the real controller until worker two is
observed and permanently returns to it if a third worker ever appears.

The proposed third is fixed at `1/1/1/1`; with two existing workers its bill is three plum, three
lemon, three apple, and three iron. Once an arm activates, the shadow view masks exactly that
three-fruit reserve. The wrapper changes only a real `PICK` that would take a banked bill fruit
below its reserve, using the same worker's non-pick shadow action when it is collision-safe and
`WAIT` otherwise. All harvests and all other real V468 actions retain priority.

Only after the full fruit bill is banked may the observed harvest-zero axe stop normal work, mine
the three iron, bank it, and append `TRAIN 1 1 1 1` from a post-pick-affordable and
post-move-shack-clear state. The hire remains retryable until worker three is observed. At least 96
turns must remain.

The arms differ only in the activation predicate:

| arm | activation after worker two |
|---|---|
| V584 | immediately |
| V585 | at least one living plum, lemon, and apple tree |
| V586 | at least one ripe plum, lemon, and apple tree |

The same unreferenced legacy controller removed in V581--V583 is omitted for source headroom. All
three compact programs are 91,179 UTF-16 units. The readable and compact forms compile
independently, all paired runners compile, the private-identifier transform round trips exactly,
and all 175 repository tests pass.

## Behavior smoke

Each arm ran seed 9,941,000 in both seats against all 12 frozen opponent families: 24 games per
arm. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | candidate W/T/L | workers | issues |
|---|---:|---:|---:|---:|---:|---:|
| V584 immediate | +0.00 | -3.38 | -13.17 | 17/0/7 | 2.00 | 0 |
| V585 living sources | +0.00 | -3.38 | -13.17 | 17/0/7 | 2.00 | 0 |
| V586 ripe sources | +0.00 | -3.38 | -13.17 | 17/0/7 | 2.00 | 0 |

V468 scores 94.67/160.67/215.46 at turns 100/200/final; every candidate scores
94.67/157.29/202.29. The baseline goes 19/1/4. Candidate score is negative against eleven of the
twelve opponent families and flat against `legend_v8_hp2_four`.

Twenty of 24 games change commands. Their first divergence ranges from turn 116 to turn 294
(mean 227.0), and they differ for 25.85 command turns on average. The selected gameplay fields,
including full command streams, are identical across all three arms; the activation sweep exposes
no safer timing regime on this map.

## Mechanism

The candidates retain V468's two opening harvests and eight initial ring plants, so they do not
repeat V579's broad producer takeover. The narrow pick restriction nevertheless breaks the
renewable score loop:

| per-game mean | V468 | candidate | change |
|---|---:|---:|---:|
| `PICK` | 13.38 | 8.88 | -4.50 |
| `PLANT` | 13.38 | 8.88 | -4.50 |
| `CHOP` | 182.79 | 157.00 | -25.79 |
| `DROP` | 38.71 | 34.29 | -4.42 |
| `WAIT` | 11.00 | 28.75 | +17.75 |
| final wood | 53.21 | 48.79 | -4.42 |

The first blocked seed is not merely one point withheld from scoring. V468 normally consumes the
banked seed and immediately plants it, so preventing that pick also prevents the next source
generation. The masked shadow often has no productive same-worker alternative and returns
`WAIT`. Fruit remains stranded by species: an arm can protect three of one or two types while the
missing type never reaches its reserve. Consequently the full-fruit latch never opens, the axe
never starts the iron trip, and the only train in every candidate game remains V468's opening
`TRAIN 3 2 0 2` at median turn 6.

This closes the third-worker-funding line under the current two-worker V468 economy. V578--V580
showed that actively gathering a complete bill destroys the main producer's income; V581--V583
showed that passive surplus never exposes a complete bill; V584--V586 now show that a minimal
per-pick escrow destroys the renewal loop before completing the bill. Another variant of the same
funding mechanism is not supported by the evidence.

## Reproduction and integrity

- builder/test: `build_v584_bill_escrow.py` / `test_build_v584_bill_escrow.py`
- canonical runners, smoke panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v584-v586-bill-escrow/`
- V584/V585/V586 panel SHA-256: `3b6fae7ed5ec4e935222e243c31ff7e40dbc9fc69533e3770ee95218792ebc28` /
  `83db855378321c555e444eabdb0953d5f57e74afe1d3989129512391b87719ac` /
  `8c8a9d82c25a25707f5a2afc86aefd9aefc338cc8a350904e7ec49e01050e4e5`
- V584/V585/V586 gate SHA-256: `a56fddbb2fd21ca67f13b50b6387f309ae9d37694bd4741f76c09836820a6c09` /
  `f9eb7f35da442702f7349749fafff265b3bc8dda91745419b2e52f025a8b137d` /
  `53fc4d69ff9030152f75bfb44451c2a4842a757223616a81db2ccde38db125c8`
- V584/V585/V586 diagnostics SHA-256: `fab9eef3f6d1d0f07503ef441bda5b3f3766a3ddc88cd2fc1f994568417a1664` /
  `f70aa1c1daf1837c424a0d3cec4c6a760ed8353fa4926f02e716e4ea746c29d4` /
  `d3f63d3a337d92ab0da124e004159ea111c68e53e063ccac619336f17d2d0690`
- V584/V585/V586 module SHA-256: `97b0d2a5ca293bde0538523f6db1dbd93ef70ff10d888b7323f91a941de77acb` /
  `77f05d23ca0c55236df62c5bc0b5796b0343262b1fc50fbb0020ede58ce6122e` /
  `d25cceef0f0a6a662b252e52339acadb41afbd838bebf5699c1b99d32b597f68`
- V584/V585/V586 compact SHA-256: `ce2485a00ba7f47d6d8d6c8e8bf58d8e125be6f84afaa781f63fdfafc0213f55` /
  `9d8ecd8f55c57dbf90307b6179f5f82ed75dfb5b2a395da30c7415e5fdce0830` /
  `ae7a2d3cbd695e3251a806241505b3afc61d0f646ec51aa30bbb18f34b0b037b`
- V584/V585/V586 runner SHA-256: `8f23901f255daac13a8ec424b6dc35b886828d686fea0161bb185fd1f5b8f763` /
  `5ad4d1306f1b7b22ac22f0255f173e826d03b5058adde02a9dde44cea8a311e7` /
  `a9157d42ad181c4903fa0fe8d4460e67f35e9a6d9fab6fcb5902bd47b919de6b`
- builder/test SHA-256: `bd36ca854d95e8cfba9a85bc2a38ecb78a1f82b84e93a538a282f2dcad0df402` /
  `6d19ff5214e31778def1594e76f734ba9db34d0fd448ea4ce495264a28e54454`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
