# I-30 implementation report — paired schedule/opponent-production exposure

Date: 2026-08-08
Author: `claude_1`
Execution reviewer: `local_claude_1` (assigned; **this report is not a gate verdict**)
Task: `20260808-phase1-work-allocation`, item 6
Branch: `agent/claude_1-banana-restoration-r2`
**Result schema version: 3** (revision 3, see §0R3; revision 2 is §0 and is
retained verbatim so the two contracts can be diffed)

Authoritative documents, in order of precedence:

1. `chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md` on `origin/agent/chatgpt_1` —
   the spec author's ruling on D1 and D5. **Where the ruling and the specification
   differ, the ruling governs**, and every such place is named in §0.
2. `chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md` on the same
   branch — the original I-30 specification.

3. `chatgpt_1/i30-revision-2-review-2026-08-08.md` on the same branch — the spec
   author's review of revision 2, verdict `REVISION_REQUIRED` with ten blocking
   machine-contract defects. **Revision 3 exists to close them, and where this report
   and the review differ, the review governs.**

Everything below is subordinate to those three documents.

> **Reading order.** §0R3 and §1R3–§8R3 are revision 3 and supersede the corresponding
> revision-2 sections wherever they disagree. §0–§9 are revision 2, kept verbatim as
> the record of what the review examined.

---

## 0R3. Revision 3 — the ten blocking review defects

Date: 2026-08-09 · Author: `claude_1` · **Result schema version: 3**

Reviewed and rejected: `chatgpt_1/i30-revision-2-review-2026-08-08.md`
(blob at `origin/agent/chatgpt_1`, sha256
`2be671a34a24010d00d5f7fb8c1ce3953bffe6475bee86d05e32e2fed61abdbc`), verdict
`REVISION_REQUIRED`, ten blocking machine-contract defects. **The review governs.**

Everything the review accepted is preserved and still asserted by tests: separately
named `gdep_*` / `wdr_*` / `net_bank_flow_*`; the exact identity on net bank flow;
ambiguous class attribution becoming `unknown` → `GATE_UNREADY`; the class-swap
(`a3`, both orders) and same-turn (`a1`) adversarial fixtures.

Every claim below is **MEASURED** (a command was run; it is in §3R3) or **INFERRED**
(reasoning from source read) or **UNRESOLVED**.

### The single most important structural change

Revision 2 evaluated the bound inside `analyze_pair`. Revision 3 splits the two
levels absolutely, and this is what closes defects 1, 2 and 3 together:

```
analyze_pair()      ONE pair. Accounting and evaluability only.
                    Statuses: GATE_UNREADY | NOT_APPLICABLE | UNPROVEN | MEASURED.
                    It has NO `bound` parameter at all -- passing one is a TypeError.
                    It can emit neither PASS nor a value FAIL.

aggregate_report()  Selects the population the bound NAMES, computes the exact
                    metric over it as a `Fraction`, verifies owner authority
                    against an `OwnerAuthority`, and is the ONLY producer of a
                    verdict.
```

**The new aggregate precedence rule**, evaluated strictly in this order:

| order | condition | verdict |
|---|---|---|
| 1 | any pair `GATE_UNREADY`, or any run's command execution invalid | `GATE_UNREADY` |
| 2 | bound absent, invalid, or not owner-**verified** | `GATE_UNREADY` + `MEASURED_UNTHRESHOLDED` |
| 3 | population empty or the metric not identifiable | `GATE_UNREADY` |
| 4 | any pair-level hard-limit `FAIL` row | `FAIL` |
| 5 | owner-verified aggregate bound exceeded | `FAIL` |
| 6 | otherwise | `PASS` |

Steps 4 and 5 accumulate into `aggregate_fail_reasons`, so a corpus that both
contains a failed row and exceeds the bound reports both. Step 1 dominates 4 and 5:
a corpus with one unready row cannot render a value verdict at all.

### Defect-by-defect

| # | review defect | closed by | mutation |
|---|---|---|---|
| 1 | `mean_*` evaluated per pair; `Bound.population` unused | `POPULATIONS` is a frozen dict the aggregate selects with; `SUPPORTED_METRICS[name]["reducer"]` names `mean` or `max`; per-pair limits live under their own `max_per_pair_*` names; the metric is a `Fraction`, never a float | `M-D1-population`, `M-D1-mean` — **CAUGHT by their own tests** |
| 2 | aggregate ignores `FAIL`; can `PASS` an empty corpus | the precedence table above; one consolidated `population_empty` guard | `M-D2-pairfail`, `M-D2-empty` — **CAUGHT** |
| 3 | `owner_frozen` self-declared | see below | `M-D3-selfdecl`, `M-D3-blob`, `M-D3-boundsha`, `M-D3-frozenfirst` — **CAUGHT** |
| 4 | ambiguous split still emits exact gross totals | see below | `M-D4-nullgross`, `M-D4-flag` — **CAUGHT** |
| 5 | initial stock labelled `natural` | new `baseline` source class, excluded from `SCHEDULE_CLASSES` and so from `D_PRODUCTION_GROSS`, retained in the exact identity as `D_BASELINE_NET` | `M-D5-bankclass`, `M-D5-schedcls` — **CAUGHT** |
| 6 | caller hashes override derived identity via `setdefault` | `RunRecord.derived_identity` is always computed; `pinned_identity` holds only what a transcript cannot prove; `identity` is their union with derived winning; disagreement → `identity_pin_mismatches` → `GATE_UNREADY`. `transcript_sha256` joined `PAIR_VARIABLE_FIELDS`, so a declared self-pair over two different transcripts is caught | `M-D6-setdefault`, `M-D6-pincheck` — **CAUGHT** |
| 7 | activation misses HARVEST/CHOP/banking/controller/seam | `ACTIVATION_CONTRACT_VERSION = 2` with seven enumerated causes, six of them read off **successful state events** rather than command strings; a claimed telemetry mechanism with no telemetry bound is `GATE_UNREADY`, never `NOT_APPLICABLE` | `M-D7-harvest`, `M-D7-banking`, `M-D7-telemetry` — **CAUGHT** |
| 8 | no proof the referee executed every emitted command | see below | `M-D8-counts`, `M-D8-manifest`, `M-D8-gate` — **CAUGHT** |
| 9 | provenance closure and raw ledgers incomplete | `provenance_manifest()` closes over the five python modules, the spec/ruling/**review** blobs read from `origin/agent/chatgpt_1`, `rust/src/game/engine.rs`, the interpreter version, the platform and the command-protocol verb set; every pair carries `candidate_ledger_sha256`/`parent_ledger_sha256`; the aggregate carries `pair_result_sha256` per pair and a `raw_ledger_index` of immutable path + sha for all 66 raw ledgers | `M-D9-ruling`, `M-D9-ledgersha` — **CAUGHT** |
| 10 | mutation output committed but not the runner | `i30/i30_mutation_runner.py` + `i30/mutation-manifest-r3-2026-08-09.json` | the machinery itself; see §7R3 |

### Defect 3 — how `owner_frozen` became verifiable

`Bound` no longer has an `owner_frozen` attribute at all. `{"provenance": "owner_frozen"}`
is now an **invalid bound**: it adds `self_declared_owner_provenance_rejected`, and an
invalid bound can decide nothing. Authority is a separate object and a separate verdict:

```
OwnerAuthority(loader, ref, authority_id)      # a blob source pinned to ONE ref
GitRefAuthority(repo_root, ref, authority_id)  # `git cat-file blob <ref>:<path>`
verify_owner_decision(bound, authority, observed_utc) -> {"verified": bool, "reasons": [...]}
```

`verified` requires **all** of:

1. an authority exists (`owner_authority_absent` otherwise — the fail-closed default,
   so a caller that passes no authority can never reach `PASS`);
2. `owner_decision_path` resolves **on that pinned ref** (`owner_decision_unresolved`);
3. `sha256(blob) == bound.owner_decision_blob` (`owner_decision_blob_mismatch`);
4. the decision parses and names `invariant == "I-30"`;
5. `decision.bound_body_sha256 == bound.body_sha256`, the sha over the bound **minus its
   own decision pointer** — the pointer is the one link that must be over a projection,
   because the decision names the bound and the bound names the decision. Editing any
   operative field (metric, operator, threshold, population, schema version) changes it
   (`owner_decision_bound_sha_mismatch`);
6. `decision.authority == authority.authority_id` (`owner_decision_authority_mismatch`);
7. `frozen_utc <= observed_utc`, both present — a bound chosen after the results were
   observed is not a bound (`owner_decision_not_frozen_before_observation`).

**An unratified bound can no longer emit a production `FAIL`.** The review's second
authority error is closed: arithmetic from a bound nobody ratified is published under
`unratified_bound_evaluation` with the explicit status `NON_PRODUCTION_MEASUREMENT`,
and the aggregate stays `GATE_UNREADY / MEASURED_UNTHRESHOLDED`.

**MEASURED — the aggregate is still `GATE_UNREADY`.** The production authority is
`GitRefAuthority(repo_root, "refs/remotes/origin/main", "user")` and the production
decision path is `coordination/decisions/i30-bound-decision.json`. It resolves to
nothing:

```
$ python3 i30_analyzer.py --report i30/i30-fixture-results-r3-2026-08-09.json
$ python3 -c '...'
aggregate_status: GATE_UNREADY
aggregate_sub_status: MEASURED_UNTHRESHOLDED
aggregate_unready_reasons: ['pair_gate_unready', 'input_execution_validity',
                            'bound_not_owner_verified', 'metric_not_identifiable']
owner_decision.verified: False   reasons: ['owner_decision_unresolved']
statuses: ['GATE_UNREADY', 'MEASURED', 'NOT_APPLICABLE']   # no PASS, no FAIL
```

No threshold was invented. `TEST_BOUND_WINDFALL` still points at
`UNRESOLVED/no-owner-decision-exists`.

`PASS` and `FAIL` are proven **reachable** only through `fx.test_authority()`, an
explicitly labelled test stand-in that serves decisions under
`coordination/decisions/i30-test-bound-<body-sha>.json` on the fictional ref
`refs/i30-test/owner-decisions`. Nothing in the shipped `main()` path can consult it.

### Defect 4 — intervals instead of a chosen endpoint

Within a resource-turn the feasible withdrawal count is an integer interval
`[lo, hi]`, and `deposits(w) = budget + w`, `withdrawals(w) = w`. Both are monotone in
`w`, so the feasible gross interval's ends sit at `w = lo` and `w = hi`. **Net bank
flow does not depend on `w` at all** — that is why it stays exact.

| the split is | gross totals | per-class gross | net | classes |
|---|---|---|---|---|
| identifiable (`lo == hi`) | exact | exact | exact | as derived |
| **not** identifiable (`lo < hi`) | **`None`** + `gdep_total_interval` / `wdr_total_interval` | **`None`** + `gdep_interval_<class>` / `wdr_interval_<class>` | exact | `unknown` |
| class-only ambiguous (unit assignment, mixed multiset) | exact | exact | exact | `unknown` (the accepted D5 output) plus a per-class feasible interval |

The per-class intervals are over the **true, pre-relabelling** classes: relabelling to
`unknown` is a reporting convention and does not make a chosen count true. The pair
propagates `None` (`_sub` returns `None` if either side is `None`) rather than
inventing a point, and `Bound.evaluate` refuses to reduce a population containing any
`None` (`metric_not_identifiable` → `GATE_UNREADY`).

MEASURED, `fixture_a1_same_turn_deposit_withdrawal` candidate:
`gdep_total = None`, `gdep_total_interval = [0, 1]`, `wdr_total_interval = [0, 1]`,
`gdep_interval_ours = [0, 1]`, `wdr_interval_baseline = [0, 1]`,
`net_bank_flow_total = 0`, `residual = 0`.
`fixture_a2_multi_source_deposit`: `gdep_total_interval = [1, 2]`,
`wdr_total_interval = [0, 1]`, `net_bank_flow_total = 1`.
`fixture_a3_class_swap` (class-only): `gross_identifiable = True`,
`gdep_total = 1`, `gdep_unknown = 1`.

### Defect 8 — the input execution gate

`ExecutionValidity` is a **harness declaration** that I-30 validates and never infers.
It runs **before any ledger is built**: on a rejected pair, `result["candidate"]`,
`result["parent"]` and every derived quantity including `schedule_windfall_net` are
`None`, and `counted_in_denominator` stays `True`.

Required fields: `execution_status`, `commands_emitted`, `commands_executed`,
`unsupported_command_events`, `malformed_command_events`, `verb_manifest`,
`verb_manifest_sha256`, `referee_sha256`, `engine_sha256`, `instrument_version`,
`corpus_version`. Rejection reasons: `execution_validity_absent` (the fail-closed
default — a record with no declaration is unready), `execution_validity_incomplete`,
`execution_status_not_ok`, `unsupported_command_events`, `malformed_command_events`,
`commands_emitted_not_all_executed`, `verb_manifest_absent`,
`verb_manifest_sha_mismatch`, `verb_outside_referee_manifest`,
`execution_provenance_incomplete`. `referee_sha256`, `verb_manifest_sha256`,
`instrument_version` and `corpus_version` also joined `SHARED_IDENTITY_FIELDS`, so a
pair whose two sides were executed by different referees is `GATE_UNREADY`.

`verb_outside_referee_manifest` is derived independently: I-30 tokenizes the command
bytes itself and requires every verb present to be in the referee's declared manifest.

**Does the gate reject a discarded-command trace? MEASURED: yes.**
`fixture_m040_discarded_train` reproduces the m040 signature exactly — `TRAIN`
emitted on three of four turns, zero unit spawns, `execution_status == "ok"` (the
discard was *silent*), the pre-repair verb manifest without `TRAIN`, and
`commands_executed == commands_emitted - 3`. It is caught twice over:

```
status                        GATE_UNREADY
unready_reasons               ['input_execution_validity']
candidate_execution.reasons   ['commands_emitted_not_all_executed',
                               'verb_outside_referee_manifest']
candidate                     None      # no ledger was ever built
schedule_windfall_net         None
```

The verb-manifest clause is the one that matters most: it rejects the trace **even if
the harness had lied about the counts**, because the pre-repair referee cannot
truthfully declare a manifest containing `TRAIN`.

The two real `m040` traces named by the review as mandatory negative controls are
**UNRESOLVED**: they live in another agent's `claude_1/pipeline/` tree, which is under
external acceptance review and out of bounds for this task. The fixture reproduces
their signature from the repair report's measured numbers; it is not the same bytes.

### 1R3. Status summary (revision 3)

| item | result |
|---|---|
| review defects closed | **9 of 10 fully; 1 partial** (defect 8 — the gate is implemented and proven, but the two real `m040` traces are out of bounds; see above) |
| disputed | **none** — every defect is accepted as stated |
| test methods | **105, all passing** (48 from revision 2, updated where the contract moved, + 56 new revision-3 tests + 1 end-to-end production-corpus test) |
| RED evidence | 54 of the 56 new tests failed against revision 2, recorded verbatim in `i30/red-evidence-r3-2026-08-09.txt`, committed before the fix |
| mutation experiment | **22 of 22 caught, 22 of 22 by their own expected test**, control green, runner + exact patch manifest committed |
| fixture corpus | 35 pairs, aggregate **`GATE_UNREADY`**, sub-status `MEASURED_UNTHRESHOLDED`, statuses `{GATE_UNREADY, MEASURED, NOT_APPLICABLE}` |
| `PASS` reachable in this repo? | **no.** No owner decision resolves on the production ref. `PASS`/`FAIL` are demonstrated only under an explicitly labelled test authority |
| pre-existing suites | `test_trace_detectors` 28 OK; `test_oscillation_library` + `test_score_hierarchy_check` 215 OK (2 skipped) — all unmodified |

Two of the 56 new tests already held against revision 2 and are recorded as such:
net bank flow was already exact under an ambiguous split, and the unrelated-command
divergence already did not activate.

### 3R3. Exact commands to reproduce (revision 3)

All from `claude_1/banana-restoration-r2/`, python 3.12.3, no third-party packages:

```bash
# 105 tests, OK
python3 -m unittest test_i30_invariant -v

# the fixture corpus + raw ledgers; aggregate GATE_UNREADY under the
# PRODUCTION owner authority (which resolves nothing)
python3 i30_analyzer.py --report i30/i30-fixture-results-r3-2026-08-09.json

# the mutation experiment: control + 22 mutations, each in its own scratch tree
python3 i30/i30_mutation_runner.py \
    --out  i30/mutation-sweep-r3-2026-08-09.json \
    --text i30/mutation-sweep-r3-2026-08-09.txt

# untouched neighbours
python3 -m unittest test_trace_detectors
python3 -m unittest test_oscillation_library test_score_hierarchy_check
```

### 4R3. Input SHA-256 (revision 3)

| file | sha256 |
|---|---|
| `i30_ledger.py` | `f658e7204a28e33b70255348eeadbb2f0582bfdd157318521b5bd153d7ec44e6` |
| `i30_analyzer.py` | `6b8a23217d4d6dbdd059a9c3257ed511f71eda811a2dafc8c7f910e4a2a374ec` |
| `i30_fixtures.py` | `dbaa7b7118d277b3380528bd7370ad75e20b125f188c155d83f0aff67f03599c` |
| `test_i30_invariant.py` | `16578581f7d1628f37973bf81597262ae07b3916c6f6fc70f0c201cfede1112d` |
| `i30/i30_mutation_runner.py` | `59cfc93ac5c2afdee435613fb87b62ce006d037030205b5ff7c0b5051d17122f` |
| `i30/mutation-manifest-r3-2026-08-09.json` | `8530be388e24ff640343edaac7199e1d6767785f3a49611784f9d5183ac21c4a` |
| `i30/i30-fixture-results-r3-2026-08-09.json` | `e87fdaadc0ab2352878f117b1623734a66ce8bd47e4eeb932a97faf63ac18157` |
| `i30/mutation-sweep-r3-2026-08-09.json` | `418bbf46b037ef6c6d100737dad0f6db6d81a6f123bd93021f5ab11fedcb7955` |
| `i30/red-evidence-r3-2026-08-09.txt` | `d4120df04a5f199f2ba2c495c8e62129fe5e31471447fe8e4f7796d284f5ce05` |
| `i30/green-evidence-r3-2026-08-09.txt` | `73ec335fb12622859a2b24106c916e0635663b969cd24933b12e96ef5afafb70` |
| `trace_detectors.py` (imported read-only, **byte-unchanged**) | `59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209` |
| `rust/src/game/engine.rs` (read-only reference) | `7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05` |
| review blob, `origin/agent/chatgpt_1` | `2be671a34a24010d00d5f7fb8c1ce3953bffe6475bee86d05e32e2fed61abdbc` |
| ruling blob, `origin/agent/chatgpt_1` | `4439b38b7d645aedca36e347387976032331184e582986e38b25985ae641ef5e` |
| spec blob, `origin/agent/chatgpt_1` | `beb34389593c3c8d5690a577f6c528b9b3c3488549f9c6d4902cf7679c45199d` |

The last three are re-derived by `provenance_manifest()` on every run, so a stale spec
or ruling changes the artifact.

### 7R3. Mutation experiment (defect 10)

`i30/i30_mutation_runner.py` is the experiment; the text file is only its printout.
Per mutation it (1) asserts the target's pinned sha256 and that the `preimage` occurs
**exactly once** so the patch is unambiguous, (2) copies every python module to a
fresh scratch tree, (3) applies the exact substitution(s), (4) runs the suite, (5)
records `CAUGHT`/`SURVIVED`, the exact failing test ids, and whether the declared
`expected_catcher` was among them.

Two deliberate design points:

- **`caught_by_expected` is reported separately from `caught`.** A mutation caught by
  a neighbouring assertion proves the suite is sensitive, not that the defect's own
  test bites. Revision 3 is 22/22 on both.
- **An unmutated control runs first** and must be green; a red control invalidates
  every row. (It caught a real problem while this was being built: a scratch tree has
  no git refs, so the repository root is now injected as `I30_REPO_ROOT`.)
- `TestR3D10MutationRunnerIsReproducible` is deselected **inside the scratch tree
  only**, because it pins the sha of the very files a mutation edits and would
  therefore flag every mutation.
- `M-D2-empty` carries `extra_patches`: the empty-population guard is deliberately
  defence-in-depth, and removing one copy alone is masked by the other. A masked
  mutation measures nothing, so both go at once.

**The 23/23 figure from revision 2 is superseded, not carried forward.** The
revision-3 set is 22 mutations chosen one-to-three per review defect. It is
**descriptive of that chosen set**: it is still not a completeness proof for the
identifiability rules, the activation contract or the execution gate.

### 8R3. UNRESOLVED after revision 3

- the two real `m040` traces as negative controls for the input gate — they are in
  another agent's tree, under external acceptance review (defect 8, partial);
- no owner decision on the I-30 bound exists anywhere, so no candidate verdict may be
  cited from this instrument under any circumstances;
- completeness of the identifiability predicates is still unproven (the review said so
  and revision 3 does not change it);
- the nine-detector proxy still does not prove all 29 invariants; no adopted real-pair
  execution or map-cluster interval exists; seat/family/multi-map aggregate paths
  remain structural;
- `GitRefAuthority` shells out to `git cat-file`; it proves a blob is on a ref, not
  that the ref itself is authentic. A signed-object check is not implemented.

---

## 0. Revision 2 — what the ruling changed

The first implementation (commit `80b77f70`) was ruled **`REVISION_REQUIRED`**. Both
findings are now implemented, test-first. The schema is versioned so that neither
change can be read into an older artifact:

| schema version | meaning |
|---|---|
| 1 | gross-only `DEP_*` as the spec wrote it, and then the first revision's silent redefinition of `DEP_*` as net — rejected by the ruling |
| **2** | gross deposits, bank withdrawals and net bank flow separately named; identity on net; non-identifiable attribution fails closed as `unknown` |

### D1 — accepted as a spec correction; schema revised

The ruling accepted that withdrawals must appear in the exact accounting, and rejected
the way the first revision did it. Implemented:

| ruling requirement | where |
|---|---|
| keep `dep_*` / `gdep_*` **gross** | `RunLedger.to_json`; `dep_<c> == gdep_<c>` and both are gross, as the spec's frozen term always meant |
| explicit `wdr_*` and `net_bank_flow_*` fields | `RunLedger.to_json`, `RunLedger.net_bank_flow` |
| net semantics machine-visible in the paired names | `d_direct_net`, `d_schedule_net`, `d_unknown_net`, `schedule_windfall_net`; the unqualified names are **removed**, not aliased, and the schema version is bumped |
| identity on net bank flow | `analyze_pair`: `D_OPP = D_DIRECT_NET + D_SCHEDULE_NET + D_UNKNOWN_NET − D_TRAIN`; `RunLedger.residual` uses `net_bank_flow_total` |
| gross production a mandatory separate diagnostic | `d_direct_gross`, `d_production_gross`, `d_unknown_gross`, `d_gdep_<c>`, `d_wdr_<c>`, `d_nbf_<c>` |
| every bound metric name states gross or net | `SUPPORTED_METRICS` + `metric_is_ambiguous`; `mean_schedule_windfall` now yields `bound_metric_ambiguous_gross_or_net` → `GATE_UNREADY` |
| a fixture where gross production rises and an equal withdrawal leaves score flat | `fixture_d1_gross_production_with_offsetting_withdrawal`: `d_production_gross = +1`, `d_schedule_net = 0`, `d_opp = 0` |
| `D_UNKNOWN_NET == 0` is not sufficient evidence | the provenance gate also fires on gross unknown mass and on any untagged atom; `fixture_a6_cancelling_unknown_flow` is the bite-test |

`dep_total`, which meant *net* in schema 1, is deleted. `gdep_total`, `wdr_total` and
`net_bank_flow_total` replace it.

### D5 — shadow ledger permitted, but ambiguity must fail closed

The ruling confirmed that a deterministic shadow ledger is allowed by §5.1 and that
engine instrumentation was never mandatory, so **D5 as a "shadow ledger vs referee
ledger" deviation is withdrawn**. What replaced it is a harder requirement: every
attribution must be *uniquely derivable*, or become `unknown` and force
`GATE_UNREADY`.

The tie-break is gone as a correctness mechanism. Three named predicates in
`i30_ledger.py` each answer only *"is this uniquely determined by the recorded
state?"* — never *"which shall I pick?"*:

| predicate | the ambiguity it refuses to resolve |
|---|---|
| `split_is_identifiable(lo, hi)` | more than one feasible (deposit, withdrawal) allocation for one resource in one turn |
| `partial_take_is_identifiable(atoms, n)` | a partial take from a mixed-class multiset — the old FIFO order |
| `assignment_is_identifiable(total, capacity, contributors)` | which of several units' cargo actually crossed the threshold — the old unit-id order |

When any of them says "no", **every atom that could have moved** — bank side and carry
side — is relabelled `unknown`, an `AMBIGUITY` event is emitted, `RunLedger.identifiable`
becomes false and the pair is `GATE_UNREADY` for `non_identifiable_attribution`. FIFO
and unit-id order now only *sequence* a take that is already identifiable.

Two deliberate non-triggers, because a rule that fires everywhere is useless rather
than safe:

- an **infeasible** allocation set (no allocation explains the observation) is not an
  ambiguity: nothing is relabelled and the conservation residual reports it. This keeps
  bite-tests 12 and 13 orthogonal.
- a successful own `PLANT` explains its seed exactly, so the seed decrease is excluded
  from bank-flow candidates. `fixture_a7_seed_and_deposit_at_one_bank_cell` is the
  control, and mutation `M11` proves it is load-bearing.

### R4 of the previous report is retracted

The previous §6 R4 said that a simultaneous deposit/withdrawal split "can misattribute a
class, but the net is still exact, so the identity and the residual remain correct. Not
exercised by any fixture." The ruling correctly called that a blocking defect. It is now
both exercised and closed: `fixture_a1_same_turn_deposit_withdrawal` reproduces exactly
that case, and it is `unknown` + `GATE_UNREADY`.

### Deviations D2–D4 are **not** settled

The ruling was explicitly limited to D1 and D5 and said the other deviations are "not
accepted by silence". Nothing in this revision relies on them being accepted. They are
restated unchanged in §6 and listed again in §8 as open.

---

## 1. Status summary

| item | result |
|---|---|
| mandated bite-tests (spec §10) | **15 of 15 implemented, 15 of 15 passing**, values unchanged from revision 1 — only field names moved |
| ruling fixtures (D1 + D5) | 9 added: `a1`, `a2`, `a2b`, `a3` (×2 variants), `a4`, `a5` (×2 modes), `a6`, `a7`, `d1` |
| test methods in the module | **48, all passing** (23 from revision 1 + 25 for the ruling) |
| mutation controls | **23 of 23 mutations caught**, `i30/mutation-sweep-r2-2026-08-08.txt` |
| fixture corpus | 25 pairs, aggregate `GATE_UNREADY`, statuses `{NOT_APPLICABLE, FAIL, GATE_UNREADY}` |
| statuses implemented | `NOT_APPLICABLE`, `UNPROVEN`, `GATE_UNREADY`, `PASS`, `FAIL`, plus the diagnostic sub-status `MEASURED_UNTHRESHOLDED` |
| `PASS` reachable in this repo? | **no** — no bound anywhere carries `provenance == "owner_frozen"`, so every active fixture is `FAIL` or `GATE_UNREADY` and the aggregate is `GATE_UNREADY` |
| pre-existing suites | `test_trace_detectors` 28 OK; `test_fuzz_panel` + `test_pre_review` 53 OK |

No numerical candidate threshold is proposed, implied or presented as owner-approved
anywhere in this work.

---

## 2. What was implemented

Three modules plus one test module, all under `claude_1/banana-restoration-r2/`.
Nothing outside that directory was modified. No bot, candidate, parent, detector,
gate, host game, value protocol, TestSession, submission, restore or Arena file was
touched; `trace_detectors.py`, `fuzz_panel.py`, every `.min.rs` and everything under
`cgauto/submissions/` are byte-unchanged (`trace_detectors.py` is imported read-only).

### `i30_ledger.py` — deterministic opponent shadow referee (spec §5)

Consumes a `RunRecord` (transcript + command stream + identity hashes), parses it with
the **real** production parser (`trace_detectors.TraceParser` / `CommandParser`), then
reconstructs the opponent's score-bearing flow by exact state differencing:

- **asset provenance registry** (§5.2): map-seeded plants are `natural`; a new plant's
  creator is the sole player occupying its cell in the post-state; absent or mixed
  occupancy is `unknown` and is never guessed;
- **atom carry** with `resource_kind`, `source_event_id`, `source_asset_id`,
  `source_class`, `source_creator`, `acquired_turn`, `acquired_verb` (§5.1), held as a
  multiset;
- **deposits / withdrawals / losses / seed consumption / TRAIN bills** (§5.3);
- **identifiability predicates** (ruling D5): `split_is_identifiable`,
  `partial_take_is_identifiable`, `assignment_is_identifiable`. Where any of them says
  the allocation is not uniquely derivable, every atom that could have moved is
  relabelled `unknown`, an `AMBIGUITY` event is emitted and `identifiable` goes false;
- aggregates, per source class and separately named (ruling D1): `GDEP_c` (gross
  deposits, also emitted under the spec's frozen name `dep_c`), `WDR_c` (bank
  withdrawals) and `NBF_c = GDEP_c − WDR_c` (net bank flow), plus `TRAIN_SPEND`,
  terminal score, terminal turn and the §6 diagnostics (first productive turn,
  productive-turn count, opponent live assets, direct interactions with our assets).

Engine rules were re-derived from source rather than assumed
(`rust/src/game/engine.rs`, cross-checked against `docs/mechanics.md` and
`cgauto/mechanics_rederivation_audit.py`):

```
recompute_scores : score = PLUM+LEMON+APPLE+BANANA + 4*WOOD      (IRON scores 0)
near_shack       : |ux-sx| + |uy-sy| <= 1
apply_drop       : the whole carry vector moves into inventories[player]
apply_pick       : one item moves inventories[player] -> carry   (a bank WITHDRAWAL)
training_cost    : n + stat^2 in PLUM/LEMON/APPLE/IRON; BANANA and WOOD free;
                   IRON charged only when the map has iron terrain
```

### `i30_analyzer.py` — paired analyzer (spec §3, §4, §6, §8, §9, §11)

Pair identity, activation detection, the frozen per-pair quantities, the status model,
the §9 aggregate report and the hash-pinned `Bound` object. Also a CLI
(`python3 i30_analyzer.py --report OUT.json`) that emits the whole fixture corpus as
per-pair + aggregate JSON.

Fail-closed order — **instrument gates are evaluated before any bound is consulted**:

1. pair identity invalid or incomplete → `GATE_UNREADY` (`pair_identity`)
2. `D_UNKNOWN_NET != 0`, **or** `D_UNKNOWN_GROSS != 0`, **or** any untagged atom in
   either run → `GATE_UNREADY` (`unknown_provenance`). The gross clause is what stops
   cancelling unknown deposits and withdrawals from passing as clean.
3. either run not `identifiable` → `GATE_UNREADY` (`non_identifiable_attribution`)
4. pair residual `!= 0`, or either per-run residual `!= 0` → `GATE_UNREADY`
   (`conservation_residual`)
5. not `banana_active` → `UNPROVEN` if a Banana mechanism is claimed, else
   `NOT_APPLICABLE`
6. no bound → `GATE_UNREADY` + `MEASURED_UNTHRESHOLDED` (`absent_bound`)
7. bound malformed / hash-pin mismatch / unsupported operator / metric name that does
   not state gross or net → `GATE_UNREADY` + `MEASURED_UNTHRESHOLDED`
8. bound exceeded → `FAIL`
9. bound satisfied **and** `provenance == "owner_frozen"` → `PASS`
10. bound satisfied but not owner-frozen → `GATE_UNREADY` + `MEASURED_UNTHRESHOLDED`
    (`bound_not_owner_frozen`)

No such owner-frozen bound exists anywhere in this repo, so step 9 has never been
reached and `PASS` is unreachable by construction here.

Raw values are preserved in the output at every status, including `GATE_UNREADY`
(§8). A pair identity mismatch sets `counted_in_denominator: true` and is never
silently dropped (§3).

### `i30_fixtures.py` — the fixture corpus

Real 11×9 map, real stdin-protocol transcripts, real command streams. Nothing here is a
bot, candidate, parent, submission or Arena artifact.

### `test_i30_invariant.py` — the fifteen bite-tests plus the ruling's fixtures

48 tests. All assertions are on exact integers, not on "nonzero" statuses (§10 closing
sentence). The revision-2 classes are `TestD1SchemaSeparatesGrossWithdrawalAndNet`,
`TestD1BoundMetricNamesStateGrossOrNet`,
`TestD5FailsClosedOnNonIdentifiableAttribution`,
`TestD5MutationRevertedTieBreakIsCaught` and `TestNoPassWithoutAnOwnerFrozenBound`.

---

## 3. Exact commands to reproduce

```bash
git checkout agent/claude_1-banana-restoration-r2
cd claude_1/banana-restoration-r2

# the fifteen bite-tests + the ruling's fixtures: 48 tests, OK
python3 -m unittest test_i30_invariant -v

# regenerate the per-pair + aggregate JSON artifact (byte-deterministic,
# 25 pairs, aggregate GATE_UNREADY)
python3 i30_analyzer.py --report i30/i30-fixture-results-r2-2026-08-08.json

# pre-existing suites, unchanged
python3 -m unittest test_trace_detectors                       # 28 tests, OK
cd ../pipeline && python3 -m unittest test_fuzz_panel test_pre_review   # 53 tests, OK
```

Host: `python3` 3.12.3, standard library only, **no pytest**, no network, no
credentials. The analyzer is deterministic: re-running the CLI produces a
byte-identical JSON (verified by `diff`).

The mutation sweep of §7 is reproduced by copying the four modules to a scratch
directory, applying one textual mutation, and re-running `python3 -m unittest
test_i30_invariant` against the copy. The working tree is never mutated. The exact
mutation list and its output are in `i30/mutation-sweep-r2-2026-08-08.txt`.

### Recorded RED states

| revision | RED commit | recorded failure | GREEN commit |
|---|---|---|---|
| 1 | `61e30e20` | `Ran 22 tests`, `FAILED (errors=22)`, 44 `NotImplementedError` frames — `i30/red-evidence-2026-08-08.txt` | `0edb66e0` |
| 2 | `ae352521` | `Ran 44 tests`, `FAILED (failures=12, errors=8)` — `i30/red-evidence-r2-2026-08-08.txt` | `5891946d` |

Revision 2's RED failures are behavioural, not import errors: at the RED commit every
adversarial fixture parses and runs through the real parser and the shadow ledger, and
the evidence file records the old tie-break's actual answers — `a1` banking one `ours`
atom and withdrawing one `natural` atom with residual `0` and no unready reason, and
`a3` moving one unit of mass between `D_DIRECT` and `D_SCHEDULE` (and flipping between
`FAIL` and not-`FAIL`) purely on acquisition order. The failures are `KeyError` on the
schema fields the ruling requires and assertion failures where the tie-break attributed
instead of emitting `unknown`.

---

## 4. Input SHA-256

Governing inputs, both read from `origin/agent/chatgpt_1` at
`da115812a274cc103cdaf2d8d3ca11695556ebea`:

```
4439b38b7d645aedca36e347387976032331184e582986e38b25985ae641ef5e  chatgpt_1/i30-d1-d5-spec-ruling-2026-08-08.md
beb34389593c3c8d5690a577f6c528b9b3c3488549f9c6d4902cf7679c45199d  chatgpt_1/schedule-opponent-production-invariant-spec-2026-08-08.md
```

The specification blob is unchanged from revision 1 (identical at the handoff's declared
`artifact_commit` `cad16c4decf2eea72a8fc861725d9e3bd50502ad`, at
`beebff2dc70bb7a742d1e6cb6a94e59bb8873d89`, and now; git blob
`638e4ca906d09e2128a9de00276a2f125a931d43`).

Revision 2 artifacts (at GREEN commit `5891946d`):

```
402f3700c1953b0b91ad25ccb431825253a97fa56be7d5852c217cc914706d6b  i30_ledger.py
cf75551bf21c3bea8d6e6068f2ffb2507ba86b218ff8af4da932b06f768b5bc2  i30_analyzer.py
3278d1be573bf1e8a2edea09faa8a29e7127dd2975c6f13d4c70b2ce7a99a189  i30_fixtures.py
72095adf4c0fee42da3b149e4c62dd1778809443d36c94e2ea08a51b362e4ca8  test_i30_invariant.py
42dd8e4dfe3a8474ae50044c59ffeeb89d72214324e6e37a906bd8ff0cfc596c  i30/i30-fixture-results-r2-2026-08-08.json
63627423834f05f3a10e27d9861f762f919abb06af6658f8d3ad725084badb98  i30/red-evidence-r2-2026-08-08.txt
acac624d8bdc882991943811f3e7d47b1dde48ed21194d12abe9a5f7b52f8e0a  i30/mutation-sweep-r2-2026-08-08.txt
```

Revision 1 artifacts, superseded but retained:

```
b393d639f28494191e9162b6d42966f2854aaa01d1c038a867b8cdd5509f74b5  i30_ledger.py            (rev 1)
e94882319a9172e20df936167ac1583927f9e40768ec73c493ffd012397b37eb  i30_analyzer.py          (rev 1)
a34f229252ded664158f181e32c493ed539cb550dc68bdd2f153d3a25744e974  i30_fixtures.py          (rev 1)
0bd29b0cd1e6da6570f1282325034af4d5dfb5f995ceb08b9b7d526edf01ab44  test_i30_invariant.py    (rev 1)
054ffea23486370e7c35b9fc3b1346e941fbb0939e292e0374600d63e7e29086  i30/i30-fixture-results-2026-08-08.json
c37b4bc2c94b2c9576ddf9bbccc74c2985bc926b994b25aa1ee20bfa8389a668  i30/red-evidence-2026-08-08.txt
```

Read-only inputs (byte-unchanged by this revision — `trace_detectors.py` still hashes
to the value recorded in revision 1):

```
59dce10dc87797bc6b1b8da0f628f4ddd82b561d93946fa91453d2ea40805209  trace_detectors.py
e0896e3f7cb2c7ac4ced35350469d704432f8c7a1a8a4c9c4ce41495ca13ecf7  conversion_race_oracle.py
7c240abfcfdf678993960fe73440735a19f934596c9651bdf915e2902f78fb05  rust/src/game/engine.rs
22c335cc712f3dd1dc07269657de9a5d79126cc4d35438f0b9d8ca44089e6944  docs/mechanics.md
```

Bound objects: none is owner-frozen. The only bound in the repo,
`i30_fixtures.TEST_BOUND_ZERO_WINDFALL`, carries
`provenance: "test_fixture"` and `owner_decision_path:
"UNRESOLVED/no-owner-decision-exists"`. It exists solely to exercise bound
arithmetic and **must not be cited as a threshold**.

---

## 5. Bite-test → spec section map, with measured values

Every measured value below is unchanged by revision 2. Under schema 1 the paired terms
were named `D_DIRECT` / `D_SCHEDULE` / `SCHEDULE_WINDFALL` and were *already* net of
withdrawals; schema 2 renames them `D_DIRECT_NET` / `D_SCHEDULE_NET` /
`SCHEDULE_WINDFALL_NET` and adds the gross diagnostics beside them. **No expected value
in the fifteen changed** — read `D_DIRECT` below as `D_DIRECT_NET`, and so on. The one
assertion that moved is bite-test 7's, from `dep_total` (which meant net) to
`gdep_total`; its value, "gross deposits are equal", is what §10 clause 7 asked for in
the first place.

| # | spec §10 clause | spec sections exercised | test class | measured |
|---|---|---|---|---|
| 1 | exact parent-vs-parent | §3, §6 | `TestBite01ExactSelfPair` | every delta and residual `0`; `NOT_APPLICABLE` |
| 2 | directly inert candidate | §3, §6 | `TestBite02InertCandidate` | command hashes differ, all deltas `0` |
| 3 | no Banana activation | §4, §8 | `TestBite03NoBananaActivation` | `NOT_APPLICABLE`; claimed-but-unexercised → `UNPROVEN` |
| 4 | direct theft only | §6, §7 | `TestBite04DirectTheftOnly` | `D_DIRECT=+1`, windfall `0`, `D_OPP=+1`, real D-6 fires |
| 5 | indirect production only | §6, §7 | `TestBite05IndirectProductionOnly` | `D_SCHEDULE=+2`, windfall `+2`, `D_OPP=+2`, **real D-6 = 0** |
| 6 | natural opportunity | §5.2, §6 | `TestBite06NaturalOpportunity` | `dDEP_NATURAL=+1`, `dDEP_OPP=0`, windfall `+1` |
| 7 | TRAIN-spend offset | §5.3, §6 | `TestBite07TrainSpendOffset` | gross deposits equal, `D_TRAIN=6`, windfall `-6`, `D_OPP=-6` |
| 8 | mixed cargo | §5.1, §5.2 | `TestBite08MixedCargo` | one DROP → ours `1`, opponent `1`, natural `1`, unknown `0` |
| 9 | longer-game schedule | §4, §6 | `TestBite09LongerGameSchedule` | terminal-turn delta `+7`, windfall `+1`, bank withdrawal `1` |
| 10 | D89-like blind spot | §1, §6, §7, §8 | `TestBite10BlindSpotFixture` | **all of D-1..D-9 PASS, D-6 = 0**, yet `D_SCHEDULE=+1`, windfall `+1` → `FAIL`, never `PASS` |
| 11 | self-pair hash mismatch | §3 | `TestBite11PairIdentityMismatch` | `GATE_UNREADY`, still counted in denominator |
| 12 | one untagged atom | §5.2, §6 | `TestBite12UntaggedAtom` | `D_UNKNOWN=1`, residual `0` → `GATE_UNREADY` |
| 13 | nonzero residual | §6 | `TestBite13NonzeroResidual` | residual `1`, `D_UNKNOWN=0` → `GATE_UNREADY` |
| 14 | absent bound / config hash | §8, §11 | `TestBite14AbsentBound` | `MEASURED_UNTHRESHOLDED` → `GATE_UNREADY`; also covers non-owner bound and hash-pin mismatch |
| 15 | remove the indirect calculation | §10 | `TestBite15MutationBitesTheIndirectTerm` | windfall `1 → 0`, status `FAIL → not FAIL`, D-6 unchanged at `0` |

Bite-tests 12 and 13 are deliberately **orthogonal**: 12 has residual `0` so only the
provenance gate can fire, and 13 has `D_UNKNOWN = 0` so only the conservation gate can
fire. Neither can pass by accident on the other's check.

Bite-test 15 detail: `SCHEDULE_WINDFALL_NET` is computed by the module-level
`compute_schedule_windfall_net`, whereas the conservation residual is computed from the
ledger aggregates directly. Replacing that one function with `lambda …: 0` therefore
leaves the residual at `0` and leaves D-6 at `0`, and the blind-spot fixture's own
assertions are what break. The mutation is caught by the intended logic, not by a
neighbouring check.

### 5b. Ruling fixtures (revision 2), with measured values

| fixture | ruling clause | measured | verdict |
|---|---|---|---|
| `a1_same_turn_deposit_withdrawal` | D5 "simultaneous same-resource deposit and withdrawal … zero net inventory change" | `gdep_unknown=1`, `wdr_unknown=1`, `net_bank_flow_unknown=0`, **`d_unknown_net=0`**, `unknown_atoms=2`, `residual=0`, `d_opp=0` | `GATE_UNREADY` (`non_identifiable_attribution` + `unknown_provenance`) |
| `a2_multi_source_deposit` | D5 "two depositing units carrying different provenance classes while another unit withdraws" | `gdep_unknown=2`, `wdr_unknown=1`, `gdep_ours=0`, `gdep_natural=0`, `residual=0` | `GATE_UNREADY` |
| `a2b_deposit_unit_assignment` | D5, unit-id tie-break | deposit count forced at `1`, depositor not: `gdep_unknown=1`, `gdep_ours=0`, `d_opp=+1`, `residual=0` | `GATE_UNREADY` |
| `a3_class_swap` (`ours_first`, `opponent_first`) | D5 "two allocations with identical state deltas and residuals but different direct/schedule splits" — the indistinguishable-pair test | both variants: `gdep_unknown=1`, `gdep_ours=0`, `gdep_opponent=0`, `d_opp=+1`, `residual=0`, and **identical** `d_direct_net` / `d_schedule_net` / `d_direct_gross` / `d_production_gross` | `GATE_UNREADY` (both) |
| `a4_dead_cell_acquisition` | D5 "acquisition after a long-dead asset occupied the same cell" | `gdep_natural=0`, `gdep_unknown=1`, `unknown_atoms=1`, `d_unknown_net=+1` | `GATE_UNREADY` (`unknown_provenance`) |
| `a5_planter_occupancy` (`mixed`, `absent`) | D5 "absent or mixed planter occupancy" | both modes: `gdep_ours=0`, `gdep_opponent=0`, `gdep_unknown=1`, `d_unknown_net=+1` | `GATE_UNREADY` |
| `a6_cancelling_unknown_flow` | D1 "`D_UNKNOWN_NET == 0` is not sufficient evidence" | `identifiable=True`, `gdep_unknown=1`, `wdr_unknown=1`, `d_unknown_net=0`, **`d_unknown_gross=1`**, `residual=0`, `d_opp=0` | `GATE_UNREADY` (`unknown_provenance` only) |
| `a7_seed_and_deposit_at_one_bank_cell` | control against over-firing | `identifiable=True`, `plant_events=1`, `gdep_ours=1`, `unknown_atoms=0`, `d_direct_net=+1`, `residual=0` | not unknown, not unready for provenance |
| `d1_gross_production_with_offsetting_withdrawal` | D1 change 5 | `gdep_opponent=1`, `wdr_opponent=1`, `net_bank_flow_opponent=0`; **`d_production_gross=+1` while `d_schedule_net=0` and `d_opp=0`** | not unknown; gross ≠ net proven |

The `a3` pair is the ruling's "strongest bite-test": the two variants differ only in the
order in which the opponent acquired two indistinguishable bananas, the ambiguous
transition is byte-identical between them, and both `D_OPP` and the residual are the
same. Under the old FIFO tie-break the two histories reported `d_direct_net = +1,
d_schedule_net = 0` and `d_direct_net = 0, d_schedule_net = +1` respectively — one unit
of mass moved between direct exploitation and schedule production with no signal at all.
The shadow ledger now returns `unknown` for both rather than selecting either history.

---

## 6. Ambiguity resolutions and deviations — stated plainly

The spec is authoritative. These are gaps it does not cover, or places I did something
different. Each is labelled **RESOLUTION** (spec silent, I chose) or **DEVIATION**
(spec says X, I did Y).

**D1 — RESOLVED BY RULING: withdrawals are a spec correction; the schema is now explicit.**
Revision 1 reported `DEP_<class>` net of same-class withdrawals. The ruling accepted the
correction in direction and rejected the schema: "redefining fields named `DEP_*` from
gross deposits to net bank flow silently changes a frozen term." Schema 2 therefore has
three separately named quantities per class — `gdep_*` (= `dep_*`, gross), `wdr_*`, and
`net_bank_flow_*` — the identity runs on net, gross production is a mandatory separate
diagnostic, and every bound metric name states which it is. Details in §0. **Closed.**

**D2 — DEVIATION: an extra `provenance` field on the bound object.**
The §11 illustrative schema has no field that distinguishes an owner-frozen bound from
any other well-formed object, yet §8 and §11 require that a non-owner-frozen bound never
yield `PASS`. I added a required-for-`PASS` field `provenance`, which must equal the
literal `"owner_frozen"`. Anything else measures and reports normally but maps to
`GATE_UNREADY` / `MEASURED_UNTHRESHOLDED`. The analyzer cannot verify ownership itself;
this is a declaration, and the reviewer should treat it as such.

**D3 — DEVIATION: `FAIL` is emitted from a non-owner-frozen bound.**
With the fixture bound, an exceeded threshold yields `FAIL` rather than
`GATE_UNREADY`. This is the fail-closed direction (it can never manufacture an
acceptance) and it is what makes bite-tests 10 and 15 meaningful. `PASS` remains
unreachable without `provenance == "owner_frozen"`.

**D4 — DEVIATION: bite-test 10 asserts nine detectors, not "29 behavioural invariants".**
§10 clause 10 says "all existing 29 behavioural invariants and D-6 are satisfied". The
only executable implementation of that set on this host is `trace_detectors.py`'s D-1..D-9.
The test runs the real `td.run_all` and asserts **all nine verdicts are PASS**, plus
D-6 = 0 specifically. The 29 invariants are not individually executable offline.
Marked **UNRESOLVED**: whether nine detectors adequately stand in for 29 invariants is
a judgement for `chatgpt_1` / `local_claude_1`, not for me.

**D5 — WITHDRAWN AND REPLACED BY THE RULING'S REQUIREMENT.**
Revision 1 flagged "shadow ledger, not referee instrumentation" as a gap versus §10's
wording. The ruling clarified that §5.1 already permits "the referee or a deterministic
shadow ledger", that §10's phrase meant real game semantics rather than a hand-written
arithmetic mock, and that **no engine mutation is required**. So this deviation is
withdrawn.

What the ruling required instead is stricter and is now implemented: a shadow ledger is
acceptable "only when every attributed transition has a unique derivation from the
recorded state". Where it does not, the affected atoms become `unknown` and the pair is
`GATE_UNREADY`. The tie-break is removed as a correctness mechanism — see §0 and §5b.

A referee-side event ledger remains the preferred later host implementation because it
removes these observational equivalence classes outright rather than failing closed on
them. That is a future engine-scope change, not a gap in this instrument.

**R1 — RESOLUTION: initial bank stock and initial unit carry are `natural`.**
The spec does not classify pre-existing stock. §5.2 says map-seeded things are
`natural`, and initial inventories are map-seeded (`official_mapgen.rs`), so both are
tagged `natural`. They are identical across an exact pair and cancel in every paired
delta. The alternative — tagging them `unknown` — would make every pair
`GATE_UNREADY` forever.

**R2 — REVISED: multiset takes, with FIFO demoted to sequencing only.**
§5.1 permits multiset treatment and requires only counts by source class. A take of the
whole multiset, or of a multiset whose atoms all share one class, is uniquely
determined. A **partial** take from a mixed-class multiset is not: FIFO would merely be
a tie-break. Revision 2 therefore relabels the whole multiset `unknown` in that case —
both the atoms that left and the atoms that stayed, since neither is determined — and
uses FIFO only to sequence an already-identifiable take. `fixture_a3_class_swap` is the
bite-test; mutations `M2` and `M5` prove it bites.

**R3 — RESOLUTION: a plant's creator is the sole post-state occupant of its cell.**
Mixed or absent occupancy → `unknown`, never inferred from proximity or ownership
(§5.2 forbids guesswork). Consequence: a PLANT whose planter steps away in the same
observed transition is unattributable. Revision 1 marked this "hardening on reasoning
alone"; `fixture_a5_planter_occupancy` now exercises both the mixed and the absent case,
and mutation `L11` confirms it bites.

**R4 — REVISED: deposit/withdrawal split within one turn (the defect the ruling named).**
Per resource per turn, `budget = inventory_delta + TRAIN_bill`, and every feasible
withdrawal count `w` satisfies `deposits = budget + w`, `0 ≤ w ≤ pick_cand`,
`0 ≤ budget + w ≤ drop_cand`. Revision 1 picked one point of that interval and admitted
it "can misattribute a class, while the net and conservation residual remain correct".
The ruling correctly called that blocking, not diagnostic. Revision 2 counts the
feasible points:

- exactly one → identifiable, use it;
- two or more → **not** identifiable: record an `AMBIGUITY` event, relabel every atom
  that could have crossed the threshold (bank side and carry side) `unknown`, and make
  the pair `GATE_UNREADY`;
- **zero** → not an ambiguity at all but an unexplained observation: relabel nothing and
  let the conservation residual report it, which is what keeps bite-tests 12 and 13
  orthogonal.

The same rule applies to *which unit's* cargo moved when several could have
(`assignment_is_identifiable`). `fixture_a1`, `fixture_a2` and `fixture_a2b` are the
bite-tests; mutations `M1`, `M3`, `M4` prove they bite.

**R5 — RESOLUTION (important): TRAIN is derived independently, never as a remainder.**
TRAIN bills come from opponent unit spawns plus the engine `training_cost` formula. It
would have been much easier to define `TRAIN_SPEND` as whatever inventory movement was
otherwise unexplained — but then the conservation residual would be zero by
construction and bite-test 13 could never bite. The residual is a real cross-check
between an independently derived event stream and the observed terminal score.

**R6 — RESOLUTION: unknown-provenance gate is stricter than §2 clause 4.**
§2 requires `unknown` to be zero "for all score-bearing opponent deposits". I fail
closed on **any** untagged atom, whether or not it is ever deposited. Strictly
stronger; flagging in case that is not wanted.

**R7 — RESOLUTION: terminal state = the last observed state block.**
Commands issued on the final recorded turn have no observed effect and are not scored.

---

## 7. Test-quality evidence: mutation sweep

A fixture that passes whether or not the fix is present proves nothing. Every mutation
below is applied to a scratch copy of the four modules, which is then re-run in full.
Verbatim output: `i30/mutation-sweep-r2-2026-08-08.txt`. **23 of 23 caught.**

### A — the revision-2 logic

| # | mutation | caught by |
|---|---|---|
| M1 | `split_is_identifiable` → always `True` (deposit/withdrawal tie-break restored) | `a1`, `a2` |
| M2 | `partial_take_is_identifiable` → always `True` (FIFO tie-break restored) | `a3` |
| M3 | `assignment_is_identifiable` → always `True` (unit-id tie-break restored) | `a2b` |
| M4 | drop the `non_identifiable_attribution` gate from the analyzer | `a1`, `a2`, `a2b`, `a3` |
| M5 | relabel only the taken atoms instead of the whole multiset | `a3` |
| M6 | `dep_*` silently redefined as net again | D1 schema test |
| M7 | per-run identity back on gross instead of net | bite-test 9 withdrawal test, `d1` |
| M8 | unqualified bound metric name accepted again | bound-metric tests |
| M9 | gross-unknown clause dropped from the provenance gate | `a6` |
| M10 | schema version not bumped | schema-version test |
| M11 | PLANT seed no longer excluded from bank-flow candidates | `a7`, plus the valid-fixture invariance test |

M11 and M9 are the two that matter most for honesty about *this* revision: M11 shows the
seed exclusion is load-bearing (without it the gate fires on a perfectly explained
transition), and M9 shows the gross-unknown clause is not redundant with the
identifiability gate — `a6` has no ambiguity at all and would otherwise pass.

Three of these mutations survived the first draft of the adversarial fixtures (M3, M9,
M11) and one survived it for the wrong reason (M7, because no test asserted a per-run
residual on a run that actually withdraws). The fixtures `a2b`, `a6` and `a7` and two
extra assertions were added in response. That sequence is recorded here rather than
presented as a clean first pass.

### B — controls carried over from revision 1

| # | mutation | caught? |
|---|---|---|
| L1 | `SCORE_WEIGHT` WOOD `4 → 1` | yes |
| L2 | CHOP wood inherits `natural` instead of the asset's class | yes |
| L3 | opponent-created assets classified `natural` | yes (5 failures) |
| L4 | drop the unknown-provenance gate | yes |
| L5 | drop the conservation-residual gate | yes |
| L6 | drop the pair-identity gate | yes |
| L7 | allow `PASS` without owner freeze | yes |
| L8 | TRAIN bill not charged | yes |
| L9 | `SCHEDULE_WINDFALL_NET` drops the `− D_TRAIN` term | yes |
| L10 | a long-dead asset may launder a later atom | yes (was **UNRESOLVED** in revision 1; `a4` closes it) |
| L11 | mixed planter occupancy resolved to `opponent` | yes (was hardening-by-reasoning; `a5` closes it) |
| L12 | withdrawals ignored entirely (the pre-D1 gross-only identity) | yes (9 failures) |

The revision-1 finding that **the fifteen mandated bite-tests never deposit WOOD** still
stands: `TestSupplementaryWoodChopCoverage` (explicitly *not* one of the fifteen) is what
catches L1 and L2, with the opponent felling one natural tree and one of ours for
`D_DIRECT_NET=4`, `D_SCHEDULE_NET=4`, `windfall_net=+4`, `D_OPP=+8`.

---

## 8. UNRESOLVED / not implemented

Closed by revision 2:

- ~~D1 (net vs gross `DEP_*`)~~ — ruled on; schema 2 separates the three quantities.
- ~~D5 (shadow ledger vs referee ledger)~~ — ruled not to be a deviation; replaced by
  the identifiability requirement, which is implemented and mutation-checked.
- ~~"a long-dead plant could launder a later untagged atom" hardening is untested~~ —
  `fixture_a4_dead_cell_acquisition`, mutation `L10`.
- ~~absent/mixed planter occupancy is hardening on reasoning alone~~ —
  `fixture_a5_planter_occupancy`, mutation `L11`.

Still **UNRESOLVED**:

- **No owner-frozen bound exists.** No object anywhere in this repo carries
  `provenance == "owner_frozen"`, so `PASS` has never been produced, the `PASS` branch is
  exercised only by reasoning, and the aggregate over the whole 25-pair corpus is
  `GATE_UNREADY`. Deliberate: fabricating one would be inventing a threshold. The
  ruling also warns that a literal `"owner_frozen"` string is **not** proof of owner
  authorisation — the decision path and blob must be validated separately, and this
  implementation does not and cannot do that. See D2 below.
- **D2 (the `provenance` field on the bound object)** and **D3 (`FAIL` emitted from a
  non-owner-frozen bound)** are unchanged and **not accepted by silence** — the ruling
  said so explicitly. D3 in particular emits `FAIL` from a fixture-namespace bound; the
  ruling's wording is that a non-owner test bound "must not be emitted as a real
  candidate `FAIL` verdict outside a fixture/test namespace". Everything here is inside
  the fixture namespace, but the analyzer does not itself enforce that boundary. Open
  for the execution review.
- **D4 (nine detectors vs 29 behavioural invariants)** is unchanged and open. The only
  executable set on this host is `trace_detectors.py`'s D-1..D-9; the ruling notes that
  "nine detectors are not automatically equivalent to all 29 behavioural invariants".
- **The identifiability rule is sufficient, not proven complete.** Each of the three
  predicates rules out a specific, enumerated class of non-identifiability
  (deposit/withdrawal split, mixed-multiset partial take, multi-unit assignment). I have
  no proof that these exhaust the equivalence classes a transcript admits. A referee-side
  event ledger would remove the question rather than answer it. Open.
- **§9 "pre-registered map-cluster 95% interval"** is not implemented. It needs a
  pre-registered cluster definition and a multi-map corpus; the fixture corpus is a
  single map. `aggregate_report` emits per-map means but no interval.
- **§6 "opponent live-asset count and ripe-fruit exposure over time"** is implemented
  as a terminal count, not a time series.
- **Seat asymmetry is unexercised.** Transcripts are always our-side views, so `seat`
  is always `0` in the corpus. Seat is carried in the identity block and in the
  aggregate breakdown, but no fixture varies it.
- **Opponent families / multi-map / multi-opponent aggregates** are structurally
  implemented but exercised only by a single-family, single-map corpus.
- **No real-corpus run.** Every fixture is synthetic. The instrument has never been run
  against a recorded candidate/parent pair, and the rate at which the identifiability
  gate would fire on real traces is unknown. If it fires often, the instrument is safe
  but unusable, and that would be an argument for the referee-side ledger.

---

## 9. Reviewer checklist (spec §12)

| §12 requirement | where |
|---|---|
| source paths and full hashes | §4 above |
| event schema and per-pair JSON examples | `i30_ledger.py` `_atom` / `RunLedger.to_json`; `i30/i30-fixture-results-r2-2026-08-08.json` |
| all fifteen bite-tests | `test_i30_invariant.py`, mapped in §5 |
| exact parent-vs-parent result | bite-test 1; `fixture_01_exact_self_pair` in the JSON, all deltas `0` |
| one synthetic D89-like result, D-6 zero and I-30 positive | bite-test 10; `fixture_10_blind_spot`, D-6 `0`, `windfall_net +1`, status `FAIL` |
| explicit `MEASURED_UNTHRESHOLDED -> GATE_UNREADY` | `analyze_pair` steps 5/6/9; bite-test 14 |
| no numerical candidate threshold presented as owner-approved | §4 and §6 D2/D3 above; the only bound is marked `test_fixture` |

### Ruling's "required next revision" checklist

| ruling item | status |
|---|---|
| 1. version the result schema with gross deposits, withdrawals and net bank flows separated | done — schema `2`, §0 |
| 2. update the identity and bound metric names to the ruling's definitions | done — §0 |
| 3. make ambiguous shadow-ledger attribution fail closed as unknown | done — §0, §5b |
| 4. add the adversarial provenance fixtures and mutation controls | done — 9 fixtures, 23/23 mutations caught, §5b and §7 |
| 5. regenerate the deterministic fixture report | done — `i30/i30-fixture-results-r2-2026-08-08.json`, 25 pairs, byte-identical on re-run |
| 6. obtain the assigned independent execution review | **not done — this is a handoff, not a verdict** |

Adoption requires the assigned execution review by `local_claude_1`. Nothing in this
report is an accepted gate verdict, and no bot, candidate, parent, detector, gate, host
game, value protocol, TestSession, submission, restore or Arena action was taken or is
authorised by it.
