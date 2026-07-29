# chatgpt_1 backlog

Last updated: 2026-07-29T12:35:00Z
Branch: `agent/chatgpt_1`
Integrator: `claude_1`

## Operating rule

Work one substantive item at a time. Before starting: fetch the session branch, read new messages, re-read current `docs/STATE.md` and relevant `docs/CONSTRAINTS.md`, obtain an explicit task record and write set, then publish a claim. Every completed item ends with a pushed handoff, acknowledgement, integration or explicit deferral, and release.

No Arena mutation, sealed-data access, resident-source edit, or shared-state edit without the authority required by the coordination protocol.

## Ordered backlog

### B0. Coordination cleanup

**Status:** done on this branch; awaiting integration.

- Release `20260729-rank-hypotheses-critique`.
- Withdraw the stale H5 claim after `claude_1` took the task under the published timeout condition.
- Preserve the old branch tip at `archive/chatgpt_1-pre-backlog-20260729` before resynchronizing.

**Done when:** release message and released task record are visible to the integrator.

### B1. Independent review of H5 postmortem intelligence

**Status:** blocked on `claude_1`'s H5 handoff. Do not duplicate the active search.

**Objective:** verify source quality and turn the public-strategy findings into project decisions.

**Work:**

- Check every material source, date, author identity, and contest-final versus practice-ladder context.
- Separate direct player statements from inference and from third-party summaries.
- Map each recovered mechanism to current evidence: production tempo, crop concurrency, harvesting, training bills, suppression, worker roles, endgame, and search.
- Mark each mechanism as already tested, contradicted, genuinely new, or useful only for Architecture-2.
- Identify missing top-player sources without treating absence as evidence.

**Deliverable:** review message or compact report with an accept/correct/reject verdict and concrete backlog effects.

**Done when:** the integrator can update H2/P1 priorities without re-reading the source corpus.

### B2. Independent review of H1 joint-economy upper bound

**Status:** blocked on `claude_1`'s active H1 handoff. Do not duplicate its analyzer.

**Objective:** verify that the bound is genuinely net, uses live-policy bills and referee-correct legality, and supports the H2 go/no-go claimed for it.

**Checks:**

- Bills come from revealed live TRAIN commands, not synthetic cheap-helper specs.
- TRAIN legality uses post-MOVE shack occupancy.
- Gross created value is reduced by honestly measured displaced suppression, banking, travel, and opponent compounding.
- D175a is used as a calibration anchor rather than as an arbitrary universal coefficient.
- Error bars include uncertainty in both available production and displacement price.
- Mechanical feasibility is not confused with policy selectability.
- The final material/marginal/immaterial verdict follows from preregistered thresholds, not retrospective interpretation.

**Deliverable:** independent accept/correct/reject review and a precise consequence for H2.

### B3. H6 bounded-lookahead oracle-gap audit

**Status:** preferred next unowned claim after B1/B2 reviews, unless those reports produce a stronger new lead.

**Objective:** decide whether limited deeper search over real resident decision states has enough broad value to justify implementation.

**Preflight only:** no resident change.

**Questions:**

- On which exact decision classes does a 2-3 ply bounded continuation disagree with the live choice?
- What is the paired value of those disagreements under referee terminal semantics?
- Is value broad across opponents, seats, maps, and tail cases?
- Can the oracle fit comfortably inside the 50 ms turn budget after realistic overhead?
- Does it optimize the resident's existing objective rather than silently changing it?

**Acceptance threshold:** material positive oracle gap, family/tail safety, and a credible deployable latency estimate. Otherwise close H6 without implementation.

**Expected artifacts:** task-specific analyzer, reproducible state sample manifest, report, and handoff.

### B4. Combined opponent-pressure preflight: H4 + H7 + H3 residual

**Status:** queued behind B3, or promoted if H5/H1 point directly here.

**Objective:** determine whether the resident's reduced opponent-crop contact under numeric pressure is causal and exploitable rather than a symptom of already losing.

**Scope:** read-only causal audit combining:

- H4: reconstruct the resources that paid opponent worker-3 bills and whether they were realistically deniable.
- H7 rewritten: harvest/chop races, last-fruit duplication, target disappearance, and wasted travel.
- H3 residual: contact coverage falls from 41.3% to 35.3% while outnumbered, concentrated in full-length games.

**Required controls:** matched opponent, roster, seat, map, duration, pre-trigger score state, and always-on versus condition-only counterfactual arms before any candidate is proposed.

**Kill condition:** no evidence that the condition is load-bearing, or the opportunity cost exceeds the denial value.

### B5. Architecture-2 design specification

**Status:** owner-gated. Start only after explicit user go/no-go and an integrator task record. H5 and H1 reviews are inputs.

**Objective:** define a new coherent bot rather than grafting subsystems onto Yamo/Orchard.

**Specification must cover:**

- opening and worker-2 transaction;
- renewable production and crop concurrency;
- harvest-capable worker specs;
- transactional training-bill reservation;
- role allocation and collision-safe joint assignments;
- suppression as part of the same scheduler;
- endgame and liquidation;
- observability, latency, deterministic testing, and source-size limits.

**Milestone gates:**

1. Referee and evaluator parity.
2. Equal-roster performance and tail safety at least match the resident.
3. Closed-loop plant-reap-fund-train works without feeding the opponent.
4. Survival against three- and four-worker opponents improves materially.
5. Same-panel dominance over the resident before any promotion discussion.

### B6. Architecture-2 implementation workstreams

**Status:** blocked on B5 approval and design acceptance.

Potential owned modules, one task each:

- architecture skeleton and state representation;
- transactional economy scheduler;
- joint assignment solver;
- evaluator parity tests and failure taxonomy;
- compact Rust packaging and latency profiling;
- independent review of other agents' modules;
- candidate qualification report and handoff to the arena controller.

No direct submission authority.

### B7. H10 spatial-planes learner review or implementation

**Status:** low-priority owner-gated alternative to Architecture-2.

**Objective:** test the only sanctioned D172 reopening: whether spatial observations can identify the +10.671 option-envelope contexts that scalar observables could not.

**First step:** architecture and data-parity review, not GPU training. Preserve every D172 independent-block, safety, latency, and sealed-data gate.

## Continuous responsibilities

- Sweep inbox and remote refs before each work block.
- Review H5, H1, or future agent handoffs when assigned.
- Challenge causal claims, trigger fidelity, evaluation parity, and source liveness.
- Publish negative results and corrections, not only promising leads.
- Keep exact commit hashes, commands, data provenance, and local/field/Arena distinctions.
- Never stage another worker's files; name explicit paths only.

## Explicitly not in my backlog

- Duplicate H5 or H1 work while `claude_1` owns it.
- More fruit-priority tuning on the resident.
- Worker-2 timing changes; H8 is closed.
- Re-running the no-loop-quartet premise; H3 corrected it.
- Body-blocking or door-camping; cross-player physical blocking is impossible.
- Global opponent-crop rescoring without causal conditioning; Phase 21 closed it live.
- Map configuration justified only by opponent-family failures.
- Identical-source resubmission outside an authorized promotion.
- Arena writes, candidate selection for submission, or changes to `cgauto/api_submit.py`.
