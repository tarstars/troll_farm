# fuzz panel report [CANDIDATE (candidate vs parent)] - yaichi-style two-role factory integration validation

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `c786b6ed46a57084983ad3206a6ff0c2aa7e1d0818500caaed85a4d82e724cb2`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `bot.rs` (sha256 dd7af27fc114f7b54ab3c9eeec14cc2aff32c5de11179a21451e7f53293b557a)
- parent: `bot-v2.rs` (sha256 87e2bf894ba871df6241224c517f9473aa89d63e24259580431e4149b53fcaa0)
- seeds: [982451653, 15485863, 32452843, 49979687]
- maps: 40 (x2 seats = 80 candidate games + 80 parent games), 300 turns each
- wall time: 28.0 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 80 |
| clean_games | 12 |
| banana_activated_games | 58 |
| orchard_eligible_games | 4 |
| orchard_inertness_checks_passed | 1 |
| blocking_games | 68 |
| flagged_games | 3 |
| instrument_invalid_games | 0 |
| parent_instrument_invalid_games | 0 |
| gate_unready_games | 0 |
| unsupported_command_games | 0 |
| malformed_command_games | 0 |
| games_with_a_successful_train | 5 |
| successful_train_events | 5 |

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

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 136, "turn_start": 136, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 137, "turn_start": 137, "unit": 0, "verb": "PLANT"}]}

### m003 seat 0 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 3, "detector": "D-1", "episodes": [{"cells": [[0, 2], [0, 3]], "k": 5, "turn_end": 228, "turn_start": 217, "unit": 0}, {"cells": [[1, 3], [0, 3]], "k": 23, "turn_end": 300, "turn_start": 253, "unit": 0}, {"cells": [[1, 3], [0, 3]], "k": 42, "turn_end": 118, "turn_start": 34, "unit": 2}]}
- **P1**: {"count": 9, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 147, "turn_start": 145, "unit": 2}, {"kind": "no_progress", "turn_end": 150, "turn_start": 148, "unit": 2}, {"kind": "no_progress", "turn_end": 179, "turn_start": 177, "unit": 2}, {"kind": "no_progress", "turn_end": 182, "turn_start": 180, "unit": 2}, {"kind": "no_progress", "turn_end": 185, "turn_start": 183, "unit": 2}]}
- **P1**: {"count": 35, "detector": "D-5", "episodes": [{"cell": [1, 3], "kind": "outside_ring", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [3, 5], "kind": "outside_ring", "turn_end": 18, "turn_start": 18, "unit": 0}, {"cell": [3, 5], "cumulative": 3, "kind": "cumulative_over_ring", "ring_size": 2, "turn_end": 18, "turn_start": 18, "unit": 0}, {"cell": [1, 3], "kind": "outside_ring", "turn_end": 123, "turn_start": 123, "unit": 0}, {"cell": [1, 3], "cumulative": 3, "kind": "cumulative_over_ring", "ring_size": 2, "turn_end": 123, "turn_start": 123, "unit": 0}]}
- **P1**: {"count": 44, "detector": "D-6", "episodes": [{"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 32, "turn_start": 31, "unit": null}, {"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 35, "turn_start": 34, "unit": null}, {"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 47, "turn_start": 46, "unit": null}, {"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 48, "turn_start": 47, "unit": null}, {"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 54, "turn_start": 53, "unit": null}]
- **P4**: {"detail": {"live_end": 119, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 33-119 while work remains through turn 119 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 119, "window_start": 33}}

### m003 seat 1 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 55, "detector": "D-5", "episodes": [{"cell": [7, 7], "kind": "outside_ring", "turn_end": 7, "turn_start": 7, "unit": 0}, {"cell": [5, 5], "kind": "outside_ring", "turn_end": 19, "turn_start": 19, "unit": 0}, {"cell": [4, 6], "kind": "outside_ring", "turn_end": 25, "turn_start": 25, "unit": 0}, {"cell": [7, 7], "kind": "outside_ring", "turn_end": 37, "turn_start": 37, "unit": 0}, {"cell": [7, 7], "kind": "outside_ring", "turn_end": 51, "turn_start": 51, "unit": 0}]}
- **P1**: {"count": 6, "detector": "D-6", "episodes": [{"cell": [4, 6], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 64, "turn_start": 63, "unit": null}, {"cell": [4, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 155, "turn_start": 154, "unit": null}, {"cell": [4, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 191, "turn_start": 190, "unit": null}, {"cell": [4, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 227, "turn_start": 226, "unit": null}, {"cell": [4, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 263, "turn_start": 262, "unit":
- **P1**: {"count": 25, "detector": "D-8", "episodes": [{"cell": [8, 6], "completion_turn": 56, "eta_opp_at_chop_start": 9, "exact_chop_turns": 5, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 66, "reason": "discretionary_owned", "turn_end": 52, "turn_start": 52, "unit": 2}, {"cell": [8, 6], "completion_turn": 56, "eta_opp_at_chop_start": 9, "exact_chop_turns": 5, "flip_turn": null, "health_decreased": false, "kind": "diag_mother_chop", "opponent_harvest_turn": 66, "reason": "discretionary_owned", "turn_end": 53, "turn_start": 53, "unit": 2}, {"cell": 

### m004 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "MINE 0", "first_divergence_turn": 5, "parent": "MOVE 0 1 5"}}

### m005 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 129, "why": "candidate makes no own-inventory/own-cargo progress over turns 31-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 31}}

### m005 seat 1 (multi_door, chopper_aggressor, seed 15485863)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 131, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 21}}

### m006 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 22, "detector": "D-1", "episodes": [{"cells": [[3, 6], [4, 6]], "k": 7, "turn_end": 138, "turn_start": 124, "unit": 0}, {"cells": [[3, 6], [4, 6]], "k": 7, "turn_end": 158, "turn_start": 144, "unit": 0}, {"cells": [[3, 6], [4, 6]], "k": 7, "turn_end": 174, "turn_start": 160, "unit": 0}, {"cells": [[3, 6], [4, 6]], "k": 7, "turn_end": 190, "turn_start": 176, "unit": 0}, {"cells": [[3, 6], [4, 6]], "k": 7, "turn_end": 206, "turn_start": 192, "unit": 0}]}
- **P1**: {"count": 7, "detector": "D-5", "episodes": [{"cell": [3, 6], "kind": "outside_ring", "turn_end": 42, "turn_start": 42, "unit": 0}, {"cell": [3, 6], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 42, "turn_start": 42, "unit": 0}, {"cell": [4, 6], "kind": "outside_ring", "turn_end": 49, "turn_start": 49, "unit": 0}, {"cell": [4, 6], "cumulative": 5, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 49, "turn_start": 49, "unit": 0}, {"cell": [5, 6], "kind": "outside_ring", "turn_end": 60, "turn_start": 60, "unit": 0}]}
- **P1**: {"count": 6, "detector": "D-6", "episodes": [{"cell": [2, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 62, "turn_start": 61, "unit": null}, {"cell": [4, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 87, "turn_start": 86, "unit": null}, {"cell": [4, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 88, "turn_start": 87, "unit": null}, {"cell": [5, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 110, "turn_start": 109, "unit": null}, {"cell": [5, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 111, "turn_start": 110, "unit": nul
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "harvest", "turn_end": 134, "turn_start": 121, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-8", "episodes": [{"cell": [2, 6], "completion_turn": 32, "eta_opp_at_chop_start": 8, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 54, "reason": "discretionary_owned", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P4**: {"detail": {"live_end": 297, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 121-297 while work remains through turn 297 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 297, "window_start": 121}}

### m006 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 6], [8, 6]], "k": 86, "turn_end": 300, "turn_start": 128, "unit": 0}]}
- **P1**: {"count": 10, "detector": "D-5", "episodes": [{"cell": [9, 6], "kind": "outside_ring", "turn_end": 6, "turn_start": 6, "unit": 0}, {"cell": [9, 6], "cumulative": 2, "kind": "cumulative_over_ring", "ring_size": 1, "turn_end": 6, "turn_start": 6, "unit": 0}, {"cell": [9, 6], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}, {"cell": [9, 6], "cumulative": 2, "kind": "cumulative_over_ring", "ring_size": 1, "turn_end": 30, "turn_start": 30, "unit": 0}, {"cell": [8, 6], "kind": "outside_ring", "turn_end": 37, "turn_start": 37, "unit": 0}]}
- **P1**: {"count": 11, "detector": "D-6", "episodes": [{"cell": [9, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 56, "turn_start": 55, "unit": null}, {"cell": [7, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 87, "turn_start": 86, "unit": null}, {"cell": [7, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 88, "turn_start": 87, "unit": null}, {"cell": [7, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 112, "turn_start": 111, "unit": null}, {"cell": [7, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 136, "turn_start": 135, "unit": nu
- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "harvest", "turn_end": 136, "turn_start": 123, "unit": 2}, {"kind": "unbanked_at_end", "provenance": "harvest", "turn_end": 300, "turn_start": 123, "unit": 2}]}
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 126-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 126}}

### m007 seat 0 (forest_dense, idle, seed 49979687)

- **P1**: {"count": 51, "detector": "D-5", "episodes": [{"cell": [0, 3], "kind": "outside_ring", "turn_end": 91, "turn_start": 91, "unit": 0}, {"cell": [5, 4], "kind": "outside_ring", "turn_end": 103, "turn_start": 103, "unit": 0}, {"cell": [6, 3], "kind": "outside_ring", "turn_end": 107, "turn_start": 107, "unit": 0}, {"cell": [6, 5], "kind": "outside_ring", "turn_end": 111, "turn_start": 111, "unit": 0}, {"cell": [0, 4], "kind": "outside_ring", "turn_end": 138, "turn_start": 138, "unit": 0}]}
- **P1**: {"count": 16, "detector": "D-8", "episodes": [{"cell": [1, 2], "completion_turn": 140, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 2, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10139, "reason": "discretionary_owned", "turn_end": 139, "turn_start": 139, "unit": 6}, {"cell": [1, 2], "completion_turn": 140, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 2, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10139, "reason": "discretionary_owned", "turn_end": 140, "turn_start": 140, "u

### m007 seat 1 (forest_dense, idle, seed 49979687)

- **P1**: {"count": 45, "detector": "D-5", "episodes": [{"cell": [7, 4], "kind": "outside_ring", "turn_end": 76, "turn_start": 76, "unit": 0}, {"cell": [8, 4], "kind": "outside_ring", "turn_end": 81, "turn_start": 81, "unit": 0}, {"cell": [6, 2], "kind": "outside_ring", "turn_end": 87, "turn_start": 87, "unit": 0}, {"cell": [8, 0], "kind": "outside_ring", "turn_end": 117, "turn_start": 117, "unit": 0}, {"cell": [8, 0], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 117, "turn_start": 117, "unit": 0}]}
- **P1**: {"count": 30, "detector": "D-8", "episodes": [{"cell": [11, 0], "completion_turn": 82, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 2, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10081, "reason": "discretionary_owned", "turn_end": 81, "turn_start": 81, "unit": 6}, {"cell": [11, 0], "completion_turn": 82, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 2, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10081, "reason": "discretionary_owned", "turn_end": 82, "turn_start": 82, "unit"

### m008 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 134, "why": "candidate makes no own-inventory/own-cargo progress over turns 28-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 28}}

### m008 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 122, "turn_start": 122, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 134, "why": "candidate makes no own-inventory/own-cargo progress over turns 27-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 27}}

### m009 seat 0 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 47, "turn_start": 47, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 48, "turn_start": 48, "unit": 0, "verb": "PLANT"}]}

### m009 seat 1 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 129, "turn_start": 129, "unit": 0, "verb": "PLANT"}]}

### m010 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 55, "detector": "D-5", "episodes": [{"cell": [4, 2], "kind": "outside_ring", "turn_end": 13, "turn_start": 13, "unit": 0}, {"cell": [2, 1], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 36, "turn_start": 36, "unit": 0}, {"cell": [3, 2], "kind": "outside_ring", "turn_end": 42, "turn_start": 42, "unit": 0}, {"cell": [3, 2], "cumulative": 5, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 42, "turn_start": 42, "unit": 0}, {"cell": [4, 2], "kind": "outside_ring", "turn_end": 49, "turn_start": 49, "unit": 0}]}
- **P1**: {"count": 34, "detector": "D-6", "episodes": [{"cell": [4, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 81, "turn_start": 80, "unit": null}, {"cell": [4, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 91, "turn_start": 90, "unit": null}, {"cell": [5, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 103, "turn_start": 102, "unit": null}, {"cell": [4, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 105, "turn_start": 104, "unit": null}, {"cell": [5, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 115, "turn_start": 114, "unit": 
- **P1**: {"count": 36, "detector": "D-8", "episodes": [{"cell": [2, 2], "completion_turn": 32, "eta_opp_at_chop_start": 4, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 54, "reason": "discretionary_owned", "turn_end": 30, "turn_start": 30, "unit": 0}, {"cell": [2, 2], "completion_turn": 32, "eta_opp_at_chop_start": 4, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 54, "reason": "discretionary_owned", "turn_end": 36, "turn_start": 36, "unit": 2}, {"cell": [

### m010 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 73, "detector": "D-5", "episodes": [{"cell": [6, 2], "kind": "outside_ring", "turn_end": 20, "turn_start": 20, "unit": 0}, {"cell": [7, 2], "kind": "outside_ring", "turn_end": 29, "turn_start": 29, "unit": 0}, {"cell": [10, 2], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 36, "turn_start": 36, "unit": 0}, {"cell": [8, 2], "kind": "outside_ring", "turn_end": 42, "turn_start": 42, "unit": 0}, {"cell": [8, 2], "cumulative": 5, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 42, "turn_start": 42, "unit": 0}]}
- **P1**: {"count": 34, "detector": "D-6", "episodes": [{"cell": [9, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 35, "turn_start": 34, "unit": null}, {"cell": [9, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 53, "turn_start": 52, "unit": null}, {"cell": [7, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 63, "turn_start": 62, "unit": null}, {"cell": [7, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 64, "turn_start": 63, "unit": null}, {"cell": [7, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 75, "turn_start": 74, "unit": null}]

### m011 seat 0 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m011 seat 1 (open_field, idle, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [3, 1], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 30, "turn_start": 30, "unit": 0}]}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[12, 3], [11, 3]], "k": 7, "turn_end": 57, "turn_start": 43, "unit": 2}]}
- **P1**: {"count": 2, "detector": "D-5", "episodes": [{"cell": [13, 3], "kind": "outside_ring", "turn_end": 39, "turn_start": 39, "unit": 0}, {"cell": [12, 3], "kind": "outside_ring", "turn_end": 66, "turn_start": 66, "unit": 0}]}
- **P1**: {"count": 3, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 35, "turn_start": 35, "unit": 0}, {"cell": [13, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 39, "turn_start": 39, "unit": 0}, {"cell": [12, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 66, "turn_start": 66, "unit": 0}]}

### m014 seat 0 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 56, "detector": "D-5", "episodes": [{"cell": [5, 1], "kind": "outside_ring", "turn_end": 21, "turn_start": 21, "unit": 0}, {"cell": [6, 1], "kind": "outside_ring", "turn_end": 34, "turn_start": 34, "unit": 0}, {"cell": [5, 2], "kind": "outside_ring", "turn_end": 135, "turn_start": 135, "unit": 0}, {"cell": [5, 0], "kind": "outside_ring", "turn_end": 139, "turn_start": 139, "unit": 0}, {"cell": [5, 0], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 139, "turn_start": 139, "unit": 0}]}
- **P3**: {"detail": {"candidate": "MOVE 0 5 2;WAIT", "first_divergence_turn": 6, "parent": "WAIT;MOVE 2 3 2"}}
- **P4**: {"detail": {"live_end": 123, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 42-123 while work remains through turn 123 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 123, "window_start": 42}}

### m014 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 61, "detector": "D-5", "episodes": [{"cell": [11, 0], "kind": "outside_ring", "turn_end": 6, "turn_start": 6, "unit": 0}, {"cell": [10, 1], "kind": "outside_ring", "turn_end": 16, "turn_start": 16, "unit": 0}, {"cell": [11, 1], "kind": "outside_ring", "turn_end": 21, "turn_start": 21, "unit": 0}, {"cell": [10, 2], "kind": "outside_ring", "turn_end": 33, "turn_start": 33, "unit": 0}, {"cell": [10, 0], "kind": "outside_ring", "turn_end": 39, "turn_start": 39, "unit": 0}]}
- **P1**: {"count": 10, "detector": "D-8", "episodes": [{"cell": [12, 0], "completion_turn": 15, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10013, "reason": "discretionary_owned", "turn_end": 13, "turn_start": 13, "unit": 2}, {"cell": [12, 0], "completion_turn": 15, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10013, "reason": "discretionary_owned", "turn_end": 14, "turn_start": 14, "unit"

### m015 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [2, 1], "kind": "outside_ring", "turn_end": 29, "turn_start": 29, "unit": 0}]}
- **P1**: {"count": 3, "detector": "D-6", "episodes": [{"cell": [2, 1], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 29, "turn_start": 29, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 36, "turn_start": 36, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 56, "turn_start": 56, "unit": 0}]}

### m015 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [11, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 34, "turn_start": 34, "unit": 0}]}

### m016 seat 0 (water_diagonal, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}]}

### m016 seat 1 (water_diagonal, harvester, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 119, "turn_start": 119, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 120, "turn_start": 120, "unit": 0, "verb": "PLANT"}]}

### m017 seat 0 (open_field, idle, seed 15485863)

- **P1**: {"count": 50, "detector": "D-5", "episodes": [{"cell": [0, 5], "kind": "outside_ring", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [1, 1], "kind": "outside_ring", "turn_end": 14, "turn_start": 14, "unit": 0}, {"cell": [2, 0], "kind": "outside_ring", "turn_end": 18, "turn_start": 18, "unit": 0}, {"cell": [2, 2], "kind": "outside_ring", "turn_end": 22, "turn_start": 22, "unit": 0}, {"cell": [3, 1], "kind": "outside_ring", "turn_end": 26, "turn_start": 26, "unit": 0}]}
- **P1**: {"count": 61, "detector": "D-8", "episodes": [{"cell": [1, 4], "completion_turn": 53, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 4, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10050, "reason": "discretionary_owned", "turn_end": 50, "turn_start": 50, "unit": 2}, {"cell": [1, 4], "completion_turn": 53, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 4, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10050, "reason": "discretionary_owned", "turn_end": 51, "turn_start": 51, "unit": 

### m017 seat 1 (open_field, idle, seed 15485863)

- **P1**: {"count": 48, "detector": "D-5", "episodes": [{"cell": [9, 1], "kind": "outside_ring", "turn_end": 64, "turn_start": 64, "unit": 0}, {"cell": [9, 5], "kind": "outside_ring", "turn_end": 76, "turn_start": 76, "unit": 0}, {"cell": [8, 1], "kind": "outside_ring", "turn_end": 87, "turn_start": 87, "unit": 0}, {"cell": [8, 1], "cumulative": 8, "kind": "cumulative_over_ring", "ring_size": 7, "turn_end": 87, "turn_start": 87, "unit": 0}, {"cell": [8, 2], "cumulative": 8, "kind": "cumulative_over_ring", "ring_size": 7, "turn_end": 94, "turn_start": 94, "unit": 0}]}
- **P1**: {"count": 56, "detector": "D-8", "episodes": [{"cell": [9, 2], "completion_turn": 12, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10010, "reason": "discretionary_owned", "turn_end": 10, "turn_start": 10, "unit": 0}, {"cell": [9, 2], "completion_turn": 12, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10010, "reason": "discretionary_owned", "turn_end": 11, "turn_start": 11, "unit": 

### m018 seat 0 (choke_corridor, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-5", "episodes": [{"cell": [3, 2], "kind": "outside_ring", "turn_end": 6, "turn_start": 6, "unit": 0}, {"cell": [3, 2], "kind": "outside_ring", "turn_end": 36, "turn_start": 36, "unit": 0}]}
- **P1**: {"count": 3, "detector": "D-6", "episodes": [{"cell": [3, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 6, "turn_start": 6, "unit": 0}, {"cell": [3, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 36, "turn_start": 36, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 41, "turn_start": 41, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-8", "episodes": [{"cell": [2, 2], "completion_turn": 32, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10030, "reason": "discretionary_owned", "turn_end": 30, "turn_start": 30, "unit": 0}]}

### m018 seat 1 (choke_corridor, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 2], [7, 2]], "k": 148, "turn_end": 300, "turn_start": 3, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 5, "turn_start": 3, "unit": 2}]}
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 1}}

### m019 seat 0 (forest_dense, harvester, seed 49979687)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 194, "turn_start": 194, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 195, "turn_start": 195, "unit": 0, "verb": "PLANT"}]}

### m019 seat 1 (forest_dense, harvester, seed 49979687)

- **P1**: {"count": 3, "detector": "D-5", "episodes": [{"cell": [6, 3], "kind": "orth_cutoff", "t_late": 284, "turn_end": 288, "turn_start": 288, "unit": 0}, {"cell": [8, 3], "kind": "orth_cutoff", "t_late": 284, "turn_end": 300, "turn_start": 300, "unit": 0}, {"cell": [8, 3], "kind": "global_cutoff", "t_late": 298, "turn_end": 300, "turn_start": 300, "unit": 0}]}
- **P1**: {"count": 50, "detector": "D-8", "episodes": [{"cell": [8, 4], "completion_turn": 98, "eta_opp_at_chop_start": 9, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 120, "reason": "discretionary_owned", "turn_end": 96, "turn_start": 96, "unit": 0}, {"cell": [8, 4], "completion_turn": 98, "eta_opp_at_chop_start": 9, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 120, "reason": "discretionary_owned", "turn_end": 100, "turn_start": 100, "unit": 6}, {"cell

### m020 seat 0 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 42, "detector": "D-5", "episodes": [{"cell": [0, 1], "kind": "outside_ring", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [6, 1], "kind": "outside_ring", "turn_end": 17, "turn_start": 17, "unit": 0}, {"cell": [5, 1], "kind": "outside_ring", "turn_end": 22, "turn_start": 22, "unit": 0}, {"cell": [0, 1], "kind": "outside_ring", "turn_end": 33, "turn_start": 33, "unit": 0}, {"cell": [0, 0], "kind": "outside_ring", "turn_end": 116, "turn_start": 116, "unit": 0}]}
- **P1**: {"count": 47, "detector": "D-6", "episodes": [{"cell": [1, 1], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 32, "turn_start": 31, "unit": null}, {"cell": [1, 1], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 35, "turn_start": 34, "unit": null}, {"cell": [6, 1], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 46, "turn_start": 45, "unit": null}, {"cell": [6, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 52, "turn_start": 51, "unit": null}, {"cell": [6, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 56, "turn_start": 55, "unit": null}]
- **P1**: {"count": 3, "detector": "D-8", "episodes": [{"cell": [3, 2], "completion_turn": 298, "eta_opp_at_chop_start": 3, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 318, "reason": "discretionary_owned", "turn_end": 296, "turn_start": 296, "unit": 2}, {"cell": [3, 2], "completion_turn": 298, "eta_opp_at_chop_start": 3, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 318, "reason": "discretionary_owned", "turn_end": 297, "turn_start": 297, "unit": 2}, {"c

### m020 seat 1 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 3], [10, 2]], "k": 3, "turn_end": 68, "turn_start": 61, "unit": 0}]}
- **P1**: {"count": 20, "detector": "D-5", "episodes": [{"cell": [10, 4], "kind": "outside_ring", "turn_end": 41, "turn_start": 41, "unit": 0}, {"cell": [9, 4], "kind": "outside_ring", "turn_end": 48, "turn_start": 48, "unit": 0}, {"cell": [9, 4], "kind": "outside_ring", "turn_end": 132, "turn_start": 132, "unit": 0}, {"cell": [9, 4], "kind": "outside_ring", "turn_end": 144, "turn_start": 144, "unit": 0}, {"cell": [9, 5], "kind": "outside_ring", "turn_end": 159, "turn_start": 159, "unit": 0}]}
- **P1**: {"count": 44, "detector": "D-6", "episodes": [{"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 38, "turn_start": 37, "unit": null}, {"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 42, "turn_start": 41, "unit": null}, {"cell": [10, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 57, "turn_start": 56, "unit": null}, {"cell": [10, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 62, "turn_start": 61, "unit": null}, {"cell": [10, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 68, "turn_start": 67, "unit": n

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

### m023 seat 0 (open_field, harvester, seed 49979687)

- **P1**: {"count": 49, "detector": "D-5", "episodes": [{"cell": [0, 3], "kind": "outside_ring", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [0, 3], "kind": "outside_ring", "turn_end": 32, "turn_start": 32, "unit": 0}, {"cell": [0, 4], "kind": "outside_ring", "turn_end": 64, "turn_start": 64, "unit": 0}, {"cell": [0, 2], "kind": "outside_ring", "turn_end": 104, "turn_start": 104, "unit": 0}, {"cell": [0, 2], "kind": "outside_ring", "turn_end": 122, "turn_start": 122, "unit": 0}]}
- **P1**: {"count": 27, "detector": "D-8", "episodes": [{"cell": [1, 4], "completion_turn": 45, "eta_opp_at_chop_start": 11, "exact_chop_turns": 4, "flip_turn": null, "health_decreased": false, "kind": "diag_mother_chop", "opponent_harvest_turn": 61, "reason": "discretionary_owned", "turn_end": 42, "turn_start": 42, "unit": 2}, {"cell": [1, 4], "completion_turn": 45, "eta_opp_at_chop_start": 11, "exact_chop_turns": 4, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 61, "reason": "discretionary_owned", "turn_end": 43, "turn_start": 43, "unit": 2}, {"cell"

### m023 seat 1 (open_field, harvester, seed 49979687)

- **P1**: {"count": 47, "detector": "D-5", "episodes": [{"cell": [12, 0], "kind": "outside_ring", "turn_end": 78, "turn_start": 78, "unit": 0}, {"cell": [12, 0], "kind": "outside_ring", "turn_end": 90, "turn_start": 90, "unit": 0}, {"cell": [8, 0], "kind": "outside_ring", "turn_end": 96, "turn_start": 96, "unit": 0}, {"cell": [12, 0], "kind": "outside_ring", "turn_end": 102, "turn_start": 102, "unit": 0}, {"cell": [8, 0], "kind": "outside_ring", "turn_end": 114, "turn_start": 114, "unit": 0}]}
- **P1**: {"count": 17, "detector": "D-6", "episodes": [{"cell": [9, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 73, "turn_start": 72, "unit": null}, {"cell": [9, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 197, "turn_start": 196, "unit": null}, {"cell": [8, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 215, "turn_start": 214, "unit": null}, {"cell": [8, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 216, "turn_start": 215, "unit": null}, {"cell": [9, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 218, "turn_start": 217, "unit"
- **P1**: {"count": 35, "detector": "D-8", "episodes": [{"cell": [11, 0], "completion_turn": 10, "eta_opp_at_chop_start": 8, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 32, "reason": "discretionary_owned", "turn_end": 8, "turn_start": 8, "unit": 0}, {"cell": [11, 0], "completion_turn": 10, "eta_opp_at_chop_start": 8, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 32, "reason": "discretionary_owned", "turn_end": 9, "turn_start": 9, "unit": 0}, {"cell": [11

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 4], [1, 4]], "k": 137, "turn_end": 300, "turn_start": 26, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 26, "turn_start": 24, "unit": 2}]}
- **P1**: {"count": 3, "detector": "D-5", "episodes": [{"cell": [2, 4], "kind": "outside_ring", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [2, 4], "cumulative": 2, "kind": "cumulative_over_ring", "ring_size": 1, "turn_end": 5, "turn_start": 5, "unit": 0}, {"kind": "concurrent_over_ring", "ring_size": 1, "turn_end": 8, "turn_start": 6, "unit": null}]}
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 21-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 21}}

### m024 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 49, "detector": "D-5", "episodes": [{"cell": [10, 0], "kind": "outside_ring", "turn_end": 7, "turn_start": 7, "unit": 0}, {"cell": [10, 0], "kind": "outside_ring", "turn_end": 31, "turn_start": 31, "unit": 0}, {"cell": [10, 0], "kind": "outside_ring", "turn_end": 43, "turn_start": 43, "unit": 0}, {"cell": [10, 0], "kind": "outside_ring", "turn_end": 61, "turn_start": 61, "unit": 0}, {"cell": [10, 0], "kind": "outside_ring", "turn_end": 81, "turn_start": 81, "unit": 0}]}
- **P1**: {"count": 24, "detector": "D-8", "episodes": [{"cell": [11, 1], "completion_turn": 40, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10038, "reason": "discretionary_owned", "turn_end": 38, "turn_start": 38, "unit": 0}, {"cell": [11, 1], "completion_turn": 40, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10038, "reason": "discretionary_owned", "turn_end": 45, "turn_start": 45, "unit"

### m025 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 198, "turn_start": 196, "unit": 2}, {"kind": "no_progress", "turn_end": 201, "turn_start": 199, "unit": 2}]}
- **P1**: {"count": 74, "detector": "D-5", "episodes": [{"cell": [2, 1], "kind": "outside_ring", "turn_end": 23, "turn_start": 23, "unit": 0}, {"cell": [2, 1], "kind": "outside_ring", "turn_end": 31, "turn_start": 31, "unit": 0}, {"cell": [0, 2], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 36, "turn_start": 36, "unit": 0}, {"cell": [2, 0], "kind": "outside_ring", "turn_end": 42, "turn_start": 42, "unit": 0}, {"cell": [2, 0], "cumulative": 5, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 42, "turn_start": 42, "unit": 0}]}
- **P1**: {"count": 8, "detector": "D-6", "episodes": [{"cell": [1, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 70, "turn_start": 70, "unit": 0}, {"cell": [1, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 76, "turn_start": 76, "unit": 0}, {"cell": [0, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 140, "turn_start": 140, "unit": 0}, {"cell": [0, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 172, "turn_start": 172, "unit": 0}, {"cell": [0, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 206, "turn_start": 206, "unit": 0}]}
- **P1**: {"count": 28, "detector": "D-8", "episodes": [{"cell": [1, 2], "completion_turn": 36, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 4, "flip_turn": null, "health_decreased": false, "kind": "diag_mother_chop", "opponent_harvest_turn": 10033, "reason": "discretionary_owned", "turn_end": 33, "turn_start": 33, "unit": 2}, {"cell": [1, 2], "completion_turn": 36, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 4, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10033, "reason": "discretionary_owned", "turn_end": 36, "turn_start": 36, "unit":
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust;PICK 0 BANANA;MOVE 2 5 4", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2;MOVE 2 4 5"}}

### m025 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[12, 6], [11, 6]], "k": 7, "turn_end": 218, "turn_start": 204, "unit": 2}]}
- **P1**: {"count": 11, "detector": "D-5", "episodes": [{"cell": [13, 7], "kind": "outside_ring", "turn_end": 31, "turn_start": 31, "unit": 0}, {"cell": [13, 7], "kind": "outside_ring", "turn_end": 43, "turn_start": 43, "unit": 0}, {"cell": [13, 7], "kind": "outside_ring", "turn_end": 55, "turn_start": 55, "unit": 0}, {"cell": [13, 7], "kind": "outside_ring", "turn_end": 67, "turn_start": 67, "unit": 0}, {"cell": [13, 7], "kind": "outside_ring", "turn_end": 79, "turn_start": 79, "unit": 0}]}
- **P1**: {"count": 11, "detector": "D-6", "episodes": [{"cell": [13, 7], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 79, "turn_start": 79, "unit": 0}, {"cell": [12, 6], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 85, "turn_start": 85, "unit": 0}, {"cell": [13, 6], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 118, "turn_start": 118, "unit": 0}, {"cell": [12, 5], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 124, "turn_start": 124, "unit": 0}, {"cell": [12, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 157, "turn_start": 157, "unit": 0}]}
- **P1**: {"count": 22, "detector": "D-8", "episodes": [{"cell": [12, 6], "completion_turn": 40, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10038, "reason": "discretionary_owned", "turn_end": 38, "turn_start": 38, "unit": 0}, {"cell": [12, 6], "completion_turn": 40, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10038, "reason": "discretionary_owned", "turn_end": 40, "turn_start": 40, "unit"

### m026 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 74, "turn_start": 72, "unit": 2}]}
- **P1**: {"count": 10, "detector": "D-5", "episodes": [{"cell": [3, 5], "kind": "outside_ring", "turn_end": 42, "turn_start": 42, "unit": 0}, {"cell": [3, 5], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 42, "turn_start": 42, "unit": 0}, {"cell": [2, 5], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 47, "turn_start": 47, "unit": 0}, {"cell": [2, 4], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 54, "turn_start": 54, "unit": 0}, {"cell": [3, 5], "kind": "outside_ring", "turn_end": 60, "turn_start": 60, "unit": 
- **P1**: {"count": 34, "detector": "D-6", "episodes": [{"cell": [1, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 58, "turn_start": 57, "unit": null}, {"cell": [1, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 64, "turn_start": 63, "unit": null}, {"cell": [1, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 79, "turn_start": 78, "unit": null}, {"cell": [1, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 82, "turn_start": 81, "unit": null}, {"cell": [3, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 93, "turn_start": 92, "unit": null}]
- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "harvest", "turn_end": 85, "turn_start": 72, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "harvest", "turn_end": 300, "turn_start": 72, "unit": 0}]}
- **P1**: {"count": 10, "detector": "D-8", "episodes": [{"cell": [2, 5], "completion_turn": 34, "eta_opp_at_chop_start": 4, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 54, "reason": "discretionary_owned", "turn_end": 32, "turn_start": 32, "unit": 2}, {"cell": [2, 5], "completion_turn": 34, "eta_opp_at_chop_start": 4, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 54, "reason": "discretionary_owned", "turn_end": 33, "turn_start": 33, "unit": 2}, {"cell": [
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 72-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 72}}

### m026 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 3, "detector": "D-1", "episodes": [{"cells": [[8, 5], [9, 5]], "k": 4, "turn_end": 46, "turn_start": 38, "unit": 0}, {"cells": [[9, 5], [10, 5]], "k": 6, "turn_end": 61, "turn_start": 48, "unit": 0}, {"cells": [[9, 5], [10, 5]], "k": 115, "turn_end": 300, "turn_start": 70, "unit": 0}]}
- **P1**: {"count": 3, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 40, "turn_start": 38, "unit": 2}, {"kind": "no_progress", "turn_end": 49, "turn_start": 47, "unit": 2}, {"kind": "no_progress", "turn_end": 73, "turn_start": 71, "unit": 2}]}
- **P1**: {"count": 7, "detector": "D-5", "episodes": [{"cell": [10, 5], "kind": "outside_ring", "turn_end": 29, "turn_start": 29, "unit": 0}, {"cell": [10, 5], "cumulative": 2, "kind": "cumulative_over_ring", "ring_size": 1, "turn_end": 29, "turn_start": 29, "unit": 0}, {"cell": [8, 5], "kind": "outside_ring", "turn_end": 37, "turn_start": 37, "unit": 0}, {"cell": [8, 5], "cumulative": 3, "kind": "cumulative_over_ring", "ring_size": 1, "turn_end": 37, "turn_start": 37, "unit": 0}, {"cell": [10, 5], "kind": "outside_ring", "turn_end": 66, "turn_start": 66, "unit": 0}]}
- **P1**: {"count": 28, "detector": "D-6", "episodes": [{"cell": [11, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 43, "turn_start": 42, "unit": null}, {"cell": [11, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 46, "turn_start": 45, "unit": null}, {"cell": [11, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 58, "turn_start": 57, "unit": null}, {"cell": [11, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 59, "turn_start": 58, "unit": null}, {"cell": [8, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 70, "turn_start": 69, "unit": nu
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 71-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 71}}

### m027 seat 0 (multi_door, idle, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 130, "why": "candidate makes no own-inventory/own-cargo progress over turns 22-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 22}}

### m027 seat 1 (multi_door, idle, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 130, "why": "candidate makes no own-inventory/own-cargo progress over turns 18-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 18}}

### m028 seat 0 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 42, "turn_start": 42, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 43, "turn_start": 43, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 129, "why": "candidate makes no own-inventory/own-cargo progress over turns 48-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 48}}

### m028 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 31, "turn_start": 31, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 32, "turn_start": 32, "unit": 0, "verb": "PLANT"}]}

### m029 seat 0 (open_field, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 5], [9, 5]], "k": 124, "turn_end": 275, "turn_start": 27, "unit": 2}]}
- **P4**: {"detail": {"live_end": 287, "terminal_from": 300, "why": "candidate makes no own-inventory/own-cargo progress over turns 19-287 while work remains through turn 287 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 287, "window_start": 19}}

### m029 seat 1 (open_field, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 4], [11, 5]], "k": 133, "turn_end": 290, "turn_start": 24, "unit": 2}]}
- **P4**: {"detail": {"live_end": 293, "terminal_from": 300, "why": "candidate makes no own-inventory/own-cargo progress over turns 22-293 while work remains through turn 293 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 293, "window_start": 22}}

### m030 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 3, "detector": "D-1", "episodes": [{"cells": [[2, 4], [2, 3]], "k": 5, "turn_end": 35, "turn_start": 25, "unit": 0}, {"cells": [[2, 4], [2, 3]], "k": 11, "turn_end": 65, "turn_start": 43, "unit": 0}, {"cells": [[2, 4], [2, 3]], "k": 22, "turn_end": 111, "turn_start": 67, "unit": 0}]}
- **P1**: {"count": 9, "detector": "D-5", "episodes": [{"cell": [3, 4], "kind": "outside_ring", "turn_end": 134, "turn_start": 134, "unit": 0}, {"cell": [3, 4], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 134, "turn_start": 134, "unit": 0}, {"cell": [4, 4], "kind": "outside_ring", "turn_end": 141, "turn_start": 141, "unit": 0}, {"cell": [4, 4], "cumulative": 5, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 141, "turn_start": 141, "unit": 0}, {"cell": [6, 4], "kind": "outside_ring", "turn_end": 155, "turn_start": 155, "unit": 0}]}
- **P1**: {"count": 39, "detector": "D-6", "episodes": [{"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 34, "turn_start": 33, "unit": null}, {"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 35, "turn_start": 34, "unit": null}, {"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 40, "turn_start": 39, "unit": null}, {"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 60, "turn_start": 59, "unit": null}, {"cell": [1, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 62, "turn_start": 61, "unit": null}]
- **P1**: {"count": 1, "detector": "D-8", "episodes": [{"cell": [2, 4], "completion_turn": 130, "eta_opp_at_chop_start": 5, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 152, "reason": "discretionary_owned", "turn_end": 128, "turn_start": 128, "unit": 0}]}
- **P4**: {"detail": {"live_end": 111, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 20-111 while work remains through turn 111 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 111, "window_start": 20}}

### m030 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[12, 4], [11, 4]], "k": 7, "turn_end": 16, "turn_start": 1, "unit": 0}, {"cells": [[10, 4], [9, 4]], "k": 141, "turn_end": 300, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 19, "turn_start": 17, "unit": 2}]}
- **P4**: {"detail": {"live_end": 300, "terminal_from": 301, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-300 while work remains through turn 300 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 300, "window_start": 1}}

### m031 seat 0 (forest_dense, idle, seed 49979687)

- **P1**: {"count": 30, "detector": "D-5", "episodes": [{"cell": [0, 4], "kind": "outside_ring", "turn_end": 62, "turn_start": 62, "unit": 0}, {"cell": [1, 5], "kind": "outside_ring", "turn_end": 66, "turn_start": 66, "unit": 0}, {"cell": [1, 4], "kind": "outside_ring", "turn_end": 77, "turn_start": 77, "unit": 0}, {"cell": [2, 5], "kind": "outside_ring", "turn_end": 83, "turn_start": 83, "unit": 0}, {"cell": [1, 4], "kind": "outside_ring", "turn_end": 131, "turn_start": 131, "unit": 0}]}
- **P1**: {"count": 20, "detector": "D-8", "episodes": [{"cell": [0, 3], "completion_turn": 94, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 2, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10093, "reason": "discretionary_owned", "turn_end": 93, "turn_start": 93, "unit": 6}, {"cell": [0, 3], "completion_turn": 94, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 2, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10093, "reason": "discretionary_owned", "turn_end": 102, "turn_start": 102, "unit"

### m031 seat 1 (forest_dense, idle, seed 49979687)

- **P1**: {"count": 14, "detector": "D-5", "episodes": [{"cell": [6, 5], "kind": "outside_ring", "turn_end": 66, "turn_start": 66, "unit": 0}, {"cell": [5, 4], "kind": "outside_ring", "turn_end": 70, "turn_start": 70, "unit": 0}, {"cell": [4, 5], "kind": "outside_ring", "turn_end": 74, "turn_start": 74, "unit": 0}, {"cell": [4, 4], "kind": "outside_ring", "turn_end": 85, "turn_start": 85, "unit": 0}, {"cell": [5, 3], "kind": "outside_ring", "turn_end": 91, "turn_start": 91, "unit": 0}]}
- **P1**: {"count": 12, "detector": "D-8", "episodes": [{"cell": [7, 5], "completion_turn": 96, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 2, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10095, "reason": "discretionary_owned", "turn_end": 95, "turn_start": 95, "unit": 6}, {"cell": [7, 5], "completion_turn": 96, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 2, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10095, "reason": "discretionary_owned", "turn_end": 98, "turn_start": 98, "unit": 

### m033 seat 0 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}

### m033 seat 1 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}

### m035 seat 1 (orchard_eligible, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"live_end": 120, "terminal_from": 145, "why": "candidate makes no own-inventory/own-cargo progress over turns 59-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 59}}

### m036 seat 0 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 6, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 79, "turn_start": 77, "unit": 2}, {"kind": "no_progress", "turn_end": 107, "turn_start": 105, "unit": 2}, {"kind": "no_progress", "turn_end": 111, "turn_start": 109, "unit": 2}, {"kind": "no_progress", "turn_end": 132, "turn_start": 130, "unit": 2}, {"kind": "no_progress", "turn_end": 179, "turn_start": 177, "unit": 2}]}
- **P1**: {"count": 66, "detector": "D-5", "episodes": [{"cell": [1, 5], "kind": "outside_ring", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [1, 5], "kind": "outside_ring", "turn_end": 29, "turn_start": 29, "unit": 0}, {"cell": [0, 5], "kind": "outside_ring", "turn_end": 36, "turn_start": 36, "unit": 0}, {"cell": [0, 5], "cumulative": 3, "kind": "cumulative_over_ring", "ring_size": 2, "turn_end": 36, "turn_start": 36, "unit": 0}, {"cell": [1, 6], "kind": "outside_ring", "turn_end": 42, "turn_start": 42, "unit": 0}]}

### m036 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 39, "detector": "D-5", "episodes": [{"cell": [10, 7], "kind": "outside_ring", "turn_end": 62, "turn_start": 62, "unit": 0}, {"cell": [10, 6], "kind": "outside_ring", "turn_end": 95, "turn_start": 95, "unit": 0}, {"cell": [11, 5], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 123, "turn_start": 123, "unit": 0}, {"cell": [10, 6], "kind": "outside_ring", "turn_end": 131, "turn_start": 131, "unit": 0}, {"cell": [10, 6], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 131, "turn_start": 131, "unit": 0}]}
- **P1**: {"count": 60, "detector": "D-8", "episodes": [{"cell": [13, 7], "completion_turn": 10, "eta_opp_at_chop_start": 15, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 32, "reason": "discretionary_owned", "turn_end": 8, "turn_start": 8, "unit": 0}, {"cell": [13, 7], "completion_turn": 10, "eta_opp_at_chop_start": 15, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 32, "reason": "discretionary_owned", "turn_end": 9, "turn_start": 9, "unit": 0}, {"cell": [

### m037 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 151, "turn_start": 151, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 152, "turn_start": 152, "unit": 0, "verb": "PLANT"}]}

### m037 seat 1 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 147, "turn_start": 147, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 148, "turn_start": 148, "unit": 0, "verb": "PLANT"}]}

### m038 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [0, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 128, "turn_start": 128, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 121, "turn_start": 121, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 122, "turn_start": 122, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 127, "turn_start": 127, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 128, "turn_start": 128, "unit": 0, "verb": "PLANT"}]}
- **P4**: {"detail": {"live_end": 120, "terminal_from": 150, "why": "candidate makes no own-inventory/own-cargo progress over turns 38-120 while work remains through turn 120 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 120, "window_start": 38}}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 51, "turn_start": 51, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PLANT"}]}

### m039 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 5, "detector": "D-5", "episodes": [{"cell": [4, 2], "kind": "outside_ring", "turn_end": 45, "turn_start": 45, "unit": 0}, {"cell": [4, 2], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 45, "turn_start": 45, "unit": 0}, {"cell": [5, 2], "kind": "outside_ring", "turn_end": 54, "turn_start": 54, "unit": 0}, {"cell": [5, 2], "cumulative": 5, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 54, "turn_start": 54, "unit": 0}, {"kind": "concurrent_over_ring", "ring_size": 3, "turn_end": 300, "turn_start": 46, "unit": null}]}
- **P1**: {"count": 38, "detector": "D-6", "episodes": [{"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 64, "turn_start": 63, "unit": null}, {"cell": [4, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 80, "turn_start": 79, "unit": null}, {"cell": [4, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 81, "turn_start": 80, "unit": null}, {"cell": [5, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 98, "turn_start": 97, "unit": null}, {"cell": [5, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 99, "turn_start": 98, "unit": null}]

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 7, "detector": "D-5", "episodes": [{"cell": [6, 2], "kind": "outside_ring", "turn_end": 50, "turn_start": 50, "unit": 0}, {"cell": [7, 2], "kind": "outside_ring", "turn_end": 63, "turn_start": 63, "unit": 0}, {"cell": [8, 2], "kind": "outside_ring", "turn_end": 80, "turn_start": 80, "unit": 0}, {"cell": [9, 2], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 87, "turn_start": 87, "unit": 0}, {"cell": [9, 1], "cumulative": 5, "kind": "cumulative_over_ring", "ring_size": 3, "turn_end": 96, "turn_start": 96, "unit": 0}]}

## Report-tier flags (non-blocking)

- m018 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m024 seat 0 [r5-horizon]: full wood carrier since turn 21 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m030 seat 1 [r5-horizon]: full wood carrier since turn 1 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
