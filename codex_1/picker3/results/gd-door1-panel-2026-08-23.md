# fuzz panel report [CANDIDATE (candidate vs parent)] - 20260820-pair-selector-anti-benching Phase-3b G-d/G-e

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `/tmp/codex1-gdge.45TjyH/claude_1/picker3/candidate-door1-p3b.rs` (sha256 457360589a65cb2662950761deba817852ea9eb0d2c53b05a3e6fd2ab9dfda8a)
- parent: `/tmp/codex1-gdge.45TjyH/claude_1/picker2/candidate-door1-p1p2.rs` (sha256 5e1f4df406480f678ff03677cdda0f69d510c5c94efe90d4f0a8231b70c3339e)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 17.6 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 240 |
| clean_games | 125 |
| banana_activated_games | 99 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 7 |
| blocking_games | 115 |
| flagged_games | 2 |
| instrument_invalid_games | 0 |
| parent_instrument_invalid_games | 0 |
| gate_unready_games | 0 |
| unsupported_command_games | 0 |
| malformed_command_games | 0 |
| games_with_a_successful_train | 2 |
| successful_train_events | 2 |

| class | games |
|---|---|
| choke_corridor | 60 |
| forest_dense | 20 |
| forest_sparse | 16 |
| multi_door | 24 |
| open_field | 36 |
| orchard_eligible | 24 |
| single_door_tent | 24 |
| water_diagonal | 36 |

| opponent profile | games |
|---|---|
| chopper_aggressor | 72 |
| harvester | 96 |
| idle | 72 |

## Blocking violations

### m003 seat 0 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 16, "turn_start": 14, "unit": 2}]}

### m004 seat 0 (orchard_eligible, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 2], [9, 2]], "k": 3, "turn_end": 31, "turn_start": 24, "unit": 2}]}

### m005 seat 0 (multi_door, chopper_aggressor, seed 86028121)

- **P1**: {"count": 20, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 104, "turn_start": 101, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 108, "turn_start": 105, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 112, "turn_start": 109, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 128, "turn_start": 125, "unit": 2}]}

### m005 seat 1 (multi_door, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 129, "why": "candidate makes no own-inventory/own-cargo progress over turns 28-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 28}}

### m006 seat 0 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 1}}

### m006 seat 1 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 1}}

### m009 seat 0 (water_diagonal, harvester, seed 49979687)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 36-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 36}}

### m009 seat 1 (water_diagonal, harvester, seed 49979687)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 36-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 36}}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 1], "kind": "outside_ring", "turn_end": 15, "turn_start": 15, "unit": 2}]}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 18-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 18}}

### m015 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 14-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 14}}

### m015 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 16}}

### m016 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 13, "turn_start": 13, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 14, "turn_start": 14, "unit": 0, "verb": "PLANT"}]}

### m017 seat 0 (open_field, idle, seed 86028121)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 112, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 1}}

### m017 seat 1 (open_field, idle, seed 86028121)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 112, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 1}}

### m018 seat 0 (choke_corridor, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 114, "why": "candidate makes no own-inventory/own-cargo progress over turns 6-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 6}}

### m018 seat 1 (choke_corridor, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 117, "why": "candidate makes no own-inventory/own-cargo progress over turns 6-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 6}}

### m021 seat 0 (choke_corridor, idle, seed 49979687)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 35-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 35}}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 17, "turn_start": 15, "unit": 2}]}
- **P4**: {"detail": {"live_end": 106, "terminal_from": 135, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-106 while work remains through turn 106 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 106, "window_start": 20}}

### m022 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 121, "why": "candidate makes no own-inventory/own-cargo progress over turns 10-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 10}}

### m022 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 107, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 26}}

### m023 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 25, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 103, "turn_start": 100, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 107, "turn_start": 104, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 111, "turn_start": 108, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}]}

### m023 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 25, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 103, "turn_start": 100, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 107, "turn_start": 104, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 111, "turn_start": 108, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}]}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 0}]}

### m026 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 117, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 1}}

### m026 seat 1 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 123, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 1}}

### m028 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 36-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 36}}

### m028 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 34-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 34}}

### m030 seat 0 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 34-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 34}}

### m030 seat 1 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 35-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 35}}

### m032 seat 0 (forest_sparse, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 115, "why": "candidate makes no own-inventory/own-cargo progress over turns 13-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 13}}

### m032 seat 1 (forest_sparse, chopper_aggressor, seed 32452843)

- **P1**: {"count": 24, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 104, "turn_start": 101, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 110, "turn_start": 107, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 123, "turn_start": 120, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 200, "why": "candidate makes no own-inventory/own-cargo progress over turns 22-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 22}}

### m035 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P3**: {"detail": {"candidate": "WAIT;PICK 2 BANANA", "first_divergence_turn": 100, "parent": "WAIT;WAIT"}}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 33-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 33}}

### m035 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 25-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 25}}

### m036 seat 0 (multi_door, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 115, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 21}}

### m036 seat 1 (multi_door, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 115, "why": "candidate makes no own-inventory/own-cargo progress over turns 28-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 28}}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 51, "turn_start": 51, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PLANT"}]}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 26}}

### m040 seat 0 (forest_dense, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 4], [3, 4]], "k": 12, "turn_end": 200, "turn_start": 176, "unit": 0}]}

### m042 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 31-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 31}}

### m046 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 117, "why": "candidate makes no own-inventory/own-cargo progress over turns 31-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 31}}

### m046 seat 1 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 126, "why": "candidate makes no own-inventory/own-cargo progress over turns 22-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 22}}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m049 seat 0 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 22, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 104, "turn_start": 101, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 110, "turn_start": 107, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 116, "turn_start": 113, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 124, "turn_start": 121, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 128, "turn_start": 125, "unit": 2}]}

### m049 seat 1 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 22, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 104, "turn_start": 101, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 110, "turn_start": 107, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 116, "turn_start": 113, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 120, "turn_start": 117, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 124, "turn_start": 121, "unit": 2}]}

### m050 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 20}}

### m050 seat 1 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 112, "why": "candidate makes no own-inventory/own-cargo progress over turns 24-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 24}}

### m052 seat 0 (single_door_tent, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 20}}

### m052 seat 1 (single_door_tent, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 17-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 17}}

### m058 seat 1 (open_field, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 3], [6, 4]], "k": 6, "turn_end": 42, "turn_start": 29, "unit": 0}]}

### m059 seat 0 (choke_corridor, harvester, seed 86028121)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 11}}

### m059 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 4], [9, 3]], "k": 94, "turn_end": 200, "turn_start": 12, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 11}}

### m061 seat 0 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}]}
- **P1**: {"count": 20, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 123, "turn_start": 120, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 130, "turn_start": 127, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 134, "turn_start": 131, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 29, "turn_start": 27, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 3], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 39-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 39}}

### m061 seat 1 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 16, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 113, "turn_start": 110, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 117, "turn_start": 114, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 121, "turn_start": 118, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 130, "turn_start": 127, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 134, "turn_start": 131, "unit": 2}]}
- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 26, "turn_start": 24, "unit": 0}, {"kind": "no_progress", "turn_end": 66, "turn_start": 64, "unit": 0}]}

### m062 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 39, "turn_start": 39, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 40, "turn_start": 40, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 45, "turn_start": 45, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 46, "turn_start": 46, "unit": 0, "verb": "PLANT"}]}

### m063 seat 1 (open_field, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 3], [10, 4]], "k": 75, "turn_end": 200, "turn_start": 50, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (10, 3)<->(10, 4) over turns 50-200 (151 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 47-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 47}}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 16}}

### m064 seat 1 (single_door_tent, idle, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 18-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 18}}

### m065 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P3**: {"detail": {"candidate": "PICK 0 BANANA;PICK 2 PLUM", "first_divergence_turn": 100, "parent": "WAIT;WAIT"}}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 115, "why": "candidate makes no own-inventory/own-cargo progress over turns 23-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 23}}

### m065 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 111, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 20}}

### m066 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [4, 2]], "k": 10, "turn_end": 24, "turn_start": 3, "unit": 2}]}
- **P1**: {"count": 25, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 103, "turn_start": 100, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 107, "turn_start": 104, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 111, "turn_start": 108, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (5, 2)<->(4, 2) over turns 3-24 (22 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 200, "why": "candidate makes no own-inventory/own-cargo progress over turns 28-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 28}}

### m068 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 125, "turn_start": 122, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 154, "turn_start": 151, "unit": 2}]}

### m068 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 14, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 104, "turn_start": 101, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 110, "turn_start": 107, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 116, "turn_start": 113, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 122, "turn_start": 119, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 128, "turn_start": 125, "unit": 2}]}
- **P1**: {"count": 3, "detector": "D-6", "episodes": [{"cell": [8, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 107, "turn_start": 107, "unit": 0}, {"cell": [8, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 113, "turn_start": 113, "unit": 0}, {"cell": [8, 3], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 131, "turn_start": 131, "unit": 0}]}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 8, "turn_start": 1, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 1], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 1-8 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 2], [9, 2]], "k": 5, "turn_end": 18, "turn_start": 7, "unit": 2}]}

### m071 seat 1 (open_field, idle, seed 86028121)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 40-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 40}}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m073 seat 0 (choke_corridor, harvester, seed 15485863)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 10-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 10}}

### m073 seat 1 (choke_corridor, harvester, seed 15485863)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 24-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 24}}

### m074 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "PICK 0 BANANA;WAIT", "first_divergence_turn": 100, "parent": "WAIT;WAIT"}}

### m074 seat 1 (orchard_eligible, idle, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 112, "why": "candidate makes no own-inventory/own-cargo progress over turns 24-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 24}}

### m077 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 25, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 103, "turn_start": 100, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 107, "turn_start": 104, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 111, "turn_start": 108, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 200, "why": "candidate makes no own-inventory/own-cargo progress over turns 3-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 3}}

### m077 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 25, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 103, "turn_start": 100, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 107, "turn_start": 104, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 111, "turn_start": 108, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 200, "why": "candidate makes no own-inventory/own-cargo progress over turns 3-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 3}}

### m078 seat 0 (choke_corridor, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 20}}

### m078 seat 1 (choke_corridor, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 3], [6, 3]], "k": 3, "turn_end": 10, "turn_start": 4, "unit": 0}]}

### m082 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 16}}

### m082 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 5], [4, 5]], "k": 91, "turn_end": 200, "turn_start": 17, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (3, 5)<->(4, 5) over turns 17-200 (184 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 16}}

### m083 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 24, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 104, "turn_start": 101, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 110, "turn_start": 107, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 123, "turn_start": 120, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 200, "why": "candidate makes no own-inventory/own-cargo progress over turns 7-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 7}}

### m083 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 24, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 104, "turn_start": 101, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 110, "turn_start": 107, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 123, "turn_start": 120, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 200, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 5}}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 21, "turn_start": 19, "unit": 2}]}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [2, 4]], "k": 4, "turn_end": 25, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m086 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 25, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 103, "turn_start": 100, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 107, "turn_start": 104, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 111, "turn_start": 108, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 200, "why": "candidate makes no own-inventory/own-cargo progress over turns 37-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 37}}

### m086 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 25, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 103, "turn_start": 100, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 107, "turn_start": 104, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 111, "turn_start": 108, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 116, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 200, "why": "candidate makes no own-inventory/own-cargo progress over turns 39-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 39}}

### m088 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 14-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 14}}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 5], [3, 5]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 5)<->(3, 5) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 29-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 29}}

### m090 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 5], [6, 5]], "k": 3, "turn_end": 18, "turn_start": 11, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 19, "turn_start": 17, "unit": 0}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 112, "why": "candidate makes no own-inventory/own-cargo progress over turns 39-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 39}}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 5, "detector": "D-6", "episodes": [{"cell": [2, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 82, "turn_start": 82, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 88, "turn_start": 88, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 93, "turn_start": 93, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 98, "turn_start": 98, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 103, "turn_start": 103, "unit": 0}]}

### m092 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 3, "detector": "D-6", "episodes": [{"cell": [7, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 107, "turn_start": 107, "unit": 0}, {"cell": [7, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 113, "turn_start": 113, "unit": 0}, {"cell": [7, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 118, "turn_start": 118, "unit": 0}]}

### m094 seat 0 (single_door_tent, idle, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 21}}

### m094 seat 1 (single_door_tent, idle, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 18-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 18}}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 22, "turn_start": 22, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m097 seat 0 (water_diagonal, idle, seed 15485863)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 34-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 34}}

### m097 seat 1 (water_diagonal, idle, seed 15485863)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 40-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 40}}

### m098 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 114, "why": "candidate makes no own-inventory/own-cargo progress over turns 25-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 25}}

### m098 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 121, "why": "candidate makes no own-inventory/own-cargo progress over turns 17-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 17}}

### m099 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 24, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 104, "turn_start": 101, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 109, "turn_start": 106, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 113, "turn_start": 110, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 117, "turn_start": 114, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 121, "turn_start": 118, "unit": 2}]}

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 8-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 8}}

### m100 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 10-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 10}}

### m100 seat 1 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 112, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 26}}

### m102 seat 0 (open_field, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 112, "why": "candidate makes no own-inventory/own-cargo progress over turns 37-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 37}}

### m102 seat 1 (open_field, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 114, "why": "candidate makes no own-inventory/own-cargo progress over turns 24-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 24}}

### m104 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "WAIT;PICK 2 APPLE", "first_divergence_turn": 100, "parent": "WAIT;WAIT"}}

### m104 seat 1 (orchard_eligible, idle, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 117, "why": "candidate makes no own-inventory/own-cargo progress over turns 37-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 37}}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

### m108 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 17-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 17}}

### m109 seat 0 (water_diagonal, harvester, seed 15485863)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 115, "why": "candidate makes no own-inventory/own-cargo progress over turns 30-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 30}}

### m109 seat 1 (water_diagonal, harvester, seed 15485863)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 115, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 20}}

### m110 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 112, "why": "candidate makes no own-inventory/own-cargo progress over turns 10-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 10}}

### m110 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [5, 2]], "k": 97, "turn_end": 200, "turn_start": 6, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 1}}

### m114 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "PICK 0 BANANA;PICK 2 PLUM", "first_divergence_turn": 100, "parent": "WAIT;WAIT"}}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 115, "why": "candidate makes no own-inventory/own-cargo progress over turns 40-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 40}}

### m114 seat 1 (orchard_eligible, idle, seed 982451653)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 109, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 16}}

### m115 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 50, "turn_start": 50, "unit": 0, "verb": "PLANT"}]}

### m118 seat 0 (choke_corridor, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 16}}

### m118 seat 1 (choke_corridor, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 106, "why": "candidate makes no own-inventory/own-cargo progress over turns 18-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 18}}

## Report-tier flags (non-blocking)

- m021 seat 1 [r5-horizon]: full wood carrier since turn 12 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m082 seat 1 [r5-horizon]: full wood carrier since turn 16 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
