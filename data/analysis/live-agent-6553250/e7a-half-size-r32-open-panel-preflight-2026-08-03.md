# E7a half-size r32 open-panel preflight

- Task: `20260802-e7a-half-size-logical-simplification`
- Frozen UTC: `2026-08-02T21:45:15Z`
- Disposition: `PREFLIGHT_LOCKED_FULL_OPEN_PANEL_PENDING`
- Arena action: none

## Exact identities and size

- Baseline: `cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
  - 62,820 bytes
  - SHA-256 `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- Candidate: `local_codex_1/e7a-half-size-logical-simplification/integrated-half-r32.rs`
  - 31,387 bytes
  - SHA-256 `abb202db71040f8784b7d02cc114ced9f71d82e82d3c8a1cc975d87d3feeb4da`
  - hard ceiling 31,410 bytes; 23 bytes of headroom
  - reduction 31,433 bytes, or 50.034% of the baseline
- Sacred source: `rust/src/bin/yamo_orchard_live.rs`
  - SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`

## Construction and non-obfuscation lock

The candidate is built only through unique named item removal and readable replacement.
The manifest records 568 unique baseline identifiers, 336 candidate identifiers, and 317
preserved identifiers. It records no identifier-renaming mapping, whole-source minifier,
encoding, or compression. The size reduction comes primarily from removing the secure
orchard state machine and general opening/priority machinery, and replacing the broad
orchestration, forecast, assignment, collision and endgame layers with readable two-worker
implementations.

Hashes:

- builder: `433188b1ae81ea6cb8e5bfb8d7606b530a6ff11d0cfeaf82274d7165375c5b7a`
- manifest: `397b337e464af36a126105f342e3b60abd3ac4b6c9c0802f68710d7e08eae4f0`
- semantic validator: `7ecdefcb46f8f40e25c09d0deb07e8915b639a028d1404d1350bdaa5014fd7f3`
- motion evaluator: `aeccde7b73891fbfa03a57c657ce230c65e1930ef04ff735c081cbf4134b6258`
- open-panel runner: `4d30ec25db7055faba9d7f33007ec4cc17f67680d529dbda876025613633d72e`
- open-panel evaluator: `f00e1870caa398110e58a8b94bc721227bfd90a51a6aaa797908bd8ae503164a`

## Static and semantic preflight

- `rustc --edition=2021 -O -D warnings` succeeds.
- Empty input exits zero with zero stdout and zero stderr.
- The semantic validator returns `SEMANTIC_FIXTURES_PASS`: 10/10 fixtures, zero malformed
  commands and zero unexpected stderr.
- Covered fixtures: E7a focus below/at/outside the distance threshold, second-worker bill
  collection and exact training, turn-35 fallback, persistent wood banking, same-target
  exclusion, landing reservation, and the turn-295/296 endgame boundary.
- Sacred source remains exact.

## Closed-loop preflight

The 16-game motion smoke is diagnostic, not qualification. Candidate-minus-baseline mean
margin is -6.625 (median -11, range -119 to +114); catastrophes are 2 versus 2; maximum
period-2 target run is 3 versus 6. Seat means are -22.5 and +9.25. This was retained only
as a fast regression check.

The continued-referee one-map official smoke uses seed 9,854,000, both seats, and all six
frozen families (12 paired tasks). It gives mean margin -9.9167; family means are resident
-6, gold_adaptive +4, compact_gold +4, norx_native_three -12, legend_balanced -42, and
mybot -7.5. Worker-two coverage is 12/12 with median delay zero. Candidate period-2 >=6
episodes are 0 versus one baseline episode. This one-map result fails the value/negative-
mass gates and is not interpreted as the full-panel verdict.

The one-thread and four-thread TSV data rows are byte-identical after removing timing
comment lines, SHA-256
`a9e6413a068c1b3affeddae82782ebe64d933f020652b29309a2775b6594c0e3`.

## Frozen full-panel command

The next value run is exactly 43 already-consumed open maps, seeds 9,854,000 through
9,854,042 inclusive, both seats, and the six families `resident`, `gold_adaptive`,
`compact_gold`, `norx_native_three`, `legend_balanced`, and `mybot`: 516 paired tasks.
No selector or threshold will be changed after this run.

```bash
python3 local_codex_1/e7a-half-size-logical-simplification/evaluate_open_panel.py \
  --start 9854000 \
  --maps 43 \
  --threads 8 \
  --bootstrap 50000 \
  --panel local_codex_1/e7a-half-size-logical-simplification/integrated-half-r32-open-panel.tsv \
  --output local_codex_1/e7a-half-size-logical-simplification/integrated-half-r32-open-panel.json
```

Passing this panel is necessary but not sufficient for Arena: the frozen replay
counterexample liveness packet remains a separate Stage-C/Stage-D obligation.
