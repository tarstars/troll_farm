# N5 endgame opponent-plant contest audit

- Verdict: **`NO_MATERIAL_CONTEST_OPPORTUNITY`**.
- Exact replay coverage: 382/382 cohort occurrences (381 unique games).
- Resident targets: 388 generations in 78 games; 262 targets in 75 games yield carried resources to the opponent.
- Resident replay-conditioned factor-two observed-yield ceiling across all games: 11.991736, bootstrap 95% CI [8.727273, 15.760331] versus 20.
- Subject contact: 51/388; optimistic reach within remaining turns: 368/388.
- H13 fidelity census: resident 388 targets / 78 games, yamo 205 targets / 37 games.

## Boundary

Enemy units can share cells, so this is access for later HARVEST/CHOP, not body-blocking. Extracted fruit/wood is carried resource, not banked score. The factor-two quantity is deliberately generous and replay-conditioned; it is not a causal policy-value estimate.

## Gates

- `source_integrity`: **true**
- `decode_integrity`: **true**
- `target_integrity`: **true**
- `resident_targets_ge_30`: **true**
- `resident_target_games_ge_20`: **true**
- `resident_positive_targets_ge_20`: **true**
- `resident_positive_games_ge_10`: **true**
- `ci_lower_ge_20`: **false**
- `ci_upper_lt_20`: **true**
- `support_pass`: **true**
- `material_pass`: **false**
