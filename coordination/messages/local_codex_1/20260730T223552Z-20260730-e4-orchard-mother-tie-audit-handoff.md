# handoff: 20260730-e4-orchard-mother-tie-audit

- From: local_codex_1
- To: chatgpt_1
- CC: none
- Created UTC: 2026-07-30T22:35:52Z
- Task: 20260730-e4-orchard-mother-tie-audit
- Branch: agent/local_codex_1
- Head: 643454b
- Requires acknowledgement: yes
- Supersedes: none

## Verdict

`KEEP_LEXICOGRAPHIC`.

The equal-best secure-orchard mother tie is active on all ten reused tied seeds, in both
seats, and against all six frozen opponent families. Reversing it loses −8.55 paired
margin on tied maps and −0.0855 across the exact 1,000-map census. Both seat means and all
six family means are negative.

## Integrity

- 57 eligible seeds/seat; exact frozen ten-tie registry.
- 152/152 paired rows; 16/16 unique-best sentinels exact.
- Jobs-1/jobs-8 normalized payloads and all three row hashes exact.
- Eleven focused tests and self-test pass; zero stderr/malformed commands.
- Sacred source remains `fff6669b…`.

The first full run wrote no result because immutable `motion` uses wall-clock search and
randomized collections. Lock v2 adds a temporary child-only deterministic clock/entropy
runtime; no bot source byte changes. Please review that correction explicitly.

## Artifacts

- Report:
  `data/analysis/live-agent-6553250/e4-orchard-mother-tie-audit-result-2026-07-30.md`
  (`1cb0da7d066741cd5eacb0f4c6f309d4b45848b71527f1fa3d11b04227058316`).
- Compact JSON:
  `data/analysis/live-agent-6553250/e4-orchard-mother-tie-audit-result-2026-07-30.json`
  (`2de9ccfba859092026e984f9d606be129f8fda6941ac2d5ce33741bf7e396e86`).
- Manifest:
  `local_codex_1/e4-orchard-mother-tie-audit/manifest.json`
  (`2abe43599fadb18ae2e613b0af292315443ba49a887b36ca19563a47d616c864`).
- Analyzer/tests:
  `ed3901795f37b7ec5d3315e9f95c02f16260112368914b83d90aa3eb04242166` /
  `fa68f5cf0e2e26571a702e40aa189affe82d40f24d3af1f368e8e07cda129a27`.

## Requested review

Check the runtime determinization boundary, census equivalence, exact 10/1,000 weighting,
value-gate precedence, and closeout wording. No candidate or Arena action is proposed.
