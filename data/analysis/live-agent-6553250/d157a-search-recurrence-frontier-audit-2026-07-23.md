# D157a search and recurrence frontier audit

Date: 2026-07-23  
Decision: **open one previously omitted objective experiment; keep prior search branches closed**

## Evidence matrix

| Branch | Strongest evidence | Binding failure | Status |
|---|---|---|---|
| Legacy RHEA / full online simulation | occasional tactical gains | 18--36 rollouts in 28 ms; cheap-opponent overfit | closed |
| GoldElite model-predictive MOVE residual | +15.906 across its development mixture | used GoldElite, not the resident | nondeployable evidence |
| Resident-backed MOVE residual | all-MOVE +1.200; bank replication +0.508 | 92.85 ms p95 and weak prospective effect | closed |
| Resident local-residual PPO | mechanics exact | every deterministic actor collapses to KEEP | closed |
| One-state MC distillation | 17%--18% positive labels | compact, spatial, large, and oracle-ID models cannot control the loss tail | closed |
| Four-mode recurrent PPO/evolution | active policies reach +12--+17 on search batches | coarse modes fail cross-map transfer; survivor collapses near balanced | closed |
| Recurrent q6 PPO, pooled margin | final held -0.738 and -0.150 after 16k/64.8k transitions | suppresses own and opponent score; family failures rotate | duration closed |
| One-use q6 offline teacher/scorers | exact oracle +36.766; held selectors around +3 | static strict-win plateau and independent-panel veto | closed |
| Two-use q6 MC teacher | exact +4.110 over one use; exact conditional oracle +36.760 | imitation/value/history/semantic policies fail map-fold transfer | static policy closed |

## Remaining causal gap

D109 explicitly prescribed a deployable family-balanced/robust return with own-score protection.
The project instead changed authority and optimizer in D110, then followed the offline-teacher
branch through D156. No experiment ever changed only the recurrent q6 training objective.

This gap is worth one bounded test because:

- D107 proves repeated q6 proposals are mechanically safe and have large oracle headroom;
- D108/D109 prove the 10,725-parameter recurrent actor learns, abstains, and ends near D40 rather
  than catastrophically below it;
- both failures are specifically consistent with pooled-objective interference; and
- opponent family and own-score deltas are available at training terminals, while the exported
  actor still receives only deployable observations.

Open D158a as a same-architecture, same-data objective ablation. Do not revive runtime rollout,
resident MOVE residuals, four-mode recurrence, one-state distillation, or static D149--D156 model
tuning. If group-robust own-protected PPO also ends near control or rotates family losses, close
the recurrent q6 objective branch and move to an offline-to-online trajectory critic rather than
another PPO duration/seed search.

