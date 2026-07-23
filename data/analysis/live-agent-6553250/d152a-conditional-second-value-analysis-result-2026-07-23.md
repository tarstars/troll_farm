# D152a conditional-second value analysis — result

Date: 2026-07-23  
Decision: **open grouped conditional value cross-fit**

Every frozen signal, safety, robustness, and target-richness gate passes.

On all 388 D148-active states, the exact combined second-action oracle strictly improves first-only
continuation and adds **+36.760 mean margin**. It adds +24.791 own score and removes 11.969 opponent
score, preserves crops exactly, and leaves worker-three reach unchanged at 92.01%. All four blocks
are strongly positive (`+32.806--+39.977`) and all eight opponent families are positive with a
`+28.804` floor. The oracle is another **+3.294** above D148's sampled selected sequence and
`+14.142` above exact one use on these active states.

Across all 909 selected-first states, the oracle adds **+30.383**, strictly improves 867/909 =
95.38%, and adds +4.608 over D148's sampled sequence. Only 48.62% of original selected seconds are
exact-best, although 70.63% lie within five points. A nonselected near-tie exists in 638/909 =
70.19% of states and 794/909 = 87.35% contain at least two positive noncontrol actions. This directly
explains why D149's single hard winner was a poor target.

The exact label distribution is rich: 15,319 noncontrol values contain 7,001 positive, 7,769
negative, and 549 zero values; population standard deviation is 27.744. Write all 16,228 labels at
SHA `28c6b74f...`. The next learner must optimize held value/regret and sign, not exact argmax
accuracy. Reserved validation remains sealed. Result JSON SHA: `ab76f844...`.
