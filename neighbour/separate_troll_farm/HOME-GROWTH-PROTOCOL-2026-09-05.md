# Compact home-tree scheduling experiment

Status: local mechanism experiment only. V439 remains live at rank28; no publication or
platform request is scheduled. The full-model planner's three deployment failures stay closed.
The fixed top-seven objective and all gates in EVALUATION.md remain unchanged.

The stratified V439 audit passes all160 games and reconstructs25,882 own/17,502 opponent issued
CHOP commands exactly. In the41 replay-rated22–25 losses, the uncontested capacity-two,
chop-power2+ cohort still declines: wood per positive event1.956→1.838→1.153 and mean tree
size3.430→3.131→1.502 across1–100/101–219/220+. Late data cover18 games,410 actor-turns,
124 positive events. Capacity3+ has the same direction but only5 late games/27 positive events.
This is not merely a pooled capacity-one effect; composition and species still matter.

Falsifiable mechanism: immediate CHOP commitment during home regeneration sometimes destroys
a young tree before an economically useful growth tick. A compact deterministic scheduler can
improve completed banked-score cycles without embedding the full two-player forward model.
Larger-tree bonuses and removing the physical capacity clamp are explicitly rejected.

## Kernel and assumptions

Use actual per-species health/cooldown rules and action-before-growth ordering. One fixed home
door cell, one unit initially empty-handed, one existing tree. Actions are WAIT/CHOP until death,
then DROP; subsequent cycles are PICK/PLANT/WAIT/CHOP/DROP. Finite banked seeds
cost one score each; wood earns four only when banked. Previously paid seed cost is sunk.
No harvest, travel, other workers or opponent policy is simulated in this local kernel.

Pre-integration model refinement, motivated by the observed sequence901547425 turns272–274:
the current tree is LEMON but remaining bank fruit is six APPLE and no LEMON. Ignoring those
future cycles could overstate the benefit of waiting. Model all four finite seed stocks in
V439's existing fixed PICK priority (BANANA, PLUM, LEMON, APPLE), not only the current species.
The priority makes the future seed sequence deterministic, so no four-dimensional inventory
search is needed. At most75 complete cycles can fit in300 turns. Dynamic programming over seed
position and time must not skip a higher-priority seed to access a later species. Retain the
single-species API/tests as a compatibility case. This refines an unintegrated mechanism, not
a selected or failed competitive candidate; no comparison data or gate is being rewritten.

Compute earliest kill times for each attainable collected-wood amount by a bounded search over
tree(size, health, cooldown), separately forcing the first WAIT or CHOP. Pre-damaging then
waiting is allowed; merely waiting to a target size is not assumed optimal. Compute fresh-seed
cycle profiles with the PLANT turn's growth tick included. Bounded seed/time dynamic programming
then maximizes banked points by the actual remaining300-turn deadline, allowing mixed cycle
sizes and unused time. Reject unsupported physical states. No arbitrary shortened planning
horizon, credited unbanked cargo, or infinite-seed approximation.

Compare first-WAIT and first-CHOP under the same continuation model; prefer CHOP on ties.
This is exact only for the stated single-cell model. Shared stock, alternative seed species,
opponent arrivals, friendly traffic and early global termination are integration risks, not facts
the kernel may invent. A later wrapper must explicitly guard these and leave all other baseline
commands unchanged. It must not commit losing-branch or simulated future policy memory.

## Bounded advancement

1. One kernel implementation, executable unit/property fixtures, and independent actual-rule
   transition/sequence checks. Reject Claude's unverified illustrative arithmetic; derive the
   example from executed actions. No candidate is selected without a real banked-score example.
2. At most one initial guarded V439 integration. No canonical edits. Measure activation on all
   archived streams, source size, matched-compiler cost and full protocol/runtime. Aim for less
   than5ms scheduler overhead; per-turn total must remain below50ms. Stop rather than restart
   the full-model compiler-microoptimization queue if the architecture is too costly.
3. One initial192-game familiar8-map/12-proxy adaptive comparison versus exact V439. Require
   at least+1 match point, no more than four negative map-point deltas, and zero execution or
   timing failures to consider fresh real-agent testing. This is development selection only.
4. Any real-agent screen, prospective confirmation and publication require new frozen plans
   with the unchanged official-outcome/deployment gates, then mature exact-agent top-seven
   verification. This document schedules no POST and is not a claim that the mechanism wins.
