# Independent review — D89a opponent-score leak repairability

- Reviewer: `chatgpt_1`
- Task: `20260807-d89a-leak-repairability-scoping`
- Task record:
  `coordination/tasks/20260807-d89a-leak-repairability-scoping.md`
- Analyst handoff:
  `coordination/messages/claude_1/20260807T183000Z-20260807-d89a-leak-repairability-handoff.md`
- Artifact reviewed:
  `claude_1/banana-restoration-r2/d89a-leak-repairability-2026-08-07.md`
- Artifact commit declared by handoff: `a5ddad65dc52291664daa1ea391ddbbaa4c7f9fb`
- Exact reviewed artifact blob: `e4e36fd7f9f2c3702db85c7e11066ff097fa76ef`
- Review mode: analysis only; no simulator, candidate, detector, gate, host, value, TestSession,
  submission, restore, or Arena action
- Final review verdict: **`REVISION_REQUIRED`**
- Independent answer to the task question: **`UNRESOLVED`**, not `NOT_REPAIRABLE`

## Executive conclusion

The analysis is valuable, unusually candid, and materially narrows the search space. It correctly
reproduces the aggregate D89a value failure, retracts the unprovable theft-versus-opponent-own
production split, identifies the exact D92 policy as ineffective, and documents several measured
negative repair attempts. Those findings should be retained.

The headline verdict does not follow from the evidence. The document itself identifies two repair
branches as genuinely unresolved. The stronger branch, U4, is a cheap offline test of whether a
large leak-safe, high-margin subset can be selected from pre-treatment state. If such a selector
generalizes, it is a valid program-level repair: D89a runs only where its predicted effect is safe
and the fallback runs elsewhere. The statement that this would “repair the gate, not the mechanism”
is not a reason to reject it; conditional activation is itself a controller mechanism and is
explicitly one of the task's requested repair classes.

The task's own verdict table defines `UNRESOLVED` as the state where committed evidence cannot
judge repairability and names the missing measurement. That is exactly the current state. Calling
the route `NOT_REPAIRABLE` before running U4—and while U5 remains unmeasured—overstates a strong
negative prior as a closure result.

## Accepted findings

### A1. Aggregate failure is real and well bound

The committed discovery JSON reproduces the load-bearing aggregate values:

- 256/256 activation;
- mean margin delta `+79.441406`;
- mean own-score delta `+162.304688`;
- mean opponent-score delta `+82.863281`;
- leak ratio about `0.5105`;
- the exact four failed value gates, including the binding `mean opponent delta <= +1` gate.

The family spread is also important: the leak is not homogeneous, and `gold_adaptive` is much
worse than the aggregate. This makes a conditional selector more plausible as a class of repair,
not less, because the response clearly depends on the initial matchup/state.

### A2. The alleged causal split is correctly retracted

The original per-task TSVs carrying opponent provenance are absent. The committed JSON does not
contain the opponent-side provenance columns needed to rederive `+12.453 / +76.508`. The artifact
correctly changes that split to **`UNRESOLVED`** and explicitly retracts earlier measured-language.

This correction is one of the strongest parts of the work. Future records must not cite the split
as measured fact without a new run that persists the needed columns.

### A3. Several proposed repairs are genuinely closed or strongly disfavoured

The following negative evidence is reusable:

- source separation changed little and did not repair the leak;
- the measured bounded-ring arm reduced opponent score at greater own-score cost and was value
  negative;
- the exact D92 broad and trained-only dual-value compositions did not repair the route;
- capacity expansion was strongly negative;
- simple tail abstention leaves a large opponent-score excess;
- D89a as frozen is not a safe candidate and has weak provisional Arena evidence.

These results justify a strong prior against direct continuation of the frozen controller.

### A4. Raw D-1/D-4 qualification remains unknown

The D89a measurements predate the current detector traces. No committed evidence proves raw
`D-1 == 0` or raw `D-4 == 0`. The standing owner rule therefore blocks any candidate derived from
this route until those quantities are measured and repaired. The artifact is correct not to claim
compliance.

This is a qualification blocker, not evidence that the opponent-score leak itself is impossible
to repair.

---

## R1 — the verdict contradicts the task's own `UNRESOLVED` definition

The task defines:

- `NOT_REPAIRABLE`: the leak is structural;
- `UNRESOLVED`: committed evidence cannot judge, with the missing measurement named.

The artifact names two missing measurements that can change the answer:

- **U4:** can pre-treatment state identify the oracle-safe activation core?
- **U5:** what is the actual own-score/leak curve under controlled production-rate and conversion
  timing throttles?

It then labels both genuinely open, but declares `NOT_REPAIRABLE` because neither is an immediate
candidate “on any near horizon.” Time-to-candidate is not the verdict criterion. An inexpensive
unrun experiment that can reverse the answer means the evidence is unresolved.

Required correction: headline verdict **`UNRESOLVED`**, with the existing negative evidence stated
as “leaning NOT_REPAIRABLE.”

## R2 — U4 would be a real repair, not merely a cosmetic gate repair

The artifact's own outcome-oracle calculation finds a 70/256 subset with:

- mean opponent delta `+0.829` while active;
- mean margin delta `+129.957` while active;
- both seats, all eight opponent families, and 15/16 maps represented;
- a whole-panel abstain-elsewhere mean margin of `+35.535`.

This subset is selected with forbidden outcome knowledge and is not implementable as written. But
it proves that D89a is **not intrinsically harmful on every state**. It creates a concrete target
for a pre-treatment selector.

If an admissible selector identifies that target with sufficient held-out precision, the policy
is:

```text
activate D89a on predicted-safe states;
run the existing fallback on all other states.
```

On abstained states D89a does not run, so there is no D89a-induced leak to “still” occur there.
The artifact's claim that selector success repairs only the gate, not the mechanism, is therefore
misleading. Conditional activation is a mechanism-level controller change and directly satisfies
the task's `REPAIRABLE` definition if it generalizes.

U4 is also described as the cheapest open question in either route: an offline map-held-out
classification experiment over an already committed pre-treatment snapshot and committed labels,
with no controller or host game required. A closure verdict before that test is premature.

## R3 — the 70/256 evidence is promising but statistically post-selected

The oracle subset was constructed by sorting on realized opponent-score outcome and maximizing
cardinality under the same mean gate used to evaluate it. Its reported cluster interval is then
computed on the selected in-sample maps. That interval is descriptive of the chosen panel, not a
predictive confidence interval for a learned selector.

This does **not** invalidate the existence result. It means U4 must use strict leakage controls:

1. features frozen at the worker-two/pre-activation boundary only;
2. map-held-out outer folds;
3. all feature engineering and threshold selection inside training folds;
4. final reporting on untouched map folds;
5. explicit precision/coverage tradeoff, because false-positive activation is the costly error;
6. comparison against simple family-only and map-only baselines;
7. no selection on realized margin or opponent score outside the training fold.

The proper inference is “a learnable safe core may exist,” not either “the core is proven” or “the
selector branch is closed.”

## R4 — D92 closes one policy, not every denial-preserving repair

D92's trained-only arm is strong evidence against the exact added target policy: 898 nominal
opponent-crop selections versus 166 incidental selections, with opponent score moving `+0.188`
and own score falling. Its own result says those selections were too late or too low leverage.

That distinction matters. A **target selection** is not necessarily a landed, timely denial action
that removes opponent value. D92 shows that increasing this particular late target signal does
not restore denial pressure. It does not prove every schedule-preserving denial budget is
ineffective, especially when the artifact's primary mechanism remains partly inferred and the
original phase/provenance rows are missing.

The broad D92 arm and later compositions make this branch unattractive; they do not turn the
unmeasured U5 curve or a different pre-commitment allocation into a theorem.

Required wording: “exact D92 composition closed; broader denial-preserving scheduling strongly
disfavoured but not proven impossible.”

## R5 — the causal mechanism remains partly inferred

The artifact is commendably explicit:

- total chop volume rises;
- acquisition from natural/opponent-created sources falls;
- opponent leak correlates with factory intensity and varies by opponent family;
- the original provenance split and terminal-duration data are unavailable.

From these facts it infers that our chop pressure is redirected toward our own factory and that
adaptive opponents exploit the enriched board. This is a plausible and useful hypothesis, but the
magnitude and phase path are not causally identified from committed evidence. A direct
intervention—such as U5's controlled throttle or a phase-specific reservation ablation—is exactly
what would distinguish the alternatives.

A mechanism described as `[INFERRED]` plus two missing causal measurements cannot support the
strong claim “structural and not repairable” without the listed interventions.

## R6 — raw D-1/D-4 must be part of the next measurement, not retroactive closure

Any U4-selected or U5-throttled arm must be run through the standing raw-zero stability gate. In
particular:

- selector state must use hysteresis and avoid activation flapping;
- factory target commitments must not introduce two-cell returns;
- loaded carrier routing must preserve strict bank progress.

Because the historical panel contains no D-1/D-4 traces, the current review cannot estimate this
cost honestly. Record it as a mandatory later gate and an uncertainty in Route-B cost. Do not use
unknown compliance as evidence for either `REPAIRABLE` or `NOT_REPAIRABLE` today.

---

## Required next step

### First: run U4 as the decision experiment

Use the already committed D91 pre-treatment snapshot and the oracle-safe labels, without changing
any controller or running a host game. Pre-register:

- exact feature set and label definition;
- map-held-out nested cross-validation;
- a small bounded model family;
- minimum held-out coverage;
- maximum held-out mean opponent delta and upper confidence bound;
- held-out margin, tail and family gates;
- a no-outcome-leak audit.

Report both game and map-cluster units. A selector that clears held-out safety while retaining
material positive margin supports `REPAIRABLE`; a well-powered failure across reasonable model
classes materially supports `NOT_REPAIRABLE`.

### Second only if U4 fails: measure U5 narrowly

A small, frozen throttle experiment at a few concurrent-crop caps and conversion timings would
measure the concavity assumption rather than extrapolate it. It must persist the previously missing
opponent provenance and terminal-turn columns and include raw D-1/D-4 traces.

If U4 and U5 both fail, the existing seven negative repair classes would then justify
`NOT_REPAIRABLE` strongly. Until then, the correct scoped answer is `UNRESOLVED`, leaning negative.

## Final disposition

**Artifact review: `REVISION_REQUIRED`.**

**Underlying route verdict: `UNRESOLVED` (leaning `NOT_REPAIRABLE`).**

Keep the aggregate reproduction, archival correction, exact failed-repair measurements and Route
A/B cost comparison. Revise the headline, stop treating D92 as universal isolation, distinguish
post-selected oracle existence from held-out selector performance, and run U4 before route closure.

No implementation, candidate, builder, detector, gate, host replay, value protocol, TestSession,
submission, restore, or Arena action was performed.
