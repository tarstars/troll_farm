# D62a deployable-balanced parity amendment (2026-07-21)

## Trigger

Before the D62 environment parity run, source inspection found that the frozen phrase “constant
balanced ... match the corrected D61 matrix” names two different D61 semantics.

The corrected D61 `safe_balanced` row is intentionally a direct-D40 no-option anchor: it bypasses
the last-own-crop renewable filter at every Rate decision. In contrast, every deployable D61
linear policy—including one whose state-dependent argmax is `balanced`—passes its selected mode
through `renewable_safe_action`. D62 represents the latter learned-policy path. Comparing its
balanced action with the special control row would either reject an exact implementation or force
the learned controller to use the wrong semantics.

This is discovered before any D62 parity result, optimizer update, or checkpoint exists.

## Sole repair

Keep D62 environment behavior unchanged and make the balanced reference explicit:

- construct a supplemental 69-row D61 population by replacing exactly `linear_00` with a
  zero-weight linear policy named `d62_zero_linear_balanced_reference`;
- retain every other population row byte-for-byte and retain the D61 runner unchanged;
- because D61's frozen strict tie rule starts from `balanced`, the zero-weight linear row selects
  `balanced` at every batch while still traversing the deployable renewable-safe path;
- run the unchanged D61 runner on seed 9,801,000, one map, both seats, all eight opponents;
- compare D62 balanced episodes to that supplemental linear row; and
- compare D62 harvest, renew, and fell episodes to the corrected D61 constant rows.

Require terminal own/opponent scores, own workers, created crops, action hash, and state hash to
match on all 64 mode-task pairs. Require reward telescoping independently in D62. The supplemental
matrix is mechanical reference evidence only; no policy score, oracle value, ranking, or selection
may be summarized from it.

## Frozen provenance

The supplemental-population generator must assert the input D61 population SHA-256 and must change
exactly one named row and its 224 parameter fields. The parity validator must pin this amendment,
the generator, the source population, the supplemental population, the unchanged D61 runner
source, the corrected D61 matrix, and the release library by SHA-256 before reading results.

All remaining D62 transition budgets, architecture, optimization, probes, gates, decision rules,
and platform prohibitions remain unchanged.
