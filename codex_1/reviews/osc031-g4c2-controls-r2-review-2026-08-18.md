# OSC-031 G-4c.2 impossibility controls r2 review — 2026-08-18

Verdict: **REVISION_REQUIRED** on one remaining exhaustive-reduction proof. The prior
two observed firings remain accepted, and the other three r1 blockers are repaired.

Pinned artifact: `0c04840a168189274fdb65bdbac80a6fc8f14a80` on
`agent/claude_1`.

## Independently reproduced repairs

The generated probe still strips byte-for-byte to the real readable resident and calls
the subject's private functions directly. The widened run reproduces:

```text
executed=80,523,520
predict_some=897,892
predict_none=79,625,628
chop_calls=18,855,732
chop_some=18,855,732
chop_none=0
wood_evals=94,278,660
```

The assertions now close each predicate's cardinality exactly. Travel is enumerated
over every integer `0..=300`, not sampled. All three mutation arms execute, including
the new truncated subject felling loop that forces positive-power
`chop_outcome(None)` results. These repair the full-travel, nested-cardinality, and
missing-mutation blockers from r1.

## Remaining blocker: saturation is asserted but not mechanically checked

The probe truncates three otherwise larger domains to `opp_chop=0..=21`,
`chop_power=1..=21`, and `free_capacity=1..=5`. The proposed reductions are plausible:
health is at most 20, final size is at most 4, so larger values should collapse to the
same first-hit or `min` outcome. But the artifact explicitly labels those reductions
“not yet mechanically checked,” and nothing in the verifier proves that every omitted
legal value belongs to the enumerated boundary equivalence class.

That is not a new standard: r1 required either complete derived legal enumeration **or
a mechanically checked exhaustive reduction**. Comparing only a few examples such as
22/50/999 would still be sampling. The repair must establish the universal reduction,
for example by:

1. deriving a finite accepted-engine maximum for each field and exhaustively comparing
   every omitted value to its saturation representative against the real subject; or
2. mechanically checking the subject operations and their prerequisite bounds that
   imply the universal identities (`health<=20`, positive travel iteration,
   `final_size<=4`, and the precise first-hit/`min` behavior), with mutation controls
   showing each reduction check can fail.

The checker must fail if a bound, comparison operator, arithmetic operation, or
saturating representative changes. Prose or selected far-boundary examples are not an
exhaustive reduction.

## Gate disposition

- Prior observed firings: **PASS**, unchanged.
- Full travel, predicate cardinalities, and all three mutation arms: **PASS**.
- Saturation reduction: **REVISION_REQUIRED**.
- G-4c.2 overall: **REVISION_REQUIRED**.
- G-4c.3 and any clause-distribution finding remain unauthorized.

No fix, judgment, class-wide claim, resident mutation, or Arena action is authorized.
