# fuzz panel report [CANDIDATE (candidate vs parent)] - separate renewable banana farm validation

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `c786b6ed46a57084983ad3206a6ff0c2aa7e1d0818500caaed85a4d82e724cb2`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `submission.rs` (sha256 5a74f6b36381c8f9eee953470f6959a75a2d88835f934f61d04de0485f8401fb)
- parent: `/home/tarstars/prj/troll_farm/readable/denial-off-champion.rs` (sha256 4ce3d1e85e8962d84c0ecb1a071de46e844d24f7dbe5a31bd6ca0579db552143)
- seeds: [982451653, 15485863, 32452843, 49979687]
- maps: 40 (x2 seats = 80 candidate games + 80 parent games), 300 turns each
- wall time: 12.7 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 80 |
| clean_games | 23 |
| banana_activated_games | 53 |
| orchard_eligible_games | 4 |
| orchard_inertness_checks_passed | 3 |
| blocking_games | 57 |
| flagged_games | 0 |
| instrument_invalid_games | 0 |
| parent_instrument_invalid_games | 0 |
| gate_unready_games | 0 |
| unsupported_command_games | 0 |
| malformed_command_games | 0 |
| games_with_a_successful_train | 0 |
| successful_train_events | 0 |

| class | games |
|---|---|
| choke_corridor | 20 |
| forest_dense | 6 |
| forest_sparse | 6 |
| multi_door | 8 |
| open_field | 12 |
| orchard_eligible | 8 |
| single_door_tent | 8 |
| water_diagonal | 12 |

| opponent profile | games |
|---|---|
| chopper_aggressor | 24 |
| harvester | 32 |
| idle | 24 |

## Blocking violations

### m001 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m001 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m003 seat 0 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 16, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 150, "why": "candidate makes no own-inventory/own-cargo progress over turns 41-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 41}}

### m003 seat 1 (single_door_tent, harvester, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 144, "why": "candidate makes no own-inventory/own-cargo progress over turns 45-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 45}}

### m004 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "PICK 0 LEMON", "first_divergence_turn": 149, "parent": "WAIT"}}

### m005 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 129, "why": "candidate makes no own-inventory/own-cargo progress over turns 31-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 31}}

### m005 seat 1 (multi_door, chopper_aggressor, seed 15485863)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 143, "why": "candidate makes no own-inventory/own-cargo progress over turns 23-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 23}}

### m006 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[2, 6], [3, 6]], "k": 50, "turn_end": 111, "turn_start": 11, "unit": 0}, {"cells": [[4, 6], [5, 6]], "k": 77, "turn_end": 281, "turn_start": 127, "unit": 0}]}
- **P4**: {"detail": {"live_end": 111, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 10-111 while work remains through turn 111 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 111, "window_start": 10}}
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 124-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 124}}

### m006 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[9, 6], [8, 6]], "k": 56, "turn_end": 122, "turn_start": 10, "unit": 0}, {"cells": [[7, 6], [6, 6]], "k": 71, "turn_end": 282, "turn_start": 140, "unit": 0}]}
- **P4**: {"detail": {"live_end": 123, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 8-123 while work remains through turn 123 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 123, "window_start": 8}}
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 136-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 136}}

### m007 seat 0 (forest_dense, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 131, "turn_start": 131, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 132, "turn_start": 132, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 137, "turn_start": 137, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 138, "turn_start": 138, "unit": 0, "verb": "PLANT"}]}

### m007 seat 1 (forest_dense, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 131, "turn_start": 131, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 132, "turn_start": 132, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 137, "turn_start": 137, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 138, "turn_start": 138, "unit": 0, "verb": "PLANT"}]}

### m008 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 134, "why": "candidate makes no own-inventory/own-cargo progress over turns 28-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 28}}

### m008 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 122, "turn_start": 122, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 134, "why": "candidate makes no own-inventory/own-cargo progress over turns 27-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 27}}

### m009 seat 0 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m009 seat 1 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 136, "why": "candidate makes no own-inventory/own-cargo progress over turns 58-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 58}}

### m010 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 2], [4, 2]], "k": 4, "turn_end": 14, "turn_start": 6, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (3, 2)<->(4, 2) over turns 6-14 (9 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 0}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 127, "why": "candidate makes no own-inventory/own-cargo progress over turns 44-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 44}}

### m010 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 2], [8, 2]], "k": 8, "turn_end": 38, "turn_start": 21, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (7, 2)<->(8, 2) over turns 21-38 (18 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 0}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 127, "why": "candidate makes no own-inventory/own-cargo progress over turns 41-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 41}}

### m011 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m011 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 1], "kind": "outside_ring", "turn_end": 15, "turn_start": 15, "unit": 2}]}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[12, 2], [13, 2]], "k": 10, "turn_end": 32, "turn_start": 12, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [13, 1], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 47, "turn_start": 47, "unit": 2}]}

### m014 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 1], [9, 1]], "k": 57, "turn_end": 121, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 124, "terminal_from": 130, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-124 while work remains through turn 124 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 124, "window_start": 5}}

### m015 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 127, "why": "candidate makes no own-inventory/own-cargo progress over turns 14-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 14}}

### m015 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 127, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 16}}

### m016 seat 0 (water_diagonal, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m016 seat 1 (water_diagonal, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 146, "turn_start": 146, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 147, "turn_start": 147, "unit": 0, "verb": "PLANT"}]}

### m017 seat 0 (open_field, idle, seed 15485863)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 144, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 21}}

### m017 seat 1 (open_field, idle, seed 15485863)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 144, "why": "candidate makes no own-inventory/own-cargo progress over turns 24-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 24}}

### m018 seat 0 (choke_corridor, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [1, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 122, "turn_start": 122, "unit": 0}, {"cell": [1, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 127, "turn_start": 127, "unit": 0}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 131, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 11}}

### m019 seat 0 (forest_dense, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 125, "turn_start": 125, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PLANT"}]}

### m019 seat 1 (forest_dense, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 133, "turn_start": 133, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 134, "turn_start": 134, "unit": 0, "verb": "PLANT"}]}

### m020 seat 0 (forest_sparse, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 127, "why": "candidate makes no own-inventory/own-cargo progress over turns 15-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 15}}

### m020 seat 1 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 3], [0, 3]], "k": 33, "turn_end": 88, "turn_start": 22, "unit": 0}]}
- **P4**: {"detail": {"live_end": 86, "terminal_from": 127, "why": "candidate makes no own-inventory/own-cargo progress over turns 12-86 while work remains through turn 86 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 86, "window_start": 12}}

### m021 seat 0 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 150, "why": "candidate makes no own-inventory/own-cargo progress over turns 46-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 46}}

### m021 seat 1 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 150, "why": "candidate makes no own-inventory/own-cargo progress over turns 58-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 58}}

### m022 seat 0 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 144, "why": "candidate makes no own-inventory/own-cargo progress over turns 17-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 17}}

### m022 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 144, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 20}}

### m023 seat 1 (open_field, harvester, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 144, "why": "candidate makes no own-inventory/own-cargo progress over turns 57-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 57}}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 0}]}

### m026 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 138, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 1}}

### m026 seat 1 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 144, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 1}}

### m027 seat 0 (multi_door, idle, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 130, "why": "candidate makes no own-inventory/own-cargo progress over turns 22-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 22}}

### m027 seat 1 (multi_door, idle, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 130, "why": "candidate makes no own-inventory/own-cargo progress over turns 18-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 18}}

### m028 seat 0 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 25, "turn_start": 25, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PLANT"}]}

### m028 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 31, "turn_start": 31, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 32, "turn_start": 32, "unit": 0, "verb": "PLANT"}]}

### m030 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 142, "why": "candidate makes no own-inventory/own-cargo progress over turns 37-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 37}}

### m030 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 8, "turn_start": 6, "unit": 2}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 142, "why": "candidate makes no own-inventory/own-cargo progress over turns 35-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 35}}

### m033 seat 0 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}

### m033 seat 1 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}

### m035 seat 1 (orchard_eligible, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 142, "why": "candidate makes no own-inventory/own-cargo progress over turns 52-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 52}}

### m036 seat 0 (multi_door, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 136, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 21}}

### m036 seat 1 (multi_door, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 136, "why": "candidate makes no own-inventory/own-cargo progress over turns 28-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 28}}

### m037 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m037 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m038 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [0, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 128, "turn_start": 128, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 150, "why": "candidate makes no own-inventory/own-cargo progress over turns 38-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 38}}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 51, "turn_start": 51, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PLANT"}]}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 128, "turn_end": 288, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 26}}

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
