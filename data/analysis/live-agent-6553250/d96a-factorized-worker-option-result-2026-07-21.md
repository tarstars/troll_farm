# D96a factorized worker-option population — result

Date: 2026-07-21  
Status: integrity pass; representation activity and incremental-headroom fail

## Verdict

Close per-worker factorization over D40's four `balanced` / `harvest` / `renew` / `fell`
semantic modes. Do not train PPO, CEM, imitation, a recurrent actor, or a wider scorer on this
interface.

The factorized population is mechanically exact, safe, active, and valuable relative to direct
D40. It does not, however, improve enough over the already-established D61 global-mode function
class. Its factor oracle gains `+58.383` margin over D40, while D61's global oracle already gains
`+57.586`; the net increment is only `+0.797` against a frozen `+5` requirement. In parallel, only
33/64 random residual policies create mixed per-worker Rate batches in at least 25% of tasks,
versus the required 48/64.

This is not a mechanics or renewable-safety failure. It says that worker identity and shared job
state do not become a sufficiently different controller while the action vocabulary still reduces
each worker to the same four coarse job kinds.

## Integrity and reproducibility

Both 20-worker runs cover exactly 197 policies x 128 tasks = 25,216 rows. They are byte-identical,
with SHA-256
`a42536705f05e816a20e12b4477675bc685f0b6f4d515659104354ea83d1b53d`. Run A completed in
662.823 seconds and run B in 665.118 seconds, using about 18.8 effective CPU cores throughout.

All frozen nesting and mechanics gates pass:

- all 69 global policies reproduce the corrected D61 matrix on every common field;
- all 64 zero-residual policies reproduce their `linear_XX` parents on every terminal, action,
  option, and worker-accounting field;
- the 128 factor policies reconstruct exactly from PCG64 seed 9601;
- reward, action-plane, mode, worker-feature, and mixed-batch accounting have zero failures; and
- there are zero illegal direct commands, provenance failures, deposit-prediction failures,
  worker-cap violations, nonfinite terminal values, or zero option hashes.

The focused release tests pass 3/3, including complete-episode zero-residual parity.

## Representation activity and safety

Most activity gates are strong:

| Gate | Result | Required | Verdict |
|---|---:|---:|---|
| Crop creation in every random-policy task | 64/64 policies | 64/64 | pass |
| Worker-three retention within ten points of D40 | 64/64 | >=48 | pass |
| Action hash changed in at least 10% of tasks | 63/64 | >=56 | pass |
| At least three requested modes | 59/64 | >=48 | pass |
| At least two modes for ordinals zero and one | 64/64 | >=48 | pass |
| Mixed Rate batch in at least 25% of tasks | **33/64** | **>=48** | **fail** |
| Fixed-policy mean-margin span | 60.766 | >=25 | pass |

Direct D40 and the factor oracle both reach worker three in 92.97% of tasks. The factor oracle
creates a crop in 128/128 tasks. Therefore the failed mixed-batch gate is not caused by losing the
economy or workforce; many sequential worker scores simply collapse back to a common mode inside
the same batch.

## Whole-game headroom

The factor oracle is strong against D40:

| Metric | Result | Required | Verdict |
|---|---:|---:|---|
| Mean margin delta | +58.383 | >=+50 | pass |
| Strict improvements | 127/128 = 99.22% | >=85% | pass |
| Worst opponent-family gain | +27.750 | >=+15 | pass |
| Mean own-score delta | +26.773 | >=0 | pass |
| Mean opponent-score delta | -31.609 | <=0 | pass |
| Worker-three reach | 92.97% | >=85% | pass |
| Crop creation | 100% | 100% | pass |
| Random policies with at least two strict oracle wins | 28 | >=12 | pass |

But the required comparison is incremental to D61, not another rediscovery of D61's option value:

| Oracle | Mean margin |
|---|---:|
| D61 global option oracle | 112.234 |
| D96 factor-random oracle | 113.031 |
| Factor minus global | **+0.797** |
| Frozen minimum | **+5.000** |

Factor rows strictly beat the global-oracle margin in 56/128 tasks, comfortably passing the
24-task breadth gate. Across all tasks the paired factor-minus-global distribution has 56
improvements, 23 ties, and 49 regressions; positive deltas sum to +650 and regressions to -548.
The useful alternatives are therefore complementary but not a stronger stand-alone initialization.

For diagnosis only, an oracle allowed to choose from the union of both populations would add
`+5.078` over the global oracle. That was not the frozen factor oracle and cannot amend the result:
it relies on hindsight selection between two populations rather than demonstrating that random
worker residuals retain global behavior while adding stable role separation. No union arm or
random label is selectable.

Ten fixed random factor policies exceed D40's mean margin descriptively. The best absolute fixed
mean is `61.227` for `factor_random_30`, but it is `-0.984` relative to its matched global parent.
The largest matched-parent improvement is `+17.516` for `factor_random_55`; it too is an inspected
random arm and cannot become a policy or initializer.

## What the failure localizes

D95 observed concurrent material domains and joint TRAIN funding. D96 supplied worker identity,
cargo, active jobs, predicted deposits, and role history, but its actions could only request a job
kind. It could not express which PLUM/LEMON/APPLE/IRON source, concrete crop lineage, target, or
collision-safe pair of jobs the workers should take. The experiment therefore separates state
factorization from action factorization: more worker context is insufficient when the action
vocabulary remains global and coarse.

The next eligible discriminator is a bounded, target-aware **joint concrete-job continuation** on
exact D40. It must evaluate two collision-safe worker assignments together at one natural batch
boundary and then return to D40. This is distinct from:

- D35's private-farm root bundles and resident overlays;
- D41/D42's single-worker rank-one deviation classifiers;
- D79's unbounded all-Rate spatial scorer;
- D82's threatened-own-crop-only response; and
- D96's four semantic modes.

Before any learner, that continuation must prove broad causal value beyond both the best
single-worker arm and exact D40 while preserving crops, workforce, transactions, and target
collisions. No D96 weights, random winner, result-dependent scale, fresh candidate, TestSession,
submission, Arena action, or resident replacement is authorized.

## Reproducibility anchors

- frozen protocol SHA-256:
  `49a1469e58bee8519197e82b88b6c34a9416e89fa56563172b82faed743dd5c7`;
- population generator SHA-256:
  `51c5a9c518d84e8bf685623590d696dd0aab33c2a661139f9d5276f9c762b459`;
- evaluator SHA-256:
  `6e3b3c0ff75f9d4118e1243323e76467855882d1439fa99d890da14a4c296291`;
- factor population SHA-256:
  `3fbe912c30bae723f6d5f27d323b2a7befac2c9758f75928a62c31e27144a900`;
- analyzer SHA-256:
  `22b7c0a053cc21db54ca23306b866692239533a6d9b888a7d8e12eb66e0175de`;
- machine result SHA-256:
  `bfb28c228ee7559b3b77aff435a75857324c9312bfe0a53fe4b0dc5dc3688664`.

Artifacts:

- `d96a-factorized-worker-option-population-{a,b}-9801000-9801007.tsv`;
- `d96a-factorized-worker-option-result.json`;
- `cgauto/make_d96a_factorized_worker_population.py`;
- `cgauto/analyze_d96a_factorized_worker_options.py`; and
- `rust/src/bin/d96_factorized_worker_option_population.rs`.
