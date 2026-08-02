# Owner banana-factory + b100/e6 Arena execution — 2026-08-02

The owner-directed unqualified live override was submitted once from exact source
`local_codex_1/banana-factory-b100-owner-override/banana-factory-b100-e6.arena.rs`, 99,440
bytes, SHA-256 `2d164ecbaf8a06092f91fffd253f295ec6d6233f2094ac707eda152b28cb2533`.
The pre-submit record was pushed first at commit
`986fad991bfec55e14d2a42f6afe1080cab1bb0a` on the agent, main, and session branches.

`TestSession/submit` returned HTTP 200 and submission `41081195`; `SUBMIT-OK` was printed. No
retry occurred. Platform agent `6590083` is the exact new identity.

The 2026-08-02T16:00:50Z immutable checkpoint contains 10 matching battles, all finished and
parsed, with zero unexpected rows, fetch failures, validity/runtime signals, or identity faults.
The room read is 0.0 at rank 130/131 and the filtered read is 13.7 at rank 124. Results are
4W/6L, mean margin -32.3, five catastrophic losses, and negative-margin mass 749.

**Disposition: mutation terminal / clean but very weak initialization / read-only monitoring.**
The owner states reconvergence takes approximately 30 minutes. No value verdict, automatic
restore, second candidate, or other Arena mutation follows from this first checkpoint.

Evidence:

- `owner-banana-factory-b100-submit-20260802T1559Z.log`;
- `owner-banana-factory-b100-initial-checkpoint-20260802T1600Z.json`, SHA-256
  `03b77b4d9233a6d764471da3ea29f4b06401da6570c38c18af068251d26ebb7d`;
- `owner-banana-factory-b100-preflight-20260802T155654Z.json`.

The owner's approximately 30-minute read was captured without platform mutation at
2026-08-02T16:29:58Z. It has 98/98 finished/fetched/parsed games plus one pending, clean
identity and zero runtime signals. The Arena row is 12.99 at rank 127/131; results are
49W/49L, mean margin +4.642857, 22 catastrophes (22.45%), and negative-margin mass 4,851.
Checkpoint SHA-256 is `83983d63e671bec97832d1937b14e674cf65f5852c66e053f9488ed516bb452e`.

**Current disposition: active owner override / clean but weak provisional 98-game evidence /
read-only.** The average-margin recovery does not qualify the source, and the checkpoint remains
below the registry's 100-game mature threshold. No automatic restore or second submission follows.
