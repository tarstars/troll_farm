# D133b q6 support-semantics repair — result

Date: 2026-07-22  
Decision: **open frozen D134 leave-one-block-out selection**

The fixed historical audit shows that a per-block 90% q6-availability requirement is not stable:
four of nine prior independent 16-map panels are below 90%, only five clear it, the range is
85.94%--92.97%, and pooled support is 2,076/2,304 (`90.10%`). The frozen protocol's narrative
“five below” is corrected in a separate addendum; its executable gates and conclusion are
unchanged.

D133b removes only availability-as-corruption. Every exact nonavailability mechanics gate passes
in all four blocks, as do the global floors of 1,024 baselines, 81,440 arms, and 4,980 roots. The
three-block training-fold support counts are 674, 677, 693, and 686 versus the prospectively fixed
D134 calibration minimum of 646; the all-block count is 910 versus 861. All seven repair gates
pass.

The complete 1,024-task teacher is strong:

- oracle margin gain `+37.295`, strict improvement 87.30%, and intervention rate 87.30%;
- all eight family means positive, with `+24.578` worst-family gain;
- 4,980 roots and 81,440 arms, with 50.48% act-now roots, 13.67% positive arm targets, 84.51%
  negative arm targets, and target standard deviation 27.28;
- mean own score `+22.555`, opponent score `-14.740`; and
- 100% crop creation with worker-three rate exactly equal to control at 89.26%.

Every original D113 aggregate signal and safety gate passes. D134 may now use these four blocks
under its already-frozen leave-one-block-out protocol. Final validation seeds remain untouched.

Lock SHA-256: `c326c398ce878030a4c548fc2a512c6b38dd25847399e416fc86d18f3779c8f6`  
Result SHA-256: `98a2c5277f365214ee1005bfeca435300f975f955b5dabe20ef0ac51c3cae054`
