# Persistent job-bundle oracle — result, 2026-07-19

## Verdict

**Reject the resident-local one-job representation.** The experiment passed every integrity check
and seven of eight frozen representation checks, but the mean gain on roots where the oracle chose
a job was **+18.584**, below the precommitted **+20.0** boundary. The boundary is not retuned: no
selector, larger target catalog, checkpoint change, or production candidate is authorized from this
grammar.

This is a near-threshold rejection, not evidence that persistent work has zero value. The retained
lesson is narrower: isolated `BANK`, `FELL_BANK`, and `HARVEST_BANK` redirections do not provide a
strong enough teacher. The next representation must control the complete economy—multiple workers,
renewal, training, production, banking, and opponent-loop pressure as one plan.

## Frozen panel and integrity

- consumed seeds: 0--9 only;
- seats: both;
- opponents: all eight fixed local families;
- resident games: 160;
- roots: 480, one first eligible root at or after turns 50, 100, and 150 per game;
- non-control options: 3,260; total rows: 3,740;
- exact resident controls: 480/480 equal uninterrupted terminal outcomes;
- job construction: only a unit whose resident command was MOVE or WAIT was redirected;
- repeat: byte-identical SHA-256
  `f55a9d618608eedc214d0a580d6d70fa15cb2563a72786aee4fd342da8d5b4af`;
- completion: 2,887/3,260 options (88.56%); remaining branches ended by explicit invalidation or
  timeout;
- implementation tests: seven Rust tests and three analyzer tests pass.

The first integrity run exposed a state-reconstruction defect: several sparring opponents retain
sticky targets. Replaying their prior observations into a fresh controller restored exact terminal
control identity before any frozen result was accepted.

## Frozen gate

| Check | Boundary | Result | Pass |
|---|---:|---:|:---:|
| Integrity | all checks | all checks | yes |
| Eligible roots | >=240 | 480 | yes |
| Non-control options | >=2,400 | 3,260 | yes |
| Non-control selection | >=10% | 59.58% | yes |
| Mean oracle delta, all roots | >=+8.0 | +11.073 | yes |
| Mean delta, selected roots | >=+20.0 | **+18.584** | **no** |
| Job-kind breadth | two kinds with >=10 roots | 3/3 | yes |
| Opponent breadth | six means >=+3.0 | 8/8 | yes |
| Weakest opponent mean | >=0 | +4.567 | yes |

Formal decision: **fail**. Seeds outside 0--9 remain unopened for this branch.

## Analysis at different abstraction levels

### Primitive and job level

The completion representation is meaningful but heavy-tailed. Control wins ties, yet a job is
strictly better at 286/480 roots. The all-root oracle delta has median +4, p75 +16, p90 +33, and
maximum +114. Among selected roots the median is +11.5, well below the +18.584 mean; a small number
of supply cascades raise the average.

`FELL_BANK` dominates selection: 179 roots, mean +20.972, composed of +5.536 own score and -15.436
opponent score. `HARVEST_BANK` is selected 76 times at +15.289; immediate `BANK` is selected 31
times at +12.871. All three verbs can repair local mistakes, but felling carries the only
above-threshold job-kind mean and obtains most of its value through downstream opponent suppression.

### Score-flow level

Across selected roots the average decomposition is +5.993 own score and -12.591 opponent score.
Of 286 selections:

- 110 improve own score and suppress the opponent;
- 91 improve own score without opponent suppression;
- 85 are profitable only through opponent suppression; and
- 58 reduce our own terminal score despite improving margin.

Thus a productive-score-only objective is incomplete, but pure denial is also unsafe. The learned
quantity must be the coupled terminal opportunity cost of both economies.

### Temporal level

Leverage decays with the checkpoint:

| Root | Selection rate | Mean oracle delta | Selected-root mean |
|---:|---:|---:|---:|
| 50 | 65.0% | +13.969 | +21.490 |
| 100 | 61.25% | +11.163 | +18.224 |
| 150 | 52.5% | +8.088 | +15.405 |

Only the turn-50 slice clears the selected-root magnitude boundary. Early work changes later asset
availability and rival supply; after turn 100, an isolated job has progressively less ability to
repair the economy trajectory.

### Map, seat, and opponent level

Both seats are positive (+10.179 and +11.967), and every opponent family is positive. Family means
range from +4.567 (`sched_bot`) to +19.117 (`compact_gold` and `gold_elite`). Breadth is not the
failure.

Map concentration is material: seed means range from +4.646 to +21.104. Seeds 2, 7, and 8 carry
the largest gains, and the maximum branches are opponent-supply collapses of +80 to +114. This
explains why the broad sign rate coexists with a selected-root median of only +11.5.

### Controller and architecture level

The resident does leave local persistent work on the table, but a terminal hindsight selector is
non-deployable and its teacher is not strong enough under the frozen gate. Adding features or
fitting a classifier would optimize selection error against an already rejected upper bound.

The missing abstraction is a **whole-economy plan**, not another cell score. A viable option must
coordinate worker roles and preserve or create future work: harvesting currencies, training,
planting renewable supply, banking, felling rival supply, and returning workers to productive
locations. This also matches the earlier evidence that strong bots' extra workers are funded by
ongoing multi-worker cycles rather than an isolated TRAIN or denial detour.

## Retained hypotheses and priority

1. **Complete-economy plan oracle.** Test whole-controller plan bundles from an early state, with
   all workers coordinated and terminal continuation value. This is the only immediate successor
   authorized by the protocol.
2. **Dual-economy terminal objective.** Represent own production and opponent renewable supply
   separately; 68.2% of selected local jobs include opponent suppression and 20.3% sacrifice own
   score.
3. **Early macro allocation.** Concentrate the next representation around the first stable
   post-opening decision near turn 50; late target repair has lower ceiling.
4. **Observable cascade state.** Future selection must identify rival renewable-stock and worker
   funding momentum from game state, not opponent labels or local-simulator hindsight.

## Artifacts

- protocol: `bundle-job-oracle-protocol-2026-07-19.md`;
- runner: `rust/src/bin/bundle_job_oracle.rs`;
- analyzer: `cgauto/bundle_job_oracle.py`;
- tests: `tests/test_bundle_job_oracle.py`;
- primary/repeat: `bundle-job-oracle-0-9.tsv`, `bundle-job-oracle-0-9-repeat.tsv`;
- machine-readable report: `bundle-job-oracle-0-9.json`.

The arena resident and submitted source were not changed.
