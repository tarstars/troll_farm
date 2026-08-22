# M1 rating-system dynamics — frozen audit protocol

Frozen UTC: 2026-07-30T18:30:46Z  
Owner: `local_codex_1`  
Reviewer: `chatgpt_1`  
Task: `20260730-m1-rating-system-dynamics`

## Question

Can the stored Legend snapshots recover how ladder score responds to wins and losses? If
yes, how many additional net wins correspond to a +1 score move near resident agent
`6561795`? The audit must distinguish an identified per-game update rule from an empirical
association across discrete score recomputations.

## Frozen inputs

Read these seven complete `troll-farm-d61p-snapshot-v1` directories, in manifest completion
time order, and no later snapshot:

1. `20260721T105508Z-d61p`
2. `20260727T130712Z-d61p`
3. `20260728T050038Z-d61p`
4. `20260728T050038Z-d61p-wide21to50`
5. `20260728T110709Z-d61p-wide`
6. `20260729T021701Z-d61p-wide`
7. `20260730T021701Z-d61p-wide`

The root is supplied at execution time. A snapshot is admissible only when its manifest is
complete, has the required schema, and every consumed leaderboard, battle-list, game-index,
and raw-game file matches the SHA-256 recorded in the snapshot evidence. Raw game reads are
restricted to `cache_file` paths explicitly indexed by an admitted snapshot; source files
remain read-only.

The two snapshots completed at `2026-07-28T05:00:38Z` are separate sampling projections of
the same ladder instant, not independent score recomputations. They may add battle
visibility but must be coalesced for score-interval construction.

## Exact panel and event construction

1. Parse exact integer `agentId`, `score`, `creationTime`, `updateTime`, and rank from every
   leaderboard.
2. For each sampled agent and snapshot instant, deduplicate battle rows by integer `gameId`.
   Record whether each battle is present in the prior and next sampled lists.
3. Decode each indexed raw game's terminal `ranks` and player identities. Treat equal ranks
   as ties; do not infer outcomes from raw in-game resource scores.
4. Construct consecutive exact-agent intervals only. Record elapsed time, score delta,
   update-time behavior, visible new/dropped games, decoded wins/losses/ties, missing raw
   outcomes, and whether both endpoints sampled that agent's battle list.
5. A battle increment is **complete** only when both endpoint lists exist, no prior-list
   battle disappears, all new rows decode, and the list is not at an observed API cap.
   Otherwise it is censored. Game-id ordering may be a descriptive diagnostic but never a
   timestamp or completeness proof.
6. Intervals with unchanged `updateTime` are score-stability controls, not rating-update
   observations. An advancing `updateTime` with no complete battle increment remains useful
   for diagnosing platform recomputation but not for fitting a per-game rule.

## Identification ladder

Return exactly one support class before interpreting a model:

- **FULL:** at least 30 score-changing, outcome-complete intervals across at least 10 agents;
  at least 80% of all score-changing sampled-agent intervals are outcome-complete; both
  positive and negative score changes occur; and the selected rule meets the validation
  gates below.
- **PARTIAL:** FULL fails, but at least 20 outcome-complete update intervals across at least
  8 agents contain both wins and losses and support a stable aggregate response estimate.
- **UNIDENTIFIABLE:** fewer observations than PARTIAL, no outcome variation, or source
  integrity/identity failure.

Support describes this stored panel only. It is not upgraded by an attractive fit.

## Candidate rules and validation

Fit only on outcome-complete intervals with advancing `updateTime`. Candidate families,
ordered from least to most elaborate:

1. affine response to wins, losses, and ties;
2. net-win response (`wins - losses`) with an intercept;
3. Elo-like logistic expected result using the agent and opponent pre-interval scores,
   with a bounded grid for scale and K;
4. recomputed aggregate win-rate transforms when a stable cumulative exposure denominator
   is actually observed.

No arbitrary polynomial or agent-specific curve may be introduced. Use leave-one-agent-out
validation when at least eight agents are fit; otherwise use deterministic leave-one-interval
out validation and label it weaker. Report MAE, median absolute error, signed bias, maximum
absolute error, baseline zero-change MAE, and residuals by agent and interval.

A rule is **recovered** only if:

- support is FULL;
- validation MAE is at most `0.05` score and at least 50% below the zero-change baseline;
- validation median absolute error is at most `0.02`;
- no agent with at least three held intervals has absolute mean residual above `0.10`;
- the qualitative coefficient signs are coherent (win positive, loss negative);
- the same parameterization explains both positive and negative score changes.

Otherwise report the best model as descriptive and do not call it the platform rule.

## Wins-per-+1 calculation

Only a recovered rule earns a point estimate. Evaluate its local finite difference at score
21.76 against the empirical opponent-score distribution observed for resident agent
`6561795`, holding the loss/tie mix at the resident's observed mix. Report the number of
additional wins required for +1 and a 95% agent-cluster bootstrap interval (1,000
replicates, seed `20260730`).

With PARTIAL support, a clearly labeled descriptive range may be reported only if its
bootstrap interval is finite and stable under leave-one-agent-out deletion. With
UNIDENTIFIABLE support, report no wins-per-+1 number.

## Required diagnostics

- Source hashes and snapshot IDs; exact number of coalesced instants.
- Counts of sampled-agent intervals by endpoint visibility, update advance, score change,
  complete/censored exposure, and raw-outcome availability.
- Whether battle-list lengths behave as capped/right-censored windows.
- Duplicate-game and cross-snapshot consistency checks.
- Outcome balance and per-agent support.
- Candidate-model train and validation metrics and residual table.
- Resident-specific observation coverage.
- Sensitivity excluding the first long July 21→27 interval and excluding same-instant
  duplicate projections.
- Minimum additional collection needed if the rule is not recovered.

## Verdict and consequence

The result must say one of:

- `RECOVERED`: an exact-enough observable update rule and wins-per-+1 estimate pass;
- `DESCRIPTIVE_ONLY`: PARTIAL/FULL source support exists but rule validation fails;
- `UNIDENTIFIABLE`: stored evidence cannot price a score point.

This is a read-only audit. It cannot qualify a bot, trigger an experiment, or authorize an
Arena action. Negative or unidentifiable results are successful completion.
