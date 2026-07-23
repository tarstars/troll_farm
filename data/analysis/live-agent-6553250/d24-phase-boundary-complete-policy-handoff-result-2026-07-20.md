# D24 phase-boundary complete-policy handoff — result (2026-07-20)

## Verdict

**Reject unconditional complete-policy handoffs for the frozen option library.**

The turn-75 two-worker farm handoff is the first macro intervention in this cycle to show a large,
robust discovery gain and retain a positive mean on a sealed block.  It nevertheless fails the
predeclared confirmation gate: the seed-clustered interval crosses zero, only five of eight
opponent families remain nonnegative, worst-opponent mean is -8.88, and negative-margin mass rises
18.72%.

No candidate was built, no source was submitted, and no Arena activity occurred.  Confirmation
seeds 50,060--50,119 may not be reused to tune another D24 option or cutoff.

## Integrity and execution

The outcome-blind smoke produced 1,920/1,920 rows twice and the two TSV files were byte-identical.
Every root field agreed across branches; every option changed the control command stream in all
320 smoke scenario/cut cells.  The new Rust binary's seven focused tests pass, it compiles with
warnings denied at the binary boundary, and the analyzer compiles under the project virtual
environment.  Four pre-existing warnings remain in unrelated library strategies.

Fresh discovery used 60 maps, both seats, eight deterministic structural opponents, four phase
boundaries, the warmed resident, and five whole-policy options.  It completed the exact
23,040-row / 3,840-common-state matrix in 240.674 seconds with 24 worker threads.  Confirmation
completed 1,920 rows / 960 common states in 26.669 seconds.

## Discovery result

Only two of twenty option/turn combinations pass every frozen gate, both at turn 75:

| Complete option | Cut | Seed-clustered margin | 95% interval | Own score | Worst opponent | Catastrophe rate | Negative mass ratio | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| `private2` | 75 | +25.973 | [+7.609, +44.337] | +64.803 | +5.417 | 12.50% vs 17.19% control | 0.858 | pass |
| `ownership2` | 75 | **+28.325** | **[+10.327, +46.323]** | **+67.800** | **+8.192** | **12.40% vs 17.19%** | **0.846** | pass/selected |
| `hybrid3` | 75 | -53.800 | [-62.209, -45.391] | -37.456 | -63.058 | 24.38% | 1.676 | reject |
| `accumulate4` | 75 | -65.233 | [-74.265, -56.202] | -44.311 | -79.058 | 26.25% | 1.860 | reject |
| `norx3` | 75 | -43.663 | [-48.497, -38.828] | -39.219 | -48.850 | 20.94% | 1.451 | reject |

The predeclared lexicographic selection first maximized worst-opponent mean, so it froze
`ownership2` at turn 75 before the sealed block was opened.

The farm timing curve is decisive.  `ownership2` changes from +28.325 at turn 75 to +7.614 at
turn 100, -9.382 at turn 125, and -14.898 at turn 150.  Waiting for the visible score reversal is
too late: the production policy needs enough remaining horizon and must start before the
opponent's compounding transition is obvious.

## Prospective confirmation

The exact frozen `ownership2`/turn-75 branch retains useful production but fails the robustness
gate on four substantive fronts:

| Measure | Confirmation | Frozen requirement | Result |
|---|---:|---:|:---:|
| Seed-clustered mean margin | +14.894 | >= +5 | pass |
| 5%-trimmed margin | +15.862 | >= +2 | pass |
| Margin 95% interval | **[-3.183, +32.970]** | lower bound > 0 | **fail** |
| Own-score delta | +59.767 | >= +5 | pass |
| Nonnegative opponents | **5/8** | >= 6/8 | **fail** |
| Worst opponent | **-8.883** (`gold_adaptive`) | >= -5 | **fail** |
| Control-tail margin delta | +55.317 over 123 cells | > 0 | pass |
| Catastrophe rate | 12.71% vs 12.81% control | no increase | pass |
| Negative-margin mass | **1.187x control** | <= 1.0x | **fail** |

Opponent means are -8.883 adaptive Gold, -2.633 Compact Gold, -2.633 fixed Gold, +13.800 MyBot,
+45.808 Printer, +38.508 Scheduler, +16.042 Script, and +19.142 Silver.  The branch is valuable
against passive or less self-compounding regimes but unsafe as an unconditional policy.

## Analysis by abstraction level

### Phase timing

Turn 75, not turn 150, is the relevant strategic boundary.  At 100 the farm still adds 38.03 own
score in discovery, but the opponent and tail costs have already erased most margin value.  By
125 the handoff is net harmful.  A controller that reacts only after losing the scoreboard race
cannot recover the missing production horizon.

### Production versus suppression

On confirmation the farm adds 59.77 own score and 13.33 own wood, but also permits 44.87 extra
opponent score and 8.95 extra opponent wood.  It improves existing control-catastrophic cells by
55.32 on average, yet creates or deepens a different loss set enough to raise total negative mass.
This cleanly identifies the trade: the resident's low production is coupled to valuable opponent
suppression, while farm productivity relaxes that suppression.

### Workforce

The two passing options remain at exactly two workers.  Their gain comes from coherent role,
target, banking, and renewable-supply scheduling—not headcount.  Conversely, the worker-rich
options fail badly and rarely complete their intended scale after a turn-75 handoff: mean maximum
workers are 2.11 for `hybrid3`, 2.45 for `accumulate4`, and 2.06 for `norx3`.  Strong bots can use
many workers because funding and supply start early; a late controller swap cannot retrofit that
trajectory.

### Ownership-aware denial

The ownership wrapper improves the discovery handoff only +2.352 margin over the plain private
farm.  It is directionally useful but too small to preserve the resident's full suppressive
effect.  This agrees with the earlier ownership-aware whole-game study: pricing current opponent
crop cycles acts downstream of the reproductive process.

### Statistics and transfer

Discovery was not a meaningless false positive: the sealed mean remains +14.89 and own production
repeats strongly.  What fails is the rank-3 robustness requirement.  The change in opponent-family
signs and negative mass shows why a second block and seed clustering were necessary.  Pooling all
1,920 confirmation cells as independent would report an artificially narrow positive interval;
the independent map-seed interval correctly crosses zero.

### Project-level conclusion

D24 advances the project despite rejection.  It establishes a real complementary macro option,
locates its useful decision time, proves that late workforce expansion is the wrong mechanism,
and isolates opponent regime as the remaining selection variable.  It does not justify another
cutoff sweep, unconditional farm candidate, or confirmation retune.

## Next hypothesis

The next bounded experiment is a **conservative turn-75 regime selector** between the warmed
resident and the frozen `ownership2` continuation.  Its target is complete terminal policy value,
not action imitation or catastrophe classification.  It may use only observable map and
turn-25/50/75 trajectory features and must pass both blocked-seed and leave-one-opponent-family-
out evaluation before any new prospective block is opened.  This is materially different from
the closed turn-3/5/10 worker-three selector: the option has replicated positive mean, the paths
share a 74-turn resident prefix, and the decision directly addresses the measured
production/suppression trade.

If held-family transfer fails, close the selector and retain the result as an architecture clue;
do not add opponent identity, nickname tables, or more capacity.

## Evidence

- `d24-phase-boundary-complete-policy-handoff-protocol-2026-07-20.md`;
- `d24-phase-handoff-smoke-0-4.tsv` and repeat TSV;
- `d24-phase-handoff-smoke-0-4.json`;
- `d24-phase-handoff-discovery-50000-50059.tsv` and `.json`;
- `d24-phase-handoff-confirmation-freeze-2026-07-20.md`;
- `d24-phase-handoff-confirmation-50060-50119.tsv` and `.json`;
- `rust/src/bin/d24_phase_handoff.rs`;
- `cgauto/d24_phase_handoff_analysis.py`.

Confirmation hashes:

- TSV: `2bf059ffd1a64ff0f2d819c4cee201f96bb5b51110b3bb925cf10dfe7ed7cc62`;
- JSON: `07b2317e205cc82567d6334dbf41be5f3f4ff1a13d52d25c5cddeb4c40ecf884`.
