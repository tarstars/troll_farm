# E3 chop-order scope audit — 2026-07-30

Verdict: **`VOID_PREMISE_DUPLICATE`**

## Decision

The registered premise that chop ordering had not been audited is false. The exact resident's
per-turn scorer itself has no fixed tree order, but the project already valued persistent
tree jobs followed by exact resident continuation and, more decisively, repeated joint
completion-boundary tree choices on the exact resident. Those upper bounds include two-tree
orders while unchosen trees continue through the exact simulator.

No E3 implementation, candidate surface, seed range, or dependency on N4 is opened.

## What the live resident does

For every reachable live tree, `MoisanBot::chop_candidates` computes:

- travel time with the unit's movement speed;
- tree growth and health at arrival;
- further growth while chopping;
- wood limited by remaining carry capacity;
- return-to-home-door time plus DROP;
- the `typeToCut` opponent-distance bonus.

The candidates are reconstructed every turn and selected jointly across the resident's two
workers. Production sets `tree_target_bonus = 0`, so the latent tree-commitment map is cleared
and there is no multi-tree plan or fixed sequence to inspect. E3's real conceptual question is
therefore whether a terminal-valued completion-boundary sequence beats adaptive greedy
rescoring—not whether a stored order is internally wrong.

## Existing coverage

### Exact-live current-target persistence

The 2026-07-16 tree-target-bonus discriminator remembered the currently selected tree until
completion eligibility ended. On 60 reused paired seeds it gained only +0.617 margin and
+0.108 wood, with 25/19/16 wins/ties/losses; the project parked it below the material bar.
This tests current-target flapping, not the next tree, but establishes that simple persistence
is not a missing large lever.

### Exact-resident one-job terminal oracle

The persistent job-bundle oracle captured 480 exact-resident roots at turns 50/100/150,
enumerated completion-valued `FELL_BANK`, `HARVEST_BANK`, and `BANK` options, executed the
job through travel/work/banking, then returned to exact resident terminal continuation.
`FELL_BANK` was selected at 179 roots and averaged +20.972 conditionally, but the complete
grammar's selected-root mean was only +18.584 versus the frozen +20.0 gate. Its protocol and
verdict explicitly close larger target catalogs and selector fitting on resident-local job
redirection.

### Exact-resident repeated completion-boundary oracle

D36 is the decisive superset:

- exact stable resident, with controller memory cloned at every root;
- up to two targets per acquisition kind per unit in the inherited D35c catalog;
- joint, collision-aware, persistent bundles including `FELL_BANK(tree)`;
- exact terminal rollout for every option;
- replan after each completion boundary, up to four non-control epochs.

All 128 tasks pass integrity, with 17,963 terminal option rollouts. Non-control is selected in
112 tasks; 87 execute at least two bundles and 292 non-control epochs run. Thus actual
multi-tree/job sequences are active, and unchosen trees grow and interact under the exact
simulator before the next boundary.

The upper bound gains only +19.617 own score and +10.633 margin versus exact resident, below
the frozen +68/+25 gates. Only 2/8 families reach +15 margin and repeated negative-margin
mass remains worse than resident. D36 explicitly closes another target, objective, threshold,
or additional resident-overlay iteration.

## Evidence that does not carry the verdict

Several other studies show target order matters but use different substrates:

- D49's chopper-first reservation permutation is highly active on D40 but fails transaction
  integrity before value.
- D41d's rank-one action continuation and D79's broad spatial target scorer use D40-family
  controller states, not exact live resident sequencing.
- D100 values same-turn pair residuals, not multi-turn completion order.
- The resident-chopper command transplant proves target choice is coupled to banking,
  regeneration, and whole-policy allocation, but is not an ordering oracle.

They prevent an overbroad claim that “tree choice never mattered,” but the E3 closure rests on
the exact-resident one-job and D36 repeated terminal oracles.

## Boundary

E3 is a subset of a rejected stronger representation, not a surviving N4 branch. N4 may still
measure reconstructability and intertemporal value of the resident's complete candidate-pair
surface; E1's opening prefix depends on that surface. Neither fact reopens a tree-only
completion sequence whose exact-resident terminal upper bound already failed and whose target
expansion was explicitly closed.

Reopening would require a materially different action representation, not another cluster
definition, target count, order depth, commitment bonus, or two-tree permutation.

## Sources

- `rust/src/bin/yamo_orchard_live.rs`, `chop_candidates`, tree commitments, and pair
  selection.
- `data/analysis/live-agent-6553250/tree-target-bonus25-stall-corrected-60.json`.
- `data/analysis/live-agent-6553250/bundle-job-oracle-{protocol,result}-2026-07-19.md`.
- D36 resident-anchored constrained joint-oracle protocol and result, both dated
  2026-07-21 under `data/analysis/live-agent-6553250/`.
- Focused D41d, D49, D79, D100, and resident-chopper-layer result records.
