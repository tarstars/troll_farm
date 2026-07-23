# D88c held-out support-count correction (2026-07-21)

## Defect

D88a/D88b copied the fixed 16-game validation ID list correctly but transcribed its already-known
D86 label support incorrectly as 12 renewable plus four nonrenewable games. The actual unchanged
D86 labels are ten renewable plus six nonrenewable games. The D88b analyzer therefore reports a
literal rejection even though all ten available renewable games satisfy each of the two absolute
`at least 10` phase-order requirements.

This defect was noticed after D88b validation telemetry had been opened. It must remain visible in
the record; the original D88b JSON and decision are immutable.

## Conservative mechanical correction

Read only the immutable D88b aggregate JSON. Do not reparse a replay or recalculate a behavioral
feature. Replace the two impossible support predicates as follows:

- `renewable_games == 12 and bank-before count >= 10` becomes
  `renewable_games == 10 and bank-before count == 10`;
- `renewable_games == 12 and complete-phase count >= 10` becomes
  `renewable_games == 10 and complete-phase count == 10`.

This preserves the preregistered absolute minimum of ten demonstrations and tightens the implied
success fraction from 83.3% to 100%. All other gates remain byte-for-byte equivalent in meaning.
Require both independently generated D88b aggregate inputs to produce identical corrected gate
sets and decisions.

If every corrected gate and every original integrity gate passes, D88c may authorize a written
controller blueprint and a disabled-by-default, prospectively frozen D89 local challenger. It
does not authorize TestSession, submission, resident replacement, or any platform write.
