# claude_1 Status

- Updated UTC: 2026-08-02T07:02:00Z
- State: Arena submission history registry built, tested and handed off; awaiting review
- Role: contributor (former coordinator; role transferred to local_codex_1 2026-07-30 by owner directive; returned to active contributor status by owner 2026-08-01)
- Current task: `20260802-arena-submission-history-registry` (handed off, awaiting review)
- Branch: agent/claude_1
- Worktree: /home/tarstars/prj/troll_farm-claude_1 (isolated; created 2026-08-01)
- Head: 845e83da114444fc7b7313d8ef2118fb35a31198 (handoff base; the handoff commit is its child on the pushed branch)
- Write set: cgauto/submission_history.py, data/analysis/arena-submission-history-inputs.json, data/analysis/arena-submission-history.json, data/analysis/arena-submission-history-provenance-2026-08-02.md, docs/arena-submission-history-schema-2026-08-02.md, tests/test_submission_history.py, coordination/messages/claude_1/, coordination/status/claude_1.md, claude_1/
- Last concrete progress UTC: 2026-08-02T07:02:00Z
- Evidence: claim 221edcd, provenance survey 7173e7c, implementation 22f811b, docs ab49427, timestamp correction 845e83d; prior task accepted as D172_GIT_LFS_PILOT_PASS
- Running job: none
- Latest verified result: 9 source families / 17 deployments / 35 observations built deterministically (`build --check` byte-identical, `validate` clean, 38/38 tests under a minimal harness). Source-level all-history medians: preseed-orchard 24.19 over 4 mature runs, far-denial 22.99 over 1; the registry's highest single score (24.89/160) belongs to a REJECTED source. Live leg 6589510/41079354 still has only 9 games of submission-scoped evidence.
- Next checkpoint: local_codex_1 reviews the handoff, runs `uv run pytest tests/test_submission_history.py` under the real virtualenv, and rules on the acceptance-4 "19.37/160" discrepancy
- Blockers: no uv/pytest/pip on this host, so the canonical pytest command could not be run; battle-level platform reads blocked (no credentials); medium_data unmounted; no collection cron here
- Arena controller: no — local_codex_1 holds it; I perform no platform mutations
