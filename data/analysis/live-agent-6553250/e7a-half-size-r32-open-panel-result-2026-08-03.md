# E7a half-size r32 full open-panel result

- Task: `20260802-e7a-half-size-logical-simplification`
- Candidate: `integrated-half-r32.rs`, 31,387 bytes, SHA-256
  `abb202db71040f8784b7d02cc114ced9f71d82e82d3c8a1cc975d87d3feeb4da`
- Panel completed UTC: `2026-08-02T21:50Z`
- Verdict: `REJECTED_OPEN_PANEL`
- Arena action: none

## Frozen panel

The exact command published before execution completed successfully in 103.936 seconds.
It evaluated 43 already-consumed official-map seeds 9,854,000--9,854,042, both seats, and
six frozen opponent families: 516 paired tasks. There were zero critical and zero
unclassified referee outcomes. The output TSV has SHA-256
`43decd5b66c10224c0f7f6be9cc475471dd2b023bdcafeedaf8cc800a2191727`; the result JSON has
SHA-256 `1435022cbb07add43c604e1c70becbdd59f45a20f733d666ac7780a71c90c555`.

## Value result

Candidate-minus-baseline mean margin is **-53.6609** and the map-cluster bootstrap 95%
lower bound is **-69.2539**. Both seats are negative: -55.1550 for seat 0 and -52.1667 for
seat 1. All six family means are negative:

| Family | Mean margin delta |
|---|---:|
| resident | -20.6047 |
| gold_adaptive | -49.5698 |
| compact_gold | -64.9767 |
| norx_native_three | -47.3488 |
| legend_balanced | -87.1628 |
| mybot | -52.3023 |

Mean own score falls from 200.5349 to 156.8702 while mean opponent score rises from
123.2539 to 133.2500. Catastrophes increase from 19 to 64 and negative-margin mass from
4,138 to 15,143. The value, bootstrap, catastrophe, negative-mass, family-breadth and
both-seat gates all fail.

## Engineering result

The candidate does preserve worker-two timing: 516/516 baseline-training tasks train in the
candidate with median delay zero. It eliminates the panel's long period-2 episodes: 115 to
zero, with maximum run 244 to 4. Latency also passes comfortably: candidate p95 is 0.353 ms
versus baseline 0.408 ms (ratio 0.865), and candidate maximum is 1.813 ms.

These engineering successes cannot compensate for the broad value failure. The exact-live
counterexample packet is not run for r32 because Stage D already rejects the candidate.

## Disposition

r32 is a terminal negative artifact under the frozen protocol. It is not submitted, and
its evaluated panel will not be used to retune r32. The owner goal remains open: any new
candidate must be a distinct, predeclared successor and use an untouched validation range.
