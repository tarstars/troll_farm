# D105b D104 cardinality measurement amendment

Date: 2026-07-22  
Status: frozen after fresh manifest generation and before successful proposal output or any terminal run

The unchanged fresh D97 generator produced 233 eligible roots from the frozen 256-task panel. This
passes D105b's prospective minimum of 220, but the frozen D104 audit runner contains a historical
`roots.len() == 240` assertion tied to its original D97 panel. It aborts before creating proposal
output. No terminal continuation has run and no outcome has been read.

Apply only this cardinality adapter:

1. preserve the immutable 11,909-row fresh manifest, SHA-256
   `389d5a3111e5232dbbea85f051b46babad9d370072599c37fe44b0e6aa0cb81b`;
2. deterministically clone the complete rows of the seven smallest existing root IDs onto the
   seven smallest unused IDs, changing only `root_id` and its textual `arm_id` prefix;
3. run the unchanged D104 binary on this 240-root padded replay input;
4. discard every proposal whose root ID is not in the immutable fresh manifest; and
5. require the retained matrix to contain exactly `233 * 64 = 14,912` unique source-root/expert
   rows before the original D105b union builder sees it.

The cloned roots exist only to satisfy a fixed audit cardinality. They cannot enter the union lock,
support metrics, terminal arms, discovery/validation fit, or value. Original-root replay and
proposal behavior are untouched.

Immutable anchors:

- D105b protocol:
  `42b5dd0f689b8d8d7e110d7babf6bcf4ea41b21811c3a28017cbbd8c3720962a`;
- adapter:
  `6f5c8e062e7449ed30f5701c1a9b73609fe250a4f3102ccce5ac8427f3866546`;
- unchanged D104 runner:
  `c68652529212d9d5067d533d3abee8865667aa821b544b8adce2b7aaff096393`.

Any mismatch permits repair only. This amendment changes no frozen task, root eligibility, action,
feature, arm, model, gate, or decision rule.
