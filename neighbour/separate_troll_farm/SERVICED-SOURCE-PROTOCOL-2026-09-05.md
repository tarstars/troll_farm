# Observed productive-source denial on V439

New mechanism, not a reopening of closed home-growth or V564 experiments. V439 remains live;
no platform request is scheduled by this protocol. Success is still mature exact-agent top-seven.

Hypothesis: a plant repeatedly harvested by the opponent is a demonstrated income source;
its destruction can merit a different chop target than static species/proximity alone suggests.
Retain every existing V439 denial term, opening, roster, assignment and renewal mechanism.
Do not presume denial is absent: V439 already remembers opponent crops and adds100/200 priority,
plus a separate scarce-type bonus. Claude's initial claim of zero opponent memory was false.
The new information is recent, unambiguous productive use observed from unit cargo changes.

## One compact implementation

Track consecutive observed states only. A fruit service requires the same enemy unit on the
same living, same-kind tree in both views, positive increase of that fruit in its cargo and
positive prior harvest power. Use actual unit positions, not adjacency. No opponent command
access. Away from the enemy shack, this cargo/position signature is sufficient: PICK is illegal,
MINE gives iron, and PLANT/DROP reduce cargo. On a source within Manhattan one of the enemy
shack, accept service only when the summed same-kind positive cargo gain of every enemy unit
currently on the source does not exceed the observed tree-fruit decrease and every such unit has
a predecessor. This conservative whole-cell rule rejects ambiguous PICK+HARVEST, growth and
last-fruit-duplication turns instead of embedding a growth correction that could invent service.
Other cargo components must remain unchanged for a credited unit.
Keep event(turn,amount) records for12 turns; require at least two distinct service turns.
Use fruit sources only in this first implementation, not speculative wood/regrowth camps.
Clear generation history when the plant disappears or changes kind, and clear observation
history on a gap/reset. Repeated same-turn views are idempotent, and denial credit requires that
the last observed view is the queried current view. Identify own plant births conservatively from prior own seed-carry
decrease at the birth cell; exclude known own trees. Ambiguous own/enemy shared births count
as own for protection. No hidden source ownership or future opponent actions are assumed.

For each existing eligible CHOP/MOVE-to-CHOP candidate of the higher-id, empty-handed own axe
after two own workers exist, retain its baseline score and add one credit. Do not replace the
starter's production, invent a raid commitment, override cargo/plant/train transactions, or
assign multiple actions. Keep the ordinary assignment/conflict resolver authoritative.

Only credit a reachable source closer by actual BFS to enemy bank doors than ours. Compute
the axe's exact existing baseline travel/growth/chop/return/DROP cycle using Moisan's own
predict_tree/chop_outcome routines, and require completion by turn300. No candidate expansion
that bypasses existing protected-tree or renewal guards.

Observed fruit rate is (sum of event amounts except the first)/(last_turn-first_turn), with
events on one turn grouped. Hypothesized income interruption lasts at most2+4*species_reset
turns: a same-kind replacement from seed to first fruit with no travel. Cap it by the remaining
deadline after our predicted kill. New credit =250*rate*interruption/cycle, converting denied
fruit score into V439's1000*wood/cycle units (wood is worth4). Coefficient is fixed at1 in actual
margin units; no sweep. This is a falsifiable approximation, NOT a certified opponent loss:
the opponent may move, replace in parallel, bank less, or exploit other sources. Sunk travel
and damage receive no extra reward; candidates are rescored from each real observed state.

## Verification and advancement

One ledger implementation and one integration. Disabled-credit mode must reproduce exact V439
on all160 archived streams. Behavioral fixtures must test real HARVEST/DROP/CHOP transactions,
growth-cancelled fruit deltas, false adjacency, own/mixed births, resets, deadline, scaling and
target selection. Check both physical seats. No raw source-string test substitutes for behavior.

Freeze final source before comparing strength. Enforce<=100000UTF16, matchedrustc1.90 default
clean compilation, exact readable/compact A/A, full protocol and interactive startup. Fullturn
budget<50ms; target ledger/credit overhead<5ms. Do not resume full-model compiler tinkering.

One192-pair familiar8-map/12-proxy adaptive panel versus exact V439. Advance only with>=1
additional match point, no more than4 negative map-point deltas, zero command/execution/timing
failures. Record activation, target switches, both scores, margin, W/D/L, map/seat/opponent
results. These are development data, not evidence of rank; activation is a diagnostic, not
a post-hoc acceptance threshold. A tie closes this implementation without platform advancement.

A passing candidate requires separately frozen fresh real-agent screen and unopened prospective
confirmation, both seats and materially different opponents near rank7 plus lower controls,
with unchanged official-outcome/deployment discipline. Publication remains a separate exact
artifact step followed by mature ranking verification. No POST is authorized by this document.
