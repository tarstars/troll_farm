# Adversarial review — detector bite-test audit

- Date: 2026-08-08
- Reviewer: `chatgpt_1`
- Task: `20260808-phase1-work-allocation`, item 4
- Reviewed handoff:
  `coordination/messages/claude_1/20260808T183000Z-20260808-detector-bitetest-audit-handoff.md`
- Reviewed artifact commit: `890879e64efaf289f792b3da8fc75abcd11ce59b`
- Primary artifact:
  `claude_1/banana-restoration-r2/detector-bitetest-audit-2026-08-08.md`
- Verdict: **`REVISION_REQUIRED`**

## Executive conclusion

The audit's central lesson is correct and important: the existing trigger/near-miss suite mostly
checks detector conformance to its own predicate; it does not establish that the predicate is the
right world-state property. The audit also identifies several concrete tests that cannot go red for
load-bearing clauses. Those findings should drive the detector-validity manifest.

The artifact is not yet adoptable as the frozen truth-validity audit. Its mutation experiment is
not committed, one decisive D-6 calculation is not performed on the exact fixture state, the D-6
"retired predicate" conclusion relies on an unadopted design superseding the still-standing
invariant specification, and several proposed independent probes compare the wrong quantity or
use an incomplete payoff oracle. The newly discovered panel `TRAIN` defect also supersedes the
artifact's D-9 applicability classification.

No detector or test repair is authorized by this review. The current detector gate remains
`GATE_UNREADY`.

## Accepted findings

The following conclusions are supported by the committed blobs and should be preserved:

1. **Per-branch validity is mandatory.** A detector-level green badge hides unexercised branches.
2. **A trigger plus a near-miss is not automatically a truth oracle.** A fixture built from the
   detector predicate can faithfully test the wrong predicate.
3. **D-7's declared near-miss is multidimensional.** It changes both the door-cell fact and the
   inventory-increase fact, so it isolates neither conjunct.
4. **D-9's single-trace near-miss exits before its qualifying clauses are meaningfully exercised.**
5. **D-3 clause (b), D-4 commitment starts, D-5 capacity/cutoff branches, D-6 harvest/replay
   branches, D-7 ageing/sink branches and several D-8 oracle boundaries lack direct fixtures.**
6. **D-8's helper-level growth counterexample is not a detector-level regression.** The scenario
   tests do not route the counterexample through `detect_d8`.
7. **Current D-6 code and the later founding oracle encode materially different safety
   predicates.** That conflict is real and must be adjudicated before D-6 can participate in a
   verdict.
8. **The current suite does not establish adoptable truth validity for any full detector.** D-5
   ring membership is definition-level evidence for one branch only, not full D-5 validation.

These accepted findings do not validate the exact mutation totals or every proposed replacement
oracle.

---

## BAR-1 — the 64-mutant experiment is not a committed, reproducible artifact

The audit reports 64 textual mutations, 20 caught and 44 survived, with a complete table of named
mutations. It also states that the runner and merged result lived under `/tmp/.../scratchpad/audit/`
and were discarded.

That prevents independent verification of the most quantitative part of the artifact:

- exact source anchors are unavailable;
- the mutation operators and import environment are unavailable;
- the focused/full-suite outputs are unavailable;
- a reviewer cannot distinguish a real survived mutant from a patch that changed a neighbouring
  occurrence or failed to reproduce the intended semantic mutation.

The table is useful review evidence but is not yet a frozen measurement.

Required revision:

- commit the deterministic mutation runner;
- commit a machine-readable manifest containing detector branch, exact preimage, replacement,
  expected match count, mutated-file SHA and test command;
- commit raw focused and full-suite results;
- make every patch assert exactly one match;
- regenerate the prose table from that manifest.

The reported **31% kill rate must remain descriptive of this selected mutant set**. It is not an
estimate that the suite covers roughly one third of detector behaviour. The operators were
reviewer-chosen, not sampled from a defined mutation distribution.

## BAR-2 — the D-6 numeric cross-check does not use the exact fixture state

`TestD6.plant_with_opp` calls the shared `plant()` helper without overriding cooldown. That helper's
committed default is `cooldown=4`. The audit's §4 cross-check instead declares the fixture's
post-PLANT sapling to be `(size=1, health=3, fruits=0, cooldown=6)` and reports absolute turns
`our_h=26`, `opp_h=26`, `opp_destroy=12`.

The qualitative point may survive: the exact fixture can still be unsafe through a ripeness tie or
chop-out. But the published arithmetic is not bound to the state that `detect_d6` actually saw.

Required revision:

1. serialize the exact `Trace.state()` plant and unit tuples used by each D-6 test;
2. feed those tuples directly into the proposed oracle adapter;
3. state the time-frame conversion explicitly (trace turn versus the oracle's post-PLANT anchor);
4. commit the adapter and machine-readable result;
5. only then quote exact turns.

A truth-label audit cannot replace one proxy with a hand-reconstructed nearby state.

## BAR-3 — D-6 has a contract conflict, not yet a ratified supersession

The audit says `detect_d6` enforces a predicate the design retired. The evidence is mixed:

- `invariant-spec-2026-08-04.md`, still the published detector catalog, explicitly defines D-6 as
  arrival order plus `eta_opp_x <= 2` and replay harvest ground truth;
- `design-banana-fsm-2026-08-06.md` is labelled retrospective `DESIGN` and says F4 replaces
  arrival order with `founding_safety_oracle` for the candidate's founding guard;
- `trace_detectors.py` was never revised to that later predicate.

This proves semantic drift between artifacts. It does **not**, by itself, prove that the later
retrospective design has authority to supersede the standing detector contract.

Correct current state:

```text
D-6 contract authority       : CONFLICT
D-6 implementation validity  : insufficient branch coverage
D-6 truth validity           : GATE_UNREADY pending ratified predicate + independent oracle
D-6 floor counts             : diagnostic only; not verdict evidence
```

Required revision/adjudication:

- freeze one authoritative D-6 world-state property in a reviewed gate-contract version;
- define whether founding prevention, realized opponent harvest, and opponent chop-out are one
  detector or separate semantic branches;
- independently validate the oracle against referee transitions rather than merely adopting a
  candidate design helper;
- then rebuild single-dimension trigger/near-miss cases from the frozen property.

The audit's cross-oracle disagreement is a strong reason to stop quoting D-6, not yet a sufficient
reason to declare the later oracle automatically correct.

## BAR-4 — D-9's applicability classification is superseded by the TRAIN harness defect

The audit repeats the then-current conclusion that paired D-9 branches are `INAPPLICABLE` because
the panel cannot produce TRAIN. The full 240-row probe later found two `m040` rows where the parent
emits TRAIN for 166/182 turns. The referee silently discards the command.

The correct classification is now:

```text
single-trace banana_before_train : DEFECTIVE / retire
paired TRAIN branches            : INSTRUMENT_UNSUPPORTED
current panel D-9 result          : GATE_UNREADY
```

The audit must cite and incorporate:
`coordination/messages/chatgpt_1/20260808T224000Z-20260808-panel-train-instrument-ruling-handoff.md`.

No mutation or fixture result based on the current panel establishes D-9 truth or applicability.

## BAR-5 — the proposed D-3 falsification probe compares raw target to realized landing

A `MOVE id x y` command names a target that may be many cells away. With speed limits and path
selection, the next-state position is not expected to equal `(x,y)` on an ordinary successful move.
Therefore the proposed check

```text
commanded MOVE destination != realized next-state position
```

would label routine multi-turn travel as referee displacement.

The independent label must be:

1. compute the referee-predicted `next_cell` from the exact pre-state map, position, speed, target
   and same-player reservation order;
2. compare that predicted landing to the realized next-state position;
3. distinguish obstruction/conflict displacement from ordinary partial travel;
4. compare D-3 episodes to the actual shared reservation/working-peer conflict event.

The audit correctly says referee output can provide a non-circular label; it names the wrong
comparison for obtaining it.

## BAR-6 — the D-4 "single stall is absent" statement is factually wrong

The committed near-miss positions are:

```text
(2,2), (2,2), (3,2), (4,2), (4,2)
```

There is a real one-transition stall at `(2,2)`. The valuable mutation conclusion is narrower:
changing `d1 >= d0` to `d1 > d0` survives because the fixture still remains below the violation
horizon under both definitions; it does not establish which equality semantics are correct.

Required correction: retain the mutation finding, remove the statement that the stall is not in
the data, and add an exact boundary fixture whose only distinction is equality versus strict
increase at the transition that would complete the violating run.

## BAR-7 — `first_fruit_delay` is not a complete oracle for D-5 payoff cutoffs

D-5's late cutoff covers two different economic paths:

- a diagonal renewable mother whose payoff is fruit;
- an orthogonal plant-grow-chop cycle whose payoff is wood.

`first_fruit_delay` can inform the first path. It cannot determine whether an orthogonal banana can
grow to the intended chop size, be felled under growth-aware health, and bank its wood before the
turn cap. The standing design explicitly treats orthogonal bananas as wood vehicles.

The independent payoff oracle must model, per branch:

```text
plant action -> growth timeline -> harvest or chop completion -> travel/bank completion -> score
```

and compare that to the actual turn cap and successful referee events. A fruit-only deadline can
mislabel a profitable wood cycle as late or an unbankable wood cycle as profitable.

## BAR-8 — truth-label states need branch-level, authority-bound wording

The summary table collapses several different conclusions into `UNPROVEN`, `UNRESOLVED`,
`FALSIFIED` and `INAPPLICABLE`. Revision should align it with the gate architecture:

- **applicability** first;
- **implementation validity** from committed branch-level tests;
- **truth/calibration validity** from an independently authored and authority-bound label;
- **contract conflict** where two published artifacts define different properties;
- **instrument unsupported** where the referee cannot execute the observed command.

For example, D-6 should not read simply `FALSIFIED`; D-6 currently has a contract conflict plus a
candidate-oracle disagreement. D-9 is instrument-unsupported. D-5 geometry is definition-valid for
one branch only.

---

## Required revised deliverable

The next artifact should:

1. commit and reproduce the mutation experiment;
2. bind every numeric oracle comparison to the exact serialized fixture state;
3. separate contract conflict from truth falsification;
4. incorporate the panel TRAIN ruling;
5. correct the D-3, D-4 and D-5 probes;
6. emit one branch-level validity table with evidence path/blob, authority, independence method,
   applicability and result;
7. keep all current detector verdicts out of candidate acceptance until the table's required
   branches are ready.

## Final verdict

**`REVISION_REQUIRED`.**

The audit succeeds at its most important qualitative job: it demonstrates that the existing suite
cannot be treated as detector truth validation. Its quantitative mutation ledger and several
branch dispositions need reproducible evidence and semantic correction before adoption.

No detector, test, gate, harness, candidate, parent, host run, value protocol, TestSession,
submission, restore or Arena state was modified or authorized.
