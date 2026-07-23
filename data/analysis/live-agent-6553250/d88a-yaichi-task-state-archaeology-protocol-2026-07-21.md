# D88a yaichi task-state archaeology — frozen protocol (2026-07-21)

## Question

D87 proves that a local `HARVEST -> existing regeneration commitment` patch is not a renewable
controller: it creates 273 crops and zero additional own-crop harvests. Public yaichi replays,
however, expose a per-unit task state in an issued `MSG` command on almost every turn. Can those
messages and exact replay state reconstruct a stable, implementation-ready controller grammar
that explains the strong two-worker renewable lifecycle on held-out games?

D88 is observational. It may authorize a controller-level D89 research implementation, but it
cannot authorize a TestSession, submission, resident replacement, Arena write, or access to any
sealed replay/map block.

## Evidence boundary and split

Use the same exact 35 open yaichi games and state decoder audited in D86. Before this protocol,
only the first 30 message rows were manually sampled in the following nine historical games:

`893174122, 893407296, 893412043, 893876322, 894397581, 895446276, 895925001,
895926495, 895927312`.

All ten current D61p yaichi games are also consumed descriptive evidence:

`896491202, 896492419, 896493461, 896493721, 896494122, 896494214, 896494703,
896495136, 896495350, 896495475`.

These 19 games are discovery. Hold out the complete message streams of the remaining 16 historical
games until parser, state normalization, lineage rules, transition summaries, and gates are coded:

`895446639, 895447009, 895447026, 895447237, 895883032, 895883103, 895883400,
895883571, 895924585, 895926546, 895926772, 895927134, 895927164, 895927169,
895927226, 895927242`.

Their D86 renewable labels and terminal outcomes are already consumed, but their task-state
sequences are not. The validation block has 12 renewable and four nonrenewable games, includes
both seats, and spans two public opponents. No threshold may be changed after its messages are
opened.

## Frozen parser and task vocabulary

For yaichi's player command string, find the `MSG ` payload, split unit segments only on literal
` | `, and parse each segment as `<unit_id>:<state text>`. Preserve the complete raw text. Normalize
only these states, in this order:

1. exact leading token `MINE`, `HARVEST`, `DROP`, `DO_CHOP`, or `PLANT`;
2. prefix `PICK_SHACK` -> `PICK_SHACK`;
3. prefix `GO_PLANT` -> `GO_PLANT`;
4. prefix `RETURN` -> `RETURN`;
5. prefix `CHOP` -> `CHOP_TRAVEL`;
6. prefix `H(` -> `HARVEST_TRAVEL`;
7. prefix `M(` -> `MINE_TRAVEL`;
8. everything else -> `UNKNOWN`, retained verbatim.

Do not add a validation-only alias. Extract coordinate pairs descriptively, but do not use them to
alter normalization or gates.

Map states to issued unit commands with these frozen allowed sets:

| State | Allowed issued command |
|---|---|
| `MINE` | `MINE` |
| `HARVEST` | `HARVEST` |
| `DROP` | `DROP` |
| `DO_CHOP` | `CHOP` |
| `PLANT` | `PLANT` |
| `PICK_SHACK` | `MOVE`, `PICK`, `WAIT` |
| `GO_PLANT` | `MOVE`, `PLANT`, `WAIT` |
| `RETURN` | `MOVE`, `DROP`, `WAIT` |
| `CHOP_TRAVEL` | `MOVE`, `CHOP`, `WAIT` |
| `HARVEST_TRAVEL` | `MOVE`, `HARVEST`, `WAIT` |
| `MINE_TRAVEL` | `MOVE`, `MINE`, `WAIT` |

`TRAIN` and `MSG` are global and excluded from per-unit conformance. A living unit without an
assigned action is `WAIT`. Do not reinterpret a mismatch from observed outcomes.

## Frozen exact lineage reconstruction

Replay every turn from decoded before/after states and assigned commands for both players.

- Every initial plant is `natural`.
- A successful PLANT is owned by the issuing player until that plant disappears. Record planter,
  turn, species, source token, harvest count, and whether each player later chops it.
- For each unit/species, maintain acquisition-ordered cargo provenance. Initial cargo is
  `initial`; successful PICK is `bank`; successful HARVEST inherits `natural`, `own_crop`, or
  `opponent_crop` from the plant under the unit. DROP and PLANT consume tokens FIFO, exactly as in
  D86. Record every underflow.
- A successful own-crop replant is a successful PLANT consuming `own_crop` provenance. A bank
  bootstrap plant consumes `bank`; a direct natural conversion consumes `natural`.
- A token is `banked` only when a successful DROP consumes it. It is not enough for a RETURN task
  to be visible.
- Worker ordinal is spawn order. Ordinal zero is the starter; ordinal one is the trained worker.

Record task-state counts/transitions by worker ordinal, successful action counts, first bank plant,
first own-crop harvest/replant, plant-source mix, harvest-destination mix, crop lifetime/outcome,
and target coordinates. Retain per-game rows so every aggregate is auditable.

## Frozen integrity gates

All must pass independently on discovery and validation:

1. every game has exact decoded turn count, exact terminal scores, no unknown diff updates, and no
   provenance underflow;
2. at least 98% of yaichi turns contain a parseable MSG payload;
3. at least 98% of living yaichi unit-turns have exactly one parsed task segment and no segment
   names a nonexistent/opponent unit;
4. at least 98% of parsed segments normalize to the frozen vocabulary;
5. at least 95% of known-state unit-turns conform to the frozen state/command table; and
6. all successful yaichi PLANT and HARVEST actions receive exact species and plant-lineage labels.

An integrity failure permits only a mechanical parser/accounting repair that does not add or
change a state alias or behavioral threshold.

## Frozen mechanism-transfer gates

Evaluate these only after integrity passes. A renewable game is the unchanged D86 strict label:
the starter successfully replants at least three harvested fruits by turn 100 and both harvests
and plants.

On the 12-game held-out renewable block require all:

1. at least 10/12 games show a successful bank-sourced starter PLANT before the first successful
   own-crop-sourced starter PLANT (`bank bootstrap before maintenance`);
2. at least 80% of the starter's successfully planted fruits are sourced from `bank` or
   `own_crop`, not direct `natural`/`opponent_crop` conversion;
3. at least 80% of successfully harvested own-crop fruit tokens are replanted by the same worker
   before they are dropped or remain in terminal cargo;
4. at least 95% of the trained worker's successful productive actions are CHOP or DROP, and no
   more than one held-out renewable game has a trained-worker successful HARVEST or PLANT;
5. at least 10/12 games contain the ordered controller phases `bank acquisition -> bank-sourced
   PLANT -> own-crop HARVEST -> own-crop-sourced PLANT`; movement may occur between phases; and
6. all four rates above retain the same qualitative direction in consumed current renewable
   games; current evidence is descriptive and cannot rescue a held-out failure.

Report, but do not gate, crop protection, own/opponent chop rates, crop age at first harvest/chop,
state-transition matrices, target reuse, task duration, nonrenewable-game differences, and outcome
correlations. These determine D89 implementation details only after the transfer gates pass.

## Decision rule

- **All integrity and mechanism gates pass:** write a complete controller blueprint and open D89,
  a disabled-by-default task-state proxy in the local research harness. Freeze D89 before running
  any new official map.
- **Integrity failure:** mechanically repair and rerun without reading value implications.
- **One mechanism gate narrowly misses while its confidence interval overlaps the threshold:**
  report `inconclusive`; collect no new platform data and prefer a descriptive controller skeleton,
  not a candidate.
- **Clear mechanism failure:** close literal yaichi task imitation. Preserve the telemetry as
  behavior-cloning/PPO supervision, but return candidate search to an independently valued macro
  action representation.

Do not tune these gates on the held-out streams. D88 evaluates mechanism identifiability, not Arena
strength; even a pass does not make a submission candidate.
