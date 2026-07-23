# D118a soft-value q6 ranker and state gate — fit result

Date: 2026-07-22  
Decision: **fit gate fails narrowly; no validation collection; held remains sealed**

## Reproducibility and fit

D118 uses one CPU training thread and is byte-exact across two complete runs. Both produce fit
artifact SHA-256 `b2cf292f93c25f4c3947582cddccbf6c841d1c4638d1bff47417b3439212e7a9`
and identical model hashes. The 20-worker game collector is never opened because the fit gate
fails, so validation seeds `9,843,670--9,843,685` and held seeds `9,843,700--9,843,715` remain
unused.

Soft value targets improve ranking over D117, but not enough for the unchanged prospective
structural standard. Mean proposal regret is `18.213--19.884` against a maximum of 18; within-ten
coverage is 41.35%--43.39% against 45%. Exact-best rates reach 19.95%. The separate gate remains
healthy at 64.81%--65.60% balanced accuracy with both recalls above 60%.

## Policy frontier

Policy-level fit value improves substantially. Seed 11803 at offset `0.5` reaches `+3.562`, 36.72%
strict gains, 59.38% activity, all eight positive families, both folds positive, and a `+1.031`
family floor. Seeds 11801 and 11804 at offset `0.5` also exceed `+3` with seven positive families
and nonnegative floors. These candidates pass every fit-policy gate but fail the model's regret and
within-ten gates.

Broader offsets reach `+6--+8` with high strict rates, but exceed the 85% activity ceiling. The
failure is therefore no longer lack of signal or gate timing; it is the remaining proposal-regret
floor under the frozen 40-epoch ranker.

## Conclusion

Close D118 without moving the observed regret thresholds. The soft objective is a clear
improvement and should be retained. Its rank cross-entropy is still decreasing at epoch 40 and
remains about 0.62 nats above target entropy, so the next isolated test should change only training
horizon: 80 deterministic single-thread epochs, same 6,626 parameters, temperature, seeds budget,
offsets, fit gates, and conditional validation range. Increase capacity only if the longer fit
still misses the unchanged structural gate.

Fit artifact SHA-256: `b2cf292f93c25f4c3947582cddccbf6c841d1c4638d1bff47417b3439212e7a9`  
Frozen manifest SHA-256: `db8d573d503da696b3ac1286f95ee77e59f01d60148c61c215d50079aeb29905`
