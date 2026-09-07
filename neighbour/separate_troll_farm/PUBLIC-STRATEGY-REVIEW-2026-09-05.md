# Primary-source strategy cross-check

These are public author descriptions, not executable replicas or fresh performance measurements.
They inform hypotheses; they do not certify our implementation or the present ladder rank.

September 5 follow-up after restoring V439: the earlier comparisons below referred to `next_bot`.
V439 already has joint immediate-action selection and near-shack economy code. Its new experimental
planner adds late-game rollouts; neither implementation is an executable reproduction of an author.

Re-reading Putibuzu's original post confirms a material remaining difference: his minimum second
worker includes harvest power one, while V439's `opening_options` enumerates harvest power zero.
He also describes broader action combinations, several rollout horizons, deeper action search,
and a leaf value including future tree production. Our current test begins only at turn 220,
uses three V439-generated roots and values banked/carried resources. These are concrete scope
limitations, not evidence that copying a worker specification would improve our bot. No public
implementation link was identified in that post.
[Author's original description](https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/5).

Putibuzu describes a stronger minimum second-worker target, a near-shack plant/chop/drop economy,
a protected watered-apple harvest loop, and multi-horizon simulation with joint action choices.
Our controller has neither that complete economic lifecycle nor that action search. Treating it
as an equivalent two-worker policy would be incorrect.
[Author's postmortem](https://forum.codingame.com/t/spring-challenge-2026-troll-farm-feedback-strategies/208241/5).

Yann Moisan describes explicitly predicting tree growth and enemy chopping, then selecting the
best compatible pair of worker actions. Our retained greedy reservation order and static trip
estimates differ, even where we reuse the same denial idea.
[Author's postmortem](https://www.yannmoisan.com/spring-challenge-2026-postmortem.html).

Delineate's winning approach separates learning to execute a chosen build order from learning
which order to choose, then jointly fine-tunes on final score differential. Deployment combines
the worker action proposals to avoid conflicts; it is not a hand-coded fixed workforce.
The writeup motivates examining reusable neighboring training work, not assuming a new training
run is cheap or guaranteed to succeed.
[Author's architectural account](https://gist.github.com/delineate/93ba9d48102e442e764db39d85ac44a3).

No public implementation was copied in this review. The negative fresh confirmation stays
closed; it must not become an implicit tuning set or justification for a parameter sweep.
