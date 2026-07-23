# D44a D43 external action-value ranking audit — result (2026-07-21)

## Verdict

**Reject D43 score reuse and close the sparse binary residual family.** The frozen actor's small
external score variation is real numerically but contains no continuation-value ranking. Across all
1,087 consumed D42 states, Spearman correlation with exact paired margin is **-0.00060** and the
map-cluster bootstrap interval is [-0.05840,+0.05813]. The top-scored half is **2.255 margin points
worse** than the bottom half.

The actor score instead correlates with the frozen D41c residual gap (`rho=+0.27656`). D43 learned a
weak restatement of its eligibility/proposal signal plus a global probability shift, not which
proposal improves terminal outcome. Twelve of seventeen frozen gates fail. Do not reverse the
score, choose a different quantile, fit D42 again, retrain D43, or build the iterative binary
counterfactual loop. No candidate or platform gate opens.

## Exact replay and scoring

- Every one of the 1,087 manifest rows across 590 tasks replays exactly from D40.
- Decision ordinal, turn, branch, candidate count, rank-zero action, and rank-one action all match.
- All 154 features are finite and preserve the D43 actor ABI.
- The grouped replay takes 9.79 seconds on 20 threads.
- The external probability mean is 0.268116, standard deviation 0.001041, and range
  0.262650--0.271075. The actor still makes zero deterministic rank-one choices.

## Ranking result

| Measure | Result | Frozen requirement | Verdict |
|---|---:|---:|---|
| probability standard deviation | 0.001041 | >=0.0005 | pass |
| global Spearman | **-0.00060** | >=+0.08 | fail |
| bootstrap Spearman 95% interval | **[-0.05840,+0.05813]** | lower >0 | fail |
| top-half minus bottom-half margin | **-2.255** | >=+4 | fail |
| clustered contrast lower bound | **-6.195** | >0 | fail |
| positive fold contrasts | **3/8** | >=6/8 | fail |
| phase/gap-residualized Spearman | **+0.01215** | >=+0.05 | fail |
| positive within-cohort contrasts | **5/12** | >=7/12 | fail |

The top half averages +5.493 margin with 52.94% positive and 38.05% negative outcomes. The bottom
half averages +7.748 with 56.72% positive and 31.31% negative. Thus the direction is not merely too
weak to clear a conservative gate; ranking by D43 is descriptively harmful.

## Top-quartile audit

The highest-scored 272 rows average only **+3.493**, have a row-level lower bound of -0.768, are
48.53% positive and 40.81% negative, and fail two of eight map folds. Their map-clustered lower
bound is +0.230 rather than the required +5. Two opponent means are negative and the resident mean
is exactly zero. Both phase means are positive, but no robust value/precision/breadth conjunction
survives.

## Multilevel conclusion

### Optimization

D43 did update the actor, but almost all useful movement was a global bias. The small conditional
component does not rank unseen exact advantages. Extending the run would reinforce an aggregate
alternative rate without evidence that the network can allocate those alternatives safely.

### Representation

The failure agrees with D16--D19 and D41g--D42: terminal effects are not a stable snapshot label for
the tested compact residual interfaces. Adding another classifier, threshold, or binary PPO pass
would repeat a closed abstraction.

### Strategy and horizon

The positive mean of the whole D42 reservoir remains real, but statewise selection is the wrong
control surface. The next experiment must let complete-game outcome select a coherent policy,
instead of estimating isolated action signs. A compact end-to-end search over the complete D40
scheduler is the highest-priority new direction: retain its validated workforce/funding mechanics,
expose a small phase/role/provenance rate-allocation surface, and optimize whole-game margin across
the opponent league with disjoint development and validation banks.

## Evidence

- protocol SHA-256:
  `f95f6f4fc01c3d74deb0b4fe74e085d233501b935af843dbc8e545f90b2b325c`;
- replay feature TSV SHA-256:
  `76b8598d4ea055dcc3dacfee0054033ac980e5dc01b5dbf1998888f87b797fa7`;
- result JSON SHA-256:
  `70a43e3885c40eb800b3a35f1917d66b0342b31d3105846f35217369adc74c9c`;
- Rust exporter SHA-256:
  `007da3e46b718f33af442a6ed50af1d241c5d9bec45b549416ec02b2c442de9e`;
- Python analyzer SHA-256:
  `3ca8912b28dd1c518ddbabd85a5e92ae0d0d870ff1c74d41447e7bb2d529e91b`;
- focused verification: one Rust exporter test and eight Python analyzer/D43 tests pass.
