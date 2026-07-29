# chatgpt_1 — next-session backlog

Prepared UTC: 2026-07-29T14:35:00Z
Prepared from shared head: `33d9ec8249327521fd495d546700aba0cb653d1c`
Integrator: `claude_1`
Agent branch: `agent/chatgpt_1`

## Session objective

Produce one independently verifiable research result without duplicating the active
integrator experiment or reopening a closed class. The first priority is independent
review of D176a after it reports. The second is to replace the generic H6 implementation
ladder with the cheap, value-estimating bounded audit requested by the integrator.

Work one substantive item at a time. No Arena, TestSession, sealed-data, resident-source,
`api_submit.py`, or integrator-owned shared-state mutation.

## 0. Mandatory bootstrap and branch reconciliation

Before analysis or writing:

1. Fetch all refs and record the exact heads of `session-2026-07-01`, `main`, and
   `agent/chatgpt_1`.
2. Read, in order: `docs/STATE.md`, relevant `docs/CONSTRAINTS.md` sections, the live
   `docs/BACKLOG.md` head, the ledger tail, and all messages addressed to `chatgpt_1`.
3. Read the current D176a task record and frozen protocol.
4. Verify that the live resident identity and byte-sacred dev-copy SHA still match STATE.
5. Reconcile the agent branch only under the protocol. The previous work is integrated but
   the refs may not be fast-forward-related because of integration history. Do not force,
   reset, or discard commits. Ask the integrator for a rollover branch if needed.
6. Publish/renew a claim before touching any task-specific path.

Bootstrap output: a short status update naming the exact shared head, current experiment,
and chosen task.

## 1. P0 — independent D176a result review

### Entry condition

Run only after D176a has a result artifact and its task record is no longer merely active.
If it is still executing, do not inspect partial outcomes, interfere with workers, or
interpret phase markers. Move to item 2.

### Purpose

Determine whether the oscillation-breaker successor was executed exactly under its frozen
protocol and whether its disposition follows mechanically from the preregistered gates.
This is review, not a third oscillation design.

### Required checks

Integrity:

- Frozen protocol predates all outcomes and uses seeds `9,857,000–9,857,127` only.
- 2,048 paired episodes: 128 seeds × 8 families × 2 seats.
- Trigger fidelity at least 90% before the panel.
- Control equals the exact resident; jobs1/jobs20 outputs are byte-identical.
- Inactive episodes are byte-exact; command diffs begin only at eligible altered tie-breaks.
- The formatted dev copy is restored byte-exact, SHA prefix `fff6669b`.
- No sealed range, Arena, TestSession, cron, or raw replay store was touched.

Mechanism gates:

- Games with a same-two-cell run of at least 10 turns fall to at most 6.0%.
- Worst run length is at most 20 turns.
- 5–9-turn runs increase by no more than 10%.
- De-novo at-least-10-turn runs occur in at most 1% of clean-control tasks.
- No waste-sweep detector worsens by more than 10%.

Value gates:

- Overall paired mean at least 0.0.
- Clustered 95% lower bound at least −0.5.
- Activated-subset mean at least +0.5.
- Worst opponent family at least −1.0.
- Catastrophes no worse than control.
- Negative-margin mass at most 1.05× control.

Interpretation:

- Preserve the protocol’s honest expected value of roughly +0.1 overall.
- A qualified candidate is a possible ride-along, not evidence that a dedicated Arena
  trial is worth submission churn.
- A mechanism or value failure closes the oscillation line permanently; do not tune.

### Deliverable

`chatgpt_1/<date>-d176a-independent-review.md` plus an immutable handoff with one verdict:
ACCEPT QUALIFIED, ACCEPT CLOSED-AT-MECHANISM, ACCEPT CLOSED-AT-VALUE, or CORRECT/REJECT
with exact gate discrepancies.

### Stop rule

Once the verdict and any corrections are handed off, release the review task. Do not build,
modify, or submit a candidate.

## 2. P1 — revise H6 into a cheap value-bound audit

### Background

The generic H6 premise is invalidated:

- two-worker compatible-pair selection is already exhaustive;
- chop scoring already predicts growth during travel and chopping;
- broad MC, turn-one rollout, MOVE residual, primitive mutation, threatened-crop MC,
  one-deviation selection, and bounded-overlay grammars are closed.

The only potentially distinct residual is short intertemporal evaluation over the
resident’s existing candidate-pair surface. The integrator explicitly requested a cheap
value estimate before opening an implementation cycle.

### Session outcome

Write a revised, bounded H6 protocol proposal. Do not implement a ranker or modify the
resident. The proposal must estimate the maximum plausible value of better first-pair
choice and contain a kill decision before any large panel.

### Proposed bounded audit

Phase A — candidate-surface census:

- Use existing decoded resident games only; no fresh or sealed data.
- Reconstruct the exact resident candidate pairs at natural two-worker decision states
  with an isolated instrumented runner.
- Record feasible-pair count, live/runner-up score gap, target classes, turn, seat,
  opponent, current margin, and whether the choice lies near an intertemporal boundary
  such as target disappearance, banking conflict, or near-term target invalidation.
- Measure export and enumeration latency separately from any counterfactual execution.
- Report coverage by game, decision, family, seat, and loss/catastrophe strata.

Phase B — small oracle-value bound, only if Phase A has material coverage:

- Freeze a capped, stratified sample before outcomes: both seats; early/mid/late; wins,
  ordinary losses, catastrophes; broad opponents; close and non-close score gaps.
- For each selected state, force one already-generated compatible pair for one turn, then
  restore exact-resident fallback. No new commands, targets, options, or scoring terms.
- Evaluate paired terminal margin for the live pair and every existing alternative pair.
- Use the hindsight-best pair only as an oracle upper bound; do not fit a selector.
- Convert active-state oracle gain into projected per-game headroom using independently
  measured activation frequency, with clustered uncertainty by source game/opponent.
- Report own score, opponent score, tail mass, and family/seat breadth, not margin alone.

### Required distinctness argument

The proposal must name why this is not D36, Phase 16, D41d–D42, D97/D107, or the turn-one
rollout line. Distinctness requires all of:

- action vocabulary is exactly the live resident’s candidate pairs;
- intervention is one turn only;
- fallback is the exact live resident;
- question is intertemporal misranking inside the current pair surface;
- no MOVE-only residual, new overlay, option library, or generic command mutation.

### Predeclared kill rules

Recommend closing H6 before a full experiment if any of the following holds:

- fewer than 5% of games contain an eligible multi-pair intertemporal boundary;
- the optimistic projected oracle headroom is below +1.0 margin/game;
- active-state oracle gain is below +5.0 mean or is concentrated in one family/seat;
- the 95% upper bound on projected overall value is below +2.0 margin/game;
- candidate-surface reconstruction or required state export exceeds 5 ms p95 before
  rollout cost;
- the proposed sample cannot be separated cleanly from a consumed grammar.

These are proposal values for integrator review, not an active frozen protocol. The
integrator may accept, correct, or close them before any execution.

### Deliverable

A revised H6 proposal document and handoff requesting either:

- a canonical read-only task record for the bounded census/value audit; or
- explicit closure as too weak/redundant.

If the record is issued during the same session, execute only the approved bounded audit
phase. Do not proceed to selector fitting or resident modification.

## 3. Conditional fallback — opponent-pressure audit design

Use only if D176a has no reviewable result and the H6 proposal is blocked/closed with no
replacement assignment.

Prepare, but do not execute, one combined read-only protocol for H4 + rewritten H7 + the
H3 residual:

- reconstruct the exact resources paying opponent worker-three bills;
- test whether those resources were reachable and deniable in the pre-scaling warning
  window;
- quantify harvest/chop races, last-fruit duplication, target disappearance, and wasted
  travel;
- test whether the resident’s 41.3%→35.3% opponent-crop contact decline is a cause or a
  symptom of already losing;
- require matched opponent, roster, seat, map, duration, and pre-trigger score controls;
- require an always-on control arm before any conditional candidate can be proposed.

Kill if the condition is not load-bearing or denial value is below displacement cost.
Do not reopen unconditional opponent-crop scoring; Phase 21 closed it live.

## 4. Explicitly deferred

- Architecture-2: owner-gated. H1 requires a renewable-resource-base proof; H5/H13 show a
  fixed-two-worker design may still contain execution value.
- H10 spatial learner: owner-gated and lower priority.
- Dead-code removal: maintenance only unless a measured runtime/source-size consequence is
  tied to a qualified experiment.
- Any D176a retune or third oscillation design.
- Any generic rollout/search implementation.
- Arena, TestSession, candidate promotion, or `cgauto/api_submit.py` changes.

## 5. End-of-session completion checklist

Before stopping:

1. Write a dated worklog with exact refs, paths, commands, evidence, and unresolved risks.
2. Commit only explicit owned paths; never `git add -A` or `git add -u`.
3. Push `agent/chatgpt_1`.
4. Send one immutable handoff to `claude_1`, CC all agents/user where relevant.
5. Update `coordination/status/chatgpt_1.md`.
6. Release every completed task; leave blocked tasks explicitly blocked.
7. Verify the remote commit exists and report whether it is integrated or only pushed.
