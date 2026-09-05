# Port post-mortem — the #2 design was not what we tested

**Agent:** `chatgpt_2`  
**Task:** `20260905-port-postmortem`  
**Date:** 2026-09-05  
**Verdict:** `PORT_SPECIFIC_HYBRID_FAILURE`  
**Outcome from the task's three-way fork:** **3 — the port broke the design in an identifiable way.**

## Answer

There is a large design here. The native `norxondor_gorgonax` program is not merely a 29.66 label attached to ordinary play: its 218 recorded games show a closed-loop economy that is mechanically unlike ours and much stronger. Our port did **not** test that economy. It copied the visible training ladder and Produce→Deforest story, grafted them onto our champion's unrecovered targeting and assignment layer, and added a seven-living-tree cap, a single planting job, an exclusive two-state switch, and no harvesting in D. Those substitutions severed the native orchard-turnover loop.

The reconstruction remains useful as a behavioural description. It is **not** a sufficient executable specification: the transitional `T` state, the second global flag, plant admission and replacement, crop choice, chop/harvest target selection, and tie-breaks were explicitly unresolved. The port silently assumed those missing layers were interchangeable with ours. The evidence says that assumption was false.

## Is the native design really stronger?

Raw package scores cannot answer this alone. The native bot faced opponents rated **25.50** on average; the two champion packages faced **17.51**. Native final margin was **+73.99** over 218 games and champion margin **−19.57** over 320; their raw difference is **+93.56 [72.33, 114.29]**, but it is confounded by different opponents, maps, draws, dates, and submissions.

There is almost no non-parametric common support: only **4/320** champion games faced an opponent rated at least 20, while **209/218** native games faced one rated at least 22; no opponent name appears often enough in both sets for a matched estimate. I therefore do not present a fake reweighted score.

Three controls all point the same way:

1. The directly observed platform ratings are **29.66** for the native bot and **18.43** on average for the two champion readings: a **+11.23 rating-point** gap. The stored record has no interval for that difference.
2. In the only broad shared slice, opponents below 22, native has just 9 games but still faced the stronger field (20.48 versus 17.44) and leads champion margin by **+156.57 [102.73, 207.97]**. This is a stress check, not a primary estimate.
3. A sensitivity model fitted within bot and seat on **1,108** games from four other profiles plus the two champion readings estimates that one extra opponent-rating point lowers margin by **7.41 [3.71, 11.17]** points. Transporting both cohorts to the midpoint field makes the native-minus-champion margin gap **+152.80 [131.60, 173.59]**. This is extrapolation, not a causal estimate, but stronger opposition cannot explain the native advantage; correcting for it enlarges the gap.

So the dead condition does not fire. The platform record shows an **11.23-rating-point native advantage** over these champion readings, and every score sensitivity points in the same direction. What is not established is a transferable score gain of any particular size, or that the strength can be copied as independent modules.

## What the port actually implemented

| Layer | What happened |
|---|---|
| Reconstructed from the native bot | training floor/cap ladder and talents; near-shack orchard idea; Produce/Deforest macro; fruit and iron funding priorities; banana conversion |
| Retained from our champion | parser and game state; movement resolver; joint assignment; banking; harvest targets; **chop targets**; low-level candidate execution |
| Invented for the port | one exclusive P/D switch; seven living orchard trees; one global plant job; no harvest in D; deterministic choices for unresolved rules |

The design decision was therefore: *native macro-economy is composable with champion micro-control*. That is exactly the component boundary the reconstruction had not validated.

## Fruit first was not the bug

The old loss read correctly observed that the port banked fruit while champion banked four-point wood. It incorrectly treated that contrast as proof that the switch happened about 100 turns too late.

The real bot does the same early investment. Its first wood arrives around turn **97**. At turn 100, both the real bot and port have **6.60 wood points**. Port v2 switches at median turn **144**, while the real first `D` flag appears at median turn **153**. Moving the port switch all the way to about turn 75 in v3 still left a **−59.62** direct margin. Switch timing was a symptom, not the missing mechanism.

The paths separate in turns **100–200**:

| turn | real score / wood points / cumulative plants | port score / wood points / cumulative plants |
|---:|---:|---:|
| 100 | 31.86 / 6.60 / 9.44 | 25.76 / 6.60 / 4.01 |
| 150 | 78.70 / 49.32 / 15.13 | 45.96 / 26.05 / 7.34 |
| 200 | 185.43 / 154.72 / 21.53 | 78.80 / 61.65 / 10.34 |
| end | 366.10 / 334.16 / 31.89 | 114.48 / 99.95 / 13.01 |

The real trajectory is the published 616-game series and the port trajectory is its 400-game closed-loop panel, so the absolute gap is descriptive rather than paired. The mechanism is nevertheless concrete and is reproduced by command counts. In turns 101–150, real play averages **24.35 HARVEST, 21.29 CHOP, 5.28 PLANT** commands per game; port averages **9.21, 17.88, 3.38**. In turns 151–200, real play averages **13.94 HARVEST, 55.16 CHOP, 5.80 PLANT**; port **0.16, 28.73, 3.01**.

The port even buys its third troll earlier—median turn **74**, versus **100.5** natively—yet has roughly half the planted-tree throughput and half the midgame chopping. The failure is not lack of roster urgency. It is loss of the forest-and-work loop that makes the roster productive.

## The identifiable break

The native program does not have one clean P→D edge. It has two asynchronous P/T/D flags. `T` is observed thinning its own mature orchard; the second flag's meaning is unknown; harvesting continues while chopping rises. Around the native D switch there are only about **seven own planted trees alive**, but the bot has already planted about **fifteen cumulatively**. Seven is a snapshot of a renewing forest, not a lifetime production cap.

The port turned that snapshot into a hard living-tree cap and allowed one global planting job, while its inherited champion chop targets had no model of native orchard thinning or slot recycling. Once the cap filled, the port did not turn over the orchard fast enough to plant the next cohort. It then disabled harvest in D. Thus it had fewer fruit deliveries, an early under-supported third troll, too few trees, and too few chop jobs. Changing the switch scalar could not repair that closed-loop state.

## Recommendation

**Reopen one line, but do not patch v3.** Charter a standalone **native orchard-turnover controller** before any graft onto the champion.

The specific repair is to recover and implement together:

- the `T`/second-flag behaviour that permits mixed harvesting, own-orchard thinning, and chopping;
- planting admission and replacement, so about seven living trees can turn over into roughly 15 cumulative plants by turn 150 and 21 by turn 200;
- native crop and chop target selection, rather than champion targeting;
- the native train timing as an output of that economy, not an independently forced schedule.

Closed-loop development checkpoints should include third TRAIN near turn 100, first D near 153, about 49 wood points and 15 cumulative plants by turn 150, about 155 wood points and 22 plants by turn 200, and continued harvest activity through turns 151–200. Per-decision agreement is not a gate. Only after those state trajectories reproduce should the standalone controller face the unchanged champion on fresh holdout maps.

If that controller cannot reproduce the checkpoints, Track R's documents should remain descriptive only and top-bot copying as an implementation strategy should close. The present evidence, however, supports a focused reopening: **the native design is strong; our hybrid never implemented it.**

## Reproduction

`analyse.py` reconstructs two independent 160-game champion readings and combines them with the committed 218-game native profile, 616-game public time series, and the port's 400-game loss read. `calibrate.py` performs the opponent-support diagnostics and sensitivities. GitHub Actions run `33950166405`, job `101263309543`, completed successfully at source commit `599788b113a0dba80d0678d7d537fe8ccdad93fa`; artifact `9964561803`, ZIP SHA-256 `ec1545b0ffde5b8335fdfc6b2deb475452fef58e0d6c78de659acc41f07c1bae`. This is author reproduction, not independent coordinator acceptance. No bot, build, ladder, platform, board, task card, or `main` state was changed.
