# chatgpt_1 — next-session backlog

Prepared UTC: 2026-07-29T14:43:00Z
Canonical shared backlog: iteration 2 at `docs/BACKLOG.md`
Latest shared head inspected: `cfa08493c176bc73b82d2ea74c1d80299a39a67e`
Integrator: `claude_1`
Agent branch: `agent/chatgpt_1`

## Session objective

Complete the highest-decision-value available read-only task under the canonical
iteration-2 backlog. The primary task is **N1 maturity-curve measurement**. It re-baselines
the actual code gap and therefore determines the value and timing of every later code
experiment. D176a review and N4/H6 follow only according to the dependency rules below.

Work one substantive item at a time. No Arena, TestSession, sealed-data, resident-source,
`api_submit.py`, cron, raw-replay-store, or integrator-owned shared-state mutation.

## 0. Mandatory bootstrap and coordination

Before analysis or writing:

1. Fetch all refs and record the exact heads of `session-2026-07-01`, `main`, and the
   current agent branch.
2. Read, in order: `docs/STATE.md`, relevant `docs/CONSTRAINTS.md`, the iteration-2 head of
   `docs/BACKLOG.md`, the ledger tail, and all messages addressed to `chatgpt_1`.
3. Acknowledge the iteration-2 backlog message.
4. Confirm whether N1 is still unclaimed. If available, renew the N1 claim and wait for the
   canonical task record before touching task-specific paths.
5. Inspect D176a status without reading or interpreting partial outcomes.
6. Reconcile branch history only under the coordination protocol. Prior work is integrated,
   but refs may diverge because of merge history. Never force-reset or discard commits;
   request a rollover branch from the integrator if needed.
7. Name explicit paths in every commit; never `git add -A` or `git add -u`.

Bootstrap output: a status message naming the exact shared head, current experiment,
claimed task, write set, and blockers.

## 1. P0 primary — N1 maturity-curve measurement

### Why first

H13 reduced the plausible code-attributable portion of the 2.94-point resident-to-yamo
gap to at most roughly one point, while prior evidence says fresh submissions can trail
mature ones by 3–4 points. If that maturity effect holds, the true code gap to the 28.22
bar may be roughly 2.5–3.5 rather than 6.46. That changes experiment sizing, submission
timing, and whether marginal candidates are worth any churn.

### Outcome

Estimate, with explicit uncertainty:

- the score trajectory after submission;
- whether score converges, plateaus, or changes only at discrete recomputations;
- the resident’s expected mature score if left untouched;
- the true remaining gap to the rank-3 bar under maturity scenarios;
- whether battle count, elapsed time, or pool recomposition best explains observed change;
- the strategic implication for H9 submission timing and minimum candidate value.

### Data scope

Read-only existing data only:

- the six recorded ladder snapshots from 2026-07-21 through 2026-07-29;
- the 8,131+ collected public-game corpus and its immutable snapshot metadata;
- submission/agent identifiers and timestamps already stored in snapshots or replay
  metadata;
- previously recorded same-code A/A and fresh-vs-mature examples as validation cases.

No live API request, battle generation, submission, or fresh collection.

### Identity and cohort rules

A maturity curve is meaningful only when code identity is stable. The analysis must:

1. Build a panel keyed by player, agent ID, submission ID/source identity where available,
   snapshot timestamp, score, rank, battle count, and league size.
2. Separate stable-agent intervals from intervals containing a new submission or uncertain
   identity.
3. Exclude or explicitly flag agents that may have changed code under the same public name.
4. Keep contest-final rankings separate from the July practice ladder.
5. Treat leaderboard score, battle outcomes, and rank as distinct measurements.
6. Use exactly one timestamped snapshot for each stated current rank/score claim.

### Analysis plan

#### A. Coverage and identifiability audit

Report first, before fitting:

- number of snapshots, unique players, stable agents/submissions, repeated observations;
- age coverage since submission;
- battle-count coverage;
- missing timestamp and identity rates;
- number of observed score changes versus frozen-score intervals;
- whether enough within-agent repeated data exists to separate maturity from pool drift.

If stable identity or age coverage is insufficient, the correct verdict is
**UNIDENTIFIABLE FROM CURRENT DATA**, not a fitted 3–4-point claim.

#### B. Descriptive event curves

For stable agents:

- score versus elapsed hours/days since submission;
- score versus battle count;
- rank and league-size changes by snapshot;
- intervals with score frozen while rank moves;
- recomputation-event detection where score changes discretely;
- resident and yamo shown separately from pooled field curves.

#### C. Controlled models

Use several predeclared specifications rather than one preferred curve:

1. Within-agent fixed-effects model with snapshot fixed effects for pool-wide movement.
2. Battle-count model with flexible age bins.
3. Age model with battle-count controls.
4. Event-study around identifiable submission/recomputation events.
5. Robust sensitivity restricted to agents with the strongest submission identity.

Cluster uncertainty by agent. Use bootstrap or robust intervals appropriate to the small
number of snapshots; do not present ordinary row-level standard errors as independent.
Avoid high-order curve fitting and threshold tuning.

#### D. Resident mature-score projection

Project only over empirically supported ages/battle counts. Report:

- central estimate and interval;
- pessimistic, central, and optimistic maturity scenarios;
- expected remaining gap to 28.22 under each scenario;
- time/battle range where the curve plateaus, if supported;
- how much of the 2.94 resident-to-yamo gap remains unexplained after maturity adjustment.

Do not extrapolate past observed support without a clearly labeled scenario.

### Validation

- Reproduce the documented fresh same-code A/A cases directionally.
- Confirm that the model distinguishes score freeze from passive rank drift.
- Run leave-one-agent-out sensitivity so a single high-profile agent cannot define the
  curve.
- Check whether estimates reverse when controlling for snapshot/pool composition.
- Report raw rows or a reproducible compact panel manifest.

### Decision rules

Possible verdicts:

- **MATURITY MATERIAL:** credible resident uplift at least +2 rating points; submission
  timing becomes strategic and downstream candidate floors must include churn recovery.
- **MATURITY MODEST:** credible uplift between +0.5 and +2; re-baseline the gap but code
  remains primary.
- **MATURITY IMMATERIAL:** credible uplift below +0.5; retire the 3–4-point assumption.
- **UNIDENTIFIABLE:** current snapshots cannot separate maturity, pool drift, and code
  identity; specify the cheapest additional passive measurement required.

Thresholds are classification aids to be frozen in the task record, not tuned after fits.

### Deliverables

Expected task-specific deliverables, subject to the integrator’s write set:

- one analyzer under a new `cgauto/` path;
- compact derived panel/manifest outside raw stores;
- `chatgpt_1/<date>-n1-maturity-curve-review.md` or integrator-designated report path;
- plots/tables referenced from the report where useful;
- immutable handoff with the mature-score estimate, true code-gap range, and H9 consequence.

### Stop rule

Once N1 is handed off, do not proceed to a submission-timing experiment. H9 remains owner-
authorized and must run only within `docs/PROMOTION-RUNBOOK.md`.

## 2. P0 secondary — D176a independent integration review

### Entry condition

Run after D176a has a final result and only if N1 is complete, blocked, or explicitly
parallelized by the integrator. Never inspect partial result artifacts.

### Review checklist

Integrity:

- protocol frozen before outcome;
- seeds `9,857,000–9,857,127`, 2,048 paired episodes;
- trigger fidelity at least 90%; jobs1/jobs20 identity;
- inactive episodes byte-exact; dev copy restored at SHA prefix `fff6669b`;
- no sealed/Arena/TestSession/raw-store mutation.

Mechanism:

- at-least-10-turn oscillation rate at most 6.0%;
- worst run at most 20 turns;
- 5–9-turn displacement increase at most 10%;
- de-novo long runs at most 1%;
- no waste detector worse by more than 10%.

Value:

- overall mean at least 0 with clustered lower bound at least −0.5;
- activated mean at least +0.5;
- worst family at least −1;
- catastrophes and negative-margin mass within frozen limits.

Disposition:

- ACCEPT QUALIFIED, ACCEPT CLOSED-AT-MECHANISM, ACCEPT CLOSED-AT-VALUE, or CORRECT/REJECT.
- A qualified roughly +0.1 candidate is a possible ride-along, not a dedicated Arena trial.
- Any closure ends the oscillation line permanently; no tuning or third design.

Deliverable: a compact independent review and handoff; no candidate build or source edit.

## 3. P1 — N4/H6 residual as a value audit

### Entry condition

Start only after N1, unless the integrator explicitly parallelizes it. Submit a revised
proposal first; do not implement a ranker.

### Question

What is the maximum plausible per-game value of choosing a better first-turn pair from
the resident’s existing compatible candidate pairs, under the resident’s own objective?

### Cheap bound proposal

Phase A — candidate-surface census:

- existing decoded resident games only;
- exact resident candidates at natural two-worker decision states;
- feasible-pair count, live/runner-up gap, target classes, turn, seat, opponent, current
  margin, target disappearance/banking/near-term invalidation boundaries;
- coverage by game/family/seat/outcome stratum;
- reconstruction and export latency.

Phase B — small oracle-value sample only if Phase A is material:

- freeze a capped stratified state sample before outcomes;
- force one already-generated compatible pair for one turn, then exact-resident fallback;
- evaluate terminal margin for live and existing alternative pairs;
- hindsight best is an oracle ceiling only; no selector fitting;
- project per-game headroom from active gain × independently measured frequency;
- report own/opponent score, family/seat breadth, catastrophes, and negative mass.

Distinctness: exact live candidate vocabulary, one-turn intervention, exact fallback,
intertemporal misranking only. No MOVE residual, new option library, overlay, command
mutation, or generic rollout.

Proposed early close conditions for integrator review:

- eligible boundary in fewer than 5% of games;
- optimistic projected headroom below +1 margin/game;
- active oracle mean below +5 or concentrated in one family/seat;
- optimistic 95% upper bound below +2 overall;
- reconstruction/export above 5 ms p95 before rollout cost;
- inability to separate the experiment from a consumed grammar.

Deliverable: bounded-audit proposal requesting a canonical record or explicit closure.
Execute only the approved audit phase if a record is issued.

## 4. Conditional fallback — N2 verification sweep

Use only when N1 is blocked and D176a/N4 are unavailable.

Re-verify or retire the remaining B4.4 cohort claims, especially planting tempo and wood
concentration. Preserve method definitions, control for roster/opponent/seat/duration, and
separate contest-final statements from July practice behavior. Do not cite B4.4 in new
protocols until this sweep reports.

## 5. Deferred beyond the next session

- N3 renewable-base feasibility: high decision value, but start after N1 unless separately
  assigned; it gates Architecture-2.
- N5 endgame opponent-plant contest and N6 denial weight: bounded experiments, not tuning.
- N7 dead-accretion removal: needs identity proof and a byte-sacred-source protocol.
- H2 Architecture-2: owner-gated and blocked on N1 + N3.
- H10 whole-policy/spatial learning: owner decision, larger programme.
- H9 submission timing: strategic after N1, still owner-authorized only.

## 6. Explicit exclusions

- Generic rollout/search work.
- D176a retuning or a third oscillation design.
- Four-lever resident economy patch.
- Fruit-priority tuning, worker-two timing, no-loop quartet reruns, body blocking,
  unconditional opponent-crop scoring, or opponent-family-as-map inference.
- Arena writes, candidate promotion, resubmission, TestSession, or `api_submit.py` changes.
- Force-resetting or deleting branch history.

## 7. End-of-session completion checklist

1. Write a dated worklog with exact refs, commands, data provenance, and uncertainty.
2. Commit only explicit owned paths.
3. Push the agent branch.
4. Send one immutable handoff to `claude_1`, CC peers/user where relevant.
5. Update `coordination/status/chatgpt_1.md`.
6. Release completed tasks and label blockers precisely.
7. Verify the remote commit and report pushed-versus-integrated status.
