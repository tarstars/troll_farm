# D129a decoupled proposal-safety composition — result

Date: 2026-07-22  
Decision: **close independent arm-safety composition; target relative cross-sign ranking**

D129 exactly reproduces D126's seed11903 ranker/state gate, trains four independent 6,097-
parameter class-balanced safety heads, and scores the frozen 60-cell composition matrix on fit and
the consumed D126 panel. Two complete executions are byte-identical. The study is retrospective
only and produces no checkpoint.

All four safety heads learn the fit labels. At their natural zero threshold, positive recall is
71.27%--77.31%, nonpositive recall is 63.95%--70.54%, and weighted BCE is 0.567--0.572. Training-
calibrated 70% specificity retains roughly 71% positive recall but only about 27% approved-arm
precision. At 98% specificity, precision rises only to 48%--51% while positive recall falls to
12%--13%.

This apparent fit signal does not transfer into closed-loop value. None of 60 development cells
passes the unchanged D126 gates. The cross-seed stable cell (`winner_veto`, 80% specificity) has
four fit passes and fit mean `+7.188`, but development mean averages only `+0.426`, strict gains
36.23%, and family floor `-3.992`; its weakest seed floor is `-4.688`.

The frontier has no hidden qualifying point:

- best individual mean: seed12903 `filter_rank` at 70%, `+2.266`, but 39.06% strict gains and a
  `-6.313` floor;
- best individual tail: seed12903 `safety_rerank` at 95%, floor `-1.469`, but only `+0.895` mean
  and 32.81% strict gains;
- most balanced near point: seed12904 `winner_veto` at 70%, floor `-2.281`, but only `+1.621`
  mean, 37.89% strict gains, and fewer than six positive families.

For comparison, unchanged D126 remains `+2.828`, 42.58% strict, and floor `-4.281`. Increasing
specificity monotonically removes actions but does not preferentially remove enough development
losses. Filtering also creates a multiple-comparisons problem: with many proposals per root, even
a modest arm-level false-positive rate leaves unsafe survivors.

The abstraction conclusion is stronger than “try another threshold.” Absolute arm sign is not a
stable enough cross-map target for this compact head. Relative within-root comparisons transfer
better because they cancel root-level shifts. The next prospective fit should preserve D119's
state gate and translation-invariant ranker, and add a root-balanced pairwise loss that explicitly
orders every positive exact proposal above every nonpositive proposal. This targets D127's 82
cross-sign ranking errors without forcing an absolute logit scale or adding a second runtime head.

Seeds `9,843,800--9,843,815` remain untouched. No Rust integration or platform interaction is
authorized by D129.

Lock SHA-256: `7602dfc460084ccdd0a037dc0e48573f055fb67bf83c0b38acdb80d410eee8af`  
Result SHA-256: `5ae1bf2f4b4e586f7933a5b01474a79bc5a862c853d0ab809e784d31ed2ef7c1`
