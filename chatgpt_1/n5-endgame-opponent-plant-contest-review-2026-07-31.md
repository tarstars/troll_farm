# Independent review — N5 endgame opponent-plant contest

- Reviewer: `chatgpt_1`
- Task: `20260730-n5-endgame-opponent-plant-contest`
- Reviewed coordinator base: `c2df655468a39c9f6f90da77a798f92b247ec6a8`
- Review date: 2026-07-31
- Empirical verdict under review: **`NO_MATERIAL_CONTEST_OPPORTUNITY`**
- Review disposition: **`BLOCKED_PENDING_PROTOCOL_CORRECTION`**

## Decision

The recorded population, generation-identity logic, carried-resource valuation, all-game
arithmetic, clustered bootstrap, verdict gates, and observational wording support the
reported `NO_MATERIAL_CONTEST_OPPORTUNITY` conclusion. I found no numerical contradiction
in the compact or machine results.

Unconditional acceptance is blocked because:

1. the frozen protocol requires synthetic lineage/outcome/access tests that the published
   six-test suite does not contain;
2. the field named `subject_eta_at_birth` is computed from the state immediately before
   the birth transition, while the protocol says “at birth.” The convention must be made
   exact and tested, or the audit must be recomputed from the post-birth state.

These are protocol-validation blockers, not evidence for a material opportunity. Neither
finding authorizes simulation, source policy work, or an Arena action.

## 1. Population and source integrity

The machine result records all **382/382 cohort occurrences** and 381 unique games. The
one cross-cohort game, `896350293`, is represented once per cohort as required. The input
manifest contains 382 occurrence rows, hashes each raw game and trajectory, reports no
missing input, and preserves the exact 242-resident / 140-yamo cohort lists.

The analyzer checks the frozen processed-index hash and record count, cohort-list counts
and ordered-ID hashes, reconstruction dependencies, and sacred resident source. It rejects
missing inputs, duplicate IDs within a cohort, decode failures, and state/trajectory turn
mismatches. The machine result reports no failures.

Exact H13 event counts reproduce:

| cohort | games | games reaching turn >250 | target generations | target games |
|---|---:|---:|---:|---:|
| resident | 242 | 170 | 388 | 78 |
| yamo | 140 | 103 | 205 | 37 |

The reported resident ratios follow exactly:

- `78 / 170 = 0.4588235294117647` target-game share of the reaching window;
- `388 / 170 = 2.2823529411764705` target generations per reaching game.

The second quantity is not “per target game”; the canonical report correctly calls it per
reaching game.

## 2. Target event and two-orientation identity

The target selection matches the literal H13 event in the implementation:

- subject-oriented generation origin is exactly `opponent`;
- successful birth turn is strictly greater than 250;
- the subject's bank-value margin in `states[birth_turn - 1]` is positive;
- the opponent-oriented counterpart has origin `actor` and the same generation ID,
  birth turn, cell, and species;
- both lineage states contain that generation at the birth cell;
- exactly one successful opponent-oriented PLANT event creates it.

The target-integrity gate rejects any selected row lacking unique-PLANT or cross-orientation
agreement. Both cohort summaries contain an empty integrity-failure list. Reconstruction
quality totals contain only actor/opponent births, with no published unknown or ambiguous
target population.

## 3. Extracted cargo is not banked score

`action_summary` selects successful HARVEST/CHOP events tied to the exact generation. It
sums gained fruit and gained wood, then reports

`extracted_score_equivalent = fruit + 4 * wood`.

This is cargo gained by a unit. It does not check a later DROP and therefore is not
terminal score. The protocol, analyzer docstring, machine report, canonical report, and
compact JSON all preserve that distinction.

Recorded totals are:

- opponent extraction from resident targets: **1,487** score-equivalent cargo units;
- resident extraction from those targets: **241**;
- positive opponent extraction: 262 targets in 75 resident games;
- resident material contact: 51/388 targets.

The 241 resident units are not subtracted from the factor-two quantity, making the frozen
valuation more generous rather than less.

## 4. Factor-two and denominator arithmetic

The primary quantity includes only targets marked reachable within their observed remaining
turns and assigns zero to all other targets and all non-target games. Its recorded total is
**2,902** swing units, implying 1,451 reachable opponent-extracted units:

- `2 * 1451 / 242 = 11.991735537190083` across every resident game;
- `2902 / 78 = 37.205128205128204` conditional on a resident target game.

The full opponent-extraction total is 1,487, so the current reach convention excludes 36
observed cargo units from the primary quantity. For scale, removing reach conditioning
entirely gives `2 * 1487 / 242 = 12.289256198347108`; this is not a substitute for the
frozen bootstrap gate.

The stricter never-contacted quantity is also internally exact:

- total missed-contact swing `= 2,496`;
- reachable opponent extraction on never-contacted targets `= 1,248`;
- `2496 / 242 = 10.314049586776859`.

The yamo descriptive value likewise reconciles:

- reachable opponent extraction `= 593` of 597 total;
- `2 * 593 / 140 = 8.471428571428572`.

Using all 242 resident games is essential. Conditioning on 78 target games would erase the
population frequency of the trigger and is not the frozen decision unit. The canonical
report states this correctly.

## 5. Whole-game uncertainty and verdict gates

The analyzer first sums target quantities within each game, produces exactly one row for
every cohort game including zero rows, and passes the 242 resident game-level values to a
20,000-replicate deterministic percentile bootstrap with seed `20260730`. Resampling is
therefore by whole game, not by target event.

The recorded resident interval is:

- mean: `11.991735537190083`;
- 95% percentile interval: `[8.727272727272727, 15.760330578512397]`.

The upper bound is `20 - 15.760330578512397 = 4.239669421487603` below the frozen gate.
All source/decode/target/support gates pass; the material lower-bound gate fails and the
strict no-material upper-bound gate passes. `decide_verdict` therefore returns
`NO_MATERIAL_CONTEST_OPPORTUNITY` exactly as the implementation specifies.

Yamo is calculated with the same definition but is not used as a verdict gate.

## 6. Observational and mechanic boundary

The result correctly avoids three invalid upgrades:

- enemy units can share cells, so “contest” is later HARVEST/CHOP access, not body-blocking;
- extracted cargo is not banked score;
- replay-conditioned realized yield is not the causal value or a theoretical upper bound
  of a changed policy.

A changed route can alter both players' positions, actions, crop growth, extraction, and
banking. The result therefore closes the current N5 lead under its frozen gate without
claiming literal zero value or authorizing a policy experiment.

## 7. Validation blocker — missing semantic tests

The frozen protocol asks for synthetic lineage, outcome, access, bootstrap, and verdict
tests. The current six focused tests cover:

- order-explicit cohort hashing;
- percentile interpolation;
- deterministic bootstrap mean behavior;
- no-material, material, overlap, and integrity verdict gates.

They do not directly exercise:

- successful-generation action extraction and cargo valuation;
- generation death/feller classification;
- BFS/ceil-div access semantics;
- strict turn-250 and positive pre-turn-margin selection;
- unique successful PLANT and cross-orientation agreement.

The analyzer self-test has the same bootstrap/verdict-only scope. Focused tests for the
missing frozen semantics are required before unconditional acceptance. If analyzer bytes
remain unchanged, this correction does not require a full-corpus rerun; if analyzer bytes
change, outputs and hashes must be regenerated.

## 8. Protocol mismatch — which state is “at birth”?

`reconstruct_generation_actions` creates a generation on turn `t` from the transition
`states[t - 1] -> states[t]` and stores it in lineage state `t`. The current access helper
uses subject unit positions from `states[birth_turn - 1]`, but the protocol and output
field call the quantity ETA “at birth.” `turns_remaining = game.turns - birth_turn` then
counts only turns after the birth transition.

This mixes a pre-PLANT position state with a post-birth remaining-turn budget unless the
protocol intentionally defines the diagnostic as the pre-turn decision state. The owner
must either:

- recompute from `states[birth_turn]`, add an indexing test, and refresh outputs/hashes; or
- explicitly freeze and document the pre-PLANT convention, rename/reword the field, and
  add a state-indexing test explaining the excluded simultaneous turn.

The exact verdict may remain stable, but protocol compliance cannot be inferred without
that resolution.

## Final disposition

The empirical evidence is numerically coherent and supports a no-material conclusion under
the implemented convention. The independent review is handed back as
`BLOCKED_PENDING_PROTOCOL_CORRECTION`, limited to the two issues above. After the owner
publishes a correction and validation evidence, a narrow re-review can decide unconditional
acceptance. Until then, no canonical closeout or successor experiment should be inferred
from this review.

## Safety

No analyzer, corpus, replay, trajectory, map, range, bulk artifact, simulator, source,
frozen result, panel, candidate, TestSession, submission, or Arena surface was executed,
opened, or changed by this review. Only this review and `chatgpt_1` coordination records
were written.
