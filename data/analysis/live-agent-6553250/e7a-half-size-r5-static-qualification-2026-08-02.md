# E7a half-size r5 — static qualification

Status: **SIZE PASS / COMPILE PASS / BEHAVIOR AND VALUE GATES PENDING**

## Exact result

- baseline: `candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`
- baseline bytes: 62,820
- baseline SHA-256: `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- candidate: `local_codex_1/e7a-half-size-logical-simplification/integrated-half-r5.rs`
- candidate bytes: **30,949**
- candidate SHA-256: `6692fa59d207785e269abaae0f6c11c917046249912da3e3c88b13599e9c5491`
- reduction: **31,871 bytes / 50.73%**
- hard ceiling: 31,410 bytes
- headroom: 461 bytes

This is a semantic reduction. The exact compact baseline is the builder input and no
whole-source formatter, whitespace pass, identifier renamer, encoder, compressor, macro table,
or alternate source was used.

## Logical deletion and replacement

The fail-closed builder applies unique named item transforms and records every item span in
`integrated-half-r5-manifest.json`.

- Removed the 14,231-byte secure APPLE orchard wrapper and its state types.
- Replaced the general Yamo state/orchestration with a focused two-worker controller.
- Replaced exhaustive 27-profile opening selection with seven readable common profiles and a
  turn-35 cheap worker fallback.
- Removed 1,701 bytes of future tree-growth/opponent-chop forecast and replaced it with direct
  travel/chop/return feasibility.
- Removed the 2,564-byte multi-worker priority/forbidden router and retained a two-worker
  occupied-cell/landing guard.
- Replaced general endgame planting with bounded conversion on an empty shack door.
- Removed newly orphaned carry, growth-rule, and `PlantKind` APIs after their owning systems
  disappeared.

The lexical audit reports 568 unique baseline identifiers, 333 candidate identifiers, 319
preserved identifiers, 249 identifiers removed with the declared blocks, and only 14 identifiers
introduced by readable replacement logic. There is no rename mapping. The introduced names are
ordinary semantic names such as `choices`, `deficit`, `few_opponents`, `fixed_bank_candidates`,
`focus`, and `ordinary_candidates`.

## Preserved core in source

- exact E7a PLUM/LEMON threshold implementation;
- protocol input parser and `GameState` layout;
- orthogonal BFS navigation;
- training legality and early fruit/iron target enumeration;
- persistent fixed-door banking for any carried cargo, with wood checked first;
- target- and stock-compatible two-worker selection;
- occupied-cell and duplicate-landing protection;
- turn-bounded fruit-to-wood conversion with a completed-return allowance.

## Static checks

```bash
python3 -m py_compile \
  local_codex_1/e7a-half-size-logical-simplification/build_integrated_half.py

python3 local_codex_1/e7a-half-size-logical-simplification/build_integrated_half.py \
  cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs \
  local_codex_1/e7a-half-size-logical-simplification/integrated-half-r5.rs \
  --manifest local_codex_1/e7a-half-size-logical-simplification/integrated-half-r5-manifest.json

rustc --edition=2021 -O -Awarnings \
  local_codex_1/e7a-half-size-logical-simplification/integrated-half-r5.rs \
  -o /tmp/e7a-integrated-half-r5
```

Observed: builder succeeds, optimized compilation succeeds, empty input exits zero with zero
stdout/stderr, and `rustc -W dead-code` emits no warnings. Sacred source remains exact SHA-256
`fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`.

## Boundary

This result satisfies only the source-size, non-obfuscation, compile, and empty-input gates.
Focus, training, banking, contention, deadline, oscillation, latency, and 512-task open-panel
value gates remain mandatory before any Arena action.
