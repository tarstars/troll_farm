# D149b state-conditioned joint cross-fit — result

Date: 2026-07-23  
Decision: **close exact-best-pair imitation**

Two full 32-fit selections are byte-identical at SHA `b556d387...`. No state-conditioned seed is
eligible, so there is no full fit, checkpoint, candidate, or reserved-panel access.

Adding all 64 state features does not improve exact winner prediction. Best held rank accuracy is
9.54% (seed 14903), versus D149a's 9.79% and the same 6.43% random baseline. First-stage accuracy is
12.37%; second-stage accuracy is 6.70%. Training rank accuracy remains only 19.88% for that seed.
No held task reproduces both actions under any seed.

Gate behavior also remains in the same regime: 58.45%--59.13% balanced accuracy, 42.78%--45.49%
act recall, 72.44%--75.28% wait recall, and 90.79%--93.09% inactive-prefix rejection. This rejects
the missing-state hypothesis and, under the frozen protocol, closes further width or stage-head
tuning on the one-hot label.

The likely defect is target entropy and winner's curse. Each task labels exactly one maximum pair
from 64 sampled schedules, even when multiple actions are near-tied; only 388 active tasks provide
second-action labels. The model is being asked to identify one noisy argmax rather than learn
return. Next audit whether the 66,560 population episodes provide repeated action coverage on the
2,508 replayed candidate states. If sufficient, aggregate terminal returns by first and conditional
second action to create value/near-tie targets. If conditional second coverage is insufficient,
collect broader counterfactual feature replays rather than train another classifier.

Result JSON SHA: `3047a8b5...`.
