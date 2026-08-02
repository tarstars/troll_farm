# claude_1 Status

- Updated UTC: 2026-08-02T07:05:00Z
- State: Arena submission history registry built, tested, handed off and republished on the required branch; awaiting review
- Role: contributor (former coordinator; role transferred to local_codex_1 2026-07-30 by owner directive; returned to active contributor status by owner 2026-08-01)
- Current task: `20260802-arena-submission-history-registry` (handed off, awaiting review)
- Branch: agent/claude_1-submission-registry (required by the assignment; supersedes the agent/claude_1 copies)
- Worktree: /home/tarstars/prj/troll_farm-claude_1-registry (isolated, one per branch; created 2026-08-02)
- Head: see the pushed branch agent/claude_1-submission-registry; review target is stated in 20260802T070500Z-...-handoff-addendum.md
- Write set: cgauto/submission_history.py, data/analysis/arena-submission-history-inputs.json, data/analysis/arena-submission-history.json, data/analysis/arena-submission-history-provenance-2026-08-02.md, docs/arena-submission-history-schema-2026-08-02.md, tests/test_submission_history.py, coordination/messages/claude_1/, coordination/status/claude_1.md, claude_1/
- Last concrete progress UTC: 2026-08-02T07:02:00Z
- Evidence: required branch agent/claude_1-submission-registry at 2529fd2 (build --check byte-identical, validate clean, 38/38 tests, sacred SHA fff6669b); first published on agent/claude_1 at b5a0fd7 before I saw the branch requirement — those copies are superseded; prior task accepted as D172_GIT_LFS_PILOT_PASS
- Running job: none
- Latest verified result: 9 source families / 17 deployments / 35 observations built deterministically (`build --check` byte-identical, `validate` clean, 38/38 tests under a minimal harness). Source-level all-history medians: preseed-orchard 24.19 over 4 mature runs, far-denial 22.99 over 1; the registry's highest single score (24.89/160) belongs to a REJECTED source. Live leg 6589510/41079354 still has only 9 games of submission-scoped evidence.
- Next checkpoint: local_codex_1 reviews agent/claude_1-submission-registry, runs `uv run pytest tests/test_submission_history.py` under the real virtualenv, rules on the acceptance-4 "19.37/160" discrepancy, and amends the write set for the one carried ladder-read evidence message
- Blockers: no uv/pytest/pip on this host, so the canonical pytest command could not be run; battle-level platform reads blocked (no credentials); medium_data unmounted; no collection cron here
- Arena controller: no — local_codex_1 holds it; I perform no platform mutations
