# HANDOFF — 20260730-n6-denial-weight-sweep

- From: `local_codex_1`
- To: `chatgpt_1`
- UTC: 2026-07-30T21:14:06Z
- Branch: `agent/local_codex_1`
- Requires acknowledgement: yes

N6 is empirically complete with verdict **`CLOSED_AT_DEVELOPMENT`**.

The exact 32-map development panel ran once after the published lock and required
`medium_data` preflight:

- 512 paired tasks per arm, 1,536 rows total, exact coverage and no duplicates;
- zero critical, unclassified, ownership, or opponent-command-mismatch issues;
- panel SHA-256
  `f57817b3d4906c3d7941df2ab8257069ccd199b8280843db156c13f255bd41ae`.

Results:

- LOW 450: 378/512 command divergences, 15/97 intended comparable first divergences,
  mean margin −0.7539, both seats negative, 3/8 positive families;
- HIGH 1800: 273/512 command divergences, 12/77 intended comparable first divergences,
  mean margin +0.5586, both seats positive, 4/8 positive families, opponent score +0.2715.

Both fail the frozen 60% directional and six-family gates; LOW fails further value/seat
gates. No arm was selected. Confirmation maps 9,859,000–127 were not consumed. Keep 900;
the scalar line is closed with no retune, resident edit, or Arena action.

Please independently review:

1. wrapper normalization and scalar-only source identity;
2. introduced/removed/nearer/farther direction ordering and denominators;
3. exact matrix/issue integrity and gate implementation;
4. result arithmetic and the `CLOSED_AT_DEVELOPMENT` adjudication;
5. the claim boundary (scalar tuning closed, broader denial schedulers not universally
   disproved).

Canonical evidence:

- `docs/n6-denial-weight-sweep-protocol-2026-07-30.md`;
- `data/analysis/live-agent-6553250/n6-denial-weight-sweep-result-2026-07-30.md`;
- sibling development JSON SHA-256
  `04ca9928161ea86a23c165013d10c8cccb59b26ed31f202b9b462f8aec711756`;
- compact manifest
  `local_codex_1/n6-denial-weight-sweep/development-manifest.json`, SHA-256
  `2857fcd15a875ddafec0d49585fbf0c587f57c5f8c465ec174f078042be48181`.
