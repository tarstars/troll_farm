# fuzz panel report - FABLE VERIFY#2: floor after P4 calibration

- candidate: `/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- parent: `/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 11.4 s

## Verdict: BLOCK

## Coverage

| metric | value |
|---|---|
| games | 240 |
| banana_activated_games | 157 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 12 |
| blocking_games | 118 |
| flagged_games | 0 |

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

### m001 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 82, "turn_start": 82, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 83, "turn_start": 83, "unit": 0, "verb": "PLANT"}]}

### m001 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 91, "turn_start": 91, "unit": 0, "verb": "PLANT"}]}

### m003 seat 0 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 3], [0, 3]], "k": 88, "turn_end": 200, "turn_start": 23, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 16, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 22}}

### m004 seat 0 (orchard_eligible, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 2], [9, 2]], "k": 3, "turn_end": 31, "turn_start": 24, "unit": 2}]}

### m005 seat 1 (multi_door, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 3], [0, 4]], "k": 5, "turn_end": 39, "turn_start": 29, "unit": 0}]}

### m010 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}

### m010 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}

### m011 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 143, "turn_start": 143, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 144, "turn_start": 144, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 149, "turn_start": 149, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 150, "turn_start": 150, "unit": 0, "verb": "PLANT"}]}

### m011 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 123, "turn_start": 123, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}]}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 1], "kind": "outside_ring", "turn_end": 15, "turn_start": 15, "unit": 2}]}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[12, 2], [13, 2]], "k": 4, "turn_end": 20, "turn_start": 12, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 21, "turn_start": 21, "unit": 0}]}

### m014 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 1], [9, 1]], "k": 96, "turn_end": 200, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 5}}

### m016 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 99, "turn_start": 99, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 100, "turn_start": 100, "unit": 0, "verb": "PLANT"}]}

### m016 seat 1 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 53, "turn_start": 53, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 54, "turn_start": 54, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 59, "turn_start": 59, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 60, "turn_start": 60, "unit": 0, "verb": "PLANT"}]}

### m020 seat 0 (forest_sparse, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PLANT"}]}

### m020 seat 1 (forest_sparse, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 110, "turn_start": 110, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 111, "turn_start": 111, "unit": 0, "verb": "PLANT"}]}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 17, "turn_start": 15, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 61-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 61}}

### m022 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [2, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 11, "turn_start": 11, "unit": 0}]}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 0}]}

### m029 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 137, "turn_start": 137, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 142, "turn_start": 142, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 143, "turn_start": 143, "unit": 0, "verb": "PLANT"}]}

### m029 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 130, "turn_start": 130, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 131, "turn_start": 131, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 137, "turn_start": 137, "unit": 0, "verb": "PLANT"}]}

### m033 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m033 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m034 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 146, "turn_start": 146, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 147, "turn_start": 147, "unit": 0, "verb": "PLANT"}]}

### m034 seat 1 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m037 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m037 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m038 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [0, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 44, "turn_start": 44, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 44, "turn_start": 44, "unit": 0, "verb": "PLANT"}]}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 37, "turn_start": 37, "unit": 0}, {"cell": [8, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 42, "turn_start": 42, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 8, "turn_end": 24, "turn_start": 7, "unit": 0}, {"cells": [[4, 2], [3, 2]], "k": 75, "turn_end": 200, "turn_start": 50, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 44-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 44}}

### m043 seat 0 (open_field, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 56, "turn_start": 56, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 57, "turn_start": 57, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PLANT"}]}

### m043 seat 1 (open_field, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 89, "turn_start": 89, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 95, "turn_start": 95, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 96, "turn_start": 96, "unit": 0, "verb": "PLANT"}]}

### m044 seat 0 (single_door_tent, idle, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 134, "turn_start": 134, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PLANT"}]}

### m044 seat 1 (single_door_tent, idle, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 108, "turn_start": 108, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m046 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 2], [6, 2]], "k": 93, "turn_end": 200, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m048 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 26, "turn_start": 26, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 25, "turn_start": 25, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PLANT"}]}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 7, "turn_start": 7, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 8, "turn_start": 8, "unit": 0, "verb": "PLANT"}]}

### m050 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [6, 2]], "k": 77, "turn_end": 169, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"live_end": 170, "terminal_from": 189, "why": "candidate makes no own-inventory/own-cargo progress over turns 12-170 while work remains through turn 170 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 170, "window_start": 12}}

### m051 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m051 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m053 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 53, "turn_start": 53, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 58, "turn_start": 58, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 59, "turn_start": 59, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 91-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 91}}

### m053 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 63, "turn_start": 63, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 64, "turn_start": 64, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 69, "turn_start": 69, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 70, "turn_start": 70, "unit": 0, "verb": "PLANT"}]}

### m054 seat 0 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 77, "turn_start": 77, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 78, "turn_start": 78, "unit": 0, "verb": "PLANT"}]}

### m054 seat 1 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m057 seat 0 (water_diagonal, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 109, "turn_start": 109, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 110, "turn_start": 110, "unit": 0, "verb": "PLANT"}]}

### m057 seat 1 (water_diagonal, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 66, "turn_start": 66, "unit": 0, "verb": "PLANT"}]}

### m059 seat 0 (choke_corridor, harvester, seed 86028121)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m059 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 4], [9, 3]], "k": 94, "turn_end": 200, "turn_start": 12, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m060 seat 0 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 5], [6, 5]], "k": 78, "turn_end": 200, "turn_start": 44, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 37-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 37}}

### m061 seat 0 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 3], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m062 seat 0 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 17, "turn_start": 17, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 18, "turn_start": 18, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 23, "turn_start": 23, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 24, "turn_start": 24, "unit": 0, "verb": "PLANT"}]}

### m062 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 39, "turn_start": 39, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 44, "turn_start": 44, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 45, "turn_start": 45, "unit": 0, "verb": "PLANT"}]}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}

### m065 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 1], [9, 1]], "k": 5, "turn_end": 20, "turn_start": 9, "unit": 2}]}

### m066 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [4, 2]], "k": 10, "turn_end": 24, "turn_start": 3, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (5, 2)<->(4, 2) over turns 3-24 (22 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m067 seat 0 (multi_door, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 92, "turn_start": 92, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 93, "turn_start": 93, "unit": 0, "verb": "PLANT"}]}

### m067 seat 1 (multi_door, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 111, "turn_start": 111, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 112, "turn_start": 112, "unit": 0, "verb": "PLANT"}]}

### m068 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [3, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 70, "turn_start": 70, "unit": 0}]}

### m068 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 6, "detector": "D-6", "episodes": [{"cell": [9, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 84, "turn_start": 84, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 108, "turn_start": 108, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 113, "turn_start": 113, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 116, "turn_start": 116, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 119, "turn_start": 119, "unit": 0}]}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 8, "turn_start": 1, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 1], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 1-8 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 2], [9, 2]], "k": 5, "turn_end": 18, "turn_start": 7, "unit": 2}]}

### m071 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 4], [8, 4]], "k": 78, "turn_end": 200, "turn_start": 44, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 32-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 32}}

### m071 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[11, 4], [10, 4]], "k": 36, "turn_end": 100, "turn_start": 27, "unit": 2}, {"cells": [[10, 4], [11, 4]], "k": 47, "turn_end": 200, "turn_start": 106, "unit": 2}]}
- **P4**: {"detail": {"live_end": 99, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 26}}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 106-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 106}}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 25, "turn_start": 25, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PLANT"}]}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}

### m073 seat 0 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 2], [2, 2]], "k": 31, "turn_end": 67, "turn_start": 5, "unit": 0}]}
- **P4**: {"detail": {"live_end": 66, "terminal_from": 73, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-66 while work remains through turn 66 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 66, "window_start": 5}}

### m073 seat 1 (choke_corridor, harvester, seed 15485863)

- **P4**: {"detail": {"live_end": 108, "terminal_from": 119, "why": "candidate makes no own-inventory/own-cargo progress over turns 13-108 while work remains through turn 108 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 108, "window_start": 13}}

### m075 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 5], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 35, "turn_start": 35, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 34, "turn_start": 34, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PLANT"}]}

### m075 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PLANT"}]}

### m076 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 91, "turn_start": 91, "unit": 0, "verb": "PLANT"}]}

### m076 seat 1 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 88, "turn_start": 88, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 89, "turn_start": 89, "unit": 0, "verb": "PLANT"}]}

### m078 seat 0 (choke_corridor, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 3], [2, 3]], "k": 3, "turn_end": 18, "turn_start": 12, "unit": 2}]}

### m079 seat 0 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 81, "turn_end": 200, "turn_start": 38, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 33-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 33}}

### m079 seat 1 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 82, "turn_end": 197, "turn_start": 33, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 31-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 31}}

### m081 seat 0 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m081 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 66, "turn_start": 66, "unit": 0, "verb": "PLANT"}]}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 23, "turn_start": 21, "unit": 2}]}

### m084 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 5], [6, 5]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 26}}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [2, 4]], "k": 3, "turn_end": 23, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m085 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 56, "turn_start": 56, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 57, "turn_start": 57, "unit": 0, "verb": "PLANT"}]}

### m087 seat 0 (multi_door, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 58-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 58}}

### m087 seat 1 (multi_door, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m088 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [4, 2]], "k": 4, "turn_end": 17, "turn_start": 9, "unit": 2}]}

### m089 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PLANT"}]}

### m089 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[4, 5], [3, 5]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}, {"cells": [[3, 5], [4, 5]], "k": 86, "turn_end": 189, "turn_start": 17, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 5)<->(3, 5) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 190, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 12-190 while work remains through turn 190 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 190, "window_start": 12}}

### m091 seat 0 (forest_sparse, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 67, "turn_start": 67, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 68, "turn_start": 68, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 91-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 91}}

### m091 seat 1 (forest_sparse, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 61, "turn_start": 61, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 62, "turn_start": 62, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 94-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 94}}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 1], [0, 0]], "k": 17, "turn_end": 36, "turn_start": 2, "unit": 0}]}

### m093 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m093 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m094 seat 1 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 0], [6, 0]], "k": 95, "turn_end": 200, "turn_start": 10, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 15, "turn_start": 15, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 16, "turn_start": 16, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 22, "turn_start": 22, "unit": 0, "verb": "PLANT"}]}

### m095 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 28, "turn_start": 28, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 23, "turn_start": 23, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 24, "turn_start": 24, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m096 seat 0 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 105, "turn_start": 105, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PLANT"}]}

### m096 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 117, "turn_start": 117, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 118, "turn_start": 118, "unit": 0, "verb": "PLANT"}]}

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 2], [10, 2]], "k": 96, "turn_end": 200, "turn_start": 8, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 8-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 8}}

### m100 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 110, "why": "candidate makes no own-inventory/own-cargo progress over turns 6-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 6}}

### m101 seat 0 (water_diagonal, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 77, "turn_start": 77, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 78, "turn_start": 78, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 100-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 100}}

### m101 seat 1 (water_diagonal, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 124, "turn_start": 124, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 125, "turn_start": 125, "unit": 0, "verb": "PLANT"}]}

### m104 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [10, 3]], "k": 85, "turn_end": 200, "turn_start": 29, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 26}}

### m106 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

### m110 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [5, 2]], "k": 97, "turn_end": 200, "turn_start": 6, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m111 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m111 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m112 seat 0 (single_door_tent, chopper_aggressor, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 47, "turn_start": 47, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 48, "turn_start": 48, "unit": 0, "verb": "PLANT"}]}

### m112 seat 1 (single_door_tent, chopper_aggressor, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 48, "turn_start": 48, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PLANT"}]}

### m113 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}

### m113 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}

### m114 seat 1 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [10, 3]], "k": 96, "turn_end": 200, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m115 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 50, "turn_start": 50, "unit": 0, "verb": "PLANT"}]}

### m115 seat 1 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 64, "turn_start": 64, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PLANT"}]}

### m116 seat 0 (water_diagonal, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PLANT"}]}

### m116 seat 1 (water_diagonal, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PLANT"}]}

### m117 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 181, "turn_start": 181, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 182, "turn_start": 182, "unit": 0, "verb": "PLANT"}]}

### m117 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 151, "turn_start": 151, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 152, "turn_start": 152, "unit": 0, "verb": "PLANT"}]}

### m118 seat 1 (choke_corridor, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 6], [6, 6]], "k": 3, "turn_end": 14, "turn_start": 8, "unit": 2}]}

---

**VERDICT: BLOCK**
