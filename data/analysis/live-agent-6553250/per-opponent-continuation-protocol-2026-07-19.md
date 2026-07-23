# Per-opponent continuation feasibility — frozen protocol, 2026-07-19

## Question

Does conditioning on a stable submitted agent make rich-opponent 50-turn continuations materially
more predictable than population-level state retrieval?

This is read-only model reconstruction.  It does not evaluate or change the resident.

## Frozen agents and result-blind panel

Use the exact Phase 21 agent IDs for the six names with at least two rich occurrences:

| Agent | ID |
|---|---:|
| Bondo416 | 6480941 |
| MSz | 6479460 |
| Meruem | 6479385 |
| celeria | 6512040 |
| gaha | 6481397 |
| viewlagoon | 6481504 |

For each agent, read the completed battle metadata and exclude the 21 consumed Phase 21 rich game
IDs.  Sort remaining exact-agent games by SHA-256 of
`per-opponent-continuation-v1:<agent_id>:<game_id>`, fetch in that order, and retain the first 24
replays with at least 150 exact decoded turns and no unknown state diff.  Assign the first 16 by
that same order to discovery and the next eight to confirmation.  Record all fetch/eligibility
attrition.  Game outcome, score, opponent, map, and commands cannot affect selection.

## Frozen examples, models, and validation

Build cutoff-50 and cutoff-100 examples with the same eight next-50-turn targets and fixed scales
as the failed cross-agent audit.  Reuse its map, state, and history features without additions;
if an agent has not trained a first worker by a cutoff, encode its four first-worker stats as zero.

Choose `k` from `{1,3,5}` on discovery leave-one-game-out, pooled across agents and cutoffs.  Freeze
the chosen values, then compare on the 96 confirmation examples:

- population mean and population state/history retrieval trained on all 96 discovery games;
- identity mean and identity state/history retrieval trained only on the target agent's 16
  discovery games.

All feature scaling is fit on the eligible training fold.  Retrieval is the unweighted mean of the
nearest `k`; tie-break by game ID.  No agent name/ID is a numeric feature—the identity models use it
only to select their training pool.

## Frozen gates

All gates must pass:

1. exact panel integrity: six agents x 24 games x two cutoffs = 288 examples, with 192 discovery
   and 96 confirmation examples;
2. identity history confirmation error is at least 10% below population state retrieval;
3. identity history is at least 5% below identity mean;
4. identity history at turn 100 is at least 10% below population state retrieval;
5. identity history beats population state in at least four of six per-agent confirmation slices;
6. identity history wins at least 55% of paired confirmation examples versus population state.

## Stop rule

- **Pass:** distill one closed-loop controller for the best-supported repeated agent first, then
  require exact held-game trajectory coverage before adding it to an ambiguity set.
- **Fail:** identity plus these aggregate observables still cannot supply a useful simulator.
  Close proxy reconstruction and return to direct causal candidate experiments using field replay
  diagnostics only, not local acceptance.

No game creation, submission, candidate source, or resident change is allowed.
