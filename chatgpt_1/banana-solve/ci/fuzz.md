# fuzz panel report - 20260802-banana-restoration-r2 owner-directed renewable candidate

- candidate: `../candidate-banana-r2.min.rs` (sha256 dfbf0331866d9631c61348143ab460e026badbcd1d5d1288ffa0dbae40186cd6)
- parent: `../../../cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 15.3 s

## Verdict: BLOCK

## Coverage

| metric | value |
|---|---|
| games | 240 |
| banana_activated_games | 161 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 12 |
| blocking_games | 9 |
| flagged_games | 110 |

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

### m025 seat 1 (orchard_eligible, chopper_aggressor, seed 15485863)

- **P1**: {"count": 3, "detector": "D-8", "episodes": [{"cell": [12, 6], "completion_turn": 7, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10005, "reason": "discretionary_owned", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [12, 6], "completion_turn": 7, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10005, "reason": "discretionary_owned", "turn_end": 6, "turn_start": 6, "unit": 0}, {

### m032 seat 1 (forest_sparse, chopper_aggressor, seed 32452843)

- **P4**: {"detail": {"parent_progress_turns": [22, 23, 26, 27, 28, 29, 35, 36], "why": "candidate makes no progress over turns 22-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 22}}

### m035 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"parent_progress_turns": [17], "why": "candidate makes no progress over turns 17-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 17}}

### m036 seat 1 (multi_door, harvester, seed 982451653)

- **P1**: {"count": 10, "detector": "D-6", "episodes": [{"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 69, "turn_start": 68, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 70, "turn_start": 69, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 98, "turn_start": 97, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 99, "turn_start": 98, "unit": null}, {"cell": [11, 7], "kind": "opp_harvested_ours", "opp_unit": 5, "turn_end": 127, "turn_start": 126, "unit":

### m042 seat 1 (water_diagonal, chopper_aggressor, seed 982451653)

- **P1**: {"count": 1, "detector": "D-1", "episodes": [{"cells": [[11, 0], [11, 1]], "k": 13, "turn_end": 54, "turn_start": 28, "unit": 2}]}

### m049 seat 0 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 3, "detector": "D-8", "episodes": [{"cell": [0, 7], "completion_turn": 7, "eta_opp_at_chop_start": 11, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 27, "reason": "discretionary_owned", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [0, 7], "completion_turn": 7, "eta_opp_at_chop_start": 11, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 27, "reason": "discretionary_owned", "turn_end": 6, "turn_start": 6, "unit": 0}, {"cell": [0, 7]

### m049 seat 1 (water_diagonal, harvester, seed 15485863)

- **P1**: {"count": 3, "detector": "D-8", "episodes": [{"cell": [10, 1], "completion_turn": 7, "eta_opp_at_chop_start": 11, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 27, "reason": "discretionary_owned", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [10, 1], "completion_turn": 7, "eta_opp_at_chop_start": 11, "exact_chop_turns": 3, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 27, "reason": "discretionary_owned", "turn_end": 6, "turn_start": 6, "unit": 0}, {"cell": [10,

### m065 seat 1 (orchard_eligible, chopper_aggressor, seed 86028121)

- **P4**: {"detail": {"parent_progress_turns": [27, 28, 31, 32], "why": "candidate makes no progress over turns 26-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 26}}

### m082 seat 0 (water_diagonal, chopper_aggressor, seed 67867967)

- **P1**: {"count": 4, "detector": "D-8", "episodes": [{"cell": [0, 5], "completion_turn": 8, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 4, "flip_turn": null, "health_decreased": true, "kind": "diag_mother_chop", "opponent_harvest_turn": 10005, "reason": "discretionary_owned", "turn_end": 5, "turn_start": 5, "unit": 0}, {"cell": [0, 5], "completion_turn": 8, "eta_opp_at_chop_start": 10000, "exact_chop_turns": 4, "flip_turn": null, "health_decreased": false, "kind": "diag_mother_chop", "opponent_harvest_turn": 10005, "reason": "discretionary_owned", "turn_end": 6, "turn_start": 6, "unit": 0}, {"
- **P4**: {"detail": {"parent_progress_turns": [13, 14], "why": "candidate makes no progress over turns 11-199 (>= 60 turns) while the parent progresses in the same window on the identical map (not an inherited WAIT-equilibrium)", "window_end": 199, "window_start": 11}}

## Report-tier flags (non-blocking)

- m001 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m001 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m003 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m003 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m004 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m005 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m010 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m010 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m011 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m011 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m012 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m012 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m012 seat 1 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m014 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m016 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m016 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m020 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m020 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m021 seat 1 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m022 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m024 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m024 seat 1 [terminal-consuming-command]: 1 D-7 unbanked_at_end episode(s) have a final PLANT BANANA or DROP command whose S_(T+1) effect is outside the finite panel transcript
- m029 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m029 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m033 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m033 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m034 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m034 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m037 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m037 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m038 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m038 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m038 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m038 seat 1 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m039 seat 1 [inherited-parent-D1]: candidate D-1 episodes (2) on a map where the parent also fails D-1 (2 episodes) - known family defect, report only
- m043 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m043 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m044 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m044 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m046 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m048 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m048 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
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
- m061 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m062 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m062 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m064 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m066 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m066 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m067 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m067 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m068 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m068 seat 1 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m070 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m070 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m070 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m071 seat 1 [terminal-consuming-command]: 1 D-7 unbanked_at_end episode(s) have a final PLANT BANANA or DROP command whose S_(T+1) effect is outside the finite panel transcript
- m072 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m072 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m073 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m075 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m075 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m075 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m076 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m076 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m078 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m079 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m079 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m081 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m081 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m084 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m085 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m085 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m085 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m087 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m087 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m088 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m089 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m089 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m090 seat 0 [inherited-parent-D1]: candidate D-1 episodes (2) on a map where the parent also fails D-1 (2 episodes) - known family defect, report only
- m090 seat 0 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m091 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m091 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m092 seat 0 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m093 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m093 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m095 seat 0 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m095 seat 1 [inherited-parent-D9]: 4 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m095 seat 1 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
- m096 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m096 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m099 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m101 seat 0 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m101 seat 1 [inherited-parent-D9]: 2 D-9 episode(s) reproduced identically by the parent on the identical map/opponent - inherited funding-phase behavior (I-18 byte-equal default), report only (ROOT-A panel-layer gate, round-6 ruling 2026-08-06)
- m104 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
- m106 seat 1 [byte-identical-parent-property]: 1 property violation(s) occurred on a complete candidate command stream byte-identical to the stable parent; inherited behavior is report-tier, not banana-attributable
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
