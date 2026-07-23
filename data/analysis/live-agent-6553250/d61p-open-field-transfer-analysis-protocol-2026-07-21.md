# D61p open field-transfer analysis protocol (2026-07-21)

## Purpose

Turn one passed, immutable D61p platform snapshot into a reproducible description of the current
resident and current Legend macro policies.  This is an offline analysis step.  It neither
collects platform data nor starts a TestSession, Arena comparison, or submission.

The immediate question is whether the next controller representation should attack renewable
safety, workforce capitalization, funding coordination, worker role allocation, or opponent-crop
compounding.  D62's 2/1,669 zero-crop tail remains a failed local invariant; this report does not
reinterpret field episodes without crops as failures unless renewable feasibility is established.

## Inputs and sealing

- Accept exactly one `data/raw/snapshots/<snapshot-id>` directory produced by
  `data/scripts/collect_snapshot.py` and parsed by `data/scripts/parse_snapshot.py`.
- Require `processed/qa.json` to have `pass=true`, every frozen integrity and volume gate true, and
  `confirmation_content_exposed=false`.
- Verify the immutable snapshot manifest, the processed manifest, the open game table, every open
  trajectory, and every referenced raw replay body by SHA-256 before analysis.
- Select game IDs only from `processed/open/games.jsonl`.  Do not enumerate or read
  `processed/sealed_confirmation`, and do not report confirmation outcomes, trajectories, or
  failures.
- Discovery and validation resident rows are the target evidence.  `calibration_only` rows and
  nonresident `top_legend_observation` rows are descriptive only.  The confirmation split stays
  sealed until a separately frozen candidate exists.

## Exact reconstruction

For every open game, reconstruct official states from frame diffs and the parsed command stream.
Require zero unknown updates, exact turn alignment, exact final inventories, and exact spawned
worker/TRAIN agreement.  Attribute planted crops, harvesting, chopping, and collected material
from official state changes rather than emitted commands.

For every resident and selected top-20 Legend appearance, record:

- successful training turns, specifications, final workforce, and training cost;
- first affordability and delay to each successful TRAIN;
- useful funding contributors to later TRAIN transactions;
- per-worker productive transitions and phase action counts;
- hybrid (`hp>0 && chop>0`) and multi-role (`HARVEST>=3 && CHOP>=3`) labor;
- planting, harvest, wood, score, and late renewable-loop measures;
- for the resident, outcome tail, self crop-creation count, and exact opponent-crop provenance.

Penalty-score games are retained as operational failures but excluded from material-mechanism
contrasts that compare exact competitive scores.

## Frozen attack-angle matrix

The report evaluates these directions without tuning thresholds after seeing the snapshot:

| ID | Attack angle | Support rule |
|---|---|---|
| F1 | Catastrophic-tail control | At least 20 exact resident target games; margin <= -100 in >=10%, >=50% of negative-margin mass, across >=3 opponents |
| F2 | Workforce capitalization | At least 30 top appearances from >=5 agents and 20 resident target games; top minus resident `P(final workers>=3)` >=0.20 |
| F3 | Front-loaded scale | Top median third-worker turn-or-301 <=100 and `P(final workers>=4)` >=0.60 |
| F4 | Coordinated later funding | At least 10 later top TRAIN events; >=50% have >=2 useful funding contributors |
| F5 | Hybrid/multi-role labor | At least 20 trained top workers and 20 active-50 top workers; hybrid rate >=0.50 and multi-role rate >=0.40 |
| F6 | Late renewable loop | At least 30 top appearances; late plant and wood shares each >=0.45, and HARVEST->PLANT and CHOP->DROP each occur in >=60% of games |
| F7 | Opponent-crop compounding | At least 5 catastrophic exact resident target games across >=3 opponents; opponent-crop wood explains >=50% of an opponent final-wood gap of >=20 |
| F8 | Resident zero-crop tail | Descriptive only: report rate, game IDs, outcomes, workforce, and opening stock; never call it an invariant failure without a feasibility label |
| F9 | TRAIN timing delay | Descriptive: compare median delay after first affordability by TRAIN ordinal; no support decision in this snapshot |
| F10 | Worker utilization | Descriptive: compare productive actions and transition mix by worker ordinal; no support decision in this snapshot |

F3--F6 deliberately reuse the already frozen rich-opponent scheduler thresholds.  F9 and F10 are
hypothesis generators, not selection gates.  A direction is `insufficient` when its stated support
floor is absent, rather than silently relaxing that floor.

## Partition and decision rules

- Report resident discovery and validation separately, their union as `resident_target`, and
  calibration rows separately.
- Report current top-20 nonresident observations both jointly and per agent.  Exclude the resident
  from the top comparison even if it is currently in the first twenty Legend rows.
- A sign seen only in discovery is not called replicated.  Validation is reported against the
  frozen metric definitions; no threshold or cohort may be changed after inspection.
- Rank supported directions in the fixed order F1, F7, F2, F4, F3, F5, F6.  This reflects direct
  resident loss first, then causal proximity; it is not fitted to observed effect size.
- The output may authorize a new offline protocol.  It cannot authorize candidate construction,
  confirmation opening, Arena use, or submission.

## Output and invocation

The machine report is written atomically to a new path and includes source/product hashes,
integrity counts, cohort summaries, the complete attack-angle matrix, and the next eligible offline
diagnostic.  Reusing an existing output path is an error.

After explicitly authorized collection and a passed parse/QA stage:

```text
.venv/bin/python cgauto/analyze_d61p_field_snapshot.py \
  data/raw/snapshots/<snapshot-id> \
  --output data/analysis/live-agent-6553250/d61p-field-transfer-<snapshot-id>.json
```

