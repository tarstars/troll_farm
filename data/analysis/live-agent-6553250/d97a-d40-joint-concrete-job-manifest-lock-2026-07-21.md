# D97a outcome-blind manifest lock

Date: 2026-07-21  
Status: locked before any D97 arm reached terminal state

The frozen D97 generator opened only current states/candidates on official-map seeds
`9,820,000--9,820,015`. It retained the first preregistered root in 240/256 tasks and enumerated
12,483 outcome-blind arms. No arm was continued to a terminal score during generation or this
support audit.

Support clears every pre-value floor:

| Item | Locked result | Required |
|---|---:|---:|
| Eligible roots | 240/256 | >=220 |
| Joint arms | 9,342 | >=5,000 |
| Single arms | 2,901 | >=1,000 |
| Control arms | exactly 1/root | exactly 1/root |
| Roots with fell and renewable alternatives | 240/240 | >=90% |
| Roots with mine | 240/240 | >=50% |
| Minimum roots in an opponent family | 26 | >=24 |
| Seats represented | 122 / 118 roots | both |

Natural, own, and opponent provenance appear in both seats; ambiguous provenance does not occur in
the locked catalogs and is therefore not a missing observed class. All 12,483 arm ids are unique,
all rows have the frozen 48-field schema, and the one-root generator repeat test is deterministic.

Reproducibility anchors:

- protocol SHA-256:
  `157a18d39ba49bf7a7b76080a0f16e8df3c622d93d6f98a22127f779ee5dd0e3`;
- generator SHA-256:
  `f39748d916be4634b9c2e48dc2e0460fbf3d7c56985d4339786b2b39f2276b23`;
- manifest SHA-256:
  `ed5a6ffeb73032006fed7e08518e82c6cf549e2b8f24f7798cbceb82837c157e`.

The manifest is now immutable. Evaluator implementation may validate and execute these arms but
may not add, remove, reorder, or relabel a root, option, action, target, or task from any outcome.
