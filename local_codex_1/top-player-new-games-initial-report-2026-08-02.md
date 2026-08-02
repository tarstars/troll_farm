# Initial report — new current games versus the top-player benchmark

Task: `20260802-top-player-new-games-multiagent-analysis`  
Analyst: `local_codex_1`  
Evidence commit: `73718b3fdf9f2dc13359e17cb0ce002f95ea559e`  
Status: independent quantitative report; awaiting the assigned `chatgpt_1` review

## Evidence boundary

The current-source evidence is 153 newly fetched open games of exact agent/submission
`6589709`/`41079653`: 95W/2T/56L, seats 68/85. Seven sealed-tagged games are excluded.
Only one game is directly against a snapshot top-20 player: `897780884`, a 333–403 loss to
rank-13 Astrobytes. The 2,684 top-20-source games are observational benchmark context, not
direct treatment evidence.

Among the 96 full 300-turn current games, the resident averages score
`37.60/72.26/105.64/138.90/173.50/211.97` at turns 50…300. The 1,268 top-20 sides that
finish with two successful workers average
`24.77/53.35/91.68/132.62/177.46/224.78`. Thus the resident leads this heterogeneous
benchmark through turn 200, crosses around turn 250, and trails by 12.81 terminal points.
This ranks late checks above opening changes; it does not identify a causal policy.

## Ranked ideas

### 1. H3a — workforce-pressure-conditioned existing-tree priority

**Disposition:** immediate intervention shortlist; rubric estimate 88/100; medium confidence
that the discriminator is worth running, no causal-value estimate before it runs.

Opponents finish with at least three workers in 46/153 current games, across 31 exact
identities and both resident seats. Those games are 16W/30L with mean margin −28.91; the
107 non-scaling games are 79W/2T/26L with mean margin +46.41. This −75.32 association has a
game bootstrap 95% interval of approximately [−109.24, −42.28], but workforce is an
observed opponent outcome and can proxy general opponent strength.

The temporal version is sharper. In 28/96 full games the opponent's second successful
TRAIN, creating worker three, appears by the turn-150 curve boundary (decoder turn ≤151).
The resident leads at turn 150 in 26/28, yet wins only 7/28 and loses 19 of those early
leads. Mean margin moves from +64.89 at turn 150 to −57.29 terminal; in the other 68 full
games it moves from +37.19 to +55.49. A game bootstrap puts the difference in late margin
change at −140.47, 95% interval [−188.33, −95.98]. The direction holds in both seats. This
is association and prioritization evidence only.

The smallest sanctioned seam is already reconstructed: the exact Phase-21 eligibility
and ETA≤6 tracked-existing-tree operation `candidate.score += candidate.score`, made sticky
only after public state first shows three opponent workers. The three arms must remain the
exact stable fallback `a8eb3b2b…`, identical always-on treatment `083107f5…`, and
conditioned treatment. The active b100 resident is supporting field evidence, not silently
substituted as a new arm.

Immediate check: freeze and run the existing H3a proposal's 6,144-cell development matrix
(128 fresh unsealed official maps × both seats × eight families × C0/A1/C1), with the exact
resident/referee hashes and paired map roots. The runnable source-reconstruction gate is:

```bash
python3 chatgpt_1/h3a_pressure_treatment_reconstruction.py --self-test
python3 -m pytest -q tests/test_h3a_pressure_treatment_reconstruction.py
```

Then build a task-private runner; do not edit a resident artifact. Pass only under the
already frozen H3a gates: conditioned − control ≥+2 mean paired margin with clustered lower
bound >0; conditioned − always-on ≥+5 with lower bound >0; both seats nonnegative; at least
6/8 families nonnegative; worst family ≥−1; no worse catastrophes; negative mass ≤1.05×;
own score loss no worse than one. Stop on insufficient activation, integrity failure,
conditioned≈always-on, failure versus control, or any tail/seat/family gate.

Nearest closures are unconditional opponent-crop bonus/distance/focus grids, harvest on
contact, worker-bill denial, identity branches, and generic cap-conditioned policy. H3a is
distinct only because its exact treatment and mandatory always-on comparator make the
workforce condition itself falsifiable.

### 2. B3.11 relative fruit-control predicate — census before any edit

**Disposition:** audit first; rubric estimate 63/100; low confidence and zero projected
policy value until exact provenance is measured.

The resident harvests 1,393 fruit units in the 153 games; 1,263 (90.7%) are APPLE, but
positive APPLE harvest occurs in only 27 games and five games contribute 56.2% of all
apples. Losses average 14.98 apples harvested versus 4.46 in wins. This concentration and
outcome reversal make aggregate “harvest more” or “plant less” rules invalid.

The only immediate action is the read-only B3.11 joint-predicate census permitted by the
constraints: for every open current game, attribute resident-created and opponent-created
fruit generations; separate actual enemy capture from mere reach; and price resident wood,
liquid stock, protected regeneration, clear time, and the next TRAIN bill. Use exact game
paths from the frozen open cohort, never a directory-wide discovery scan.

Pass to a source proposal only if the same predecision predicate recurs across both seats
and multiple exact opponents and conservative deny/capture benefit minus lost wood reaches
20 margin per affected game. Stop otherwise. No source seam exists before that result.
This remains distinct from B3.8/B3.10/D173 only as a relative control-feasibility
measurement; harvest-before-chop, near-camp harvest, focus/species inversion, ETA/bonus
retuning, and opponent-bill reachability remain closed.

### 3. Explicit WAIT state census — search only for a new recurrent invariant

**Disposition:** audit first but lower priority; rubric estimate 58/100; do not build a
blanket WAIT rewrite.

The resident emits 1,658 explicit WAIT actions in the 96 full games, but 1,232 (74.3%) occur
after turn 250. WAIT means are 18.55 in non-losses and 15.70 in losses, and its correlation
with terminal margin is −0.04. In the direct Astrobytes game, the five t4–8 WAITs are
productive ripening waits that fund TRAIN on t11, while the t291–300 waits occur after all
83 collected wood is banked. The benchmark logging/no-command convention is also a
confound.

Immediate check: decode the 153 exact open trajectories and classify each WAIT by action
legality and adjacent planner state. Retain only a repeated, current-source state not already
covered by transit/full-capacity artifacts, E5 ripeness wait, E2 routing, D171/D176
oscillation, B3.14 bank commitment, or B3.15 on-tree ownership. A surviving state needs an
exact replay reproducer, one invariant-sized seam, and same-map/both-seat A/B. Stop if the
excess is terminal, semantic, benign, already closed, or has an optimistic whole-corpus
ceiling below one point/game.

## Explicitly not immediate

- Generic worker-three training, worker-two retiming, funding ladders, fixed openings and
  A2 retunes are closed; the association above does not reopen them.
- Primitive-only delineate cloning is a legitimate L1 programme, but extractor parity and a
  closed-loop value gate make it a gated programme rather than an immediate edit.
- A new two-worker productive architecture is supported descriptively by the benchmark, but
  it requires an owner-authorized new representation. Plants-minus-PICK is only a provenance
  proxy, not proof of a self-reproducing orchard.
- Generic harvest/plant/mining grafts, banking cleanup, body blocking, collision rewrites,
  and crop bonus/focus retuning are closed or unsupported.

## Reproduction notes

All counts use the hash-pinned side table and the exact processed/open trajectories named by
its current-game IDs. Successful roster size is `1 + effect_trained`; using TRAIN command
count would wrongly exclude game `896636759`, whose second TRAIN fails. The turn-150 group
uses decoder `second_train_turn <= 151` to match the curve boundary; a literal ≤150 gives
27 rather than 28 games. These definitions must remain explicit in review.
