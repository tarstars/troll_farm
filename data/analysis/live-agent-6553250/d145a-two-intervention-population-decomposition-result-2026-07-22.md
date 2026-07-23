# D145a two-intervention population decomposition — result

Date: 2026-07-22  
Decision: **improve per-task search allocation before trajectory-teacher scaling**

The D144 two-use signal is robust across disjoint sequence populations, but uniform sampling has
not saturated at 64 double replicas per task.

## Population robustness

| Population | Double replicas | Executed pairs | Increment over one use | Strict tasks | Positive families | Floor |
|---|---:|---:|---:|---:|---:|---:|
| Even ordinal | 56 | 4,440 | **+2.133** | 39/128 = 30.47% | 8/8 | +1.250 |
| Odd ordinal | 55 | 4,417 | **+3.141** | 41/128 = 32.03% | 8/8 | +0.500 |
| Full | 111 | 8,857 | **+4.148** | 57/128 = 44.53% | 8/8 | +1.750 |

Both independent partitions pass the frozen `+2`, 25%, and six-family floors with exact relative
safety. The value is not one lucky slice.

## Sample-efficiency curve

| Prefix replicas | Increment | Strict tasks | Fraction of full mean |
|---:|---:|---:|---:|
| 8 | +0.766 | 10/128 | 18.46% |
| 16 | +0.992 | 17/128 | 23.92% |
| 32 | +1.398 | 25/128 | 33.71% |
| 64 | +3.109 | 40/128 | **74.95%** |
| 111 | +4.148 | 57/128 | 100% |

The 64-replica prefix misses the prospective 80% saturation floor by 5.05 percentage points, the
only failed D145 gate. Scaling uniform search at 64 would discard too much of the demonstrated
headroom; simply collecting more maps at that depth is premature.

## Trajectory structure

The deterministic manifest contains all 57 full-population winners (SHA `88b5e08e...`). Their
second move adds `+27.316` mean over the same first intervention alone, median `+21`, and minimum
`+1`; all selected sequences pass this causal identity check. Only 43/57 first moves are positive
alone. The first move matches the task's exact one-use oracle in only 11/57 = **19.30%**, so this is
not a greedy one-use policy plus a small residual. A joint two-stage learner is required.

Winning timing is highly concentrated:

- first boundary 0: 46/57; boundary 1: 10; boundary 2: 1;
- gap one: 42/57; gaps two/three: 6/7; gaps four/five: 1/1;
- first action kind: 19 single-worker first, 4 single-worker second, 34 joint; and
- the same representative slot is reused in only 2/57.

This suggests the next cheap experiment: evaluate schedule-conditioned subsets of the frozen
population, especially first-boundary-zero/immediate-next-boundary pairs, against equal-budget
uniform prefixes. If concentration recovers more value per episode, use it for deeper search and
only then scale map breadth. No D126, final validation, candidate, or platform action follows.

Result SHA-256: `25ce7d1ab5ef1819ffe5e8ae3b4b577f5c4d20c78108e3cbadd2b067e511e37d`.

