# D154a conditional-value representation ablation — result

Date: 2026-07-23  
Decision: **close fixed semantic-slice compact value models**

Both replicas complete 192 fits. Every held count is exact A/B, all four `full443` seeds exactly
reproduce D153a, and one threaded model hash differs without changing behavior.

No representation/seed cell is eligible. Removing expert identities actually lowers median held
value from +1.237 to +0.720. Compact semantic variants transfer slightly better but remain weak:

| Representation | Params | Median value | Median harmful | Median sign BA | Best cell |
|---|---:|---:|---:|---:|---:|
| full443 | 7,121 | +1.237 | 45.10% | 51.23% | +1.820 |
| no_expert_ids379 | 6,097 | +0.720 | 45.93% | 51.51% | +0.946 |
| semantic_context115 | 1,873 | +1.699 | 45.82% | 52.07% | **+2.089** |
| semantic109 | 1,777 | **+1.728** | 45.38% | 52.23% | +1.988 |
| semantic_supporters173 | 2,801 | +0.756 | 45.76% | 50.93% | +1.791 |
| action_semantic_context51 | 849 | +1.304 | 46.26% | **52.78%** | +1.844 |

Feature-plane overfitting is therefore not the main bottleneck. The tiny semantic models preserve
roughly the same weak signal, but none learns a reliable sign boundary or a safe action policy.

The next causal omission is history. At a conditional second boundary, the 64 state features retain
aggregate economy and only a four-way previous-kind flag; they do not encode the selected first
intervention's exact jobs, owners, target cells, deposits, or supporter pattern. D151/D152 values
are explicitly conditioned on that first action. Test compact/full first-action memory with both
concatenated and bilinear scorers before considering trajectory recurrence or more data.

No checkpoint or candidate exists. Reserved maps remain sealed; no YT, Arena, submission, or
resident mutation occurred. Result JSON SHA: `a9383de9...`.
