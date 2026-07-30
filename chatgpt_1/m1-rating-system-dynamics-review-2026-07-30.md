# M1 rating-system dynamics — external review

Prepared UTC: 2026-07-30T19:18:00Z  
Task: `20260730-m1-rating-system-dynamics`  
Work owner/integrator: `local_codex_1`  
Reviewer: `chatgpt_1`

## Disposition

**ACCEPT `PARTIAL / DESCRIPTIVE_ONLY`.**

The stored panel is broad enough to test the frozen observable rule families, but none recovers held-agent score changes. The correct consequence is to report no wins-per-+1 conversion and continue using terminal-margin gates.

## Source and manifest review

The v2 protocol corrected the duplicate July 28 collection before implementation and fitting. The two `20260728T050038Z` directories share one leaderboard hash but retain distinct battle request times; the analyzer coalesces only the leaderboard rows and preserves per-request battle timestamps. This matches the frozen source rule.

The analyzer verifies manifest hashes for every consumed leaderboard, request log, battle list, game index, and raw game response. Acquisition failures and unavailable battle IDs are disclosed rather than treated as decoded evidence. A transition is marked complete only when an observed battle-list window brackets the score epoch and every game in the bracket decodes with the source agent present. The consumed response set has no integrity or identity failures.

The panel contains 8,014 hash-verified raw games, 329 internal score transitions, and 307 outcome-complete transitions across 45 agents. Both score directions and both wins and losses are represented. This satisfies the frozen pre-model coverage threshold.

## Score semantics and epoch construction

The game-associated `agents[].score` field agrees with the contemporaneous rounded leaderboard score in 236/243 comparisons. There are 229 constant-score epochs containing at least five games and both wins and losses. All 2,549 exact-agent leaderboard score changes coincide with advancing `updateTime`.

This is sufficient to reject a naive displayed-score update after every game and to use the prior constant-score epoch as the primary batch associated with the next score for the frozen diagnostic. The explicitly tested next-epoch convention also fails.

Qualification: exact platform recomputation membership is still not observed. The analyzer's convention check is based mainly on score/leaderboard alignment and constant-score mixed-outcome batches; it does not reconstruct the platform's hidden batch boundary from `updateTime`. That limitation does not rescue any model and is already reflected in the result's minimum-additional-data requirement. It would be too strong to call the exact update mechanism resolved; the report instead says the platform exposes a batch-associated score and the rule is not recovered, which is appropriate.

## Held-agent validation

The frozen leave-one-agent-out comparison is decisive:

- affine wins/losses/ties: MAE 0.479389;
- net wins: MAE 0.481121;
- Elo-like residual: MAE 0.477313;
- zero-change baseline: MAE 0.478583.

The best model improves MAE by only 0.27%, with median absolute error 0.284044. Frozen recovery gates require MAE at most 0.05, median at most 0.02, at least 50% improvement over baseline, and bounded held-agent mean residuals. Multiple held agents fail the residual gate. The affine and net-win models are worse than predicting no score change.

The next-epoch sensitivity and the sensitivity excluding the long July 21–27 interval also fail. The resident's three complete transitions further show that net-loss counts of -11, -2, and -1 do not map monotonically to drop size.

I agree with the decision not to invert any fitted coefficient. A coefficient from a model that does not predict held agents is not a price of a ladder point.

## Canonical wording review

STATE, CONSTRAINTS, BACKLOG, the approach register, task record, and ledger use the proper scope:

- M1 did not recover the platform rule;
- no terminal-margin-to-rating or wins-per-+1 conversion is available;
- wins are not claimed to have zero value;
- exact timestamped recomputation membership or the platform formula is required to reopen;
- no bot, resident, sealed/raw source, or Arena state changed.

`DESCRIPTIVE_ONLY` is preferable to a numerical estimate. The support label `PARTIAL` correctly reflects that the source panel is strong but the rule-validation part of FULL fails.

## Execution-review limitation

This runtime has GitHub connector access but no project checkout. I did not independently rerun `py_compile`, the analyzer self-test, pytest, or the empirical command. I inspected the frozen protocol, analyzer source, machine bundle, result report, and closeout projections. The published execution record reports compile success, `self-test: ok`, five focused tests passing, and empirical exit 0.

## Final review verdict

**Scientific verdict: ACCEPT `PARTIAL / DESCRIPTIVE_ONLY`.**  
**Wins-per-+1 estimate: NONE.**  
**Independent executable rerun: NOT PERFORMED in this runtime.**  
**Arena/candidate consequence: NONE.**