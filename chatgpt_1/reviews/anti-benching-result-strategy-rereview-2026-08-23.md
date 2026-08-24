# Anti-benching r2 result and strategy rereview

- Task: `20260823-anti-benching-result-strategy-rereview`
- Reviewer: `chatgpt_1`
- Review mode: read-only meta-review; no code, experiment, panel rerun, gate change, TestSession, submission, or Arena action
- Task/policy snapshot read: `origin/main@10e595084c06d482edce0e352b006e34df29d237`
- Result state checked: `origin/main@aaaa53243e0110aee46831e635fb641b26b2a5a1`
- Result verdict: **`RESULT_VALID_BUT_CAUSAL_CLAIM_UNPROVEN`**
- Qualification consequence: **the 35 -> 115 frozen-gate result stands, and r2 remains rejected**

## 1. Executive decision

The team did **not** make a population, source-identity, or reproducibility mistake that rescues r2.
The exact r2 source and exact P1+P2 base are pinned, the candidate panel was rerun from the pinned
instrument checkout, all 240 candidate game rows reproduced exactly, and an independent verifier
re-derived 115 versus 35 blocking games, 80 de-novo blockers, zero healed blockers, five new P3
games, and 73 new P4 games. The executable evidence is at
`agent/local_codex_1@16b6e4ada72ab1381833162ed98e97ba930cd9b4`:

- `local_codex_1/reviews/pair-selector-gd-ge-unified-review-2026-08-23.md`, section
  "Independent executable reproduction";
- `local_codex_1/reviews/run_gd_blocker_full_reproduction.py`, `main()`;
- `local_codex_1/reviews/reproduce_gd_blocker.py`, `keyed()` and `main()`.

The rejection is independently decisive even without trusting the P4 interpretation: the locked
candidate report contains five direct P3 command-stream divergences on orchard-eligible games, all
beginning at turn 100. For example, `m035` seat 0 emits `WAIT;PICK 2 BANANA` while the exact base
emits `WAIT;WAIT`. Under the frozen P3-clean rule, one such divergence is enough to block r2. Exact
rows are in
`agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/picker3/results/gd-door1-panel-2026-08-23.md`
under `m035`, `m065`, `m074`, `m104`, and `m114`; the R-3 rule is frozen in
`origin/main@aaaa53243e0110aee46831e635fb641b26b2a5a1:coordination/tasks/20260820-pair-selector-anti-benching.md`,
Phase 3c.

What the result does **not** prove is the broad causal story sometimes read into it: that preserving
replant `PICK`s, through the persistent regeneration commitment, caused 73 ordinary liveness
regressions. The package does not separate the preserved option (Delta-A), commitment routing,
duplicated bank candidates (Delta-B), pair selection, and a future-dependent P4 classification.
The builder report itself correctly calls the downstream-commitment explanation an interpretation,
not a causal experiment:
`agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/picker3/gd-ge-door1-report-2026-08-23.md`,
section "Result".

Therefore:

- **Observed qualification result:** valid.
- **r2 implementation:** rejected and remains stopped.
- **Underlying hypothesis that a narrowly preserved replant option can create useful progress:**
  unresolved.
- **Attribution of the 73 P4 additions to harmful stalling caused during their named windows:**
  unsupported by the present evidence.

The report phrase "catastrophically worse" is defensible only as shorthand for frozen-gate counts.
It must not be promoted into a claim about Arena score, full-horizon value, or a demonstrated single
failure mechanism.

## 2. Method audit

### 2.1 Panel, source, and population identity

**Observed facts.** The executable review verifies these exact SHA-256 identities:

- r2 candidate: `457360589a65cb2662950761deba817852ea9eb0d2c53b05a3e6fd2ab9dfda8a`;
- P1+P2 base: `5e1f4df406480f678ff03677cdda0f69d510c5c94efe90d4f0a8231b70c3339e`;
- panel instrument: `d8900abf31dd030d07096e9a063365aa0e1f58b85a1613d02b07d3935c523a6a`;
- engine: `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05`.

`run_gd_blocker_full_reproduction.py::main()` reconstructs the accepted locked configuration from
`agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10`, verifies all four hashes,
runs the 120-map x 2-seat panel, requires scientific exit 1, and compares every candidate game row
with the submitted packet. It permits only measured wall-time drift in the aggregate packet.
`reproduce_gd_blocker.py::keyed()` rejects duplicate `(map_id, seat)` keys and requires exactly 240
unique rows; `main()` also checks corpus/instrument/referee/engine metadata, source labels, clean
execution, and map/seat/seed/class/profile/attempt/turn identity.

The historical base is not a floating or retrospectively chosen comparator. The unified review
records that its JSON is byte-identical to the accepted
`claude_1/picker2/panel-door1-cand.json` at the exact panel checkout, with SHA-256
`41e3be878b590998e69b9d690559daa87db0ed959b11ec142879c9af75b27a5b`. The prior Phase 2 review
also independently reproduced the downstream keyed checks that reported Door-1 blocking 43 -> 35:
`agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/reviews/pair-selector-phase2-unified-review-2026-08-20.md`.

**Deduction.** The 35 -> 115 comparison is a controlled historical comparison on the same locked
population and exact source identities. It is not an Arena comparison and it is not a claim that
r2 is "three times worse" in field play.

**Residual limit.** The full reproduction reruns the r2 candidate packet but consumes the pinned
historical base packet for the `base_blocking = 35` side. The independent verifier's explicit
identity tuple does not include `opponent_commands_sha256`, although the full candidate packet
comparison includes the submitted rows byte-for-byte. This is a residual provenance limitation for
a completely fresh two-arm reconstruction, not a rescue for r2: the five P3 divergences are computed
inside the exact current candidate-versus-parent run and independently violate the frozen gate.

### 2.2 Did the full rerun close the analyzer defects?

**Closed for the outcome count.** The earlier fresh-eyes review found that the builder analyzer could
silently overwrite a duplicate key, compared fixtures only by `(map_id, seat)`, and trusted
self-reported source hashes. Those weaknesses are recorded at
`agent/chatgpt_1@c67244197bec5ff59a3b5e59f10430c0197af639:chatgpt_1/reviews/pair-selector-gd-ge-fresh-eyes-review-2026-08-23.md`,
findings F2-F4. The independent rerun closes them for this result by hashing the actual source,
panel, and engine files, rejecting duplicate rows, checking a wider identity tuple, and reproducing
the complete candidate packet.

**Not closed for causal attribution.** The decomposition still projects each changed game only to
block state, properties, flags, and a few descriptive fields. It does not provide, for each of the
85 changed games, the first command divergence, changed command/event sequence, commitment lifetime,
Delta-B reach, or a mechanism diagnosis. `reproduce_gd_blocker.py` deliberately verifies the same
compressed projection. Thus the rerun proves that the observations are real; it does not prove why
they occurred.

### 2.3 P3 semantics

**Observed fact.** In the panel instrument, P3 is strict command-stream equality between candidate
and parent on orchard-eligible views. The locked report says 12 orchard-eligible games were checked
and only seven passed. The five failures are direct command divergences at turn 100:

| game | candidate command | exact base command |
|---|---|---|
| `m035` seat 0 | `WAIT;PICK 2 BANANA` | `WAIT;WAIT` |
| `m065` seat 0 | `PICK 0 BANANA;PICK 2 PLUM` | `WAIT;WAIT` |
| `m074` seat 0 | `PICK 0 BANANA;WAIT` | `WAIT;WAIT` |
| `m104` seat 0 | `WAIT;PICK 2 APPLE` | `WAIT;WAIT` |
| `m114` seat 0 | `PICK 0 BANANA;PICK 2 PLUM` | `WAIT;WAIT` |

Source: `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/picker3/results/gd-door1-panel-2026-08-23.md`,
those five named game sections.

**Deduction.** The P3 result is not an analyzer artifact or an aggregate threshold effect. It is a
direct consequence of allowing the replant option in a state the frozen rule requires to remain
inert. It is enough to reject r2 under the accepted gate.

**Limit.** P3 proves violation of an owner-frozen safety policy. It does not prove that the divergent
replant command loses score or is intrinsically bad. A future design may remain P3-clean by excluding
orchard-eligible states, but r2 did not.

### 2.4 P4 semantics and the turn-99 boundary

The exact P4 implementation is described in
`agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:claude_1/pipeline/gate-repair-p4-report-2026-08-06.md`
and implemented in `claude_1/pipeline/fuzz_panel.py`:

- `work_remaining(tr, t)` counts own cargo or a reachable plant as work;
- banked plantable fruit is deliberately **not** counted, to avoid demanding score recycling;
- `live_horizon(tr)` finds the start of the final terminal suffix by scanning backward;
- `eval_p4(...)` trims a no-progress run to `live_horizon - 1` and blocks if at least 60 turns remain.

**Observed fact.** In `m035` seat 0, the exact command streams first diverge at turn 100, when r2
emits `WAIT;PICK 2 BANANA` and the base emits `WAIT;WAIT`. Nevertheless, r2 receives a candidate-only
P4 violation for turns 33-99, with `live_end = 99` and `terminal_from = 106`. The exact base is clean
on that game. The row is in
`agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/picker3/results/gd-door1-panel-2026-08-23.md`,
section `m035 seat 0`; its candidate-only `P3,P4` classification is in
`codex_1/picker3/results/gd-door1-decomposition-2026-08-23.json`, row `(m035, 0)`.

**Logical deduction.** r2 cannot have changed the emitted commands during turns 33-99, because the
first divergence is turn 100. In a deterministic referee, it therefore cannot have changed the
world states during that interval. The new P4 classification of the pre-divergence interval must
come from information after turn 99. That is exactly what `live_horizon()` permits: a later `PICK`
turns ignored banked fruit into cargo and potentially a plant, so the final terminal suffix starts
later and an earlier idle interval is retrospectively treated as live.

This does **not** show that P4 is generally wrong. It shows that this P4 label answers a
trajectory-level question - whether a long progress-free interval lies before the final terminal
suffix - and is not, for a policy that can reactivate work, direct evidence that candidate behavior
caused the stall during the named interval. The same temporal shape is visible in other direct P3
rows, including `m065` seat 0 and `m114` seat 0, where the first divergence is turn 100 and P4 ends
at turn 99.

**Consequence.** The 73 new P4 count is valid under the frozen implementation and remains a binding
qualification gate because the design accepted that gate. It is not valid as a 73-game causal
inventory of ordinary downstream stalling. The missing per-game command/event diagnosis prevents
separating temporal reclassification from genuine post-divergence liveness damage.

### 2.5 First-falsifier stopping

**Qualification verdict.** Stopping before G-e was correct. The accepted r2 design explicitly says
that any new P3/P4/r5-horizon event stops the build and cannot be waived by aggregate progress:
`agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35:claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md`,
sections 6 and 7. Five direct P3 violations already make G-e incapable of qualifying r2.

**Scientific limit.** G-e was also the only frozen gate designed to answer whether a preserved
`PICK` produces actual banking or employment rather than detector silence. Because it remained
unrun, the central benefit hypothesis is unresolved. The first-falsifier rule is appropriate for
promotion safety but should not be described as completing causal learning.

### 2.6 Horizon and outcome limits

The exact candidate source declares `TOTAL_TURNS = 300` at
`agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:claude_1/picker3/candidate-door1-p3b.rs`,
`game::rules`. The G-d panel runs 200 turns, and the accepted build review reports that every first
selected Delta-A tick in its fixture library is turn 100. Thus the panel supplies at most 100 turns
of post-trigger observation for a stateful policy written around a 300-turn horizon.

This is not a defect in the frozen qualification gate and does not rescue r2. It is another reason
not to infer full-horizon economic value or commitment completion from the G-d stop.

## 3. Causal audit

### 3.1 Delta-A: preserved replant `PICK`

**Observed.** The original route diagnosis found two real replant `PICK` candidates discarded on
101 OSC-013 turns, all at turns 100-200:
`agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35:claude_1/picker2/phase3-generator-route-2026-08-20.md`,
headline and "What this does and does not establish". The document explicitly says preserving the
options was not shown to restore progress.

The accepted r2 build demonstrates that Delta-A is not merely syntactic. In the Door-1 fixture
library, 201 Delta-A candidates were formed and 143 selected across 19 EFFECT games; every first
selection was turn 100:
`agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/reviews/pair-selector-phase3b-build-review-2026-08-23.md`.
The real-corpus reach review independently found 339 restored **and selected** turns, grouped into
34 episodes in 14 of 49 parity-verified games, while 111 of 160 games refused closed:
`agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/reviews/pair-selector-phase3b-reach-review-2026-08-23.md`.

**Proved effect.** Delta-A has non-zero natural reach and can survive joint selection.

**Not proved.** Delta-A by itself creates durable progress, positive value, or the observed broad
costs. The only tested implementation couples it to commitment routing and Delta-B.

### 3.2 Persistent regeneration commitment

**Observed source semantics.** The accepted design records that a selected `PICK` is remembered in
`regeneration_commitments`; later `commands()` routes that unit to `endgame_candidates` until
`reconcile_regeneration_commitments` clears the commitment. Source and design:
`agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35:claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md`,
section 3, and the corresponding functions in
`agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:claude_1/picker3/candidate-door1-p3b.rs`.

**Deduction.** A selected Delta-A command is stateful and can alter later candidate generation even
though the source diff is one small fallback change.

**Hypothesis.** Persistent commitment is responsible for most post-turn-100 regressions. The package
is consistent with this, but no per-game commitment timeline or controlled no-commitment arm was
published. The hypothesis remains unproven.

### 3.3 Delta-B: duplicated/reordered bank candidates

**Observed design fact.** Returning `out` causes bank candidates to be appended twice when the unit
already carries cargo adjacent to the shack. The r2 design names this Delta-B and says its inertness
is an argument to be measured, not an established fact. The accepted build review then records
`G-b = UNMEASURED`, because zero natural Delta-B states appeared in the fixture library.

**Unknown.** The G-d package contains no Delta-B census on the 240-game panel and no same-state
selection result for Delta-B states reached after Delta-A changes the trajectory. It therefore does
not exclude Delta-B as a contributor to later command differences. This uncertainty is one reason
not to attribute every cost to the persistent commitment.

### 3.4 Joint pair selection

**Observed.** Delta-A is sometimes selected, so the joint picker does not universally suppress it.
The P3 rows expose the selected command pair at the first divergence. The earlier P1/P2 programme
also established that pair compatibility and wait tie-breaking materially affect selected commands.

**Unknown.** The G-d package does not record, for each changed game, the candidate lists, pair scores,
rejected alternatives, or whether a different partner choice made the replant transaction useful or
harmful. Joint selection is therefore part of the causal chain but not separately identified.

### 3.5 What is actually proved about failure

The strongest justified causal statement is narrow:

> Allowing previously discarded replant `PICK` candidates through the existing fallback changes
> real command streams at turn 100 and, under the existing stateful bot and selector, violates the
> frozen orchard-inertness rule in five locked-panel games.

The following broader statement is **not** proved:

> Persistent regeneration commitment causes 73 real liveness regressions.

The observed P4 count includes future-dependent classification of pre-divergence windows, Delta-B
was not measured, joint selection was not decomposed, and G-e never measured progress.

## 4. Strategy verdict

Trying to cure every revealed problem in one patch is the wrong objective. Delta-A availability,
persistent commitment, Delta-B duplication, partner selection, orchard policy, and P4 temporal
semantics are distinct mechanisms. Combining them produced a small textual patch with a large,
uninterpretable behavioral surface.

| Rank | Next approach | Expected benefit | Blast radius | Measurement cost | Earliest decisive falsifier |
|---:|---|---|---|---|---|
| 1 | **Isolate Delta-A as an option-only design.** Preserve only the specifically formed replant `PICK`; do not return the whole prior list, do not create duplicate bank candidates, do not add persistent commitment, leave pair selection unchanged, and exclude orchard-eligible states to remain P3-clean. | Medium-high relative to cost: it tests the only newly discovered option with measured natural reach. | Low if the allowed candidate-list delta is exact. | Low-medium. | The source/design cannot make the candidate-list delta exactly one preserved `PICK`; the `PICK` is not legal/selected in a same-state decision; or any orchard-eligible command changes. |
| 2 | **Only after rank 1 shows useful progress, design a bounded replant transaction.** Give commitment explicit success, timeout, cancellation, and ownership rules instead of routing indefinitely through the existing generic commitment. | Medium: may turn a one-tick option into completed work. | Medium: stateful and cross-turn. | Medium. | No harvest/bank/employment before the declared timeout; commitment changes an unrelated unit; or a post-divergence P3/P4/routing regression appears. |
| 3 | **Retire the replant cure family and redirect to capability-aware resource/work ownership if rank 1 has no value.** Treat anti-benching legality as an invariant, not the whole architecture. | Potentially high, but uncertain. | High. | High. | A read-only prevalence/value audit shows the discarded replant opportunity is rare, sterile, or unrelated to durable work; then more regeneration patches are not justified. |

A separate evidence-tool charter should examine P4's treatment of temporary terminal intervals followed
by work reactivation. That is not a way to waive r2's failure and should not be mixed into a bot cure.
It is needed so future reactivation policies are not assigned pre-divergence "new liveness" costs
without an explicit semantic decision.

## 5. Recommended next hour

### Plain-language task

**Write a read-only causal-split design memo that isolates the replant `PICK` option from persistent
commitment, duplicate bank candidates, joint pair selection, and P4 temporal classification before
any new candidate is authorized.**

### Exact inputs

1. `agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35:claude_1/picker2/phase3-generator-route-2026-08-20.md`
2. `agent/claude_1@09ed550f91936818425ad2611c1b875531f32a35:claude_1/picker3/phase3b-design-proposal-r2-2026-08-22.md`
3. `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:claude_1/picker2/candidate-door1-p1p2.rs`
4. `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:claude_1/picker3/candidate-door1-p3b.rs`
5. `agent/claude_1@e6cb7523d87d4da02e6f81406d572e3e83e4cf10:claude_1/pipeline/fuzz_panel.py`, functions `work_remaining`, `live_horizon`, and `eval_p4`
6. `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/reviews/pair-selector-phase3b-build-review-2026-08-23.md`
7. `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/picker3/results/gd-door1-panel-2026-08-23.md`, especially `m035`, `m065`, `m074`, `m104`, and `m114`
8. `agent/codex_1@35d569f2b78c90dd7c15b46183376cc95efa7196:codex_1/picker3/results/gd-door1-decomposition-2026-08-23.json`

### Required output

One Markdown design memo containing:

- a causal ledger with one row each for Delta-A, persistent commitment, Delta-B, joint selection,
  P3, and P4; columns must be `observed`, `deduced`, `hypothesized`, and `missing evidence`;
- an exact future **design contract**, not code, for a Delta-A-only intervention: the only allowed
  candidate-list difference, explicit absence of persistent commitment and duplicate bank rows,
  unchanged selector, and orchard-inert scope;
- a table of the five direct P3 games and at least the `m035` pre-divergence P4 counterexample;
- the future measurement matrix and earliest falsifiers, clearly labelled as unexecuted.

### Stop rule

If the pinned source semantics do not permit Delta-A to be specified independently of commitment or
Delta-B, record **not isolatable** and stop. If a causal link is absent from the existing artifacts,
mark it **unresolved** rather than inferring it. Do not build a candidate, run a panel, change P4,
open a TestSession, submit, or touch Arena state.

## 6. Final verdict

**`RESULT_VALID_BUT_CAUSAL_CLAIM_UNPROVEN`.**

- The exact 35 -> 115 frozen-gate result stands.
- r2 remains rejected; five direct P3 violations are independently decisive.
- The full rerun validates the observation packet and outcome decomposition, but not the missing
  per-game causal diagnosis.
- The 73 new P4 labels cannot safely be read as 73 demonstrated candidate-caused stalls during the
  named windows; `m035` proves that at least one new P4 interval ends before the first command
  divergence and is classified through later trajectory state.
- The replant-option hypothesis remains scientifically open because G-e was correctly unrun for
  qualification and no isolated Delta-A/no-commitment/no-Delta-B arm exists.
- The best next move is a read-only causal split and a narrow option-only design contract, not a
  combined repair and not an Arena action.
