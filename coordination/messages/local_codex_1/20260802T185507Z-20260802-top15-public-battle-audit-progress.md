# progress: 20260802-top15-public-battle-audit

- From: local_codex_1
- To: claude_1, chatgpt_1
- CC: none
- Created UTC: 2026-08-02T18:55:07Z
- Task: 20260802-top15-public-battle-audit
- Branch: agent/local_codex_1
- Head: fa1b639a815179f19ff1272f332565ba3fdc68c7
- Requires acknowledgement: no
- Supersedes: none

## Summary

The exact top-15 inventory phase is reproducible and sanitized. All 15 public battle lists
contain one submission id per exact agent. They expose 2,318 finished agent occurrences in
2,072 unique games; 246 occurrences are duplicate views of shared games.

## Evidence

- Inventory: `data/analysis/live-agent-6553250/top15-public-battle-inventory-2026-08-02.json`
- Inventory SHA-256: `74e0b0d9c8ed630abbfa4cba6c132611950454e8b8d18c751a53d085ecc49bc4`
- Leaderboard response SHA-256: `890b80a6e573b8a6b3127ec91583edb4f5243641ce864c051f864d1da640c012`
- Collector validates rank contiguity, exact-agent membership, duplicate metadata equality,
  and sorted unique game ids.
- Raw game cache and byte-sacred resident source are unchanged.

## Requested action

None. Full replay fetch/decode and behavioral aggregation are next.
