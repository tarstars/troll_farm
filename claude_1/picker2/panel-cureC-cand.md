# fuzz panel report [CANDIDATE (candidate vs parent)] - 20260820-pair-selector-anti-benching Phase-2 panel: P1+P2 on the cure-C base vs the cure-C matched floor

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `../../claude_1/picker2/candidate-cureC-p1p2.rs` (sha256 d127cf861ad7f145e5693b0a595bcc8e3c870f424926b18bdbb3debec80b0412)
- parent: `../../cgauto/submissions/submitted-sub41153619-cure-c-quiet.rs` (sha256 ad3bfefe4b2326f4f6b4a270dc862ea19a0e319a1cddfde44b96cc6f6d35a5d1)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 9.4 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 240 |
| clean_games | 207 |
| banana_activated_games | 23 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 12 |
| blocking_games | 33 |
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

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 1], "kind": "outside_ring", "turn_end": 15, "turn_start": 15, "unit": 2}]}

### m016 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 13, "turn_start": 13, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 14, "turn_start": 14, "unit": 0, "verb": "PLANT"}]}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 17, "turn_start": 15, "unit": 2}]}
- **P4**: {"detail": {"live_end": 106, "terminal_from": 135, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-106 while work remains through turn 106 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 106, "window_start": 20}}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 0}]}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 51, "turn_start": 51, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PLANT"}]}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 26}}

### m040 seat 1 (forest_dense, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 0], [3, 0]], "k": 3, "turn_end": 86, "turn_start": 80, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 0)<->(3, 0) over turns 80-86 (7 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 0}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m058 seat 1 (open_field, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 3], [6, 4]], "k": 7, "turn_end": 43, "turn_start": 28, "unit": 0}]}

### m059 seat 0 (choke_corridor, harvester, seed 86028121)

- **P4**: {"detail": {"live_end": 104, "terminal_from": 116, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-104 while work remains through turn 104 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 104, "window_start": 11}}

### m059 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 4], [9, 3]], "k": 94, "turn_end": 200, "turn_start": 12, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 11}}

### m061 seat 0 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 29, "turn_start": 27, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 3], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 39-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 39}}

### m061 seat 1 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 26, "turn_start": 24, "unit": 0}, {"kind": "no_progress", "turn_end": 66, "turn_start": 64, "unit": 0}]}

### m062 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 39, "turn_start": 39, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 40, "turn_start": 40, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 45, "turn_start": 45, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 46, "turn_start": 46, "unit": 0, "verb": "PLANT"}]}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}

### m066 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [4, 2]], "k": 10, "turn_end": 24, "turn_start": 3, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (5, 2)<->(4, 2) over turns 3-24 (22 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 8, "turn_start": 1, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 1], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 1-8 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 2], [9, 2]], "k": 5, "turn_end": 18, "turn_start": 7, "unit": 2}]}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m082 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 5], [4, 5]], "k": 91, "turn_end": 200, "turn_start": 17, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (3, 5)<->(4, 5) over turns 17-200 (184 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 16}}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 23, "turn_start": 21, "unit": 2}]}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [2, 4]], "k": 4, "turn_end": 25, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 5], [3, 5]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 5)<->(3, 5) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 5, "detector": "D-6", "episodes": [{"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 67, "turn_start": 67, "unit": 0}, {"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 72, "turn_start": 72, "unit": 0}, {"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 77, "turn_start": 77, "unit": 0}, {"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 82, "turn_start": 82, "unit": 0}, {"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 87, "turn_start": 87, "unit": 0}]}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 22, "turn_start": 22, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 8-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 8}}

### m106 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 11}}
- **P4**: {"detail": {"live_end": 182, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 111-182 while work remains through turn 182 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 182, "window_start": 111}}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

### m110 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [5, 2]], "k": 97, "turn_end": 200, "turn_start": 6, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 1}}

### m115 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 50, "turn_start": 50, "unit": 0, "verb": "PLANT"}]}

## Report-tier flags (non-blocking)

- m021 seat 1 [r5-horizon]: full wood carrier since turn 12 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m082 seat 1 [r5-horizon]: full wood carrier since turn 16 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
