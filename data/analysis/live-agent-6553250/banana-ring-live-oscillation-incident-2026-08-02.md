# Bounded banana-ring live oscillation incident

Date: 2026-08-02
Resident: agent `6590136`, submission `41081465`

## Exact replay evidence

The newest completed live cohort was decoded through the existing official frame/diff parser with
zero unknown updates. A detector marked a unit when its positions satisfy `p[t] = p[t-2] != p[t-1]`
for consecutive turns. Many games contain multi-turn episodes; game `897829265` provides two long,
visually obvious examples for worker 2:

| turns | positions | carried stock | emitted behavior |
|---|---|---:|---|
| 20--29 | `(10,4) <-> (11,4)` | empty | reversing MOVE every turn |
| 269--280 | `(8,2) <-> (8,3)` | empty | reversing MOVE every turn |

The first loop lasts ten state transitions. The second lasts eleven and runs beside worker 0's
repeated PLUM PICK/DROP cycle on `(9,3)`. In both windows, the engine executes the requested move;
this is not a collision refusal or a stuck movement result. The bot regenerates the trained
worker's tree choice every turn, so a state-dependent target/routing decision reverses with the
worker's position.

The exact source-level divergence between the readable research source and the 99,990-byte Arena
artifact has not yet been localized on this replay. That localization belongs to restoration r2;
it is not necessary to classify the live artifact as implementation-invalid.

## Scientific disposition

Focused semantic tests, eight inherited equality streams, and behavioral smoke did not cover this
liveness failure. Therefore the live score of this source cannot be used to accept or reject the
banana algorithm. Future restoration must zero-gate period-2 movement on this replay, prove broad
research/compact equality, and require sticky worker commitments rather than per-turn retargeting.
