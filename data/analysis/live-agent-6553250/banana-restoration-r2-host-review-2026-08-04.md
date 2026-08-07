# Banana restoration R2 host review

Date: 2026-08-04

Task: `20260802-banana-restoration-r2`

Candidate: `candidate-banana-r2.min.rs`, 74,725 bytes, SHA-256
`f29efd0e9c8cd17a2151678b2b0a449baba76aa12ede283d5ef486f5a5fe6eb9`, from remote commit
`a787d478df4adeaf5eac352718d391ef4294526d` on
`agent/claude_1-banana-restoration-r2`.

## Verdict

**IMPLEMENTATION_INVALID.** This verdict concerns the exact `f29efd0e...` implementation, not
the value of bounded banana production. No Arena or TestSession mutation occurred, and no score
from this candidate is admissible as banana-value evidence.

The host-only replay gates stop at the first terminal implementation divergence, as required by
the task. Exact game `897829265` and a value panel cannot repair a source that already contradicts
its own invariant contract.

## Checks independently reproduced

- Parent SHA `a8eb3b2b...` and candidate SHA `f29efd0e...` verified.
- The six-insertion rebuild reproduced the exact 74,725 candidate bytes.
- Optimized standalone compile passed; empty input produced zero stdout and stderr.
- Detector self-tests: 23/23 pass.
- TIER-P parent dormancy fixtures: 7/7 pass.
- TIER-C candidate semantic fixtures: 8/8 report pass.
- Sacred source remained exact SHA `fff6669b...`.

These checks establish build integrity. They do not overcome the contract failures below.

## Terminal failure 1 — the committed lifecycle trace falsifies I-9

Invariant I-9 says replant demand may reserve at most one carried banana seed and that every
additional harvested banana is surplus that must take a bank path. The handoff's own supposedly
all-green closed-loop trace `traces/t1_lifecycle-*` records:

| Turn | Banana carry before command | Command |
|---:|---:|---|
| 55 | 0 | `HARVEST 0` |
| 56 | 1 | `HARVEST 0` |
| 57 | 2 | move toward a plant cell |
| 58 | 2 | `PLANT 0 BANANA` |
| 61 | 1 | `PLANT 0 BANANA` |
| 79 | 0 bananas, other cargo | first later `DROP 0` |

Thus two harvested seeds are replanted before any surplus-banana banking. The source explains the
failure directly: while any eligible vacancy exists, `demand` remains true and every carried
banana is offered as a Plant candidate; banking is offered only when `!demand`. The D-7 ledger
checks that bananas are not lost, but it does not test the stricter one-seed/surplus-bank rule.

This is precisely the behavioral distinction the owner requested: harvest one renewable seed and
bank the excess instead of expanding resource production for its own sake.

## Terminal failure 2 — the revised ownership-loss response is not implemented

The reviewed C7/I-10a resolution required a contested mother to harvest only when winnable,
otherwise convert if conversion beats the opponent, otherwise abandon. In readable block I1,
`banana_action` special-cases only `contested && fruits_ready`. If the opponent ETA is no greater
than the resident ETA and fruit is not ready, execution falls through to the normal lifecycle;
there is no conversion comparison and no transition to `BananaPhase::Abandoned`. When fruit is
ready but the resident is farther away, it emits a move toward fruit the strict ownership rule
already assigns to the opponent.

The committed contested mini-referee has a static opponent, so it cannot exercise opponent fruit
capture and cannot establish the replay-outcome portion of D-6/I-11. Its PASS does not cover this
branch.

## Missing mandatory artifact

Acceptance checks 2 and 3 require a complete independently readable research source and
research/compact command equality. The handoff contains readable insertion fragments plus the
whole minified candidate, but no complete compilable readable research source. Consequently the
requested research-versus-compact replay equality gate cannot be run from the handoff as stated.

## Additional diagnostic, not a verdict basis

One closed-loop consumed-map smoke against the existing motion opponent produced parent margin
`+54` versus candidate margin `-149` on seed 0, seat 0; opponent score increased from 158 to 354.
This single development match is not a value estimate and is not used for the invalid verdict. It
only reinforces the decision not to bypass the implementation contract.

## Required disposition

Do not submit, value-test, or reuse exact candidate `f29efd0e...`. A revision must have a new
source hash and handoff, add an explicit per-harvest one-seed reservation with surplus banking,
implement the full contested ownership-loss state transition, provide a complete readable source,
and add non-vacuous tests that fail on the current bytes. Only then do the dormant-equality,
banana-live research/compact, and `897829265` host replay gates resume.
