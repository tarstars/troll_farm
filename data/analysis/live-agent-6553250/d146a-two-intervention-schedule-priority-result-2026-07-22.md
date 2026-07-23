# D146a two-intervention schedule-priority audit — result

Date: 2026-07-22  
Decision: **scale breadth at 64 prioritized trajectories/task for a joint two-stage teacher**

Outcome-blind schedule priority fixes D145's sample-efficiency failure on the unchanged D144
population.

| Budget | Uniform increment / strict | Prioritized increment / strict | Mean delta | Full-111 retention |
|---:|---:|---:|---:|---:|
| 32/task | +1.398 / 19.53% | **+3.133 / 32.03%** | **+1.734** | 75.52% |
| 64/task | +3.109 / 31.25% | **+3.938 / 40.63%** | **+0.828** | **94.92%** |

Both priority views preserve 100% crops, exact worker-three reach, all eight positive families, and
positive floors (`+1.438` at 32; `+1.750` at 64). Every frozen efficiency and saturation gate
passes.

The causal schedule class is clear. `early_immediate` alone uses 3,522 rows, of which 2,942 execute
both interventions, and adds `+3.125` beyond exact one use on 40/128 tasks with all eight families
positive. Equal-sized classes are far weaker: early-delayed `+1.344`, later-immediate `+0.430`, and
later-delayed `+0.273`. The value is concentrated in action-pair exploration at boundary zero and
the immediately following q6 boundary, not generic later search.

At budget 32 the priority contains 3,484 early-immediate plus 612 early-delayed rows. At budget 64
it contains 3,522 early-immediate, 3,550 early-delayed, and 1,120 later-immediate rows. This is a
fixed schedule-only ordering; no outcome or action feature enters selection.

Next replay the 57 D145 winning trajectories with complete selected state/action features and
require exact terminal parity. If that interface passes, freeze a new-map YT corpus with 64
schedule-prioritized trajectories per task and train a joint first/second-stage scorer. D145's
19.30% greedy-first compatibility rules out merely attaching a second head to the old one-use
choice. No candidate, D126/final seed, submission, or Arena action exists yet.

Result SHA-256: `7d7c444e8598d839b93ee58959086e6daa6634fdeed3b129b2cbf5ac622c7b07`.

