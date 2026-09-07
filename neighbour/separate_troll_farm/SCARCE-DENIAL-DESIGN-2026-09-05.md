# Released workers with scarce-fruit denial

## Hypothesis and exact comparison

The capital-release ablation begins chopping on turn 5 but still lets putibuzu train on 68 and
loses 203–263. Reinspection of the winning V439 game shows its second worker also has carry one
(`1/1/0/2`), compared with our `1/1/1/2`. Capacity alone therefore does not explain this block.
V439 cuts the scarce wild plums early and wins 117–86 without an opponent second hire.

Test the scarce-kind denial rule inside the **live** production comparison of the two-worker
controller. This is not a restoration of the dead opponent-crop bonus. Compare exact archived
cap2, new cap2+denial, and the archived V439 reference. Keep first-hire talents, movement, renewal,
and worker ceiling unchanged. The four-worker default and denial-disabled behavior are retained.

## Mechanism

Latch the same initial plum/lemon focus selector as V439. A legal chop offer on a non-owned tree
of that kind receives the old bonus while the opponent has at most two workers or the worker is
already on the tree. Convert its scale exactly: old `1000*wood/trip` becomes this controller's
`100000*(4*wood)/trip`, so `900/(1+enemy-shack Manhattan distance)` becomes
`360000/(1+enemy-shack Manhattan distance)`. Add after division, not as fictitious banked points.

Keep the existing complete-trip feasibility, crop protection and reservation rules. Do not reward
cutting an owned source. No opponent-planted-only filter, new game-long raid quota or arbitrary
early cutoff is added. Existing persistent chop goals are unchanged in this single-change test;
their potentially stale commitments remain a documented limitation, not silently fixed here.

Behavioral fixtures must distinguish near payable wood from a farther scarce-fruit target, disable
the bonus for an unrelated kind/owned crop, suppress it after three enemy workers except on-tree,
prevent two workers taking the same tree, and retain the original suite. Disabled export must
reproduce the frozen cap2 commands; readable/compact enabled exports must agree on full streams.

## Development budget and prospective decision

Run one familiar 192-pair, eight-map local panel versus exact V439 (regression only). Run four
official development games, all seat 0: repeat exact cap2 versus putibuzu/2609051701, then enabled
versus putibuzu/2609051701, delineate/2609051102 and Pony/2609051603. Compare with existing exact
cap2 and V439/V368 references; verify initial state, fixed opponents, repeat control and full
command streams. No automatic retries or source tuning while the block is being collected.

Advance to a separately frozen fresh-map/both-seat comparison if the enabled variant gains at
least one match point over cap2 without losing its Pony control win and passes deployment audits.
This is triage, not a significance test or a rating claim. A source error requires fixtures and
a new snapshot, not hidden replacement of the frozen policy. A failed screen does not authorize
publication. Production remains V543 unless a later supported finalist passes actual deployment
and competitive checks under EVALUATION.md.
