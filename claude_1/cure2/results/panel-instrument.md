# fuzz panel report [CANDIDATE (candidate vs parent)] - 20260825-dance-cure-candidate-2-swap G-1 panel (instrument arm) — EVIDENCE for the C-5 stop, not a gate pass

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `../../claude_1/cure2/arm-instrument.rs` (sha256 5c678e6a8e320c93d2c948e6bae1278c80692aaa4e8d751464cd204ee7dee442)
- parent: `../../cgauto/submissions/candidate-door1-pure-deletion.rs` (sha256 547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 18.1 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 240 |
| clean_games | 200 |
| banana_activated_games | 24 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 0 |
| blocking_games | 40 |
| flagged_games | 0 |
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

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[10, 2], [11, 2]], "k": 74, "turn_end": 200, "turn_start": 52, "unit": 0}, {"cells": [[8, 2], [9, 2]], "k": 3, "turn_end": 31, "turn_start": 24, "unit": 2}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(10,2)/TREE(10,2)/r=P/b=0 u2=BANK(1,1)/BANK(1,1)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 2;MOVE 2 12 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2;MOVE 2 12 3"}}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 42-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 42}}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 1], "kind": "outside_ring", "turn_end": 15, "turn_start": 15, "unit": 2}]}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[12, 2], [13, 2]], "k": 10, "turn_end": 32, "turn_start": 12, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [13, 1], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 47, "turn_start": 47, "unit": 2}]}

### m014 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(10,0)/TREE(10,0)/r=P/b=0 u2=BANK(1,2)/BANK(1,2)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 3;MOVE 2 6 1", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3;MOVE 2 6 1"}}

### m014 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 1], [9, 1]], "k": 96, "turn_end": 200, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 5}}

### m016 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 13, "turn_start": 13, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 14, "turn_start": 14, "unit": 0, "verb": "PLANT"}]}

### m021 seat 0 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [7, 2]], "k": 86, "turn_end": 200, "turn_start": 27, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 22-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 22}}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 17, "turn_start": 15, "unit": 2}]}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 0}]}

### m025 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(10,3)/TREE(10,3)/r=P/b=0 u2=TREE(11,6)/TREE(10,3)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 2;MOVE 2 4 5", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2;MOVE 2 4 5"}}

### m028 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 4], [8, 4]], "k": 3, "turn_end": 32, "turn_start": 26, "unit": 0}]}

### m035 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(12,1)/TREE(9,3)/r=P/b=0 u2=TREE(9,3)/TREE(9,3)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 3;MOVE 2 6 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3;MOVE 2 6 3"}}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 51, "turn_start": 51, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PLANT"}]}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 26}}

### m045 seat 0 (orchard_eligible, chopper_aggressor, seed 49979687)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(9,1)/TREE(9,1)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 7", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 7"}}

### m046 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 2], [6, 2]], "k": 93, "turn_end": 200, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 11}}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m054 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(11,1)/TREE(11,1)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 2", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2"}}

### m061 seat 1 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 26, "turn_start": 24, "unit": 0}, {"kind": "no_progress", "turn_end": 66, "turn_start": 64, "unit": 0}]}

### m062 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 39, "turn_start": 39, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 40, "turn_start": 40, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 45, "turn_start": 45, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 46, "turn_start": 46, "unit": 0, "verb": "PLANT"}]}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}

### m065 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=NONE/TREE(10,1)/r=N/b=0 u2=TREE(10,1)/TREE(10,1)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;WAIT;MOVE 2 8 1", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;WAIT;MOVE 2 8 1"}}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 23, "turn_start": 21, "unit": 2}]}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m073 seat 0 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 2], [2, 2]], "k": 32, "turn_end": 69, "turn_start": 5, "unit": 0}]}
- **P4**: {"detail": {"live_end": 68, "terminal_from": 75, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-68 while work remains through turn 68 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 68, "window_start": 5}}

### m074 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(10,0)/TREE(10,0)/r=P/b=0 u2=NONE/TREE(10,0)/r=N/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 7;WAIT", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 7;WAIT"}}

### m079 seat 0 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 81, "turn_end": 200, "turn_start": 38, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 33-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 33}}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 21, "turn_start": 19, "unit": 2}]}

### m084 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 5], [6, 5]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 26}}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [2, 4]], "k": 4, "turn_end": 25, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=CELL(2,4)/CELL(2,4)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 5", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 5"}}

### m090 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 0}]}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 5, "detector": "D-6", "episodes": [{"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 80, "turn_start": 80, "unit": 0}, {"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 85, "turn_start": 85, "unit": 0}, {"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 90, "turn_start": 90, "unit": 0}, {"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 95, "turn_start": 95, "unit": 0}, {"cell": [3, 1], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 103, "turn_start": 103, "unit": 0}]}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 22, "turn_start": 22, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(9,2)/TREE(9,2)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 1 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3"}}

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 2], [10, 2]], "k": 96, "turn_end": 200, "turn_start": 8, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 8-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 8}}

### m104 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=TREE(11,4)/TREE(11,4)/r=P/b=0 u2=BANK(1,2)/BANK(1,2)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;MOVE 0 0 4;MOVE 2 6 6", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 0 4;MOVE 2 6 6"}}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

### m114 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v5 t=1 u0=NONE/TREE(12,3)/r=N/b=0 u2=TREE(12,3)/TREE(12,3)/r=P/b=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0;WAIT;MOVE 2 1 2", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;WAIT;MOVE 2 1 2"}}

### m115 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 50, "turn_start": 50, "unit": 0, "verb": "PLANT"}]}

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
