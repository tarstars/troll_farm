# Dispatch primary review — failed mechanics/export gate

Primary independently compiled/reran18 passing tests with absoluteRust1.90.
Tests sum critical_issue_count only, hiding noncritical blocked moves. Parsed192
unique rows:77/1/114=77.5 vs167/6/19=170;26313vs1issues,0criticalboth. ALL192
baseline command arrays match gap210944 controls, not just scores. Production
hashes unchanged; worker terminal04:19:01 exit0.

Original gate ordering was violated: source303335UTF16,nocompact,no16streams or
runtime validation, yet192panel ran. Failed offline mechanics evidence only.
emit() uses a one-pass conflict filter: cancelling a later MOVE can leave an
earlier target occupied. Current-cell MOVEs and saturated doors need reproducers.
Do not equate BFS-minus-own-units with official semantics: Java resolves terrain
distances first, then endpoints/dependencies/circularswaps. Direct endpoints are
a local harness requirement, not an official prohibition against distant goals.

Primary verified Java Unit.getTrainingCosts chargesIRON when league>=3; both
parse and execution use Unit.canTrain. It does not infer league from terrain.
Rust parser always checks fullbill, but engine.apply_train skipsIRON if terrain
is empty. Earlier zeroiron/iron-free/chop1 free-hire fixtures mixed unsupported
assumptions; their failure alone is not a highest-league controller defect.
See docs/REFEREE-LEAGUE-SCOPE-2026-09-07.md. Do not silently alter frozenmodels.

Authorize one concrete movement/export repair, economics heldfixed, with all
legality counts tested. No promise this recovers the92.5pointdeficit or rank7.
