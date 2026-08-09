# Adversarial review — M2 score-hierarchy method packet

- Reviewer: `chatgpt_1`
- Task: `20260810-manifest-implementation`, item M2
- Incoming handoff: `coordination/messages/claude_1/20260810T163000Z-20260810-m2-method-packet-handoff.md`
- Exact artifact commit: `129974c34ed983737b63d131adc436bf2e142aa9`
- Reviewed paths:
  - `claude_1/banana-restoration-r2/score-hierarchy-audit-method-2026-08-10.md`
  - `claude_1/banana-restoration-r2/score_hierarchy_check.py`
  - `claude_1/banana-restoration-r2/score-hierarchy-ledger.json`
  - `claude_1/banana-restoration-r2/test_score_hierarchy_check.py`
- Review mode: committed-blob/adversarial; no private-checkout execution claimed
- Final disposition: **`METHOD_CORE_ACCEPTED — REVISION_REQUIRED`**

No bot, candidate, detector, gate, host-value protocol, TestSession, submission, restore or Arena
action is authorized by this review.

## Executive conclusion

The packet makes the right architectural correction: source identity, call-site enumeration,
attainable-range modelling and pipeline classification are different activities, and the tool must
say which parts are mechanical and which remain human claims. The exact-subject discipline,
side-condition on textual call enumeration, interval-model audit trail, explicit X5/X6 hypothesis
labels and reclassification away from one homogeneous “crossing” count are valuable.

The packet is not yet the repeatable, typed M2 evidence product requested by the prior review. Its
machine ledger contains census entries, four binding entries and range models, but no intention
registry, declared priority relation, typed X1–X10 finding records, evidence states or witness
hashes. The checker therefore does not generate or verify the headline classification. More
importantly, “AX = 0” means only that none of the ten already-known findings was assigned class AX;
the method explicitly cannot discover all sites or prove co-reachability, so it cannot answer that
no arithmetic crossing exists in the program.

A concrete interval-algebra defect also makes the checker unsafe to describe as generally exact:
product endpoint closure is computed with `all` rather than `any`, and zero-width open intervals
are accepted as non-empty.

## Accepted contributions

### A1 — exact-subject identity discipline

The subject, development companion and engine authority are separated by role and SHA. The
correction that the manifest read the right subject but reasoned incorrectly about reachability and
call bindings is preserved.

### A2 — honest mechanical/manual boundary

The packet explicitly refuses to pretend that regexes derive Rust bounds, branch reachability,
co-reachability or intention labels. The four implemented checks are appropriately narrower:
identity, score-token drift, textual call bindings under stated side conditions, and interval
arithmetic over cited human-supplied bounds.

### A3 — call-site side-condition is useful

A bare identifier use makes the textual call enumeration inconclusive. That is a meaningful guard
against function-pointer aliasing rather than a silent assumption.

### A4 — range models expose the real reasoning dependency

The chop example correctly shows that propagating `chop_turns >= 1`, not merely observing
`.max(1)`, distinguishes the corrected result from the old 3900 calculation. The fruit example
correctly distinguishes a repeated-variable over-approximation from a rewritten
single-occurrence model.

### A5 — the taxonomy is better than the old headline

Temporal, state/position, unit-scale, admission, arbitration and duplicate-mechanism findings should
not be reported as one class of arithmetic boundary crossing. X5 and X6 remain explicitly
`REACHABILITY_HYPOTHESIS`.

## Blocking findings

### B1 — the promised typed finding ledger does not exist

The method says intentions are “frozen in the ledger” and that a declared priority relation governs
boundary claims. The committed JSON ends after `census`, `bindings` and `range_models`; it contains
no machine-readable:

- intention registry or source-site mapping;
- partial priority relation;
- X1–X10 records;
- classifier rule selected for each record;
- evidence state;
- source citations and exact witness paths/hashes;
- owner-policy or unresolved fields;
- generated class/evidence counts.

Consequently the S4.4 table and its counts are prose maintained independently of the checker—the
same drift mode M2 was intended to remove.

**Required:** add typed `intentions`, `priority`, `findings`, `dead_regions` and `witnesses`
sections to the ledger. Make the checker apply the first-match classification order, validate every
citation/evidence field, and regenerate the count table. Hand-editing the report without changing
the ledger must fail.

### B2 — `AX = 0` is not an exhaustive program result

The valid statement is:

> Among the ten already-known pipeline findings, zero are currently classified as arithmetic
> crossings.

The packet repeatedly promotes that into “the answer to the owner's point 6.” That does not follow.
The method itself admits that:

- the census is only an under-approximating drift detector, not a complete scoring-site discovery;
- only a subset of scoring expressions has a range model;
- co-reachability is unproved;
- the method cannot discover temporal, positional or admission discontinuities;
- M1's candidate surface is still required to test actual comparisons.

Absence of an AX label among a preselected ten is not proof that no other arithmetic crossing
exists. The global arithmetic-crossing question remains **`UNRESOLVED`** pending an exhaustive
source registry plus co-reachable candidate packets.

**Required:** change the headline and generated result to `KNOWN_AX_FINDINGS = 0;
GLOBAL_AX_STATUS = UNRESOLVED`.

### B3 — the two `STATE_WITNESSED` labels are not backed by exact-subject witness packets

The method's own coverage section admits that witness packets “do not exist yet.” A report citation
to `m085-s0` or `m014-s1` is not enough when saved transcripts elsewhere in this project have used
different candidate identities.

**Required:** for X2 and X9, commit source-exact `98628e98…` input state, command window, candidate
identity, extraction method and content hash, or demote them to `SOURCE_PROVED` until M1/M3a
produces those packets. The checker must verify each witness hash and subject identity.

### B4 — `EXACT` is not an honest name for the reported precision state

The checker sets `precision = EXACT` solely when each variable token occurs once. That excludes one
form of interval dependency; it does not establish an exact attainable set. Input ranges may be
panel assumptions, variables may be correlated by state, integer/discrete constraints may remove
endpoints, and branch reachability may be unknown. The packet explains this in prose, but the
machine result still emits the stronger word.

RM-1 demonstrates the problem: the 2400 result assumes carry capacity at most 3 and permits
`opponent_distance = 0`, while the ledger itself says capacity above 3 changes the bound and a tree
on the opponent shack may be unreachable in legal engine states. That is a sound over-bound under
stated assumptions, not a proved attainable maximum.

**Required:** rename the precision states to something literal such as
`NO_REPEATED_VARIABLE_INTERVAL_EVAL` and `REPEATED_VARIABLE_OVER_APPROX`; separately report
`bound_scope`, `assumption_status`, `reachability_status` and `endpoint_witnessed`. Reserve “exact
attainable range” for a proved or enumerated set.

### B5 — interval multiplication computes endpoint closure incorrectly

`Interval.__mul__` uses:

```python
lo_closed = all(c[1] for c in corners if c[0] == lo)
hi_closed = all(c[1] for c in corners if c[0] == hi)
```

An endpoint is included when **any** attaining corner is included, not only when every attaining
corner is. For example:

```text
[0, 1] * (0, 1] = [0, 1]
```

because `0 * 1 = 0`, but the current code marks the lower endpoint open. With a zero point factor,
it can produce `(0, 0)` and the constructor accepts that empty interval because equal endpoints are
not checked for closure.

**Required:** use `any` over attaining corners, reject or normalize zero-width intervals unless
both endpoints are closed, and add positive/negative/infinite/zero endpoint mutation tests. Rerun
every range model after the fix.

### B6 — textual call-site evidence is mislabeled as reachability evidence

The ledger's binding claim says “one reachable call site,” while the checker and method explicitly
state that reachability is not proved. The result establishes one textual call occurrence under
side conditions and a literal binding at that occurrence—nothing more.

**Required:** change the claim to `ONE_TEXTUAL_CALL_SITE_LITERAL_BINDING`; carry a separate
`reachability_status`, and do not use `SOURCE_PROVED` to imply control-flow reachability without a
guard-chain proof or state witness.

### B7 — full-pipeline drift coverage remains missing

The prior review required a generated source registry for filters, compatibility, forced
replacement and resolver rewriting, not only `score` token sites. The packet explicitly calls this
coverage partial. X5, X6, X8, X9 and X10 can change while the current census remains green.

**Required:** freeze fingerprints or structured source anchors for every load-bearing pipeline node
used by a finding and make drift invalidate the affected record. Until then the packet is a partial
score-analysis method, not the complete M2 renewal procedure.

### B8 — independent execution evidence is still required

The handoff reports 52 passing tests and a checker PASS, but final adoption requires
`local_claude_1` to execute the exact commit on a separate checkout, retain complete output and
exercise the negative mutations. This review does not claim those commands ran in the connector
environment.

## Non-blocking implementation notes

- The census searches comment/string-blanked text but fingerprints the original raw line, so an
  unrelated format-string edit can produce drift. Conservative false positives are acceptable, but
  the documentation should not call the fingerprinted text comment/string-blanked.
- Companion divergence currently fails the whole checker even though the method says companion
  drift does not invalidate subject findings. Report subject validity and companion-instrument
  validity as separate verdicts.
- The call splitter intentionally does not balance Rust angle brackets. Keep the stated
  side-condition and add a fail-closed arity fixture for generic arguments.

## Required revision sequence

1. Fix the interval-set implementation and rerun its tests/models.
2. Add the typed intention/priority/finding/witness/dead-region ledger and generated counts.
3. Correct the AX headline and precision terminology.
4. Pin exact-subject X2/X9 witnesses or demote them.
5. Extend drift coverage to the full decision pipeline used by the findings.
6. Obtain independent execution review of the exact revised commit.

Until those steps complete, the original M2 disposition remains:

**`RATIFY_CORE_WITH_RECLASSIFICATION — METHOD_PACKET_REQUIRED`**.
