# fuzz panel report - FABLE INDEPENDENT VERIFY: parent-vs-parent raw floor

- candidate: `/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- parent: `/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 11.5 s

## Verdict: BLOCK

## Coverage

| metric | value |
|---|---|
| games | 240 |
| banana_activated_games | 157 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 12 |
| blocking_games | 223 |
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

### m000 seat 0 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 1}}

### m000 seat 1 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 1}}

### m001 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 82, "turn_start": 82, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 83, "turn_start": 83, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 106-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 106}}

### m001 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 91, "turn_start": 91, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 114-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 114}}

### m002 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 1}}

### m002 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 36-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 36}}

### m003 seat 0 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 3], [0, 3]], "k": 88, "turn_end": 200, "turn_start": 23, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 16, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

### m003 seat 1 (single_door_tent, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 63-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 63}}

### m004 seat 0 (orchard_eligible, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 2], [9, 2]], "k": 3, "turn_end": 31, "turn_start": 24, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 59-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 59}}

### m004 seat 1 (orchard_eligible, idle, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 25-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 25}}

### m005 seat 0 (multi_door, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 53-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 53}}

### m005 seat 1 (multi_door, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 3], [0, 4]], "k": 5, "turn_end": 39, "turn_start": 29, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 53-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 53}}

### m006 seat 0 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 10-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 10}}

### m006 seat 1 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 10-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 10}}

### m008 seat 0 (forest_sparse, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 19-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 19}}

### m008 seat 1 (forest_sparse, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 20-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 20}}

### m009 seat 0 (water_diagonal, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 42-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 42}}

### m009 seat 1 (water_diagonal, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 42-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 42}}

### m010 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 116-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 116}}

### m010 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 125-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 125}}

### m011 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 143, "turn_start": 143, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 144, "turn_start": 144, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 149, "turn_start": 149, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 150, "turn_start": 150, "unit": 0, "verb": "PLANT"}]}

### m011 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 123, "turn_start": 123, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}]}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 1], "kind": "outside_ring", "turn_end": 15, "turn_start": 15, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 21-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 21}}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[12, 2], [13, 2]], "k": 4, "turn_end": 20, "turn_start": 12, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 21, "turn_start": 21, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

### m013 seat 0 (choke_corridor, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 4-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 4}}

### m013 seat 1 (choke_corridor, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 5-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 5}}

### m014 seat 0 (orchard_eligible, idle, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 25-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 25}}

### m014 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 1], [9, 1]], "k": 96, "turn_end": 200, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 5-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 5}}

### m015 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 20-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 20}}

### m015 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 7-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 7}}

### m016 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 99, "turn_start": 99, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 100, "turn_start": 100, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 105-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 105}}

### m016 seat 1 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 53, "turn_start": 53, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 54, "turn_start": 54, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 59, "turn_start": 59, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 60, "turn_start": 60, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 82-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 82}}

### m017 seat 0 (open_field, idle, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 12-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 12}}

### m017 seat 1 (open_field, idle, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 13-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 13}}

### m018 seat 0 (choke_corridor, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 8-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 8}}

### m018 seat 1 (choke_corridor, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 14-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 14}}

### m020 seat 0 (forest_sparse, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PLANT"}]}

### m020 seat 1 (forest_sparse, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 110, "turn_start": 110, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 111, "turn_start": 111, "unit": 0, "verb": "PLANT"}]}

### m021 seat 0 (choke_corridor, idle, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 42-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 42}}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 17, "turn_start": 15, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 61-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 61}}

### m022 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [2, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 11, "turn_start": 11, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 21-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 21}}

### m022 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 18-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 18}}

### m023 seat 0 (open_field, harvester, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 64-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 64}}

### m023 seat 1 (open_field, harvester, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 64-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 64}}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 79-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 79}}

### m024 seat 1 (single_door_tent, idle, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 71-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 71}}

### m025 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 35}}

### m025 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 26}}

### m026 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 18-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 18}}

### m026 seat 1 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 24-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 24}}

### m027 seat 0 (multi_door, idle, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 44-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 44}}

### m027 seat 1 (multi_door, idle, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 44-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 44}}

### m028 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

### m028 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 26}}

### m029 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 137, "turn_start": 137, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 142, "turn_start": 142, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 143, "turn_start": 143, "unit": 0, "verb": "PLANT"}]}

### m029 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 130, "turn_start": 130, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 131, "turn_start": 131, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 137, "turn_start": 137, "unit": 0, "verb": "PLANT"}]}

### m030 seat 0 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 35}}

### m030 seat 1 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 35}}

### m032 seat 0 (forest_sparse, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 30-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 30}}

### m032 seat 1 (forest_sparse, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 37-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 37}}

### m033 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 41-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 41}}

### m033 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 41-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 41}}

### m034 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 146, "turn_start": 146, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 147, "turn_start": 147, "unit": 0, "verb": "PLANT"}]}

### m034 seat 1 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m035 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 29-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 29}}

### m035 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 18-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 18}}

### m036 seat 0 (multi_door, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 35}}

### m036 seat 1 (multi_door, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 38-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 38}}

### m037 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m037 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m038 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [0, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 44, "turn_start": 44, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 44, "turn_start": 44, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 58-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 58}}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 37, "turn_start": 37, "unit": 0}, {"cell": [8, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 42, "turn_start": 42, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 50-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 50}}

### m039 seat 0 (choke_corridor, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 33-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 33}}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 8, "turn_end": 24, "turn_start": 7, "unit": 0}, {"cells": [[4, 2], [3, 2]], "k": 75, "turn_end": 200, "turn_start": 50, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 44-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 44}}

### m041 seat 0 (choke_corridor, idle, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 11}}

### m041 seat 1 (choke_corridor, idle, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

### m042 seat 0 (water_diagonal, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 29-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 29}}

### m042 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 33-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 33}}

### m043 seat 0 (open_field, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 56, "turn_start": 56, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 57, "turn_start": 57, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 112-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 112}}

### m043 seat 1 (open_field, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 89, "turn_start": 89, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 95, "turn_start": 95, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 96, "turn_start": 96, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 101-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 101}}

### m044 seat 0 (single_door_tent, idle, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 134, "turn_start": 134, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PLANT"}]}

### m044 seat 1 (single_door_tent, idle, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 108, "turn_start": 108, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m045 seat 0 (orchard_eligible, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 1}}

### m045 seat 1 (orchard_eligible, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 18-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 18}}

### m046 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 2], [6, 2]], "k": 93, "turn_end": 200, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 11}}

### m046 seat 1 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 43-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 43}}

### m047 seat 0 (multi_door, idle, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 104-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 104}}

### m047 seat 1 (multi_door, idle, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 124-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 124}}

### m048 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 26, "turn_start": 26, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 25, "turn_start": 25, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 34-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 34}}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 7, "turn_start": 7, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 8, "turn_start": 8, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

### m049 seat 0 (water_diagonal, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 98-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 98}}

### m049 seat 1 (water_diagonal, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 61-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 61}}

### m050 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 26}}

### m050 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [6, 2]], "k": 77, "turn_end": 169, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 12-170 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 170, "window_start": 12}}

### m051 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m051 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m052 seat 0 (single_door_tent, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 28-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 28}}

### m052 seat 1 (single_door_tent, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 26}}

### m053 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 53, "turn_start": 53, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 58, "turn_start": 58, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 59, "turn_start": 59, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 91-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 91}}

### m053 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 63, "turn_start": 63, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 64, "turn_start": 64, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 69, "turn_start": 69, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 70, "turn_start": 70, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 93-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 93}}

### m054 seat 0 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 77, "turn_start": 77, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 78, "turn_start": 78, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 106-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 106}}

### m054 seat 1 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 58-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 58}}

### m055 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 1}}

### m055 seat 1 (multi_door, chopper_aggressor, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 28-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 28}}

### m057 seat 0 (water_diagonal, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 109, "turn_start": 109, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 110, "turn_start": 110, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 132-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 132}}

### m057 seat 1 (water_diagonal, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 66, "turn_start": 66, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 88-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 88}}

### m058 seat 0 (open_field, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 28-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 28}}

### m058 seat 1 (open_field, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 35}}

### m059 seat 0 (choke_corridor, harvester, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 11}}

### m059 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 4], [9, 3]], "k": 94, "turn_end": 200, "turn_start": 12, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 11}}

### m060 seat 0 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 5], [6, 5]], "k": 78, "turn_end": 200, "turn_start": 44, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 37-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 37}}

### m060 seat 1 (forest_sparse, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 47-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 47}}

### m061 seat 0 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 3], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 92-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 92}}

### m061 seat 1 (choke_corridor, idle, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 107-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 107}}

### m062 seat 0 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 17, "turn_start": 17, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 18, "turn_start": 18, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 23, "turn_start": 23, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 24, "turn_start": 24, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 52-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 52}}

### m062 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 39, "turn_start": 39, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 44, "turn_start": 44, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 45, "turn_start": 45, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 50-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 50}}

### m063 seat 0 (open_field, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 59-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 59}}

### m063 seat 1 (open_field, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 54-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 54}}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 25-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 25}}

### m064 seat 1 (single_door_tent, idle, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 20-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 20}}

### m065 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 19-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 19}}

### m065 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 1], [9, 1]], "k": 5, "turn_end": 20, "turn_start": 9, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 33-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 33}}

### m066 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [4, 2]], "k": 10, "turn_end": 24, "turn_start": 3, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (5, 2)<->(4, 2) over turns 3-24 (22 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 32-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 32}}

### m066 seat 1 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 50-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 50}}

### m067 seat 0 (multi_door, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 92, "turn_start": 92, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 93, "turn_start": 93, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 133-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 133}}

### m067 seat 1 (multi_door, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 111, "turn_start": 111, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 112, "turn_start": 112, "unit": 0, "verb": "PLANT"}]}

### m068 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [3, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 70, "turn_start": 70, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 106-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 106}}

### m068 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 6, "detector": "D-6", "episodes": [{"cell": [9, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 84, "turn_start": 84, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 108, "turn_start": 108, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 113, "turn_start": 113, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 116, "turn_start": 116, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 119, "turn_start": 119, "unit": 0}]}

### m069 seat 0 (water_diagonal, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 110-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 110}}

### m069 seat 1 (water_diagonal, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 86-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 86}}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 8, "turn_start": 1, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 1], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 1-8 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 38-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 38}}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 2], [9, 2]], "k": 5, "turn_end": 18, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 56-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 56}}

### m071 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 4], [8, 4]], "k": 78, "turn_end": 200, "turn_start": 44, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 32-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 32}}

### m071 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[11, 4], [10, 4]], "k": 36, "turn_end": 100, "turn_start": 27, "unit": 2}, {"cells": [[10, 4], [11, 4]], "k": 47, "turn_end": 200, "turn_start": 106, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 26-99 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 99, "window_start": 26}}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 106-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 106}}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 25, "turn_start": 25, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 48-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 48}}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 45-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 45}}

### m073 seat 0 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 2], [2, 2]], "k": 31, "turn_end": 67, "turn_start": 5, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 5-66 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 66, "window_start": 5}}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 73-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 73}}

### m073 seat 1 (choke_corridor, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 13-108 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 108, "window_start": 13}}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 119-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 119}}

### m074 seat 0 (orchard_eligible, idle, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 48-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 48}}

### m074 seat 1 (orchard_eligible, idle, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 30-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 30}}

### m075 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 5], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 35, "turn_start": 35, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 34, "turn_start": 34, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 36-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 36}}

### m075 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 48-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 48}}

### m076 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 91, "turn_start": 91, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 122-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 122}}

### m076 seat 1 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 88, "turn_start": 88, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 89, "turn_start": 89, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 129-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 129}}

### m077 seat 0 (open_field, idle, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 10-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 10}}

### m077 seat 1 (open_field, idle, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 10-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 10}}

### m078 seat 0 (choke_corridor, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 3], [2, 3]], "k": 3, "turn_end": 18, "turn_start": 12, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 29-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 29}}

### m078 seat 1 (choke_corridor, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 28-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 28}}

### m079 seat 0 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 81, "turn_end": 200, "turn_start": 38, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 33-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 33}}

### m079 seat 1 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 82, "turn_end": 197, "turn_start": 33, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 31-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 31}}

### m081 seat 0 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 59-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 59}}

### m081 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 66, "turn_start": 66, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 89-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 89}}

### m082 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 15-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 15}}

### m082 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 17-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 17}}

### m083 seat 0 (open_field, harvester, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

### m083 seat 1 (open_field, harvester, seed 86028121)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 23, "turn_start": 21, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 70-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 70}}

### m084 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 5], [6, 5]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 26}}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [2, 4]], "k": 3, "turn_end": 23, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 38-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 38}}

### m085 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 56, "turn_start": 56, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 57, "turn_start": 57, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 71-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 71}}

### m086 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 46-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 46}}

### m086 seat 1 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 48-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 48}}

### m087 seat 0 (multi_door, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 58-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 58}}

### m087 seat 1 (multi_door, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 58-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 58}}

### m088 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 18-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 18}}

### m088 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [4, 2]], "k": 4, "turn_end": 17, "turn_start": 9, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 26}}

### m089 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PLANT"}]}

### m089 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[4, 5], [3, 5]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}, {"cells": [[3, 5], [4, 5]], "k": 86, "turn_end": 189, "turn_start": 17, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 5)<->(3, 5) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 12-190 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 190, "window_start": 12}}

### m090 seat 1 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 45-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 45}}

### m091 seat 0 (forest_sparse, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 67, "turn_start": 67, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 68, "turn_start": 68, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 91-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 91}}

### m091 seat 1 (forest_sparse, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 61, "turn_start": 61, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 62, "turn_start": 62, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 94-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 94}}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 1], [0, 0]], "k": 17, "turn_end": 36, "turn_start": 2, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 79-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 79}}

### m092 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 55-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 55}}

### m093 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 41-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 41}}

### m093 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 41-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 41}}

### m094 seat 0 (single_door_tent, idle, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 21-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 21}}

### m094 seat 1 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 0], [6, 0]], "k": 95, "turn_end": 200, "turn_start": 10, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 1}}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 15, "turn_start": 15, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 16, "turn_start": 16, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 22, "turn_start": 22, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 44-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 44}}

### m095 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 28, "turn_start": 28, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 23, "turn_start": 23, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 24, "turn_start": 24, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 46-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 46}}

### m096 seat 0 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 105, "turn_start": 105, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 128-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 128}}

### m096 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 117, "turn_start": 117, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 118, "turn_start": 118, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 140-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 140}}

### m097 seat 0 (water_diagonal, idle, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 35}}

### m097 seat 1 (water_diagonal, idle, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 40-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 40}}

### m098 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 32-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 32}}

### m098 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 34-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 34}}

### m099 seat 0 (choke_corridor, harvester, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 57-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 57}}

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 2], [10, 2]], "k": 96, "turn_end": 200, "turn_start": 8, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 8-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 8}}

### m100 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 6-99 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 99, "window_start": 6}}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 110-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 110}}

### m100 seat 1 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 38-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 38}}

### m101 seat 0 (water_diagonal, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 77, "turn_start": 77, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 78, "turn_start": 78, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 100-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 100}}

### m101 seat 1 (water_diagonal, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 124, "turn_start": 124, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 125, "turn_start": 125, "unit": 0, "verb": "PLANT"}]}

### m102 seat 0 (open_field, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 46-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 46}}

### m102 seat 1 (open_field, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 36-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 36}}

### m103 seat 0 (single_door_tent, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 35}}

### m103 seat 1 (single_door_tent, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 33-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 33}}

### m104 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [10, 3]], "k": 85, "turn_end": 200, "turn_start": 29, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 26}}

### m105 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 24-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 24}}

### m105 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 39-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 39}}

### m106 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 11}}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 38-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 38}}

### m108 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 27-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 27}}

### m108 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 21-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 21}}

### m109 seat 0 (water_diagonal, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 45-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 45}}

### m109 seat 1 (water_diagonal, harvester, seed 15485863)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 35}}

### m110 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

### m110 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [5, 2]], "k": 97, "turn_end": 200, "turn_start": 6, "unit": 0}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 1}}

### m111 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 59-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 59}}

### m111 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 59-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 59}}

### m112 seat 0 (single_door_tent, chopper_aggressor, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 47, "turn_start": 47, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 48, "turn_start": 48, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 49-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 49}}

### m112 seat 1 (single_door_tent, chopper_aggressor, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 48, "turn_start": 48, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 54-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 54}}

### m113 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 47-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 47}}

### m113 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 47-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 47}}

### m114 seat 0 (orchard_eligible, idle, seed 982451653)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 40-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 40}}

### m114 seat 1 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [10, 3]], "k": 96, "turn_end": 200, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 1}}

### m115 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 50, "turn_start": 50, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 57-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 57}}

### m115 seat 1 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 64, "turn_start": 64, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 89-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 89}}

### m116 seat 0 (water_diagonal, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PLANT"}]}

### m116 seat 1 (water_diagonal, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PLANT"}]}

### m117 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 181, "turn_start": 181, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 182, "turn_start": 182, "unit": 0, "verb": "PLANT"}]}

### m117 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 151, "turn_start": 151, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 152, "turn_start": 152, "unit": 0, "verb": "PLANT"}]}

### m118 seat 0 (choke_corridor, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 14-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 14}}

### m118 seat 1 (choke_corridor, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 6], [6, 6]], "k": 3, "turn_end": 14, "turn_start": 8, "unit": 2}]}
- **P4**: {"detail": {"why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 (>= 60 turns) [RAW liveness: every stall window blocks, no parent exemption]", "window_end": 199, "window_start": 22}}

---

**VERDICT: BLOCK**
