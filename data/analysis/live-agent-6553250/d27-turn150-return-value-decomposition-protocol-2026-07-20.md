# D27 turn-150 return-value decomposition — frozen protocol (2026-07-20)

## Question

Why does D26's longest bounded farm pulse fail despite recovering substantial own production?
Separate two possibilities:

1. the shared farm phase through turn 149 creates an irreversibly bad map state; or
2. replacing `ownership2` with a cold `SecureOrchardBot` at turn 150 is itself worse than leaving
   the farm controller active.

This is a read-only causal diagnostic on already-consumed D24/D26 rows.  It opens no seed, chooses
no parameter, and cannot authorize a candidate or Arena action.

## Exact shared-state comparison

For every seed 50,000--50,119, both seats, and all eight structural opponents, match:

- `R`: warmed resident from turn 75 through terminal;
- `F`: D24 `ownership2` from turn 75 through terminal; and
- `P`: D26 `ownership2` from turn 75 through turn 149, followed by a cold resident.

`F` and `P` use the same turn-75 root, opponent instance, farm policy, and commands through turn
149.  Their state at the start of turn 150 is therefore common by construction.  Validate all
D24/D26 resident terminal and root fields before analysis.

For terminal margin, own score, opponent score, and own/opponent wood report:

- permanent farm-path value: `F - R`;
- return-continuation effect: `P - F`;
- observed pulse value: `P - R`; and
- the exact identity residual `(F - R) + (P - F) - (P - R)`.

Cluster intervals by the 120 independent map seeds after averaging seats and opponent families.
Also report opponent-family means, control-catastrophic-cell means, sign quadrants, catastrophic
frequency, and negative-margin mass for all three terminal policies.

## Frozen interpretation

- **Cold re-entry is a primary failure** if `P - F` has mean <= -10 margin and a seed-clustered
  95% upper bound below zero.  The next experiment may compare implementable resident-state
  handoff mechanisms, but may not extend the fixed cutoff grid.
- **Cold re-entry is beneficial** if `P - F` has mean >= +5 and a 95% lower bound above zero.  In
  that case the farm-created state, not the restart, is the dominant problem; move upstream to
  planting geometry/exclusivity.
- Otherwise classify the effects as mixed.  Prioritize planting geometry if `F` itself increases
  catastrophic frequency or negative-margin mass over `R`; otherwise prioritize handoff state.

Regardless of classification, D27 cannot revive D26, tune a cutoff, or open prospective data.

## Outputs

- analyzer: `cgauto/d27_return_value_decomposition.py`;
- JSON: `d27-turn150-return-value-decomposition-50000-50119.json`;
- result: `d27-turn150-return-value-decomposition-result-2026-07-20.md`.
