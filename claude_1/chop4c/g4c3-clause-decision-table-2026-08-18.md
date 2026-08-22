# OSC-031 chop clause-decision table (G-4c.3)

Population: the owner-pinned manifest `osc031-167-manifest.json`, sha256 `b9eed4c2d66401761845bcb223893cc91a82171806cc43fd1ce4175bae1f21e5` — 167 turns, unit 0. Instrument frozen at G-4c.1; parity IDENTICAL.

**Attributions and measurements only.** Whether the named clause is a defect or correct caution is the OWNER's ruling; nothing here anticipates it.

## Terminal clause per tree evaluation

| clause | evaluations |
|---|---:|
| `GATE_UNIT` | 0 |
| `DEAD_OR_UNREACHABLE` | 0 |
| `PREDICT_TREE_NONE` | 315 |
| `PREDICTED_NONPOSITIVE` | 0 |
| `CHOP_OUTCOME_NONE` | 0 |
| `ROUND_TRIP_CLOCK` | 0 |
| `WOOD_NONPOSITIVE` | 0 |
| `ACCEPT` | 0 |
| **total** | **315** |

- 167 pinned turns carry 315 tree evaluations: the chop planner is invoked more than once per unit-turn.
- Turns whose evaluations do not share a single terminal clause: **0**.
- Pinned turns with no chop evaluation: **0**.
- Turns observed outside the manifest, reported not dropped: **31** (1, 2, 3, 4, 5, 6, 7, 10, 18, 26, 34, 42, 50, 58, 66, 74, 82, 90, 98, 106, 114, 122, 130, 138, 146, 154, 162, 170, 178, 186, 194).

## Boundaries

One game. No fix, no judgment, no class-wide claim, no Arena action; the resident and dev copy are untouched. The five clauses showing zero here were dispositioned under G-4c.2: `DEAD_OR_UNREACHABLE` and `ROUND_TRIP_CLOCK` observed firing on purpose-built states, `PREDICTED_NONPOSITIVE` / `CHOP_OUTCOME_NONE` / `WOOD_NONPOSITIVE` proven unreachable over the exhaustive legal domain.
