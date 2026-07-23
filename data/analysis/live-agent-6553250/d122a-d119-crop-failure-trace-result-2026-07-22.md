# D122a D119 crop-failure trace — result

Date: 2026-07-22  
Decision: **replace absolute crop success with relative control safety in future protocols**

D122 exactly reproduces the four D119 models and traces all 24 frozen policy paths. The first
attempt stops before writing a result because the tracer assumes crop failures follow an action;
the observed trace has no selected action. A separately locked mechanics repair represents that
case explicitly and leaves all data, models, policies, and attribution fields unchanged.

There are exactly two unique crop-failure tasks, and every one of the 24 policies has the same two:

- map `9,843,725`, seat 0, `silver_boss`; and
- map `9,843,725`, seat 1, `silver_boss`.

In both tasks D40 itself creates zero crops and the q6 collector exposes zero decision boundaries.
Every policy is therefore forced to control (`choice = null`); there is no selected intervention,
failing root, unsafe proposal, or safe q6 alternative. The 1,278/1,280 crop rate in D121 is not a
policy regression. A 100% absolute gate is impossible on this panel even for exact D40.

Future protocols should mirror workforce safety and require crop performance relative to control,
for example no additional crop failures or `policy_crop_rate >= control_crop_rate`, while still
reporting the absolute rate. This semantics correction alone does not rescue D119: after ignoring
the impossible absolute crop gate, none of the 24 retrospective policies satisfies all remaining
mean, strict, activity, family, directional-score, and workforce criteria.

The next model hypothesis remains task-balanced act/wait calibration. D119's useful broad policies
exceed 85% activity, while moderate policies stop just below `+2`; the training loss currently
weights every root equally, overrepresenting tasks/opponents with many boundaries. Test
task-balanced root weights retrospectively before buying fresh validation data.

Original lock SHA-256: `945b90f5f15c6554a11f71680566e58d97f395da8bdb9ad78a026b99fadc8e5f`  
Repair lock SHA-256: `f9af5570fe983988e0e142ec13438ad7060d9ad9673f5074d617f2b80374c8e9`  
Result SHA-256: `0f667bbb70b841b525e9795ba1a0dd9c8421baa3bd7800763dcf84ef26f93138`
