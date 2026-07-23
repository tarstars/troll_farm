# D41c rank-aware parallel ABI — preflight result (2026-07-21)

## Verdict

**PASS and select 64 environments for the frozen D41c PPO run.** Exact prior ranks are now produced
inside Rust, parallel slot execution preserves every checked historical value, and width 64 is
materially faster than width 16.

The machine-readable artifact is `d41c-rank-parallel-preflight-2026-07-21.json`, SHA-256
`bccf184df2e1b4913f0236381409a17ca9549ea0f92a8d441fd95731c1e5e5b2`.

## Integrity

- Rank zero equals the D40 teacher index and each legal candidate set contains an exact
  `0..count-1` rank permutation; padding uses the invalid `u16::MAX` sentinel.
- Independent 4,096-decision rank streams are byte-identical at both vector widths.
- The width-16 legacy action/feature hash remains
  `306779511abd482bd0a102c9cb0949f4ff40e0180ea1895fc8cefc9c584ef4fd`, exactly matching D41a
  before parallelization.
- A 32-episode D41b smoke block matches every frozen terminal score, workforce/crop counter,
  action hash, and state hash.
- Maximum telescoping reward error is `4.9323e-6` margin points, below the `1e-4` gate.
- The release library SHA-256 frozen for training is
  `5839a7b888f2772e54a293a66ed5b186df378d5b8514f43a200898c8eef70173`.

## Throughput

| Width | A decisions/s | B decisions/s | Effective CPU cores, A/B |
|---:|---:|---:|---:|
| 16 | 1,181 | 1,346 | 6.39 / 6.29 |
| 64 | **2,233** | **2,407** | **10.54 / 10.63** |

Width 64 improves the two-run mean throughput by about 75% and raises measured parallel CPU use,
while all hashes remain deterministic. It therefore fixes D41c's rollout geometry at 64
environments x 64 decisions = 4,096 transitions per update.

## Pre-training controls

The fresh 512-task development baselines were generated after the D41c protocol and before any
training:

- D40: 218.311 own score, 177.229 opponent score, **+41.082 margin**, 99.61% worker two,
  92.38% worker three, and 100% crops;
- random legal: 71.320 own score, 197.455 opponent score, **-126.135 margin**, 62.11% worker two,
  1.56% worker three, and 94.53% crops.

Their SHA-256 values are respectively
`0c71718f4bbe4c7b65b3b7b0ca6fd2991a6a2460d0f32497248ad1ebe33d48e2` and
`856d1e8ebf925bdabe585d485180ffa855f1ce50e421e103875cbb29ae092dd4`.

The sole frozen seed-411 PPO run is therefore eligible. No confirmation or platform action opens
from this infrastructure pass alone.
