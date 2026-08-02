# 20260802-e7a-sector-owner-override-publication: replace defective ring bot with sector candidate

- Status: in progress — pre-submission checks pass; one Arena mutation pending
- Owner / arena controller: `local_codex_1`
- Branch: `agent/local_codex_1`
- Created UTC: 2026-08-02T17:41:07Z
- Authority: direct owner instruction, 2026-08-02: publish the candidate with sector after
  observing severe live oscillation in the bounded banana-ring bot

## Exact mutation

Submit exactly once:

`cgauto/submissions/candidate-agent6553250-preseed-e7a-lemon-near-tie.min.rs`

- bytes: 62,820
- SHA-256: `97bfe71e3f2f05e1b8fa3c697c5e5db3624ac9739e90954e9fa9be79a8e48595`
- parent: mature historical resident source SHA-256 `a8eb3b2bb646c59baf4c0a8b6bbdd9ca626e20ab2a27553dadbded047b884e55`

This ends and replaces the bounded banana-ring cycle (`6590136` / `41081465`). No retry is
allowed after an ambiguous response.

## Evidence and explicit override

The candidate is mechanically exact but was not prospectively value-qualified. Its consumed-panel
estimate is +4.0083 mean margin against the parent, root-bootstrap 95% interval
[-1.5875, +13.1015]. The owner explicitly directs publication despite that value-gate status.

Fresh host checks immediately before the mutation:

- candidate regeneration is byte-exact;
- all five focused tests pass;
- standalone optimized compilation passes;
- the 16-seat-game semantic bridge is exact, with zero runtime/command faults;
- sacred source remains SHA-256 `fff6669b0bc0b15b0992637f70c07197e1838f403cb7fd038bc1fae73d52b13f`;
- recovered live source is the bounded ring artifact, SHA-256
  `d2d8f65804991fed5ca8cdaacc1b62fd90ab553ee6952c6286029497e525eecc`;
- pre-replacement read at 2026-08-02T17:40:03Z: ring agent `6590136`, submission `41081465`,
  Arena-room score 11.8, rank 129/131;
- no other submit process or Arena controller is active.

## Completion

Record the exact API response, returned submission and agent identities, artifact recovery hash,
first clean submission-scoped checkpoint, registry/default-source decision, ledger entry, and
post-mutation notification. Do not represent the consumed-panel estimate as fresh validation.
