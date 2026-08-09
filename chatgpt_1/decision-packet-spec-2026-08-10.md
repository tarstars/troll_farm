# M1 specification — versioned per-turn Decision Packet

- Spec author: `chatgpt_1`
- Task: `20260810-manifest-implementation`, item M1
- Subject bot:
  `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
- Subject SHA-256:
  `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- Implementation owner: `claude_1`
- Execution reviewer: `local_claude_1`
- Spec/conformance reviewer: `chatgpt_1`
- Status: **frozen implementation contract; specification only**
- Boundary: tooling and analysis only. No bot policy, candidate behavior, detector predicate, gate,
  host-value protocol, TestSession, submission, restore or Arena mutation is authorized.

## 1. Purpose

The Decision Packet explains one complete turn of the bot as an executable decision pipeline, not
merely as a list of scalar scores.

For one exact input state it must answer, without re-reading the Rust source:

1. Which persistent mode and control-flow branches were active?
2. Which action generators were entered, skipped or terminated early, and why?
3. Which finite action opportunities were considered?
4. Which candidates were emitted or excluded, and why?
5. What intention, target, score expression and attainable range belongs to each candidate?
6. Which candidate pairs were legal or rejected, and why?
7. Which pair or greedy sequence won, including exact tie-breaking?
8. Which commands were selected before movement resolution?
9. Which commands were rewritten by the resolver, using which occupied/reserved cells and ranking
   keys?
10. Which persistent commitments were changed?
11. When an accepted engine/referee is available, what actually executed and what progress
    resulted?

A packet is successful only when an independent verifier can replay the selection and rewrite
outcome from the packet itself. A pretty-printed winner with no rejected alternatives is not a
Decision Packet.

## 2. Correct model of the bot

The subject is a hybrid pipeline:

```text
wire state
  -> persistent-state reconciliation and mode selection
  -> candidate-generator selection / early returns
  -> finite opportunity enumeration and filtering
  -> score construction
  -> two-unit pair compatibility + score aggregation
     or >=3-unit greedy arbitration
  -> forced candidate replacement / door-unblocking layers
  -> post-selection MOVE conflict resolution and rewriting
  -> persistent commitment updates
  -> emitted command line
  -> optional accepted-engine execution evidence
```

Scalar score is one stage. Candidate absence, early returns, hard compatibility and resolver
rewrites can dominate behavior without any score comparison. The packet schema must therefore
represent all stages explicitly.

## 3. Non-goals

M1 does not:

- change any score, target, filter, tie-break, command or persistent state;
- declare any intention hierarchy correct;
- infer “best action” from the bot's own score;
- require an accepted referee for decision-only packets;
- turn provisional execution from the current unaccepted panel into fact;
- replace independent M3b adjudication;
- promise a low-latency production path. The first implementation is an offline analysis tool.

## 4. Identity and trust envelope

Every packet must start with a machine-verifiable envelope.

```json
{
  "schema": "troll-farm-decision-packet/v1",
  "packet_id": "sha256:<canonical packet identity>",
  "subject": {
    "path": "cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs",
    "sha256": "98628e98...",
    "instrumentation_sha256": "...",
    "tool_commit": "<40 hex>",
    "source_registry_sha256": "..."
  },
  "input": {
    "map_sha256": "...",
    "state_sha256": "...",
    "turn": 17,
    "seat": 0,
    "source": "literal_fixture|recorded_game|manual_state",
    "source_ref": "...",
    "trust": "SOURCE_EXACT|PROVISIONAL_EXECUTION|ACCEPTED_EXECUTION"
  }
}
```

Requirements:

- The subject SHA is exact, never a prefix.
- Instrumenting a neighbouring resident (`fff6669b`) does not satisfy this task.
- Every source span and expression id is bound into `source_registry_sha256`.
- The input state is canonicalized before hashing; map, inventories, plants, units, turn and
  persistent bot state are included.
- A packet must say `PROVISIONAL_EXECUTION` or `EXECUTION_UNAVAILABLE` until the referee is
  accepted. It may not imply accepted execution merely because a closed loop ran.

## 5. Stable semantic registries

The implementation must contain code-owned registries; prose is generated from them.

### 5.1 Stage registry

At minimum:

- `STATE_RECONCILE`
- `OPENING_INITIALIZE`
- `TRAIN_DEADLINE`
- `MODE_SELECT`
- `CANDIDATE_GENERATE`
- `FORCED_REPLACEMENT`
- `PAIR_SELECT`
- `GREEDY_SELECT`
- `MOVE_RESOLVE`
- `COMMITMENT_UPDATE`
- `EMIT`
- `EXECUTE` (optional extension)

### 5.2 Intent registry

The registry must distinguish primary intention from score-term contributions. Initial ids may
include:

- `WAIT`
- `BANK`
- `EQUIP_FOR_TRAIN`
- `CLEAR_SHACK_FOR_TRAIN`
- `HARVEST_FRUIT`
- `MINE_IRON`
- `CHOP_WOOD`
- `DENY_FOCUS_SPECIES`
- `REGENERATE_CARRIED_FRUIT`
- `CONVERT_BANKED_FRUIT`
- `COMMIT_CURRENT_CHOP`
- `IDLE_HARVEST`
- `UNBLOCK_UNIQUE_DOOR`

These names are not an owner-ratified priority hierarchy. Each registry entry carries:

```text
intent_id
human_label
source_sites
status = OBSERVED | HYPOTHESIZED | OWNER_RATIFIED
completion_predicate
progress_predicate
invalidation_predicate
```

A composite score such as chop value plus denial bonus has:

- primary candidate intent: `CHOP_WOOD`;
- term contribution intent: `DENY_FOCUS_SPECIES`.

This prevents a bonus from hiding a second intention inside one number.

### 5.3 Priority-class registry

`priority_class` must be explicit metadata, not inferred from numeric magnitude. Until the owner
ratifies ordering, use `HYPOTHESIZED` classes and preserve uncertainty.

A packet must never transform “score 7000” into “higher intention” without an explicit registry
entry.

### 5.4 Source-site registry

Every generator, filter, score term, early return, compatibility rule, replacement and resolver
branch has a stable id, for example:

```text
GEN_ENDGAME_CONVERT_ON_DOOR
FILTER_BANK_DOOR_OCCUPIED
TERM_CHOP_WOOD_RATE
TERM_FOCUS_DENIAL_BONUS
PAIR_TARGET_NONE_BYPASS
REWRITE_RESERVED_LANDING_DETOUR
```

Each id binds:

- exact source path;
- source line range at the subject SHA;
- AST/text fingerprint;
- stage;
- intent or rule id;
- expected input/output shape.

A drift checker fails when a source fingerprint moves or changes without a registry update.
Generated documentation is a projection of this registry; it is never the authority.

## 6. Packet event model

A packet contains an ordered `events` array. Events use stable ids and explicit parent/causal links.

Common fields:

```json
{
  "event_id": "e0042",
  "stage": "CANDIDATE_GENERATE",
  "site_id": "GEN_ENDGAME_CONVERT_ON_DOOR",
  "unit_id": 0,
  "parents": ["e0038"],
  "outcome": "EMITTED|EXCLUDED|SKIPPED|EARLY_RETURN|REPLACED|SELECTED|REWRITTEN",
  "reason_code": "...",
  "facts": {}
}
```

Free-form prose may be rendered for humans, but all load-bearing reasons must be enums plus data.

## 7. Control-flow and mode trace

The packet records persistent bot state before and after the turn and every branch that controls
candidate availability.

Required fields include:

- `type_to_cut`;
- `desired_second` and opening flags;
- `opening_abandoned`;
- `idle_regeneration`, `persistent_regeneration`, `door_unblocking`,
  `partial_bank_transit`, `idle_harvest`, `idle_harvest_clock_only`;
- `regeneration_commitments`;
- opponent ETA penalty;
- derived `train_now`, `early`, `endgame`, committed-regeneration status per unit;
- selected candidate generator per unit;
- every early-return condition and whether it fired.

When a generator is skipped because another branch returned early, record a generator-level event:

```text
outcome: SKIPPED
reason_code: SKIPPED_BY_EARLY_RETURN
blocking_event: <event id>
```

Do not fabricate candidate-level exclusions for a generator that was never entered.

## 8. Complete finite opportunity accounting

“Every candidate and exclusion reason” means:

- for an entered generator, enumerate its finite opportunity domain;
- for each opportunity, emit either an `EMITTED` candidate or an `EXCLUDED` event;
- for an unentered generator, emit one `SKIPPED` generator event.

Examples of finite opportunities:

- each plant for harvest/chop;
- each iron-adjacent walkable cell;
- each shack door;
- each carried or banked fruit kind;
- each walkable planting cell when that generator genuinely enumerates all cells;
- each own unit for forced door clearing.

Exclusion reason codes must be specific, for example:

```text
NO_CAPACITY
NO_POWER
WRONG_KIND
DEAD_PLANT
UNREACHABLE
TIME_HORIZON
OCCUPIED_BY_OWN_UNIT
OPPONENT_CONTACT_FILTER
COMMITMENT_FILTER
SAFE_REGENERATION_FILTER
STOCK_SHORTAGE
GENERATOR_NOT_ENTERED
```

A generic `FILTERED` reason is not accepted.

## 9. Candidate record

Each emitted candidate has a deterministic `candidate_id`, stable under unrelated list ordering.
Recommended identity:

```text
sha256(subject sha, turn-state hash, unit id, site id, opportunity key, command, target)
```

Required record:

```json
{
  "candidate_id": "c:...",
  "unit_id": 0,
  "generator_id": "GEN_CHOP",
  "intent_id": "CHOP_WOOD",
  "intent_status": "OBSERVED",
  "command": "MOVE 0 9 1",
  "semantic_target": {"kind": "TREE", "cell": [9, 1]},
  "predicted_landing": [2, 4],
  "priority_class": {"id": "WORK", "status": "HYPOTHESIZED"},
  "score": {"decimal": "57.142857142857146", "f64_bits": "0x..."},
  "score_expression_id": "S_CHOP_TOTAL",
  "score_terms": [],
  "eligibility_facts": {},
  "source_site": "..."
}
```

Scores and term values include both a human decimal and exact IEEE-754 bits. Replay must not
depend on decimal round-tripping.

## 10. Score-term and attainable-range contract

Every score is decomposed into named terms. A term record contains:

```json
{
  "term_id": "TERM_CHOP_WOOD_RATE",
  "contribution_intent": "CHOP_WOOD",
  "operation": "ADD|SUBTRACT|OVERRIDE|MULTIPLY|DIVIDE",
  "value": {"decimal": "57.142857...", "f64_bits": "0x..."},
  "formula": "1000 * wood / turns",
  "inputs": {
    "wood": {"value": 1, "source": "predicted_final_size/free_capacity"},
    "turns": {"value": 17, "source": "travel+chop+return+1"}
  },
  "ranges": {
    "state_conditioned": {"min": "57.142857...", "max": "57.142857...", "status": "EXACT"},
    "site_reachable": {"min": "0", "max": "1500", "status": "PROVED"}
  },
  "range_proof": {
    "assumptions": ["chop_turns >= 1", "final +1 overhead", "carry_capacity <= 3"],
    "source_sites": ["..."],
    "method": "STATIC_INTERVAL|ENUMERATION|SYMBOLIC|UNKNOWN",
    "witness": null
  }
}
```

### 10.1 Range levels

Every term must provide both:

1. **state-conditioned range** — normally a singleton once current inputs are known;
2. **site-reachable range** — the attainable range under real source/engine invariants for the
   exact subject revision.

A syntactic range is not enough. `turns.max(1)` does not justify `turns >= 1` when the producing
control flow proves `turns >= 2`. Conversely, a parameter does not imply multiple call-site values
when only one call site exists.

### 10.2 Proof status

Allowed values:

- `PROVED`
- `MEASURED_COMPLETE_DOMAIN`
- `MEASURED_SAMPLE`
- `HYPOTHESIZED`
- `UNKNOWN`
- `NOT_APPLICABLE`

Unknown bounds remain unknown. The tool must not invent a finite bound to render a nicer packet.

### 10.3 Cross-boundary diagnostics

The packet may report diagnostics, not verdicts:

- candidate's reachable range overlaps another priority class;
- pair-sum can trade one unit across a class boundary;
- an `OVERRIDE` discards a computed value;
- temporal/control-flow branch changes the score expression for the same intent;
- a score term is dead under current call graph or invariant.

These diagnostics require an explicit compared set of co-reachable candidates. A global numerical
overlap alone is not proof of a behavioral crossing.

## 11. Pair selection and greedy arbitration

### 11.1 Two-unit path

Record every Cartesian candidate pair in deterministic enumeration order:

```json
{
  "pair_id": "p:...",
  "candidate_ids": ["c:a", "c:b"],
  "target_compatible": false,
  "target_compatibility_rule": "PAIR_TARGET_NONE_BYPASS",
  "stock_compatible": true,
  "rejection_reasons": ["SAME_TARGET_CELL"],
  "pair_score": {"decimal": "...", "f64_bits": "0x..."},
  "comparison_index": 42,
  "selected": false
}
```

For `Target::None`, record both:

- semantic compatibility result;
- physical stationary occupation of the unit's current cell.

This makes “planner says compatible while world occupation conflicts” directly queryable.

The packet must identify:

- independently best candidate per unit;
- best legal pair;
- why the independent best pair was rejected, if it was;
- score cost paid by each unit to obtain pair compatibility;
- exact tie-breaking / first-winner behavior.

### 11.2 Three-or-more-unit path

Even if dead for the current bot policy, the packet registry must represent the greedy branch and
mark it `UNREACHABLE_UNDER_SUBJECT_INVARIANTS` only with a cited proof. If later source changes make
it reachable, the drift check must fail until packet support is added.

## 12. Forced replacements and candidate-set mutations

Door-clearing and other layers can replace a unit's whole candidate list or inject forced
candidates. Each mutation event records:

- candidate set before;
- rule and triggering facts;
- removed candidate ids;
- inserted candidate ids;
- whether the mutation is mandatory or merely high-scored;
- downstream effect on selection.

This distinguishes a `20_000` list replacement from a `6_500` candidate that may lose a score
comparison, even when both are labelled `CLEAR_SHACK_FOR_TRAIN`.

## 13. Resolver trace

For every selected MOVE, record:

- unit current cell, semantic target and original command;
- engine-predicted landing;
- `moving_ids`;
- `occupied_now`;
- initial and evolving `reserved` set;
- priority and forbidden sets;
- direct-landing legality;
- every detour candidate with exclusion reasons and ranking key;
- chosen resolver branch: `DIRECT`, `DETOUR`, `WAIT_NO_LANDING`, `ALREADY_AT_LANDING`;
- rewritten command;
- whether the rewrite violates the selected candidate's semantic target or predicted progress;
- typed feedback status: currently `NOT_FED_BACK` for the shipped bot.

A resolver event must causally reference the candidate and pair events that produced it.

The independent verifier must reproduce the post-rewrite command vector from these records.

## 14. Persistent-state update trace

Record every mutation after selection/rewrite:

- reconciliation removals from `regeneration_commitments`;
- new commitments inferred from selected commands;
- opening-state changes;
- announcement state;
- any future blocked-target or movement state added by later experimental branches.

For each mutation include old value, new value, reason and source site.

## 15. Optional execution extension

Decision-only packets do not require a referee. Execution evidence is a separate extension:

```json
{
  "execution": {
    "status": "UNAVAILABLE|PROVISIONAL|ACCEPTED",
    "engine_or_referee_sha256": "...",
    "schema_version": "...",
    "parsed_commands": [],
    "executed_events": [],
    "unsupported_or_malformed": [],
    "next_state_sha256": "...",
    "progress_delta": {}
  }
}
```

Rules:

- `ACCEPTED` requires the accepted referee/engine identity and full command execution provenance.
- Current TRAIN-panel output is not accepted execution evidence.
- When execution is unavailable, decision fields remain useful and the packet says so explicitly.
- Realized progress must be separated from predicted progress.

## 16. Blind projection for M3b independent adjudication

The implementation must generate two projections from one sealed packet.

### 16.1 Blind situation view

Contains:

- exact map and state;
- unit capabilities and inventories;
- legal action opportunity descriptions;
- source/trust identity;
- packet commitment hash.

It hides:

- bot scores and score ranges;
- selected candidates/pair;
- resolver choice;
- realized outcome after the decision.

`chatgpt_1` records an independent action judgment against this view.

### 16.2 Reveal view

After adjudication, reveal the full Decision Packet and compare:

- independent choice versus bot choice;
- intent and action disagreements;
- score/eligibility/compatibility mechanism causing the difference;
- confidence and unresolved facts.

This prevents the adjudicator from grading the scorer with the scorer's own output.

## 17. Output and rendering

Authoritative format: canonical JSON, one packet per turn or one standalone packet per requested
state.

Required tools:

```text
decision_packet explain --state <file> --turn <n> --json <packet.json>
decision_packet render  --packet <packet.json> --markdown <report.md>
decision_packet verify  --packet <packet.json>
decision_packet blind   --packet <packet.json> --out <situation.json>
```

The Markdown renderer is generated output and may be regenerated. JSON plus source registry is the
authority.

Large all-pair surfaces may be compressed in archives, but the single-state `explain` path must be
simple and reviewable. The old N4 pair-surface tooling can supply reusable capture patterns, but it
is SHA-locked to a different resident and cannot be treated as M1 completion without retargeting and
revalidation against `98628e98`.

## 18. Non-interference requirement

Instrumentation must not change behavior.

Acceptance requires:

- exact emitted command stream equality between instrumented and uninstrumented subject;
- exact persistent-state equality after every turn;
- deterministic packet bytes for the same source/state;
- no dependency of selection on logging order, packet ids or renderer;
- packet capture reset before every turn so stale events cannot leak.

At minimum test the literal oscillation states and a deterministic multi-map corpus. Any mismatch is
`NOT_ACCEPTED`, not a tolerable instrumentation effect.

## 19. Independent replay verifier

A verifier implemented outside the instrumented candidate must consume the packet and reconstruct:

1. candidate availability after control flow;
2. candidate score from term values;
3. candidate ordering;
4. pair compatibility and stock compatibility;
5. selected pair or greedy sequence;
6. forced replacement effects;
7. resolver rewrite output.

It compares every reconstructed result to packet claims. The verifier must not call the candidate's
selection functions or share their implementation helpers; otherwise both can agree on the same
error.

## 20. Required red/green fixtures

### 20.1 M1 corridor block — `m110-s1`

The packet must show:

- distinct semantic target versus stationary physical occupation;
- constant goal;
- direct landing blocked by reserved peer;
- forced retreat chosen by resolver;
- no feedback to target validity;
- blocker action and intent (`WAIT`/stationary, not inferred “working”).

### 20.2 M2 `Target::None` bypass — `m014-s1`

The packet must show:

- stationary unit emits WAIT with `Target::None`;
- moving unit targets the stationary cell;
- semantic compatibility returns true;
- physical occupation conflict appears only in the resolver;
- repeated detour mechanism.

### 20.3 M3 scorer cycle — `m085-s0`

The packet must show:

- generator branch entered on each side of the two-cycle;
- candidate opportunity universe differs on-door versus off-door;
- excluded/skipped alternate door while on-door;
- exact conversion and competing chop terms/ranges;
- selected target flips without progress.

### 20.4 Provisional working-blocker case — `m040-s1`

Packet may be generated but execution trust is `PROVISIONAL` until the referee is accepted. It must
not be mixed with accepted fixtures.

### 20.5 Additional anti-overfit fixtures

- legal swap;
- legal movement chain;
- bank candidate filtered to empty;
- forced unique-door replacement;
- soft `6_500` train-clear candidate losing to another candidate;
- pair where independent maxima are incompatible;
- duplicate non-TRAIN command when an accepted parser packet becomes available.

## 21. Mutation and completeness tests

Required mutants/controls include:

1. omit one candidate generator;
2. omit one exclusion reason;
3. alter one score term value;
4. alter one attainable-range bound (`turns >= 2` to `>= 1`);
5. hide one early return;
6. make `Target::None` compatibility invisible;
7. omit one rejected pair;
8. alter pair tie order;
9. omit a forced replacement;
10. omit a resolver rewrite reason;
11. report pre-rewrite as final command;
12. reuse stale prior-turn packet events;
13. instrument the wrong subject SHA;
14. mark provisional execution accepted;
15. change a source site without updating the registry.

Every mutant must be caught by committed tests. Surviving mutants require an equivalent-mutant
argument tied to reachability, not a generic explanation.

## 22. Completeness metrics

Each packet publishes:

- generators entered/skipped;
- finite opportunities considered;
- emitted/excluded candidates;
- pair count = Cartesian product size for two-unit selection;
- pairs accepted/rejected, partitioned by reason;
- replacements and rewrites;
- score sites and range-proof statuses used;
- unknown/provisional fields.

A verifier checks conservation identities, for example:

```text
opportunities = emitted + excluded
pairs_total = pairs_accepted + pairs_rejected
selected_pre_rewrite commands = resolver inputs
resolver outputs = emitted bot commands excluding protocol-level MSG/TRAIN additions as declared
```

Missing coverage produces `PACKET_INCOMPLETE`, never a partially green explanation.

## 23. Rollout sequence

1. Freeze schema, source registry and exact candidate SHA.
2. Implement single-state capture for mode, candidate generation and exclusions.
3. Add score terms and attainable-range proofs.
4. Add pair arbitration and independent replay.
5. Add forced replacement and resolver trace.
6. Prove non-interference on literal fixtures and deterministic corpus.
7. Add blind/reveal projections.
8. Generate packets for M3a situations.
9. Execution review by `local_claude_1`.
10. Conformance review by `chatgpt_1`.

No full-corpus latency gate blocks this offline tool. Performance is reported, but correctness,
completeness and non-interference are adoption gates.

## 24. Acceptance checklist

M1 is accepted only when all are true:

- exact subject SHA and registry drift guard;
- complete pipeline, not score-only;
- all entered opportunities emitted or excluded with typed reason;
- skipped generators and early returns visible;
- intents and score-term intents explicit;
- exact f64 values and attainable ranges with proof status;
- every pair and rejection recorded;
- selected alternatives and tie order recorded;
- forced replacements recorded;
- resolver pre/post commands and typed reasons recorded;
- persistent state changes recorded;
- independent replay succeeds;
- blind projection supports independent adjudication;
- execution trust status cannot be overstated;
- instrumentation is command/state byte-neutral;
- known M1/M2/M3 fixtures expose their mechanisms;
- completeness and mutation suites pass;
- method and source registry are committed and reproducible.

## Final ruling

The Decision Packet is both the first bridge and the first debugger. It must be generated from the
code that actually decides, and an independent verifier must prove it explains the decision. A
static intention/score table, a winner-only trace or a packet that ignores control flow and resolver
rewrites does not satisfy M1.
