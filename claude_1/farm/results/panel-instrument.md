# fuzz panel report [CANDIDATE (candidate vs parent)] - 20260826-banana-farm-candidate panel (instrument arm)

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `c786b6ed46a57084983ad3206a6ff0c2aa7e1d0818500caaed85a4d82e724cb2`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `../../claude_1/farm/arm-instrument.rs` (sha256 354d1302f79ddc241ae49c5c0b1763ad045077bfb5f74d6e850bf43a43376b41)
- parent: `../../cgauto/submissions/candidate-door1-pure-deletion.rs` (sha256 547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 12.5 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 240 |
| clean_games | 144 |
| banana_activated_games | 97 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 0 |
| blocking_games | 96 |
| flagged_games | 4 |
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

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [1, 3]], "k": 5, "turn_end": 29, "turn_start": 19, "unit": 2}]}
- **P1**: {"count": 36, "detector": "D-5", "episodes": [{"cell": [3, 4], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}, {"cell": [2, 3], "kind": "outside_ring", "turn_end": 103, "turn_start": 103, "unit": 0}, {"cell": [2, 3], "cumulative": 3, "kind": "cumulative_over_ring", "ring_size": 2, "turn_end": 103, "turn_start": 103, "unit": 0}, {"cell": [1, 4], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 2, "turn_end": 104, "turn_start": 104, "unit": 2}, {"cell": [1, 4], "cumulative": 4, "kind": "cumulative_over_ring", "ring_size": 2, "turn_end": 113, "turn_start": 113, 
- **P1**: {"count": 16, "detector": "D-6", "episodes": [{"cell": [2, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 47, "turn_start": 46, "unit": null}, {"cell": [2, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 60, "turn_start": 59, "unit": null}, {"cell": [2, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 83, "turn_start": 82, "unit": null}, {"cell": [2, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 89, "turn_start": 88, "unit": null}, {"cell": [2, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 107, "turn_start": 106, "unit": null

### m003 seat 1 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 119, "turn_start": 109, "unit": 0}]}
- **P1**: {"count": 17, "detector": "D-6", "episodes": [{"cell": [6, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 39, "turn_start": 38, "unit": null}, {"cell": [6, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 41, "turn_start": 40, "unit": null}, {"cell": [6, 6], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 62, "turn_start": 61, "unit": null}, {"cell": [6, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 68, "turn_start": 67, "unit": null}, {"cell": [6, 6], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 84, "turn_start": 83, "unit": null}]
- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"bananas": 1, "kind": "lost_bananas", "turn_end": 190, "turn_start": 189, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 200, "unit": 2}]}

### m004 seat 0 (orchard_eligible, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[10, 2], [11, 2]], "k": 74, "turn_end": 200, "turn_start": 52, "unit": 0}, {"cells": [[8, 2], [9, 2]], "k": 3, "turn_end": 31, "turn_start": 24, "unit": 2}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=2 fp=0 fh=0 fl=0 fd=a fe=0 fw=0 fE=- fW=- u0=NONE/TREE(10,2)/r=P/b=0/k=0 u2=NONE/BANK(1,1)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 2;MOVE 2 12 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2;MOVE 2 12 3"}}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 42-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 42}}

### m007 seat 1 (forest_dense, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 2], [6, 2]], "k": 4, "turn_end": 35, "turn_start": 27, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (7, 2)<->(6, 2) over turns 27-35 (9 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 0}

### m009 seat 1 (water_diagonal, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 0], [10, 0]], "k": 3, "turn_end": 145, "turn_start": 138, "unit": 2}]}
- **P1**: {"count": 4, "detector": "D-5", "episodes": [{"cell": [7, 0], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}, {"cell": [10, 2], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 151, "turn_start": 151, "unit": 2}, {"cell": [9, 0], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 191, "turn_start": 191, "unit": 0}, {"cell": [9, 0], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 200, "turn_start": 200, "unit": 2}]}
- **P1**: {"count": 14, "detector": "D-6", "episodes": [{"cell": [8, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 39, "turn_start": 38, "unit": null}, {"cell": [8, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 42, "turn_start": 41, "unit": null}, {"cell": [8, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 74, "turn_start": 73, "unit": null}, {"cell": [8, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 92, "turn_start": 91, "unit": null}, {"cell": [9, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 95, "turn_start": 94, "unit": null}]
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 196, "unit": 2}]}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 2], [10, 2]], "k": 3, "turn_end": 33, "turn_start": 27, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 29, "turn_start": 29, "unit": 2}, {"cell": [12, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 2}]}

### m014 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=2 fp=0 fh=0 fl=0 fd=a fe=0 fw=0 fE=- fW=- u0=NONE/TREE(10,0)/r=P/b=0/k=0 u2=NONE/BANK(1,2)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 3;MOVE 2 6 1", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3;MOVE 2 6 1"}}

### m014 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 1], [9, 1]], "k": 96, "turn_end": 200, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 5}}

### m015 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [2, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 30, "turn_start": 30, "unit": 0}]}

### m015 seat 1 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [9, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 29, "turn_start": 29, "unit": 0}]}

### m016 seat 0 (water_diagonal, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 13, "turn_start": 13, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 14, "turn_start": 14, "unit": 0, "verb": "PLANT"}]}

### m019 seat 0 (forest_dense, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 2], [0, 3]], "k": 11, "turn_end": 28, "turn_start": 6, "unit": 0}]}

### m019 seat 1 (forest_dense, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 3], [9, 3]], "k": 83, "turn_end": 200, "turn_start": 34, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (8, 3)<->(9, 3) over turns 34-200 (167 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 0}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 29-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 29}}

### m021 seat 0 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [7, 2]], "k": 16, "turn_end": 59, "turn_start": 27, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 199, "unit": 2}]}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 17, "turn_start": 15, "unit": 2}]}

### m023 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [0, 2], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 10, "detector": "D-6", "episodes": [{"cell": [3, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 86, "turn_start": 85, "unit": null}, {"cell": [3, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 97, "turn_start": 96, "unit": null}, {"cell": [3, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 98, "turn_start": 97, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 111, "turn_start": 110, "unit": null}, {"cell": [3, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 134, "turn_start": 133, "unit": nu

### m023 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 4, "detector": "D-5", "episodes": [{"cell": [5, 0], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}, {"cell": [8, 2], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 91, "turn_start": 91, "unit": 2}, {"cell": [7, 0], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 110, "turn_start": 110, "unit": 0}, {"cell": [7, 0], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 117, "turn_start": 117, "unit": 2}]}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [0, 4]], "k": 83, "turn_end": 200, "turn_start": 33, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (1, 4)<->(0, 4) over turns 33-200 (168 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 0}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 23-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 23}}

### m024 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [8, 1], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}

### m025 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 1], [2, 1]], "k": 3, "turn_end": 116, "turn_start": 109, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [0, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 40, "turn_start": 40, "unit": 2}, {"cell": [1, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 46, "turn_start": 46, "unit": 0}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=2 fp=0 fh=0 fl=0 fd=a fe=0 fw=0 fE=- fW=- u0=CELL(0,2)/CELL(0,2)/r=N/b=0/k=0 u2=NONE/CELL(0,2)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;PICK 0 BANANA;MOVE 2 5 4", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2;MOVE 2 4 5"}}

### m025 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 6], [10, 6]], "k": 3, "turn_end": 86, "turn_start": 80, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [13, 6], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 40, "turn_start": 40, "unit": 0}]}

### m026 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 21, "detector": "D-6", "episodes": [{"cell": [2, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 35, "turn_start": 34, "unit": null}, {"cell": [2, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 47, "turn_start": 46, "unit": null}, {"cell": [2, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 48, "turn_start": 47, "unit": null}, {"cell": [2, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 60, "turn_start": 59, "unit": null}, {"cell": [2, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 61, "turn_start": 60, "unit": null}]
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 65-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 65}}

### m028 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [3, 0], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 28, "turn_start": 28, "unit": 2}]}

### m030 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 3], [10, 3]], "k": 10, "turn_end": 51, "turn_start": 31, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 199, "unit": 2}]}

### m030 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 3], [2, 3]], "k": 6, "turn_end": 47, "turn_start": 35, "unit": 0}]}
- **P1**: {"count": 12, "detector": "D-6", "episodes": [{"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 33, "turn_start": 32, "unit": null}, {"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 53, "turn_start": 52, "unit": null}, {"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 65, "turn_start": 64, "unit": null}, {"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 66, "turn_start": 65, "unit": null}, {"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 90, "turn_start": 89, "unit": n

### m032 seat 0 (forest_sparse, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 2], [1, 3]], "k": 10, "turn_end": 29, "turn_start": 9, "unit": 0}]}
- **P1**: {"count": 6, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 11, "turn_start": 8, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 15, "turn_start": 12, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 19, "turn_start": 16, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 23, "turn_start": 20, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 27, "turn_start": 24, "unit": 2}]}
- **P1**: {"count": 9, "detector": "D-6", "episodes": [{"cell": [1, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 51, "turn_start": 51, "unit": 2}, {"cell": [3, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 79, "turn_start": 79, "unit": 0}, {"cell": [3, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 80, "turn_start": 80, "unit": 2}, {"cell": [2, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 82, "turn_start": 82, "unit": 2}, {"cell": [3, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 107, "turn_start": 107, "unit": 2}]}
- **P1**: {"count": 3, "detector": "D-7", "episodes": [{"bananas": 1, "kind": "lost_bananas", "turn_end": 106, "turn_start": 105, "unit": 0}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 130, "turn_start": 129, "unit": 0}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 89, "turn_start": 88, "unit": 2}]}

### m032 seat 1 (forest_sparse, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 5], [10, 5]], "k": 12, "turn_end": 112, "turn_start": 87, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [10, 5], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [11, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 55, "turn_start": 55, "unit": 2}]}

### m035 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 40, "turn_start": 40, "unit": 2}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=2 fp=0 fh=0 fl=0 fd=a fe=0 fw=0 fE=- fW=- u0=CELL(0,3)/CELL(0,3)/r=N/b=0/k=0 u2=NONE/CELL(0,3)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;PICK 0 BANANA;MOVE 2 6 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3;MOVE 2 6 3"}}

### m035 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [11, 2], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [11, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 30, "turn_start": 30, "unit": 0}]}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 51, "turn_start": 51, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PLANT"}]}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 26}}

### m040 seat 0 (forest_dense, harvester, seed 67867967)

- **P1**: {"count": 4, "detector": "D-1", "episodes": [{"cells": [[2, 1], [1, 1]], "k": 40, "turn_end": 115, "turn_start": 34, "unit": 0}, {"cells": [[1, 1], [1, 0]], "k": 42, "turn_end": 200, "turn_start": 115, "unit": 0}, {"cells": [[0, 2], [0, 3]], "k": 40, "turn_end": 115, "turn_start": 35, "unit": 6}, {"cells": [[0, 2], [0, 1]], "k": 42, "turn_end": 200, "turn_start": 115, "unit": 6}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 34-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 34}}

### m040 seat 1 (forest_dense, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [7, 2]], "k": 76, "turn_end": 200, "turn_start": 48, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 45-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 45}}

### m042 seat 0 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 2], [2, 3]], "k": 3, "turn_end": 67, "turn_start": 61, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 63, "turn_start": 63, "unit": 0}]}

### m042 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [8, 0], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [10, 0], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 46, "turn_start": 46, "unit": 0}, {"cell": [11, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 74, "turn_start": 74, "unit": 2}]}

### m045 seat 0 (orchard_eligible, chopper_aggressor, seed 49979687)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=0 fp=0 fh=0 fl=0 fd=- fe=0 fw=0 fE=- fW=- u0=NONE/TREE(9,1)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 7", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 7"}}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m049 seat 0 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 3, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 44, "turn_start": 35, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 90, "turn_start": 82, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 110, "turn_start": 107, "unit": 2}]}

### m049 seat 1 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[8, 3], [9, 3]], "k": 10, "turn_end": 29, "turn_start": 8, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 64, "turn_start": 55, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"bananas": 1, "kind": "lost_bananas", "turn_end": 87, "turn_start": 86, "unit": 2}]}

### m050 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 8, "detector": "D-6", "episodes": [{"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 60, "turn_start": 59, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 101, "turn_start": 100, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 132, "turn_start": 131, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 137, "turn_start": 136, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 143, "turn_start": 142, "unit":

### m054 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=0 fp=0 fh=0 fl=0 fd=- fe=0 fw=0 fE=- fW=- u0=NONE/TREE(11,1)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 2", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2"}}

### m056 seat 0 (forest_dense, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 47, "turn_start": 37, "unit": 2}]}
- **P1**: {"count": 4, "detector": "D-6", "episodes": [{"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 79, "turn_start": 78, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 81, "turn_start": 80, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 82, "turn_start": 81, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 97, "turn_start": 96, "unit": null}]}
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 198, "unit": 2}]}

### m056 seat 1 (forest_dense, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 2], [8, 2]], "k": 11, "turn_end": 200, "turn_start": 177, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 42, "turn_start": 33, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 173, "turn_start": 171, "unit": 2}]}
- **P1**: {"count": 29, "detector": "D-5", "episodes": [{"cell": [5, 0], "kind": "outside_ring", "turn_end": 67, "turn_start": 67, "unit": 2}, {"cell": [6, 1], "kind": "outside_ring", "turn_end": 73, "turn_start": 73, "unit": 2}, {"cell": [4, 0], "kind": "outside_ring", "turn_end": 82, "turn_start": 82, "unit": 2}, {"cell": [4, 0], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 82, "turn_start": 82, "unit": 2}, {"cell": [5, 1], "kind": "outside_ring", "turn_end": 90, "turn_start": 90, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [3, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 194, "turn_start": 193, "unit": null}]}
- **P1**: {"count": 8, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 186, "turn_start": 173, "unit": 0}, {"kind": "carried_overage", "provenance": "harvest", "turn_end": 188, "turn_start": 175, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 173, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "harvest", "turn_end": 200, "turn_start": 175, "unit": 0}, {"kind": "carried_overage", "provenance": "harvest", "turn_end": 152, "turn_start": 139, "unit": 2}]}

### m058 seat 1 (open_field, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 3], [6, 4]], "k": 6, "turn_end": 42, "turn_start": 29, "unit": 0}]}

### m059 seat 1 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 4], [9, 3]], "k": 94, "turn_end": 200, "turn_start": 12, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 11}}

### m060 seat 0 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 0], [0, 1]], "k": 13, "turn_end": 30, "turn_start": 3, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [0, 3], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 13, "detector": "D-6", "episodes": [{"cell": [0, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 45, "turn_start": 44, "unit": null}, {"cell": [0, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 103, "turn_start": 102, "unit": null}, {"cell": [0, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 104, "turn_start": 103, "unit": null}, {"cell": [0, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 106, "turn_start": 105, "unit": null}, {"cell": [0, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 109, "turn_start": 108, "unit"

### m060 seat 1 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [5, 4], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 18, "detector": "D-6", "episodes": [{"cell": [6, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 36, "turn_start": 35, "unit": null}, {"cell": [6, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 59, "turn_start": 58, "unit": null}, {"cell": [6, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 60, "turn_start": 59, "unit": null}, {"cell": [6, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 78, "turn_start": 77, "unit": null}, {"cell": [6, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 83, "turn_start": 82, "unit": null}]

### m061 seat 0 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 26, "turn_start": 24, "unit": 0}]}

### m061 seat 1 (choke_corridor, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 26, "turn_start": 24, "unit": 0}, {"kind": "no_progress", "turn_end": 66, "turn_start": 64, "unit": 0}]}

### m062 seat 1 (water_diagonal, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 39, "turn_start": 39, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 40, "turn_start": 40, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 45, "turn_start": 45, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 46, "turn_start": 46, "unit": 0, "verb": "PLANT"}]}

### m063 seat 1 (open_field, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 3], [10, 4]], "k": 75, "turn_end": 200, "turn_start": 50, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (10, 3)<->(10, 4) over turns 50-200 (151 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 47-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 47}}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}

### m065 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=2 fp=0 fh=0 fl=0 fd=a fe=0 fw=0 fE=- fW=- u0=CELL(0,2)/CELL(0,2)/r=N/b=0/k=0 u2=NONE/CELL(0,2)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;PICK 0 BANANA;MOVE 2 8 1", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;WAIT;MOVE 2 8 1"}}

### m065 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 1], [11, 1]], "k": 9, "turn_end": 36, "turn_start": 17, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (10, 1)<->(11, 1) over turns 17-36 (20 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m066 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 12, "turn_end": 29, "turn_start": 4, "unit": 2}]}
- **P1**: {"count": 9, "detector": "D-6", "episodes": [{"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 48, "turn_start": 47, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 66, "turn_start": 65, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 80, "turn_start": 79, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 81, "turn_start": 80, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 95, "turn_start": 94, "unit": null}]}
- **P1**: {"count": 26, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 200, "unit": 0}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 56, "turn_start": 55, "unit": 2}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 62, "turn_start": 61, "unit": 2}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 68, "turn_start": 67, "unit": 2}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 74, "turn_start": 73, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 4-29 (26 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m068 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 1], [0, 1]], "k": 12, "turn_end": 166, "turn_start": 142, "unit": 2}]}
- **P1**: {"count": 2, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 115, "turn_start": 112, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 134, "turn_start": 123, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 124, "turn_start": 122, "unit": 0}]}
- **P1**: {"count": 7, "detector": "D-6", "episodes": [{"cell": [3, 3], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 85, "turn_start": 85, "unit": 2}, {"cell": [1, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 90, "turn_start": 90, "unit": 0}, {"cell": [3, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 130, "turn_start": 130, "unit": 2}, {"cell": [2, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 132, "turn_start": 132, "unit": 2}, {"cell": [3, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 177, "turn_start": 177, "unit": 2}]}
- **P1**: {"count": 11, "detector": "D-7", "episodes": [{"bananas": 1, "kind": "lost_bananas", "turn_end": 59, "turn_start": 58, "unit": 0}, {"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 127, "turn_start": 114, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 114, "unit": 0}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 42, "turn_start": 41, "unit": 2}, {"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 148, "turn_start": 135, "unit": 2}]}

### m068 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 4, "detector": "D-1", "episodes": [{"cells": [[10, 3], [10, 4]], "k": 3, "turn_end": 120, "turn_start": 114, "unit": 2}, {"cells": [[8, 4], [7, 4]], "k": 15, "turn_end": 166, "turn_start": 135, "unit": 2}, {"cells": [[8, 4], [7, 4]], "k": 4, "turn_end": 184, "turn_start": 176, "unit": 2}, {"cells": [[8, 4], [7, 4]], "k": 3, "turn_end": 200, "turn_start": 193, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 40, "turn_start": 32, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 115, "turn_start": 113, "unit": 0}]}
- **P1**: {"count": 7, "detector": "D-6", "episodes": [{"cell": [9, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 71, "turn_start": 71, "unit": 0}, {"cell": [9, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 89, "turn_start": 89, "unit": 0}, {"cell": [9, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 95, "turn_start": 95, "unit": 0}, {"cell": [8, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 98, "turn_start": 98, "unit": 2}, {"cell": [9, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 103, "turn_start": 103, "unit": 2}]}
- **P1**: {"count": 16, "detector": "D-7", "episodes": [{"bananas": 1, "kind": "lost_bananas", "turn_end": 34, "turn_start": 33, "unit": 0}, {"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 118, "turn_start": 105, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 105, "unit": 0}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 87, "turn_start": 86, "unit": 2}, {"bananas": 1, "kind": "lost_bananas", "turn_end": 95, "turn_start": 94, "unit": 2}]}

### m069 seat 0 (water_diagonal, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 178, "turn_start": 176, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [0, 1], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 181, "turn_start": 168, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 168, "unit": 0}]}

### m069 seat 1 (water_diagonal, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 138, "turn_start": 136, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [6, 4], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 9, "detector": "D-6", "episodes": [{"cell": [7, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 54, "turn_start": 53, "unit": null}, {"cell": [7, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 55, "turn_start": 54, "unit": null}, {"cell": [7, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 69, "turn_start": 68, "unit": null}, {"cell": [7, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 91, "turn_start": 90, "unit": null}, {"cell": [7, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 102, "turn_start": 101, "unit": null}
- **P1**: {"count": 2, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "bank_pick", "turn_end": 142, "turn_start": 129, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 129, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 136-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 136}}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [7, 2]], "k": 17, "turn_end": 61, "turn_start": 27, "unit": 0}]}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[2, 2], [2, 1]], "k": 74, "turn_end": 200, "turn_start": 52, "unit": 0}, {"cells": [[10, 2], [9, 2]], "k": 5, "turn_end": 18, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 44-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 44}}

### m071 seat 0 (open_field, idle, seed 86028121)

- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 199, "unit": 2}]}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m073 seat 0 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 10, "detector": "D-6", "episodes": [{"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 48, "turn_start": 47, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 53, "turn_start": 52, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 84, "turn_start": 83, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 89, "turn_start": 88, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 120, "turn_start": 119, "unit": null

### m074 seat 0 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 0], [3, 0]], "k": 4, "turn_end": 29, "turn_start": 21, "unit": 0}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=2 fp=0 fh=0 fl=0 fd=a fe=0 fw=0 fE=- fW=- u0=CELL(0,7)/CELL(0,7)/r=N/b=0/k=0 u2=NONE/CELL(1,6)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;PICK 0 BANANA;MOVE 2 5 1", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 7;WAIT"}}

### m078 seat 1 (choke_corridor, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 3], [6, 3]], "k": 3, "turn_end": 10, "turn_start": 4, "unit": 0}]}

### m079 seat 0 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 81, "turn_end": 200, "turn_start": 38, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 33-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 33}}

### m083 seat 0 (open_field, harvester, seed 86028121)

- **P1**: {"count": 44, "detector": "D-6", "episodes": [{"cell": [1, 7], "eta_opp_h": 0, "kind": "opp_harvest_eta", "min_own_eta": 0, "turn_end": 96, "turn_start": 96, "unit": 2}, {"cell": [0, 5], "eta_opp_h": 0, "kind": "opp_harvest_eta", "min_own_eta": 0, "turn_end": 103, "turn_start": 103, "unit": 2}, {"cell": [0, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 48, "turn_start": 47, "unit": null}, {"cell": [0, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 53, "turn_start": 52, "unit": null}, {"cell": [0, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 59, "tur

### m083 seat 1 (open_field, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 3], [8, 3]], "k": 8, "turn_end": 28, "turn_start": 12, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 7, "turn_start": 4, "unit": 2}]}
- **P1**: {"count": 39, "detector": "D-6", "episodes": [{"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 40, "turn_start": 39, "unit": null}, {"cell": [9, 3], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 41, "turn_start": 40, "unit": null}, {"cell": [10, 3], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 42, "turn_start": 41, "unit": null}, {"cell": [9, 3], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 47, "turn_start": 46, "unit": null}, {"cell": [9, 3], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 53, "turn_start": 52, "unit": null

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 5], "kind": "outside_ring", "turn_end": 36, "turn_start": 36, "unit": 0}]}
- **P1**: {"count": 10, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "harvest", "turn_end": 76, "turn_start": 63, "unit": 0}, {"kind": "carried_overage", "provenance": "harvest", "turn_end": 102, "turn_start": 89, "unit": 0}, {"kind": "carried_overage", "provenance": "harvest", "turn_end": 103, "turn_start": 90, "unit": 0}, {"kind": "carried_overage", "provenance": "harvest", "turn_end": 136, "turn_start": 123, "unit": 0}, {"kind": "carried_overage", "provenance": "harvest", "turn_end": 162, "turn_start": 149, "unit": 0}]}

### m084 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 57, "turn_start": 47, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [8, 0], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [2, 4]], "k": 4, "turn_end": 25, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=0 fp=0 fh=0 fl=0 fd=- fe=0 fw=0 fE=- fW=- u0=NONE/CELL(2,4)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 5", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 5"}}

### m086 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [3, 5], "kind": "outside_ring", "turn_end": 162, "turn_start": 162, "unit": 0}]}
- **P1**: {"count": 6, "detector": "D-6", "episodes": [{"cell": [1, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 105, "turn_start": 104, "unit": null}, {"cell": [1, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 118, "turn_start": 117, "unit": null}, {"cell": [2, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 135, "turn_start": 134, "unit": null}, {"cell": [1, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 160, "turn_start": 159, "unit": null}, {"cell": [1, 5], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 172, "turn_start": 171, "unit

### m088 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [0, 1], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [0, 1], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 30, "turn_start": 30, "unit": 0}]}

### m088 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 29, "turn_start": 29, "unit": 0}]}

### m090 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 5], [6, 5]], "k": 3, "turn_end": 18, "turn_start": 11, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 19, "turn_start": 17, "unit": 0}]}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 1], [3, 2]], "k": 20, "turn_end": 57, "turn_start": 16, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [2, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 68, "turn_start": 68, "unit": 2}, {"cell": [2, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 82, "turn_start": 82, "unit": 2}]}

### m092 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-2", "episodes": [{"drops": 2, "picks": 2, "turn_end": 77, "turn_start": 67, "unit": 2}, {"drops": 2, "picks": 2, "turn_end": 84, "turn_start": 81, "unit": 2}]}
- **P1**: {"count": 7, "detector": "D-6", "episodes": [{"cell": [6, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 90, "turn_start": 90, "unit": 2}, {"cell": [6, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 94, "turn_start": 94, "unit": 2}, {"cell": [6, 3], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 106, "turn_start": 106, "unit": 2}, {"cell": [7, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 118, "turn_start": 118, "unit": 0}, {"cell": [6, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 123, "turn_start": 123, "unit": 2}]}

### m094 seat 1 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [8, 0], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 22, "turn_start": 22, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=0 fp=0 fh=0 fl=0 fd=- fe=0 fw=0 fE=- fW=- u0=NONE/TREE(9,2)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3"}}

### m097 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [0, 1], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 199, "unit": 2}]}

### m098 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [0, 6], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [2, 6], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 39, "turn_start": 39, "unit": 2}]}

### m098 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 4], [7, 4]], "k": 8, "turn_end": 30, "turn_start": 13, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 3], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 30, "turn_start": 30, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 3], free_capacity 0) exhibits a two-cell alternation cells (6, 4)<->(7, 4) over turns 13-30 (18 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m099 seat 0 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 11, "detector": "D-6", "episodes": [{"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 79, "turn_start": 78, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 80, "turn_start": 79, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 86, "turn_start": 85, "unit": null}, {"cell": [2, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 116, "turn_start": 115, "unit": null}, {"cell": [1, 2], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 118, "turn_start": 117, "unit": nu

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 2], [10, 2]], "k": 96, "turn_end": 200, "turn_start": 8, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 8-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 8}}

### m104 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=2 fp=0 fh=0 fl=0 fd=a fe=0 fw=0 fE=- fW=- u0=NONE/TREE(11,4)/r=P/b=0/k=0 u2=NONE/BANK(1,2)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 0 4;MOVE 2 6 6", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 0 4;MOVE 2 6 6"}}

### m106 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 8, "detector": "D-6", "episodes": [{"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 130, "turn_start": 129, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 143, "turn_start": 142, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 144, "turn_start": 143, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 156, "turn_start": 155, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 170, "turn_start": 169, "unit
- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"bananas": 1, "kind": "lost_bananas", "turn_end": 136, "turn_start": 135, "unit": 2}]}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

### m109 seat 0 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[0, 2], [0, 3]], "k": 61, "turn_end": 200, "turn_start": 77, "unit": 0}]}
- **P1**: {"count": 5, "detector": "D-6", "episodes": [{"cell": [0, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 54, "turn_start": 53, "unit": null}, {"cell": [0, 0], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 77, "turn_start": 76, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 119, "turn_start": 118, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 159, "turn_start": 158, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 199, "turn_start": 198, "unit": n
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 76-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 76}}

### m109 seat 1 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 4, "detector": "D-5", "episodes": [{"cell": [7, 4], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 0}, {"cell": [8, 2], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 132, "turn_start": 132, "unit": 0}, {"cell": [9, 2], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 145, "turn_start": 145, "unit": 2}, {"cell": [8, 3], "cumulative": 9, "kind": "cumulative_over_ring", "ring_size": 8, "turn_end": 150, "turn_start": 150, "unit": 2}]}
- **P1**: {"count": 5, "detector": "D-6", "episodes": [{"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 36, "turn_start": 35, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 60, "turn_start": 59, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 84, "turn_start": 83, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 108, "turn_start": 107, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 132, "turn_start": 131, "unit": nul

### m110 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 2], [2, 2]], "k": 18, "turn_end": 49, "turn_start": 13, "unit": 0}]}
- **P1**: {"count": 5, "detector": "D-6", "episodes": [{"cell": [2, 1], "eta_opp_h": 0, "kind": "opp_harvest_eta", "min_own_eta": 0, "turn_end": 66, "turn_start": 66, "unit": 0}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 42, "turn_start": 41, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 43, "turn_start": 42, "unit": null}, {"cell": [2, 1], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 107, "turn_start": 106, "unit": null}, {"cell": [1, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 197, "turn_start": 196

### m110 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [5, 2]], "k": 97, "turn_end": 200, "turn_start": 6, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 1}}

### m114 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=2 fp=0 fh=0 fl=0 fd=a fe=0 fw=0 fE=- fW=- u0=NONE/CELL(0,2)/r=P/b=0/k=0 u2=CELL(1,1)/CELL(1,1)/r=N/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 2;PICK 2 BANANA", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;WAIT;MOVE 2 1 2"}}

### m114 seat 1 (orchard_eligible, idle, seed 982451653)

- **P1**: {"count": 19, "detector": "D-5", "episodes": [{"cell": [11, 1], "kind": "outside_ring", "turn_end": 30, "turn_start": 30, "unit": 2}, {"cell": [13, 3], "cumulative": 6, "kind": "cumulative_over_ring", "ring_size": 5, "turn_end": 114, "turn_start": 114, "unit": 0}, {"cell": [13, 1], "cumulative": 6, "kind": "cumulative_over_ring", "ring_size": 5, "turn_end": 114, "turn_start": 114, "unit": 2}, {"cell": [13, 3], "cumulative": 6, "kind": "cumulative_over_ring", "ring_size": 5, "turn_end": 124, "turn_start": 124, "unit": 0}, {"cell": [13, 1], "cumulative": 6, "kind": "cumulative_over_ring", "ring_

### m115 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 50, "turn_start": 50, "unit": 0, "verb": "PLANT"}]}

## Report-tier flags (non-blocking)

- m019 seat 1 [r5-horizon]: full wood carrier since turn 29 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m024 seat 0 [r5-horizon]: full wood carrier since turn 23 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m024 seat 0 [r5-horizon]: full wood carrier since turn 21 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated
- m056 seat 1 [margin-collapse]: banana-activated map: candidate margin -58 < parent margin 50 - 100
- m069 seat 1 [r5-horizon]: full wood carrier since turn 136 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
