# D114a supervised one-use q6 linear scorer — result

Date: 2026-07-22  
Decision: **collection/teacher pass; no linear validation admission; held remains sealed**

## Data and mechanics

D114 collects 256 training tasks with 1,323 roots / 21,374 arms and 128 independent validation
tasks with 816 roots / 13,233 arms. Throughput is 25.00 and 28.83 arms/s. Support rates are 91.80%
and 96.09%; all frozen inputs, grids, features, paired gains, identities, one-use counters, safety,
and mechanics pass with zero failures.

The teacher remains strong: train oracle `+35.977` with a `+27.031` family floor; validation oracle
`+39.055` with a `+29.313` floor. Both have all eight positive families and 100% crops. The failure
is therefore learner capacity/objective, not missing counterfactual signal.

## Linear selection

The fixed grid fits root-balanced ridge regression for two target clips, four alphas, and six
abstention offsets. None of 48 rounded 379-weight policies passes validation, so no population is
emitted and untouched held seeds `9,843,500--9,843,515` remain unopened.

The best validation mean is only `+0.336`. One version reaches 14.06% strict gains at 32.03%
activity, four positive families, and a `-2.313` floor; another has the same mean at 13.28%
activity but only 5.47% strict gains. Larger offsets become nearly or completely inert. The direct
regressor maps a high-value nonlinear oracle into weak abstention, not a useful controller.

## Conclusion

Close the single-hyperplane act-advantage fit. Do not open held maps, widen the ridge grid, move a
validation threshold, or refit on validation. Reuse only the D114 training matrix in a new
prospective nonlinear experiment; collect a new validation panel because D114 validation has now
selected the abstraction change. The next bounded class should be a small quantizable MLP trained
with root-balanced, class-balanced act-now classification, which better matches the sparse
positive decision boundary while remaining far below the 100k submission budget.

Fit result: `bcf9d49723e49c00b24d42b5364965bea1edeb245ecaf5fce5b826e335ae1f0b`  
Repair manifest: `b3768479031d4ca8b84c54a82c79bc648539036e22571b43f3f7a6c1fb59e95a`
