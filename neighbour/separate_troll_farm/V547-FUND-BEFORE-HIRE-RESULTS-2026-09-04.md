# V547 fund-before-hire result

## Design and build

V547 retained V546's ten-tree repaired-R1FA economy and changed one decision: after the first
additional troll, later hires were ineligible through turn 100. The controller kept gathering the
same bills, leaving their inventory visible as score at the turn-100 checkpoint, and released the
training guard on turn 101.

The compact source was 99,856 UTF-16 units, SHA-256
`f87bd4822bc74ebbb6c6f754453e91921363ea281aa3d7a3cc5152850b0ee059`. Readable and compact
forms compiled and accepted sample protocol input. Nineteen focused builder, gate, and diagnostic
tests passed. Candidate planning latency was 0.956 ms p95 and 3.99 ms maximum.

## Matched V546 comparison

V546 and V547 were run against exact V468 on the same 192 games (seeds 9,941,000--9,941,007,
both seats, 12 opponent families). Every V468 baseline field and command stream matched between
the two panels, isolating the training-timing change.

| measure | V546 | V547 | delta |
|---|---:|---:|---:|
| own score at turn 100 | 20.12 | 39.03 | +18.91 |
| own score at turn 200 | 142.91 | 122.56 | -20.35 |
| final own score | 378.48 | 358.81 | -19.67 |
| final opponent score | 160.46 | 163.26 | +2.80 |
| final margin | 218.02 | 195.55 | -22.47 |
| wood | 84.89 | 79.62 | -5.27 |
| PLANT commands | 25.31 | 24.02 | -1.29 |
| CHOP commands | 134.36 | 124.30 | -10.06 |
| final workers | 3.781 | 3.771 | -0.010 |
| W/T/L | 166/1/25 | 164/1/27 | -2/0/+2 |

The median training event moved from turn 81 to turn 101. Margin improved in 41 games, tied in 36,
and regressed in 115; the paired margin delta was -22.47 with standard error 3.31. All eleven
economy-selected opponent families gained at turn 100, but ten lost at least 9.6 final margin; the
resident-selected family was exactly unchanged. The delay therefore banked part of the missing
checkpoint score, but withheld productive workers during the decisive turn-100--200 interval.

## Gate verdict

Against required V468, V547 scored 39.0 versus 93.0 at turn 100 (-54.0), 122.6 versus 176.2 at
turn 200 (-53.6), and 358.8 versus 247.2 at turn 300 (+111.6). W/T/L was 164/1/27 versus
177/3/12, and opponents' final mean score rose by 55.0. It fails both early checkpoints and the
outcome safety check. No fresh-map holdout, packaging audit, or platform submission was opened;
V543 remains the published artifact.

The result also rules out training expenditure as the whole early-score deficit: suppressing it
recovers only 18.9 of V546's 72.9-point turn-100 gap. A viable bridge must change the first two
workers' scoring actions rather than impose a fixed global hiring date.

V547 panel SHA-256:
`303a62fcb94230b45b3b62333b27fe206d31b21f03ff2a7a8371bcce91e351b5`.
Gate-report SHA-256:
`7a063c5228c7de4a57ff9dec1edb4cf2a45aab2165095ad9e973367392fcb91d`.
Diagnostic-report SHA-256:
`6bf8ff391e9bfdfbc53754dfc416dd1977ba58ef957b1286ca2afd7c6a09cb02`.
