# fuzz panel report - 20260802-banana-restoration-r2 fuzz panel (candidate eac2eb36 vs parent a8eb3b2b)

- candidate: `../banana-restoration-r2/candidate-banana-r2.min.rs` (sha256 eac2eb36b5f2abf0e92b62615584f3d9135055a09e6eec0bbee7c4e4a6a4f23b)
- parent: `../../cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 14.6 s

## Verdict: BLOCK

## Coverage

| metric | value |
|---|---|
| games | 240 |
| banana_activated_games | 171 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 12 |
| blocking_games | 47 |
| flagged_games | 89 |

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

### m003 seat 1 (single_door_tent, harvester, seed 49979687)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[1, 3], [0, 3]], "k": 79, "turn_end": 200, "turn_start": 41, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [34, 35, 38, 39, 40, 41, 44, 45, 46, 47], "why": "candidate makes no progress over turns 34-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 34}}

### m007 seat 0 (forest_dense, idle, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 4], [3, 4]], "k": 17, "turn_end": 200, "turn_start": 165, "unit": 0}]}

### m012 seat 0 (single_door_tent, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"parent_progress_turns": [20], "why": "candidate makes no progress over turns 19-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 19}}

### m012 seat 1 (single_door_tent, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"parent_progress_turns": [20, 21], "why": "candidate makes no progress over turns 12-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 12}}

### m015 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P4**: {"detail": {"parent_progress_turns": [13, 14, 15, 18, 19], "why": "candidate makes no progress over turns 9-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 9}}

### m021 seat 1 (choke_corridor, idle, seed 49979687)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 24, "turn_start": 22, "unit": 2}]}

### m024 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 0], [8, 0]], "k": 73, "turn_end": 200, "turn_start": 54, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [45, 46, 49, 50, 51, 52, 55, 56, 69, 70], "why": "candidate makes no progress over turns 44-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 44}}

### m024 seat 1 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[9, 3], [8, 3]], "k": 4, "turn_end": 55, "turn_start": 47, "unit": 2}, {"cells": [[9, 3], [8, 3]], "k": 3, "turn_end": 101, "turn_start": 95, "unit": 2}]}

### m025 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[10, 6], [9, 6]], "k": 6, "turn_end": 30, "turn_start": 18, "unit": 0}]}
- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [12, 5], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 49, "turn_start": 49, "unit": 0}, {"cell": [13, 6], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 49, "turn_start": 49, "unit": 2}]}

### m028 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"parent_progress_turns": [17, 20, 21], "why": "candidate makes no progress over turns 17-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 17}}

### m028 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"parent_progress_turns": [20, 21, 24, 25], "why": "candidate makes no progress over turns 12-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 12}}

### m032 seat 0 (forest_sparse, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"parent_progress_turns": [20, 21, 22, 28, 29], "why": "candidate makes no progress over turns 20-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 20}}

### m035 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [13, 4], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 39, "turn_start": 39, "unit": 0}]}

### m036 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 11, "detector": "D-6", "episodes": [{"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 38, "turn_start": 37, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 66, "turn_start": 65, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 67, "turn_start": 66, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 95, "turn_start": 94, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 96, "turn_start": 95, "unit": n

### m038 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [0, 4], "eta_opp_x": 1, "kind": "opp_chop_eta", "turn_end": 44, "turn_start": 44, "unit": 0}]}

### m038 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 2, "detector": "D-6", "episodes": [{"cell": [8, 2], "eta_opp_x": 2, "kind": "opp_chop_eta", "turn_end": 37, "turn_start": 37, "unit": 0}, {"cell": [8, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 42, "turn_start": 42, "unit": 0}]}

### m042 seat 0 (water_diagonal, chopper_aggressor, seed 982451653)

- **P4**: {"detail": {"parent_progress_turns": [22, 23, 24, 27, 28], "why": "candidate makes no progress over turns 18-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 18}}

### m042 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 0], [11, 1]], "k": 18, "turn_end": 64, "turn_start": 28, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [29, 30, 32], "why": "candidate makes no progress over turns 22-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 22}}

### m048 seat 0 (forest_sparse, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 26, "turn_start": 26, "unit": 0}]}

### m050 seat 0 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 2], [2, 2]], "k": 87, "turn_end": 200, "turn_start": 25, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [24, 25], "why": "candidate makes no progress over turns 24-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 24}}

### m050 seat 1 (choke_corridor, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [171, 172, 175, 176, 182, 183, 184, 187, 188], "why": "candidate makes no progress over turns 45-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 45}}

### m056 seat 1 (forest_dense, harvester, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[4, 0], [5, 0]], "k": 8, "turn_end": 96, "turn_start": 79, "unit": 0}]}
- **P2**: {"detail": "full wood carrier (carry [0, 0, 0, 0, 0, 2], free_capacity 0) exhibits a two-cell alternation cells (4, 0)<->(5, 0) over turns 79-96 (18 states, >= 3 A->B->A cycles) with cargo unchanged and no DROP - violates I-19 (no monotone door approach), I-20 (non-progress beyond the one-turn conflict tolerance) and I-21 (banking commitment never completes); a D-1 episode by construction", "unit": 0}

### m059 seat 0 (choke_corridor, harvester, seed 86028121)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 4], [2, 3]], "k": 15, "turn_end": 92, "turn_start": 61, "unit": 2}]}

### m060 seat 1 (forest_sparse, harvester, seed 982451653)

- **P1**: {"count": 17, "detector": "D-6", "episodes": [{"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 38, "turn_start": 37, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 52, "turn_start": 51, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 54, "turn_start": 53, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 6, "turn_end": 66, "turn_start": 65, "unit": null}, {"cell": [8, 4], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 79, "turn_start": 78, "unit": null}]
- **P4**: {"detail": {"parent_progress_turns": [45, 46], "why": "candidate makes no progress over turns 45-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 45}}

### m064 seat 0 (single_door_tent, idle, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 11, "turn_start": 9, "unit": 2}]}

### m065 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"parent_progress_turns": [32], "why": "candidate makes no progress over turns 32-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 32}}

### m066 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 4, "detector": "D-1", "episodes": [{"cells": [[10, 2], [9, 2]], "k": 24, "turn_end": 61, "turn_start": 12, "unit": 0}, {"cells": [[9, 2], [10, 2]], "k": 4, "turn_end": 73, "turn_start": 65, "unit": 0}, {"cells": [[9, 2], [10, 2]], "k": 3, "turn_end": 83, "turn_start": 77, "unit": 0}, {"cells": [[7, 2], [6, 2]], "k": 39, "turn_end": 200, "turn_start": 122, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}
- **P1**: {"count": 3, "detector": "D-6", "episodes": [{"cell": [11, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 55, "turn_start": 54, "unit": null}, {"cell": [11, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 67, "turn_start": 66, "unit": null}, {"cell": [11, 2], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 93, "turn_start": 92, "unit": null}]}

### m068 seat 0 (forest_dense, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"parent_progress_turns": [104, 105], "why": "candidate makes no progress over turns 102-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 102}}

### m068 seat 1 (forest_dense, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"parent_progress_turns": [101, 102, 105, 106, 107, 108, 110, 111, 112, 113], "why": "candidate makes no progress over turns 101-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 101}}

### m073 seat 0 (choke_corridor, harvester, seed 15485863)

- **P4**: {"detail": {"parent_progress_turns": [67, 68, 69, 70, 71, 72], "why": "candidate makes no progress over turns 14-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 14}}

### m073 seat 1 (choke_corridor, harvester, seed 15485863)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[7, 2], [8, 2]], "k": 22, "turn_end": 54, "turn_start": 10, "unit": 0}]}
- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 6, "turn_start": 4, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [109, 118], "why": "candidate makes no progress over turns 101-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 101}}

### m074 seat 1 (orchard_eligible, idle, seed 32452843)

- **P1**: {"count": 1, "detector": "D-7", "episodes": [{"kind": "unbanked_at_end", "provenance": "harvest", "turn_end": 200, "turn_start": 194, "unit": 0}]}

### m075 seat 0 (multi_door, chopper_aggressor, seed 49979687)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [1, 5], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 35, "turn_start": 35, "unit": 0}]}

### m084 seat 0 (single_door_tent, idle, seed 982451653)

- **P1**: {"count": 4, "detector": "D-7", "episodes": [{"kind": "carried_overage", "provenance": "harvest", "turn_end": 65, "turn_start": 52, "unit": 0}, {"kind": "carried_overage", "provenance": "harvest", "turn_end": 66, "turn_start": 53, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "harvest", "turn_end": 200, "turn_start": 52, "unit": 0}, {"kind": "unbanked_at_end", "provenance": "harvest", "turn_end": 200, "turn_start": 53, "unit": 0}]}
- **P4**: {"detail": {"parent_progress_turns": [60, 68, 69], "why": "candidate makes no progress over turns 58-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 58}}

### m088 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"parent_progress_turns": [13, 16, 17], "why": "candidate makes no progress over turns 13-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 13}}

### m088 seat 1 (water_diagonal, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"parent_progress_turns": [17, 20, 21, 22, 24, 25], "why": "candidate makes no progress over turns 16-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 16}}

### m090 seat 0 (choke_corridor, harvester, seed 982451653)

- **P4**: {"detail": {"parent_progress_turns": [191, 192, 195, 196, 197, 198, 199], "why": "candidate makes no progress over turns 106-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 106}}

### m090 seat 1 (choke_corridor, harvester, seed 982451653)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [37, 38, 39, 40, 43, 44], "why": "candidate makes no progress over turns 36-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 36}}

### m095 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P1**: {"count": 1, "detector": "D-6", "episodes": [{"cell": [12, 2], "eta_opp_x": 0, "kind": "opp_chop_eta", "turn_end": 28, "turn_start": 28, "unit": 0}]}

### m097 seat 0 (water_diagonal, idle, seed 15485863)

- **P1**: {"count": 2, "detector": "D-1", "episodes": [{"cells": [[0, 2], [0, 3]], "k": 3, "turn_end": 79, "turn_start": 73, "unit": 2}, {"cells": [[1, 3], [0, 3]], "k": 3, "turn_end": 92, "turn_start": 86, "unit": 2}]}

### m098 seat 0 (open_field, chopper_aggressor, seed 32452843)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[3, 5], [3, 6]], "k": 9, "turn_end": 36, "turn_start": 18, "unit": 2}]}

### m098 seat 1 (open_field, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"parent_progress_turns": [32, 33], "why": "candidate makes no progress over turns 28-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 28}}

### m100 seat 0 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[2, 3], [2, 2]], "k": 27, "turn_end": 100, "turn_start": 45, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [100, 101, 103], "why": "candidate makes no progress over turns 41-103 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 103, "window_start": 41}}
- **P4**: {"detail": {"parent_progress_turns": [108, 109], "why": "candidate makes no progress over turns 106-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 106}}

### m100 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}

### m106 seat 1 (choke_corridor, harvester, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 7, "turn_start": 5, "unit": 2}]}

### m118 seat 0 (choke_corridor, chopper_aggressor, seed 67867967)

- **P4**: {"detail": {"parent_progress_turns": [9, 10, 12, 13], "why": "candidate makes no progress over turns 9-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 9}}

### m118 seat 1 (choke_corridor, chopper_aggressor, seed 67867967)

- **P1**: {"count": 1, "detector": "D-4", "episodes": [{"kind": "no_progress", "turn_end": 3, "turn_start": 1, "unit": 2}]}
- **P4**: {"detail": {"parent_progress_turns": [20, 21], "why": "candidate makes no progress over turns 20-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 20}}

## Report-tier flags (non-blocking)

- m001 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m001 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m004 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m005 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m010 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m010 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m011 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m011 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
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
- m048 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m048 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
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
- m062 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m062 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m067 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m067 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m070 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m072 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m072 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m075 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m075 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m076 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m076 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m079 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m079 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m081 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m081 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m084 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m085 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m085 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m085 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m087 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m087 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m089 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m089 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m090 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (2 episodes) - known family defect, report only
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

---

**VERDICT: BLOCK**
