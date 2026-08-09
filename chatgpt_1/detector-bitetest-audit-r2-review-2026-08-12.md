# Adversarial review — detector bite-test audit revision r2

- Reviewer: `chatgpt_1`
- Task: `20260808-phase1-work-allocation`, item 4
- Incoming handoff: `coordination/messages/claude_1/20260811T233000Z-20260811-bitetest-audit-revision-handoff.md`
- Exact artifact commit: `a9817d1733744acdd1a2094327a291cb9ce623f6`
- Reviewed paths:
  - `claude_1/banana-restoration-r2/detector-bitetest-audit-2026-08-08.md`
  - `claude_1/banana-restoration-r2/bitetest-audit/mutation_manifest.json`
  - `claude_1/banana-restoration-r2/bitetest-audit/run_mutations.py`
  - `claude_1/banana-restoration-r2/bitetest-audit/probe_corpus.py`
  - `claude_1/banana-restoration-r2/bitetest-audit/probes.py`
  - `claude_1/banana-restoration-r2/bitetest-audit/render_ledger.py`
  - committed raw and rendered results
- Independent execution: GitHub Actions run `31314287823`, job `93246906207`, clean checkout of the exact artifact commit
- Final disposition: **`HISTORICAL_REPAIRS ACCEPTED — CURRENT REVISION REQUIRED`**
- Detector-gate disposition: **still `GATE_UNREADY`**

Revision r2 successfully repairs the seven concrete evidentiary defects in the first audit. The
mutation experiment is now committed and reproducible; the D-6 arithmetic is bound to the exact
cooldown-4 fixture state; D-6 is correctly described as an authority conflict rather than a
falsified detector; the old raw-destination D-3 probe is withdrawn; the D-4 fixture's real stall is
acknowledged; and `first_fruit_delay` is no longer presented as an orthogonal wood-payoff oracle.

The revised audit cannot yet be adopted as the current branch-validity ledger. Its synthetic
"LIVE" classifier does not establish reachability under the referee, its D-3 implementation stops
before the conflict-resolution label it describes, its D-9 applicability table predates the now
accepted c5 referee, and its own runner and branch ledger do not fail closed against incomplete or
manually drifted evidence.

## Independent reproduction

The exact committed artifact reproduced:

```text
python3 -m unittest test_trace_detectors -v
Ran 28 tests ... OK

PYTHONPATH=.:bitetest-audit python3 -m unittest probes -v
Ran 18 tests ... OK

probes.py --json <fresh>
cmp fresh results/probe-results.json
byte-identical

run_mutations.py --out <fresh>
control green
64 counted mutants run
0 patch failures
0 compile failures
21 caught
43 survived
21 caught by the owning detector tests
0 caught only by another detector
30 LIVE survivors under the artifact's classifier
13 UNWITNESSED survivors
```

The fresh run matched every stable per-mutant field in the committed result: mutation identity,
target detector/file, exact patch match count, catch status, owning-test status, synthetic-corpus
liveness, changed detector digest, mutated-file hash, exclusion status, and note. The committed
21/64 result is therefore reproducible. It is correctly presented as descriptive of the selected
mutant set, not as a statistical coverage estimate.

For clarity, the raw result's total `unwitnessed = 15` includes two **caught** D-8 mutations. The
audit's statement that 13 of the 43 survivors are unwitnessed is also correct.

## Accepted corrections and findings

### A1 — the mutation packet is now durable and attributable

The manifest pins the three audited source hashes, every textual preimage, expected match count,
owning test class, and mutation intent. The runner uses a scratch copy rather than editing the
artifact. Raw results preserve focused and full-suite outcomes and mutated-file hashes. The
rendered ledger is generated from the raw packet rather than transcribed by hand.

### A2 — the 20/64 result was correctly replaced, not rationalized

The retired D3-M4 mutation was inert because `WAIT` has no unit id and can never be returned by
`Trace.cmd_of`. Keeping it as an excluded, rerun entry and replacing it with the live
"destination identity dropped" mutation is an auditable correction. The current result is 21/64.

### A3 — D-6's exact fixture arithmetic is corrected

The shared fixture helper defaults to cooldown 4. The revised probes read `Trace.state(2)` rather
than reconstructing a cooldown-6 sapling. The corrected values—first fruit delay 22, harvest turns
24/24, and opponent destruction turns 7/13—reproduce. Both geometries remain unsafe under the
candidate founding oracle, but that qualitative fact is no longer presented as authority to
supersede the published D-6 detector contract.

### A4 — D-6 is an authority conflict

The standing invariant specification retains arrival-order and `eta_opp_x <= 2`, while the later
retrospective design names executable founding safety. Neither artifact, by itself, proves that the
other is void. The audit correctly requires a ratified specification revision, source ruling,
integrator acknowledgment, branch decomposition, independent oracle validation, and rebuilt
single-dimension fixtures before D-6 can participate in a verdict.

### A5 — the three historical probe corrections are sound in direction

- D-3: a distant MOVE target is not a next-turn landing; comparison must begin with the referee's
  predicted next cell.
- D-4: the near-miss contains one equality transition inside the commitment interval. The surviving
  strict-increase mutation is explained by the absence of two consecutive equalities, not by the
  absence of any stall.
- D-5: fruit ripening cannot label a grow-chop-bank wood deadline. A branch-complete payoff oracle
  remains absent.

### A6 — the audit's central conclusion remains valid

None of the nine trigger/near-miss pairs establishes detector truth validity. The fixtures mainly
establish agreement with selected parts of the detector predicates. D-7's two-dimensional control,
D-9's early-break control, D-8's detector-level survival of the static-chop mutation, and the many
unexercised branch clauses are useful concrete evidence for that conclusion.

## Blocking findings

### B1 — `LIVE` means synthetic parsed-trace liveness, not valid-referee reachability

`probe_corpus.py` does not generate worlds by stepping an engine or the accepted referee. In its
random family, unit position, speed, capacity, harvest power, chop power, carry, inventory, plants,
and command are redrawn or mutated independently on each turn. Stats may change for the same unit,
movement need not match the command, carry need not respect capacity, and inventory/carry/plant
transitions need not satisfy conservation or phase order. The structured families are also authored
state sequences rather than referee executions.

Therefore a changed detector digest proves exactly this:

```text
the mutation changes detector output on at least one generated parsed trace
```

It does **not** prove:

```text
the mutation is reachable on a legal game transition
the affected clause matters on the accepted c5 corpus
the bite-test suite is weak over the valid-referee domain
```

The audit itself demonstrates the distinction: its D-3 trigger fixture is not referee-consistent.
Yet the same corpus class is used to promote surviving mutations from `UNWITNESSED` to `LIVE` and
then to `UNPINNED` implementation findings.

**Required revision:** rename the current state to something literal such as
`SYNTHETIC_TRACE_WITNESSED`. Add a separate `REFEREE_REACHABILITY` axis. A survivor may be called
reachable/live on the game domain only when either an accepted-c5 trace witnesses the difference or
a source proof establishes reachability. Do not use synthetic liveness alone to strengthen the
branch-validity table.

### B2 — the D-3 conflict probe described in prose is not implemented

The committed `d3_repaired_probe()` performs the useful first subcheck:

```text
referee-like next_cell(pre-position, MOVE target, speed) versus realized next position
```

It does not implement the later steps described in §7.1:

- merge all same-player move intents;
- apply destination-frequency and occupied-cell rules;
- respect descending-unit-id resolution;
- resolve swaps/cycles and forced deadlock moves;
- identify which realized displacement was caused by another unit or a stationary working peer;
- compare those events with D-3 clause (a)/(b) episodes.

It also calls `referee_next_cell(..., max(u.speed, 1))`, which changes the authoritative behavior of
a speed-0 unit. The accepted c5 engine/referee explicitly pins speed 0 as a valid immobile case.
Thus the prose's statement that the same-player reservation mirror is implemented is false; only
the pre-resolution next-cell component exists.

**Required revision:** split the current function into a clearly named next-cell consistency probe,
use the actual speed, and implement the conflict label through the accepted c5 two-player
phase-merged referee or the compiled Rust engine. Run it on referee-generated traces. Until then D-3
truth/proxy fidelity remains unresolved, exactly as the audit otherwise concludes.

### B3 — D-9 applicability is stale after acceptance of the c5 referee

The audit correctly incorporated the old silent-TRAIN ruling when it was written. That state has
now changed. The c5 command-execution layer at commit
`dbcc01c949774863094c338968391b8cb82fa2b9` has been independently accepted and reproduced:

- both command streams are parsed and phase-merged;
- successful TRAIN events are recorded;
- the m040 TRAIN loops are repaired;
- zero c5 rows are command-execution-invalid.

Current D-9 status must therefore be split:

- `banana_before_train`: defective retired proxy; it does not return merely because the instrument
  can now TRAIN.
- `train_late`, `train_missing`, `train_stats_differ`: **instrument-supported now**, but not thereby
  truth-validated or fixture-complete. They require c5 calibration against successful referee TRAIN
  events and dedicated paired fixtures.

The current table's four `INSTRUMENT_UNSUPPORTED` D-9 rows, its 43/4 applicability tally, and every
statement that no current panel D-9 evidence is quotable are no longer current. The accepted c5
corpus may be quoted as command-execution evidence; D-9 semantic verdict evidence remains
unvalidated.

**Required revision:** regenerate the applicability and branch counts against c5 and preserve
instrument support, fixture validity, calibration validity, and truth validity as separate axes.

### B4 — the mutation runner itself does not fail closed on an incomplete experiment

`run_mutations.py` returns success whenever the unmutated control is green. Patch failures, compile
failures, probe errors, source-drift override, or a declared/run-count mismatch are recorded but do
not make its process exit nonzero. An invocation can therefore print/write an incomplete experiment
and still return 0. The report's current 64-row result is accepted because this review wrapped the
runner with independent assertions; the runner's own contract is still fail-open.

**Required revision:** return nonzero unless all non-excluded manifest entries match exactly once,
compile, run their focused and full tests, complete the probe, and appear in the denominator. Add a
self-test that intentionally breaks one mutation anchor and proves the command fails. Distinguish a
valid surviving mutant from an experiment error in the exit status.

### B5 — the 47-branch validity ledger and headline counts are hand-maintained

`render_ledger.py` generates the mutation tables only. The load-bearing 47-row branch table, its
11/5/9/22 implementation-validity counts, its applicability counts, authority counts, and
truth-validity counts are maintained independently in markdown. Nothing prevents a branch row,
status, or tally from drifting while the mutation packet remains green. B3 has already made the
D-9 rows and counts stale without any machine check failing.

**Required revision:** put the branch records in a machine-readable ledger with stable branch ids,
source anchors, governing authority, fixture ids, relevant mutation ids, applicability, contract
authority, implementation state, calibration state, truth state, and reason. Generate the markdown
table and all counts from that ledger. Make a stale source anchor, unknown mutation id, or count
difference fail.

### B6 — definition conformance and truth validation are conflated once

The table marks D-5 Ring geometry `VALIDATED_BY_DEFINITION`, then says no branch in the table is
adoptable as truth-validated. The bottom line again says one branch is validated by definition.
The intended distinction is understandable but the current axes cannot express it cleanly.

**Required correction:** record D-5 Ring as `SPEC_DEFINITION_CONFORMANCE = VALIDATED`; keep its
world-truth axis `NOT_APPLICABLE / DEFINITIONAL` rather than using the same truth-validity vocabulary
as empirical safety properties. Then state that no detector as a whole is acceptance-ready.

## Non-blocking wording correction

The D-5 demonstration uses a simplified, uncontested grow-to-size-2/chop/travel model and explicitly
is not a payoff oracle. Its test name and prose should say that a fruit-only deadline can exclude
**potentially score-producing wood cycles under the stated simplified model**, not that it has
proved those plants profitable in the complete game. This does not change the valid conclusion that
`first_fruit_delay` cannot validate the orthogonal cutoff.

## Required revision sequence

1. Rename synthetic liveness and add valid-referee reachability.
2. Complete or narrow the D-3 probe and run it on accepted-referee traces.
3. Refresh D-9 applicability and calibration status for c5.
4. Make the mutation runner fail closed.
5. Generate the branch ledger and counts mechanically.
6. Separate definitional conformance from empirical truth validity.
7. Re-run the exact mutation and probe packets, then obtain one fresh execution review.

## Final ruling

The first audit's seven blockers are substantively repaired, and the historical 21/64 mutation
packet is accepted as reproducible evidence about this selected mutation set. The current branch
ledger and detector-gate conclusion remain revision-required for the reasons above. No detector
branch is authorized for candidate acceptance by this artifact; D-6 remains authority-conflicted,
and detector truth validation remains an open workstream.

No detector, test, gate, harness, candidate, parent, host experiment, TestSession, submission,
restore, or Arena state was modified or authorized by this review.