# progress: 20260730-n5-endgame-opponent-plant-contest

- From: local_codex_1
- To: chatgpt_1
- CC: user
- Created UTC: 2026-07-30T20:36:30Z
- Task: 20260730-n5-endgame-opponent-plant-contest
- Branch: agent/local_codex_1
- Requires acknowledgement: no
- Supersedes: none

## Implementation lock

The deterministic analyzer and six focused tests are implemented. Compile, self-test, and
pytest pass. Analyzer SHA-256 is
`f2075297ae24631714abfe3b6d92b7fc357dad17228a237cf73d36c2beedcd2d`;
test SHA-256 is
`947951899951440d4d86493df94e61841bf62dee4ec1a506d451f0eaac5699e6`.

The implementation verifies the exact index/cohort/dependency hashes, hashes all raw and
trajectory inputs, reconstructs both lineage orientations, emits exact target and per-game
tables, bootstraps whole games including zeros, and fails closed to `UNIDENTIFIABLE`.

## Boundary

No full corpus result has been inspected yet. No resident, simulation, input, or Arena
path was touched.
