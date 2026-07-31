# DoubtinGiyov tent-proximity denial reconstruction

Verdict: **`MECHANICALLY_COHERENT`**.

## Exact identity and integrity

Game `897547554` is exact active agent/submission `6585578`/`41070584` against DoubtinGiyov `6482016`/`40751228`. Final score is 208–262 from our seat; 300/300 turns decode with zero unknown updates.

## Geometry and trigger

The opponent shack is at (7, 7). There are no adjacent trees initially. The maximum standing cardinal-adjacent tree count is 3; the first >2 state is turn 21.
The resident first contacts an adjacent generation on turn 69. Band exposure is {'more_than_two': 135, 'one_or_two': 150, 'zero': 15}.

## Observed orchard flow

The opponent creates 37 adjacent generations across 37 total adjacent generations. Confirmed opponent adjacent HARVEST commands: 70 for 70 items; confirmed adjacent DROP commands: 83.
Before the resident's first adjacent-tree contact, the opponent already completed 12 harvests for 12 items and 19 drops for 24 items.
Resident adjacent CHOP commands are 65, with 65 directly confirmed by a health decrease or removal.

The first three planted generations are:

- turn 13: BANANA at (6, 7), first resident contact 88, first opponent harvest 70.
- turn 17: BANANA at (7, 6), first resident contact 69, first opponent harvest 56.
- turn 20: APPLE at (8, 7), first resident contact 112, first opponent harvest 56.

## Interpretation

The proposed 0 / 1–2 / >2 trigger is mechanically present and the current policy responds late while the opponent harvests at shack-adjacent cells. This supports implementing a bounded successor candidate. The replay alone does not prove the candidate's causal score uplift, and it authorizes no second Arena cycle.
