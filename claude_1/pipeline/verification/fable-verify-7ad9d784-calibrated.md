# fuzz panel report - FABLE VERIFY#2: 7ad9d784 calibrated raw

- candidate: `/tmp/claude-1000/-home-tarstars-prj-troll-farm/3b336b91-cd2f-4655-9aaf-31fd6d3d156f/scratchpad/cand-7ad9d784.rs` (sha256 None)
- parent: `/home/tarstars/prj/troll_farm-claude_1/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 12.2 s

## Verdict: BLOCK

## Coverage

| metric | value |
|---|---|
| games | 240 |
| banana_activated_games | 152 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 5 |
| blocking_games | 146 |
| flagged_games | 21 |

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

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}

### m001 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 91, "turn_start": 91, "unit": 0, "verb": "PLANT"}]}

### m003 seat 0 (single_door_tent, harvester, seed 49979687)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 19-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 19}}

### m003 seat 1 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 3, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 47, "turn_start": 45, "unit": 2}, {"kind": "no_progress", "turn_end": 50, "turn_start": 48, "unit": 2}, {"kind": "no_progress", "turn_end": 66, "turn_start": 64, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 63-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 63}}

### m004 seat 0 (orchard_eligible, idle, seed 67867967)

- **P3**: {"detail": {"candidate": "CHOP 0;WAIT", "first_divergence_turn": 26, "parent": "CHOP 0;MOVE 2 9 2"}}

### m004 seat 1 (orchard_eligible, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 27, "turn_start": 25, "unit": 0}, {"kind": "no_progress", "turn_end": 15, "turn_start": 13, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 24-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 24}}

### m009 seat 1 (water_diagonal, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 34, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 28-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 28}}

### m010 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}

### m010 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 84, "turn_start": 84, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 85, "turn_start": 85, "unit": 0, "verb": "PLANT"}]}

### m011 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 141, "turn_start": 141, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 142, "turn_start": 142, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 147, "turn_start": 147, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 148, "turn_start": 148, "unit": 0, "verb": "PLANT"}]}

### m011 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 124, "turn_start": 124, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 125, "turn_start": 125, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 130, "turn_start": 130, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 131, "turn_start": 131, "unit": 0, "verb": "PLANT"}]}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 27, "turn_start": 14, "unit": 2}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 17-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 17}}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 34, "turn_start": 21, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 21, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 21}}

### m013 seat 1 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 6, "turn_start": 4, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m014 seat 1 (orchard_eligible, idle, seed 32452843)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 5}}

### m015 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 28, "turn_start": 15, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 15, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 15-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 15}}

### m015 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 15, "turn_start": 2, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 2, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 2-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 2}}

### m016 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 99, "turn_start": 99, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 100, "turn_start": 100, "unit": 0, "verb": "PLANT"}]}

### m016 seat 1 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 53, "turn_start": 53, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 54, "turn_start": 54, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 59, "turn_start": 59, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 60, "turn_start": 60, "unit": 0, "verb": "PLANT"}]}

### m017 seat 0 (open_field, idle, seed 86028121)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 132-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 132}}

### m018 seat 0 (choke_corridor, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 15, "turn_start": 2, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 2, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 17-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 17}}

### m018 seat 1 (choke_corridor, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 20, "turn_start": 7, "unit": 2}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 7-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 7}}

### m020 seat 0 (forest_sparse, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PLANT"}]}

### m020 seat 1 (forest_sparse, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 108, "turn_start": 108, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 109, "turn_start": 109, "unit": 0, "verb": "PLANT"}]}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 23, "turn_start": 21, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 20}}

### m022 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 24, "turn_start": 11, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 11, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m022 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 15, "turn_start": 2, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 2, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 2-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 2}}

### m023 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 33, "turn_start": 31, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 28-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 28}}

### m023 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 28, "turn_start": 26, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 24-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 24}}

### m024 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 200, "unit": 0}]}

### m028 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 34, "turn_start": 21, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 21, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 21}}

### m029 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 137, "turn_start": 137, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 142, "turn_start": 142, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 143, "turn_start": 143, "unit": 0, "verb": "PLANT"}]}

### m029 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 134, "turn_start": 134, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PLANT"}]}

### m032 seat 0 (forest_sparse, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 29, "turn_start": 16, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 16, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 16}}

### m033 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m033 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m034 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 146, "turn_start": 146, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 147, "turn_start": 147, "unit": 0, "verb": "PLANT"}]}

### m034 seat 1 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m035 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 29, "turn_start": 27, "unit": 2}]}
- **P3**: {"detail": {"candidate": "WAIT;CHOP 2", "first_divergence_turn": 10, "parent": "PLANT 0 BANANA;CHOP 2"}}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 16}}

### m036 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 4, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 28, "turn_start": 26, "unit": 0}, {"kind": "no_progress", "turn_end": 32, "turn_start": 30, "unit": 0}, {"kind": "no_progress", "turn_end": 38, "turn_start": 36, "unit": 0}, {"kind": "no_progress", "turn_end": 47, "turn_start": 45, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 44-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 44}}

### m037 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 117, "turn_start": 117, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 118, "turn_start": 118, "unit": 0, "verb": "PLANT"}]}

### m037 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m038 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 51, "turn_start": 38, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 38, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 38-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 38}}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 50, "turn_start": 37, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 37, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 37-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 37}}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 46-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 46}}

### m041 seat 0 (choke_corridor, idle, seed 86028121)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 8, "turn_start": 6, "unit": 2}]}

### m041 seat 1 (choke_corridor, idle, seed 86028121)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 10, "turn_start": 8, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m042 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 41, "turn_start": 28, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 28, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 32-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 32}}

### m043 seat 0 (open_field, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 56, "turn_start": 56, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 57, "turn_start": 57, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 64, "turn_start": 64, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PLANT"}]}

### m043 seat 1 (open_field, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 89, "turn_start": 89, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 95, "turn_start": 95, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 96, "turn_start": 96, "unit": 0, "verb": "PLANT"}]}

### m044 seat 0 (single_door_tent, idle, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 134, "turn_start": 134, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PLANT"}]}

### m044 seat 1 (single_door_tent, idle, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 108, "turn_start": 108, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m046 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m046 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 6, "turn_start": 4, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m048 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 39, "turn_start": 26, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 26, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 25, "turn_start": 25, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 26}}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 7, "turn_start": 7, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 8, "turn_start": 8, "unit": 0, "verb": "PLANT"}]}

### m050 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 4, "turn_start": 2, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m051 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 115, "turn_start": 115, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 116, "turn_start": 116, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m051 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m053 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 53, "turn_start": 53, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 58, "turn_start": 58, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 59, "turn_start": 59, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 91-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 91}}

### m053 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 63, "turn_start": 63, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 64, "turn_start": 64, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 69, "turn_start": 69, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 70, "turn_start": 70, "unit": 0, "verb": "PLANT"}]}

### m054 seat 0 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 77, "turn_start": 77, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 78, "turn_start": 78, "unit": 0, "verb": "PLANT"}]}
- **P3**: {"detail": {"candidate": "MOVE 0 0 2", "first_divergence_turn": 75, "parent": "MOVE 0 1 1"}}

### m054 seat 1 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m056 seat 1 (forest_dense, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 21, "turn_start": 19, "unit": 0}, {"kind": "no_progress", "turn_end": 126, "turn_start": 124, "unit": 2}]}

### m057 seat 0 (water_diagonal, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 109, "turn_start": 109, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 110, "turn_start": 110, "unit": 0, "verb": "PLANT"}]}

### m057 seat 1 (water_diagonal, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 66, "turn_start": 66, "unit": 0, "verb": "PLANT"}]}

### m058 seat 1 (open_field, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}, {"kind": "no_progress", "turn_end": 17, "turn_start": 15, "unit": 2}]}

### m059 seat 0 (choke_corridor, harvester, seed 86028121)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m059 seat 1 (choke_corridor, harvester, seed 86028121)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m060 seat 0 (forest_sparse, harvester, seed 982451653)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 37-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 37}}

### m061 seat 0 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 5, "turn_start": 3, "unit": 2}]}

### m062 seat 0 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 37, "turn_start": 24, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 17, "turn_start": 17, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 18, "turn_start": 18, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 23, "turn_start": 23, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 44, "turn_start": 44, "unit": 0, "verb": "PLANT"}]}

### m062 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 58, "turn_start": 45, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 45, "unit": 0}]}
- **P1**: {"count": 3, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 39, "turn_start": 39, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 44, "turn_start": 44, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 45-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 45}}

### m063 seat 0 (open_field, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 59, "turn_start": 57, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 55-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 55}}

### m063 seat 1 (open_field, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 53, "turn_start": 51, "unit": 2}, {"kind": "no_progress", "turn_end": 56, "turn_start": 54, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 52-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 52}}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 14, "turn_start": 12, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 12-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 12}}

### m064 seat 1 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 18, "turn_start": 16, "unit": 0}, {"kind": "no_progress", "turn_end": 23, "turn_start": 21, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 20}}

### m065 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 39, "turn_start": 26, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 26, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 30-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 30}}

### m066 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 6, "turn_start": 4, "unit": 2}]}

### m066 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 10, "turn_start": 8, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m067 seat 0 (multi_door, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 92, "turn_start": 92, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 93, "turn_start": 93, "unit": 0, "verb": "PLANT"}]}

### m067 seat 1 (multi_door, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 111, "turn_start": 111, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 112, "turn_start": 112, "unit": 0, "verb": "PLANT"}]}

### m068 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 73, "turn_start": 60, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 60, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 81-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 81}}

### m068 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 93, "turn_start": 80, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 80, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 80-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 80}}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 4, "turn_start": 2, "unit": 2}]}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 6, "turn_start": 4, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m071 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 115, "turn_start": 113, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 200, "unit": 2}]}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 25, "turn_start": 25, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PLANT"}]}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}

### m073 seat 0 (choke_corridor, harvester, seed 15485863)

- **P4**: {"detail": {"live_end": 66, "terminal_from": 73, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-66 while work remains through turn 66 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 66, "window_start": 5}}

### m073 seat 1 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m074 seat 0 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 46, "turn_start": 44, "unit": 0}, {"kind": "no_progress", "turn_end": 50, "turn_start": 48, "unit": 0}]}
- **P3**: {"detail": {"candidate": "WAIT;CHOP 2", "first_divergence_turn": 44, "parent": "MOVE 0 2 7;CHOP 2"}}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 47-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 47}}

### m075 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 48, "turn_start": 35, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 35, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 34, "turn_start": 34, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 35}}

### m075 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 56, "turn_start": 43, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 43, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 43-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 43}}

### m076 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 90, "turn_start": 90, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 91, "turn_start": 91, "unit": 0, "verb": "PLANT"}]}

### m076 seat 1 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 88, "turn_start": 88, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 89, "turn_start": 89, "unit": 0, "verb": "PLANT"}]}

### m079 seat 0 (forest_sparse, harvester, seed 15485863)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 34-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 34}}

### m079 seat 1 (forest_sparse, harvester, seed 15485863)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 30-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 30}}

### m081 seat 0 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m081 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 65, "turn_start": 65, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 66, "turn_start": 66, "unit": 0, "verb": "PLANT"}]}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}
- **P3**: {"detail": {"candidate": "WAIT", "first_divergence_turn": 19, "parent": "MOVE 0 2 4"}}

### m085 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 56, "turn_start": 56, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 57, "turn_start": 57, "unit": 0, "verb": "PLANT"}]}

### m087 seat 0 (multi_door, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 58-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 58}}

### m087 seat 1 (multi_door, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m088 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 27, "turn_start": 14, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 14, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 14-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 14}}

### m088 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 23, "turn_start": 21, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 34, "turn_start": 21, "unit": 2}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 21, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 21}}

### m089 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 135, "turn_start": 135, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PLANT"}]}

### m089 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 113, "turn_start": 113, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 114, "turn_start": 114, "unit": 0, "verb": "PLANT"}]}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 5, "turn_start": 3, "unit": 2}]}
- **P4**: {"detail": {"live_end": 191, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-191 while work remains through turn 191 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 191, "window_start": 11}}

### m090 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 8, "turn_start": 6, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m091 seat 0 (forest_sparse, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 67, "turn_start": 67, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 68, "turn_start": 68, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 91-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 91}}

### m091 seat 1 (forest_sparse, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 61, "turn_start": 61, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 62, "turn_start": 62, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 94-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 94}}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 72, "turn_start": 59, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 59, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 68-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 68}}

### m093 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m093 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m094 seat 1 (single_door_tent, idle, seed 67867967)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 39-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 39}}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 35, "turn_start": 22, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 22, "unit": 0}]}
- **P1**: {"count": 3, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 15, "turn_start": 15, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 16, "turn_start": 16, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}]}
- **P3**: {"detail": {"candidate": "WAIT", "first_divergence_turn": 22, "parent": "PLANT 0 BANANA"}}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 22-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 22}}

### m095 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 37, "turn_start": 24, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 24, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 23, "turn_start": 23, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 24-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 24}}

### m096 seat 0 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 105, "turn_start": 105, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PLANT"}]}

### m096 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 117, "turn_start": 117, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 118, "turn_start": 118, "unit": 0, "verb": "PLANT"}]}

### m097 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 42, "turn_start": 40, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 38-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 38}}

### m098 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 32, "turn_start": 19, "unit": 2}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 19, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 33-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 33}}

### m098 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 33, "turn_start": 20, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 20, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 35-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 35}}

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 8, "turn_start": 6, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m100 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 99, "terminal_from": 110, "why": "candidate makes no own-inventory/own-cargo progress over turns 6-99 while work remains through turn 99 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 99, "window_start": 6}}

### m101 seat 0 (water_diagonal, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 77, "turn_start": 77, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 78, "turn_start": 78, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 100-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 100}}

### m101 seat 1 (water_diagonal, idle, seed 86028121)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 124, "turn_start": 124, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 125, "turn_start": 125, "unit": 0, "verb": "PLANT"}]}

### m104 seat 0 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 96, "turn_start": 94, "unit": 2}]}
- **P3**: {"detail": {"candidate": "HARVEST 0;WAIT", "first_divergence_turn": 94, "parent": "HARVEST 0;MOVE 2 2 3"}}

### m104 seat 1 (orchard_eligible, idle, seed 32452843)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 26}}

### m106 seat 0 (choke_corridor, harvester, seed 67867967)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 12, "turn_start": 10, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 7-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 7}}

### m110 seat 1 (choke_corridor, harvester, seed 32452843)

- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

### m111 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m111 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}]}

### m112 seat 0 (single_door_tent, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 55, "turn_start": 42, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 42, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 42-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 42}}

### m112 seat 1 (single_door_tent, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 62, "turn_start": 49, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 49, "unit": 0}]}
- **P1**: {"count": 3, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 48, "turn_start": 48, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 49-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 49}}

### m113 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}

### m113 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 35, "turn_start": 35, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 36, "turn_start": 36, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 41, "turn_start": 41, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PLANT"}]}

### m115 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 63, "turn_start": 50, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 50, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 50-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 50}}

### m115 seat 1 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 78, "turn_start": 65, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 65, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 64, "turn_start": 64, "unit": 0, "verb": "PICK"}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 65-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 65}}

### m116 seat 0 (water_diagonal, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 106, "turn_start": 106, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 107, "turn_start": 107, "unit": 0, "verb": "PLANT"}]}

### m116 seat 1 (water_diagonal, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 126, "turn_start": 126, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PLANT"}]}

### m117 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 181, "turn_start": 181, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 182, "turn_start": 182, "unit": 0, "verb": "PLANT"}]}

### m117 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 149, "turn_start": 149, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 150, "turn_start": 150, "unit": 0, "verb": "PLANT"}]}

### m118 seat 0 (choke_corridor, chopper_aggressor, seed 67867967)

- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 22, "turn_start": 9, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 9, "unit": 0}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 11}}

### m118 seat 1 (choke_corridor, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 4, "turn_start": 2, "unit": 2}]}
- **P4**: {"detail": {"live_end": 199, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-199 while work remains through turn 199 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 199, "window_start": 1}}

## Report-tier flags (non-blocking)

- m009 seat 1 [r5-horizon]: full wood carrier since turn 28 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m013 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m021 seat 1 [r5-horizon]: full wood carrier since turn 12 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m023 seat 1 [r5-horizon]: full wood carrier since turn 24 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m035 seat 0 [r5-horizon]: full wood carrier since turn 16 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m036 seat 1 [r5-horizon]: full wood carrier since turn 20 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m041 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m046 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m050 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m064 seat 0 [r5-horizon]: full wood carrier since turn 9 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m064 seat 1 [r5-horizon]: full wood carrier since turn 12 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m066 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m070 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m073 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m074 seat 0 [r5-horizon]: full wood carrier since turn 30 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m088 seat 1 [r5-horizon]: full wood carrier since turn 18 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m090 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m097 seat 1 [r5-horizon]: full wood carrier since turn 35 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m099 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m106 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m118 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated

---

**VERDICT: BLOCK**
