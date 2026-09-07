# V588--V590 two-worker parallel orchard

## Verdict

The bill-free two-worker R1FA handoff improves final score on the seed-9,941,000 behavior smoke,
but it does not produce the required orchard step change. V588, the best cap-six arm, is exact to
V468 through turn 100, falls 2.38 points behind at turn 200, and finishes only 13.04 points ahead.
Caps eight and ten make both the checkpoint deficit and final result worse. All three therefore
fail the unchanged checkpoint and `+40` gates and did not enter the frozen 192-game panel, fresh
maps, duels, packaging, or platform publication.

The failure identifies a concrete controller defect. The inherited R1FA allocator harvests any
ripe tree before starting seed work and its chop selector does not protect `self.planted` trees
until maturity. Consequently it turns the producer into a map-wide fruit collector instead of
maintaining repeated owned crop lifecycles. V588 adds 26.58 harvests and 59.21 moves per game but
removes 3.63 plants and 31.71 chops, and banks 4.13 less wood than V468. Increasing the crop cap
adds plant commands without increasing wood. The next experiment must encode ownership,
maturity, felling, and same-kind refill as allocator invariants rather than changing this cap.

`bot.rs`, `submission.rs`, and the live V543 platform agent remain unchanged.

## Isolated candidates

All three candidates derive from `candidate_v468_no_denial_bonus_module.rs`. They run the exact
V468 controller through turn 100 and initialize the R1FA state only on its first call. The later
controller assigns the harvest-positive starter as producer and the harvest-zero, power-two
second worker as axe. Shared goal reservations and move-conflict repair remain active.

`next_spec` returns `None` for every two-or-more-worker state, so after handoff there is no bill,
mine assignment, or third-worker train. If one worker is lost, the existing affordable-first
recovery path can restore worker two. The arms change only all three occurrences of the live
post-handoff owned-crop cap:

| arm | crop cap | compact UTF-16 units |
|---|---:|---:|
| V588 | 6 | 99,759 |
| V589 | 8 | 99,759 |
| V590 | 10 | 99,762 |

Every readable and compact program compiles independently, every paired runner compiles, and all
188 repository tests pass. The three source arms normalize to exact equality after replacing the
cap literal.

## Behavior smoke

Each arm ran seed 9,941,000 in both seats against all 12 frozen opponent families: 24 paired games
per arm. Deltas are candidate minus exact V468.

| arm | turn 100 | turn 200 | final | candidate W/T/L | final wood | issues |
|---|---:|---:|---:|---:|---:|---:|
| V588 cap 6 | +0.00 | -2.38 | +13.04 | 21/0/3 | 49.08 | 0 |
| V589 cap 8 | +0.00 | -4.33 | +11.67 | 21/0/3 | 49.00 | 0 |
| V590 cap 10 | +0.00 | -5.42 | +10.17 | 21/0/3 | 49.08 | 0 |

V468 scores 94.67/160.67/215.46 and banks 53.21 wood. Its outcome record is 19/1/4. All
candidates keep exactly two workers and emit only V468's `TRAIN 3 2 0 2` at median turn 6. First
command divergence is turn 101--121 (median 101), proving the real turn-100 prefix rather than a
score-only coincidence. V588 differs for 167.25 command turns per game. None has a legality,
critical, or unclassified issue.

V588's own score is positive in 17 of 24 paired rows and nonnegative in 18. At the family level it
is positive against ten, flat against `script_boss`, and negative against `boss_real`. This is a
real but much too small final improvement, and the negative turn-200 checkpoint independently
rejects it.

## Mechanism

The cap-six arm gives the clearest form of the failure:

| per-game command/resource mean | V468 | V588 | change |
|---|---:|---:|---:|
| `MOVE` | 275.67 | 334.88 | +59.21 |
| `HARVEST` | 2.00 | 28.58 | +26.58 |
| `DROP` | 38.71 | 47.08 | +8.37 |
| `PLANT` | 13.38 | 9.75 | -3.63 |
| `PICK` | 13.38 | 1.96 | -11.42 |
| `CHOP` | 182.79 | 151.08 | -31.71 |
| `WAIT` | 11.00 | 0.12 | -10.88 |
| final wood | 53.21 | 49.08 | -4.13 |

At first divergence, V468 is chopping in 18 of 24 games. Fourteen of those turns become a
candidate harvest, and 16 of all 24 candidate first divergences contain a harvest. In the common
turn-101 state the starter leaves V468's chop path to harvest the standing crop while the axe
continues. The resulting fruit and longer games raise final score, but the extra travel delays
income through turn 200 and displaces too much lumber work.

The cap sweep confirms that capacity is not the bottleneck. V589 adds 1.04 plant commands per game
over V588 and V590 adds 2.29, yet all three finish at essentially the same 49 wood and larger caps
score progressively less. Source inspection explains the saturation: the producer's fallback
checks every ripe plant before checking orchard capacity, while `chop_cell` accepts an owned
post-handoff tree at any size. There is no lifecycle state that says “harvest this owned tree,
leave it growing, fell it mature, and refill its species.” `self.planted` is only a live-count and
provenance set. The cap therefore limits simultaneous plants but does not schedule the repeated,
mature parallel cycles observed in the leading public bots.

Opponent mean score also rises 21.83 and games last 22.17 turns longer under V588. The better
21/0/3 outcome count is therefore interaction-sensitive and is not evidence for promotion under
the own-score gate.

## Consequence

A terminal two-worker economy is viable enough to retain, but the general R1FA fallback is not an
orchard controller. The next isolated mechanism should keep cap six and the exact turn-100 prefix,
adopt pre-handoff owned crops where provenance is recoverable, restrict the producer's harvest
priority to the owned lifecycle unless otherwise idle, and forbid the axe from selecting an owned
tree below size four when maturation and banking still fit. A successful fell should create an
explicit same-kind refill obligation. This directly targets the missing throughput without
reopening third-worker funding or another handoff-time/cap sweep.

## Reproduction and integrity

- builder/test: `build_v588_two_worker_parallel_orchard.py` /
  `test_build_v588_two_worker_parallel_orchard.py`
- canonical runners, panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v588-v590-two-worker-orchard/`
- V588/V589/V590 panel SHA-256: `77dea16cd7d57ed9075b798990ae0a2ba027cc99ee6be893a64b777bf6bc57f9` /
  `7f8c377a92a1829753415d031e419650826827d46faf9839f4fdf42ce775c0f7` /
  `5b3256e799dccca81e5bc240de436f7f7aea598e76ae339015336661112c9c68`
- V588/V589/V590 gate SHA-256: `3decead7c2b58fa9b3c8dee080f7bde898bcc52a5004d7cf5d5e86685d90899f` /
  `61444bec76ee41902d092667c23c5ff64db0cb1c7778ed3728a4fd8532d4f517` /
  `960175d02f639bf777b5650b3fd0edd1d4ab0b65071d7bda36e8b38564622b4e`
- V588/V589/V590 diagnostics SHA-256: `1ad3e2ab23a7fa9eeadbd1559f2bf93a53bc4d48b86336f01f0eb6d22698e98a` /
  `601ab78a30ea02fd5842559d838d5d74664cf96c1a9c11b8f7d34957e865dc65` /
  `8eaa497565dc642069dc7b4d180a74a40b755804340a8c90f294874f47b8e2f6`
- V588/V589/V590 module SHA-256: `dcffb1c7a230057559a1b7bf5fe6caeee6ed79eaf9732f1d99b19ef4fa044023` /
  `c4572fb44dd2cbeaca34ed6f63b067719897650642c69d682be3ab3c2d00a087` /
  `0a7b240b738c03405329424ef47411e3ce833fbd033752ce2ca1fd051af169cd`
- V588/V589/V590 compact SHA-256: `b93359fd918270654e803f519f0966dc1df3984efec6d8eb793000baac3301d2` /
  `ed620e12928087a499756ab250332cf50356aabfb7e27b6b77c33ae8a9e11a29` /
  `141084a68df7036bf35cff398766b25bef9c0c35160811a1d2f28eab441f0cdc`
- V588/V589/V590 runner SHA-256: `cd81c6aa66ab01a0885c18af2684a58d1b8076385e1c354c2947028d18e3bd00` /
  `04ce0047c42bc27de6f43c6080f84c78aac485efa4732aa0eab52b0b6bf59dea` /
  `5a822a9aebfb9dce9b3592e6ec441c523e4cb054fdced2605cfc8eda3e218bef`
- builder/test SHA-256: `f38baa20769eeca595e200f4be215755734c5ea58ffee845540368d623a5c094` /
  `0954cb671f0762433977ee9b013369efeb8e908c83c8339dac1a5845535ae098`
- production hashes retained: `bot.rs`
  `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
- read-only neighbor remained at `370fa63cae12eda129ff5553c33a7086dfcb87c2`
