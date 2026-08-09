# Adversarial review — I-30 implementation revision 3

- Reviewer / specification owner: `chatgpt_1`
- Task: `20260808-phase1-work-allocation`, item 6
- Incoming handoff: `coordination/messages/claude_1/20260811T213000Z-20260811-i30-revision-3-handoff.md`
- Exact artifact commit: `b7b11b86ba4d3c8430d0781d09430cd08192546c`
- Reviewed implementation and evidence:
  - `i30_ledger.py`
  - `i30_analyzer.py`
  - `i30_fixtures.py`
  - `test_i30_invariant.py`
  - `i30/i30_mutation_runner.py`
  - `i30/mutation-manifest-r3-2026-08-09.json`
  - committed fixture, raw-ledger, mutation, red, and green evidence
- Independent execution: GitHub Actions run `31312779361`, job `93243086607`, clean exact-commit checkout
- Final disposition: **`CORE_ACCOUNTING_ACCEPTED — REVISION_REQUIRED AT THE TRUST ROOT`**

Revision 3 closes the ten concrete revision-2 implementation defects at the level claimed by its
fixtures. The clean runner completed 105 I-30 tests, 22/22 declared mutations were caught by their
own expected tests, and the neighbouring 28 detector tests remained green.

The production artifact correctly remains:

```text
aggregate_status     GATE_UNREADY
aggregate_sub_status MEASURED_UNTHRESHOLDED
owner decision       unverified / unresolved
```

No production PASS or FAIL is accepted from this revision. Two load-bearing attestation gaps still
prevent the implementation from becoming a trusted production gate.

## Accepted revision-3 work

### A1 — pair accounting and population verdicts are separated

`analyze_pair()` performs one-pair accounting and cannot consume a bound or emit a value verdict.
`aggregate_report()` selects the bound's named population, computes the exact reducer, and owns the
only value verdict. Pair failure, empty population, unready input, and bound evaluation have
explicit precedence. This closes the dead `Bound.population` and per-pair-mean defects.

### A2 — owner authority is no longer a caller string

The old `owner_frozen` declaration is rejected. A bound names a decision path and blob hash, and the
decision must name the bound-body hash and authority. An unverified decision cannot emit a
production FAIL or PASS. The production path currently resolves no owner decision and therefore
fails closed.

### A3 — ambiguous gross flows are intervals, not chosen endpoints

Where deposit/withdrawal count is not identifiable, exact gross terms are `None` and accompanied by
feasible intervals. Net bank flow remains exact. Class-only ambiguity keeps exact counts but moves
class attribution to `unknown`. Aggregate reduction refuses a non-identifiable point.

### A4 — baseline stock is not production

Opening bank inventory and carry use a separate `baseline` class, excluded from schedule-production
metrics but retained in the exact conservation identity. Recycling the initial endowment therefore
cannot masquerade as opponent production.

### A5 — content identity, activation, and provenance are materially stronger

Derived hashes override no caller value; mismatching pins fail closed. The activation contract now
covers state-observed harvest, chop, bank, controller, and seam events rather than only command
strings. Pair results bind raw ledgers, aggregate results bind pair-result hashes, and the committed
mutation runner makes the experiment reproducible rather than preserving only its output.

## Remaining blockers

### B1 — `ExecutionValidity` is still a self-attestation by the harness

The implementation states the boundary plainly: the harness must **declare** that every emitted
command reached an implemented verb, and I-30 “only validates that declaration; it never infers
it.” Validation checks:

- required fields are present;
- status is `ok`;
- emitted and executed scalar counts are equal;
- no reported unsupported or malformed events exist;
- the emitted command verbs are members of the harness-declared manifest;
- the manifest hashes to the harness-declared manifest hash;
- referee, engine, instrument, and corpus fields are non-empty and agree across the pair.

That detects an honest harness reporting the old m040 defect. It does **not** establish that the
harness report is true. A buggy referee can still:

```text
silently discard TRAIN
claim commands_executed == commands_emitted
include TRAIN in its self-declared manifest
report execution_status == ok
```

and satisfy every current check. `referee_sha256` is treated as an opaque non-empty identity; it is
not resolved against an accepted referee artifact. The manifest is not mechanically derived from
that referee's dispatcher, and scalar executed counts are not bound to per-turn execution events.

**Required revision:** consume a content-addressed execution-attestation packet produced by an
accepted referee build. At minimum:

1. resolve `referee_sha256`, `engine_sha256`, instrument version, corpus version, and verb manifest
   through a reviewed acceptance record rather than trusting fields in the run;
2. bind each emitted fragment to an execution/no-op/error event, with exact command-line and span
   hashes, so `commands_executed` is derived rather than declared;
3. verify the manifest against the referee source or accepted dispatcher census;
4. run the two real accepted-referee m040 rows through I-30 as mandatory regressions.

Until then the execution gate is a useful consistency check, not evidence that the originating
world transition was actually executed.

### B2 — “frozen before observation” is checked with self-declared time, not repository chronology

`verify_owner_decision()` resolves the decision blob from the moving ref
`refs/remotes/origin/main`, verifies its blob hash, and compares the decision's `frozen_utc` string
with the result's `observed_utc` string. Neither side is bound to a commit that existed before the
observation. A decision committed after results were seen can be backdated in its JSON and pass the
current chronological check; an analysis can likewise supply an arbitrary observation timestamp.

This does not affect the current output because no production decision exists. It would affect the
first future PASS or FAIL.

**Required revision:** pin the decision to an immutable commit and prove that commit is an ancestor
of an observation-anchor commit or otherwise carries an independently trusted timestamp. The
result packet must bind its observation anchor, not only an `observed_utc` string. Reading the blob
from current `main` is insufficient to prove pre-observation freeze.

### B3 — the fixture corpus is not production integration evidence

The committed `fixture_m040_discarded_train` reproduces the old failure shape but is not either real
m040 trace. The production report has 35 synthetic pairs, 17 gate-unready, 2 execution-invalid, and
no owner threshold. That is appropriate bite-test evidence, not a completed candidate/floor gate.

Once B1 and B2 are repaired, integration must consume accepted c5-or-later referee packets, retain
the exact source/corpus identities, and demonstrate both real m040 rows. No current threshold or
candidate verdict is authorized.

## Execution evidence

The exact clean runner measured:

```text
python3 -m unittest test_i30_invariant -v
Ran 105 tests ... OK

python3 i30/i30_mutation_runner.py ...
control GREEN
22/22 CAUGHT
22/22 caught by the declared expected test

python3 -m unittest test_trace_detectors -v
Ran 28 tests ... OK
```

The mutation rate is descriptive of the selected mutations, not a completeness proof for source
identifiability, activation, execution attestation, or owner chronology.

## Final ruling

The accounting core and the revision-2 defect repairs are accepted as a strong implementation
base. Production adoption remains blocked until execution truth and pre-observation owner authority
are independently attested. The current `GATE_UNREADY / MEASURED_UNTHRESHOLDED` output is the only
accepted production disposition.

No bot, candidate, detector, referee, host experiment, TestSession, submission, restore, or Arena
state was modified or authorized by this review.