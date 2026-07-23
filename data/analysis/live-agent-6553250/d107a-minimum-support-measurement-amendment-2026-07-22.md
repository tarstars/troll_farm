# D107a minimum-support measurement amendment

Date: 2026-07-22  
Status: frozen after run A execution, before support-audit execution or terminal analysis

The frozen D107a protocol requires the minimum number of unique noncontrol proposals at every
eligible zero-control boundary. The original locked runner
`b15214ee87ca925cb43b565f31815f169d6e18c4105abbb4d776a3cc687e860a` records the sum and maximum
but accidentally omits the minimum. This is a measurement omission; run A completed without an
integrity assertion and no D107a terminal field or population margin has been analyzed.

Use amended runner
`2bd7e3c5628cf048af61082aba848bb6ea6f66d3967e4ee056823679693d0514`. Its proposal construction,
scoring, selection, stepping, terminal serialization, and existing counters are unchanged. It only:

1. accumulates `minimum_unique_proposals` beside the existing sum and maximum;
2. serializes that new column; and
3. accepts an optional controller-count limit so the audit can execute only population row zero.

After the two original full runs finish and reproduce byte-for-byte, execute the amended runner on
the same 128 tasks with controller limit one. Require 128 zero rows. Remove only the new minimum
column and require every remaining population byte/field to equal the corresponding original run-A
zero row; require its baseline file to equal the original baseline exactly. Then use
`minimum_unique_proposals - 1` as the per-episode minimum noncontrol support, taking the minimum
over episodes with at least one eligible boundary.

The audit may inspect proposal counts and equality only. It cannot replace either full population
run, alter activity/value thresholds, select a controller, or authorize terminal analysis unless
the original reproducibility and all amended integrity checks pass.
