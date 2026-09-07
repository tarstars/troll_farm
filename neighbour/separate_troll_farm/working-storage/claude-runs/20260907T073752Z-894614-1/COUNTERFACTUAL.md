# Four forced counterfactuals — map 9947505, adaptive resident (index 0)

bill = [PLUM 6, LEMON 3, APPLE 3, BANANA 0, IRON 3, WOOD 0], spec (2,1,1,1)

## seat0 t40
  DIAG activate t=40 spec=(2, 1, 1, 1) bill=[6, 3, 3, 0, 3, 0] forced=true
  DIAG cancel t=78
  bank at cancel+1 [P,L,A,B,I,W] = [6, 1, 8, 4, 3, 4]
  workers max ON 2 vs OFF 2
  final ON 152:160 (turn 230) vs OFF 140:148 (turn 226)
  margin ON -8 vs OFF -8 => delta 0
  first persistent margin crossing turn: None

## seat1 t40
  DIAG activate t=40 spec=(2, 1, 1, 1) bill=[6, 3, 3, 0, 3, 0] forced=true
  DIAG cancel t=86
  bank at cancel+1 [P,L,A,B,I,W] = [2, 2, 8, 4, 3, 8]
  workers max ON 2 vs OFF 2
  final ON 168:176 (turn 232) vs OFF 148:144 (turn 239)
  margin ON -8 vs OFF 4 => delta -12
  first persistent margin crossing turn: None

## seat0 t60
  DIAG activate t=60 spec=(2, 1, 1, 1) bill=[6, 3, 3, 0, 3, 0] forced=true
  DIAG cancel t=106
  bank at cancel+1 [P,L,A,B,I,W] = [4, 1, 8, 4, 3, 9]
  workers max ON 2 vs OFF 2
  final ON 184:156 (turn 252) vs OFF 140:148 (turn 226)
  margin ON 28 vs OFF -8 => delta 36
  first persistent margin crossing turn: 165

## seat1 t60
  DIAG activate t=60 spec=(2, 1, 1, 1) bill=[6, 3, 3, 0, 3, 0] forced=true
  DIAG cancel t=106
  bank at cancel+1 [P,L,A,B,I,W] = [4, 1, 8, 3, 3, 9]
  workers max ON 2 vs OFF 2
  final ON 176:168 (turn 266) vs OFF 148:144 (turn 239)
  margin ON 8 vs OFF 4 => delta 4
  first persistent margin crossing turn: None


## Margin (own-opponent) ON minus OFF at checkpoints

| proposal | t80 | t100 | t120 | t150 | t180 | t200 | t220 | last common |
|---|---|---|---|---|---|---|---|---|
| seat0 t40 | -13 | -17 | -6 | -7 | -10 | 5 | -8 | 0 |  (last common turn 226)
| seat1 t40 | -17 | -8 | -18 | -14 | -3 | -23 | -6 | -8 |  (last common turn 232)
| seat0 t60 | -10 | 1 | -2 | -5 | 18 | 30 | 18 | 37 |  (last common turn 226)
| seat1 t60 | -3 | -4 | 0 | -3 | 2 | -3 | 12 | 0 |  (last common turn 239)

## LEMON bank on the ON arm during the open commitment

seat0 t40: LEMON 000000000000001111111111111111111111111111111111111  (need 3; turns 40..90)
seat1 t40: LEMON 000000000000001111111111111111222222222222222222222  (need 3; turns 40..90)
seat0 t60: LEMON 000000001111111111111111111111111111111111111111111  (need 3; turns 60..110)
seat1 t60: LEMON 000000000000001111111111111111111111111111111111111  (need 3; turns 60..110)

## Authoritative final outcomes (panel TSV, not the one-turn-early DIAG stream)

Baseline OFF is identical in all rows: 148:148, margin 0, 0 issues, 2 workers.

| proposal | forced price (macro-parent @H=60) | cancel turn / reason | LEMON banked (need 3) | paid | workers ON | final ON | margin delta |
|---|---|---|---|---|---|---|---|
| seat0 t40 | -17.000 | 78 / nothing outstanding reachable | 1 | no | 2 | 156:160 | -4 |
| seat1 t40 |  -1.402 | 86 / nothing outstanding reachable | 2 | no | 2 | 172:180 | -8 |
| seat0 t60 |  -8.057 | 106 / deadline (opened+45) | 1 | no | 2 | 184:164 | +20 |
| seat1 t60 |  -6.854 | 106 / deadline (opened+45) | 1 | no | 2 | 176:172 | +4 |

The four forced prices reproduce the previously reviewed values -17.0 / -8.06 /
-1.40 / -6.85 exactly, so this is the same repaired family, not a variant.

0 of 4 reach payment; 0 of 4 train a third troll; 0 of 4 take a productive
new-worker action.  There is no investment whose payoff the horizon could
truncate.  The two positive margin deltas (seat0 t60 +20, seat1 t60 +4) arrive
long after the commitment is cancelled at t106 (seat0 t60 crosses only at ~t165,
still -5 at t150) and come from re-tasked gathering plus a longer game against an
adaptive opponent, not from a hire that never happened.
