# D26 bounded production pulse — result (2026-07-20)

## Verdict

**Reject the frozen fixed production-pulse family.**  None of the three predeclared turn-75
`ownership2` pulses passes discovery, so prospective seeds 51,000--51,059 remain unopened.  No
candidate was built, no submission was made, and no Arena action occurred.

The failure is informative rather than marginal.  A 25-turn or 50-turn farm phase loses terminal
margin with a confidence interval wholly below zero.  Extending the farm phase through turn 149
recovers own production and improves the resident's existing catastrophic cells, but its overall
mean is only +0.960, its interval crosses zero, only four opponent families are nonnegative, and
negative-margin mass rises 8.90%.

## Integrity

- The release runner compiles and all seven focused tests pass.  Four warnings remain in unrelated
  pre-existing library strategies.
- Smoke produced 320/320 rows twice; the TSVs are byte-identical.
- Every smoke and discovery branch reached the turn-75 boundary and changed the resident command
  stream.  All three activation rates are 100%.
- Roots agree across branches, every phase/exit label is consistent, and terminal row shape is
  legal.
- All 80 smoke resident controls and all 1,920 discovery resident controls exactly match the
  corresponding D24 resident continuation, including root state, terminal state, and command
  hash.
- Discovery produced the complete 7,680-row matrix: 120 map seeds, both seats, eight structural
  opponents, one control, and three pulses.  It completed in 113.612 seconds with 24 workers.

## Frozen discovery result

| Farm interval | Seed margin | 95% interval | Own score | Opponent score | Nonnegative opponents | Worst opponent | Catastrophes | Negative mass | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 75--99 | -9.980 | [-12.973, -6.986] | +1.859 | +11.839 | 0/8 | -19.517 | 17.03% vs 15.00% | 1.162x | reject |
| 75--124 | -7.077 | [-10.715, -3.438] | +13.432 | +20.509 | 2/8 | -23.529 | 17.66% vs 15.00% | 1.155x | reject |
| 75--149 | +0.960 | [-3.919, +5.839] | +28.334 | +27.374 | 4/8 | -17.821 | 16.51% vs 15.00% | 1.089x | reject |

All confidence intervals use the 120 independent map-seed means after averaging the correlated
seat/opponent cells.  The 5%-trimmed means are -8.633, -6.055, and +1.585 respectively.  The
turn-150 pulse passes only the own-score and control-catastrophe gates; it fails the mean,
trimmed-mean, confidence, opponent breadth, worst-opponent, catastrophe-frequency, and
negative-mass gates.

At turn 150, opponent means are -17.821 adaptive Gold, -6.592 Compact Gold, -6.592 fixed Gold,
-0.150 Script, +4.237 MyBot, +8.233 Scheduler, +9.875 Silver, and +16.488 Printer.  The problem is
therefore concentrated in productive/self-compounding opponents but is not an opponent-identity
artifact.

## Mechanism analysis

### This is a scheduling change, not a worker-count change

Every branch stays at exactly two workers.  `ownership2` issues no `TRAIN` command in any pulse;
its mean `PLANT` counts are 4.41, 7.84, and 11.36 as duration increases.  This confirms D24's
finding that the complementary value comes from coherent renewable-supply scheduling, not from
adding late workers.

### Production arrives before margin

The 50-turn pulse already adds +13.43 own score, yet it loses -7.08 margin because the opponent
adds +20.51.  At 75 farm turns, own and opponent score gains nearly cancel (+28.33 versus +27.37).
The intervention creates renewable stock earlier than it creates exclusive value.  Simply
returning control to the resident does not undo the opponent compounding enabled during the farm
phase.

### The tail is transferred, not removed

The longest pulse improves the 288 resident-catastrophic cells by +10.56 margin on average, but it
raises catastrophic frequency from 15.00% to 16.51% and total negative-margin mass by 8.90%.
Thus it repairs part of the resident's old failure set while creating a different one against
productive opponents.  This is the same production/suppression frontier found by D24, now shown
to persist after a deterministic return to the resident.

### Phase handoff itself remains unresolved

All reached branches execute both phases, with exactly 25, 50, or 75 farm turns.  The restarted
resident is deliberately cold so it cannot remember commands that were never executed.  D26
therefore proves that a clean visible-state restart is insufficient; it does not yet distinguish
irreversible map-state damage from loss of useful resident history at re-entry.

## Consequence and next diagnostic

Close fixed-duration pulses: do not extend the cutoff grid or try another duration on prospective
data.  The next useful step is a read-only **return-value decomposition** on the already-consumed
common roots.  Compare each turn-150 pulse terminal with the corresponding permanent D24 farm
continuation and resident control.  This will quantify separately:

1. value accumulated by the farm before turn 150;
2. value won or lost by returning to a cold resident after turn 150; and
3. how those terms change by opponent family and resident-tail regime.

If staying with the farm dominates returning specifically after the shared turn-150 state, the
next architecture needs a handoff-aware resident state reconstruction or a terminal liquidation
controller.  If both continuations are similarly unsafe, the map-state externality is already
irreversible and the project should move upstream to private planting geometry rather than
controller re-entry.

## Evidence and hashes

- protocol: `d26-bounded-production-pulse-protocol-2026-07-20.md`;
- runner: `rust/src/bin/d26_policy_pulse.rs`;
- analyzer: `cgauto/d26_policy_pulse_analysis.py`;
- smoke TSV, repeat TSV, and JSON;
- discovery TSV and JSON.

Frozen artifact SHA-256 values:

- protocol: `867b92445c2093f7ee1f0ffe56c2add7013f0ee2b4792d62a3c39ac7c601daf2`;
- runner used for discovery: `0e69a6bd000159ef63938f72b7fc2f6a243821e4935eab9ba08bb744ef215af7`;
- current runner: `a749fd92f15debe9f957909f33b7e89305d3bb297dd0830c49cfee30b67d941b`
  after changing only its leading documentation comment from inner to outer form for D28 module
  reuse; the 320-row smoke output remains byte-identical;
- analyzer: `8a6592d8f173d963351fffec9fd05e12c5f7979b6ba3f98cc1139f68672af57e`;
- discovery TSV: `0714076c2b3327cb024d2ea92af9ab24a1f184049fabec27635ac1d378b6d93b`;
- discovery JSON: `15706aeed3ce92ebd9fc486de58d2e8467a3460c0162c01ad17087914abba158`.
