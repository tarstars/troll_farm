# Adversarial review — acceptance-gate architecture revision

Date: 2026-08-08  
Reviewer: `chatgpt_1`  
Task: `20260808-phase1-work-allocation`, item 5 review  
Reviewed artifact: `local_claude_1/gate-architecture-revision-2026-08-08.md`  
Reviewed artifact blob: `289dc25f10a254784bff2b3c3e0d147bad6b4238`  
Allocation correction blob: `42605cd0c7036cefb78e37c6d700231ac9e4b72f`  
Boundary: committed-blob/adversarial review; no gate, detector, candidate, host or Arena edit.

## Verdict

**`REVISION_REQUIRED`, with most high-level architecture accepted.**

The revision resolves the central AR-1…AR-9 contradictions:

- it introduces an honest `GATE_UNREADY` verdict;
- restores D-1 and D-4 to raw-zero acceptance effects;
- removes candidate-selected tiers and runtime parent-relative waivers;
- adopts a frozen calibration corpus and two-sided acceptance test;
- requires transitive provenance closure;
- separates games from episodes;
- refuses to make D-9 report-only merely because its current predicate is defective.

The two design choices the author explicitly asked me to attack are mostly sound:

1. **A trustworthy positive can precede per-detector incompleteness in verdict precedence.** A
   candidate with one independently established defect is blocked even if another property remains
   unknown. This is logically valid, provided global instrument prerequisites are ready and the
   result reports incomplete coverage rather than pretending the whole gate was fit.
2. **No generic waiver mechanism is preferable to an operable waiver ledger under the current
   owner rule.** An owner exception must become a new versioned gate contract, not an ad-hoc
   runtime episode exemption.

The draft nevertheless remains unadoptable because it conflates a hard acceptance rule with
instrument validity, defines validity at detector rather than clause/semantic-predicate level, and
prematurely calls the retained D-9 clauses ordinary validated blockers even though both committed
tests and the measured floor never execute them.

## Reviewed supporting evidence

- `claude_1/banana-restoration-r2/test_trace_detectors.py`, blob
  `ffe2923caaa45e6fb7dc3435c0988d33e0364916`;
- `claude_1/banana-restoration-r2/trace_detectors.py`, blob
  `3e4e3e95c40be5aa2a6e688b18fc54cf75093114`;
- D-9 execution-review message
  `coordination/messages/claude_1/20260808T113000Z-20260807-d9-calibration-execution-review.md`,
  blob `2c673264c6d1ee8fa8360cc6af64097c513c0b14`;
- original AR-1…AR-9 review, blob
  `c4e170f0cca40f20b3b6594db94315f01af6df46`.

I did not execute the private-repository suite. The D-9 execution facts below are explicitly
Claude's committed execution result; the test-coverage findings are directly visible in the exact
committed test blob.

---

## GAR-1 — D-1/D-4 must be absolute **after** instrument validation, not outside it

Section 5 says D-1 and D-4:

> do not enter detector states … One episode is `BLOCK`.

The first half is unsafe. The owner rule binds candidate behaviour: a genuine D-1 or D-4 episode
is an unconditional block and cannot be waived, compared to the parent or tolerated. It does not
make the detector implementation infallible.

If D-1 or D-4 is parsed incorrectly, uses a wrong state transition, or has a refuted semantic
predicate, the gate must not issue a candidate verdict from it. Otherwise the architecture repeats
D-9's exact failure with higher priority: a defective detector can permanently block every
candidate because it has been placed outside readiness.

Required rule:

```text
D-1/D-4 acceptance effect: absolute raw zero, no waiver, no comparison.
D-1/D-4 instrument requirement: implementation-valid AND calibration-valid.
If instrument validity is absent/refuted: GATE_UNREADY.
If valid and one episode fires: BLOCK.
```

They may be outside comparative tiers and waiver machinery; they may not be outside instrument
validation. This is a blocking architecture correction.

## GAR-2 — validity must be per clause/semantic branch, not per detector name

The draft's current classification marks D-9 implementation `validated` because the repository
contains a trigger and near-miss for D-9. The exact test file shows both tests call
`td.detect_d9(tr)` with one argument and exercise only `banana_before_train`:

- trigger: pre-TRAIN PICK BANANA;
- near miss: candidate TRAIN occurs before PICK;
- no `parent_commands` are passed;
- `train_late`, `train_missing`, and `train_stats_differ` do not appear in the test.

The proxy clause is precisely the clause being retired. After retirement, every remaining D-9
clause has zero committed test exercise.

Claude's independent runtime probe reaches the same result from a different axis: the parent emits
no TRAIN in the measured 60/60 games, so `p_train` is never set and the paired block never runs.
The package therefore has neither implementation nor runtime calibration evidence for the retained
clauses.

The frozen validity manifest must enumerate semantic branches, for example:

```text
D-9/train_late
D-9/train_missing
D-9/train_stats_differ
```

Each branch gets its own positive trigger, near-miss, oracle truth and evaluability status. Overall
D-9 is active only when every required branch is ready or the contract explicitly defines a branch
as not applicable. A detector-level `VALIDATED` boolean is too coarse.

## GAR-3 — the two-axis model needs a formal state product and independent truth labels

The distinction between implementation validity and calibration validity is correct. The machine
contract does not yet define their states or composition.

At minimum each semantic branch needs:

```text
implementation: VALIDATED | REFUTED | UNPROVEN
calibration:    VALIDATED | REFUTED | UNPROVEN | NOT_APPLICABLE
```

Recommended composition:

- either axis `REFUTED` → branch `DEFECTIVE`, gate `GATE_UNREADY`;
- either required axis `UNPROVEN` → branch `UNPROVEN`, gate cannot ACCEPT;
- `NOT_APPLICABLE` only under a frozen, machine-checkable precondition;
- branch active only when both required axes are `VALIDATED`.

More importantly, a detector's own trigger/near-miss pair proves implementation conformance to a
specification only if the expected truth is established independently. A fixture built from the
same predicate can faithfully test the wrong predicate. D-9 is the worked example.

The calibration corpus therefore needs, per branch:

- an independent world-state oracle or manually frozen truth label;
- the evidence path and hash for that truth;
- a positive case, a neighboring negative case and, where relevant, an unevaluable case;
- proof that the detector code is not reused to manufacture the expected label.

Silence on the current parent is not by itself positive calibration validity unless the property is
independently known absent. The prose claim that zero floor episodes proves D-2/D-3/D-7/D-8 defects
are absent is therefore too strong until item 4 audits the contracts and truth labels. It is
consistent evidence, not yet a validated semantic conclusion.

## GAR-4 — D-9 is not resolved after proxy retirement; it becomes `UNPROVEN`

Section 7 says to retire the proxy and keep the paired clauses, “after which D-9 is an ordinary
blocker requiring the same two-sided validation as any other.” The direction is correct but the
implied current status is not.

After retirement:

- all retained clauses have zero test coverage;
- the current floor does not exercise their precondition because the parent does not TRAIN in the
  measured games;
- the semantics for “parent never TRAINs” are not frozen;
- no positive paired displacement fixture exists.

D-9 must therefore be classified `UNPROVEN` immediately after the edit. It becomes an active
ordinary blocker only after purpose-built parent/candidate traces exercise late, missing and
different-stat TRAIN outcomes and their near misses. Until then the whole required blocker set
cannot ACCEPT.

The architecture should also require explicit per-game evaluability:

- parent TRAIN exists → paired clauses evaluable;
- parent TRAIN absent → frozen `NOT_APPLICABLE` or `UNPROVEN` rule, never accidental PASS.

## GAR-5 — evaluation order is acceptable only as verdict precedence, not diagnostic short-circuit

The draft intentionally orders a validated positive before an unrelated unready blocker. I accept
the logic with three conditions.

### Global readiness precedes every candidate verdict

Provenance and floor drift are listed, but the global set must also include the frozen validity
manifest, parser/referee integrity, calibration-corpus truth labels and result-schema version. A
failure in a shared foundation can invalidate the supposedly positive detector too; it must yield
`GATE_UNREADY` before BLOCK.

### All checks still run and are reported

After global readiness, the implementation should collect all valid findings and all unready
required branches before selecting a verdict. `BLOCK` may have precedence, but evaluation must not
stop at the first positive. Otherwise a known defect hides measurement debt and the next candidate
repeats the same surprise.

### BLOCK must carry coverage status

A partially ready result may truthfully say:

```text
verdict: BLOCK
known_defects: [...]
coverage_complete: false
unready_required_branches: [...]
```

It must not say or imply “the instrument is fit” without qualification. The verdict means “at
least one defect is established,” not “the full candidate was evaluated.” ACCEPT remains possible
only with `coverage_complete: true`.

With these additions, positive-before-unknown is sound and useful.

## GAR-6 — floor drift requires a full normalized violation manifest

The draft requires floor drift to abort but does not freeze what constitutes equality. Counts are
insufficient for the same reason identified in AR-5 and in the disputed D-9 `118 -> 46` result:

- one episode can be replaced with a different signature at the same count;
- severity or interval length can grow;
- P4 or another property may block without appearing in `detector_counts`;
- games and episodes can be conflated.

The floor manifest must contain the normalized multiset of **all** blocking and readiness findings,
including non-detector properties, keyed by map/seat/property/detector/branch/signature and
multiplicity. Drift compares that manifest byte-for-byte or by a versioned canonical
normalization. Aggregate counts remain report fields only.

When detector semantics change deliberately, the calibration-corpus version and expected floor
manifest change together through a reviewed contract revision; they are never silently
rebaselined.

## GAR-7 — no generic waiver mechanism is accepted, with one wording correction

I accept the choice to specify no waiver ledger. It is stricter than AR-4 but compatible with the
owner's current raw/absolute ruling and simpler to audit.

The sentence allowing a later owner ruling to name exact episodes should not create an informal
side channel. If the owner changes the rule, the change must produce:

- a new versioned, hash-pinned gate contract;
- explicit scope and causal rationale;
- new positive and negative controls;
- independent reviews;
- visible debt semantics where applicable.

Until that new contract is adopted, the current gate has no waiver path at all. Do not implement a
dormant schema or parse exception messages speculatively.

## GAR-8 — two-sided test accepted, but “intended detector” must mean intended branch and oracle

The current parent may be expected to BLOCK; a repaired reference must ACCEPT; a deliberately
broken descendant must be blocked by the intended detector. This resolves AR-3.

Strengthen the last step:

- the broken descendant must differ only by the frozen mutation under test;
- the intended semantic branch must fire with the oracle-expected signature;
- no unrelated earlier blocker may satisfy the test;
- a near-miss descendant must remain accepted;
- source, mutation and result hashes must be embedded.

This prevents a broken descendant from “passing” the two-sided test merely because the gate blocks
for a neighboring defect.

## GAR-9 — provenance closure accepted; add truth and schema dependencies

Section 8 is directionally complete and resolves AR-9. Add to the mandatory dependency closure:

- the validity-state manifest;
- branch-level contract and oracle truth-label files;
- canonical episode normalization/schema code;
- result JSON schema/version;
- the owner-frozen I-30 bound once item 6 is implemented.

Environment version strings are evidence, not substitutes for hashing actual executable inputs
where available.

---

## Required revision checklist

1. Keep D-1/D-4 raw-zero and waiver-free, but place their detector implementations under the same
   readiness requirements as every other instrument.
2. Replace detector-level `VALIDATED` with a branch-level two-axis state matrix.
3. Add independent truth labels/oracles to the calibration corpus.
4. Mark post-proxy D-9 `UNPROVEN`; add paired-clause positive, near-miss and no-parent-TRAIN cases.
5. Treat evaluation order as verdict precedence after global readiness; execute/report all checks
   and expose `coverage_complete`.
6. Freeze the full normalized all-property floor manifest, not detector counts.
7. Keep the gate waiver-free; any future owner exception is a new reviewed contract version.
8. Strengthen the broken-descendant test to target one semantic branch with a near-miss control.
9. Add validity, truth, normalization, schema and I-30-bound inputs to provenance closure.

## Final disposition

| architecture choice | review result |
|---|---|
| three-verdict lattice | **ACCEPT** |
| candidate-independent frozen calibration corpus | **ACCEPT_WITH_REVISIONS** |
| D-1/D-4 raw-zero acceptance effect | **ACCEPT** |
| D-1/D-4 outside instrument validity | **REJECT** |
| positive BLOCK before unrelated unknown | **ACCEPT_WITH_CONDITIONS** |
| no generic waiver ledger | **ACCEPT** |
| detector-level two-axis classification | **REJECT — must be branch-level** |
| D-9 ordinary blocker immediately after proxy retirement | **REJECT — `UNPROVEN` first** |
| two-sided reference/broken test | **ACCEPT_WITH_REVISIONS** |
| transitive provenance closure | **ACCEPT_WITH_REVISIONS** |

The revision is close in governing principles but still has machine-contract gaps capable of
recreating false blocking. It should be revised before implementation or adoption.
