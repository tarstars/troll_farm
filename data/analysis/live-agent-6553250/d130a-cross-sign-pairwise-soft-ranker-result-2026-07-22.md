# D130a cross-sign pairwise soft ranker — result

Date: 2026-07-22  
Decision: **close the coefficient-1 prospective controller; audit seed transfer retrospectively**

D130 adds one equal-root positive-vs-nonpositive pairwise logistic term to D119 while retaining the
same 6,626 parameters and unchanged runtime. Two complete executions are byte-identical.

The added objective works on its direct fit statistic. Relative to D119 seed11903's 67.69%
cross-sign pair accuracy and 46.83% positive-winner rate, D130 reaches 74.54%--76.17% and
52.38%--54.92%. It mostly preserves general proposal quality, with regret `17.609--18.126` and
within-ten coverage `44.44%--45.43%`. Seeds13002 and 13004 pass every structural and fit-policy
gate; the frozen regret selector chooses seed13002.

The selected fit policy is strong: `+5.488` mean, 52.34% strict gains, all required family/fold
gates, and a `-0.281` family floor. On consumed D126 development it collapses to `-0.047` mean,
40.23% strict gains, five positive families, and a `-11.719` floor. Norx is `-11.719`, script
`-4.844`, and mybot `-5.156`; one fold is `-0.703`. Own score rises `+1.266`, but opponent score
rises even more at `+1.313`.

This is not a structural-fit failure: the objective and policy gates admit two seeds. It is either
an objective-level transfer failure or a training-only selector failure between seed13002 and the
unscored eligible seed13004. The frozen protocol permits scoring only the selected seed, so D130
cannot answer that distinction.

Close D130 without lowering a gate, opening fresh seeds, or touching the platform. The next bounded
step is a retrospective D131 audit on the already-consumed D126 panel: reproduce all four fixed
D130 models and their training-calibrated offsets, score each once, and measure fit-to-development
correlation. This audit has no qualification authority. If no seed transfers, close coefficient-1
cross-sign ranking; if a nonselected seed is broadly stable, redesign the prospective training-
only selector before any fresh collection.

Seeds `9,843,800--9,843,815` remain untouched.

Lock SHA-256: `b0bd271c574766e16cfd2efbab64dbacc294d574313d80b0132665d07c25993b`  
Result SHA-256: `d8ef59a0dc8dcc234f883ed5ec2ad4b1551c135756260ece8c443a1d9ab3dbdf`
