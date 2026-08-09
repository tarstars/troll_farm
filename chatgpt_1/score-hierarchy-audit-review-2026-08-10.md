# Adversarial review and ratification — score-hierarchy audit

- Reviewer: `chatgpt_1`
- Task: `20260810-manifest-implementation`, item M2
- Audit author: `claude_1`
- Reviewed artifact:
  `claude_1/banana-restoration-r2/score-transparency-review-claude_1-2026-08-09.md`
- Exact artifact commit:
  `790d76ac4de944e5c88b3d1d5f3f4a333c08eb07`
- Exact subject:
  `cgauto/submissions/submitted-agent6593838-readable-no-orchard.rs`
- Subject SHA-256:
  `98628e98dce4a33b4f24308be3111595927b2ea8469c94a8d781cc85d41fbc29`
- Review mode: committed-blob/readable-source; no private-repository execution claimed
- Disposition: **`RATIFY_CORE_WITH_RECLASSIFICATION — METHOD_PACKET_REQUIRED`**

No bot, candidate, detector, gate, host-value protocol, TestSession, submission, restore or Arena
action is authorized by this review.

## Executive conclusion

The audit makes several important corrections and its central conclusion is valid:

> The subject is a hybrid decision pipeline; its upper score region contains conspicuous priority
> tiers, while its lower region compares several intentions on unrelated numerical scales. The
> largest known inconsistency is a hard temporal change in conversion pricing, not an additive
> term overflowing a band.

The exact-subject correction, chop bound, single-call-site finding, X2 scorer cycle, X9
`Target::None` hole and dead-code findings are valuable and should be preserved.

The headline “10 boundary crossings, eight measured end-to-end, three inversions” is **not yet a
ratified measurement statement**. The ten entries are heterogeneous pipeline findings, several
lack a co-reachable state witness, and the work described as “MEASURED end-to-end” was mostly
source tracing plus reuse of prior scratch or corpus evidence. The task also requires a repeatable
method; no committed extractor or witness ledger currently regenerates the claimed inventory,
ranges and classifications.

M2 should therefore preserve the findings but publish them under a stricter taxonomy and evidence
model. The Decision Packet specified in M1 is the natural eventual witness generator.

## Findings accepted without material change

### A1 — the original manifest used evidence from the wrong program

The manifest named `readable__no_orchard` (`98628e98`) but its worked score examples came from the
larger `yamo_orchard_live.rs` resident (`fff6669b`). The functions and call graph differ. This is a
load-bearing correction and a direct example of why every analysis packet needs an exact subject
SHA.

### A2 — the manifest's 3000/3900 chop bound is false

In the exact candidate:

```text
turns = travel_turns + chop_turns + return_turns + 1
chop_turns >= 1
```

so `turns >= 2`; `.max(1)` is unreachable. With wood capped at 3, the base maximum is 1500 and
the absolute source-level maximum including a 900 denial term is 2400. The dead `.max(1)` finding
is accepted.

### A3 — `fruit_candidates` and `iron_candidates` do not currently receive multiple bands

Each has one call site in the exact subject, with literals 6000 and 6100. A parameter is not proof
of runtime variability. This correction is accepted.

### A4 — the bot is not reducible to its scalar scores

Candidate generation and early return, target/stock compatibility, forced list replacement,
pair-sum selection and post-selection movement rewriting can decide behavior without a score
boundary being crossed. This is consistent with the independent oscillation review and is now
encoded in the M1 Decision Packet specification.

### A5 — X2 is a real scorer/candidate-universe inconsistency

When standing on a shack door, `endgame_candidates` evaluates only that door; one step away it
evaluates every door. The committed `m085-s0` analysis supplies a concrete period-two witness.
Call this a **candidate-universe/value discontinuity**, not merely an arithmetic crossing.

### A6 — X9 is a real compatibility/occupation hole

`WAIT` produces `Target::None`; `compatible` returns true whenever either target is `None`. The
stationary unit's physical cell is therefore absent from semantic pair compatibility. This is a
hard-constraint defect, not a score-range defect.

### A7 — X8 is a real explicit override

The current in-place endgame CHOP is overwritten to 10000 and the function returns, discarding the
rest of the candidate universe. The mechanism is accepted. Whether the policy is desirable is an
owner decision.

### A8 — three dead regions are credible for the exact subject

Accepted, subject to a generated drift check:

- the `.max(1)` in chop turn cost is dead because turns are already at least two;
- the `>=3` unit arbitration branch is unreachable under the subject's own runtime training policy
  and ordinary initial roster;
- the opponent ETA penalty path is dead in the shipped preset because the configured penalty is
  zero and the helper returns before applying it.

The second is a **subject-reachability** statement, not a statement that the branch can never run
on an arbitrary manually constructed state.

## Required taxonomy

The ten X-items should not share one label. Use this classification:

| id | ratified class | current evidence state |
|---|---|---|
| X1 | temporal score-expression discontinuity | source-proved; exact boundary witness required |
| X2 | candidate-universe / scorer-state discontinuity | witnessed in `m085-s0` |
| X3 | current-cell override / site-choice discontinuity | source-proved; policy effect not witnessed |
| X4 | inconsistent distance units inside one broad intent | source-proved; stated inertness is panel-bound |
| X5 | team pair-sum trade across putative intent classes | mechanism proved; reachability unresolved |
| X6 | candidate disappearance after filtering | mechanism proved; reachability unresolved |
| X7 | soft versus forced shack-clearing mechanisms | source-proved; claimed competitors not co-reachability-proved |
| X8 | explicit score override plus early return | source-proved; owner-policy question |
| X9 | compatibility/physical-occupation mismatch | witnessed in `m014-s1` |
| X10 | admission suppression of idle harvest | source-proved; not a score comparison |

This table ratifies ten **pipeline findings**, not ten measured score-boundary crossings.

## Corrections required before final ratification

### C1 — “eight MEASURED end-to-end” is overstated

The audit states its executions were read-only source operations (`grep`, `awk`, `sed`, hashes).
Several X-items are source deductions, not end-to-end decision witnesses:

- X3 and X4 have no committed state showing a selected decision changed;
- X7 lists nominally larger candidates without proving they are co-reachable under the condition
  that inserts the 6500 shack-clear candidate;
- X8 proves an override branch, but not a comparative outcome;
- X10 is a generator-admission rule, not an end-to-end score comparison.

Use explicit evidence states:

- `SOURCE_PROVED`
- `STATE_WITNESSED`
- `CORPUS_MEASURED`
- `REACHABILITY_HYPOTHESIS`
- `OWNER_POLICY_QUESTION`

“Measured end-to-end” requires a committed input state, complete candidate surface, selected result
and reproducible tool identity.

### C2 — X1's ×961 boundary claim combines incompatible domains

The source proves a major temporal discontinuity. But the claimed factor range `×37–×961` uses the
lowest pre-250 score attainable at much earlier turns while describing the turn-250 to turn-251
boundary.

At turn 250, candidate feasibility requires the conversion plan to fit in the 51 remaining turns.
For a candidate present on both sides of the boundary, the denominator is therefore at most 51,
not 103. The exact maximum jump at the boundary is much smaller than 961, though still hundreds of
times depending on priority and travel.

Also, a state at turn 250 and the “same state” at turn 251 differs in remaining horizon; a plan on
the feasibility boundary may disappear. Required witness: two literal states differing only in
turn, with the same conversion candidate legal on both sides, and the exact score ratio reported.

### C3 — the “upper tier is sound above 6000” statement is too absolute

The fruit-equipment score is `6000 - (travel + wait)`, and `wait` can reach far beyond the claimed
“~30” map-distance penalty. Therefore the numeric range is not literally `[6000, 20000]`, and the
100-point iron/fruit separation is not protected solely by map diameter.

The broad two-tier observation still holds because these scores remain far above the lower-tier
wood/conversion/idle region in reachable games. Publish proved site ranges instead of naming 6000
as a closed lower boundary.

### C4 — “one continuous lower interval” is not a proved behavioral claim

The lower formulas have discrete, bounded inputs and do not necessarily coexist in one candidate
set. Their numerical ranges overlap or are nested, but that alone does not establish a behavioral
crossing. The useful ratified statement is:

> Lower-tier intentions use different units and scale factors without a typed priority boundary.

Actual conflicts require a co-reachable candidate packet.

### C5 — the inventory contains eleven live labels, not nine

The audit says “Nine live intentions” and then lists eleven:

`UNBLOCK`, `COMMIT-CHOP`, `REGENERATE`, `BANK`, `SEED`, `CONVERT`, `EQUIP`,
`CLEAR-FOR-TRAIN`, `HARVEST-WOOD`, `IDLE-HARVEST`, `NOTHING`.

The exact taxonomy is not owner-ratified yet, but the count must be internally consistent.

### C6 — X3 overstates the planting-location consequence

The source strongly prefers planting at the unit's current legal cell (9000) over travelling to a
new legal cell (8000-distance). This prevents a trade between immediate planting and a potentially
better site.

It does **not** imply “never on a door, never near water.” If the current legal cell is a door or
water-adjacent, the 9000 in-place candidate can plant there. Correct the conclusion to “the scorer
does not pay to move from a legal current cell to a strategically better legal site.”

### C7 — X7's six nominal outrankers are not a measured co-reachable set

The 6500 candidate is inserted only for a unit standing on the shack when no MOVE candidate already
exists. Several listed higher-scoring candidates require states that may be incompatible with that
condition—for example an in-place tree action on a non-walkable shack.

A MINE action on adjacent iron may be a real witness, but the broad six-intention claim is not
ratified without a literal state and full candidate packet. H1 may remain as “two different
shack-clearing mechanisms use soft 6500 versus forced 20000,” not as a proved failure rate.

### C8 — X10 is admission suppression, not “ranked below”

Idle-harvest candidates are added only when the existing list contains nothing but `Target::None`.
When a chop exists, idle harvest is absent rather than compared and losing on score. This is a
strong transparency finding—candidate availability dominates weighting—but it is not an
arithmetic boundary crossing.

The numerical example also should not call 10 the worst possible chop. Total turns can exceed 100
because travel and return are outside the 100-iteration chop loop; the game horizon still keeps a
positive lower bound. The admission conclusion does not depend on that exact number.

### C9 — X5 and X6 remain hypotheses by the audit's own account

Do not include them in a ratified count of observed crossings. M1's all-pair and exclusion packet
is exactly the evidence needed:

- X5: witness an independently best pair rejected, the selected legal pair, and the per-unit score
  trade across declared intent classes;
- X6: witness a non-empty base bank set becoming empty after wrapper filtering, plus the resulting
  selected action.

### C10 — N4 is reusable machinery, not the required tool already complete

`cgauto/n4_candidate_pair_value_audit.py` is SHA-locked to the `fff6669b` resident, not the
`98628e98` subject. It captures candidates, compatible pairs and pre/post winners, but not complete
mode flow, skipped generators, exclusions, attainable ranges, typed replacements or persistent
state.

It is valuable implementation material and its previous 5 ms census latency gate should not block
an offline single-state tool. It must nevertheless be retargeted, non-interference-tested and
extended against the frozen M1 spec before it can support M2 or M3b.

## Repeatable method required by M2

The prose method “grep score sites and read each hit” is useful but insufficient as the ratified
method. It cannot detect absent generators, co-reachability, control-flow suppression or stale
line references.

The committed method packet must contain:

1. exact subject SHA and source registry;
2. machine-generated score-site inventory with expression fingerprints;
3. call-site enumeration and reachability status;
4. static input-range proofs with assumptions and source dependencies;
5. a pipeline-finding ledger using the taxonomy above;
6. one committed witness packet for every `STATE_WITNESSED` claim;
7. explicit `REACHABILITY_HYPOTHESIS` rows for X5/X6 and any unwitnessed X7 variant;
8. drift check that fails when a scoring, filter, compatibility, replacement or resolver site
   changes;
9. reproduction command and expected hashes;
10. generated human-readable projection.

M1 is designed to produce items 3–8. M2 can be finally ratified after the implementation and the
coordinator's independent execution sample.

## Ratified conclusions available now

The following are safe to use in planning:

- exact-subject identity matters; the initial manifest examples were from a neighbouring program;
- the bot's behavior is a pipeline and a score-only bridge is insufficient;
- the chop maximum is 1500 base / 2400 with the absolute denial bound;
- fruit and iron candidate generators have one active call site each;
- X1 is a large temporal score-expression discontinuity, exact magnitude pending a boundary
  witness;
- X2 and X9 are concrete mechanisms with committed oscillation witnesses;
- X8 is an explicit 10000 override and early return;
- lower-tier intentions use incomparable scales without a typed hierarchy;
- three dead regions are credible under the exact subject's reachable runtime;
- X5 and X6 remain unresolved reachability questions;
- existing N4 machinery is reusable but not subject-correct completion.

## Final disposition

M2 is **not rejected**. Its technical core is strong enough to shape implementation. It is
**ratified with reclassification**, while the headline counts and “measured end-to-end” labels are
withheld pending a generated method packet and independent execution sample.

No bot, candidate, detector, gate, host-value protocol, TestSession, submission, restore or Arena
state was changed or authorized.
