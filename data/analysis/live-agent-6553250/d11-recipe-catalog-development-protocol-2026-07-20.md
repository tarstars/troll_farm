# D11 fixed-recipe catalog — development protocol (2026-07-20)

## Question

Before adding a recipe selector to the accepted D11 V5 live substrate, determine whether the
eight recipes produce a material, repeatable full-game portfolio advantage.  The first decision
is deliberately simpler than selector fitting:

1. does one fixed recipe dominate recipe 6 (`2/2/0/2`)?
2. if not, how large is the hindsight gap between the best fixed recipe and a per-map recipe
   oracle?
3. is the winner stable across seat and opponent families, or does it depend on observable map
   state strongly enough to justify a selector?

No Arena action, resident change, or submission candidate follows from this development study.

## Why this is a new experiment

Earlier opening studies changed the Yamo continuation itself.  They established useful negative
controls:

- always using the max-bank opening lost 10.232 mean score on reused seeds, while its hindsight
  oracle offered only +4.927 and a nested map selector transferred at -2.925;
- the 29-option replicated first-worker screen found no opponent-robust activation rule;
- the shared-state Monte-Carlo teacher had real branch value, but its deployable approximation
  missed the precision gate and its 209.487 ms median / 279.460 ms p95 latency was unaffordable;
- opponent-label workforce selection also failed unchanged validation.

The D11 actor is different: one network was trained with all eight recipe identities in its
observation, and each recipe induces a complete actor-controlled two-worker trajectory.  The
catalog therefore tests full policies with a common controller rather than transplanting an
opening into Yamo.

## Frozen substrate and runner

- V5 source:
  `curriculum-level5-seed-reacquisition-d11-live-v5-fixed-recipe6.rs`, 68,988 bytes,
  SHA-256 `078929c1649b48225fd281656755bc7e21e79bb096177c6645b5166044902aa8`.
- V5 binary SHA-256:
  `3f313a1bc10f2e036225c6acbb32af6b0949ed4d1ed86bbdc6d77a177d67b596`.
- exact-engine runner:
  `rust/src/bin/d11_recipe_catalog.rs`, SHA-256
  `4a26593ea648f4114ed3dedb69bd3896dcf2072d6c4bd1447a2bedbf5fa4dbc8`.
- process protocol: invoke V5 as `--recipe ID`, send the same referee-relative map and turn
  stream used by the accepted parity audit, and apply its commands in the referee-faithful Rust
  engine.

The smoke cell (seed 0, both seats, resident opponent, all recipes) was repeated exactly.  All
non-timing TSV fields matched.  The runner's seven release-mode tests pass.

## Recipe catalog

| ID | Requested worker | Working label |
|---:|---|---|
| 0 | `1/1/1/1` | cheap planter |
| 1 | `1/2/1/1` | compact farmer |
| 2 | `2/2/1/1` | balanced |
| 3 | `2/2/2/1` | harvest producer |
| 4 | `1/3/0/1` | level-1 anchor |
| 5 | `1/2/0/2` | lean chopper |
| 6 | `2/2/0/2` | standard chopper / integration fixture |
| 7 | `2/3/1/2` | hybrid chopper |

## Development block

- Seeds: reused local map seeds 0--7.  These are not a holdout and cannot promote a selector.
- Seats: both.
- Opponents:
  - current stable resident continuation (`resident`);
  - compact and adaptive local wood/economy controls (`compact_gold`, `gold_adaptive`);
  - a native three-worker reconstruction (`norx_native_three`);
  - a worker-rich renewable-field proxy (`legend_balanced`);
  - an independent local controller (`mybot`).
- Recipes: all eight in every seed/seat/opponent cell.
- Games: 8 seeds × 2 seats × 6 opponents × 8 recipes = 768.
- Parallelism: 20 independent games.  Parallel scheduling changes no game state.

The opponent zoo remains a mechanism panel, not an Arena calibration.  Absolute win rates are
diagnostic only.  Recipe comparisons are paired within identical seed/seat/opponent cells.

## Analysis levels

1. **Game level:** score margin, wood edge, terminal turn, successful worker count, and action
   counts.
2. **Paired cell level:** each recipe's margin and wood delta from recipe 6 on the same
   seed/seat/opponent.
3. **Map level:** average both seats and all opponents before ranking recipes; this prevents a
   large opponent family from masquerading as extra map evidence.
4. **Opponent level:** repeat ranking separately for every opponent and report the worst
   opponent mean.
5. **Portfolio level:** compare the best fixed recipe with a map-only oracle and, separately, an
   inadmissible cell oracle.  The latter is only an information ceiling.
6. **Mechanism level:** distinguish recipe quality from failure to train by worker completion,
   repeated TRAIN count, production/harvest/chop mix, and terminal resource edge.

## Decision rules

This development block may generate and rank hypotheses but cannot validate them.

- Prefer a fixed recipe hypothesis if it beats recipe 6 on mean map-balanced margin, has no
  opponent mean below recipe 6 by more than 5 points, and completes training in at least 95% of
  games.
- Consider a map selector only if the map-only oracle gains at least 5 mean margin over the best
  fixed recipe, selects at least two recipes on at least two maps each, and its gain is not
  explained solely by failed training.
- Do not build an online rollout selector from this catalog.  Any selector must use only static
  referee-visible features and must be frozen before a disjoint prospective seed block.
- If neither condition holds, retain recipe 6 and move to layered continuation work rather than
  spending source bytes on selection.

## Outputs

- row-level development TSV: `d11-recipe-catalog-development-seeds0-7.tsv`;
- machine-readable multilevel analysis: `d11-recipe-catalog-development-2026-07-20.json`;
- human result and next hypothesis: `d11-recipe-catalog-development-result-2026-07-20.md`.

