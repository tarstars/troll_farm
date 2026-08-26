# fuzz panel report [CANDIDATE (candidate vs parent)] - 20260826-candidate-3b-stuck-holder-release panel (ruleoff arm)

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `942eb22355a32f3355e241bea0afc5fbee63ba6d786cb4d5b41666763b7f5c01`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `../../claude_1/cure3b/arm-ruleoff.rs` (sha256 8823a21f9061c3efe2ef0acea6167a4d4eb397727889456a7c3b1d6688c126d6)
- parent: `../../cgauto/submissions/candidate-door1-pure-deletion.rs` (sha256 547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 17.7 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 240 |
| clean_games | 188 |
| banana_activated_games | 24 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 0 |
| blocking_games | 52 |
| flagged_games | 1 |
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
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(10,2)/r=P/b=0/k=0 u2=NONE/BANK(1,1)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 2;MOVE 2 12 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2;MOVE 2 12 3"}}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 42-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 42}}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 1], "kind": "outside_ring", "turn_end": 15, "turn_start": 15, "unit": 2}]}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[12, 2], [13, 2]], "k": 10, "turn_end": 32, "turn_start": 12, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [13, 1], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 47, "turn_start": 47, "unit": 2}]}

### m014 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(10,0)/r=P/b=0/k=0 u2=NONE/BANK(1,2)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 3;MOVE 2 6 1", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3;MOVE 2 6 1"}}

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

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(10,3)/r=P/b=0/k=0 u2=NONE/TREE(10,3)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 2;MOVE 2 4 5", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2;MOVE 2 4 5"}}

### m028 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 4], [8, 4]], "k": 3, "turn_end": 32, "turn_start": 26, "unit": 0}]}

### m035 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(9,3)/r=P/b=0/k=0 u2=NONE/TREE(9,3)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 3;MOVE 2 6 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3;MOVE 2 6 3"}}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 38, "turn_start": 38, "unit": 0}]}
- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 37, "turn_start": 37, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 38, "turn_start": 38, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 51, "turn_start": 51, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 52, "turn_start": 52, "unit": 0, "verb": "PLANT"}]}

### m039 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 26}}

### m040 seat 0 (forest_dense, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 4], [3, 4]], "k": 12, "turn_end": 200, "turn_start": 176, "unit": 0}]}

### m045 seat 0 (orchard_eligible, chopper_aggressor, seed 49979687)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(9,1)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 7", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 7"}}

### m046 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 2], [6, 2]], "k": 93, "turn_end": 200, "turn_start": 14, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 11}}

### m048 seat 1 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}

### m054 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(11,1)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 2", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2"}}

### m058 seat 1 (open_field, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 3], [6, 4]], "k": 6, "turn_end": 42, "turn_start": 29, "unit": 0}]}

### m059 seat 0 (choke_corridor, harvester, seed 86028121)

- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 11-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 11}}

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

### m063 seat 1 (open_field, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 3], [10, 4]], "k": 75, "turn_end": 200, "turn_start": 50, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (10, 3)<->(10, 4) over turns 50-200 (151 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 47-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 47}}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}

### m065 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(10,1)/r=N/b=0/k=0 u2=NONE/TREE(10,1)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;WAIT;MOVE 2 8 1", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;WAIT;MOVE 2 8 1"}}

### m066 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[5, 2], [4, 2]], "k": 10, "turn_end": 24, "turn_start": 3, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (5, 2)<->(4, 2) over turns 3-24 (22 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 2], [3, 2]], "k": 3, "turn_end": 8, "turn_start": 1, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 1], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 1-8 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m070 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[2, 2], [2, 1]], "k": 74, "turn_end": 200, "turn_start": 52, "unit": 0}, {"cells": [[10, 2], [9, 2]], "k": 5, "turn_end": 18, "turn_start": 7, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 44-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 44}}

### m072 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 26, "turn_start": 26, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PLANT"}]}

### m072 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}

### m073 seat 0 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 2], [2, 2]], "k": 32, "turn_end": 69, "turn_start": 5, "unit": 0}]}
- **P4**: {"detail": {"live_end": 68, "terminal_from": 75, "why": "candidate makes no own-inventory/own-cargo progress over turns 5-68 while work remains through turn 68 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 68, "window_start": 5}}

### m074 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(10,0)/r=P/b=0/k=0 u2=NONE/TREE(10,0)/r=N/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 7;WAIT", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 7;WAIT"}}

### m078 seat 1 (choke_corridor, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 3], [6, 3]], "k": 3, "turn_end": 10, "turn_start": 4, "unit": 0}]}

### m079 seat 0 (forest_sparse, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 3], [11, 2]], "k": 81, "turn_end": 200, "turn_start": 38, "unit": 2}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 33-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 33}}

### m082 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 5], [4, 5]], "k": 91, "turn_end": 200, "turn_start": 17, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (3, 5)<->(4, 5) over turns 17-200 (184 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 16-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 16}}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 21, "turn_start": 19, "unit": 2}]}

### m084 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 5], [6, 5]], "k": 84, "turn_end": 200, "turn_start": 32, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 26-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 26}}

### m085 seat 0 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 4], [2, 4]], "k": 4, "turn_end": 25, "turn_start": 17, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 11, "turn_start": 11, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 12, "turn_start": 12, "unit": 0, "verb": "PLANT"}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/CELL(2,4)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 5", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 5"}}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 5], [3, 5]], "k": 3, "turn_end": 9, "turn_start": 2, "unit": 2}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 5)<->(3, 5) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m090 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 5], [6, 5]], "k": 3, "turn_end": 18, "turn_start": 11, "unit": 2}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 19, "turn_start": 17, "unit": 0}]}

### m092 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 5, "detector": "D-6", "episodes": [{"cell": [2, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 82, "turn_start": 82, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 88, "turn_start": 88, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 93, "turn_start": 93, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 98, "turn_start": 98, "unit": 0}, {"cell": [2, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 103, "turn_start": 103, "unit": 0}]}

### m095 seat 0 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 4, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 21, "turn_start": 21, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 22, "turn_start": 22, "unit": 0, "verb": "PLANT"}, {"kind": "banana_before_train", "turn_end": 27, "turn_start": 27, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 28, "turn_start": 28, "unit": 0, "verb": "PLANT"}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(9,2)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 3"}}

### m099 seat 1 (choke_corridor, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[9, 2], [10, 2]], "k": 96, "turn_end": 200, "turn_start": 8, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 8-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 8}}

### m104 seat 0 (orchard_eligible, idle, seed 32452843)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(11,4)/r=P/b=0/k=0 u2=NONE/BANK(1,2)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 0 4;MOVE 2 6 6", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 0 4;MOVE 2 6 6"}}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

### m110 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[6, 2], [5, 2]], "k": 97, "turn_end": 200, "turn_start": 6, "unit": 0}]}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 1-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 1}}

### m114 seat 0 (orchard_eligible, idle, seed 982451653)

- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v7 t=1 u0=NONE/TREE(12,3)/r=N/b=0/k=0 u2=NONE/TREE(12,3)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rs=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;WAIT;MOVE 2 1 2", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;WAIT;MOVE 2 1 2"}}

### m115 seat 0 (multi_door, chopper_aggressor, seed 15485863)

- **P1**: {"count": 2, "detector": "D-9", "episodes": [{"kind": "banana_before_train", "turn_end": 49, "turn_start": 49, "unit": 0, "verb": "PICK"}, {"kind": "banana_before_train", "turn_end": 50, "turn_start": 50, "unit": 0, "verb": "PLANT"}]}

## Report-tier flags (non-blocking)

- m082 seat 1 [r5-horizon]: full wood carrier since turn 16 never DROPs at a door within the bounded banking horizon of 30 turns - I-21 forced banking violated

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
