# V546 dense source orchard result

## Design and live evidence

The 68-game V543 live snapshot showed the specific high-rated gap: against five opponents rated at
least 18, V543 planted 10.6 trees and banked 51.8 wood while opponents planted 36.6 and banked 96.4;
all five games were losses. V546 retained the complete V543 adaptive controller and changed only
the repaired R1FA economy's three verified-own-tree maintenance checks from six live trees to ten.

The compact source was 99,828 UTF-16 units, SHA-256
`9f539ef1cfe6993abc27968ea8866d3fd051d4a6a49cbb2148c6a088ba84750e`. Both forms compiled and
accepted sample protocol input; nine focused builder tests passed.

## Matched V543 comparison

Exact V543 and V546 were independently run against V468 on the same 192 games (seeds 9,941,000--
9,941,007, both seats, 12 opponent families). The V468 command streams matched between runs.

| measure | V543 | V546 | delta |
|---|---:|---:|---:|
| mean own score | 358.21 | 378.48 | +20.27 |
| mean opponent score | 158.40 | 160.46 | +2.06 |
| mean margin | 199.81 | 218.02 | +18.21 |
| mean wood | 77.68 | 84.89 | +7.21 |
| plant commands | 19.65 | 25.31 | +5.66 |
| W/T/L | 163/1/28 | 166/1/25 | +3/0/-3 |

Margin improved in 124 games, tied in 35 and regressed in 33; the paired mean improvement's
standard error was 2.10. The resident family was byte-behaviorally unaffected at −31.1 mean margin
and 5/1/10. All eleven economy-selected families improved mean margin, from +4.5 to +28.8.
Candidate timing remained bounded at 1.00 ms p95 and 3.98 ms maximum.

## Gate verdict

Against the required V468 baseline, V546 scored 20.1 versus 93.0 at turn 100 (−72.9), 142.9 versus
176.2 at turn 200 (−33.3), and 378.5 versus 247.2 at turn 300 (+131.2). W/T/L was 166/1/25 versus
177/3/12. The denser orchard is a real late-economy improvement but does not preserve the required
opening, so V546 fails the absolute checkpoint gate. No fresh-map holdout, packaging audit, or
platform submission was opened.

V543-control panel SHA-256:
`e5d897be480a01314299f3867775971ab7978a159b85eec0f92b6e47d6630360`.
V546 panel SHA-256: `29605b5486354f7446a64049c846813ee28810614a9dab36f8d4d261a107409e`.
V546 gate-report SHA-256:
`ddf9c8952cb645934ec9e4897455fa746c55c6b0c91e3e9daa01b3507f68ace5`.
