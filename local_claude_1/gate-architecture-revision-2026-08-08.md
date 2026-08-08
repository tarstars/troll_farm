> **SUPERSEDED 2026-08-08** by `local_claude_1/gate-architecture-revision-2-2026-08-08.md`
> after `chatgpt_1`'s review (`d1e8da15`) returned `REVISION_REQUIRED` with findings
> GAR-1…GAR-6, all accepted. Kept immutable for the record. Its two material errors:
> it placed D-1/D-4 outside instrument validation (a refuted detector would then block
> every candidate forever), and it defined validity per detector rather than per
> semantic branch — so it wrongly called D-9 implementation-validated when the committed
> tests exercise only the clause being retired.

# Acceptance-gate architecture — revision against AR-1…AR-9

- Date: 2026-08-08
- Author: `local_claude_1` (Phase 1 item 5, `20260808-phase1-work-allocation`)
- Revises: `claude_1/pipeline/design-gate-redesign-2026-08-07.md`
- Against: `chatgpt_1/gate-architecture-review-2026-08-07.md` (`8daad3f2`), verdict
  `REVISION_REQUIRED`, findings AR-1…AR-9
- Status: **PROPOSED.** Nothing here is adopted. No detector, gate, candidate, workflow, host
  run, or Arena action is authorised by this document.
- Reviewers per allocation: `claude_1` (execution), `chatgpt_1` (adversarial). I author this
  because neither peer is neutral — `chatgpt_1` raised the findings, `claude_1` wrote the
  design under critique.

## 0. Why the previous design could not be patched

Its three defects are structural, not editorial. It classified D-1/D-4 as tolerant checks
against a binding owner rule requiring raw zero (AR-1); it required the current parent to be
*accepted* when the parent provably blocks (AR-3); and it let the candidate under review
influence its own detector tiers (AR-6). Each of those changes what acceptance *means*, so the
revision replaces the semantics rather than adjusting thresholds.

## 1. Verdict lattice — three outcomes, not two

The central change. A binary ACCEPT/BLOCK forces the gate to lie whenever the instrument is
unfit, because both answers assert something about the candidate.

| verdict | meaning |
|---|---|
| `GATE_UNREADY` | The instrument is not fit to judge. **This says nothing about the candidate.** |
| `BLOCK` | The instrument is fit for this finding, and the candidate has a defect. |
| `ACCEPT` | The instrument is fit, and the candidate is clean. |

`GATE_UNREADY` is not a soft block and must never be reported, summarised, or counted as one.
"The gate was broken, so the candidate failed" is as false as "…so it passed". This is AR-7
generalised: the honest third answer is *we do not know*.

## 2. Evaluation order

Order is semantic, because it decides what can mask what.

1. **Provenance closure incomplete** → `GATE_UNREADY`. Nothing further runs.
2. **Floor self-test drift** → `GATE_UNREADY`. Nothing further runs.
3. **Any `VALIDATED` blocker fires** → `BLOCK`.
4. **Any required blocker not `VALIDATED`** → `GATE_UNREADY`.
5. Otherwise → `ACCEPT`.

**Step 3 precedes step 4 deliberately.** A validated detector that fires is trustworthy
positive evidence even while some *other* detector is unproven; the absence of a firing from an
unproven detector is not evidence of anything. Positives and negatives are not symmetric, and
the order encodes that. A `BLOCK` therefore remains issuable on a partially-ready gate, while
`ACCEPT` requires full readiness.

## 3. Detector validity has two axes, not one (AR-6, AR-7)

Tiers are removed, but a single `VALIDATED` state is also wrong — and **D-9 is the proof.** It
passes both of its committed bite-tests perfectly *and* fires 196 false positives on the floor.
A bite-test establishes that a detector does what its specification says; it cannot establish
that the specification is right. Those are different failures and need different evidence:

- **Implementation validity** — from committed bite-tests on the frozen corpus: the detector
  trips its positive trigger and ignores its near-miss control. *Does it obey its spec?*
- **Calibration validity** — from the floor self-test: the detector stays silent on a run where
  the property it claims to measure provably holds. *Is the spec true?*

A detector may contribute to `ACCEPT` only when neither axis is refuted and implementation
validity is positively demonstrated. `DEFECTIVE` on either axis means it must not be quoted in
any verdict, in either direction, until repaired and revalidated.

Per AR-6, counts alone never establish validity, and bite-tests are required for **every**
blocking detector rather than only the unexercised ones.

### 3.1 Current classification

**Correction of my own first draft.** This section originally asserted that no detector had a
committed negative control and therefore none was validated. **That was false**, and checking
before publishing is the only reason it did not ship. `claude_1/banana-restoration-r2/test_trace_detectors.py`
(28 tests, all passing) and `detector-selftest-report-2026-08-04.md` provide a documented
trigger and near-miss pair for **all nine detectors**, committed 2026-08-04.

| detector | floor episodes / games | implementation | calibration |
|---|---:|---|---|
| D-1 | 35 / 32 | validated | untested; firings are Phase-2's question |
| D-4 | 6 / 6 | validated | untested; localised and believed genuine |
| D-5 | 1 / 1 | validated | untested |
| D-6 | 15 / 9 | validated | untested |
| D-2, D-3, D-7, D-8 | 0 / 0 | validated | silent on the floor, consistent with correctness |
| D-9 | 196 / 74 | validated | **REFUTED** — 196 firings where truth is provably zero |

Two consequences worth stating plainly. First, **zero floor episodes for D-2/D-3/D-7/D-8 is not
a gap**: their bite-tests prove they *can* fire, so silence on the parent is evidence the parent
lacks those defects. The "PASS on zero evidence" worry is answered by the fixtures, not by the
floor. Second, **only D-9 is refuted**, and it is refuted on the axis its bite-tests cannot
reach — which is exactly why both axes are required.

## 4. Frozen calibration corpus (AR-6)

Tiers were candidate-dependent and therefore gameable: a candidate could soften a detector by
matching the floor. Replaced by a corpus that is frozen, hash-pinned and versioned
independently of any candidate:

- the current parent;
- one positive fixture per detector, which it must trip;
- one near-miss negative control per detector, which it must not;
- deliberately broken descendants used for the two-sided test of §6.

Detector states are recomputed only when this corpus or the detector contract changes, never
per submission. **Corpus drift aborts with `GATE_UNREADY`.** The candidate under review never
participates in its own classification.

## 5. Absolutes, and the deliberate absence of a waiver mechanism (AR-1, AR-4, AR-5)

**D-1 and D-4 are hard, pre-state, absolute conditions.** Raw zero. They do not enter detector
states, comparison, ledgers, or quarantine machinery. One episode is `BLOCK`. This restores the
owner's binding rule that the previous design contradicted (AR-1).

**No waiver ledger is specified, and none should be built.** AR-4 is right that a hash-pinned
ledger is still an exemption with better bookkeeping — a new causal defect can present the same
signature and be hidden. This revision goes further than AR-4 and declines to build the
mechanism at all. Rationale: the round-6 ROOT-A parent-differential gate was removed by owner
ruling on 2026-08-06, and an exemption mechanism that exists is an exemption mechanism that
gets used. If the owner later authorises a specific exception, it is an explicit ruling naming
the exact episodes, and AR-4's six conditions become its minimum contract.

**Comparative detection is likewise unspecified and dormant.** Should the owner ever authorise
a comparative detector, AR-5 fixes its only permissible form: normalized episode **multiset**
dominance against the frozen floor for that exact map/seat/detector, forbidding multiplicity or
severity growth, permitting removal, and recording new signatures separately even when the
aggregate count falls. Count deltas — whether `<= 0` or `= 0` — are insufficient and are
rejected. No detector uses this today.

## 6. Two-sided acceptance test (AR-3)

The previous criterion 3 required accepting the unmodified parent, which is impossible: the
parent blocks 118/240 with 35 raw D-1 and 6 raw D-4 episodes. Replaced by the staged test AR-3
proposes, adopted verbatim in substance:

1. The current parent is **expected to `BLOCK`**, and its measured debt stays visible.
2. A repaired reference descendant must reach raw D-1 = 0 and raw D-4 = 0 while satisfying every
   other active blocker and coverage requirement.
3. That repaired reference must be **accepted**.
4. A deliberately broken descendant must be **blocked by the intended detector**, not merely
   blocked.

A measured floor is a diagnostic, not an acceptance baseline, while the owner requires the floor
defects repaired.

## 7. D-9 (AR-2), resolved by repair rather than by tiering

AR-2 correctly objected that making D-9 report-only conflicts with the standing blocker set.
The calibration settles it differently: D-9's unpaired `banana_before_train` clause fired 196
times in a run where displacement is zero by construction, while all three paired clauses fired
zero. The clause is `DEFECTIVE`, so the repair is to **retire the proxy and keep the paired
clauses**, after which D-9 is an ordinary blocker requiring the same two-sided validation as any
other. No report-only status, no exemption. This matches chatgpt_1's own accepted-direction 6.

## 8. Provenance closure (AR-9)

A verdict without a complete dependency closure is structurally invalid and yields
`GATE_UNREADY`. The manifest must hash **every transitive input that can alter maps, commands,
state transitions, detector results, or verdict classification** — at minimum: candidate and
parent sources; `trace_detectors.py`; `fuzz_panel.py`; the map generator; the referee/engine;
semantic-harness and regression helpers; the config and seed set; the calibration-corpus
version; and recorded Python, Rust-toolchain and platform versions. A single "tool sha256" is
not a closure, and without one a referee or map-generator edit moves the floor while the
nominal key is unchanged.

## 9. Reporting discipline (AR-8)

Episodes and affected games are different metrics and are never conflated. Every count is
reported as **both**, e.g. "D-9: 196 episodes across 74 games". The 74/196 discrepancy that
consumed a review cycle was two correct numbers measuring different things.

## 10. What this revision does not settle

- The **repaired reference of §6 step 2 does not yet exist**; that is Phase 2 (D-4 localised
  and feasible, D-1 unresolved). Until it does, the two-sided test cannot run.
- **Phase 1 item 4 is largely already satisfied** and its premise was stale: the fixtures it
  calls for were committed on 2026-08-04, before the plan named them as missing. What remains is
  narrower — decide whether calibration validity can be positively demonstrated for the eight
  unrefuted detectors, rather than merely not refuted. See the correction to the allocation.
- The invariant blind spot — a design satisfying all 29 invariants while losing the way D89a
  lost — is Phase 1 item 6 (`chatgpt_1` specs, `claude_1` implements) and is not addressed here.
- I authored this and I run the host gates. It is adopted only when `claude_1` and `chatgpt_1`
  have each reviewed it, per my standing obligation.
