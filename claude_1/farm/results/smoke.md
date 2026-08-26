# fuzz panel report [CANDIDATE (candidate vs parent)] - 20260826-banana-farm-candidate SMOKE (instrument arm, 8 maps)

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `c786b6ed46a57084983ad3206a6ff0c2aa7e1d0818500caaed85a4d82e724cb2`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `../../claude_1/farm/arm-instrument.rs` (sha256 354d1302f79ddc241ae49c5c0b1763ad045077bfb5f74d6e850bf43a43376b41)
- parent: `../../cgauto/submissions/candidate-door1-pure-deletion.rs` (sha256 547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 8 (x2 seats = 16 candidate games + 16 parent games), 200 turns each
- wall time: 7.3 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 16 |
| clean_games | 12 |
| banana_activated_games | 4 |
| orchard_eligible_games | 1 |
| orchard_inertness_checks_passed | 0 |
| blocking_games | 4 |
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
| choke_corridor | 4 |
| forest_dense | 2 |
| multi_door | 2 |
| open_field | 2 |
| orchard_eligible | 2 |
| single_door_tent | 2 |
| water_diagonal | 2 |

| opponent profile | games |
|---|---|
| chopper_aggressor | 4 |
| harvester | 6 |
| idle | 6 |

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

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
