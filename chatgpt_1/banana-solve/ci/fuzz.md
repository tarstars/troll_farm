# fuzz panel report - 20260802-banana-restoration-r2 owner-directed conservative candidate

- candidate: `../candidate-banana-r2.min.rs` (sha256 2ada1da49e32a8edf1490bebd65c12c6587486f0080b1201254d50c3b5bc47f2)
- parent: `../../../cgauto/submissions/candidate-agent6553250-preseed-orchard-coverage-slim.min.rs` (sha256 a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55)
- seeds: [982451653, 15485863, 32452843, 49979687, 67867967, 86028121]
- maps: 120 (x2 seats = 240 candidate games + 240 parent games), 200 turns each
- wall time: 15.2 s

## Verdict: CLEAR

## Coverage

| metric | value |
|---|---|
| games | 240 |
| banana_activated_games | 161 |
| orchard_eligible_games | 12 |
| orchard_inertness_checks_passed | 12 |
| blocking_games | 0 |
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
- m065 seat 1 [inherited-parent-D1]: candidate D-1 episodes (1) on a map where the parent also fails D-1 (1 episodes) - known family defect, report only
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

**VERDICT: CLEAR**
