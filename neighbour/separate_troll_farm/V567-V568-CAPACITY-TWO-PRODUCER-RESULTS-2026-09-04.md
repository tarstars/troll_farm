# V567--V568 capacity-two producer and ripe-first source collection

## Verdict

Neither candidate qualifies. V567 proves that putting the trained movement-two/carry-two worker
on the bill and the original worker on the axe restores much of V566's late scaling: final own
score rose 27.87 versus V566 and cleared the absolute `+40` final-score requirement against V468.
It paid for that result with an even weaker opening, however. Against exact V468 it was -52.37 at
turn 100, -91.06 at turn 200, and +43.18 final, while losses rose from 12 to 43. V568's ripe-first
source collection recovered 11.10 points at turn 200 relative to V567 but finished 6.07 lower and
raised losses to 57. It failed the final requirement as well as both checkpoints.

This closes the dense third-worker allocation line. V564--V568 can trade opening score for late
workers, but none can preserve V468's checkpoint curve. No fresh panel, duels, packaging, or
platform publication were opened. `bot.rs`, `submission.rs`, and the live V543 agent remain
unchanged.

## Isolated changes

V567 regenerates exact V566 and changes only the two-worker roles:

1. The original movement-one/carry-one worker becomes the dedicated axe.
2. The trained movement-two/carry-two worker becomes the sole producer.
3. The one-worker role remains producer, and at three workers the exact V564/V566 two-producer and
   one-hybrid map is restored.

V568 adds one ordering change. When a required source is short, it first harvests reachable ripe
fruit of that kind, then spends a banked seed if no ripe fruit is available. The original unripe
fruit fallback remains after that block. The training ladder, `2/3/1/2` third worker, `2/4/0/3`
fourth worker, ten-tree cap, bill ordering, iron path, chop selector, adaptive guard, and wrappers
are unchanged.

The focused tests were written before implementation and normalize each changed block back to its
parent. Readable, compact, and paired-runner forms compiled independently. The compact sources are
99,910 and 99,911 UTF-16 units. All 111 repository tests pass.

## Frozen V468 gate

Each arm used the frozen eight seeds, both seats, and 12 opponent families: 192 paired games.

| checkpoint | V468 | V567 | delta | V568 | delta |
|---|---:|---:|---:|---:|---:|
| turn 100 | 93.01 | 40.64 | -52.37 | 37.94 | -55.07 |
| turn 200 | 176.18 | 85.12 | -91.06 | 96.22 | -79.96 |
| final | 247.25 | 290.43 | +43.18 | 284.36 | +37.11 |

V468 went 177/3/12. V567 went 147/2/43 and let opponents score 48.53 more points; V568 went
135/0/57 and let opponents score 50.47 more. V567 met only the final-score requirement. V568 met
none of the three conditions. Both were weakest against the two locally strongest families:
V567 was -21.31 against `mybot` and -39.06 against `resident`; V568 was -27.44 and -31.31.

The one-map smokes were not used as promotion evidence. They suggested large late gains, but the
full panel exposed the checkpoint and outcome regressions, again validating the fixed gate.

## What the role swap changed

All panels below share the same 192 map-seats and exact V468 baseline.

| measure | V564 | V566 | V567 | V568 |
|---|---:|---:|---:|---:|
| turn-100 own score | 24.26 | 68.40 | 40.64 | 37.94 |
| turn-200 own score | 148.39 | 116.24 | 85.12 | 96.22 |
| final own score | 418.72 | 262.56 | 290.43 | 284.36 |
| final opponent score | 168.39 | 140.70 | 156.74 | 158.69 |
| wood | 95.10 | 60.45 | 66.41 | 64.77 |
| final workers | 3.83 | 3.56 | 3.73 | 3.61 |

Relative to V566, V567 was -27.76/-31.11/+27.87 across the checkpoints. It bought the
`2/3/1/2` third worker in 173 rather than 165 games and the fourth worker in 159 rather than 134.
Mean third-worker command time improved from 165.53 to 138.27 and mean fourth-worker time from
239.60 to 215.76. The higher-capacity producer therefore works as intended, but does not eliminate
the dense controller's source-establishment cost. It exchanged V566's early axe recovery for more
late completions and still remained 128.29 final points behind V564.

Through turn 100, V567 averaged 110.14 moves, 41.67 chops, 16.42 harvests, 18.39 drops, and 6.17
plants. Exact V468 averaged 80.51 moves, 51.18 chops, 21.62 harvests, 30.17 drops, and 0.92 plants.
The role swap thus retains a measured 29.63-move establishment tax while producing fewer of every
immediate scoring action. The checkpoint failure is the candidate economy, not a missing late
worker payoff.

## What ripe-first collection changed

Relative to V567, V568 was -2.70 at turn 100, +11.10 at turn 200, and -6.07 final. It completed
only 167 third workers and 143 fourth workers, versus 173 and 159. Through turn 100 it avoided
2.59 picks and 0.84 plants per game, but added 11.07 moves while losing 1.25 harvests and 1.12
chops. Selecting reachable natural fruit by kind still sent the producer on long trips; it did
not reproduce the compact source geometry inferred from the public elite trace.

The regression persists outside runner issue rows. On V568's 178 zero-issue rows, its delta from
V567 was -2.65/+11.85/-6.23 at the checkpoints. V567 recorded 17 noncritical `move_blocked`
events in 13 rows. V568 recorded 66 in 14 rows, including one 50-event jam, but no critical or
unclassified issue. Removing those rows does not rescue the candidate. Planning latency remained
small: V567/V568 p95 was 0.92/0.93 ms and maximum was 3.67/3.96 ms.

## Consequence

The completed V564--V568 sequence separates the tradeoff cleanly. Two producers can scale, one
axe can preserve more opening score, and a capacity-two producer can recover later workers, but
the bill-building controller cannot deliver all three simultaneously. Another role predicate or
fruit-source ordering is unlikely to bridge a 52--91 point checkpoint deficit.

The next experiment returns to the champion prefix and keeps its two-worker roster. The read-only
neighbor at commit `370fa63cae12eda129ff5553c33a7086dfcb87c2` supplies a distinct timing hypothesis:
after the champion's own second train, establish a small near-shack banana wood reserve while near
wild trees are still used, then fell the mature reserve only after nearby wild wood is exhausted.
This differs from V557--V562, which started reserve work after turn 100 and had no growing reserve
waiting at the handoff. Bananas yield the same four wood as other mature species but require only
six health, making the mechanism large enough to test without another irreversible roster change.

## Reproduction and integrity

- builder/test: `build_v567_capacity_two_producer.py` /
  `test_build_v567_capacity_two_producer.py`
- archived runners, build logs, smokes, panels, gates, and diagnostics:
  `/data/separate_troll_farm-working/archive/2026-09-04-v567-v568-producer/`
- V567 panel/gate/diagnostics SHA-256: `b76cda4304d2464e44eb5ef12d99d6832b46f0b1e731ad562d0898a9ecf5f590` /
  `1dd7e6f6f5290f77a0ef592037083440546d726a00270b15120649c5650e32a2` /
  `0667af6cc1424113dec2a36fc4e87447f65ff3d60c0462b87702e3a94b9239bf`
- V568 panel/gate/diagnostics SHA-256: `6ffe87c407101cff18c8ce695199432f3a6f890b4ba8fde421c0a543252c4bfd` /
  `de8aaa3a330a57d99df43ada2b72e009aba9a5b1ec619488549ec1f8f3ed0a0f` /
  `a3a118e736fbe33cd1aa04c2ea978a5b6447823184809b1cb4e93405f83e9f0f`
- V567/V568 module SHA-256: `ac8a1a7cb2fe61de6f7c160a3a4a27bed75ddb750f882ba05f11e5a3d850b67f` /
  `3fcc9f506738460c917224dc4e571ef2fab8c683391475de78a6f752a902d8e9`
- V567/V568 compact SHA-256: `dc8620b1ff510d864e7e92437b74fc3a20103cceca52fe91489f2f9c73bd0f60` /
  `b5b30d448c5df5ef1fb8c182be8b04a962db3dda3ce3c90f505deafc4a9c6c2d`
- builder/test SHA-256: `a80144402b36f7f8ae5b25d4865644955ccb4068a08fe408fc4c9d760233b0c1` /
  `9722ec6f1f9b337ab8627aa49c26dd2cf242124c80971549348b718f7dd6773c`
- production hashes retained: `bot.rs` `b8d2c4e298d7d748612b64b1a91c3d88826c467846f9544d0df1b86279588372`;
  `submission.rs` `922a233526ed590dafcc6302461de2dafef720fb003bd2359f55dfd93ac1b4a7`
