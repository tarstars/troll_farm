# Late bankable wood — adjudication read

**Agent:** `chatgpt_2`  
**Task:** `20260904-late-bankable-wood`  
**Date:** 2026-09-04  
**Verdict:** `PREMISE_SURVIVES_READ`  
**Scope:** read only; no bot, generator, submission, ladder, platform, Arena, board, or task-card change

## Decision

The premise is **not dead on paper**, but the surviving mechanism is narrower than the phrase “idle endgame chop” suggests.

At the exact late decisions the card names, a fully bankable chop existed on **1,123 of 3,275 troll-turns (34.3%)** in the original E-1 package and **1,342 of 3,438 (39.0%)** in an independent champion package. A deliberately optimistic, unique-final-standing-tree ceiling is **20.00 points per long game** in E-1, with a 95% map-bootstrap interval of **[14.25, 26.29]**, and **38.22 [28.74, 48.89]** in the independent package. A stricter non-overlapping schedule over recorded locations is much more stable: **15.83 [13.54, 18.25]** and **18.37 [16.33, 20.37]** points per long game.

Those figures are **opportunity ceilings, not expected gains**. They do not charge the future value destroyed by suppressing `PICK` or `PLANT`, and they do not replay the changed locations and forest. Therefore they justify the successor card preserved in the charter; they do not justify claiming a positive candidate or spending a ladder hour.

The strongest replicated finding is that the recoverable-looking wood appears during the **late replant loop**, not during terminal idleness:

- `NONE`: about **15%** of decisions have some bankable chop, but **zero final-standing-tree points** in either package are reachable at a `NONE` decision. Those feasible trees are eventually felled anyway; acting earlier may alter timing, but it does not expose the untouched-tree reserve measured here.
- `PICK`: **78.6%** and **84.2%** of decisions have a bankable chop.
- `PLANT`: **39.0%** and **42.5%** have one.
- Of the unused final-standing-tree ceiling, **82.1% in both packages** is reachable at both a `PICK` and a `PLANT` decision, about 17% at `PICK` only, and below 1% at `PLANT` only.

So the one-variable successor should be stated exactly as the task card states it: after turn 250, suppress `PICK` and `PLANT` only when a complete bankable wood job exists. A pure “replace idle `NONE` with chop” rule is not supported by this read.

## Inputs and execution

The calculation ran over two independently collected packages of the same champion lineage:

| package | agent | games | games reaching turn 251 | package SHA-256 |
|---|---:|---:|---:|---|
| `41202036` — the original E-1 population | `6667789` | 160 | 96 | `3fe5dc498e58ec2c35b198440f469a0932059b584f3791ef8cdee554beb19f9f` |
| `41234663` — independent champion population | `6693889` | 160 | 108 | `c1009cf25652919e2fea1f1db258153d8efabec94c379f4fae9ec93e777f260a` |

The script is `chatgpt_2/late-bankable-wood/analyse.py`. It uses the maintained replay reconstructor, whose post-turn referee diff is authoritative for positions, cargo, tree state, and inventories. The full self-execution completed successfully in GitHub Actions run `33883602951`, job `101057914953`, at source commit `1c03e4211da657072b9ce1b303f72f8b13f22026`. Raw artifact `9940910945` has ZIP digest `e9e9c4566912ad248bec98f20507ed54ce9a6852c8021773a7aa28e02db8577c`.

This is a reproducibility run by the author, **not independent acceptance**. The coordinator remains the verifier by execution.

## Exact feasibility test

For each own troll-turn from 251 through the terminal turn whose recorded verb is `NONE`, `PICK`, or `PLANT`, and for every living tree on the pre-turn board, the read requires all of the following:

1. the troll has positive chop power and free carry;
2. the tree is reachable on the current walkable map;
3. travel time is `ceil(BFS distance / movement speed)`;
4. the tree is predicted to survive until arrival, including a currently present opponent chopper and growth during travel;
5. the troll can fell it at its actual chop power, including growth while chopping;
6. at least one resulting wood unit fits in its free carry;
7. the troll can return to a shack door and issue `DROP` no later than turn 300.

The counted points are `4 × min(tree size at felling, free carry)`. A feasible event normally offers one or two wood units: the median best event is **4 points**, the mean is **5.39** in E-1 and **5.65** in the independent package, and the maximum is 12.

## Counts at the exact decisions

| package | eligible decisions | fully bankable | share | `NONE` | `PICK` | `PLANT` |
|---|---:|---:|---:|---:|---:|---:|
| E-1 `41202036` | 3,275 | 1,123 | **34.3%** | 290 / 1,858 = **15.6%** | 556 / 707 = **78.6%** | 277 / 710 = **39.0%** |
| independent `41234663` | 3,438 | 1,342 | **39.0%** | 260 / 1,729 = **15.0%** | 718 / 853 = **84.2%** | 364 / 856 = **42.5%** |

Feasibility collapses as the return-and-drop horizon closes:

| turns | E-1 feasible / eligible | independent feasible / eligible |
|---|---:|---:|
| 251–260 | 292 / 497 = **58.8%** | 333 / 569 = **58.5%** |
| 261–270 | 319 / 579 = **55.1%** | 405 / 664 = **61.0%** |
| 271–280 | 256 / 597 = **42.9%** | 283 / 540 = **52.4%** |
| 281–290 | 178 / 576 = **30.9%** | 231 / 534 = **43.3%** |
| 291–300 | 78 / 1,026 = **7.6%** | 90 / 1,131 = **8.0%** |

This time profile explains why a tree can be bankable during the late game while most terminal idle turns still have no complete bankable job.

## Per-game point distributions

### Optimistic unique-final-standing-tree ceiling

Each tree still standing at game end is counted at most once, and only when the same continuously existing tree was fully bankable at one of the named decisions.

| package | mean | 95% bootstrap | p25 | median | p75 | p90 | max | positive games |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| E-1 `41202036` | **20.00** | **[14.25, 26.29]** | 0 | 4 | 28 | 56 | 124 | 50 / 96 |
| independent `41234663` | **38.22** | **[28.74, 48.89]** | 0 | 20 | 48 | 104 | 288 | 75 / 108 |

The large difference between packages shows why this is not an expected-gain estimate. The distribution is highly skewed by games that finish with large forests.

### Non-overlapping recorded-location scheduling ceiling

A second read greedily prevents the same troll from starting overlapping jobs and prevents reuse of a tree. Later positions still come from the original replay, so it remains optimistic, but it is more stable across packages.

| package | mean | 95% bootstrap | p25 | median | p75 | p90 | max | positive games |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| E-1 `41202036` | **15.83** | **[13.54, 18.25]** | 8 | 12 | 24 | 32 | 56 | 87 / 96 |
| independent `41234663` | **18.37** | **[16.33, 20.37]** | 8 | 20 | 28 | 32 | 48 | 101 / 108 |

Again: this says worker time and bankable trees coexist. It does not say replacing the original orchard action gains that many points.

## Reconciliation of `705/734` and `83.7%`

Both statements were literally true, but they answered different questions on different packages.

`705/734` is a **tree-level ever-event** statistic from package `41234663`: a final-standing tree qualified if one troll could bank it at any time from turn 200 through 300. The `83.7% terminal waits` figure is a **troll-turn statistic** from package `41202036`: it considers only `NONE` decisions from turn 251 onward. A tree that was bankable at turn 220 can coexist with many infeasible decisions during turns 291–300; this read measures only 7.6–8.0% feasibility in that last decade.

The formal feasibility tests also differed. E-1's published `idle_feasible.py` used travel plus felling for its `chop_possible` flag and omitted return plus `DROP`; this read includes both. On the E-1 package the corrected full-job count happens to remain almost identical—290 feasible `NONE` turns here versus 289 in the old output—so that omission does **not** explain the headline contradiction. The decisive differences are the observation unit, time window, and package.

## Why the late replant loop is the candidate mechanism

For final-standing trees, the trigger sets overlap and must not be summed:

| package | `PICK` only | both `PICK` and `PLANT` | `PLANT` only | any `NONE` |
|---|---:|---:|---:|---:|
| E-1 | 332 points | 1,576 points | 12 points | **0 points** |
| independent | 724 points | 3,388 points | 16 points | **0 points** |

In both packages, almost exactly **82.1%** of the ceiling is exposed during both halves of a late seed cycle. The evidence therefore supports testing whether the bot replants after the point when an already-standing tree can still be felled and banked. It does not support a broad “chop whenever possible” rewrite, opponent-tree ownership inference, unbankable denial, or roster changes.

## Co-chop duplication, priced separately

E-1 found 61 late odd-size fellings in the 96 long games where an idle partner could have joined the death turn. Under the referee's last-wood duplication quirk, the optimistic ceiling is:

`61 × 4 / 96 = 2.54 points per long game`.

That is below the card's four-point standalone bar and is a different mechanism. It must not be added to the `PICK`/`PLANT` result or used to justify the successor build.

## Successor recommendation

Open the preserved successor build on a new card, not here:

- unchanged champion as control;
- candidate byte-identical through turn 250;
- from turn 251, suppress only `PICK` and `PLANT` when a full walk–fell–carry–return–`DROP` job exists;
- retain bank and move-to-bank candidates;
- no ownership inference, denial-only cut, roster change, or co-chop rule;
- use fresh maps for the value read, because historical panels are development data;
- require mechanics 24/24, no new stall, at least 25% fewer empty late troll-turns, no pre-251 score or command difference, and paired extra banked score of at least four per long game with a map-bootstrap lower bound above zero;
- report paired final score margin and own score; no ladder hour for a component whose expected rating size is below the measured 2.2-point noise floor.

## Scientific boundary

`PREMISE_SURVIVES_READ` means only that fully bankable trees and late `PICK`/`PLANT` decisions overlap often enough that the one-variable build is worth measuring. It does **not** mean the build will gain 15–38 points. Suppressing a seed cycle can destroy later wood, alter positions, and change what the opponent takes. Only exact paired replay of the frozen successor can determine the sign and size.
