# fuzz panel report [CANDIDATE (candidate vs parent)] - 20260826-banana-farm-candidate SMOKE (farm-off arm, 8 maps)

- **run identity: `candidate` -- CANDIDATE (candidate vs parent)**. A number from this report may only ever be quoted as a candidate number (review B5).
- instrument: `fuzz-panel/5-two-player-phase-merged-referee`  |  corpus: `c5-two-player-phase-merged-2026-08-11`
- referee sha256: `c786b6ed46a57084983ad3206a6ff0c2aa7e1d0818500caaed85a4d82e724cb2`  |  engine.rs sha256: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`
- phase order: MOVE -> HARVEST -> PLANT -> CHOP -> PICK -> TRAIN -> DROP -> MINE (rust/src/game/engine.rs:755-806)
- supported commands: CHOP DROP HARVEST MINE MOVE MSG PICK PLANT TRAIN WAIT (an unimplemented verb is a retained `unsupported_verb` error: the row stays in the denominator and the aggregate is GATE_UNREADY)
- candidate: `../../claude_1/farm/arm-farmoff.rs` (sha256 d3a280bbde879a85e0c9cb5a1b7af3c2ccca970716d251b1bd7b02ee1349dd55)
- parent: `../../cgauto/submissions/candidate-door1-pure-deletion.rs` (sha256 547fa706cc1c684a1f8c2a08174792d95e553b2382facfe15884d2ef544070b0)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 8 (x2 seats = 16 candidate games + 16 parent games), 200 turns each
- wall time: 5.8 s

## Verdict: BLOCK (candidate run)

## Coverage

| metric | value |
|---|---|
| games | 16 |
| clean_games | 14 |
| banana_activated_games | 1 |
| orchard_eligible_games | 1 |
| orchard_inertness_checks_passed | 0 |
| blocking_games | 2 |
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

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 16, "turn_start": 14, "unit": 2}]}

### m004 seat 0 (orchard_eligible, idle, seed 67867967)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[10, 2], [11, 2]], "k": 74, "turn_end": 200, "turn_start": 52, "unit": 0}, {"cells": [[8, 2], [9, 2]], "k": 3, "turn_end": 31, "turn_start": 24, "unit": 2}]}
- **P3**: {"detail": {"candidate": "MSG yamo-carry-regen-transit-idle-harvest-rust NARRATE v8 t=1 fs=0 fp=0 fh=0 fl=0 fd=- fe=0 fw=0 fE=- fW=- u0=NONE/TREE(10,2)/r=P/b=0/k=0 u2=NONE/BANK(1,1)/r=P/b=0/k=0 pz=1 sp=0 wc=0 sw=0 so=0 sn=0 sf=0 kp=0 kq=0 kl=0 kr=0 rd=0 rg=0 ri=0 rx=0 rf=0 rt=0 ro=0 nl=0 nl_producer=0 nl_door=0 nl_admissibility=0 nl_other=0 ka=0 kc=0 xc=0 xw=0 xn=0 xp=0 xg=0 xd=0 xj=0;MOVE 0 1 2;MOVE 2 12 3", "first_divergence_turn": 1, "parent": "MSG yamo-carry-regen-transit-idle-harvest-rust;MOVE 0 1 2;MOVE 2 12 3"}}
- **P4**: {"detail": {"live_end": 200, "terminal_from": 201, "why": "candidate makes no own-inventory/own-cargo progress over turns 42-200 while work remains through turn 200 (>= 60 live turns) [RAW liveness: every stall window over a non-terminal world blocks]", "window_end": 200, "window_start": 42}}

---

**VERDICT: BLOCK -- CANDIDATE (candidate vs parent)**
