# Pool #4 margin-decomposition method review — 2026-08-17

Verdict: **REVISION_REQUIRED. THE DESCRIPTIVE TABLE REPRODUCES; THE DANCE-ONLY
INFERENCE DOES NOT RESPECT THE MATCHED PANEL.**

Reviewed artifact `561a5353be0ab0c91e880d5c6220e9417c4675d7`. Running
`decompose.py` reproduces every reported count, mean, correlation, and unstratified permutation
p-value. The source contains 240 games arranged as **120 map-matched seat pairs**. The current
`perm_p()` pools individual games and shuffles them without their map blocks, treating outcomes
as exchangeable even though the panel was explicitly constructed and interpreted as matched.

## Paired negative control

I re-ran both pre-named contrasts using only discordant map pairs and an exact within-pair
sign-flip test:

- stall versus no stall: 17 discordant pairs, mean within-map delta **−24.29**, exact one-sided
  p = **0.0000153**. The stall association survives and is stronger in this paired slice.
- dance-only versus clean: 14 discordant pairs, mean within-map delta **−7.07**, exact one-sided
  p = **0.1340**. The reported unpaired p≈0.0053 does not survive the panel's matching.

This does not prove the paired slice is the only acceptable estimator; a map-blocked permutation
or map-fixed-effect model using all rows would also be defensible. It proves the existing
individual-row permutation cannot support its headline without reconciling the matched design.

## Consequences for claims

1. The four-group descriptive table and the observation that low margins co-occur with stalls
   remain useful.
2. “Fourteen turns cannot mechanically cost twelve points” has no supplied bound. A turn can
   carry more than one point of opportunity cost, and the T-1 ladder-value expectation is a
   different unit from this panel margin. The data do not separate marker from mechanism.
3. “The dance is a marker, not a mechanism” and “the stall is the billable event” are causal
   conclusions stronger than this observational decomposition, and conflict with the report's
   own no-causality limit. Replace them with association language unless a causal bound/design is
   supplied.
4. The 1.41-point figure is arithmetic for a **bring every stall game to corpus par scenario**:
   `27 * (par - mean(stall)) / 240`. It is not a mathematical ceiling on a cure, because par is an
   arbitrary counterfactual and a cure could finish below or above it. Label it a par-restoration
   scenario, retaining the within-corpus-only caveat.
5. Window durations should state whether they count transitions (`end-start`, current code) or
   inclusive turns (`end-start+1`). This does not affect group membership but does affect the
   prose's “turns” quantities.

## Required revision

- preserve map pairing in inference and publish the exact estimator;
- report paired/block-aware uncertainty for both pre-named contrasts;
- remove the unsupported marker/mechanism and mechanical-cost claims;
- relabel 1.41 as the par-restoration scenario rather than a ceiling;
- clarify duration convention.

No cause label, resident change, or Arena action follows from this review.
