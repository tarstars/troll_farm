# D14 resident residual environment — smoke protocol (2026-07-20)

## Purpose

Qualify the exact vectorized environment required for resident-aware PPO before spending a
training budget.  This is infrastructure and causal-action validation, not policy selection.

## Frozen environment

- A scenario ID deterministically maps to:
  - map seed `scenario / 12`;
  - opponent `scenario % 6` in the frozen panel order;
  - controlled seat `(scenario / 6) % 2`.
- The stable resident proposes its complete joint command once per referee turn.
- The policy makes sequential decisions for resident units.
- Stage-A legal actions are `KEEP` plus executable local actions only.
- `KEEP` is move plane 0 at the active unit's current cell.
- Every non-overridden resident command, including training, remains intact.
- Reward is per-turn score-margin change divided by 100, so undiscounted episode return
  telescopes to terminal margin change divided by 100.
- Observation: 137 × 11 × 22 bytes; action mask: 13 × 11 × 22 bytes.  Current resident intent,
  previous resident intent, and the other worker's intent each receive 13 spatial planes.

## Smoke block

- Scenario IDs 0--239: maps 0--19, both seats, all six opponents.
- Deterministic all-`KEEP` evaluation.
- Uniform-random legal-action evaluation with random seed 71421.
- Vector batch size 24 for correctness and throughput.

All scenarios are consumed development states.  Existing exact resident rows from D11/D12 are
the independent parity reference.

## Frozen gates

The environment is eligible for PPO only if:

1. all-`KEEP` matches the independent resident reference in terminal margin, wood edge, terminal
   turn, own worker count, and opponent worker count for 240/240 scenarios;
2. all-`KEEP` produces zero overrides and finite returns;
3. every observed mask contains `KEEP`, has between one and seven Stage-A legal actions, and no
   selected legal action is rejected;
4. random legal play completes 240/240 scenarios without a crash, produces overrides in at
   least 95% of episodes, and changes at least 50% of terminal margins;
5. random play is worse than all-`KEEP` in mean map-balanced margin, establishing that the
   residual decisions causally affect the full-game objective;
6. measured batch throughput is at least 500 unit decisions per second on the local machine.

Passing authorizes a short PPO learning-signal run only.  It does not authorize candidate source,
prospective evaluation, submission, or Arena activity.

## Outputs

- keep: `d14-resident-residual-keep-scenarios0-239.json`;
- random: `d14-resident-residual-random-scenarios0-239.json`;
- qualification: `d14-resident-residual-environment-smoke-2026-07-20.json`;
- result: `d14-resident-residual-environment-smoke-result-2026-07-20.md`.
