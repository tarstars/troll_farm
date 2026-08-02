# Owner-directed restoration of best measured bot — 2026-08-02

Phase: **submission complete; clean initial health; read-only maturation monitoring**

## Selection

Immediately before the restore, active funding-first agent/submission
`6585846`/`41071360` had matured to 265/265 parsed games, score 16.37, rank 109/130,
40 catastrophes (15.1%), negative-margin mass 10,285, zero runtime signals, and clean
identity. Its encouraging 11-game checkpoint did not persist.

The strongest mature artifact in the current owner-directed lineage is the far-denial d3
source. Its previous exact agent/submission `6585578`/`41070584` terminated at 160/160
parsed, score 22.99, rank 34/113, 15 catastrophes (9.375%), negative-margin mass 3,801,
zero runtime signals, and clean identity.

Selected source:
`cgauto/submissions/candidate-agent6561795-owner-far-denial-no-return-d3-slim.min.rs`;
63,033 bytes; SHA-256
`307a07556ab79a3089995841575c07f4b001f2ea08ee5b13ff7586f0149c76cd`.
The sidecar, source, historical task, and terminal checkpoint agree exactly.

## Preflight and mutation

- Platform source recovery matched the displaced funding-first source at SHA-256
  `b8382910116bbfaeade378732508bf4281a7f4ee793ae8f14ae41992ece37af4`.
- Sacred `rust/src/bin/yamo_orchard_live.rs` remained byte-exact at SHA-256 `fff6669b…`.
- `local_codex_1` was the sole Arena controller; `claude_1` explicitly held no mutation
  authority and was blocked on credentials.
- The owner directly instructed submission of the current best bot. The exact preflight and
  start notice were remotely published at `576c3e9` before the platform write.
- `TestSession/submit` returned HTTP 200 exactly once with submission `41079354` and
  `SUBMIT-OK`; no retry occurred. The platform assigned new agent `6589510` and queued ten
  matching battles.

Submission log:
`owner-best-far-denial-restore-submit-20260802T054349Z.log`, SHA-256
`fb4ffe79a8b298f216a59e530a8974d6712a85d14e5753dd4553f2807ed26f32`.

## Initial health

The first exact submission-scoped checkpoint at `2026-08-02T05:44:29Z` has 9/9 finished
and parsed games plus one pending, exact agent/submission identity, zero unexpected rows,
fetch failures, invalid results, or runtime signals. Record: 4 wins / 5 losses, mean margin
+13.667, one catastrophe, negative-margin mass 378. The fresh row reports score 0.0 and
rank 129/130; this nine-game initialization is immature and does not overturn the same
source's historical 22.99/160 evidence.

Checkpoint:
`owner-best-far-denial-restore-initial-checkpoint-20260802T054421Z.json`, SHA-256
`f63943d0ef5fff6630299994ff418fc08be6ec01eb5753e59fc387f7f19e20d2`.

## Disposition

The requested platform mutation is complete. Agent/submission `6589510`/`41079354` is the
sole live leg. Further interaction is read-only maturation monitoring; no automatic second
submission or unrelated candidate follows.

