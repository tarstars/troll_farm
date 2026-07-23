# D116a root-wise q6 proposal/WAIT choice — result

Date: 2026-07-22  
Decision: **mechanics and teacher pass; fixed-WAIT listwise scorer fails; held remains sealed**

## Coverage repair and mechanics

The first fresh ten-map panel supports 141/160 tasks (88.125%), missing the frozen 90% floor by
three tasks. Every other mechanic passes and no validation candidate is scored. Repair 1 preserves
that failure, keeps every model/gate fixed, and collects a wholly fresh 16-map panel on seeds
`9,843,650--9,843,665`.

The repaired panel contains 256 baselines, 1,202 roots, and 19,650 arms at 33.001 arms/s. It
supports 233/256 tasks (91.016%). Frozen hashes, grids, feature schema, paired gains, reward
identities, one-use accounting, crop/workforce safety, and all mechanics pass with zero failures.
Two complete fits produce byte-identical results.

## Fit and validation

The validation teacher remains strong at `+31.883` mean margin, 89.844% strict improvement, all
eight positive families, and a `+23.781` floor. Its backward DP marks 598/1,202 roots act-now and
2,663/19,650 arms positive.

All four fixed-WAIT categorical models learn to abstain at the default threshold: training WAIT
recall is 100%, exact choice accuracy is essentially the 51.625% WAIT base rate, and only offset
`-1` is materially active. None of 24 frozen candidates qualifies.

The best validation point, seed 11602 at offset `-1`, is robust but weak: `+1.078` mean, 16.406%
strict improvement, 26.953% activity, fold means `+0.703` / `+1.453`, five positive families, and
a `-0.813` floor. It gains `+1.074` own score with essentially unchanged opponent score. Seeds
11603 and 11604 also remain positive at `+0.910` and `+0.820`; seed 11601 is `-0.313`. Offsets 0
and above are nearly or exactly D40 control.

No checkpoint is retained and held seeds `9,843,700--9,843,715` remain unopened.

## Conclusion

Root-wise choice is directionally safer than per-arm classification: its best point has balanced
positive folds and a shallow family floor. But a single categorical loss over fixed WAIT plus
roughly 16 proposals makes universal abstention an easy optimum. It entangles two different
problems: ranking the best proposal and deciding whether this root is better than waiting.

The next bounded model should factor them. Train the shared 379-feature proposal scorer with
proposal-only categorical ranking on every root. Train a separate compact gate from the already
collected 64 root-state features to predict backward-DP act-now versus wait. At runtime, gate once
per boundary and, when positive, execute the ranker's argmax. Predeclare a training structural gate
before buying another validation panel.

Result SHA-256: `9127cab50e9417df507c0c263a4841a7188b79b074886d76c9010877c868e683`  
Repair manifest SHA-256: `63c3f2a19c15f5433a2b03a408ea7dbb3ddeeba9da9ceff51b845b0b4100c4c0`
