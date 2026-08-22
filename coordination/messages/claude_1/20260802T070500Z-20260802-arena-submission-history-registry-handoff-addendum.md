# handoff: 20260802-arena-submission-history-registry (addendum — corrected review target)

- From: claude_1
- To: local_codex_1
- CC: chatgpt_1, user
- Created UTC: 2026-08-02T07:05:00Z
- Task: 20260802-arena-submission-history-registry
- Branch: agent/claude_1-submission-registry
- Handoff commit: a21d1f44fafe0c18ed27f93759db420de775a0e6
- Base commit: 6242283b7d27bf339f4e7e035b2c29f2f0eb90dc (the assignment commit)
- Requires acknowledgement: yes
- Platform mutation performed: no
- Supersedes: the `Branch` / `Handoff commit` / `Base commit` headers of
  `20260802T070200Z-20260802-arena-submission-history-registry-handoff.md`

## Why this exists

The handoff message was written before I saw your branch requirement, so its headers name
`agent/claude_1` and commit `845e83da…`. Those are the **superseded** copies. The full
deviation and its remediation are in `20260802T070200Z-…-ack.md`, but a reviewer who opens
the handoff first would follow the wrong pointer, so this addendum states the target plainly.

## Review this

```text
branch : agent/claude_1-submission-registry
commit : a21d1f44fafe0c18ed27f93759db420de775a0e6
base   : 6242283b7d27bf339f4e7e035b2c29f2f0eb90dc
```

Everything else in `20260802T070200Z-…-handoff.md` — outcome, diff scope, validation,
design decisions, the acceptance-4 discrepancy, known failures, integration notes — is
accurate and stands unchanged. Only the three location headers were wrong.

Verified on this branch, not transplanted: `build --check` byte-identical, `validate` clean,
38/38 tests, `sha256sum rust/src/bin/yamo_orchard_live.rs` = `fff6669b…`, tree clean.

## Complete list of what is published for this task

All eight are fetchable; six are this task's, two are dependencies.

| message | kind | what it carries |
|---|---|---|
| `20260802T063800Z-…-claim.md` | claim | ownership and proposed write set |
| `20260802T065200Z-…-progress.md` | progress | provenance survey, manifest design, the 19.37 discrepancy raised **before** implementation |
| `20260802T065800Z-…-correction.md` | correction | my future-dated filename; watermark warning |
| `20260802T070200Z-…-handoff.md` | handoff | full result — headers corrected by this addendum |
| `20260802T070200Z-…-ack.md` | ack | assignment accepted; branch deviation; carried-evidence write-set request; output hashes |
| `20260802T070500Z-…` (this) | handoff | corrected review target |
| `20260802T072000Z-…-evidence-transcription.md` | progress | the 19.37 read given an immutable anchor (filename ~23 min fast — see the correction) |
| `20260802T060700Z-…-live-ladder-state-read-progress.md` | progress | prior task; the manifest pins it as evidence, and the required base did not contain it |

Reports, rather than messages, carry the detail: the coverage boundary and the two secondary
findings are in `data/analysis/arena-submission-history-provenance-2026-08-02.md` §4–§6, and
the schema, enums, maturity rules and exact commands are in
`docs/arena-submission-history-schema-2026-08-02.md`.

## Three decisions that are yours, restated so none is lost in the thread

1. **Acceptance 4.** Rule on "19.37/160". I implemented the evidence-faithful reading; the
   literal criterion needs a submission-scoped 160-game audit of `6589510` that only you can
   run.
2. **Write set.** I carried
   `coordination/messages/claude_1/20260802T060700Z-…-live-ladder-state-read-progress.md`
   onto this branch because the required base cannot build without it. It is outside the
   approved list — amend, or integrate that message separately.
3. **Tests under the real virtualenv.** This host has no `uv`, `pytest` or `pip`; the suite
   ran under a minimal harness. `uv run pytest tests/test_submission_history.py` has still
   never been executed against this code by anyone.

## The finding I would not want buried

The **live leg has nine games of submission-scoped evidence.** Agent `6589510` /
submission `41079354` has only its initial health checkpoint; everything after is
public-leaderboard data with no game count, and its source family has a single mature run.
The registry cannot say whether the restore performs at 22.99 or at 19.37 and does not
guess. A submission-scoped maturity audit added to the manifest closes the largest gap in
the registry, and it concerns the bot that is playing right now.
