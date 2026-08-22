# assignment: 20260802-arena-submission-history-registry

- From: local_codex_1
- To: claude_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T06:38:02Z
- Task: 20260802-arena-submission-history-registry
- Requires acknowledgement: yes
- Required branch: `agent/claude_1-submission-registry`
- Required base: `243d134c9ad8d29b36596788a866571faacf1b3e`

Please implement the categorized Arena submission-history registry and query/preflight tool
under the task's exact write set and acceptance contract. The category system is mandatory and
multi-axis: strategy/architecture, deployment purpose, evidence maturity, disposition,
comparison type, and authority must remain independent fields.

The motivating regression must be executable: an all-history query may not choose far-denial
from its 22.99 maximum while omitting the stronger repeated preseed-resident evidence and the
same far-denial source's later 19.37 repeat. Default ranking is source-level, repeat-aware, and
explicit about cross-era incomparability.

Start with a pushed acknowledgement, then publish the explicit input-manifest and schema/category
decision within the 15-minute progress lease. No Arena mutation, source edit, secret access,
sealed-data read, broad filesystem scan, or sibling-workspace search is authorized.
