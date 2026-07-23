# D117a factorized q6 ranker and state gate — fit result

Date: 2026-07-22  
Decision: **fit gate fails; no validation collection; held remains sealed**

## Fit outcome

D117 reuses the 1,323-root / 21,374-arm fit-only matrix and trains four 6,626-parameter models.
The separate state gate works: balanced act/wait accuracy is 64.42%--65.03%, act recall is
58.13%--61.41%, and wait recall is 67.64%--70.72%. Every gate clears its prospective structural
threshold.

The proposal ranker remains below the frozen exact-choice gate. Top-1 accuracy is 16.10%--18.22%
on all roots and 17.81%--19.69% on act roots, versus required 20% for both. Consequently none of
24 model/offset pairs is fit-eligible and no selection lock, validation data, or checkpoint is
created. Seeds `9,843,670--9,843,685` and global held seeds `9,843,700--9,843,715` remain unused.

Policy-level fit evidence is directionally stronger than exact top-1. Seed 11703 at offset 0 has
`+2.309` mean, 44.14% strict gains, 80.47% activity, six positive families, both folds positive,
and a `-2.500` floor; it passes every fit-policy gate but fails both frozen rank-accuracy gates.
At offset `-0.5`, several seeds reach `+2.3--+4.6` but exceed the 85% activity ceiling.

## Reproducibility finding

The frozen 20-thread CPU optimizer is not byte-stable for seed 11701. Repeated full fits produce
different seed-11701 weight hashes (`05bc5d71…`, `9dd5d602…`, `6a96052f…`) and full result hashes
`0dc395a4…`, `e5d8ef55…`, and `fae9da6f…`; seeds 11702--11704 remain exact and the terminal
fit-fail decision never changes. Three independent one-thread seed-11701 fits are byte-identical
at model hash `46e8568a…` with identical metrics. Future CPU learner protocols should use one
training thread while leaving the 20-worker exact collector unchanged.

## Head-level decomposition

On fit data, the learned ranker with perfect DP timing yields `+8.17--+8.97`, 58%--61% strict
gains, all eight positive families, and a `+3.06--+3.84` floor. Conversely, perfect proposal
ranking with the learned state gate yields `+20.65--+21.32` at offset 0 and `+27.70--+29.07` at
broader offsets, with all families strongly positive. The state gate is therefore not the main
bottleneck.

The learned ranker's mean proposal regret is about 20 points; only 18%--19% of choices are exact,
28% are within five points, and 39%--40% are within ten. Exact top-1 discards useful near-tie
structure and is a poor sole fit proxy.

## Conclusion

Close D117 at its prospective fit gate. Keep the factorized runtime and state gate, but replace
one-hot proposal ranking with value-aware soft listwise targets derived from all exact proposal
advantages. A temperature tied prospectively to the observed target scale can reward near-optimal
arms and reduce regret. Gate the next fit on mean regret and within-ten coverage, plus policy value,
and require one-thread deterministic optimization before any fresh validation collection.

Current fit artifact SHA-256: `fae9da6ffdea2dbc9497f95886f7240365e164170d5b7551abb50ada10aa4903`  
Frozen manifest SHA-256: `ba67b7ca681d7d11c4ceec897dc2c48c3255328913067a9674afd52771a62495`
