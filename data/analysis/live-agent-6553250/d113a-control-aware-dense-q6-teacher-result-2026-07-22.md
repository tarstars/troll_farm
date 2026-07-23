# D113a control-aware dense q6 teacher — result

Date: 2026-07-22  
Decision: **full mechanics, signal, and oracle-safety pass; open supervised scorer fit**

## Execution and support

The unchanged snapshot collector evaluates untouched seeds `9,843,200--9,843,207`, both seats and
all eight opponents. It emits 128 exact D40 baselines, 736 roots, and 11,980 one-deviation arms in
594.52 seconds (`20.151` arms/s). All frozen inputs, root grids, state/action features, paired
gains, one-use counters, reward identities, and mechanics pass; all failure counters are zero.

116/128 tasks (90.625%) expose at least one paired q6 root, clearing the frozen 90% support floor.
The other 12 are included as forced D40 control with zero gain and no arm labels.

## Exact one-use oracle

Across all 128 tasks, including forced controls, the exact proposal oracle achieves:

- `+36.766` mean margin gain and 89.844% strict improvement;
- `+25.039` own-score gain and `-11.727` opponent-score delta;
- all eight positive families, with means from mybot `+18.313` to gold_adaptive `+61.813`;
- 100% crop creation and worker-three reach exactly equal to D40 at 89.844%; and
- 86 joint, 29 single-worker, and 13 control selections.

The first-boundary-only oracle already gains `+30.875`; later boundaries add `+5.891`. The useful
signal is therefore both proposal choice and calibrated waiting, not merely wider support.

## Backward teacher

Backward dynamic programming marks 344/736 roots (46.739%) as act-now and 392 as wait. Of 11,980
arm targets, 1,435 (11.978%) are positive, 10,334 (86.260%) negative, and 211 zero. Targets range
from `-250` to `+115`, with standard deviation `26.000`. Every prospectively frozen signal and
oracle-safety gate passes.

## Conclusion

Dense counterfactual credit resolves the ambiguity that defeated random/evolutionary terminal
selection. Open a new-map supervised experiment in the same deployable 379-weight linear class:
fit act-now-versus-wait targets with root-balanced regularized regression, select regularization
and a fixed abstention offset on separate new validation maps, then evaluate the frozen one-use
controller closed-loop twice on untouched held maps. D113 data is evidence only and is not used to
fit or select the scorer.

Result JSON: `ee323c9d12f1a0e7f84af6961db7c76ba3bedcb0af3c31a56b6efc2f9e376e46`  
Labels: `957b43167ea7b55af084215d198f57aaf980c438ceca848fcf5021a611a5cf57`  
Frozen manifest: `22950d827b69e37f4b0696898f69b46dc6fa6efb0a542067361705f9c66d657d`
