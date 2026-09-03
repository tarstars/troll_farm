# Three-troll optimized start: executed result

**Verdict: `DEAD_AS_BOT`**

## What was compared

The candidate and control share the same turn-2-second-troll opening. Only the candidate enables the wood-aware third-troll optimizer. The paired result therefore measures that optimizer rather than the already-known early-second-troll change.

## Validity and runtime

- candidate fixture bed: PASS; control: PASS
- candidate smoke mechanics: 19/24; control: 15/24
- source size: candidate 90,070 UTF-16 units; control 90,071; limit 100,000
- timing: first-turn max 2.397 ms; warm p99 1.045 ms
- panel execution faults zero: True

## Third troll

- trained in 14/24 smoke games
- trained by turn 110 in 14 games
- p25 / median / p75 turn: 10 / 30 / 56
- selected tuples: {'1 1 0 1': 10, '1 2 0 1': 4}
- fallback or no admitted/completed third-troll plan: 10 games

## Candidate minus control on identical maps and opponents

- paired win difference: +0.0500 [+0.0050, +0.0950]
- paired margin difference: +2.39 [0.6575, 4.175]
- pre-registered death condition (below -0.05 with interval clear): False
- direct duel: 51 candidate wins in 200 games; paired reading {'bootstrap': {'draws': 10000, 'seed': 1}, 'games': 200, 'losses': 92, 'maps': 100, 'maps_won_on_both_seats': 3, 'maps_won_on_neither_seat': 52, 'margin_interval_95': [-1.81, -0.24], 'margin_mean': -0.97, 'ties': 57, 'unit': 'map (both seats carried together)', 'win_rate': 0.255, 'win_rate_interval_95': [0.2, 0.31], 'win_rate_interval_above_half': False, 'win_rate_interval_below_half': True, 'wins': 51}

## Boundary

The optimizer is a deterministic contested-resource assignment model and live policy gate. Its value estimate is not a proof of turn-300 game value; the paired panel is the value check.
No ladder or platform action was taken.
