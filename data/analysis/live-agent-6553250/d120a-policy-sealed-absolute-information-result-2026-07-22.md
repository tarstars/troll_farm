# D120a policy-sealed absolute-information diagnostic — result

Date: 2026-07-22  
Decision: **close on per-opponent information floors; checkpoint outcome remains unobserved**

D120 prospectively replaces D119's failed 90% support fraction with absolute overall and
per-stratum information floors. It uses the fixed 80-map/1,280-task D119 aggregate, the exact
seed-11901/offset-0 checkpoint, and unchanged held policy gates. The lock verifies with zero
mismatches. Teacher and checkpoint metrics are withheld unless every information floor passes.

Overall information is ample: 1,139 supported tasks, 6,321 roots, and 103,602 arms. Each seat has
at least 564 supported tasks and each interleaved fold at least 560, so all overall, seat, fold,
integrity, and throughput gates pass. Opportunity density is strongly opponent-dependent,
however. `mybot` has 124 supported tasks against the frozen 128 floor. `legend_balanced` has 395
roots and 7,232 arms against floors of 500 and 8,000; `mybot` and `norx_native_three` are also
below 8,000 arms.

These are the only failures. D120 therefore closes without computing teacher or policy metrics.
The result is useful: a single uniform support/arm floor is a poor description of this opponent
mixture, and root-balanced learning exposes very different sample mass across families. Lowering
the observed floors again would be threshold chasing, so D120 does not do it.

The next analysis may consume the panel explicitly as retrospective data and score all 24 frozen
D119 candidates to measure selection transfer, block stability, and family imbalance. Such an
audit can generate a better model/training hypothesis but cannot qualify D119, authorize Rust
integration, or serve as final confirmation.

Lock SHA-256: `a36d910efaa9cc0d84333dbb503431931e952b17d892b596c8d2d07b6ba4b570`  
Result SHA-256: `7f0ce432ea5f750f72ec80ae7db27ca72844e98f891291a649905c35f62dbf71`
