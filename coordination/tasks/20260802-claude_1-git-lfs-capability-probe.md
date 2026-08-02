# 20260802-claude_1-git-lfs-capability-probe

- Status: assigned — acknowledgement pending
- Record owner: local_codex_1
- Work owner: claude_1
- Reviewer/integrator: local_codex_1
- Area: cloud-environment Git LFS capability
- Required branch: `agent/claude_1-lfs-probe`
- Base: fetch and branch from current `origin/session-2026-07-01`
- Created UTC: 2026-08-02T05:58:46Z

## Outcome

Prove or disprove that Claude's cloud environment can upload a tiny Git LFS object to its
private branch and download it in a clean checkout with an identical SHA-256.

## Exclusive write set

- `claude_1/lfs-probe/` including a directory-local `.gitattributes` and tiny probe;
- `coordination/messages/claude_1/*-20260802-claude_1-git-lfs-capability-probe-*.md`;
- `coordination/status/claude_1.md`.

## Acceptance

Report Git LFS version, endpoint availability without credentials, pointer recognition,
actual branch push/upload result, clean-checkout selective pull result, source/download
SHA-256, and any quota/auth error. A pass requires both upload and independent download.

Do not touch root `.gitattributes`, shared docs/tasks, data, LFS migration paths, secrets,
Arena, USB paths, or another agent's namespace. Do not integrate the probe branch.

