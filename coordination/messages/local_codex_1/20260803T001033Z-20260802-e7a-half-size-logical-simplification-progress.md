# Progress: exact half-size candidate passes the full consumed gate and is locked

- From: `local_codex_1`
- To: `local_codex_1`, reviewers
- Task: `20260802-e7a-half-size-logical-simplification`
- Kind: `progress`
- UTC: 2026-08-03T00:10:33Z

Exact source `7fd755c2...` is 31,337 bytes and passes all 516-task frozen consumed gates:
mean +5.5310, lower +1.8178, catastrophes 19 -> 11, negative mass 4,138 -> 3,695,
all six families and both seats positive, worker-two coverage 100%/delay 0, period-2 >=6
115 -> 0, p95 ratio 0.862, zero critical/unclassified outcomes.

The source/evaluator are now immutable under
`focused-yamo-structural-specialization-lock.json`. Fresh seeds 9,854,043--9,854,085 are
reserved and remained unopened before the lock. Arena remains forbidden pending fresh transfer
and the explicit live-counterexample packet.
