# Curriculum Level 2 confirmation clone result — 2026-07-19

## Verdict

**Launch-sanity pass.**  The independent seed-67 clone clears every predeclared clone floor on the
already-consumed preflight bank and may initialize the confirmation PPO run.  This read is not
confirmation evidence; prospective evidence remains exactly seeds 2,007,000--2,008,999.

| Metric | Required | Observed | Result |
|---|---:|---:|---|
| Overall success | >=80% | 90.75% | pass |
| Nonzero-total-deficit success | >=75% | 83.96% | pass |
| Recipe-family floor | >=70% | 75.56% | pass |
| Height floor | >=65% | 88.45% | pass |
| Paired teacher median delay | <=20 turns | 0 turns | pass |

The disjoint seed-67 run ends at 94.8% teacher-action accuracy after 400,000 online labels.  It
takes 863.80 wall seconds and 10,312.65 CPU-seconds, or 59.69% aggregate capacity on the 20-core
host.  Relative to the seed-61 discovery clone, overall success rises by 0.85 points while the
worst recipe falls by 3.60 points; both are comfortably within normal independent-seed variation
and above their frozen floors.

Frozen artifacts:

- checkpoint: `1824e8dc2e81ecbbaa8b69a6f1433f3df61392ca5ba5df85a0f8a8a97c417415`;
- exact diagnostic evaluation: `4b48b71f9eb69f65ee5c401fd10b2699b29854f925e23b8563f502f5568937b6`;
- training summary: `a7e9ebfeaef76be23f38160bb6ef15db3675507c6a32a051d0d73c4544d71f1f`;
- prospective teacher control: `822bd1fbc629b889b3b2fd571f7136d4cacd18845939df73cb162ceba289e586`;
- prospective seed-67 random control: `271d2aaab17694400c3ff018d5841cc229237649f78aa24a2cf6164d415b0848`.

On the new bank, the teacher solves 1,999/2,000 maps and random legal solves 814/2,000 overall but
0/1,178 nontrivial starts.  Both controls were generated and hashed before the first learned-policy
evaluation.

## Next move

Run the unchanged two-million-transition teacher-anchored PPO process from this exact checkpoint,
using stream 5,300,000.  Record the 500,000-transition read without early stopping and decide only
from the final frozen confirmation gates plus exact action audit.
