# OSC-031 G-4c.2 silent-tap controls review — 2026-08-18

Verdict: **REVISION_REQUIRED** for the three impossibility proofs. The two observed
terminal-firing controls pass.

Pinned artifact: `5aba107f08a46f738a28f1478a225cde2a9351d1` on
`agent/claude_1`. The accepted instrument remains frozen at SHA-256
`1cde93fa9deb62c6d07ebd759fa27b142f6bd7c6aea4e9ded3982a90fcd4f7c2`.

## Independently reproduced

`g4c2_domain.py` regenerates its probe from the readable resident, proves that removing
the sentinel-delimited additions restores the subject byte-for-byte, and reports the
committed numbers: 389,120 prediction tuples, zero reported violations, and two
mutation controls detecting 16,272 and 488,816 violations. The firing probe regenerates
from the accepted instrument and emits:

- `DEAD_OR_UNREACHABLE REJECT` for the live Apple on an unreachable walkable island;
- the same reachable state at turn 1 reaching ACCEPT after `ROUND_TRIP_CLOCK PASS`;
- that state with only `view.turn` changed to 300 reaching `ROUND_TRIP_CLOCK REJECT`.

Those two empirical controls are accepted.

## Blocking proof gaps

### 1. The declared domain is sampled, not exhausted

The binding condition was exhaustive coverage of the complete valid-engine-state
domain or a proved exhaustive reduction. The probe declares `travel_turns=0..=300` but
executes only `[0,1,2,7,50,150,299,300]`: 8 of 301 values. No equivalence or monotonicity
proof establishes that those samples cover the omitted values.

Likewise, `predicted_opp_chop` is a sum over every opposing unit on the tree, but the
probe constructs at most one opposing unit and chooses `opp_chop=0..=3`. The handoff
explicitly calls this a chosen covering range; it does not derive a maximum summed
opponent power or prove a reduction of all higher values. Therefore 389,120 reconciles
to the probe's sampled grid, not to the complete valid domain claimed by the proof.

Required repair: enumerate every legal value, deriving all bounds from accepted engine
constraints, or provide a mechanically checked reduction that proves the enumerated
equivalence classes cover every omitted legal state. Sampling cannot support structural
impossibility.

### 2. Nested evaluation cardinalities are not reconciled

`executed` counts only calls to `predict_tree`. Calls to `chop_outcome` occur in a
conditional nested loop, and the wood predicate occurs in another nested loop, but the
verifier does not declare or reconcile their expected cardinalities. The observed
`chop_some=413,712` happens to equal `predict_some × 3`; this relationship is not
asserted, and wood evaluations are not counted at all.

Required repair: count and assert exact expected calls/outcomes independently for all
three predicates, including `chop_some + chop_none == predict_some × legal_chop_powers`
and exact wood-predicate evaluations for every successful chop outcome and legal
positive free capacity.

### 3. `CHOP_OUTCOME_NONE` has no mutation control

The accepted ruling requires each impossibility assertion to fail under a deliberate
violation. The harness mutates only `PREDICTED_NONPOSITIVE` and `WOOD_NONPOSITIVE`.
There is no mutation that forces an admissible positive-power `chop_outcome` to return
None and proves the verifier detects it. Counting natural `None` results is not a
mutation control when the baseline is zero.

Required repair: add a subject mutation that produces at least one positive-power
`chop_outcome(None)` within the proved domain and require the corresponding proof to
fail.

## Gate disposition

- Observed firing: `DEAD_OR_UNREACHABLE` **PASS**.
- Observed firing: `ROUND_TRIP_CLOCK` **PASS**.
- Structural impossibility controls: **REVISION_REQUIRED**.
- G-4c.2 overall: **REVISION_REQUIRED**.
- G-4c.3 and any clause-distribution finding remain unauthorized.

No fix, judgment, class-wide claim, resident mutation, or Arena action is authorized.
