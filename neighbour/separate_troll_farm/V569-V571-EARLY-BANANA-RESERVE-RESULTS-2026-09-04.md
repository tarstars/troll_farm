# V569--V571 champion-prefix early banana wood reserve

## Verdict

None of the three reserve caps qualifies. After the final turn-45 start repair, V569 scored
-2.75/-5.21/-6.08 and V570 scored -5.38/-2.00/+6.88 against exact V468 at turns 100, 200, and
final. V571 scored -5.75/-2.38/+5.38. Every arm failed both nonnegative checkpoint conditions and
the required `+40` final gain on the 24-game behavior smoke. The most favorable earlier policy,
immediate cap three, reached +22.63 final but was still negative at turn 100.

The experiment exposed a roster-level limit rather than a cap-tuning opportunity. V468's second
worker has carry capacity two on every smoke row. A mature size-four banana contains four wood,
but this feller can bank at most two wood from it. Meanwhile the carry-one planter must plant,
later return to harvest a fruit, and bank it before the feller can act. That extra work
replaced chops, increased movement, reduced banked wood, and raised opponent score. No arm was
credible enough to open the preregistered 192-game panel, fresh maps, duels, packaging, or platform
publication. `bot.rs`, `submission.rs`, and the live V543 agent remain unchanged.

## Isolated design

V569--V571 regenerate exact V468 as the inner controller and add one common overlay. They differ
only in the hard live-plot cap of one, two, or three:

1. Inner commands remain byte-exact until the next observed state contains V468's own second
   troll; the handoff is state-based, not tied to a guessed training turn.
2. The overlay never trains and acts only while exactly two own workers are alive.
3. A plot is a reachable non-door, non-iron own-half cell within two steps of an own door. Plots
   use bananas exclusively and begin no earlier than turn 45.
4. The original harvest-capable worker plants the seed and harvests one ripe fruit. Carried cargo
   and an active V468 apple cycle retain priority.
5. The higher-id axe continues V468's work until no initial wild tree remains within four steps,
   then fells the mature reserve and banks its wood.
6. Protected reserve plants remain in the cloned inner view but have health and fruits masked, so
   V468 cannot select them while the overlay owns their lifecycle.

Focused tests were written before implementation and cover the observed prefix, permanent
two-worker roster, plot geometry, lifecycle, distinct roles, apple/cargo priority, inner-view
masking, cap-only normalization, and all three emitted candidates. Readable, compact, and paired
runner forms compile. The compact sources are each 99,670 UTF-16 units, and all 120 repository
tests pass.

## Repair path

Each behavior smoke uses seed 9941000, both seats, and all 12 frozen opponent families: 24 paired
games. It is diagnostic evidence, not a substitute for the promotion panel.

| policy | arm | turn 100 | turn 200 | final | W/T/L |
|---|---|---:|---:|---:|---:|
| raw reserve visible to V468 | V569 cap 1 | -27.6 | -44.3 | -42.0 | 11/0/13 |
| raw reserve visible to V468 | V570 cap 2 | -43.7 | -78.3 | -74.8 | 5/0/19 |
| raw reserve visible to V468 | V571 cap 3 | -37.6 | -74.7 | -75.0 | 5/0/19 |
| masked inner view, empty-tree harvest | V569 cap 1 | -4.7 | +8.3 | +25.1 | 20/1/3 |
| masked, one-fruit harvest, immediate start | V569 cap 1 | -6.0 | +3.0 | +12.1 | 20/1/3 |
| masked, one-fruit harvest, immediate start | V570 cap 2 | -8.3 | -1.3 | +9.4 | 20/0/4 |
| masked, one-fruit harvest, immediate start | V571 cap 3 | -8.0 | +6.5 | +22.6 | 19/1/4 |

The raw controller repeatedly targeted a reserve tree that the overlay was protecting, producing
blocked movement and oscillation. Masking protected health and fruit in the inner view removed
that ownership conflict without deleting the tree from state. The next repair ended harvesting
after one confirmed fruit: a carry-one planter could never empty a three-fruit mature banana
because the tree regenerated while it made its bank trip. Finally, turn 45 gives the banana's
roughly 24-turn growth/fruit window time to finish before V468's typical nearby-wild handoff around
turn 75. This improved policy timing, but did not change the underlying capacity cost.

## Final turn-45 smoke

| checkpoint | V468 | V569 cap 1 | delta | V570 cap 2 | delta | V571 cap 3 | delta |
|---|---:|---:|---:|---:|---:|---:|---:|
| turn 100 | 94.67 | 91.92 | -2.75 | 89.29 | -5.38 | 88.92 | -5.75 |
| turn 200 | 160.67 | 155.46 | -5.21 | 158.67 | -2.00 | 158.29 | -2.38 |
| final | 215.46 | 209.38 | -6.08 | 222.33 | +6.88 | 220.83 | +5.38 |

V468 went 19/1/4. V569 went 18/0/6, while V570 and V571 each went 17/0/7. Opponent final score
rose by 25.63, 21.58, and 21.50 respectively. The first changed command was between turns 45 and
122 because active apple cycles can defer reserve work. Every arm retained V468's turn-six
`3/2/0/2` train and finished with exactly two workers on all 24 rows.

The gate stops here by design. A candidate must be nonnegative at turns 100 and 200 and gain at
least 40 final own points before the 192-game panel is allowed. No V569--V571 arm satisfies even
the checkpoint half of that condition.

## Work and capacity mechanism

The final per-game action profile makes the regression concrete:

| arm | moves | chops | drops | harvests | plants | picks | waits | wood |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| V468 | 275.67 | 182.79 | 38.71 | 2.00 | 13.38 | 13.38 | 11.00 | 53.21 |
| V569 | 310.67 | 146.29 | 47.96 | 17.42 | 11.96 | 11.92 | 5.04 | 47.54 |
| V570 | 310.04 | 128.62 | 60.33 | 30.29 | 12.83 | 12.79 | 4.92 | 47.83 |
| V571 | 312.00 | 128.17 | 59.54 | 29.79 | 12.67 | 12.62 | 5.54 | 47.50 |

Even cap one added 35 moves and removed 36.5 chops per game. Larger caps doubled reserve
harvesting but did not increase wood: each still finished around 47.5 versus V468's 53.2. The
reserve converts a banked banana and two established workers' time into only the feller's
carry-limited wood pickup, while also releasing the opponent from pressure. The locally attractive
six-health tree does not create extra labor or carry capacity.

The final candidates recorded only noncritical `move_blocked` issues: V569 had 231 events across
16 rows, V570 199 across 23, and V571 197 across 23. There were no critical or unclassified
issues. Candidate planning p95/max remained small at 0.516/1.707 ms, 0.860/2.162 ms, and
0.863/2.118 ms. Legality and latency therefore do not explain or rescue the score failure.

## Consequence

Early timing does not rescue a banana battery on V468's fixed two-worker roster. V557--V562 began
too late; V569--V571 prove that a grown reserve waiting near the wild-wood handoff still consumes
more established-role work than its carry-two feller can monetize. More cap or start-turn tuning
is not a credible route to the 40-point requirement.

The important untested bridge is now narrower. V543/V564 modify the opening before the champion's
own second hire and lose the checkpoint curve; V552--V554 keep V468 until turns 80--120, when the
dense worker bill is already unavailable and role reconstruction takes another 80--130 turns.
The next experiment will keep exact V468 only until its second worker is observed, then initialize
the locally proven V564 capacity-three scaling policy from that live roster without retraining the
second worker. Role selection must be capability-aware because the observed second-worker
specification can vary outside this smoke. This tests the missing handoff interval rather than
another orchard refinement.

## Reproduction and integrity

- builder/test: `build_v569_early_banana_reserve.py` /
  `test_build_v569_early_banana_reserve.py`
- archived paired runners and every intermediate/final smoke:
  `/data/separate_troll_farm-working/archive/2026-09-04-v569-v571-early-reserve/`
- final V569 panel/gate/diagnostics SHA-256: `78833227371a0aa81f8c56ce29d67ade851d93604059bddd8abac682021efe2c` /
  `a686d755e21e66c90e806dcf5cba553048afae74e7f9275123fe3fd19c09160e` /
  `ff79c1314cb57d9a106aeca2aca2ef75d7da03d9f266be890051210ce9ea69e4`
- final V570 panel/gate/diagnostics SHA-256: `e95632d5795d1cdc7cb37cbf1aeaf855e395a89b78cc1aab8a5768b2a6a56454` /
  `9bb0af799a53e9378c8e82388c909516b2cea569c4fe82b5ab9cf12f96bbf2f6` /
  `d06e195e8be7481472b1319580e283e2dbd5e077d545d1ab37304cc8b04c5fd4`
- final V571 panel/gate/diagnostics SHA-256: `84147082014b20244f1e011653cb9b4ecddbfa41f4a6abc0a39c8e839535aa94` /
  `d5e825948dd628fd14380f90b59c7951af051a9ca65758932c8ccf0af4edd7c6` /
  `41fdcbaf84886f81c621b2e70dd659d7b5d851567f7f1be50846e0ddf8c4708e`
- V569/V570/V571 module SHA-256: `342cff6690b2757d30331104d6ceb0cce4f65a193edbec915c9bb07c8b09a542` /
  `e8d1186a96b85aec20f0d75476439e067e041ba1ca3e0fb2180c9e6ec7c007d7` /
  `aa122829ecab39dc9805dcfeee49531a201cf4faf9513abde8833f826b889c62`
- V569/V570/V571 compact SHA-256: `0584e92ea45a7c31b27201627d663196f8f1c15d820cfc99fa23493bc8d47963` /
  `7496cba48135096c4b6c694a14992c3966fb8cef8f3f88369df87a3ee362cb5b` /
  `9a9b2ba208dfcde8cb12d75e5c685046bc94a6bda3c432a65fb6337e05e7792c`
- V569/V570/V571 paired-runner SHA-256: `e55bfe03b0cb8a02e0a7b819374d253f55b55a4e2a2e8361339168ded5c7dea4` /
  `87ce31bfa6bfac9036ba5f50f7b19b9714bd8f726588a8068b1ca8cd2dd08f7b` /
  `b91a6a1305a0711fbc1bd87a5f624ca9e069f75824ce14c0aaffa73202d6685c`
- builder/test SHA-256: `9dae559f35e0b8f96a53fe45e6f8d6aea5f22fc5456502b30b6f9ce74e68fdea` /
  `84fdbabf547810dc53d2bc92b89825860fdf7df770d310b831c511803fe6e99c`
- read-only neighbor evidence commit: `370fa63cae12eda129ff5553c33a7086dfcb87c2`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
