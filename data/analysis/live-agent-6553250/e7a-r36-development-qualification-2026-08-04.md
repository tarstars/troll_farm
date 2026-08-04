# E7a round-36 deployment qualification

Status: **DEVELOPMENT EXACT-EQUALITY PASS / ARENA SUBMISSION AUTHORIZED BY OWNER**

## Candidate

- Source: `cgauto/submissions/candidate-agent6553250-e7a-r36-simplified.min.rs`
- Bytes: 55,799.
- SHA-256: `2caac7c6e71e8dcc613a2275fe8129cdf9aec2c1230e50f7dfdec79908528381`.
- Exact E7a baseline: 62,820 bytes, SHA-256 `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`.
- Reduction: 7,021 bytes from exact E7a (6,479 bytes relative to the previously documented
  62,278-byte qualified checkpoint comparison).

## Frozen 516-task result

The consumed development design used official-generator seeds 9,854,000--9,854,042, both seats,
and six frozen opponent families: 516 paired tasks total.

- Verdict: `DEVELOPMENT_EXACT_EQUALITY_PASS`.
- Differing terminal tasks: **0/516**; first difference: none.
- Mean paired margin delta and bootstrap lower bound: 0 / 0.
- Catastrophes: 19 / 19; negative-margin mass: 4,138 / 4,138.
- Every family and both seats: zero delta.
- Training, liveness, issues, and all twelve terminal-field pairs: exact.
- Candidate p95 latency ratio: 1.00480; maximum 7.276 ms.
- All frozen gates: pass.

Evidence:

- JSON SHA-256: `ec61d43a577414ba26e5383fcc2be7b012797dfd765a6547aa7b1f653ba7e39e`.
- TSV SHA-256: `c9a8161a335124ed70bb0ed4485433f189246fbb40dd0f1cb05f7322a255c854`.

Three compile-only preflights exposed runner API drift accumulated after round 22: the generic
runner lacked live fields, the round-22 adapter still initialized round 36's deleted `scores`
field, and its relative referee path required generation beside the template. No map or task ran
during those failures. The final evaluator pins the qualified round-22 adapter SHA and derives
only the uniquely anchored removal of that obsolete initializer; the generated runner hash is
recorded in the result.

## Arena preflight

The submission-history tool reports that this exact hash has never been deployed. Platform source
recovery before mutation is byte-exact to the current readable no-orchard SHA `98628e98...`.
Current agent `6593838` / submission `41089629` is complete and healthy at 160 games, score 24.76,
rank 21/137, 94W/2T/64L, 17 catastrophes, negative-margin mass 4,986, zero runtime signals, and
clean identity.

The owner directly instructed one submission after exact equality. Any resulting standing is one
draw from a noisy distribution: exact E7a previously ranged from 23.56/rank 32 to 25.30/rank 12.
No automatic retry is allowed.
