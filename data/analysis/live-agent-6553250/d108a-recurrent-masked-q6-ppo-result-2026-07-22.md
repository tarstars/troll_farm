# D108a recurrent masked q6 PPO — result

Date: 2026-07-22  
Decision: **mechanics/signal/safety pass; fixed-policy value fail; no candidate**

## Execution

D108a completed the frozen 16,000 transitions and 40 PPO updates in 534.30 seconds at 29.95
transitions/s. It produced 5,065 complete paired episodes. All losses and parameters remained
finite; all 64 representative expert indices were explored; paired reward error stayed below
`1.2e-5`; and no illegal action, direct-command failure, provenance failure, or deposit failure
occurred.

The actor is small: 4,452 actor parameters plus 6,273 critic parameters, 10,725 total. Its L2 drift
is 1.962. It changes 246/256 frozen probe choices and finishes with 15 distinct probe actions. The
number of probe controls rises from 7 initially to 137 finally, direct evidence that PPO learns
abstention rather than merely rotating among q6 experts.

## Held evaluation

Both complete 768-row evaluation matrices are byte-identical with SHA-256
`7204f02a166b53dd778ac14ff7957c15db518432e885f7a9a939939e14839058`.
All control, initialized, and final rows preserve crops, D40's 95.703% worker-three rate, exact
paired reward identity, and zero mechanical failures.

The initialized actor is poor: `-8.879` mean margin versus D40, all eight families negative, and a
worst family of `-20.156`. PPO improves it by `+8.141` on identical tasks and strictly beats it on
58.98% of tasks. The final actor reaches `-0.738` versus D40 and strictly improves 42.19% of held
tasks. It intervenes on 83.59% of tasks and repeats on 65.63%.

Four families are positive:

- legend_balanced `+4.750`;
- silver_boss `+3.875`;
- compact_gold `+3.156`; and
- gold_adaptive `+0.406`.

Norx is exactly neutral; mybot is `-0.094`; resident is `-4.281`; and script_boss is `-13.719`.
Mean opponent score falls `0.793`, but own score falls `1.531`, leaving the small net regression.
Consequently mean gain, positive-family count, and worst-family gates fail. No D108a checkpoint is
eligible for submission or candidate construction.

## Diagnosis

This is undertraining evidence, not representation collapse:

- mechanics, optimization-signal, and safety gate groups all pass;
- every family improves relative to initialization, including script_boss by `+6.438` and resident
  by `+6.656`;
- final-rollout training reaches `+2.537` with 49.07% strict wins;
- mean KL is only `0.000362`, mean clip fraction `0.0104%`, and entropy remains 2.485 near the end;
  optimization is far from a trust-region or entropy collapse; and
- the final policy is already within one point of D40 overall while learning a large control region.

The next experiment should isolate duration. Train the same architecture, objective, initialization,
and optimizer from scratch for roughly four times as many transitions on entirely new maps. Widen
the vector batch to 60 only for utilization; a consumed-map benchmark improves exact-environment
throughput from 31.1 transitions/s at 20 environments to 45.5 at 60. Use a larger new training pool
and a new 512-task held panel. Do not continue or select the D108a checkpoint, tune against its held
families, or change the representation.

Result JSON: `d36abd2f1610163ae2a775978cb69a59ac48658e65b174e65c3ddeccad37083c`  
Checkpoint: `0776b2a34f1f9a7e073a314df0856a05f561cb70dc12540061fef065a23326b4`
