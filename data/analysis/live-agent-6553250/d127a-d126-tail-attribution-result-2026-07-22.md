# D127a D126 tail attribution — result

Date: 2026-07-22  
Decision: **replace global threshold repair with proposal-specific value safety**

D127 exactly reproduces seed11903 and audits the failed D126 panel retrospectively. The initial
execution stops before writing a result because three NumPy gate logits are not JSON-serializable;
a separately locked mechanics-only cast fixes serialization without changing any model, offset,
metric, trace, or decision. Two repaired executions produce identical result bytes.

Global calibration cannot repair the tail. None of the 13 frozen offsets from `-0.10` through
`+0.50` passes all gates. At `-0.05`, mean remains `+2.820`, but norx is unchanged at `-4.281`.
At `+0.05`, norx improves to `-3.156`, but strict gains fall to 38.28%. Offsets `+0.40/+0.45`
finally lift the family floor above `-3`, while mean collapses to `+0.527/+0.707`, strict gains to
30.86%/30.08%, and only three/five families remain positive. Activity is not the root cause.

At the exact D126 threshold, 215 tasks intervene and 98 have negative terminal deltas. Attribution
is decisive:

- 82/98 losses are proposal-ranking errors: a positive exact proposal exists at the same root;
- 15/98 should abstain because every proposal at that root loses; and
- only 1/98 is a true act-now-versus-later timing error.

The ranking problem spans action types and all opponents, so a narrow hand-written action ban is
not supported. Norx is especially clear: all 13 losing norx interventions are ranking errors. The
chosen arms total `-248`, while the exact best proposals at those same roots total `+643`, leaving
`+891` points of same-root recoverable margin. Across all 82 ranking errors, selecting the exact
best same-root arm would recover 3,101 points.

The architectural cause is identifiable. D119 trains proposal logits with a listwise softmax over
exact advantages. That learns relative order but is invariant to adding a root-specific constant,
so it cannot express whether the selected proposal itself is safe. The state-only gate can know
that some proposal is valuable yet cannot verify that the ranker chose it.

Next keep D119's soft listwise loss, state gate, features, root balancing, 80 epochs, and compact
architecture, but add a root-balanced smooth-L1 anchor from every proposal logit to exact
`act_advantage / 10`. At runtime require both the state gate and a positive predicted value for the
selected proposal. This is an observable proposal-specific safety rule, not a terminal-label
shield. Test it first on fit data and the consumed D126 panel; only a structural and retrospective
pass can justify another untouched validation block.

Original lock SHA-256: `fb7bc776056695e8ec36d8e838c618a8ff625e8fc65da46e9702f2975fd07c94`  
Repair lock SHA-256: `0f73868c182d5f52c5b973e25145975f33fbb7478a1a30fe0e18e38137353690`  
Result SHA-256: `ad5cef897a88bbe87d7da285de65205f39585aa13f834238dfe3b665ed72369b`
