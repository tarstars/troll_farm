# Curriculum Level 5 D11 seed-reacquisition clone result — 2026-07-20

## Verdict

**Functional near-pass; proceed to the frozen PPO/compute branch.**  The single preregistered
800,000-label clone raises overall success from 80.00% to **91.80%**, nontrivial success from
80.07% to **90.88%**, and worst-recipe success from 74.67% to **86.27%**.  It preserves every
recurrent-opponent mechanism gate.

The clone nevertheless fails one and only one frozen functional threshold: renewable harvest is
**92.60%**, below the required 95%.  The strict action audit remains unopened because the protocol
permits it only after a full functional pass.  No clone tuning, extension, or post-hoc threshold
change is allowed.  This result activates the identical one-million-transition local/YT PPO
benchmark.

## Frozen-bank result

| Measure | Fixed actor | Clone | Required | Verdict |
|---|---:|---:|---:|---|
| Overall success | 80.00% | **91.80%** | >=90% | pass |
| Nontrivial success | 80.07% | **90.88%** | >=88% | pass |
| Worst recipe | 74.67% | **86.27%** | >=82% | pass |
| Worst height | 79.53% | **89.76%** | >=85% | pass |
| Terminal crop | 80.80% | **93.40%** | >=90% | pass |
| Renewable harvest | 84.60% | **92.60%** | >=95% | **fail** |
| Paired-teacher median delay | 0 | **0** | <=30 | pass |

The clone's recipe rates span 86.27--100%; its height rates span 89.76--94.40%.  Thus the miss is
not an aggregate result hiding a recipe or geometry collapse.

## Opponent-mechanism preservation

| Measure | Clone | Required | Verdict |
|---|---:|---:|---|
| First / third-worker training | 100% / 98.40% | >=98% / >=85% | pass |
| Fresh first / second receipt | 100% / 100% | 100% / 100% | pass |
| Chopper / feeder productivity | 100% / 95.80% | >=98% / >=80% | pass |
| Rival crop / own renewable harvest | 100% / 91.40% | >=95% / >=80% | pass |
| At least one / two / three destructions | 98.80% / 97.00% / 92.00% | >=95% / >=85% / >=70% | pass |
| Maximum destructions / workers | 3 / 3 | <=3 / <=3 | pass |

The improvement therefore did not come from suppressing recurrent pressure.  The remaining miss
is inside the player's recovery/harvest chain.

## Optimization and compute

The clone consumed exactly 800,000 labels in 478.62 wall seconds.  It used 6,401.36 aggregate CPU
seconds, equivalent to 13.37 continuously busy cores and 66.87% of the 20-core host.  Teacher
collection remained much faster than neural optimization.  A single clone is still cheaper than
remote startup; the now-authorized one-million-transition PPO is large enough to measure YT's
end-to-end value.

The clone is valid as the PPO initializer: it is finite and exceeds the prelearning actor by 11.8
percentage points, so the frozen fallback to the accepted checkpoint does not trigger.

## Next action

Run the same seed-137, stream-7,200,000, one-million-transition teacher-anchored PPO once locally
and once on YT.  Treat both checkpoints as throughput evidence only.  Select the backend for the
fresh seed-139 four-million-transition run solely by the frozen parity and projected 20% wall-time
advantage rule.

## Reproducibility anchors

- learning protocol:
  `48922c1f7fe4d20936f3d6c1e8aed6b6040c9eb900e231d109fd931057fc368b`;
- readiness:
  `f6d98896a4e39ef74f8dee97effe0fd8ebc9ec89875e7074c3c2ee7447cb1bba`;
- clone checkpoint:
  `0d89846065a7c87e6248f66bd2cf2a63d5e90955fc557a9684ae56657fe6a343`;
- clone evaluation:
  `a239907f05c80ac18740dc9462f96fa2f4c92465336449aba71eb4d139959c31`;
- clone summary:
  `f6cc02002c5b1a51f9b2ca08940bd7ff3db56884c223f85968e4674a7f28f3ae`;
- teacher control:
  `0089e4b1be5d8ef1e9fe72736c28426a1889c6b5ad8f2f08efea22757a3cbf4e`; and
- random control:
  `db6d3edd059ea8c33fcee7883c93955b25b8a34518bf9b7101220db5a00469b8`.
