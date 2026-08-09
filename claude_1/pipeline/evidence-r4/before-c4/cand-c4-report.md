# fuzz panel report - 20260802-banana-restoration-r2 fuzz panel (candidate eac2eb36 vs parent a8eb3b2b)

- instrument: `fuzz-panel/4-engine-conformant-referee`  |  corpus: `c4-engine-conformant-referee-2026-08-10`
- referee sha256: `a333bd6641cebde2503158154338706456b2d16995e6178e6583d11f859fdfa2`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/before-r3/claude_1/banana-restoration-r2/candidate-banana-r2.min.rs` (sha256 eac2eb36b5f2abf0e92b62615584f3d9135055a09e6eec0bbee7c4e4a6a4f23b)
- parent: `/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 17.1 s

## Verdict: BLOCK

## Coverage

| metric | value |
|---|---|
| games | 240 |
| clean_games | 117 |
| banana_activated_games | 172 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 12 |
| blocking_games | 123 |
| flagged_games | 0 |
| instrument_invalid_games | 0 |
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

### m001 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 82, "turn_start": 82, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 83, "turn_start": 83, "unit": 0, "verb": "PLANT"}]}

### m001 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 91, "turn_start": 91, "unit": 0, "verb": "PLANT"}]}

### m003 seat 1 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 3], [0, 3]], "k": 79, "turn_end": 200, "turn_start": 41, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 34-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 34}}

### m004 seat 0 (orchard_eligible, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 2], [9, 2]], "k": 3, "turn_end": 31, "turn_start": 24, "unit": 2}]}

### m005 seat 1 (multi_door, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 3], [0, 4]], "k": 5, "turn_end": 39, "turn_start": 29, "unit": 0}]}

### m007 seat 0 (forest_dense, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 4], [3, 4]], "k": 17, "turn_end": 200, "turn_start": 165, "unit": 0}]}

### m010 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}

### m010 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}

### m011 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 143, "turn_start": 143, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 144, "turn_start": 144, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 149, "turn_start": 149, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 150, "turn_start": 150, "unit": 0, "verb": "PLANT"}]}

### m011 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 123, "turn_start": 123, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}]}

### m014 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 1], [9, 1]], "k": 96, "turn_end": 200, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 5}}

### m016 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 99, "turn_start": 99, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 100, "turn_start": 100, "unit": 0, "verb": "PLANT"}]}

### m016 seat 1 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 53, "turn_start": 53, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 54, "turn_start": 54, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 59, "turn_start": 59, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 60, "turn_start": 60, "unit": 0, "verb": "PLANT"}]}

### m017 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[0, 3], [0, 2]], "k": 4, "turn_end": 93, "turn_start": 85, "unit": 2}, {"cells": [[1, 3], [0, 3]], "k": 4, "turn_end": 121, "turn_start": 113, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 127-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 127}}

### m017 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 4], [10, 4]], "k": 4, "turn_end": 121, "turn_start": 113, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 127-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 127}}

### m020 seat 0 (forest_sparse, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PLANT"}]}

### m020 seat 1 (forest_sparse, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 110, "turn_start": 110, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 111, "turn_start": 111, "unit": 0, "verb": "PLANT"}]}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 24, "turn_start": 22, "unit": 2}]}

### m024 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[9, 3], [8, 3]], "k": 4, "turn_end": 57, "turn_start": 49, "unit": 2}, {"cells": [[9, 3], [8, 3]], "k": 3, "turn_end": 102, "turn_start": 96, "unit": 2}]}

### m025 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 6], [9, 6]], "k": 4, "turn_end": 27, "turn_start": 18, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [12, 5], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 49, "turn_start": 49, "unit": 0}, {"cell": [13, 6], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 49, "turn_start": 49, "unit": 2}]}

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

### m035 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [13, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 39, "turn_start": 39, "unit": 0}]}

### m036 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 11, "detector": "D-6", "episodes": [{"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 39, "turn_start": 38, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 67, "turn_start": 66, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 68, "turn_start": 67, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 96, "turn_start": 95, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 97, "turn_start": 96, "unit": n
- **P4**: {"detail": {"live_end": 99, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 38-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 38}}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 109-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 109}}

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
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 44-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 44}}

### m042 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 0], [11, 1]], "k": 18, "turn_end": 64, "turn_start": 28, "unit": 2}]}

### m043 seat 0 (open_field, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 95, "turn_start": 95, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 96, "turn_start": 96, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 101, "turn_start": 101, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 102, "turn_start": 102, "unit": 0, "verb": "PLANT"}]}

### m043 seat 1 (open_field, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 87, "turn_start": 87, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 88, "turn_start": 88, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 93, "turn_start": 93, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 94, "turn_start": 94, "unit": 0, "verb": "PLANT"}]}

### m044 seat 0 (single_door_tent, idle, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 134, "turn_start": 134, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PLANT"}]}

### m044 seat 1 (single_door_tent, idle, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 108, "turn_start": 108, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m046 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 2], [1, 2]], "k": 20, "turn_end": 101, "turn_start": 60, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 133-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 133}}

### m048 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 36, "turn_start": 36, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 7, "turn_start": 7, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 8, "turn_start": 8, "unit": 0, "verb": "PLANT"}]}

### m050 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 2], [2, 2]], "k": 88, "turn_end": 195, "turn_start": 19, "unit": 2}]}
- **P4**: {"detail": {"live_end": 195, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 18-195 while work remains through turn 195 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 195, "window_start": 18}}

### m050 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}

### m051 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m051 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m053 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 53, "turn_start": 53, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 58, "turn_start": 58, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 59, "turn_start": 59, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 91-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 91}}

### m053 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 63, "turn_start": 63, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 64, "turn_start": 64, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 69, "turn_start": 69, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 70, "turn_start": 70, "unit": 0, "verb": "PLANT"}]}

### m054 seat 0 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 77, "turn_start": 77, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 78, "turn_start": 78, "unit": 0, "verb": "PLANT"}]}

### m054 seat 1 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m056 seat 1 (forest_dense, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 0], [5, 0]], "k": 8, "turn_end": 96, "turn_start": 79, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 0)<->(5, 0) over turns 79-96 (18 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 0}

### m057 seat 0 (water_diagonal, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 109, "turn_start": 109, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 110, "turn_start": 110, "unit": 0, "verb": "PLANT"}]}

### m057 seat 1 (water_diagonal, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 66, "turn_start": 66, "unit": 0, "verb": "PLANT"}]}

### m059 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 3], [2, 4]], "k": 15, "turn_end": 94, "turn_start": 64, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 101-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 101}}

### m059 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 4], [9, 3]], "k": 94, "turn_end": 200, "turn_start": 12, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 11}}

### m060 seat 0 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[1, 0], [0, 0]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}, {"cells": [[5, 5], [6, 5]], "k": 75, "turn_end": 200, "turn_start": 50, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 43-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 43}}

### m060 seat 1 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 17, "detector": "D-6", "episodes": [{"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 38, "turn_start": 37, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 52, "turn_start": 51, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 55, "turn_start": 54, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 67, "turn_start": 66, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 80, "turn_start": 79, "unit": null}]
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 45-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 45}}

### m062 seat 0 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 17, "turn_start": 17, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 18, "turn_start": 18, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 23, "turn_start": 23, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 24, "turn_start": 24, "unit": 0, "verb": "PLANT"}]}

### m062 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}

### m066 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 3, "detector": "D-1", "episodes": [{"cells": [[9, 2], [10, 2]], "k": 22, "turn_end": 58, "turn_start": 13, "unit": 0}, {"cells": [[11, 2], [10, 2]], "k": 67, "turn_end": 200, "turn_start": 66, "unit": 0}, {"cells": [[10, 2], [9, 2]], "k": 3, "turn_end": 66, "turn_start": 59, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}
- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [11, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 40, "turn_start": 39, "unit": null}, {"cell": [11, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 64, "turn_start": 63, "unit": null}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 66-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 66}}

### m067 seat 0 (multi_door, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 92, "turn_start": 92, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 93, "turn_start": 93, "unit": 0, "verb": "PLANT"}]}

### m067 seat 1 (multi_door, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 111, "turn_start": 111, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 112, "turn_start": 112, "unit": 0, "verb": "PLANT"}]}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 71-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 71}}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 2], [9, 2]], "k": 5, "turn_end": 18, "turn_start": 7, "unit": 2}]}

### m071 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 3, "detector": "D-1", "episodes": [{"cells": [[0, 3], [0, 2]], "k": 3, "turn_end": 86, "turn_start": 79, "unit": 2}, {"cells": [[1, 0], [2, 0]], "k": 3, "turn_end": 135, "turn_start": 128, "unit": 2}, {"cells": [[1, 0], [2, 0]], "k": 3, "turn_end": 179, "turn_start": 173, "unit": 2}]}

### m071 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[9, 2], [8, 2]], "k": 3, "turn_end": 57, "turn_start": 51, "unit": 2}, {"cells": [[9, 2], [8, 2]], "k": 3, "turn_end": 103, "turn_start": 97, "unit": 2}]}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 25, "turn_start": 25, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PLANT"}]}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}

### m073 seat 1 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 2], [8, 2]], "k": 18, "turn_end": 47, "turn_start": 10, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 6, "turn_start": 4, "unit": 2}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 131, "why": "candidate makes no own-inventory/own-cargo progress over turns 54-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 54}}

### m075 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 5], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 35, "turn_start": 35, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 34, "turn_start": 34, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PLANT"}]}

### m075 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PLANT"}]}

### m076 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 91, "turn_start": 91, "unit": 0, "verb": "PLANT"}]}

### m076 seat 1 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 88, "turn_start": 88, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 89, "turn_start": 89, "unit": 0, "verb": "PLANT"}]}

### m079 seat 0 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 81, "turn_end": 200, "turn_start": 38, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 33-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 33}}

### m079 seat 1 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 82, "turn_end": 197, "turn_start": 33, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 31-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 31}}

### m081 seat 0 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m081 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 66, "turn_start": 66, "unit": 0, "verb": "PLANT"}]}

### m082 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [0, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 0}, {"cell": [1, 5], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 2}]}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 4, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "harvest", "turn_end": 65, "turn_start": 52, "unit": 0}, {"kind": "carried_overage", "provenance": "harvest", "turn_end": 66, "turn_start": 53, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "harvest", "turn_end": 200, "turn_start": 52, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "harvest", "turn_end": 200, "turn_start": 53, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 58-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 58}}

### m084 seat 1 (single_door_tent, idle, seed 982451653)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 82-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 82}}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [2, 4]], "k": 3, "turn_end": 23, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m085 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 54, "turn_start": 54, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 55, "turn_start": 55, "unit": 0, "verb": "PLANT"}]}

### m087 seat 0 (multi_door, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 58-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 58}}

### m087 seat 1 (multi_door, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m089 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PLANT"}]}

### m089 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 4], [2, 5]], "k": 27, "turn_end": 100, "turn_start": 46, "unit": 2}]}
- **P4**: {"detail": {"live_end": 103, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 41-103 while work remains through turn 103 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 103, "window_start": 41}}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 106-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 106}}

### m090 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}

### m091 seat 0 (forest_sparse, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 67, "turn_start": 67, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 68, "turn_start": 68, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 91-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 91}}

### m091 seat 1 (forest_sparse, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 61, "turn_start": 61, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 62, "turn_start": 62, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 94-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 94}}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 1], [0, 0]], "k": 17, "turn_end": 36, "turn_start": 2, "unit": 0}]}

### m093 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m093 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 15, "turn_start": 15, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 16, "turn_start": 16, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 22, "turn_start": 22, "unit": 0, "verb": "PLANT"}]}

### m095 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 28, "turn_start": 28, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 23, "turn_start": 23, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 24, "turn_start": 24, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m096 seat 0 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 105, "turn_start": 105, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PLANT"}]}

### m096 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 117, "turn_start": 117, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 118, "turn_start": 118, "unit": 0, "verb": "PLANT"}]}

### m097 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 3], [0, 3]], "k": 4, "turn_end": 159, "turn_start": 151, "unit": 2}]}

### m097 seat 1 (water_diagonal, idle, seed 15485863)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 65-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 65}}

### m098 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 5], [3, 6]], "k": 9, "turn_end": 36, "turn_start": 18, "unit": 2}]}

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 2], [10, 2]], "k": 96, "turn_end": 200, "turn_start": 8, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 8-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 8}}

### m100 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 13-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 13}}

### m100 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}

### m101 seat 0 (water_diagonal, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 74, "turn_start": 74, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 75, "turn_start": 75, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 115-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 115}}

### m101 seat 1 (water_diagonal, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 125, "turn_start": 125, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PLANT"}]}

### m104 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [10, 3]], "k": 85, "turn_end": 200, "turn_start": 29, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 26}}

### m106 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 133, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 58-133 while work remains through turn 133 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 133, "window_start": 58}}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

### m110 seat 0 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 73-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 73}}

### m110 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [5, 2]], "k": 93, "turn_end": 200, "turn_start": 14, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 9-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 9}}

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

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}

---

**VERDICT: BLOCK**
