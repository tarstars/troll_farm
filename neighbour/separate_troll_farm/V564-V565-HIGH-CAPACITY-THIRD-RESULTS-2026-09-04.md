# V564--V565 high-capacity third-worker experiment

## Verdict

V564 proves that a capacity-three third worker is a real late-game accelerator inside the dense
economy. Against the archived exact V546 rows it gained 40.24 final own score, 10.21 wood, and
32.31 margin per game, improved every opponent family, and completed worker four in nine more
games. It is nevertheless not a promotable bot: against the frozen V468 baseline it lost 68.75
points at turn 100 and 27.80 at turn 200. V565's elite `3/4/2/3` third worker delayed the economy
too far and was worse than V546 at turn 200 and at the finish.

The experiment isolates a useful component but also closes the dense line as a complete opening.
Even a hindsight whole-game selector between V468 and V564 can gain at most 0.44 final points while
keeping aggregate turn-100 and turn-200 deltas nonnegative. Neither candidate entered fresh maps,
duels, packaging, or the platform. `bot.rs`, `submission.rs`, and the live V543 agent remain
unchanged.

## Isolation and validation

Both candidates are regenerated from exact V468 through the same deterministic V546 dense-source
builder. The only semantic difference from V546 is the worker-three specification:

| candidate | third-worker specification | compact UTF-16 units |
|---|---|---:|
| V564 | `2/3/1/2` | 99,828 |
| V565 | `3/4/2/3` | 99,828 |

The first and fourth hires, ten-tree cap, crop ordering, routing, adaptive selector, denial,
rescue, and all other controller source normalize byte-identically to V546. Focused tests lock the
single-literal change. Readable and compact forms compiled independently; the complete repository
suite passes, 102 tests total.

The frozen development panel contains eight seeds, both seats, and the same 12 opponent families,
192 games per candidate. Exact V468 is the absolute baseline. The archived V546 panel uses the
same rows and supplies the causal parent comparison.

## Absolute V468 gate

| candidate | turn 100 delta | turn 200 delta | final delta | candidate W/T/L | verdict |
|---|---:|---:|---:|---:|---|
| V564 | -68.75 | -27.80 | +171.47 | 174/1/17 | FAIL |
| V565 | -58.81 | -98.24 | +98.38 | 162/0/30 | FAIL |

V468 scored 93.01, 176.18, and 247.25 at the three checkpoints and went 177/3/12. V564 scored
24.26, 148.39, and 418.72; V565 scored 34.20, 77.94, and 345.62. Although both clear the final
+40 requirement, neither preserves either early checkpoint. Opponents also gained 60.17 points
against V564 and 62.96 against V565, and both candidates worsened the outcome count.

## V564 mechanism

V564 is materially better than exact V546 on identical games:

| measure | V546 | V564 | delta |
|---|---:|---:|---:|
| turn-100 own score | 20.11 | 24.26 | +4.15 |
| turn-200 own score | 142.91 | 148.39 | +5.47 |
| final own score | 378.48 | 418.72 | +40.24 |
| final opponent score | 160.46 | 168.39 | +7.93 |
| final margin | 218.02 | 250.33 | +32.31 |
| wood | 84.89 | 95.10 | +10.21 |
| W/T/L | 166/1/25 | 174/1/17 | +8 wins, -8 losses |

The stronger worker-three bill costs five additional lemons. It delayed the third hire from mean
turn 78.90 to 93.58, but its capacity then shortened the path to worker four. V546 finished with
four workers in 166 games, three in ten, and two in sixteen; V564 finished with four in 175, three
in one, and two in sixteen. Its fourth hires had mean turn 239.81 versus 245.52 for V546 despite
including nine additional, harder completions.

Relative to V546, V564 added 2.03 ring harvests, 2.70 ring chops, 4.93 drops, and 10.21 banked wood
per game. All 12 opponent families had positive own-score deltas, from +4.44 against resident to
+55.62 against legend balanced. The full runner recorded 164 noncritical `move_blocked` issues,
against 50 plus one opponent-plant blockage for V546, but the result is not an issue artifact:
the 168 zero-issue rows still gained 40.64 own score and 34.10 margin, while the 24 issue rows
gained 37.42 and 19.75. There were no critical or unclassified issues. Candidate planning latency
was 0.98 ms at p95 and 3.97 ms maximum.

## V565 comparison

V565's larger bill pushed the third hire to mean turn 158.25 and the fourth to 290.99. Against
V546 it was +14.08 at turn 100, -64.97 at turn 200, and -32.85 at the finish, with 5.29 less wood
and 43.58 less margin. It completed four workers in 167 games, only one more than V546. Eleven of
12 family deltas were negative; resident alone gained 9.75. The elite specification works in an
elite opponent's whole policy, but its cost is not supportable by this controller.

## Selector bound and consequence

Only one V564 row individually met all three absolute conditions: seed 9941001, seat 1, resident,
with deltas +6, +12, and +68. Across all 192 rows, only three had turn-100 cost no worse than six.
An exhaustive whole-row selection under aggregate turn-100 and turn-200 deltas of at least zero
chooses that row plus seed 9941001, seat 0, resident (-6, -11, +16). Their totals are 0, +1, and
+84, only +0.4375 final points per panel game. Every remaining candidate row costs more than the
available turn-100 surplus. Thus no oracle selector between the dense candidate and V468 can come
close to the required +40.

V564 supplies the best measured dense late phase so far, but it cannot be the opening. The next
experiment will preserve a dedicated axe during the two-worker bill phase: only the original
producer establishes the minimal plum/lemon/apple sources, the higher-id worker continues normal
chopping, and the policy transitions to V564 after buying the capacity-three third worker. This
tests whether V564's measured late repayment can coexist with enough of V468's early income.

## Reproduction and integrity

- builder/test: `build_v564_high_capacity_third.py` /
  `test_build_v564_high_capacity_third.py`
- canonical and archived artifacts:
  `/data/separate_troll_farm-working/archive/2026-09-04-v564-v565/`
- V564 panel/gate/diagnostics SHA-256: `b3d3b180599ded0c35e844d97c7104a07f27197d884a965036296a7a9ec9c9b9` /
  `12e92426adc954157ebdd6ff39d09a08ff7eaedc22c5f06969feb23e253767bd` /
  `90c00e82250029007891fedd7f3e7ce7a6fa9be23d5f22a4be1116c1ec415fd0`
- V565 panel/gate/diagnostics SHA-256: `c6aa3247bb79e566b51e840c53ea2feefc9dbf87ee61032310463d82ba9b0eb0` /
  `47cd61d7be4e9c7f2e2ab7d257e6ad39ea45cb31703fa216d07b3b486b61cdf1` /
  `1dc8abdb231b588697f6d956d56524e7662ae7375da08a0b3a7644853eb260ca`
- V564/V565 compact SHA-256: `b4c4c116a1a406e8f2b588e5ec2b2607814e1b56a28026e560dd8a83a324a2e9` /
  `8c7bdeba5b91064f47ec34e13fff738c3b90dfaf7806660bbd695dc355539b42`
- builder/test SHA-256: `b4f304a0f24156dfb549f3255caf3aa18e48a4731fdde4d781abb13e825e397f` /
  `c1e00cdf035847f204bd1b6e6f3bc47c82970b9b57e003956dc21a0b0ec23be6`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
