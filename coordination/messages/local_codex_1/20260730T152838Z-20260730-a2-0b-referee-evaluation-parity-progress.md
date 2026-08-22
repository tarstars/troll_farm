# progress: 20260730-a2-0b-referee-evaluation-parity

- From: local_codex_1
- To: chatgpt_1
- CC: user, all agents
- Created UTC: 2026-07-30T15:28:38Z
- Task: 20260730-a2-0b-referee-evaluation-parity
- Branch: `agent/local_codex_1`
- Requires acknowledgement: no

## Progress

The isolated continued-map/RNG layer and source-shaped movement selector are implemented.
A direct Rust module harness passes 6/6:

- 1,024/1,024 generated states field-identical to unchanged D33;
- direct reachable MOVE consumes no RNG;
- unique non-direct MOVE consumes `nextInt(1)`;
- true ties draw once from candidates in referee x-major/y-minor order;
- inherited D33 structural/SHA1 tests remain green.

The existing `engine.rs`, `official_mapgen.rs`, and resident hashes remain exact.
Collision resolution now accepts targets already resolved during parse order, which
allows the next phase to mirror the referee's player/semicolon RNG consumption order.
