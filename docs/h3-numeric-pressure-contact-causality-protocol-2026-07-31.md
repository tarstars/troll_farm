# H3′ numeric-pressure contact-causality protocol — 2026-07-31

## Question

Does the resident's opponent-crop contact hazard fall specifically after a successful
opponent third-worker TRAIN, including while the resident is still nonnegative, or is
the previously observed 41.3%→35.3% coverage drop only a symptom of game composition
and already losing?

This is a read-only temporal-ordering audit. It does not reopen the falsified “no-loop
quartet” causal-peer claim, Phase 21 opponent-crop scoring, harvest-before-chop, H4 bill
denial, H7′ contention, or M5 duration conditioning. It cannot establish intervention
value.

## Frozen population

Use only the 200 exact resident games named in
`d159a-current-resident-all-finished-effect-refresh-raw.json`, SHA-256
`97dc82a730b5a691f2bf63036834b1a9ed23bc186b00d09b874ac092efddf443`.
The accepted D159 result has SHA-256
`bd3fe4571aec423cdb57d514a2f610c0dcfe9845099b5500a6721e98d72965ac`
and records exact identity and zero unknown diff updates. Read only the named raw games
and trajectories. Do not enumerate or open any other game.

The scaled cohort has an exact successful opponent TRAIN with `n_before=2`; the event
turn is the first such TRAIN. The no-scale pool has no successful opponent third-worker
TRAIN. Do not classify from terminal workforce alone.

## Exact risk and timing

For every opponent crop generation, use the frozen D159 birth, death, and first resident
contact turns. A crop is at risk on a turn from birth through the earliest resident
contact, death, or game end. A first resident contact contributes one event.

TRAIN resolves after CHOP and the new worker cannot act until the next turn. For event
turn `T`:

- primary pre window: `T−49 … T`;
- primary post window: `T+1 … T+50`;
- pre-loss pre window: `T−19 … T`;
- pre-loss post window: `T+1 … T+20`.

Require complete windows. The pre-loss subset additionally requires the permanent
negative crossover strictly after `T+20`, so every post-pressure risk turn occurs before
permanent loss. Report raw first-contact events, at-risk crop-turns, unsmoothed hazards
per 1,000 crop-turns, and the Jeffreys-smoothed rate
`(events+0.5)/(exposure+1)` used only for finite ratios/bootstrap replicates.

Also reproduce eventual pooled contact coverage for scaled and no-scale games, with a
game-cluster bootstrap interval. That is the historical descriptive claim, not the
causal estimand.

## Frozen matching

For each complete-window scaled game, choose the nearest no-scale game with replacement:

- exact resident seat;
- control duration at least `T+50`;
- distance uses only frozen pregame/prematch fields, standardized over the 200 games:
  opponent ladder score, opening fruit total, tree-health total, tree count,
  shack-door distance, own-private fruit, opponent-private fruit, and
  water-adjacent-cell count;
- ties break by game ID.

Never match on terminal margin, win/loss, game duration beyond the follow-up requirement,
terminal workforce, crop outcomes, contact, crossover, or any post-event feature.
Report standardized mean differences before and after matching, unique controls, and
maximum control reuse. Every matched covariate must have absolute post-match SMD ≤0.25.

## Estimand and uncertainty

For scaled and matched control windows compute post/pre contact-hazard ratios. The
difference-in-differences ratio is:

`(scaled_post / scaled_pre) / (control_post / control_pre)`.

Values below one mean a pressure-specific decline beyond the same-turn secular change in
no-scale games. Compute it for the primary 50-turn cohort and the 20-turn pre-loss subset.
Use 10,000 deterministic matched-pair/game-cluster bootstrap replicates, seed 20260731,
preserving each scaled game and its selected control as a pair. Report percentile 95%
intervals and raw count/rate components. Outcome/margin associations are descriptive
only.

## Integrity and materiality gates

All integrity gates must pass:

1. exact 200 unique D159 IDs, frozen hashes/source identity, all named files, all games
   decoded, zero unknown updates, and zero outside reads;
2. exact successful TRAIN transitions and resident seat for every game;
3. at least 40 complete primary matched pairs covering at least 12 scaled opponent
   identities and both resident seats;
4. at least 20 complete pre-loss pairs covering at least 8 scaled opponent identities
   and both resident seats;
5. every post-match covariate absolute SMD ≤0.25;
6. nonzero contact events and risk exposure in every aggregate event-study cell;
7. deterministic repeated output.

Return `TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY` only if all are true:

- scaled eventual contact coverage is at least 5 percentage points below no-scale
  coverage and the game-cluster bootstrap upper bound is below zero;
- primary matched DiD hazard ratio ≤0.80 and its 95% upper bound is below 1.0;
- pre-loss matched DiD hazard ratio ≤0.80 and its 95% upper bound is below 1.0.

Passing establishes a temporally ordered observational signal only. A successor must
freeze three arms—conditioned change, identical always-on change, and unchanged
control—and prove the conditioning is load-bearing before any candidate claim.

## Frozen verdicts

- `TEMPORALLY_ORDERED_PRESSURE_SIGNAL_PREFLIGHT_ONLY`: every integrity/materiality gate
  passes; request a separate causal/value protocol with the mandatory always-on arm.
- `NO_LOAD_BEARING_NUMERIC_PRESSURE_SIGNAL`: integrity passes but at least one
  materiality gate fails; close H3′ without a targeting change or experiment.
- `UNIDENTIFIABLE`: timing, risk exposure, matching support, or cohort coverage fails.

## Stop rules

Stop after analyzer/tests, compact JSON/report/manifest, canonical closeout, and peer
handoff. Do not edit source, define a score bonus, simulate alternative outcomes, open a
panel, read unlisted games/maps, create a candidate, submit, or touch Arena.
