# D132a YT q6 exact-teacher parity pilot — result

Date: 2026-07-22  
Decision: **authorize a separately frozen multi-shard teacher corpus**

The exact D112 Rust teacher collector now has a passing YT CPU path under the user-directed root
`//home/delivery_ml/research/tarstars/troll_farm`. On consumed seed `9,843,780`, the distributed
job generated 2,232 arm rows and 16 baseline rows in 112.594 seconds of mapper-active time.

Both reconstructed TSVs are byte-identical to the frozen local D126 subsets, including headers,
row order, and terminal newlines:

| artifact | rows | bytes | SHA-256 |
|---|---:|---:|---|
| arms | 2,232 | 12,705,141 | `5047bebd4c68f6625ec688e4bc7cc50f5129556185a4cda95d58e6999ee43533` |
| baselines | 16 | 3,963 | `1e570ef934ee2e80201b3d10b0f6c938d08607f5e1de1589cb89089c3f1cccd4` |

The first operation failed before invoking the collector because the default worker image lacked
the GLIBC versions required by the frozen local binary. Repair 1 added the already-proven Jammy
base and Python 3.11 layers. Repair 2 changed only the namespace to the root directed by the user.
Operation `95ab008a-17a0e104-42e03e8-6554149d` then completed with all six frozen gates true.

This proves collector parity and makes YT profitable for corpus generation: independent shards
can run concurrently without changing teacher semantics. It does not qualify a controller or
open final validation seeds `9,843,800--9,843,815`. Freeze a larger corpus in independent blocks,
retain block identity, and use leave-one-block-out transfer for learner selection.

Repair-2 lock SHA-256: `3973663789f87b2798373776c769312ce58d76ffa6061d0b7958f7ba3da3d403`  
Repair-2 launch SHA-256: `4deaaa768efbfa82e2ce37a636f6a4e5be49c6448f0d5cf722602208fa006ea2`  
Result SHA-256: `2c0791cb8b6974ec049628870a0fbcbde36ca00119dfd24fff377d980d3000ab`
