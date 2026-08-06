# fuzz panel report - 20260802-banana-restoration-r2 fuzz panel (candidate eac2eb36 vs parent a8eb3b2b)

- candidate: `/home/runner/work/troll_farm/troll_farm/chatgpt_1/banana-solve/candidate-banana-r2.min.rs` (sha256 bbe54a489c98222d2e382b112cf26034defaf6e287b0576a1c3282438deea951)
- parent: `/tmp/banana-pinned/cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 23.0 s

## Verdict: BLOCK

## Coverage

| metric | value |
|---|---|
| games | 240 |
| banana_activated_games | 161 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 12 |
| blocking_games | 22 |
| flagged_games | 100 |

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

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-5", "episodes": [{"cell": [4, 1], "kind": "outside_ring", "turn_end": 15, "turn_start": 15, "unit": 2}]}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 21, "turn_start": 21, "unit": 0}]}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 17, "turn_start": 15, "unit": 2}]}

### m022 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [2, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 11, "turn_start": 11, "unit": 0}]}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 25, "turn_start": 23, "unit": 0}]}

### m024 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 200, "unit": 0}]}

### m038 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [0, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 44, "turn_start": 44, "unit": 0}]}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 37, "turn_start": 37, "unit": 0}, {"cell": [8, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 42, "turn_start": 42, "unit": 0}]}

### m048 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 26, "turn_start": 26, "unit": 0}]}

### m061 seat 0 (choke_corridor, idle, seed 15485863)

- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 3], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}

### m066 seat 0 (choke_corridor, harvester, seed 982451653)

- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (5, 2)<->(4, 2) over turns 3-24 (22 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m068 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [3, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 70, "turn_start": 70, "unit": 0}]}

### m068 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P1**: {"count": 6, "detector": "D-6", "episodes": [{"cell": [9, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 84, "turn_start": 84, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 108, "turn_start": 108, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 113, "turn_start": 113, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 116, "turn_start": 116, "unit": 0}, {"cell": [9, 4], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 119, "turn_start": 119, "unit": 0}]}

### m070 seat 0 (choke_corridor, harvester, seed 67867967)

- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 1], free_capacity 0) exhibits a two-cell alternation cells (4, 2)<->(3, 2) over turns 1-8 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m071 seat 1 (open_field, idle, seed 86028121)

- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "bank_pick", "turn_end": 200, "turn_start": 200, "unit": 2}]}

### m075 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 5], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 35, "turn_start": 35, "unit": 0}]}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 23, "turn_start": 21, "unit": 2}]}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 5)<->(3, 5) over turns 2-9 (8 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 2}

### m095 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 28, "turn_start": 28, "unit": 0}]}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

## Report-tier flags (non-blocking)

- m001 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m001 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m003 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m004 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m005 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m010 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m010 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m011 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m011 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m012 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m014 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m016 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m016 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m020 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m020 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m029 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m029 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m033 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m033 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m034 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m034 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m037 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m037 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m038 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m038 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m039 seat 1 [inherited-parent-D1]: candidate D-1 episodes (2) on a map where the parent also fails D-1 (2 episodes) - known family defect, report only
- m043 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m043 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m044 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m044 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m046 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m048 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m048 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m050 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m051 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m051 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m053 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m053 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m054 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m054 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m057 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m057 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m059 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m060 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m061 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m062 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m062 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m065 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m066 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m067 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m067 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m070 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m070 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m072 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m072 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m073 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m075 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m075 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m076 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m076 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m078 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m079 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m079 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m081 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m081 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m085 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m085 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m085 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m087 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m087 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m088 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m089 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m089 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m090 seat 0 [inherited-parent-D1]: candidate D-1 episodes (2) on a map where the parent also fails D-1 (2 episodes) - known family defect, report only
- m091 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m091 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m092 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m093 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m093 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m095 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m095 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m096 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m096 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m099 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m101 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m101 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m104 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m110 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m111 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m111 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m112 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m112 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m113 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m113 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m115 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m115 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m116 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m116 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m117 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m117 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m118 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only

---

**VERDICT: BLOCK**
