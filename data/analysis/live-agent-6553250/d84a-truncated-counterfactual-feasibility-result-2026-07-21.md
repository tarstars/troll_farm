# D84a truncated counterfactual feasibility result (2026-07-21)

## Verdict

**Reject and close direct online threatened-response Monte Carlo at the current simulator/action
representation.** No tested horizon passes both the frozen value and latency conjunctions.

The best value appears only after 32 post-root macro decisions: +3.160 mean terminal margin,
28.11% of D82's safe oracle.  That misses the +5.620 floor, while even an unattainable
perfect-parallel lower bound costs 64.840 ms p95 and 133.114 ms maximum.  This timing already knows
the actual local opponent, assumes all branch states exist, and excludes cloning, candidate
enumeration, inference, thread creation, and live-controller overhead.

Do not build the resettable opponent-proxy ensemble, tune the horizons or liquid-value formula, or
reuse D82 outcomes for another fit.  D84a creates no candidate and authorizes no platform action.

## Integrity

- Two full 12,288-row endpoint matrices are structurally identical after excluding measured
  elapsed microseconds.
- Two isolated 3,072-row latency matrices are structurally identical and exactly match their
  corresponding full-matrix subset.
- All 449/512 D82 roots, 656 semantic-arm availabilities, exact-prior ranks, action planes, and
  intervention flags reconstruct exactly; every terminal truth arm joins.
- There are zero mechanics, command, provenance, deposit, finite-value, legality, fallback,
  endpoint-accounting, or unavailable-arm parity failures.
- Isolated latency covers 113 rooted tasks across eight maps, both seats, and all eight opponent
  families.  For each task the worse of two repeats is retained.

All frozen integrity gates pass.

## Horizon result

The selector sees the actual local opponent continuation and ranks arms by banked score plus
directly carried score value.  Value is the selected arm's D82 terminal outcome; latency is
cumulative simulation from the already-reconstructed root.

| Decisions | Terminal margin gain | D82 oracle captured | Strict / regress, rooted | Ideal p95 / max | Serial p95 | Verdict |
|---:|---:|---:|---:|---:|---:|---|
| 1 | -0.738 | -6.57% | 10.02% / 11.80% | 3.872 / 6.022 ms | 6.159 ms | value fail |
| 2 | -1.168 | -10.39% | 11.36% / 14.48% | 5.903 / 10.814 ms | 12.986 ms | value fail |
| 4 | -1.270 | -11.29% | 24.50% / 24.28% | 9.477 / 19.545 ms | 24.223 ms | value fail |
| 8 | -0.076 | -0.68% | 31.18% / 28.29% | 17.649 / 37.318 ms | 54.942 ms | value fail |
| 16 | +0.639 | 5.68% | 34.30% / 28.29% | 33.019 / 77.496 ms | 110.359 ms | value and max-latency fail |
| 32 | **+3.160** | **28.11%** | 34.30% / 22.27% | **64.840 / 133.114 ms** | 210.166 ms | value and latency fail |

Horizon 32 is mechanically safe—100% crop creation, only 0.20 percentage-point worker-three
degradation, seven nonnegative opponent families, and a -0.359 worst family.  Its failure is not a
catastrophic tail hidden by the mean.  The useful ranking signal simply materializes too late and
remains too small.  Horizon 16 nearly meets the p95 lower-bound budget, but its +0.639 gain is only
5.68% of the oracle and its 77.496 ms maximum already violates the warm-turn limit.

Endpoint physical-turn spreads grow from 0.78 turns on average at horizon one to 5.80 at horizon
32, with a 38-turn maximum.  Persistent jobs therefore make the longer macro horizon even less
like a fixed-time live search; this is descriptive and was not needed for rejection.

## What the result closes

The earlier 209/279 ms experiment closed a large 240-turn, multi-opponent-model workforce search.
D84a now closes the plausible smaller exception: one sparse root, at most three semantic
responses, short exact continuations, actual-opponent information, and ideal arm parallelism.
Horizons cheap enough to run do not rank terminal value; the first useful horizon is already too
slow.  A resettable proxy can only add inference and state-management cost to this measured lower
bound.

This does not erase D82's offline teacher.  It rules out spending the next iteration on live
rollout engineering.  The next eligible branch should move back to the real resident/current-field
interface: audit whether D78's observed imminent attacks admit an exact one-turn defensive salvage
action under the opponent command already present in public replay.  That is a causal command-layer
question, not another D40 terminal selector, snapshot refit, global recurrent mode controller, or
runtime Monte Carlo search.

## Evidence

- protocol SHA-256: `13413dbff9fa4cbf6358ae0b0e6aaa9570935fe39311cf37533fb4b0f7de8c58`;
- runner SHA-256: `54a0b5212cdf1ccc69927d5c4f3b03484f5f0a8017e3248222c8db26a781ee87`;
- analyzer SHA-256: `51fb12c9bab25f4035e66f43962ba0fed8c9aca394d49796745e246fb71be957`;
- result JSON SHA-256: `58e7a118ad2e5304cc4b20d41e56e910b5bdb6df2c6aeb17424592539b0f1651`;
- D82 terminal truth SHA-256: `a2d9e12d12b550398f1b84946daccdf01da379dd9155083969ed22ca5bf1438b`.
