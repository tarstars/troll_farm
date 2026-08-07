# Independent review — acceptance-gate re-design

- Reviewer: `chatgpt_1`
- Task: `20260807-gate-architecture-review`
- Task record: `coordination/tasks/20260807-gate-architecture-review.md`
- Claim: `coordination/messages/chatgpt_1/20260807T102000Z-20260807-gate-architecture-review-claim.md`
- Artifact reviewed: canonical `agent/claude_1` commit
  `3ca092abba353b4dd07b63e85f6d25deb9852d0d`
- Primary document: `claude_1/pipeline/design-gate-redesign-2026-08-07.md`
- Supporting evidence:
  - `claude_1/pipeline/verification/fable-verification-2026-08-06.md`
  - `claude_1/pipeline/verification/fable-verify-floor-calibrated.md`
  - `local_claude_1/verification/README-floor-selftest-2026-08-07.md`
  - `local_claude_1/verification/local_claude_1-floor-selftest-result-2026-08-07.json`
- Verdict: **`REVISION_REQUIRED`**

## Executive conclusion

The proposal correctly identifies that the current gate mixes absolute safety, lineage
regression, and harness calibration. Its mandatory floor self-test, provenance manifest,
`UNPROVEN` status for unexercised detectors, and insistence on bite-tests are valuable and should
be retained.

The proposed acceptance semantics are nevertheless internally inconsistent and directly
incompatible with the owner's binding rule. The design classifies D-1 and D-4 as tolerant Tier B
checks, allows a waiver ledger and floor-relative deltas, and requires the unmodified parent to
be accepted. The owner instead requires raw D-1 = 0 and raw D-4 = 0 with no waiver or
parent-relative exemption, and has accepted that the parent lineage must be repaired first.
Those requirements cannot both hold.

The design also treats the waiver ledger as semantically different from the banned exemption,
uses an underdefined candidate-dependent tier computation, and gates on per-map counts in a way
that can replace one failure with another. These are architecture defects, not implementation
details.

## Accepted directions

Preserve the following in the revision:

1. A floor self-test is mandatory and drift must abort without a verdict.
2. A verdict without a complete hash-bound manifest is structurally invalid.
3. D-2, D-3 and D-8 are `UNPROVEN`, not passing, until committed bite-tests exercise them.
4. The safety/regression/calibration taxonomy is useful and should be made explicit in the
   machine contract.
5. Aggregate totals must not let improvement on one map conceal a new failure on another.
6. D-9 should eventually test the causal world-state claim rather than the current
   banana-before-TRAIN proxy; detector ownership and the exact predicate remain referred to
   `local_codex_1`/the integrator.

None of these accepted directions authorizes a gate, detector, candidate, or workflow change.

---

## AR-1 — D-1/D-4 Tier B and waivers violate the binding owner rule

Sections 4.2–4.6 classify D-1 and D-4 as Tier B and permit acceptance when their per-map delta is
non-positive or when an episode is listed in the waiver ledger. Either path permits nonzero raw
D-1/D-4 episodes.

The task's binding constraint is the opposite:

- raw D-1 must be zero;
- raw D-4 must be zero;
- no inherited-parent, aligned-prefix, ledger, or other exemption may touch either detector.

Required revision: D-1 and D-4 must be hard, pre-tier absolute conditions. They do not enter the
waiver ledger, floor-relative comparison, or quarantine machinery. Any run with one D-1 or D-4
episode is `BLOCK`.

This finding is explicitly **incompatible with the owner's standing strict rule** as the proposal
is currently written.

## AR-2 — making D-9 report-only also conflicts with the standing blocker set

The task record says D-5 through D-9 remain active. Section 4.3 places D-9 in Tier Q and section
4.6 makes Tier Q report-only. That changes the acceptance effect even though the detector
predicate itself is untouched; the statement in section 6 that no predicate is weakened does not
answer this gating change.

If the current D-9 predicate is miscalibrated, the honest verdict is `GATE_UNREADY` or
`UNIDENTIFIABLE` until the referred detector fix is ratified and bite-tested. It is not valid to
obtain an `ACCEPT` by silently removing a standing blocker from the verdict.

The same principle applies to D-8: while it is unexercised, the gate may report `UNPROVEN`, but it
cannot certify the full standing blocker set without either a passing bite-test or an exact owner
exception.

This finding is also **incompatible with the owner's standing rule** as the proposal is currently
written.

## AR-3 — criterion 3 is impossible with the current parent

The independently established floor is:

- parent versus itself: `BLOCK 118/240`;
- raw D-1 episodes: 35;
- raw D-4 episodes: 6.

Therefore the unmodified parent cannot be accepted under the binding zero-episode rule. Section 8
criterion 3 requires the opposite and is not achievable.

Replace the criterion with a staged two-sided test:

1. The current parent is expected to `BLOCK`, and its measured debt remains visible.
2. A repaired reference descendant must first reach raw D-1 = 0 and raw D-4 = 0 while satisfying
   every other active blocker and coverage requirement.
3. That repaired reference must be accepted.
4. A deliberately broken descendant must be blocked by the intended detector/bite-test.

The floor self-test may continue to measure the current parent, but a measured floor is not an
acceptance baseline while the owner requires the floor defects to be repaired.

## AR-4 — the waiver ledger is more auditable, but not semantically different

A finite, hash-pinned, owner-ratified ledger is operationally better than an invisible runtime
comparison. It is inspectable, reviewable, and reproducible.

It is still an exemption: a matching episode becomes nonblocking because an older parent episode
was approved. A new causal defect can produce the same `(seed, map_id, detector,
episode_signature)` and be hidden by that entry. The proposal's claim that a new defect cannot
hide in an enumerated list is therefore too strong.

For D-1/D-4 the ledger is forbidden outright. For any other detector where the owner permits an
exception, the revision must at least require:

- a precise normalized signature and multiplicity, not only detector/map identity;
- proof of the cause being waived, not merely reproduction by the parent;
- an exact ratification message path and commit;
- an owner, expiry/sunset condition, and removal test;
- a negative control showing that a nearby but causally different episode still blocks;
- an explicit non-`CLEAR` debt status if accepted behavior still violates an invariant.

Without these conditions the ledger is the banned mechanism with better bookkeeping, not a new
acceptance principle.

## AR-5 — neither count delta `<= 0` nor count delta `= 0` is sufficient

Section 4.6 says per-map `delta <= 0`, while section 7 says this permits trading a failure on map X
for a fix on map Y. If the delta is genuinely computed per map and detector, cross-map trading is
already impossible. The stated justification and the proposed rule do not describe the same
quantity.

Count-only per-map comparison has a different defect: the candidate may remove one episode and
introduce a different or more severe episode on the same map while keeping the count unchanged or
lower. Requiring `delta = 0` would avoid neither substitution nor severity changes, and would also
reject genuine fixes that reduce the count.

Required revision for any owner-permitted comparative detector:

- compare normalized episode **multisets**, not only counts;
- require every unwaived candidate episode to be contained in the ratified floor set for that
  exact map/seat/detector;
- forbid multiplicity or severity growth;
- allow removal of old episodes;
- record new signatures separately even when the aggregate count falls.

D-1 and D-4 remain raw zero and do not use this mechanism.

## AR-6 — tier computation is underdefined and candidate-dependent

Section 4.1 says the floor self-test is parent versus parent. Section 4.2 then requires variance
"across candidates," and section 4.2 says the tier is recomputed by the tool each run. A floor run
alone cannot compute candidate variance. The set denoted by "candidates" is not specified.

If the current candidate participates in its own tier assignment, acceptance semantics change
with the submission: a candidate may turn a detector into Q or U merely by matching the floor.
That is circular and gameable.

Required revision:

- define a frozen, hash-pinned calibration corpus containing the parent, positive bite-tests, and
  deliberately broken controls;
- derive tiers only from that corpus and the ratified detector contract;
- version the resulting tier manifest independently of candidate evaluation;
- abort on calibration-corpus drift;
- never let the candidate under review choose or change its own detector tier.

Counts alone also cannot establish detector validity. Every blocking detector needs both positive
and negative oracle tests; bite-tests are not only for Tier U.

## AR-7 — Q and U need a gate-readiness state, not automatic report-only status

A detector can have zero variance because the calibration corpus is too narrow, not because the
detector carries no useful information. Likewise, zero observed episodes can mean missing state
coverage.

The proposed rule makes Q always report-only and contains the malformed condition "no Tier-A/B
detector is in tier U" even though tiers are mutually exclusive.

The revision should define a separate required-blocker set. If a required blocker is Q because its
predicate is known defective, or U because it is unexercised, the overall result is
`GATE_UNREADY`/`UNPROVEN`, not `ACCEPT`, unless the owner grants an exact exception. This is how the
gate remains honest without pretending an unmeasured property passed.

## AR-8 — the D-9 statistics are different metrics, not different calibration stages

The apparent discrepancy is reconciled:

- Claude's `74` is the number of **game rows containing at least one D-9 violation**.
- The coordinator's `196` is the sum of the individual D-9 **episodes** across those rows.

The calibrated floor report contains D-9 rows with `count: 2` and `count: 4`, so one affected game
can contribute several episodes. The same distinction explains the design table's D-1 `32`
versus the host total of `35` episodes, and D-6 `9` versus `15` episodes.

Section 4.3 therefore labels game-incidence counts as detector "floor" counts without saying so.
The revision must carry at least three separate quantities:

1. affected games;
2. total episodes;
3. normalized per-map/seat episode-signature multisets.

Equal affected-game counts (`74`) do not by themselves prove that D-9 is candidate-invariant. The
zero-information claim needs equality of the map/seat set and episode kinds/multiplicities across
floor, `bbe54a48`, and tip, or a direct causal proof from the detector predicate. Until that is
shown, section 5 is directionally plausible but not established strongly enough to drive Q
classification.

## AR-9 — the FST hash key omits material transitive inputs

Section 4.1 keys the floor on parent, detector module, config and seed set. The panel also imports
and depends on the panel runner, map generator, referee, semantic harness, regression helpers,
Python/Rust toolchains, and possibly compiler behavior. Section 4.7's singular `tool sha256` is
not a complete dependency closure.

The manifest must enumerate and hash every transitive code/config input that can alter maps,
commands, state transitions, detector results, or verdict classification. Environment versions
must also be recorded. Otherwise a referee or map-generator edit can move the floor while the
nominal FST key remains unchanged.

---

## Achievable revised architecture

A coherent next draft can use the following order:

1. Run a fully dependency-bound floor self-test; drift aborts.
2. Enforce raw D-1 = 0 and raw D-4 = 0 as unconditional hard gates.
3. Require every standing blocker to be calibrated and exercised; unresolved Q/U blockers make
   the gate unready rather than green.
4. Use absolute zero for valid safety detectors.
5. For explicitly owner-approved comparative detectors only, use signature-multiset dominance
   against a frozen calibration floor; do not use candidate-selected tiers.
6. Keep any exception ledger outside D-1/D-4, with causal evidence, exact ratification, expiry,
   and visible debt status.
7. Accept only a repaired reference that satisfies the strict gate, then prove a broken
   descendant is rejected.
8. Emit a complete dependency/provenance manifest with every verdict.

## Reproduction and evidence boundary

I performed no host rerun. The task record authorizes reliance on the independently established
floor facts. The exact committed coordinator reproduction is:

```bash
cd claude_1/pipeline
python3 fuzz_panel.py \
  --config /home/tarstars/prj/troll_farm-local_claude_1/local_claude_1/verification/local_claude_1-floor-selftest-config-2026-08-07.json \
  --report <report-path> \
  --json <result-path>
```

Recorded/verified inputs:

- candidate and parent SHA-256:
  `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`;
- executed `fuzz_panel.py` SHA-256:
  `cc7db6f2f048a1739e587cff9e26e5783d08f69672e233b227a6294f03b6571d`;
- committed floor-config SHA-256, calculated from the exact committed bytes:
  `cd56eae54a46213e416c46972ef953c84a72b47ad238db52d9fa0f7fa03f92ad`;
- source base-config SHA-256 recorded by the coordinator:
  `f5394e7a8b974062b07f42bc535e113dca2e9d67b64c9b196c1a4b63660b99fe`.

The coordinator record does not hash every imported dependency or toolchain component; AR-9 is the
consequence. I make no additional quantitative execution claim beyond the task's established
facts and the metric reconciliation visible in the committed reports.

## Final verdict

**`REVISION_REQUIRED`.**

The draft contains valuable measurement architecture, but it cannot be accepted until the strict
D-1/D-4 rule, active D-5..D-9 blocker set, tier calibration, waiver semantics, per-map comparison,
two-sided criterion, statistic definitions, and provenance closure are made mutually consistent.

No gate, detector, candidate, workflow, host run, value protocol, TestSession, submission,
restore, or Arena action was performed or authorized by this review.
