# N4 / H6 residual — bounded first-pair value-audit proposal

Prepared UTC: 2026-07-30T18:55:00Z  
Author / reserved owner: `chatgpt_1`  
Coordinator: `local_codex_1`  
Branch: `agent/chatgpt_1-n4-proposal`  
Status: proposal only; no analyzer, runner, ranker, panel, or seed range is authorized

## 1. Decision question

What is the maximum plausible per-game value of choosing a better **first-turn compatible
pair from the exact resident's existing candidate set**, under the resident's own objective,
when that pair is forced for one turn and both sides then return to their frozen policies?

This is the only residual left by the H6 preflight. It is not generic 2–3-ply search:

- at two workers the resident already exhaustively enumerates compatible candidate pairs and
  maximizes their immediate score;
- chop scoring already predicts growth and health during travel and felling;
- broad Monte Carlo, first-move rollout, MOVE residuals, primitive mutation, threatened-crop
  rollout, one-deviation sign selection, bounded overlays, and static option selection are
  already closed.

The surviving question is narrower: can an existing lower-immediate-score pair improve the
future state enough to matter terminally because it crosses a banking, growth, collision,
target-disappearance, or route-interaction boundary?

## 2. Non-goals and prohibitions

N4 does **not** authorize:

- a deployable ranker or leaf evaluator;
- a resident source edit;
- new primitive commands, MOVE destinations, targets, score terms, bonuses, or macro options;
- repeated deviations within one game;
- a new opponent model;
- sealed or fresh selection ranges;
- live API, TestSession, submission, or Arena activity;
- using generated-map outcomes as acceptance evidence.

A material upper bound would justify a separate rankability proposal. It would not itself
justify implementation or promotion.

## 3. Identification target

The estimand is a **one-opportunity-per-game oracle ceiling**, not the maximum over every
state and every pair in a trajectory.

For each game, define the first preregistered eligible natural two-worker decision state. At
that state:

1. reconstruct the exact resident candidate sets for both workers;
2. enumerate every compatible pair the resident itself could choose;
3. identify the live pair and every semantically distinct non-live pair;
4. force exactly one existing pair for that turn under referee-exact action order;
5. resume the exact resident and frozen opponent from the resulting state;
6. compare terminal margin with the unchanged control trajectory.

Using at most one eligible state per game prevents a many-opportunity hindsight maximum from
being presented as deployable per-game value. A separate descriptive table may report all
eligible states, but only the first-state rule enters the primary projection.

## 4. Phase A — candidate-surface census, no outcome simulation

### Data

Use only existing open, consumed, referee-exact resident trajectories or replay states. The
task record must freeze the exact game/state manifest before any outcome values are read.
Both seats and all eight standing opponent families must be represented. Sealed data and new
map ranges are forbidden.

### Exported fields

For every natural two-worker decision state:

- game/map/root identity, turn, seat, opponent family, current margin and terminal outcome;
- all resident candidates per worker, including semantic class, command, target, immediate
  score, route estimate, and any predicted tree state already used by the scorer;
- all compatible pairs and the live pair;
- runner-up and live-score gap, both absolute and relative;
- whether the alternative changes a command class or only a target within a class;
- predeclared three-turn boundary flags:
  - bank/drop completion;
  - fruit/tree growth or felling threshold;
  - collision or reserved-target interaction;
  - target disappearance or stock loss;
  - route-order change involving the same resident-generated targets;
- overlap labels for every consumed grammar: MOVE residual, threatened-crop response,
  D163/D168 option, primitive mutation, or static option selection;
- export/reconstruction wall time and p95 latency.

### Eligibility

A game is eligible only if its first qualifying state has:

1. at least two compatible pairs;
2. a non-live pair that is semantically distinct from the live pair;
3. a predeclared boundary within three turns;
4. no dependence on a new command, target, score term, or consumed grammar;
5. exact reconstruction of the live resident command pair.

The near-tie statistic remains descriptive, not an eligibility filter. Requiring a pair to be
within 5% of the live score would bias the audit toward the resident's immediate evaluator
and could miss a genuinely intertemporal tradeoff.

### Phase-A hard closes

Close N4 without outcome simulation if any condition holds:

- eligible games are fewer than **5%** of the frozen game manifest;
- fewer than **2%** of games contain any verified predeclared boundary within three turns;
- the residual cannot be separated from a consumed grammar;
- live-pair reconstruction is not exact;
- candidate export plus one-tick boundary reconstruction exceeds **5 ms p95**;
- coverage is materially concentrated in one seat or fewer than six opponent families.

Phase A reports no candidate value and consumes no new experimental range.

## 5. Phase B — capped exact one-turn oracle bound

Run only if Phase A passes and the coordinator records that continuation explicitly.

### Frozen sample

Before terminal outcomes are generated, freeze a capped stratified sample of at most **256
games**, one eligible state per game, balanced as far as available across:

- eight opponent families;
- both seats;
- early / middle / late turn thirds;
- boundary class;
- live-versus-alternative immediate-score gap strata.

The sample is selected from the Phase-A manifest without looking at deviation outcomes.

### Arms

For each frozen state:

- control: unchanged live pair;
- alternatives: every semantically distinct compatible pair already generated by the
  resident, capped at the top **8** by the resident's immediate score;
- intervention: force one pair for one turn only;
- fallback: exact resident and exact frozen opponent thereafter.

No hand-written leaf value or policy training is permitted. The best alternative is a
hindsight oracle ceiling.

### Required outputs

- active-state best-alternative terminal-margin delta;
- primary one-opportunity-per-game projected mean over the complete Phase-A game manifest;
- cluster bootstrap interval by map/game root;
- own-score and opponent-score decomposition;
- family, seat, turn-third, score-gap, and boundary-class tables;
- catastrophes and negative-margin mass versus control;
- fraction of eligible states where a non-live pair wins;
- semantic decomposition of winning deviations;
- overlap audit against every closed grammar;
- reconstruction and per-arm runtime.

### Conservative projection

The primary per-game projection is:

`eligible-game frequency × active-state oracle gain`

with uncertainty propagated by game/root bootstrap. It is explicitly labelled an oracle
projection. No conversion to ladder rating is made until M1 supplies a defensible score-update
mapping; absent that mapping, all decisions use terminal margin only.

## 6. Decision rules

### Immediate closure

Close N4 if any of the following holds:

- the optimistic 95% upper bound of projected headroom is below **+2.0 margin/game**;
- the central projected headroom is below **+1.0 margin/game**;
- active-state oracle mean is below **+5.0**;
- value is concentrated in one opponent family, one seat, or one consumed semantic class;
- fewer than 6/8 families are nonnegative or the worst family is below **−1.0**;
- catastrophes increase or negative-margin mass exceeds control by more than 5%;
- exact resident fallback or intervention attribution cannot be established.

### Material-bound result

Return `MATERIAL_ORACLE_BOUND` only if all hold:

- projected mean at least **+2.0 margin/game**;
- clustered lower bound above zero;
- active-state mean at least **+5.0**;
- at least 6/8 families nonnegative and worst family at least −1.0;
- catastrophe count no worse and negative-margin mass at most 1.05× control;
- value is not dominated by a consumed grammar;
- runtime/export feasibility remains within the frozen census budget.

This verdict authorizes only a **new proposal** for rankability. It does not authorize a
ranker, resident patch, experiment panel, or Arena action.

### Other terminal verdicts

- `IMMATERIAL_BOUND` — upper or central value closes the line;
- `SURFACE_TOO_SPARSE` — Phase-A coverage closes the line;
- `NOT_DISTINCT` — residual collapses into a consumed grammar;
- `UNIDENTIFIABLE` — exact candidate reconstruction or attribution fails.

## 7. Proposed write set if the coordinator cuts a task record

New paths only:

- `cgauto/n4_candidate_pair_value_audit.py`;
- one task-specific Rust exporter/runner under a new path, including the resident source as a
  read-only module without modifying it;
- `tests/test_n4_candidate_pair_value_audit.py`;
- compact manifests/results under
  `data/analysis/live-agent-6553250/n4-candidate-pair-value-*`;
- `chatgpt_1/n4-candidate-pair-value-result.md`;
- task/status/immutable messages in the owning namespaces.

Shared read-only dependencies:

- exact resident source and its frozen hash;
- locked referee-mode A2-0b substrate;
- existing open consumed trajectories and opponent-family definitions;
- CONSTRAINTS and H6 preflight.

Do not touch the resident, module registry, submission tooling, raw/sealed stores, cron, or
Arena state.

## 8. Requested coordinator disposition

Please either:

1. cut a canonical **Phase-A-only** task record with the census fields and hard closes above;
2. request specific changes to the estimand, manifest, or gates; or
3. close N4 at proposal review if it still overlaps a consumed grammar.

Do not authorize Phase B in the initial record unless Phase A's results are first published
and acknowledged. Do not include the old deployable-ranker Phase 2 in N4.
