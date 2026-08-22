# progress: 20260730-a2-0b-referee-evaluation-parity

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T15:22:05Z
- Task: 20260730-a2-0b-referee-evaluation-parity
- Branch: `agent/local_codex_1`
- Requires acknowledgement: no

## Progress

The A2-0b protocol is frozen before implementation at
`docs/a2-0b-referee-evaluation-parity-protocol-2026-07-30.md`, SHA-256
`c912896d98da164cb34255ce44c4da1e463ecb23fa9b5ebba923f4f0f1f0b432`.

The fixed calibration reuses only D173b's already-consumed 2,048-task matrix. Its
known-resident exact target is 49 catastrophes and 12,749 negative-margin mass.
The new path is isolated: frozen `engine.rs`, `official_mapgen.rs`, resident, opponent
sources, and old results remain untouched.

Gates require 1,024-seed initial-state identity, exact RNG draw accounting, zero
reason-counted referee-invalid commands, 1-vs-20-thread byte identity, both seats/eight
families, full six-detector coverage, and disclosed legacy/referee divergence. No panel
runs until a separate implementation lock is pushed.
